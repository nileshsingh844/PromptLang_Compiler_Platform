"""FastAPI application main entry point."""

import logging
import os

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from promptlang.api.routes import generate_router, validate_router, optimize_router, diagrams_router
from promptlang.api.routes.generate import init_orchestrator
from promptlang.core.cache.manager import CacheManager

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

logger = structlog.get_logger()

app = FastAPI(
    title="PromptLang Compiler Platform API",
    description="Transform Human Input → PromptLang IR → Optimized IR → Model Dialect → Contract Enforced Output",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate_router)
app.include_router(validate_router)
app.include_router(optimize_router)
app.include_router(diagrams_router)


@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup."""
    logger.info("Initializing PromptLang API")
    cache_manager = CacheManager(
        l2_redis_url=os.getenv("REDIS_URL"),
    )
    init_orchestrator(cm=cache_manager)
    logger.info("PromptLang API ready")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "PromptLang Compiler Platform",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
