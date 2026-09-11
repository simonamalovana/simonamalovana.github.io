#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
OUT = ROOT / "assets" / "images" / "personal"
data = json.loads((CONTENT / "personal.json").read_text(encoding="utf-8"))

EXPECTED_WIDTHS = (480, 800)
files = []

for photo in data["photos"]:
    for width in EXPECTED_WIDTHS:
        path = OUT / f'{photo["file"]}-{width}.webp'
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Missing Personal gallery asset: {path.relative_to(ROOT)}")
        with Image.open(path) as image:
            if image.format != "WEBP":
                raise RuntimeError(f"Unexpected Personal image format: {path.name} ({image.format})")
            if image.width != width:
                raise RuntimeError(f"Unexpected Personal image width: {path.name} ({image.width}px)")
        files.append(path)

print(
    f"Validated {len(data['photos'])} curated Personal photographs in two responsive sizes "
    f"({sum(path.stat().st_size for path in files) / 1024 / 1024:.1f} MiB total)."
)
