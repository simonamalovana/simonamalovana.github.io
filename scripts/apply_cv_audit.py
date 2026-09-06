#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

PATH = Path(__file__).resolve().parent / "build_cv.py"
text = PATH.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"CV audit patch anchor not found: {label}")
    text = text.replace(old, new, 1)


replace_once(
    '    section("Selected academic and professional activities"),\n    entry("2023–present", "Associate Editor", "Political Economy, Prague University of Economics and Business"),',
    '    section("Selected academic and professional activities"),\n    entry("June 2026–present", "Managing Editor", "Czech Journal of Economics and Finance"),\n    entry("2023–present", "Associate Editor", "Political Economy, Prague University of Economics and Business"),',
    "managing editor",
)

replace_once(
    '    entry("2025", "IBRN Climate Workshop", "Norges Bank, Oslo", "Presented ‘Decoding Climate-related Risks in Sovereign Bond Pricing’."),',
    '    entry("20 May 2025", "Central Bank of Ireland Research Seminar", "Dublin", "Presented ‘Distributional Effects of Borrower-Based Macroprudential Measures’."),\n    entry("2025", "IBRN Climate Workshop", "Norges Bank, Oslo", "Presented ‘Decoding Climate-related Risks in Sovereign Bond Pricing’."),',
    "Central Bank of Ireland seminar",
)

replace_once(
    'publications = [\n',
    'publications = [\n    ("What Drives Sectoral Differences in Currency Derivatives Usage in a Small Open Economy? Evidence from Supervisory Data", "Zuzana Gric and Jan Janků", "Journal of Financial Services Research, online first, 2026", "https://doi.org/10.1007/s10693-026-00472-6"),\n',
    "derivatives journal publication",
)

old_working = '    ("What Drives Sectoral Differences in Currency Derivative Usage in a Small Open Economy? Evidence from Supervisory Data", "Zuzana Gric and Jan Janků", "CNB Working Papers 12/2023 · R&R in Journal of Financial Services Research", "https://www.cnb.cz/en/economic-research/research-publications/cnb-working-paper-series/What-Drives-Sectoral-Differences-in-Currency-Derivative-Usage-in-a-Small-Open-Economy-Evidence-from-Supervisory-Data-00001/"),\n'
if old_working in text:
    text = text.replace(old_working, "", 1)
elif "R&R in Journal of Financial Services Research" in text:
    raise RuntimeError("CV audit found an unexpected derivatives working-paper representation")

PATH.write_text(text, encoding="utf-8")
print("Applied September 2026 CV content audit.")
