#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
site = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
email = site["email"]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


pages = [
    "index.html",
    "research/index.html",
    "policy/index.html",
    "presentations/index.html",
    "about/index.html",
    "personal/index.html",
    "photos/index.html",
]
for page in pages:
    html = (DIST / page).read_text(encoding="utf-8")
    require('/assets/prelaunch.css' in html, f"Pre-launch stylesheet missing on {page}")
    nav_match = re.search(r'<nav class="main-nav" aria-label="Main navigation">(.*?)</nav>', html, flags=re.S)
    require(nav_match is not None, f"Main navigation missing on {page}")
    nav = nav_match.group(1)
    require('href="/personal/"' not in nav, f"Personal is still in primary navigation on {page}")
    for label in ["Research", "Policy", "Presentations", "About", "CV"]:
        require(label in nav, f"Primary navigation is missing {label} on {page}")
    require('href="/personal/"' in html, f"Secondary Personal footer link missing on {page}")
    require('href="/photos/">Media photos</a>' in html, f"Media photos footer label missing on {page}")
    require(f'href="mailto:{email}">Email</a>' in html, f"Contact email missing on {page}")

home = (DIST / "index.html").read_text(encoding="utf-8")
require('<a href="/research/">Research →</a>' in home, "Homepage Recent section is missing Research navigation")
require('<a href="/policy/">Policy →</a>' in home, "Homepage Recent section is missing Policy navigation")
require('<a href="/presentations/">Presentations →</a>' in home, "Homepage Upcoming section is missing Presentations navigation")
profile_match = re.search(r'<div class="profile-links">.*?</div>', home, flags=re.S)
require(profile_match is not None, "Homepage profile links block missing")
require('/assets/files/CV-Simona-Malovana.pdf' in profile_match.group(0), "Hero CV link missing")
require(f'mailto:{email}' in profile_match.group(0), "Hero contact email missing")
require('/assets/images/simona-malovana-portrait.webp' in home, "Approved homepage hero photograph changed unexpectedly")

photos_html = (DIST / "photos" / "index.html").read_text(encoding="utf-8")
require('<h1>Media photos</h1>' in photos_html, "Professional photo page is not clearly labelled Media photos")
require('<title>Media photos — Simona Malovaná</title>' in photos_html, "Media photos page title missing")

css = (DIST / "assets" / "prelaunch.css").read_text(encoding="utf-8")
require('overflow-x: visible' in css, "Mobile navigation wrap polish missing")
require('grid-template-columns: 1fr' in css and '@media (max-width: 900px)' in css, "Tablet hero should collapse to one column")
require('order: 0' in css, "Mobile hero should keep identity copy before the photograph")
require('#76817f' in css, "Accessible search placeholder contrast polish missing")
require('font-size: .76rem' in css, "Small metadata typography polish missing")
require('padding: 10px 0' in css, "Mobile filter tap-target polish missing")

personal_dir = DIST / "assets" / "images" / "personal"
photos = sorted(personal_dir.glob("*.jpg"))
require(len(photos) == 26, f"Expected 26 optimized Personal images, found {len(photos)}")
total_bytes = sum(path.stat().st_size for path in photos)
require(total_bytes <= 12 * 1024 * 1024, f"Personal gallery is still too heavy: {total_bytes / 1024 / 1024:.1f} MiB")
for path in photos:
    require(path.stat().st_size <= 900_000, f"Personal image unexpectedly large after optimization: {path.name}")
    with Image.open(path) as image:
        require(max(image.size) <= 1400, f"Personal image exceeds launch dimension cap: {path.name} {image.size}")

print(
    "Pre-launch validation passed: concise primary navigation, visible contact email, secondary "
    "Personal/Media photos, homepage hierarchy, approved hero, typography, tablet/mobile UX, "
    f"accessibility and optimized Personal gallery ({total_bytes / 1024 / 1024:.1f} MiB) are ready."
)
