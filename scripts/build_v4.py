#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import shutil
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets"
DIST = ROOT / "dist"
TODAY = date.today()


def load(name):
    return json.loads((CONTENT / name).read_text(encoding="utf-8"))


site = load("site.json")
about = load("about.json")
research = load("research.json")
policy = load("policy.json")
events = load("events.json")
photos = load("photos.json")
presentations_data = load("presentations.json")
presentations = presentations_data["presentations"]
organized = presentations_data["organized"]


def esc(value=""):
    return html.escape(str(value), quote=True)


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def month_year(value):
    return parse_date(value).strftime("%B %Y")


def external_icon():
    return '<span class="external" aria-hidden="true">↗</span>'


def nav(active):
    links = [
        ("research", "/research/", "Research"),
        ("policy", "/policy/", "Policy"),
        ("presentations", "/presentations/", "Presentations"),
        ("about", "/about/", "About"),
    ]
    out = []
    for key, href, label in links:
        cls = ' class="active" aria-current="page"' if key == active else ""
        out.append(f'<a href="{href}"{cls}>{label}</a>')
    out.append('<a href="/assets/files/CV-Simona-Malovana.pdf">CV ↗</a>')
    return "".join(out)


def canonical_for(active):
    path = "" if active == "home" else f"{active}/"
    return f"https://simonamalovana.com/{path}"


def layout(title, body, active="", description=None):
    page_title = site["name"] if title == "Home" else f"{title} — {site['name']}"
    desc = description or site["description"]
    canonical = canonical_for(active)
    og_image = site["hero_image"] if site["hero_image"].startswith("http") else f"https://simonamalovana.com{site['hero_image']}"
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page_title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta property="og:title" content="{esc(page_title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(og_image)}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="stylesheet" href="/assets/site-v4.css">
  <link rel="alternate" type="application/rss+xml" title="Simona Malovaná — latest work" href="/feed.xml">
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="shell header-inner">
      <a class="brand" href="/" aria-label="Simona Malovaná home">Simona Malovaná</a>
      <nav class="main-nav" aria-label="Main navigation">{nav(active)}</nav>
    </div>
  </header>
  <main id="main">{body}</main>
  <footer class="site-footer">
    <div class="shell footer-grid">
      <div class="footer-primary"><strong>Simona Malovaná</strong><p>{esc(site['disclaimer'])}</p></div>
      <div class="footer-links">
        <a href="{esc(site['scholar'])}">Google Scholar ↗</a>
        <a href="{esc(site['repec'])}">IDEAS/RePEc ↗</a>
        <a href="{esc(site['orcid'])}">ORCID ↗</a>
        <a href="{esc(site['github'])}">GitHub ↗</a>
        <a href="/photos/">Photos</a>
      </div>
    </div>
  </footer>
  <script src="/assets/site.js" defer></script>
</body>
</html>'''


TOPIC_GROUPS = {
    "monetary": {"Monetary policy", "Spillovers", "Euroisation", "FX", "Investment"},
    "macroprudential": {"Macroprudential policy", "Mortgages", "Distribution", "Inequality", "Households"},
    "banking": {"Banking", "Credit", "Regulation", "Capital regulation", "Risk weights", "Payments", "Supervisory data"},
    "risk": {"Climate", "Geopolitics", "Sovereign risk", "Capital flows", "Financial stability", "Markets"},
    "methods": {"Meta-analysis", "Survey", "Central banking", "Research", "Macro-financial"},
}
TOPIC_LABELS = [
    ("monetary", "Monetary policy"),
    ("macroprudential", "Macroprudential & housing"),
    ("banking", "Banking & credit"),
    ("risk", "Climate, geopolitics & risk"),
    ("methods", "Methods & central banking"),
]
TOPIC_NAMES = dict(TOPIC_LABELS)


def broad_topics(item):
    raw = set(item.get("topics", []))
    groups = [key for key, values in TOPIC_GROUPS.items() if raw & values]
    return groups or ["methods"]


def work_row(item, show_topics=True):
    url = item.get("url")
    title = esc(item["title"])
    title_html = f'<a href="{esc(url)}">{title}{external_icon()}</a>' if url else title
    authors = item.get("authors", "")
    venue = item.get("venue", "")
    status = item.get("status", "")
    groups = broad_topics(item)
    topic_html = ""
    if show_topics:
        topic_html = '<p class="work-topics">' + " · ".join(esc(TOPIC_NAMES[g]) for g in groups) + "</p>"
    return f'''<article class="work-card" data-kind="{esc(item.get('type',''))}" data-topics="{esc('|'.join(groups))}">
      <div class="work-aside"><span>{esc(month_year(item['date']))}</span><span>{esc(item.get('type','').replace('-', ' ').title())}</span></div>
      <div class="work-main">
        <h3>{title_html}</h3>
        {f'<p class="authors">with {esc(authors)}</p>' if authors else ''}
        <p class="venue">{esc(venue)}</p>
        {f'<p class="status">{esc(status)}</p>' if status else ''}
        {topic_html}
      </div>
    </article>'''


def recent_row(item):
    kind = item.get("type", "").replace("-", " ").title()
    url = item.get("url")
    title = esc(item["title"])
    title_html = f'<a href="{esc(url)}">{title}</a>' if url else title
    venue = item.get("venue", "")
    return f'''<article class="recent-row">
      <div class="recent-aside"><span>{esc(month_year(item['date']))}</span><span>{esc(kind)}</span></div>
      <div><h3>{title_html}</h3><p>{esc(venue)}</p></div>
    </article>'''


def event_row(event):
    url = event.get("url")
    title = esc(event["title"])
    title_html = f'<a href="{esc(url)}">{title}</a>' if url else title
    details = " · ".join(x for x in [event.get("role", ""), event.get("location", "")] if x)
    return f'''<article class="upcoming-row">
      <div class="upcoming-date">{esc(event.get('date_label') or month_year(event['date']))}</div>
      <div><h3>{title_html}</h3><p>{esc(details)}</p></div>
    </article>'''


def presentation_row(item):
    url = item.get("url")
    event = esc(item["event"])
    event_html = f'<a href="{esc(url)}">{event}{external_icon()}</a>' if url else event
    details = item.get("details", "")
    location = item.get("location", "")
    return f'''<article class="presentation-row">
      <div class="presentation-meta">{esc(item.get("date_label", str(item["year"])))}</div>
      <div class="presentation-main">
        <h3>{event_html}</h3>
        {f'<p>{esc(details)}</p>' if details else ''}
        {f'<p class="venue">{esc(location)}</p>' if location else ''}
      </div>
    </article>'''


recent_candidates = [x for x in (research + policy) if x.get("type") != "talk" and parse_date(x["date"]) <= TODAY]
recent_items = []
seen_recent_titles = set()
for item in sorted(recent_candidates, key=lambda x: x["date"], reverse=True):
    key = item["title"].casefold().strip()
    if key in seen_recent_titles:
        continue
    seen_recent_titles.add(key)
    recent_items.append(item)
    if len(recent_items) == 4:
        break
upcoming = sorted([x for x in events if parse_date(x["date"]) >= TODAY], key=lambda x: x["date"])

home_body = f'''
<section class="home-hero">
  <div class="shell hero-grid">
    <div class="hero-copy">
      <span class="signature-rule" aria-hidden="true"></span>
      <h1>Simona Malovaná</h1>
      <p class="hero-role">Executive Director<br>Research and Statistics Department<br><span>Czech National Bank</span></p>
      <p class="hero-summary">Economist and researcher working on monetary policy, macroprudential policy, banking and financial stability.</p>
      <div class="profile-links">
        <a href="{esc(site['scholar'])}">Google Scholar ↗</a>
        <a href="{esc(site['repec'])}">IDEAS/RePEc ↗</a>
        <a href="{esc(site['orcid'])}">ORCID ↗</a>
      </div>
    </div>
    <figure class="hero-photo"><img src="{esc(site['hero_image'])}" alt="{esc(site['hero_image_alt'])}" fetchpriority="high" decoding="async"><figcaption>Photo: Czech National Bank</figcaption></figure>
  </div>
</section>
<section class="home-section">
  <div class="shell index-shell">
    <div class="section-head"><h2>Recent</h2><a href="/research/">All research →</a></div>
    <div class="recent-list">{''.join(recent_row(x) for x in recent_items)}</div>
  </div>
</section>
<section class="home-section upcoming-section">
  <div class="shell index-shell">
    <div class="section-head"><h2>Upcoming</h2></div>
    <div class="upcoming-list">{''.join(event_row(x) for x in upcoming) if upcoming else '<p class="empty">No public upcoming events listed.</p>'}</div>
  </div>
</section>
'''


topic_buttons = "".join(f'<button type="button" class="topic-button" data-filter-topic="{key}">{label}</button>' for key, label in TOPIC_LABELS)
research_sorted = sorted(research, key=lambda x: x["date"], reverse=True)
research_body = f'''
<section class="page-head"><div class="shell narrow"><span class="signature-rule" aria-hidden="true"></span><h1>Research</h1><p>Publications, working papers and ongoing work.</p></div></section>
<section class="content-section"><div class="shell index-shell">
  <div class="filter-panel" data-filter-scope>
    <div class="filter-main"><div class="type-filter"><button type="button" class="text-filter active" data-filter-kind="all">All</button><button type="button" class="text-filter" data-filter-kind="publication">Publications</button><button type="button" class="text-filter" data-filter-kind="working-paper">Working papers</button><button type="button" class="text-filter" data-filter-kind="work-in-progress">Work in progress</button></div><input class="search-input" type="search" placeholder="Search" aria-label="Search research" data-filter-search></div>
    <details class="topic-filter"><summary>Filter by topic</summary><div class="topic-options">{topic_buttons}</div></details>
  </div>
  <div class="work-list" data-filter-list>{''.join(work_row(x) for x in research_sorted)}</div><p class="no-results" data-no-results hidden>No matching research items.</p>
</div></section>
'''


policy_items = sorted([x for x in policy if x.get("type") != "talk"], key=lambda x: x["date"], reverse=True)
policy_body = f'''
<section class="page-head"><div class="shell narrow"><span class="signature-rule" aria-hidden="true"></span><h1>Policy</h1><p>Selected policy publications, central-bank notes and media contributions.</p></div></section>
<section class="content-section"><div class="shell index-shell">
  <div class="filter-panel" data-filter-scope><div class="filter-main"><div class="type-filter"><button type="button" class="text-filter active" data-filter-kind="all">All</button><button type="button" class="text-filter" data-filter-kind="policy">Policy publications</button><button type="button" class="text-filter" data-filter-kind="media">Media</button></div><input class="search-input" type="search" placeholder="Search" aria-label="Search policy" data-filter-search></div></div>
  <div class="work-list" data-filter-list>{''.join(work_row(x, show_topics=False) for x in policy_items)}</div><p class="no-results" data-no-results hidden>No matching items.</p>
</div></section>
'''


years = sorted({x["year"] for x in presentations}, reverse=True)
year_sections = []
for year in years:
    rows = "".join(presentation_row(x) for x in presentations if x["year"] == year)
    year_sections.append(f'<section class="year-group" id="year-{year}"><h2>{year}</h2><div>{rows}</div></section>')

year_links = "".join(f'<a href="#year-{year}">{year}</a>' for year in years)
year_nav = f'<nav class="year-nav" aria-label="Presentation years">{year_links}<a href="#organized">Organized</a></nav>'

organized_rows_parts = []
for item in organized:
    title_html = f'<a href="{esc(item["url"])}">{esc(item["event"])}{external_icon()}</a>' if item.get("url") else esc(item["event"])
    organized_rows_parts.append(f'''<article class="organized-row"><div class="presentation-meta">{esc(item["date_label"])}</div><div><h3>{title_html}</h3>{f'<p class="venue">{esc(item["location"])}</p>' if item.get("location") else ''}</div></article>''')
organized_rows = "".join(organized_rows_parts)
presentations_body = f'''
<section class="page-head"><div class="shell narrow"><span class="signature-rule" aria-hidden="true"></span><h1>Presentations</h1><p>Talks, conference presentations, research seminars, panels and discussions.</p></div></section>
<section class="content-section"><div class="shell presentation-shell">{year_nav}{''.join(year_sections)}<section class="organized-section" id="organized"><h2>Organized conferences & workshops</h2><div>{organized_rows}</div></section></div></section>
'''


roles_html = "".join(f'''<div class="timeline-row"><div>{esc(r["period"])}</div><div><h3>{esc(r["role"])}</h3><p>{esc(r["institution"])}</p></div></div>''' for r in about["roles"])
networks_html = "".join(f'''<li><strong>{f'<a href="{esc(n["url"])}">{esc(n["name"])}{external_icon()}</a>' if n.get('url') else esc(n['name'])}</strong><span>{esc(n.get("period",""))}</span></li>''' for n in about["networks"])
about_body = f'''
<section class="page-head"><div class="shell narrow"><span class="signature-rule" aria-hidden="true"></span><h1>About</h1>{''.join(f'<p>{esc(p)}</p>' for p in about["intro"])}</div></section>
<section class="content-section"><div class="shell about-grid"><div><h2>Experience</h2>{roles_html}</div><aside><h2>Research networks</h2><ul class="network-list">{networks_html}</ul><div class="identity-links"><a href="{esc(site['orcid'])}">ORCID ↗</a><a href="{esc(site['scholar'])}">Google Scholar ↗</a><a href="{esc(site['repec'])}">IDEAS/RePEc ↗</a></div></aside></div></section>
'''


photo_html = "".join(f'<figure><img loading="lazy" decoding="async" src="{esc(p["url"])}" alt="{esc(p["alt"])}"></figure>' for p in photos)
photos_body = f'''
<section class="page-head"><div class="shell narrow"><span class="signature-rule" aria-hidden="true"></span><h1>Photos</h1><p>For media and conference use. Please credit the Czech National Bank.</p></div></section>
<section class="content-section"><div class="shell"><div class="photo-grid">{photo_html}</div></div></section>
'''


if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir(parents=True)
for sub in ("research", "policy", "presentations", "about", "photos", "assets"):
    (DIST / sub).mkdir()

(DIST / "index.html").write_text(layout("Home", home_body, "home"), encoding="utf-8")
(DIST / "research" / "index.html").write_text(layout("Research", research_body, "research"), encoding="utf-8")
(DIST / "policy" / "index.html").write_text(layout("Policy", policy_body, "policy"), encoding="utf-8")
(DIST / "presentations" / "index.html").write_text(layout("Presentations", presentations_body, "presentations"), encoding="utf-8")
(DIST / "about" / "index.html").write_text(layout("About", about_body, "about"), encoding="utf-8")
(DIST / "photos" / "index.html").write_text(layout("Photos", photos_body, "photos"), encoding="utf-8")
shutil.copy2(ASSETS / "site-v4.css", DIST / "assets" / "site-v4.css")
shutil.copy2(ASSETS / "site.js", DIST / "assets" / "site.js")
shutil.copytree(ASSETS / "images", DIST / "assets" / "images", dirs_exist_ok=True)
shutil.copytree(ASSETS / "files", DIST / "assets" / "files", dirs_exist_ok=True)

paths = ["", "research/", "policy/", "presentations/", "about/", "photos/"]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>https://simonamalovana.com/{p}</loc></url>\n" for p in paths) + "</urlset>\n"
(DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")

rss_items = sorted([x for x in research + policy if parse_date(x["date"]) <= TODAY], key=lambda x: x["date"], reverse=True)[:15]
rss = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0"><channel>', f'<title>{esc(site["name"])} — latest work</title>', '<link>https://simonamalovana.com/</link>', f'<description>{esc(site["description"])}</description>']
for item in rss_items:
    link = item.get("url") or "https://simonamalovana.com/"
    rss += ["<item>", f'<title>{esc(item["title"])}</title>', f'<link>{esc(link)}</link>', f'<guid>{esc(link + "#" + quote(item["title"]))}</guid>', f'<pubDate>{parse_date(item["date"]).strftime("%a, %d %b %Y 00:00:00 +0000")}</pubDate>', "</item>"]
rss.append("</channel></rss>")
(DIST / "feed.xml").write_text("\n".join(rss), encoding="utf-8")
(DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://simonamalovana.com/sitemap.xml\n", encoding="utf-8")

print(f"Built V4: {len(research)} research items, {len(policy_items)} policy/media items, {len(presentations)} presentations, {len(organized)} organized events.")
