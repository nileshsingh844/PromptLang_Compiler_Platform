from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional, Any

from pydantic import BaseModel


class GitHubContent(BaseModel):
    readme: str
    docs: Dict[str, str]
    package_manifest: dict
    license: str
    repo_metadata: dict
    file_structure: dict


class GitHubParser:
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token

    async def extract(self, repo_url: str) -> GitHubContent:
        cache_path = self._cache_path(repo_url)
        cached = self._read_cache(cache_path)
        if cached is not None:
            return GitHubContent.model_validate(cached)

        # Lazy import so repo can run without PyGithub unless GitHub extraction is used
        try:
            from github import Github  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "PyGithub is required for GitHub extraction. Install 'PyGithub' to use input_type=github."
            ) from e

        gh = Github(self.github_token) if self.github_token else Github()

        owner, name = self._parse_owner_repo(repo_url)
        repo = gh.get_repo(f"{owner}/{name}")

        repo_metadata = {
            "full_name": repo.full_name,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "topics": getattr(repo, "get_topics", lambda: [])(),
            "html_url": repo.html_url,
            "default_branch": repo.default_branch,
        }

        readme = ""
        try:
            readme = repo.get_readme().decoded_content.decode("utf-8", errors="replace")
        except Exception:
            readme = ""

        docs: Dict[str, str] = {}
        for docs_path in ("docs", "doc", "documentation"):
            try:
                docs.update(self._extract_markdown_tree(repo, docs_path))
                if docs:
                    break
            except Exception:
                continue

        package_manifest: Dict[str, Any] = {}
        for manifest in ("package.json", "requirements.txt", "pyproject.toml", "go.mod"):
            try:
                content_file = repo.get_contents(manifest)
                raw = content_file.decoded_content.decode("utf-8", errors="replace")
                package_manifest = self._parse_manifest(manifest, raw)
                if package_manifest:
                    break
            except Exception:
                continue

        license_text = ""
        for license_name in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
            try:
                license_file = repo.get_contents(license_name)
                license_text = license_file.decoded_content.decode("utf-8", errors="replace")
                break
            except Exception:
                continue

        file_structure = self._build_directory_tree(repo)

        result = GitHubContent(
            readme=readme,
            docs=docs,
            package_manifest=package_manifest,
            license=license_text,
            repo_metadata=repo_metadata,
            file_structure=file_structure,
        )

        self._write_cache(cache_path, result.dict())
        return result

    def _parse_owner_repo(self, repo_url: str) -> tuple[str, str]:
        s = repo_url.strip().rstrip("/")
        if s.endswith(".git"):
            s = s[:-4]
        parts = s.split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub repo URL: {repo_url}")
        return parts[-2], parts[-1]

    def _parse_manifest(self, filename: str, raw: str) -> dict:
        if filename == "package.json":
            try:
                return json.loads(raw)
            except Exception:
                return {}
        if filename in ("requirements.txt", "go.mod"):
            return {"raw": raw}
        if filename == "pyproject.toml":
            return {"raw": raw}
        return {}

    def _extract_markdown_tree(self, repo: Any, root_path: str) -> Dict[str, str]:
        docs: Dict[str, str] = {}
        contents = repo.get_contents(root_path)
        stack = list(contents) if isinstance(contents, list) else [contents]

        while stack:
            node = stack.pop()
            if node.type == "dir":
                try:
                    stack.extend(repo.get_contents(node.path))
                except Exception:
                    continue
            else:
                if node.path.lower().endswith(".md"):
                    try:
                        docs[node.path] = node.decoded_content.decode("utf-8", errors="replace")
                    except Exception:
                        continue

        return docs

    def _build_directory_tree(self, repo: Any) -> dict:
        def walk(path: str, depth: int) -> dict:
            if depth <= 0:
                return {}
            try:
                contents = repo.get_contents(path)
            except Exception:
                return {}

            nodes = contents if isinstance(contents, list) else [contents]
            tree: Dict[str, Any] = {}
            for n in nodes:
                name = Path(n.path).name
                if n.type == "dir":
                    tree[name] = walk(n.path, depth - 1)
                else:
                    tree[name] = "file"
            return tree

        # Depth cap to keep it fast and small
        return walk("", depth=4)

    def _cache_path(self, repo_url: str) -> Path:
        repo_hash = hashlib.sha256(repo_url.encode("utf-8")).hexdigest()[:16]
        base = Path("knowledge/extracted")
        base.mkdir(parents=True, exist_ok=True)
        return base / f"{repo_hash}.json"

    def _read_cache(self, path: Path) -> Optional[dict]:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _write_cache(self, path: Path, payload: dict) -> None:
        try:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            return
