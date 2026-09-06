#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CONTENT = ROOT / "content"
data = json.loads((CONTENT / "personal.json").read_text(encoding="utf-8"))


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


figures = []
for photo in data["photos"]:
    src = f'/assets/images/personal/{esc(photo["file"])}'
    caption = esc(photo["caption"])
    figures.append(
        f'<figure><img loading="lazy" decoding="async" src="{src}" alt="{caption}">'
        f'<figcaption>{caption}</figcaption></figure>'
    )

body = f'''
<section class="page-head"><div class="shell narrow"><span class="signature-rule" aria-hidden="true"></span><h1>Personal</h1><p>{esc(data["description"])}</p></div></section>
<section class="content-section"><div class="shell"><div class="section-head"><h2>{esc(data["title"])}</h2></div><div class="photo-grid personal-photo-grid">{"".join(figures)}</div></div></section>
'''

template = (DIST / "photos" / "index.html").read_text(encoding="utf-8")
description = "Personal gallery of favorite places and landscapes photographed by Simona Malovaná."
page = template
page = page.replace("Photos — Simona Malovaná", "Personal — Simona Malovaná")
page = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(description)}">', page, count=1)
page = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(description)}">', page, count=1)
page = page.replace("https://simonamalovana.com/photos/", "https://simonamalovana.com/personal/")
page = re.sub(r'<main id="main" tabindex="-1">.*?</main>', f'<main id="main" tabindex="-1">{body}</main>', page, count=1, flags=re.S)

personal_dir = DIST / "personal"
personal_dir.mkdir(exist_ok=True)
(personal_dir / "index.html").write_text(page, encoding="utf-8")


def add_personal_nav(page_html: str, active: bool = False) -> str:
    if 'href="/personal/"' in page_html:
        return page_html
    match = re.search(r'<nav class="main-nav" aria-label="Main navigation">(.*?)</nav>', page_html, flags=re.S)
    if not match:
        return page_html
    nav = match.group(1)
    link = '<a href="/personal/">Personal</a>'
    about_pos = nav.find('<a href="/about/"')
    if about_pos >= 0:
        nav = nav[:about_pos] + link + nav[about_pos:]
    else:
        nav += link
    if active:
        nav = nav.replace(link, '<a href="/personal/" class="active" aria-current="page">Personal</a>')
    return page_html[:match.start(1)] + nav + page_html[match.end(1):]


for html_path in DIST.rglob("*.html"):
    current = html_path.read_text(encoding="utf-8")
    current = add_personal_nav(current, active=(html_path == personal_dir / "index.html"))
    html_path.write_text(current, encoding="utf-8")

sitemap_path = DIST / "sitemap.xml"
sitemap = sitemap_path.read_text(encoding="utf-8")
entry = "  <url><loc>https://simonamalovana.com/personal/</loc></url>\n"
if "https://simonamalovana.com/personal/" not in sitemap:
    sitemap = sitemap.replace("</urlset>", entry + "</urlset>")
    sitemap_path.write_text(sitemap, encoding="utf-8")

css_path = DIST / "assets" / "site-v4.css"
css = css_path.read_text(encoding="utf-8")
css += """

/* Restored Personal gallery */
.personal-photo-grid img { width: 100%; height: auto; }
.personal-photo-grid figcaption { text-align: left; color: var(--muted); }
"""
css_path.write_text(css, encoding="utf-8")
print(f"Built Personal page with {len(data['photos'])} legacy photos.")
