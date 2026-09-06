#!/usr/bin/env python3
from __future__ import annotations

import io
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
OUT = ROOT / "assets" / "images" / "personal"
data = json.loads((CONTENT / "personal.json").read_text(encoding="utf-8"))
OUT.mkdir(parents=True, exist_ok=True)

MAX_DIMENSION = 1400
JPEG_QUALITY = 82


def fetch(photo: dict) -> tuple[str, int]:
    target = OUT / photo["file"]
    req = Request(photo["source"], headers={"User-Agent": "Mozilla/5.0 (compatible; simonamalovana.com migration)"})
    with urlopen(req, timeout=45) as response:
        body = response.read()
        content_type = response.headers.get("Content-Type", "")
    if len(body) < 10_000:
        raise RuntimeError(f"Downloaded image is unexpectedly small: {photo['file']} ({len(body)} bytes)")
    if "image" not in content_type.lower():
        raise RuntimeError(f"Unexpected content type for {photo['file']}: {content_type}")

    with Image.open(io.BytesIO(body)) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
        image.save(target, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)

    return photo["file"], target.stat().st_size


sizes = []
with ThreadPoolExecutor(max_workers=6) as pool:
    futures = [pool.submit(fetch, photo) for photo in data["photos"]]
    for future in as_completed(futures):
        sizes.append(future.result())

missing = [photo["file"] for photo in data["photos"] if not (OUT / photo["file"]).exists()]
if missing:
    raise RuntimeError(f"Missing personal gallery assets after download: {missing}")

print(
    f"Fetched and optimized {len(sizes)} personal gallery images "
    f"({sum(size for _, size in sizes) / 1024 / 1024:.1f} MiB total)."
)
