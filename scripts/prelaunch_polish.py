#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
site = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
email = site["email"]
email_link = f'<a href="mailto:{email}">Email</a>'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Pre-launch polish anchor not found: {label}")
    return text.replace(old, new, 1)


# Load the small override stylesheet after the stable V4 stylesheet on every page.
shutil.copy2(ASSETS / "prelaunch.css", DIST / "assets" / "prelaunch.css")
for html_path in DIST.rglob("*.html"):
    page = html_path.read_text(encoding="utf-8")
    if '/assets/prelaunch.css' not in page:
        page = page.replace(
            '<link rel="stylesheet" href="/assets/site-v4.css">',
            '<link rel="stylesheet" href="/assets/site-v4.css">\n  <link rel="stylesheet" href="/assets/prelaunch.css">',
            1,
        )

    # The professional top-level architecture is deliberately concise.
    # Personal is preserved as legacy content, but belongs in the footer only.
    page = re.sub(
        r'(<nav class="main-nav" aria-label="Main navigation">.*?)'
        r'<a href="/personal/"(?: class="active" aria-current="page")?>Personal</a>'
        r'(.*?</nav>)',
        r'\1\2',
        page,
        flags=re.S,
    )

    # Distinguish professional press/conference images from the Personal gallery.
    page = page.replace('<a href="/photos/">Photos</a>', '<a href="/photos/">Media photos</a>')

    # Make direct contact visible on every page without bloating primary navigation.
    if f'mailto:{email}' not in page:
        page = page.replace(
            f'<a href="{site["github"]}">GitHub ↗</a>',
            f'<a href="{site["github"]}">GitHub ↗</a>{email_link}',
            1,
        )

    html_path.write_text(page, encoding="utf-8")


home_path = DIST / "index.html"
home = home_path.read_text(encoding="utf-8")

# Recent mixes research and policy/media, so the navigation should expose both destinations.
home = replace_once(
    home,
    '<div class="section-head"><h2>Recent</h2><a href="/research/">All research →</a></div>',
    '<div class="section-head"><h2>Recent</h2><div class="section-head-links"><a href="/research/">Research →</a><a href="/policy/">Policy →</a></div></div>',
    "homepage Recent navigation",
)

# Upcoming items are public appearances; give visitors a direct path to the complete speaking record.
home = replace_once(
    home,
    '<div class="section-head"><h2>Upcoming</h2></div>',
    '<div class="section-head"><h2>Upcoming</h2><a href="/presentations/">Presentations →</a></div>',
    "homepage Upcoming navigation",
)

# CV and direct contact are important enough to be available in the hero as well as globally.
profile_match = re.search(r'(<div class="profile-links">)(.*?)(</div>)', home, flags=re.S)
if not profile_match:
    raise RuntimeError("Homepage profile links block not found")
profile_block = profile_match.group(0)
updated_block = profile_block
if '/assets/files/CV-Simona-Malovana.pdf' not in updated_block:
    updated_block = updated_block.replace(
        '</div>',
        '<a href="/assets/files/CV-Simona-Malovana.pdf">CV ↗</a></div>',
        1,
    )
if f'mailto:{email}' not in updated_block:
    updated_block = updated_block.replace(
        '</div>',
        f'<a href="mailto:{email}">Email</a></div>',
        1,
    )
if updated_block != profile_block:
    home = home[:profile_match.start()] + updated_block + home[profile_match.end():]

home_path.write_text(home, encoding="utf-8")

# Clarify the professional image-download page without changing its stable URL.
photos_path = DIST / "photos" / "index.html"
photos = photos_path.read_text(encoding="utf-8")
photos = photos.replace('<title>Photos — Simona Malovaná</title>', '<title>Media photos — Simona Malovaná</title>')
photos = photos.replace('<meta property="og:title" content="Photos — Simona Malovaná">', '<meta property="og:title" content="Media photos — Simona Malovaná">')
photos = photos.replace('<h1>Photos</h1>', '<h1>Media photos</h1>', 1)
photos_path.write_text(photos, encoding="utf-8")

print("Applied complete final pre-launch polish, including contact email.")
