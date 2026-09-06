#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
DIST = ROOT / "dist"


def load(name: str):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def render_resources(item: dict) -> str:
    resources = item.get("resources", []) + item.get("links", [])
    if not resources:
        return ""
    parts = []
    for resource in resources:
        label = esc(resource["label"])
        url = resource.get("url")
        if url:
            parts.append(f'<a href="{esc(url)}">{label}<span class="external" aria-hidden="true">↗</span></a>')
        else:
            parts.append(f'<span>{label}</span>')
    return '<p class="work-resources"><span class="work-resources-label">Resources:</span> ' + " · ".join(parts) + "</p>"


def render_abstract(item: dict) -> str:
    abstract = item.get("abstract", "").strip()
    return f'<p class="work-abstract">{esc(abstract)}</p>' if abstract else ""


def enrich_page(path: Path, items: list[dict]) -> None:
    page = path.read_text(encoding="utf-8")
    blocks = list(re.finditer(r'<article class="work-card".*?</article>', page, flags=re.S))
    replacements: list[tuple[int, int, str]] = []

    for match in blocks:
        block = match.group(0)
        item = next((x for x in items if esc(x["title"]) in block), None)
        if not item:
            continue
        extra = render_abstract(item) + render_resources(item)
        if not extra:
            continue
        marker = "\n      </div>\n    </article>"
        if marker not in block:
            continue
        block = block.replace(marker, f"\n        {extra}{marker}", 1)
        replacements.append((match.start(), match.end(), block))

    for start, end, block in reversed(replacements):
        page = page[:start] + block + page[end:]
    path.write_text(page, encoding="utf-8")


enrich_page(DIST / "research" / "index.html", load("research.json"))
enrich_page(DIST / "policy" / "index.html", [x for x in load("policy.json") if x.get("type") != "talk"])

css_path = DIST / "assets" / "site-v4.css"
css = css_path.read_text(encoding="utf-8")
css += """

/* Content-audit details: abstracts and secondary resources */
.work-abstract { margin: 12px 0 0; color: var(--ink); font-size: .88rem; line-height: 1.58; max-width: 76ch; }
.work-resources { margin: 10px 0 0; color: var(--accent-dark); font-size: .78rem; line-height: 1.5; }
.work-resources-label { color: var(--muted); }
.work-resources a:hover { text-decoration: underline; text-underline-offset: 3px; }
"""
css_path.write_text(css, encoding="utf-8")
print("Rendered abstracts and secondary resources.")
