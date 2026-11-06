#!/usr/bin/env python3
"""Build the first public Data Story without requiring an API key on the website.

Sources:
- CNB: exact effective dates of 2W repo rate changes.
- ECB SDMX MIR: Czech monthly new-business rates on loans for house purchase;
  the underlying statistics originate from the national central bank.

No estimated observations or interpolation are published. If the source cannot
be validated, the story remains available but explicitly displays data unavailable.
"""
from __future__ import annotations

import csv
import io
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SOURCE = ROOT / "pages" / "mortgage-rates.html"
OUT = DIST / "data-stories" / "mortgage-rates"
REPO_URL = "https://www.cnb.cz/en/faq/.galleries/development_of_the_cnb_2w_repo_rate.txt"
MORTGAGE_SERIES = "MIR.M.CZ.B.A2C.A.R.A.2250.CZK.N"
MORTGAGE_URL = (
    "https://data-api.ecb.europa.eu/service/data/MIR/"
    "M.CZ.B.A2C.A.R.A.2250.CZK.N?format=csvdata&startPeriod=2015-01"
)


def get_text(url: str, accept: str = "text/plain") -> str:
    req = Request(url, headers={"User-Agent": "aradR-data-stories/1.0", "Accept": accept})
    with urlopen(req, timeout=35) as response:
        return response.read().decode("utf-8-sig")


def mortgage_observations(text: str) -> dict[str, float]:
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not {"TIME_PERIOD", "OBS_VALUE"} <= set(reader.fieldnames):
        raise ValueError("Unexpected ECB CSV structure: missing TIME_PERIOD / OBS_VALUE")
    out = {}
    for row in reader:
        period = (row.get("TIME_PERIOD") or "").strip()
        value = (row.get("OBS_VALUE") or "").strip()
        if not re.fullmatch(r"20\d{2}-(0[1-9]|1[0-2])", period) or not value:
            continue
        rate = float(value)
        if not 0 <= rate <= 20:
            raise ValueError(f"Invalid mortgage rate for {period}")
        out[period] = rate
    if len(out) < 80 or not any(p.startswith("2025-") for p in out):
        raise ValueError(f"Insufficient monthly mortgage observations: {len(out)}")
    return out


def repo_month_ends(text: str, months: list[str]) -> dict[str, float]:
    events = []
    for line in text.splitlines():
        match = re.fullmatch(r"\s*(\d{8})\|([0-9.]+)\s*", line.strip())
        if match:
            d = datetime.strptime(match.group(1), "%Y%m%d").date()
            rate = float(match.group(2))
            if not 0 <= rate <= 50:
                raise ValueError("Out-of-range 2W repo rate")
            events.append((d, rate))
    if not events or events != sorted(events):
        raise ValueError("Missing/unsorted CNB repo-rate history")
    out = {}
    for month in months:
        y, m = map(int, month.split("-"))
        end = date(y + (m == 12), m % 12 + 1, 1)
        valid = [v for d, v in events if d < end]
        if not valid:
            raise ValueError(f"No CNB repo rate available for {month}")
        out[month] = valid[-1]
    return out


def load_data() -> dict:
    mortgage = mortgage_observations(get_text(MORTGAGE_URL, "text/csv"))
    months = sorted(m for m in mortgage if "2015-01" <= m <= date.today().strftime("%Y-%m"))
    repo = repo_month_ends(get_text(REPO_URL), months)
    rows = [{"month": m, "mortgage": round(mortgage[m], 4), "repo": repo[m]} for m in months]
    return {
        "status": "verified",
        "series": MORTGAGE_SERIES,
        "updated": date.today().isoformat(),
        "mortgage_last_month": rows[-1]["month"],
        "mortgage_source": MORTGAGE_URL,
        "repo_source": REPO_URL,
        "repo_statistic": "month-end 2W repo rate (effective as of end of calendar month)",
        "mortgage_statistic": "monthly AAR/NDER, CZK new loans to households for house purchase, total fixation",
        "rows": rows,
    }


def add_home_link(html: str) -> str:
    if '/data-stories/mortgage-rates/' in html:
        return html
    item = (
        '<section class="home-section" aria-labelledby="data-stories-title">'
        '<div class="shell index-shell"><div class="section-head">'
        '<h2 id="data-stories-title">Data stories</h2>'
        '<a href="/data-stories/mortgage-rates/">Explore the first story →</a>'
        '</div><div class="recent-list"><article class="recent-row">'
        '<div class="recent-aside"><span>Interactive analysis</span>'
        '<span>Powered by aradR</span></div><div>'
        '<h3><a href="/data-stories/mortgage-rates/">How quickly do mortgage rates '
        'follow monetary policy?</a></h3>'
        '<p>Explore Czech interest rates, download data and reproduce the analysis in R.</p>'
        '</div></article></div></div></section>'
    )
    return html.replace('</main>', item + '</main>', 1)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = None
    try:
        data = load_data()
        print(f"Verified {len(data['rows'])} month pairs; last: {data['mortgage_last_month']}")
    except Exception as exc:
        # A third-party outage must not take down the entire personal site.
        print(f"Data Story feed unavailable; refusing to publish unverified numbers: {exc}")
        data = {"status": "unavailable", "rows": [], "message": "Data temporarily unavailable. The data feed is being checked."}
    (OUT / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    shutil.copyfile(SOURCE, OUT / "index.html")
    (DIST / "assets" / "mortgage-story.css").write_text(
        (ROOT / "assets" / "mortgage-story.css").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (DIST / "assets" / "mortgage-story.js").write_text(
        (ROOT / "assets" / "mortgage-story.js").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    home = DIST / "index.html"
    if data["status"] == "verified":
        home.write_text(add_home_link(home.read_text(encoding="utf-8")), encoding="utf-8")
    else:
        print("Skipping homepage promotion until complete real data are verified.")
    sitemap = DIST / "sitemap.xml"
    xml = sitemap.read_text(encoding="utf-8")
    address = "https://simonamalovana.com/data-stories/mortgage-rates/"
    if address not in xml:
        xml = xml.replace("</urlset>", f"  <url><loc>{address}</loc></url>\n</urlset>")
        sitemap.write_text(xml, encoding="utf-8")
    print("Data Story page built; no fabricated figures or estimates.")


if __name__ == "__main__":
    main()
