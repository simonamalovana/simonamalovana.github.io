#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CONTENT = ROOT / "content"

links = json.loads((CONTENT / "presentation_links.json").read_text(encoding="utf-8"))
pres = json.loads((CONTENT / "presentations.json").read_text(encoding="utf-8"))
path = DIST / "presentations" / "index.html"
page = path.read_text(encoding="utf-8")


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def external(url: str, label: str) -> str:
    return f'<a href="{esc(url)}">{label}<span class="external" aria-hidden="true">↗</span></a>'


def enrich_article(page_html: str, css_class: str, event: str, details: str | None, cfg: dict) -> str:
    blocks = list(re.finditer(rf'<article class="{re.escape(css_class)}">.*?</article>', page_html, flags=re.S))
    e = esc(event)
    d = esc(details) if details else None
    target = None
    for m in blocks:
        block = m.group(0)
        if e in block and (d is None or d in block):
            target = (m, block)
            break
    if not target:
        return page_html
    m, block = target

    event_url = cfg.get("event_url")
    if event_url:
        block = re.sub(r'<h3>.*?</h3>', f'<h3>{external(event_url, e)}</h3>', block, count=1, flags=re.S)

    details_url = cfg.get("details_url")
    if details_url and d:
        block = block.replace(f'<p>{d}</p>', f'<p>{external(details_url, d)}</p>', 1)

    extra_links = cfg.get("links", [])
    if extra_links:
        rendered = " · ".join(external(x["url"], esc(x["label"])) for x in extra_links)
        insert = f'<p class="presentation-links">{rendered}</p>'
        block = block.replace('</div></article>', f'{insert}</div></article>', 1)

    return page_html[:m.start()] + block + page_html[m.end():]


for item in pres["presentations"]:
    key = f'{item["year"]}|{item["event"]}|{item.get("details", "")}'
    cfg = links.get("presentations", {}).get(key)
    if cfg:
        page = enrich_article(page, "presentation-row", item["event"], item.get("details"), cfg)

for item in pres["organized"]:
    cfg = links.get("organized", {}).get(item["event"])
    if cfg:
        page = enrich_article(page, "organized-row", item["event"], None, cfg)

path.write_text(page, encoding="utf-8")
print("Restored presentation links.")
