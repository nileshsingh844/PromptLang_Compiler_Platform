"""Unit tests for intent router."""

import pytest

from promptlang.core.intent.router import IntentRouter


def test_route_scaffold():
    """Test scaffold intent detection."""
    router = IntentRouter()
    intent = router.route("Create a new FastAPI project")
    assert intent == "scaffold"


def test_route_debug():
    """Test debug intent detection."""
    router = IntentRouter()
    intent = router.route("Fix this error: AttributeError")
    assert intent == "debug"


def test_route_explicit():
    """Test explicit intent override."""
    router = IntentRouter()
    intent = router.route("some text", explicit_intent="refactor")
    assert intent == "refactor"


def test_route_default():
    """Test default to scaffold."""
    router = IntentRouter()
    intent = router.route("random text without intent markers")
    assert intent == "scaffold"
