from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel


class EnrichedContext(BaseModel):
    best_practices: List[Dict[str, Any]]
    examples: List[Dict[str, Any]]
    domain_knowledge: List[Dict[str, Any]]
    meta: Dict[str, Any]
