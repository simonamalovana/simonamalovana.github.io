#!/usr/bin/env python3
from __future__ import annotations

import json
import re
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
legacy_resource_links = load("legacy_resource_links.json")

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

# Preserve every legacy Personal image and page, but keep it out of the professional primary navigation.
require(len(personal["photos"]) == 26, f"Personal gallery should contain 26 photos, found {len(personal['photos'])}")
for photo in personal["photos"]:
    require((DIST / "assets" / "images" / "personal" / photo["file"]).exists(), f"Personal image missing from dist: {photo['file']}")

require((DIST / "personal" / "index.html").exists(), "Personal page not generated")
personal_html = (DIST / "personal" / "index.html").read_text(encoding="utf-8")
require("Some of my favorite places" in personal_html, "Personal gallery heading missing")

pages_with_global_navigation = [
    "index.html",
    "research/index.html",
    "policy/index.html",
    "presentations/index.html",
    "about/index.html",
    "personal/index.html",
    "photos/index.html",
]
for page in pages_with_global_navigation:
    html = (DIST / page).read_text(encoding="utf-8")
    nav_match = re.search(r'<nav class="main-nav" aria-label="Main navigation">(.*?)</nav>', html, flags=re.S)
    require(nav_match is not None, f"Main navigation missing on {page}")
    require('href="/personal/"' not in nav_match.group(1), f"Personal must not appear in primary navigation on {page}")
    require('href="/personal/"' in html, f"Personal footer link missing on {page}")

research_html = (DIST / "research" / "index.html").read_text(encoding="utf-8")
require("Gross-flow decompositions" in research_html, "Full Flight from the Front Line abstract was not rendered")
require("Original CNB Working Paper 12/2023" in research_html, "Secondary research resources were not rendered")

expected_legacy_urls = {
    "https://drive.google.com/file/d/1lpmxL55CKvT1F8jDUBlZxYP7eLKdaE0A/view?usp=sharing",
    "https://drive.google.com/open?id=18xA2L3j9ftDD7SALiQn80795UiFTFw_c",
    "https://drive.google.com/open?id=1dGSA4gPrZdtTOzahChdened8sQDIt0Or",
    "https://drive.google.com/open?id=1joWeNIZu6QG6ldFKIRPIRVtwYkCDHwf1",
    "https://drive.google.com/open?id=1o24rYr-eBkWY9WApxl3OzH0C2LhyygXJ",
    "https://drive.google.com/file/d/1qrLkNqd-qOltOGO3jNVukUhFI7H7D0aM/view?usp=sharing",
}
configured_legacy_urls = {url for links in legacy_resource_links.values() for url in links.values()}
require(expected_legacy_urls <= configured_legacy_urls, "One or more exact legacy Google Drive resource links are missing from the migration map")
for url in expected_legacy_urls:
    require(url.replace("&", "&amp;") in research_html or url in research_html, f"Legacy resource link was not rendered: {url}")

policy_html = (DIST / "policy" / "index.html").read_text(encoding="utf-8")
require("Hospodářské noviny version" in policy_html, "Secondary HN link was not rendered")
require("Czech National Bank republication" in policy_html, "Secondary Bankast/CNB link was not rendered")

cv = DIST / "assets" / "files" / "CV-Simona-Malovana.pdf"
require(cv.exists() and cv.stat().st_size > 25_000, "Generated CV PDF missing or unexpectedly small")

print("Migration validation passed: legacy content, exact resource links, audited updates, secondary Personal gallery and generated CV are present.")
