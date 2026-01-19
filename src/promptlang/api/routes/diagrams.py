"""
API endpoints for diagram generation workflow
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import logging
import tempfile
import os
from pathlib import Path
import uuid

from promptlang.core.diagram.pipeline import DiagramPipeline, PipelineConfig, PipelineStatus, DiagramTool, DiagramFormat
from promptlang.core.diagram.catalog import DiagramCatalog
from promptlang.core.diagram.analyzer import ProjectAnalyzer
from promptlang.core.diagram.scorer import RelevanceScorer
from promptlang.core.translator.llm_provider import get_llm_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/diagrams", tags=["diagrams"])

# Global pipeline instances (in production, use proper session management)
pipelines: Dict[str, DiagramPipeline] = {}


class DiagramRequest(BaseModel):
    """Request model for diagram generation"""
    prd_content: str = Field(..., description="PRD content for analysis")
    codebase_path: Optional[str] = Field(None, description="Path to codebase (optional)")
    config: Optional[Dict[str, Any]] = Field(None, description="Pipeline configuration")
    approved_diagrams: Optional[List[str]] = Field(None, description="Approved diagram IDs for interactive mode")


class DiagramConfig(BaseModel):
    """Configuration model for diagram generation"""
    max_diagrams: int = Field(50, description="Maximum number of diagrams to generate")
    min_score_threshold: float = Field(0.0, description="Minimum relevance score threshold")
    include_optional: bool = Field(True, description="Include optional diagrams")
    preferred_tool: Optional[str] = Field(None, description="Preferred diagram tool")
    output_format: str = Field("svg", description="Output format")
    export_directory: str = Field("./diagrams", description="Export directory")
    generate_complementary: bool = Field(True, description="Generate complementary diagrams")
    parallel_generation: bool = Field(True, description="Enable parallel generation")
    timeout_seconds: int = Field(300, description="Timeout in seconds")


class DiagramPreviewRequest(BaseModel):
    """Request model for diagram preview"""
    prd_content: str = Field(..., description="PRD content for analysis")
    codebase_path: Optional[str] = Field(None, description="Path to codebase (optional)")
    limit: int = Field(10, description="Number of recommendations to preview")


class DiagramResponse(BaseModel):
    """Response model for diagram generation"""
    pipeline_id: str
    status: str
    recommendations: List[Dict[str, Any]]
    generated_diagrams: List[Dict[str, Any]]
    failed_diagrams: List[str]
    execution_time: float
    summary: Dict[str, Any]


@router.post("/preview", response_model=Dict[str, Any])
async def preview_diagrams(request: DiagramPreviewRequest):
    """Get a preview of diagram recommendations without generation"""
    try:
        # Create pipeline with default config
        pipeline = DiagramPipeline()
        
        # Get preview
        preview = pipeline.get_recommendation_preview(
            request.prd_content, 
            request.codebase_path, 
            request.limit
        )
        
        return {
            "success": True,
            "data": preview
        }
        
    except Exception as e:
        logger.error(f"Preview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=DiagramResponse)
async def generate_diagrams(request: DiagramRequest):
    """Generate diagrams based on PRD and optional codebase"""
    try:
        # Create pipeline config
        config = PipelineConfig()
        if request.config:
            config_dict = request.config
            
            # Map config values
            if "max_diagrams" in config_dict:
                config.max_diagrams = config_dict["max_diagrams"]
            if "min_score_threshold" in config_dict:
                config.min_score_threshold = config_dict["min_score_threshold"]
            if "include_optional" in config_dict:
                config.include_optional = config_dict["include_optional"]
            if "preferred_tool" in config_dict:
                tool_map = {"plantuml": DiagramTool.PLANTUML, "mermaid": DiagramTool.MERMAID}
                config.preferred_tool = tool_map.get(config_dict["preferred_tool"])
            if "output_format" in config_dict:
                format_map = {"svg": DiagramFormat.SVG, "png": DiagramFormat.PNG, "pdf": DiagramFormat.PDF}
                config.output_format = format_map.get(config_dict["output_format"], DiagramFormat.SVG)
            if "export_directory" in config_dict:
                config.export_directory = config_dict["export_directory"]
            if "generate_complementary" in config_dict:
                config.generate_complementary = config_dict["generate_complementary"]
            if "parallel_generation" in config_dict:
                config.parallel_generation = config_dict["parallel_generation"]
            if "timeout_seconds" in config_dict:
                config.timeout_seconds = config_dict["timeout_seconds"]
        
        # Validate config
        llm_provider = get_llm_provider()
        pipeline = DiagramPipeline(config, llm_provider)
        issues = pipeline.validate_config()
        if issues:
            raise HTTPException(status_code=400, detail={"config_issues": issues})
        
        # Execute pipeline
        if request.approved_diagrams:
            result = pipeline.execute_interactive(
                request.prd_content, 
                request.codebase_path, 
                request.approved_diagrams
            )
        else:
            result = pipeline.execute(request.prd_content, request.codebase_path)
        
        # Convert to response format
        response = DiagramResponse(
            pipeline_id=str(uuid.uuid4()),
            status=result.status.value,
            recommendations=[
                {
                    "id": rec.diagram.id,
                    "name": rec.diagram.name,
                    "category": rec.diagram.category.value,
                    "score": rec.relevance_score,
                    "tier": rec.selection_tier.value,
                    "reasoning": rec.reasoning,
                    "confidence": rec.confidence,
                    "effort": rec.estimated_effort,
                    "prerequisites_met": rec.prerequisites_met,
                    "complementary_diagrams": rec.complementary_diagrams
                }
                for rec in result.recommendations
            ],
            generated_diagrams=[
                {
                    "id": diag.diagram_type.id,
                    "name": diag.diagram_type.name,
                    "tool": diag.tool.value,
                    "format": diag.format.value,
                    "content": diag.content,
                    "source_code": diag.source_code,
                    "success": diag.success,
                    "error_message": diag.error_message,
                    "file_size": diag.file_size,
                    "generation_time": diag.generation_time,
                    "metadata": diag.metadata
                }
                for diag in result.generated_diagrams
            ],
            failed_diagrams=result.failed_diagrams,
            execution_time=result.execution_time,
            summary=result.summary
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Diagram generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-prd")
async def upload_prd(file: UploadFile = File(...)):
    """Upload PRD file for analysis"""
    try:
        # Validate file type
        if not file.filename.endswith(('.md', '.txt', '.docx', '.pdf')):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read file content
        content = await file.read()
        
        # For simplicity, assume text files
        try:
            prd_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File encoding not supported")
        
        return {
            "success": True,
            "filename": file.filename,
            "content_length": len(prd_content),
            "content_preview": prd_content[:500] + "..." if len(prd_content) > 500 else prd_content
        }
        
    except Exception as e:
        logger.error(f"PRD upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog")
async def get_diagram_catalog():
    """Get the complete diagram catalog"""
    try:
        pipeline = DiagramPipeline()
        catalog = pipeline.get_catalog_info()
        
        return {
            "success": True,
            "data": catalog
        }
        
    except Exception as e:
        logger.error(f"Catalog retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog/categories")
async def get_diagram_categories():
    """Get diagram categories with counts"""
    try:
        pipeline = DiagramPipeline()
        catalog = pipeline.get_catalog_info()
        
        categories = {}
        for diagram_id, diagram_data in catalog["diagrams"].items():
            category = diagram_data["category"]
            if category not in categories:
                categories[category] = {
                    "name": category,
                    "count": 0,
                    "diagrams": []
                }
            categories[category]["count"] += 1
            categories[category]["diagrams"].append({
                "id": diagram_data["id"],
                "name": diagram_data["name"],
                "description": diagram_data["description"],
                "complexity": diagram_data["complexity"],
                "usage_frequency": diagram_data["usage_frequency"]
            })
        
        return {
            "success": True,
            "data": categories
        }
        
    except Exception as e:
        logger.error(f"Categories retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def get_supported_tools():
    """Get supported diagram generation tools"""
    try:
        pipeline = DiagramPipeline()
        tools = pipeline.generator.get_supported_tools()
        
        tool_info = []
        for tool in tools:
            tool_info.append({
                "name": tool.value,
                "display_name": tool.value.replace("_", " ").title(),
                "supported_formats": ["svg", "png", "pdf", "source"]  # Simplified
            })
        
        return {
            "success": True,
            "data": tool_info
        }
        
    except Exception as e:
        logger.error(f"Tools retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formats")
async def get_supported_formats():
    """Get supported output formats"""
    try:
        pipeline = DiagramPipeline()
        formats = pipeline.generator.get_supported_formats()
        
        format_info = []
        for format in formats:
            format_info.append({
                "name": format.value,
                "display_name": format.value.upper(),
                "description": f"{format.value.upper()} format"
            })
        
        return {
            "success": True,
            "data": format_info
        }
        
    except Exception as e:
        logger.error(f"Formats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{diagram_id}")
async def download_diagram(diagram_id: str, format: str = "svg"):
    """Download a specific diagram"""
    try:
        # This is a simplified implementation
        # In practice, you'd need to store generated diagrams or regenerate them
        
        export_dir = Path("./diagrams")
        file_path = export_dir / f"{diagram_id}.{format}"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Diagram not found")
        
        return FileResponse(
            file_path,
            media_type=f"image/{format}" if format in ["svg", "png"] else "application/octet-stream",
            filename=f"{diagram_id}.{format}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Diagram download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{pipeline_id}")
async def export_all_diagrams(pipeline_id: str, format: str = "zip"):
    """Export all diagrams from a pipeline"""
    try:
        # This is a simplified implementation
        # In practice, you'd need to track pipeline results and create ZIP files
        
        export_dir = Path("./diagrams")
        if not export_dir.exists():
            raise HTTPException(status_code=404, detail="Export directory not found")
        
        # Create ZIP file (simplified)
        zip_path = export_dir / f"diagrams_{pipeline_id}.zip"
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"diagrams_{pipeline_id}.zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for diagram service"""
    try:
        pipeline = DiagramPipeline()
        catalog_stats = pipeline.get_catalog_info()["stats"]
        
        return {
            "status": "healthy",
            "catalog_stats": catalog_stats,
            "supported_tools": [tool.value for tool in pipeline.generator.get_supported_tools()],
            "supported_formats": [fmt.value for fmt in pipeline.generator.get_supported_formats()]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )


@router.post("/validate-config")
async def validate_config(config: DiagramConfig):
    """Validate pipeline configuration"""
    try:
        # Convert to PipelineConfig
        pipeline_config = PipelineConfig(
            max_diagrams=config.max_diagrams,
            min_score_threshold=config.min_score_threshold,
            include_optional=config.include_optional,
            preferred_tool=DiagramTool(config.preferred_tool) if config.preferred_tool else None,
            output_format=DiagramFormat(config.output_format),
            export_directory=config.export_directory,
            generate_complementary=config.generate_complementary,
            parallel_generation=config.parallel_generation,
            timeout_seconds=config.timeout_seconds
        )
        
        # Validate
        pipeline = DiagramPipeline(pipeline_config)
        issues = pipeline.validate_config()
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
        
    except Exception as e:
        logger.error(f"Config validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_service_stats():
    """Get service statistics"""
    try:
        pipeline = DiagramPipeline()
        catalog = pipeline.get_catalog_info()
        
        stats = {
            "catalog": catalog["stats"],
            "categories": len(set(d["category"] for d in catalog["diagrams"].values())),
            "tools": len(pipeline.generator.get_supported_tools()),
            "formats": len(pipeline.generator.get_supported_formats()),
            "active_pipelines": len(pipelines)
        }
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Background task for long-running operations
@router.post("/generate-async")
async def generate_diagrams_async(request: DiagramRequest, background_tasks: BackgroundTasks):
    """Start asynchronous diagram generation"""
    try:
        pipeline_id = str(uuid.uuid4())
        
        # Create and store pipeline
        config = PipelineConfig()
        if request.config:
            # Apply config (same as in generate endpoint)
            pass
        
        pipeline = DiagramPipeline(config)
        pipelines[pipeline_id] = pipeline
        
        # Start background task
        background_tasks.add_task(
            _run_pipeline_async,
            pipeline_id,
            pipeline,
            request.prd_content,
            request.codebase_path,
            request.approved_diagrams
        )
        
        return {
            "success": True,
            "pipeline_id": pipeline_id,
            "status": "started"
        }
        
    except Exception as e:
        logger.error(f"Async generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{pipeline_id}")
async def get_pipeline_status(pipeline_id: str):
    """Get status of asynchronous pipeline"""
    try:
        if pipeline_id not in pipelines:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        
        pipeline = pipelines[pipeline_id]
        status = pipeline.get_pipeline_status()
        
        return {
            "success": True,
            "pipeline_id": pipeline_id,
            "status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _run_pipeline_async(pipeline_id: str, pipeline: DiagramPipeline, 
                            prd_content: str, codebase_path: Optional[str],
                            approved_diagrams: Optional[List[str]]):
    """Run pipeline in background"""
    try:
        if approved_diagrams:
            pipeline.execute_interactive(prd_content, codebase_path, approved_diagrams)
        else:
            pipeline.execute(prd_content, codebase_path)
        
        # Store result (in practice, use proper storage)
        pipelines[pipeline_id] = pipeline
        
    except Exception as e:
        logger.error(f"Async pipeline {pipeline_id} failed: {e}")
        pipeline.status = PipelineStatus.FAILED
