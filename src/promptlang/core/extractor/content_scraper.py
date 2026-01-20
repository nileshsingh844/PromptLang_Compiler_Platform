from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel


class ScrapedContent(BaseModel):
    title: str
    main_content: str
    metadata: dict
    links: list
    images: list
    content_type: str


class ContentScraper:
    async def scrape_url(self, url: str) -> ScrapedContent:
        cache_path = self._cache_path(url)
        cached = self._read_cache(cache_path)
        if cached is not None:
            return ScrapedContent.model_validate(cached)

        html = await self._fetch_html(url)
        cleaned = self._clean_html(html)

        try:
            from bs4 import BeautifulSoup  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "beautifulsoup4 is required for URL scraping. Install 'beautifulsoup4' to use input_type=url."
            ) from e

        soup = BeautifulSoup(cleaned, "html.parser")
        title = (soup.title.string.strip() if soup.title and soup.title.string else "").strip()

        # Extract main content: prefer <main>, otherwise body
        main_node = soup.find("main") or soup.find("article") or soup.body
        main_text = ""
        if main_node:
            main_text = main_node.get_text("\n", strip=True)

        # Links/images
        links: List[str] = []
        for a in soup.find_all("a"):
            href = a.get("href")
            if href and isinstance(href, str):
                links.append(href)
        links = list(dict.fromkeys(links))

        images: List[str] = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and isinstance(src, str):
                images.append(src)
        images = list(dict.fromkeys(images))

        metadata: Dict[str, Any] = {
            "url": url,
        }
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            metadata["description"] = desc.get("content")

        content_type = self._detect_content_type(soup)

        result = ScrapedContent(
            title=title,
            main_content=main_text,
            metadata=metadata,
            links=links,
            images=images,
            content_type=content_type,
        )

        self._write_cache(cache_path, result.dict())
        return result

    async def _fetch_html(self, url: str) -> str:
        # Lazy import so repo can run without Playwright unless URL scraping is used
        try:
            from playwright.async_api import async_playwright  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "playwright is required for URL scraping. Install 'playwright' and run 'playwright install' to use input_type=url."
            ) from e

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30_000)
                return await page.content()
            finally:
                await browser.close()

    def _clean_html(self, html: str) -> str:
        # Very lightweight cleanup; BeautifulSoup will handle most.
        return html

    def _detect_content_type(self, soup: Any) -> str:
        url = ""
        try:
            url = soup.find("meta", attrs={"property": "og:url"}).get("content")  # type: ignore
        except Exception:
            url = ""

        text = (soup.get_text(" ", strip=True) or "").lower()
        if any(k in text for k in ["api reference", "documentation", "docs", "getting started"]):
            return "documentation"
        if any(k in text for k in ["pricing", "features", "sign up", "get started"]):
            return "product_page"
        if any(k in text for k in ["posted", "minutes read", "subscribe"]):
            return "article"
        return "landing_page"

    def _cache_path(self, url: str) -> Path:
        h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        base = Path("knowledge/extracted")
        base.mkdir(parents=True, exist_ok=True)
        return base / f"url_{h}.json"

    def _read_cache(self, path: Path) -> Dict[str, Any] | None:
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
