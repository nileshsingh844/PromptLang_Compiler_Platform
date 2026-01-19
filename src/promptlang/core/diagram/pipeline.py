"""
Diagram Pipeline - Main orchestration for diagram generation workflow
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, Tuple
from enum import Enum
import logging
import time
from pathlib import Path

from .catalog import DiagramCatalog, DiagramType
from .analyzer import ProjectAnalyzer, ProjectContext
from .scorer import RelevanceScorer, DiagramRecommendation, SelectionTier
from .generator_simple import SimpleDiagramGenerator, GeneratedDiagram, DiagramTool, DiagramFormat

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineConfig:
    """Configuration for diagram generation pipeline"""
    max_diagrams: int = 50
    min_score_threshold: float = 0.0
    include_optional: bool = True
    preferred_tool: Optional[DiagramTool] = None
    output_format: DiagramFormat = DiagramFormat.SVG
    export_directory: str = "./diagrams"
    generate_complementary: bool = True
    parallel_generation: bool = True
    timeout_seconds: int = 300


@dataclass
class PipelineResult:
    """Result of diagram generation pipeline"""
    status: PipelineStatus
    recommendations: List[DiagramRecommendation] = field(default_factory=list)
    generated_diagrams: List[GeneratedDiagram] = field(default_factory=list)
    failed_diagrams: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)


class DiagramPipeline:
    """Main pipeline for diagram generation workflow"""
    
    def __init__(self, config: Optional[PipelineConfig] = None, llm_provider=None):
        self.config = config or PipelineConfig()
        self.llm_provider = llm_provider
        
        # Initialize components
        self.catalog = DiagramCatalog()
        self.analyzer = ProjectAnalyzer()
        self.scorer = RelevanceScorer()
        self.generator = SimpleDiagramGenerator()
        
        # Pipeline state
        self.status = PipelineStatus.PENDING
        self.start_time = 0.0
        self.end_time = 0.0
    
    def execute(self, prd_content: str, codebase_path: Optional[str] = None) -> PipelineResult:
        """Execute the complete diagram generation pipeline"""
        self.status = PipelineStatus.RUNNING
        self.start_time = time.time()
        
        try:
            logger.info("Starting diagram generation pipeline")
            
            # Step 1: Analyze project context
            logger.info("Step 1: Analyzing project context")
            context = self._analyze_project(prd_content, codebase_path)
            
            # Step 2: Score and rank diagrams
            logger.info("Step 2: Scoring and ranking diagrams")
            recommendations = self._score_diagrams(context)
            
            # Step 3: Filter recommendations
            logger.info("Step 3: Filtering recommendations")
            filtered_recommendations = self._filter_recommendations(recommendations)
            
            # Step 4: Generate diagrams
            logger.info("Step 4: Generating diagrams")
            generated_diagrams = self._generate_diagrams(filtered_recommendations, context)
            
            # Step 5: Create summary
            logger.info("Step 5: Creating summary")
            summary = self._create_summary(context, filtered_recommendations, generated_diagrams)
            
            # Step 6: Export if configured
            if self.config.export_directory:
                logger.info("Step 6: Exporting diagrams")
                self._export_diagrams(generated_diagrams)
            
            self.end_time = time.time()
            self.status = PipelineStatus.COMPLETED
            
            result = PipelineResult(
                status=self.status,
                recommendations=filtered_recommendations,
                generated_diagrams=generated_diagrams,
                failed_diagrams=[d.diagram_type.id for d in generated_diagrams if not d.success],
                execution_time=self.end_time - self.start_time,
                summary=summary,
                metadata={
                    "context": context,
                    "config": self.config,
                    "catalog_stats": self.catalog.get_stats()
                }
            )
            
            logger.info(f"Pipeline completed successfully in {result.execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.end_time = time.time()
            self.status = PipelineStatus.FAILED
            logger.error(f"Pipeline failed: {e}")
            
            return PipelineResult(
                status=self.status,
                execution_time=self.end_time - self.start_time,
                metadata={"error": str(e)}
            )
    
    def execute_interactive(self, prd_content: str, codebase_path: Optional[str] = None,
                           approved_diagrams: Optional[List[str]] = None) -> PipelineResult:
        """Execute pipeline with interactive approval"""
        self.status = PipelineStatus.RUNNING
        self.start_time = time.time()
        
        try:
            # Analyze project
            context = self._analyze_project(prd_content, codebase_path)
            
            # Get recommendations
            recommendations = self._score_diagrams(context)
            
            # Filter by user approval
            if approved_diagrams:
                filtered_recommendations = [
                    r for r in recommendations 
                    if r.diagram.id in approved_diagrams
                ]
            else:
                filtered_recommendations = self._filter_recommendations(recommendations)
            
            # Generate approved diagrams
            generated_diagrams = self._generate_diagrams(filtered_recommendations, context)
            
            # Create summary
            summary = self._create_summary(context, filtered_recommendations, generated_diagrams)
            
            self.end_time = time.time()
            self.status = PipelineStatus.COMPLETED
            
            return PipelineResult(
                status=self.status,
                recommendations=filtered_recommendations,
                generated_diagrams=generated_diagrams,
                execution_time=self.end_time - self.start_time,
                summary=summary,
                metadata={"context": context, "interactive": True}
            )
            
        except Exception as e:
            self.end_time = time.time()
            self.status = PipelineStatus.FAILED
            logger.error(f"Interactive pipeline failed: {e}")
            
            return PipelineResult(
                status=self.status,
                execution_time=self.end_time - self.start_time,
                metadata={"error": str(e)}
            )
    
    def get_recommendations_only(self, prd_content: str, codebase_path: Optional[str] = None) -> List[DiagramRecommendation]:
        """Get recommendations without generating diagrams"""
        context = self._analyze_project(prd_content, codebase_path)
        recommendations = self._score_diagrams(context)
        return self._filter_recommendations(recommendations)
    
    def _analyze_project(self, prd_content: str, codebase_path: Optional[str]) -> ProjectContext:
        """Analyze project to extract context"""
        if codebase_path:
            return self.analyzer.analyze_combined(prd_content, codebase_path)
        else:
            return self.analyzer.analyze_prd(prd_content)
    
    def _score_diagrams(self, context: ProjectContext) -> List[DiagramRecommendation]:
        """Score all diagrams against project context"""
        all_diagrams = self.catalog.get_all_diagrams()
        return self.scorer.score_diagrams(context, all_diagrams)
    
    def _filter_recommendations(self, recommendations: List[DiagramRecommendation]) -> List[DiagramRecommendation]:
        """Filter recommendations based on configuration"""
        filtered = []
        
        for rec in recommendations:
            # Apply score threshold
            if rec.relevance_score < self.config.min_score_threshold:
                continue
            
            # Apply tier filtering
            if rec.selection_tier == SelectionTier.OPTIONAL and not self.config.include_optional:
                continue
            
            # Apply max diagrams limit
            if len(filtered) >= self.config.max_diagrams:
                break
            
            filtered.append(rec)
        
        return filtered
    
    def _generate_diagrams(self, recommendations: List[DiagramRecommendation], 
                          context: ProjectContext) -> List[GeneratedDiagram]:
        """Generate diagrams for recommendations"""
        diagram_types = [rec.diagram for rec in recommendations]
        
        if self.config.parallel_generation:
            return self.generator.generate_batch(diagram_types, context, self.config.preferred_tool)
        else:
            generated = []
            for diagram_type in diagram_types:
                diagram = self.generator.generate_diagram(
                    diagram_type, context, self.config.preferred_tool, self.config.output_format
                )
                generated.append(diagram)
            return generated
    
    def _create_summary(self, context: ProjectContext, recommendations: List[DiagramRecommendation],
                       generated_diagrams: List[GeneratedDiagram]) -> Dict[str, Any]:
        """Create pipeline execution summary"""
        successful_diagrams = [d for d in generated_diagrams if d.success]
        failed_diagrams = [d for d in generated_diagrams if not d.success]
        
        summary = {
            "project": {
                "name": context.project_name,
                "type": context.project_type.value if context.project_type else "unknown",
                "phase": context.project_phase.value,
                "domains": list(context.domains),
                "technologies": list(context.technology_stack.languages),
            },
            "recommendations": {
                "total": len(recommendations),
                "by_tier": {
                    "must_generate": len([r for r in recommendations if r.selection_tier == SelectionTier.MUST_GENERATE]),
                    "should_generate": len([r for r in recommendations if r.selection_tier == SelectionTier.SHOULD_GENERATE]),
                    "could_generate": len([r for r in recommendations if r.selection_tier == SelectionTier.COULD_GENERATE]),
                    "optional": len([r for r in recommendations if r.selection_tier == SelectionTier.OPTIONAL]),
                },
                "average_score": sum(r.relevance_score for r in recommendations) / len(recommendations) if recommendations else 0,
                "top_5": [
                    {
                        "name": r.diagram.name,
                        "score": r.relevance_score,
                        "tier": r.selection_tier.value,
                        "reasoning": r.reasoning[:2]
                    }
                    for r in recommendations[:5]
                ]
            },
            "generation": {
                "total_attempted": len(generated_diagrams),
                "successful": len(successful_diagrams),
                "failed": len(failed_diagrams),
                "success_rate": len(successful_diagrams) / len(generated_diagrams) if generated_diagrams else 0,
                "tools_used": list(set(d.tool for d in successful_diagrams)),
                "formats_generated": list(set(d.format for d in successful_diagrams)),
            },
            "execution": {
                "status": self.status.value,
                "execution_time": self.end_time - self.start_time,
                "config": {
                    "max_diagrams": self.config.max_diagrams,
                    "min_score_threshold": self.config.min_score_threshold,
                    "include_optional": self.config.include_optional,
                    "preferred_tool": self.config.preferred_tool.value if self.config.preferred_tool else None,
                    "output_format": self.config.output_format.value,
                }
            }
        }
        
        return summary
    
    def _export_diagrams(self, generated_diagrams: List[GeneratedDiagram]):
        """Export diagrams to configured directory"""
        successful_diagrams = [d for d in generated_diagrams if d.success]
        
        if successful_diagrams:
            exported = self.generator.export_diagrams(successful_diagrams, self.config.export_directory)
            logger.info(f"Exported {len(exported)} diagrams to {self.config.export_directory}")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": self.end_time - self.start_time if self.end_time > 0 else 0,
            "config": self.config
        }
    
    def cancel(self):
        """Cancel pipeline execution"""
        self.status = PipelineStatus.CANCELLED
        self.end_time = time.time()
        logger.info("Pipeline cancelled")
    
    def reset(self):
        """Reset pipeline state"""
        self.status = PipelineStatus.PENDING
        self.start_time = 0.0
        self.end_time = 0.0
        logger.info("Pipeline reset")
    
    def get_catalog_info(self) -> Dict[str, Any]:
        """Get catalog information"""
        return self.catalog.export_catalog()
    
    def validate_config(self) -> List[str]:
        """Validate pipeline configuration"""
        issues = []
        
        if self.config.max_diagrams <= 0:
            issues.append("max_diagrams must be greater than 0")
        
        if not (0 <= self.config.min_score_threshold <= 1):
            issues.append("min_score_threshold must be between 0 and 1")
        
        if self.config.timeout_seconds <= 0:
            issues.append("timeout_seconds must be greater than 0")
        
        # Check if preferred tool is supported
        if self.config.preferred_tool:
            supported_tools = self.generator.get_supported_tools()
            if self.config.preferred_tool not in supported_tools:
                issues.append(f"Preferred tool {self.config.preferred_tool.value} is not supported")
        
        # Check if output format is supported
        supported_formats = self.generator.get_supported_formats()
        if self.config.output_format not in supported_formats:
            issues.append(f"Output format {self.config.output_format.value} is not supported")
        
        return issues
    
    def estimate_execution_time(self, num_diagrams: int) -> float:
        """Estimate execution time for given number of diagrams"""
        # Base time for analysis and scoring
        base_time = 5.0  # seconds
        
        # Time per diagram (varies by complexity)
        avg_time_per_diagram = 2.0  # seconds
        
        estimated_time = base_time + (num_diagrams * avg_time_per_diagram)
        
        # Add buffer for parallel processing overhead
        if self.config.parallel_generation:
            estimated_time *= 0.7  # Parallel processing reduces time
        
        return estimated_time
    
    def get_recommendation_preview(self, prd_content: str, codebase_path: Optional[str] = None,
                                 limit: int = 10) -> Dict[str, Any]:
        """Get a preview of recommendations without full scoring"""
        context = self._analyze_project(prd_content, codebase_path)
        
        # Get a sample of diagrams for quick preview
        all_diagrams = self.catalog.get_all_diagrams()
        sample_diagrams = all_diagrams[:limit]
        
        # Quick scoring (simplified)
        preview_recommendations = []
        for diagram in sample_diagrams:
            # Simple relevance check based on keywords and domains
            score = 0.0
            reasoning = []
            
            # Check domain match
            if context.domains and diagram.domains:
                domain_match = len(context.domains.intersection(diagram.domains))
                if domain_match > 0:
                    score += 0.3
                    reasoning.append(f"Domain match: {domain_match} domains")
            
            # Check phase match
            if context.project_phase in diagram.relevant_phases:
                score += 0.2
                reasoning.append(f"Relevant for {context.project_phase.value} phase")
            
            # Check stakeholder match
            if context.stakeholders and diagram.target_stakeholders:
                stakeholder_match = len(context.stakeholders.intersection(diagram.target_stakeholders))
                if stakeholder_match > 0:
                    score += 0.1
                    reasoning.append(f"Relevant for {stakeholder_match} stakeholder types")
            
            # Determine tier
            if score >= 0.7:
                tier = SelectionTier.MUST_GENERATE
            elif score >= 0.5:
                tier = SelectionTier.SHOULD_GENERATE
            elif score >= 0.3:
                tier = SelectionTier.COULD_GENERATE
            else:
                tier = SelectionTier.OPTIONAL
            
            preview_recommendations.append({
                "id": diagram.id,
                "name": diagram.name,
                "category": diagram.category.value,
                "estimated_score": score,
                "estimated_tier": tier.value,
                "reasoning": reasoning,
                "complexity": diagram.complexity.value
            })
        
        # Sort by estimated score
        preview_recommendations.sort(key=lambda x: x["estimated_score"], reverse=True)
        
        return {
            "project_context": {
                "name": context.project_name,
                "type": context.project_type.value if context.project_type else "unknown",
                "domains": list(context.domains),
                "technologies": list(context.technology_stack.languages),
                "stakeholders": [s.value for s in context.stakeholders]
            },
            "preview_recommendations": preview_recommendations,
            "catalog_stats": self.catalog.get_stats(),
            "estimated_total_diagrams": len(all_diagrams),
            "estimated_execution_time": self.estimate_execution_time(len(all_diagrams))
        }
