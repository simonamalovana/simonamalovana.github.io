#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


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

home = (DIST / "index.html").read_text(encoding="utf-8")
require('<a href="/research/">Research →</a>' in home, "Homepage Recent section is missing Research navigation")
require('<a href="/policy/">Policy →</a>' in home, "Homepage Recent section is missing Policy navigation")
require('<a href="/presentations/">Presentations →</a>' in home, "Homepage Upcoming section is missing Presentations navigation")
profile_match = re.search(r'<div class="profile-links">.*?</div>', home, flags=re.S)
require(profile_match is not None, "Homepage profile links block missing")
require('/assets/files/CV-Simona-Malovana.pdf' in profile_match.group(0), "Hero CV link missing")
require('/assets/images/simona-malovana-portrait.webp' in home, "Approved homepage hero photograph changed unexpectedly")

css = (DIST / "assets" / "prelaunch.css").read_text(encoding="utf-8")
require('flex-wrap: wrap' in css and 'overflow-x: visible' in css, "Mobile navigation wrap polish missing")
require('order: 0' in css, "Mobile hero should keep identity copy before the photograph")
require('#76817f' in css, "Accessible search placeholder contrast polish missing")

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
    "Pre-launch validation passed: homepage navigation, hero photo, mobile UX, "
    f"accessibility polish and optimized Personal gallery ({total_bytes / 1024 / 1024:.1f} MiB) are ready."
)
