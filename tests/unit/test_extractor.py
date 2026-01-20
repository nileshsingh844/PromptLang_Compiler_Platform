import sys
import types

import pytest
from promptlang.core.extractor.github_parser import GitHubParser, GitHubContent
from promptlang.core.extractor.knowledge_card_builder import KnowledgeCardBuilder
from promptlang.core.extractor.content_scraper import ContentScraper


@pytest.mark.asyncio
async def test_github_parser_extracts_readme(monkeypatch, tmp_path):
    class FakeReadme:
        decoded_content = b"# Hello README"

    class FakeFile:
        def __init__(self, content: bytes):
            self.decoded_content = content
            self.type = "file"
            self.path = "README.md"

    class FakeRepo:
        full_name = "org/repo"
        description = "desc"
        stargazers_count = 1
        forks_count = 2
        html_url = "https://github.com/org/repo"
        default_branch = "main"

        def get_topics(self):
            return ["topic1"]

        def get_readme(self):
            return FakeReadme()

        def get_contents(self, path):
            if path == "package.json":
                return FakeFile(b"{\"name\":\"repo\"}")
            raise Exception("not found")

    class FakeGithub:
        def __init__(self, token=None):
            pass

        def get_repo(self, full_name):
            return FakeRepo()

    # GitHubParser performs a local import: `from github import Github`
    # Inject a fake `github` module into sys.modules so that import succeeds.
    fake_github_module = types.ModuleType("github")
    fake_github_module.Github = FakeGithub
    monkeypatch.setitem(sys.modules, "github", fake_github_module)

    parser = GitHubParser()
    content = await parser.extract("https://github.com/org/repo")

    assert isinstance(content, GitHubContent)
    assert "Hello README" in content.readme


@pytest.mark.asyncio
async def test_knowledge_card_builder_generates_valid_schema():
    builder = KnowledgeCardBuilder(llm_manager=None)
    card = await builder.build_from_text("Build a REST API for todos")

    assert card.project_name
    assert card.project_type
    assert isinstance(card.features, list)
    assert isinstance(card.tech_stack, dict)


def test_content_scraper_detects_content_type(monkeypatch):
    scraper = ContentScraper()

    class FakeSoup:
        def __init__(self, text):
            self._text = text

        def get_text(self, sep=" ", strip=True):
            return self._text

        def find(self, *args, **kwargs):
            return None

    soup = FakeSoup("API Reference Documentation Getting Started")
    assert scraper._detect_content_type(soup) == "documentation"

    soup2 = FakeSoup("Pricing Features Sign up")
    assert scraper._detect_content_type(soup2) == "product_page"
