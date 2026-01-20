from promptlang.core.prompt_compiler.engine import PromptTemplateEngine


def test_template_engine_lists_templates():
    engine = PromptTemplateEngine()
    templates = engine.list_templates()
    assert "universal_cursor_prompt" in templates


def test_template_engine_renders_universal_template():
    engine = PromptTemplateEngine()

    out = engine.render(
        "universal_cursor_prompt",
        ir={
            "task": {"description": "Build a production API"},
            "constraints": {"must_have": ["tests"], "must_avoid": ["secrets"]},
            "context": {"stack": {"language": "Python", "framework": "FastAPI", "architecture": "monolith"}},
        },
        knowledge_card={"project_name": "demo", "project_type": "api", "domain": "general"},
        enriched_context={
            "best_practices": [{"title": "BP", "url": "http://x", "text": "do x"}],
            "examples": [],
            "domain_knowledge": [],
        },
    )

    assert "CURSOR PROMPT" in out
    assert "demo" in out
    assert "Best Practices" in out
    assert "http://x" in out
