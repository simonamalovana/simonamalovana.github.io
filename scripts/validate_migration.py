#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
DIST = ROOT / "dist"


def load(name: str):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


research = load("research.json")
policy = load("policy.json")
presentations = load("presentations.json")
about = load("about.json")
personal = load("personal.json")

research_by_title = {item["title"]: item for item in research}
policy_titles = {item["title"] for item in policy}
presentation_titles = {item.get("details", "") for item in presentations["presentations"]}

legacy_research_required = {
    "Banks' Credit Losses and Provisioning over the Business Cycle: Implications for IFRS 9",
    "Introducing Macro-Financial Variables into Semi-Structural Model",
    "Banks' Capital Surplus and the Impact of Additional Capital Requirements",
    "Foreign Exchange Interventions at the Zero Lower Bound in the Czech Economy: A DSGE Approach",
    "Flight from the Front Line: Geopolitical Risk, Distance, and Capital Flow Dynamics",
    "State-Dependent Effects of Borrower-Based Macroprudential Measures",
}
require(legacy_research_required <= set(research_by_title), f"Legacy research items missing: {legacy_research_required - set(research_by_title)}")

final_derivatives = "What Drives Sectoral Differences in Currency Derivatives Usage in a Small Open Economy? Evidence from Supervisory Data"
require(final_derivatives in research_by_title, "Final derivatives publication missing")
require(research_by_title[final_derivatives]["type"] == "publication", "Derivatives article is not a publication")
require("10.1007/s10693-026-00472-6" in research_by_title[final_derivatives]["url"], "Derivatives DOI missing")
require(not any("R&R in Journal of Financial Services Research" in item.get("status", "") for item in research), "Stale JFSR R&R status remains")
require(any("Environmental Consciousness" in title for title in research_by_title), "Final Environmental Consciousness title missing")

for title in [
    "Svět se mění. A s ním i otázky, na které musí centrální banky hledat odpovědi",
    "Když modely nestačí: Jak Česká národní banka předvídá budoucnost v době krizí",
    "Climate-related disasters can push up the cost of debt",
    "How do central bank decisions affect everyday life?",
]:
    require(title in policy_titles, f"Audited policy/media item missing: {title}")

require(any(item["event"] == "Central Bank of Ireland Research Seminar" and item.get("date_label", "").startswith("20 May") for item in presentations["presentations"]), "Central Bank of Ireland seminar missing or undated")
require(any("CNB Research Strategy: Priorities" in details for details in presentation_titles), "Research Connect presentation missing")
require(not any(item["event"] == "Third Annual Czech National Bank Conference" for item in presentations["organized"]), "2026 scientific committee should not be in organized presentations")

roles = {(item["role"], item["institution"]) for item in about["roles"]}
require(("Managing Editor", "Czech Journal of Economics and Finance") in roles, "Managing Editor role missing")
require(any(role == "Visiting Scholar" and "Central Bank of Ireland" in institution for role, institution in roles), "Central Bank of Ireland visit missing")

require(len(personal["photos"]) == 26, f"Personal gallery should contain 26 photos, found {len(personal['photos'])}")
for photo in personal["photos"]:
    require((DIST / "assets" / "images" / "personal" / photo["file"]).exists(), f"Personal image missing from dist: {photo['file']}")

require((DIST / "personal" / "index.html").exists(), "Personal page not generated")
personal_html = (DIST / "personal" / "index.html").read_text(encoding="utf-8")
require("Some of my favorite places" in personal_html, "Personal gallery heading missing")
require('href="/personal/" class="active" aria-current="page"' in personal_html, "Personal nav state missing")

for page in ["index.html", "research/index.html", "policy/index.html", "presentations/index.html", "about/index.html"]:
    html = (DIST / page).read_text(encoding="utf-8")
    require('href="/personal/"' in html, f"Personal nav link missing on {page}")

research_html = (DIST / "research" / "index.html").read_text(encoding="utf-8")
require("Gross-flow decompositions" in research_html, "Full Flight from the Front Line abstract was not rendered")
require("Original CNB Working Paper 12/2023" in research_html, "Secondary research resources were not rendered")

policy_html = (DIST / "policy" / "index.html").read_text(encoding="utf-8")
require("Hospodářské noviny version" in policy_html, "Secondary HN link was not rendered")
require("Czech National Bank republication" in policy_html, "Secondary Bankast/CNB link was not rendered")

cv = DIST / "assets" / "files" / "CV-Simona-Malovana.pdf"
require(cv.exists() and cv.stat().st_size > 25_000, "Generated CV PDF missing or unexpectedly small")

print("Migration validation passed: legacy content, audited updates, Personal gallery and generated CV are present.")
