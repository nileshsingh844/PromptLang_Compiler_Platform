"""IR builder orchestrating translation from human input to IR."""

import logging
from typing import Any, Dict, Optional

from promptlang.core.clarification.engine import ClarificationEngine
from promptlang.core.intent.router import IntentRouter
from promptlang.core.translator.llm_provider import LLMProvider, get_llm_provider

logger = logging.getLogger(__name__)


class IRBuilder:
    """Builds PromptLang IR from human input."""

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        intent_router: Optional[IntentRouter] = None,
        clarification_engine: Optional[ClarificationEngine] = None,
    ):
        """Initialize IR builder.

        Args:
            llm_provider: LLM provider instance
            intent_router: Intent router instance
            clarification_engine: Clarification engine instance
        """
        self.llm_provider = llm_provider or get_llm_provider()
        self.intent_router = intent_router or IntentRouter()
        self.clarification_engine = clarification_engine or ClarificationEngine()

    async def build(
        self,
        input_text: str,
        explicit_intent: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Build IR from human input.

        Args:
            input_text: Human input text
            explicit_intent: Explicitly provided intent
            context: Additional context

        Returns:
            PromptLang IR dictionary
        """
        # Stage 1: Route intent
        intent = self.intent_router.route(input_text, explicit_intent=explicit_intent)

        # Stage 1.5: Clarification (questions or assumptions)
        questions, assumptions = self.clarification_engine.clarify(input_text, intent)

        # Apply assumptions to context
        if context is None:
            context = {}
        context.update(assumptions)

        # Stage 2: Translate to IR
        ir = await self.llm_provider.translate_to_ir(input_text, intent, context)

        # Add any clarifications/questions as metadata
        if questions:
            ir.setdefault("meta", {})["clarification_questions"] = questions

        logger.info(f"IR built successfully for intent: {intent}")
        return ir
