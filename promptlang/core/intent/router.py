"""Intent router for classifying user input."""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class IntentRouter:
    """Routes user input to appropriate intent category."""

    INTENTS = ["scaffold", "debug", "refactor", "explain", "devops"]

    # Intent detection patterns
    PATTERNS = {
        "scaffold": [
            r"create.*project",
            r"build.*from.*scratch",
            r"scaffold",
            r"generate.*structure",
            r"new.*application",
            r"setup.*project",
        ],
        "debug": [
            r"fix.*error",
            r"why.*not.*work",
            r"debug",
            r"trace.*issue",
            r"resolve.*problem",
            r"error.*log",
        ],
        "refactor": [
            r"refactor",
            r"improve.*code",
            r"clean.*up",
            r"optimize.*structure",
            r"restructure",
        ],
        "explain": [
            r"explain",
            r"how.*work",
            r"what.*do",
            r"understand",
            r"document",
        ],
        "devops": [
            r"deploy",
            r"docker",
            r"ci/cd",
            r"kubernetes",
            r"infrastructure",
            r"production",
        ],
    }

    def route(self, input_text: str, explicit_intent: Optional[str] = None) -> str:
        """Route input to intent.

        Args:
            input_text: User input text
            explicit_intent: Explicitly provided intent (takes precedence)

        Returns:
            Detected intent
        """
        if explicit_intent and explicit_intent in self.INTENTS:
            return explicit_intent

        input_lower = input_text.lower()

        # Score each intent
        scores = {}
        for intent, patterns in self.PATTERNS.items():
            score = sum(1 for pattern in patterns if re.search(pattern, input_lower))
            if score > 0:
                scores[intent] = score

        if scores:
            # Return intent with highest score
            detected = max(scores, key=scores.get)  # type: ignore
            logger.info(f"Intent detected: {detected} (score: {scores[detected]})")
            return detected

        # Default to scaffold
        logger.info("No intent detected, defaulting to scaffold")
        return "scaffold"
