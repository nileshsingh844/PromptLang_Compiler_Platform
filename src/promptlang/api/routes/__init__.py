"""API routes."""

from promptlang.api.routes.generate import router as generate_router
from promptlang.api.routes.validate import router as validate_router
from promptlang.api.routes.optimize import router as optimize_router
from promptlang.api.routes.diagrams import router as diagrams_router
from promptlang.api.routes.prompt_generation import router as prompt_generation_router

__all__ = [
    "generate_router",
    "validate_router",
    "optimize_router",
    "diagrams_router",
    "prompt_generation_router",
]
