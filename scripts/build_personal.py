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


# Personal content is preserved from the legacy website, but it is intentionally
# secondary to the professional site architecture. Keep it in the footer rather
# than promoting it to the primary navigation.
def add_personal_footer(page_html: str) -> str:
    if 'href="/personal/"' in page_html:
        return page_html
    footer_match = re.search(r'(<div class="footer-links">)(.*?)(</div>)', page_html, flags=re.S)
    if not footer_match:
        return page_html
    links = footer_match.group(2)
    personal_link = '<a href="/personal/">Personal</a>'
    photos_pos = links.find('<a href="/photos/">')
    if photos_pos >= 0:
        links = links[:photos_pos] + personal_link + links[photos_pos:]
    else:
        links += personal_link
    return page_html[:footer_match.start(2)] + links + page_html[footer_match.end(2):]


for html_path in DIST.rglob("*.html"):
    current = html_path.read_text(encoding="utf-8")
    current = add_personal_footer(current)
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
print(f"Built Personal page with {len(data['photos'])} legacy photos as a secondary footer destination.")
