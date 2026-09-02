#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "files" / "CV-Simona-Malovana.pdf"

PAPER = colors.HexColor("#F2F7F6")
INK = colors.HexColor("#252B2D")
MUTED = colors.HexColor("#687273")
ACCENT = colors.HexColor("#147F7B")
LINE = colors.HexColor("#D2DCDA")

pdfmetrics.registerFont(TTFont("DVSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVSans-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CVName", fontName="DVSans", fontSize=24, leading=27, textColor=INK, spaceAfter=4))
styles.add(ParagraphStyle(name="CVRole", fontName="DVSans", fontSize=9.2, leading=13, textColor=MUTED))
styles.add(ParagraphStyle(name="CVContact", fontName="DVSans", fontSize=8.2, leading=12, textColor=MUTED, alignment=TA_RIGHT))
styles.add(ParagraphStyle(name="CVSection", fontName="DVSans-Bold", fontSize=10.2, leading=13, textColor=INK, spaceBefore=13, spaceAfter=6, keepWithNext=True))
styles.add(ParagraphStyle(name="CVPeriod", fontName="DVSans", fontSize=7.7, leading=10.8, textColor=ACCENT))
styles.add(ParagraphStyle(name="CVEntry", fontName="DVSans", fontSize=8.2, leading=11.5, textColor=INK))
styles.add(ParagraphStyle(name="CVEntrySmall", fontName="DVSans", fontSize=7.6, leading=10.5, textColor=INK))
styles.add(ParagraphStyle(name="CVMeta", fontName="DVSans", fontSize=7.5, leading=10.5, textColor=MUTED))
styles.add(ParagraphStyle(name="CVPaper", fontName="DVSans", fontSize=7.4, leading=10.4, textColor=INK, spaceAfter=5))


def link(label: str, url: str) -> str:
    return f'<link href="{escape(url)}" color="#0E5F5C">{escape(label)}</link>'


def section(title: str):
    return Paragraph(escape(title), styles["CVSection"])


def entry(period: str, title: str, institution: str = "", detail: str = ""):
    body = f"<b>{escape(title)}</b>"
    if institution:
        body += f"<br/><font color='#687273'>{escape(institution)}</font>"
    if detail:
        body += f"<br/>{escape(detail)}"
    table = Table(
        [[Paragraph(escape(period), styles["CVPeriod"]), Paragraph(body, styles["CVEntry"])]],
        colWidths=[31 * mm, 144 * mm],
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 5 * mm),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEABOVE", (0, 0), (-1, 0), 0.3, LINE),
    ]))
    return table


def paper(title: str, coauthors: str, venue: str, url: str = ""):
    title_html = link(title, url) if url else escape(title)
    tail = f" (with {escape(coauthors)})" if coauthors else ""
    return Paragraph(f"<b>{title_html}</b>{tail}. <font color='#687273'>{escape(venue)}</font>", styles["CVPaper"])


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(1.2)
    canvas.line(18 * mm, A4[1] - 15 * mm, 38 * mm, A4[1] - 15 * mm)
    canvas.setFont("DVSans", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 10 * mm, "Simona Malovaná · Curriculum Vitae")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"{doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(
    str(OUTPUT),
    pagesize=A4,
    leftMargin=18 * mm,
    rightMargin=18 * mm,
    topMargin=20 * mm,
    bottomMargin=17 * mm,
    title="Curriculum Vitae — Simona Malovaná",
    author="Simona Malovaná",
    subject="Curriculum Vitae, updated September 2026",
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates(PageTemplate(id="cv", frames=[frame], onPage=draw_page))

story = []
header = Table([
    [Paragraph("Simona Malovaná", styles["CVName"]), Paragraph(
        f"{link('simona.malovana@cnb.cz', 'mailto:simona.malovana@cnb.cz')}<br/>"
        f"{link('simonamalovana.com', 'https://simonamalovana.com/')} · "
        f"{link('ORCID', 'https://orcid.org/0000-0002-0658-3214')}<br/>"
        f"{link('Google Scholar', 'https://scholar.google.com/citations?hl=en&oi=ao&user=Tkg9CYgAAAAJ')} · "
        f"{link('IDEAS/RePEc', 'https://ideas.repec.org/f/pma2281.html')}",
        styles["CVContact"],
    )],
    [Paragraph("Executive Director, Research and Statistics Department<br/>Czech National Bank · Na Příkopě 864/28 · 115 03 Prague 1 · Czechia", styles["CVRole"]), ""],
], colWidths=[112 * mm, 63 * mm])
header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("SPAN", (0, 1), (1, 1)), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
story += [header, Spacer(1, 7 * mm), section("Positions")]
story += [
    entry("2025–present", "Executive Director, Research and Statistics Department", "Czech National Bank", "Leads the Bank’s research and statistical functions, sets strategic priorities, oversees 100+ staff, and supports monetary and macroprudential policymaking with research, data and analytical tools."),
    entry("2019–2024", "Director, Financial Research Division, Financial Stability Department", "Czech National Bank", "Led research strategy and teams, edited the CNB Working Paper and Research and Policy Note series, and contributed to financial-stability and monetary-policy analysis."),
    entry("2017–2019", "Head, Financial Research Unit, Financial Stability Department", "Czech National Bank", "Led a research team, coordinated publications and prepared policy analysis for Bank Board discussions."),
    entry("2014–2016", "Economist / Senior Economist, Financial Stability Department", "Czech National Bank", "Produced financial-stability analysis, contributed to the Financial Stability Report and developed household-sector stress tests."),
    section("Education"),
    entry("2019", "Ph.D. in Economics", "Faculty of Social Sciences, Charles University, Prague"),
    entry("2014", "PhDr. in Economics (M.Phil. equivalent)", "Faculty of Social Sciences, Charles University, Prague"),
    entry("2014", "Master’s degree in Economics, with honours", "Faculty of Social Sciences, Charles University, Prague"),
    PageBreak(),
    section("Academic positions"),
    entry("2025–present", "Assistant Professor (part-time)", "Department of Finance and Capital Markets, Faculty of Social Sciences, Charles University"),
    entry("2024–present", "Research Fellow (part-time)", "Department of Finance and Capital Markets, Faculty of Social Sciences, Charles University"),
    entry("2022–present", "Research Fellow (part-time)", "Department of Monetary Theory and Policy, Prague University of Economics and Business"),
    section("Research grant"),
    entry("2024–2026", "Central Bank Policies, Financial Sector, and Inequality (24-12098S)", "Czech Science Foundation (GAČR)", "Principal Investigator."),
    section("Research visits"),
    entry("May 2025", "Visiting Scholar", "Central Bank of Ireland"),
    entry("May 2024", "Visiting Scholar", "Bank of Finland Institute for Emerging Economies (BOFIT)"),
    section("Research networks"),
    entry("2023–present", "ESCB Research Network: Challenges for Monetary Policy Transmission in a Changing World (ChaMP)", detail="Contributor to Workstream 1 on monetary-policy transmission through banks and non-bank financial institutions."),
    entry("2021–present", "International Banking Research Network (IBRN)", detail="Contributor to initiatives on climate risks, non-bank financial intermediation, liquidity and low interest rates; former methodology-team lead for a climate-risk initiative."),
    entry("2020–2021", "ESCB Research Cluster 3", detail="Coordinator for Financial Stability, Macroprudential Regulation and Supervision."),
    section("Selected academic and professional activities"),
    entry("2023–present", "Associate Editor", "Political Economy, Prague University of Economics and Business"),
    entry("2018–present", "Scientific and organizing committee member", "Annual Czech National Bank Conference / CNB Research Open Day"),
    entry("2024–present", "Scientific committee member", "Annual CNB Workshop on Financial Stability and Macroprudential Policy"),
    PageBreak(),
    section("Selected presentations and conference roles"),
    entry("2026", "Third Annual Czech National Bank Conference", "Prague", "Chaired the keynote ‘Looking Beyond Financial Stability: The Real and Distributional Effects of Mortgage Credit Constraints’; co-author of ‘Safe for Whom? Investment Flows to Sovereign Bonds During Global and Regional Stress’."),
    entry("2026", "Research Connect Conference", "Prague", "Presented ‘CNB Research Strategy: Priorities’."),
    entry("2026", "SUERF–BAFFI Bocconi e-lecture", "Online", "Presented ‘Geopolitical Risks, Proximity and Cross-border Adjustments’."),
    entry("2026", "46th Macroprudential Policy Group Meeting", "Online", "Presented ‘Macroprudential Policy and Income Inequality’."),
    entry("2025", "IBRN Climate Workshop", "Norges Bank, Oslo", "Presented ‘Decoding Climate-related Risks in Sovereign Bond Pricing’."),
    entry("2025", "3rd Durham–Bristol Banking Policy Forum", "Durham", "Panelist on geopolitical risks, challenges and opportunities."),
    entry("2025", "Second Annual Czech National Bank Conference", "Prague", "Co-author presentation on euroisation and the bank lending channel."),
    entry("2024", "Selected conferences and seminars", "Prague · Frankfurt · Rotterdam · Rome · Helsinki · Tallinn · Bratislava · Mexico City", "Presentations and discussions at the CEBRA Annual Meeting, EEA–ESEM Congress, ChaMP workshops, IBRN Winter Meeting, ESCB Research Cluster 3 workshop, BOFIT and central-bank research seminars."),
    entry("2023", "Selected conferences and seminars", "Basel · Frankfurt · Lisbon · London · New York · Chania · Saariselkä", "Presentations, discussions and keynote roles at IBRN, ESCB research clusters, ChaMP, CEBRA, CCBS, FEBS and CNB Research Open Day."),
    section("Organized conferences and workshops"),
    entry("June 2026", "Third Annual Czech National Bank Conference", "Czech National Bank, Prague", "Scientific committee."),
    entry("June 2025", "Annual International Journal of Central Banking Research Conference", "Czech National Bank, Prague", "Scientific and organizing committee."),
    entry("2018–2025", "CNB Research Open Day and Annual Czech National Bank Conference", "Czech National Bank, Prague", "Scientific and organizing committee."),
    section("Teaching"),
    entry("2019–2020", "Adjunct Lecturer", "Institute of Economic Studies, Charles University", "Courses on monetary policy and financial stability."),
    entry("2014–2019", "Teaching Assistant", "Institute of Economic Studies, Charles University", "Monetary policy, financial stability and international macroeconomics."),
    PageBreak(),
    section("Publications"),
]

publications = [
    ("Credit Shocks Fade, Output Shocks Persist: A Meta-Analysis of 2,600 VAR Estimates Across 63 Countries", "Jan Janků, Josef Bajzík, Klára Moravcová and Ngoc Anh Ngo", "Journal of International Money and Finance, 167, 2026", "https://www.sciencedirect.com/science/article/pii/S0261560626001166"),
    ("What Do Economists Think About the Green Transition? Exploring the Impact of Environmental Consciousness", "Dominika Ehrenbergerová and Zuzana Gric", "Environment and Development Economics, First View, 2026", "https://doi.org/10.1017/S1355770X26100515"),
    ("Instant Payments in Czechia: Adoption and Future Trends", "Ivan Trubelík, Tomáš Karhánek and Aleš Michl", "Journal of Payments Strategy & Systems, 20(1), 2026", "https://doi.org/10.69554/RTVE9288"),
    ("Macroprudential Policy and Income Inequality: The Trade-off Between Crisis Prevention and Credit Redistribution", "Martin Hodula and Jan Janků", "International Journal of Central Banking, 21(4), 2025", "https://www.ijcb.org/journal/v21n4/macroprudential-policy-and-income-inequality-trade-between-crisis-prevention-and"),
    ("Borrower-Based Macroprudential Measures and Credit Growth: How Biased is the Existing Literature?", "Martin Hodula, Josef Bajzík and Zuzana Gric", "Journal of Economic Surveys, 39(1), 2025", "https://onlinelibrary.wiley.com/doi/10.1111/joes.12608"),
    ("Bank Capital, Lending and Regulation: A Meta-analysis", "Martin Hodula, Josef Bajzík and Zuzana Gric", "Journal of Economic Surveys, 38(3), 2024", "https://onlinelibrary.wiley.com/doi/10.1111/joes.12560"),
    ("Researching the Research: A Central Banking Edition", "Martin Hodula and Zuzana Gric", "International Journal of Central Banking, 20(1), 2024", "https://www.ijcb.org/journal/v20n1/researching-research-central-banking-edition"),
    ("Monetary Policy Spillover to Small Open Economies: Is the Transmission Different Under Low Interest Rates?", "Jin Cao, Valeriya Dinger, Tomás Gómez, Zuzana Gric, Martin Hodula, Alejandro Jara, Ragnar Juelsrud, Karolis Liaudinskas and Yaz Terajima", "Journal of Financial Stability, 65, 2023", "https://doi.org/10.1016/j.jfs.2023.101116"),
    ("Macroprudential Policy in Central Banks: Integrated or Separate? Survey Among Academics and Central Bankers", "Martin Hodula, Josef Bajzík and Zuzana Gric", "Journal of Financial Stability, 65, 2023", "https://doi.org/10.1016/j.jfs.2023.101107"),
    ("A Prolonged Period of Low Interest Rates in Europe: Unintended Consequences", "Josef Bajzík, Dominika Ehrenbergerová and Jan Janků", "Journal of Economic Surveys, 37(2), 2023", "https://onlinelibrary.wiley.com/doi/abs/10.1111/joes.12499"),
    ("Too Much of a Good Thing? Households’ Macroeconomic Conditions and Credit Dynamics", "Martin Hodula and Jan Frait", "German Economic Review, 23(4), 2022", "https://doi.org/10.1515/ger-2021-0033"),
    ("The Effect of Higher Capital Requirements on Bank Lending: The Capital Surplus Matters", "Dominika Ehrenbergerová", "Empirica, 49(3), 2022", "https://doi.org/10.1007/s10663-022-09536-x"),
    ("What Does Really Drive Consumer Confidence?", "Martin Hodula and Jan Frait", "Social Indicators Research, 155(3), 2021", "https://doi.org/10.1007/s11205-021-02626-6"),
    ("The Pro-cyclicality of Risk Weights for Credit Exposures: Driven by the Retail Segment", "", "Economic Systems, 45(1), 2021", "https://doi.org/10.1016/j.ecosys.2020.100763"),
    ("Does Monetary Policy Influence Banks’ Risk Weights under the Internal Ratings-based Approach?", "Dominika Kolcunová and Václav Brož", "Economic Systems, 43(2), 2019", "https://doi.org/10.1016/j.ecosys.2018.10.003"),
    ("Monetary Policy and Macroprudential Policy: Rivals or Teammates?", "Jan Frait", "Journal of Financial Stability, 32, 2017", "https://doi.org/10.1016/j.jfs.2017.08.004"),
]
story += [paper(*p) for p in publications]
story += [PageBreak(), section("Working papers and ongoing research")]
working = [
    ("Drying Up: The Effect of Drought on Corporate Loans with AnaCredit Data", "Jan Janků, Tomáš Karhánek and Ivan Trubelík", "CNB Working Papers 11/2026 · Submitted to International Review of Financial Analysis", "https://www.cnb.cz/en/economic-research/research-publications/cnb-working-paper-series/Drying-Up-The-Effect-of-Drought-on-Corporate-Loans-with-AnaCredit-Data/"),
    ("Who Is Less Likely to Get a Mortgage When Borrowing Limits Tighten?", "Zuzana Gric and Dominika Ehrenbergerová", "CNB Working Papers 10/2026 · Submitted to Journal of International Money and Finance", "https://www.cnb.cz/en/economic-research/research-publications/cnb-working-paper-series/Who-Is-Less-Likely-to-Get-a-Mortgage-When-Borrowing-Limits-Tighten/"),
    ("Euroisation and the Bank Lending Channel of Monetary Policy: Evidence from Czechia", "Zuzana Gric and Jan Janků", "CNB Working Papers 7/2026", "https://www.cnb.cz/en/economic-research/research-publications/cnb-working-paper-series/Euroisation-and-the-Bank-Lending-Channel-of-Monetary-Policy-Evidence-from-Czechia-00001/"),
    ("When Monetary and Macroprudential Policies Tighten Together: Evidence from the Czech Mortgage Market", "Martin Hodula and Lukáš Pfeifer", "CNB Working Papers 2/2026", "https://www.cnb.cz/en/economic-research/research-publications/cnb-working-paper-series/When-Monetary-and-Macroprudential-Policies-Tighten-Together-Evidence-from-the-Czech-Mortgage-Market/"),
    ("When Foreign Rates Matter More: Domestic Investor Responses in a Small Open Economy", "Martin Hodula", "CNB Working Papers 11/2025", "https://www.cnb.cz/en/economic-research/research-publications/cnb-working-paper-series/When-Foreign-Rates-Matter-More-Domestic-Investor-Responses-in-a-Small-Open-Economy/"),
    ("Decoding Climate-related Risks in Sovereign Bond Pricing: A Global Perspective", "Sofia Anyfantaki, Marianna Blix Grimaldi, Carlos Madeira and Georgios Papadopoulos", "BIS Working Papers No. 1275, 2025", "https://www.bis.org/publications/working-paper-1275-decoding-climate-related-risks-sovereign-bond-pricing-global-perspective"),
    ("Geopolitical Risks and Their Impact on Global Macro-Financial Stability: Literature and Measurements", "Martin Hodula, Jan Janků and Ngoc Anh Ngo", "CNB Working Papers 8/2024 · R&R in Journal of Economic Surveys", "https://www.cnb.cz/en/economic-research/research-publications/cnb-working-paper-series/Geopolitical-Risks-and-Their-Impact-on-Global-Macro-Financial-Stability-Literature-and-Measurements/"),
    ("Monetary Policy Has a Long-Lasting Impact on Credit: Evidence from 91 VAR Studies", "Josef Bajzík, Jan Janků, Klára Moravcová and Ngoc Anh Ngo", "CNB Working Papers 19/2023 · Submitted to IMF Economic Review", "https://www.cnb.cz/en/economic-research/research-publications/cnb-working-paper-series/Monetary-Policy-Has-a-Long-Lasting-Impact-on-Credit-Evidence-from-91-VAR-Studies/"),
    ("How Do Climate Policies Affect Holdings of Green and Brown Firms’ Securities?", "Dominika Ehrenbergerová and Caterina Mendicino", "CNB Working Papers 11/2023 · R&R in Economic Modelling", "https://www.cnb.cz/en/economic-research/research-publications/cnb-working-paper-series/How-Do-Climate-Policies-Affect-Holdings-of-Green-and-Brown-Firms-Securities-00001/"),
    ("What Drives Sectoral Differences in Currency Derivative Usage in a Small Open Economy? Evidence from Supervisory Data", "Zuzana Gric and Jan Janků", "CNB Working Papers 12/2023 · R&R in Journal of Financial Services Research", "https://www.cnb.cz/en/economic-research/research-publications/cnb-working-paper-series/What-Drives-Sectoral-Differences-in-Currency-Derivative-Usage-in-a-Small-Open-Economy-Evidence-from-Supervisory-Data-00001/"),
    ("Safe for Whom? Investment Flows to Sovereign Bonds During Global and Regional Stress", "Martijn Boermans, Alessandro Chiari and Martin Hodula", "Work in progress, 2026", "https://www.cnb.cz/en/economic-research/conferences-seminars-and-workshops/2026-third-annual-czech-national-bank-conference/"),
    ("Flight from the Front Line: Geopolitical Risk, Distance, and Capital Flow Dynamics", "Martin Hodula and Jan Janků", "Work in progress · CNB Research Brief 1/2026", "https://www.cnb.cz/en/economic-research/research-publications/research-brief/Flight-from-the-Front-Line-Geopolitical-Risk-Distance-and-Capital-Flow-Dynamics/"),
    ("State-Dependent Effects of Borrower-Based Macroprudential Measures", "", "Work in progress, 2026", ""),
]
story += [paper(*p) for p in working]
story += [
    section("Additional information"),
    entry("Languages", "English — advanced (C1); German — beginner to intermediate (A2/B1)"),
    entry("Certification", "CFA Level I and II passed on the first attempt"),
    entry("Refereeing", "Journal of Financial Stability · International Journal of Central Banking · Economic Modelling · Finance Research Letters · Czech Journal of Economics and Finance"),
    entry("Awards", "CNB Economic Research Award for Best Research Paper (2018, 2021) · Professor František Vencovský Award for Young Economist (2019) · Karel Engliš Prize for Young Economist (2014)"),
    Spacer(1, 5 * mm),
    Paragraph("Last updated: September 2026", styles["CVMeta"]),
]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc.build(story)
print(f"Built {OUTPUT}")
