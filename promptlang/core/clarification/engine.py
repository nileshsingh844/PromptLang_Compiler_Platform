"""Clarification engine for gathering missing information."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ClarificationEngine:
    """Engine for asking clarification questions or making assumptions."""

    MAX_QUESTIONS = 3

    def __init__(self, max_questions: int = MAX_QUESTIONS):
        """Initialize clarification engine.

        Args:
            max_questions: Maximum questions to ask before making assumptions
        """
        self.max_questions = max_questions

    def clarify(
        self, input_text: str, intent: str, partial_ir: Optional[Dict[str, Any]] = None
    ) -> tuple[List[str], Dict[str, Any]]:
        """Generate clarification questions or make assumptions.

        Args:
            input_text: User input
            intent: Detected intent
            partial_ir: Partial IR data if available

        Returns:
            Tuple of (questions_list, assumptions_dict)
        """
        questions: List[str] = []
        assumptions: Dict[str, Any] = {}

        # Determine what needs clarification based on intent
        if intent == "scaffold":
            # Check for missing context
            if not self._has_language_hint(input_text):
                if len(questions) < self.max_questions:
                    questions.append("What programming language should we use?")
                else:
                    assumptions["language"] = "python"  # Default

            if not self._has_framework_hint(input_text):
                if len(questions) < self.max_questions:
                    questions.append("Which framework should we use?")
                else:
                    assumptions["framework"] = None  # No default

        elif intent == "debug":
            # Check for error context
            if not self._has_error_context(input_text):
                if len(questions) < self.max_questions:
                    questions.append("Can you provide the error message or traceback?")
                else:
                    assumptions["error_log"] = ""

        # If we have questions, return them
        if questions:
            return questions, {}

        # Otherwise, return assumptions
        logger.info(f"Making assumptions: {assumptions}")
        return [], assumptions

    def _has_language_hint(self, text: str) -> bool:
        """Check if text contains language hint."""
        languages = ["python", "javascript", "typescript", "java", "go", "rust"]
        text_lower = text.lower()
        return any(lang in text_lower for lang in languages)

    def _has_framework_hint(self, text: str) -> bool:
        """Check if text contains framework hint."""
        frameworks = ["fastapi", "flask", "django", "react", "vue", "next"]
        text_lower = text.lower()
        return any(fw in text_lower for fw in frameworks)

    def _has_error_context(self, text: str) -> bool:
        """Check if text contains error context."""
        error_indicators = ["error", "exception", "traceback", "failed", "crash"]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in error_indicators)
