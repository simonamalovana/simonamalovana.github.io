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

def nav(active):
    links = [
        ("home", "/", "Home"),
        ("research", "/research/", "Research"),
        ("policy", "/policy/", "Policy"),
        ("presentations", "/presentations/", "Presentations"),
        ("about", "/about/", "About"),
        ("photos", "/photos/", "Photos"),
    ]
    out = []
    for key, href, label in links:
        cls = ' class="active" aria-current="page"' if key == active else ""
        out.append(f'<a href="{href}"{cls}>{label}</a>')
    out.append('<a href="https://simonamalovana.com/s/CV-Malovana.pdf">CV ↗</a>')
    return "".join(out)

def external_icon():
    return '<span class="external" aria-hidden="true">↗</span>'

def canonical_for(active):
    path = "" if active == "home" else f"{active}/"
    return f"https://simonamalovana.com/{path}"

def layout(title, body, active="", description=None, extra_head=""):
    page_title = site["name"] if title == "Home" else f"{title} — {site['name']}"
    desc = description or site["description"]
    canonical = canonical_for(active)
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
  <meta property="og:image" content="{esc(site['hero_image'])}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="stylesheet" href="/assets/site-v3.css">
  <link rel="alternate" type="application/rss+xml" title="Simona Malovaná — latest work" href="/feed.xml">
  {extra_head}
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
      <div>
        <strong>Simona Malovaná</strong>
        <p>{esc(site['disclaimer'])}</p>
      </div>
      <div class="footer-links">
        <a href="{esc(site['scholar'])}">Google Scholar ↗</a>
        <a href="{esc(site['repec'])}">IDEAS/RePEc ↗</a>
        <a href="{esc(site['orcid'])}">ORCID ↗</a>
        <a href="{esc(site['github'])}">GitHub ↗</a>
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
        labels = dict(TOPIC_LABELS)
        topic_html = '<div class="tags">' + "".join(
            f'<span class="tag">{esc(labels[g])}</span>' for g in groups
        ) + "</div>"
    authors_html = f'<p class="authors">with {esc(authors)}</p>' if authors else ""
    status_html = f'<p class="status">{esc(status)}</p>' if status else ""
    return f'''<article class="work-card" data-kind="{esc(item.get('type',''))}" data-topics="{esc('|'.join(groups))}">
      <div class="work-date">{esc(month_year(item['date']))}</div>
      <div class="work-main">
        <div class="work-type">{esc(item.get('type','').replace('-', ' ').title())}</div>
        <h3>{title_html}</h3>
        {authors_html}
        <p class="venue">{esc(venue)}</p>
        {status_html}
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
      <div class="recent-meta"><span>{esc(month_year(item['date']))}</span><span>{esc(kind)}</span></div>
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
    kind = item.get("kind", "")
    return f'''<article class="presentation-row">
      <div class="presentation-meta">{esc(item.get("date_label", str(item["year"])))}</div>
      <div class="presentation-main">
        <div class="work-type">{esc(kind)}</div>
        <h3>{event_html}</h3>
        {f'<p>{esc(details)}</p>' if details else ''}
        {f'<p class="venue">{esc(location)}</p>' if location else ''}
      </div>
    </article>'''

recent_items = [x for x in (research + policy) if x.get("type") != "talk" and parse_date(x["date"]) <= TODAY]
recent_items = sorted(recent_items, key=lambda x: x["date"], reverse=True)[:5]
upcoming = sorted([x for x in events if parse_date(x["date"]) >= TODAY], key=lambda x: x["date"])

home_body = f'''
<section class="home-hero">
  <div class="shell home-hero-grid">
    <div class="home-intro">
      <h1>Simona Malovaná</h1>
      <p class="home-role">Executive Director, Research and Statistics Department<br>Czech National Bank</p>
      <p class="home-summary">Economist and researcher working on monetary policy, macroprudential policy, banking and financial stability.</p>
      <div class="home-links">
        <a href="/research/">Research</a>
        <a href="/policy/">Policy</a>
        <a href="/presentations/">Presentations</a>
        <a href="/about/">About</a>
      </div>
      <div class="profile-links">
        <a href="{esc(site['scholar'])}">Google Scholar ↗</a>
        <a href="{esc(site['repec'])}">IDEAS/RePEc ↗</a>
        <a href="{esc(site['orcid'])}">ORCID ↗</a>
      </div>
    </div>
    <figure class="home-photo"><img src="{esc(site['hero_image'])}" alt="{esc(site['hero_image_alt'])}"><figcaption>Photo: Czech National Bank</figcaption></figure>
  </div>
</section>
<section class="home-section">
  <div class="shell home-content">
    <div class="section-title"><h2>Recent</h2><a href="/research/">Research archive →</a></div>
    <div class="recent-list">{''.join(recent_row(x) for x in recent_items)}</div>
  </div>
</section>
<section class="home-section upcoming-section">
  <div class="shell home-content">
    <div class="section-title"><h2>Upcoming</h2></div>
    <div class="upcoming-list">{''.join(event_row(x) for x in upcoming) if upcoming else '<p class="empty">No public upcoming events listed.</p>'}</div>
  </div>
</section>
'''

topic_buttons = "".join(f'<button type="button" class="chip" data-filter-topic="{key}">{label}</button>' for key, label in TOPIC_LABELS)
research_sorted = sorted(research, key=lambda x: x["date"], reverse=True)
research_body = f'''
<section class="page-head"><div class="shell narrow"><h1>Research</h1><p>Publications, working papers and ongoing work.</p></div></section>
<section class="content-section"><div class="shell">
  <div class="filter-panel" data-filter-scope>
    <div class="filter-row"><div class="chips"><button type="button" class="chip active" data-filter-kind="all">All</button><button type="button" class="chip" data-filter-kind="publication">Publications</button><button type="button" class="chip" data-filter-kind="working-paper">Working papers</button><button type="button" class="chip" data-filter-kind="work-in-progress">Work in progress</button></div><input class="search-input" type="search" placeholder="Search research" aria-label="Search research" data-filter-search></div>
    <div class="topic-row"><span>Topic</span><div class="chips secondary">{topic_buttons}</div></div>
  </div>
  <div class="work-list" data-filter-list>{''.join(work_row(x) for x in research_sorted)}</div><p class="no-results" data-no-results hidden>No matching research items.</p>
</div></section>
'''

policy_items = sorted([x for x in policy if x.get("type") != "talk"], key=lambda x: x["date"], reverse=True)
policy_body = f'''
<section class="page-head"><div class="shell narrow"><h1>Policy</h1><p>Selected policy publications, central-bank notes and media contributions.</p></div></section>
<section class="content-section"><div class="shell">
  <div class="filter-panel" data-filter-scope><div class="filter-row"><div class="chips"><button type="button" class="chip active" data-filter-kind="all">All</button><button type="button" class="chip" data-filter-kind="policy">Policy publications</button><button type="button" class="chip" data-filter-kind="media">Media</button></div><input class="search-input" type="search" placeholder="Search policy" aria-label="Search policy" data-filter-search></div></div>
  <div class="work-list" data-filter-list>{''.join(work_row(x, show_topics=False) for x in policy_items)}</div><p class="no-results" data-no-results hidden>No matching items.</p>
</div></section>
'''

years = sorted({x["year"] for x in presentations}, reverse=True)
year_sections = []
for year in years:
    rows = "".join(presentation_row(x) for x in presentations if x["year"] == year)
    year_sections.append(f'<section class="year-group"><h2>{year}</h2><div>{rows}</div></section>')
organized_rows_parts = []
for x in organized:
    title_html = f'<a href="{esc(x["url"])}">{esc(x["event"])}{external_icon()}</a>' if x.get("url") else esc(x["event"])
    location_html = f'<p class="venue">{esc(x["location"])}</p>' if x.get("location") else ""
    organized_rows_parts.append(f'''<article class="organized-row"><div class="presentation-meta">{esc(x["date_label"])}</div><div><h3>{title_html}</h3>{location_html}</div></article>''')
organized_rows = "".join(organized_rows_parts)
presentations_body = f'''
<section class="page-head"><div class="shell narrow"><h1>Presentations</h1><p>Talks, conference presentations, research seminars, panel contributions and discussions.</p></div></section>
<section class="content-section"><div class="shell presentation-shell">{''.join(year_sections)}<section class="organized-section"><h2>Organized conferences & workshops</h2><div>{organized_rows}</div></section></div></section>
'''

roles_html = "".join(f'''<div class="timeline-row"><div>{esc(r["period"])}</div><div><h3>{esc(r["role"])}</h3><p>{esc(r["institution"])}</p></div></div>''' for r in about["roles"])
networks_html = "".join(f'''<li><div><strong>{esc(n["name"])}</strong><span>{esc(n.get("period",""))}</span></div></li>''' for n in about["networks"])
about_body = f'''
<section class="page-head"><div class="shell narrow"><h1>About</h1>{''.join(f'<p>{esc(p)}</p>' for p in about["intro"])}</div></section>
<section class="content-section"><div class="shell about-grid"><div><h2>Experience</h2>{roles_html}</div><aside><h2>Research networks</h2><ul class="network-list">{networks_html}</ul><div class="identity-links"><a href="{esc(site['orcid'])}">ORCID ↗</a><a href="{esc(site['scholar'])}">Google Scholar ↗</a><a href="{esc(site['repec'])}">IDEAS/RePEc ↗</a></div></aside></div></section>
'''

photo_html = "".join(f'<figure><img loading="lazy" src="{esc(p["url"])}" alt="{esc(p["alt"])}"></figure>' for p in photos)
photos_body = f'''
<section class="page-head"><div class="shell narrow"><h1>Photos</h1><p>For media and conference use. Please credit the Czech National Bank.</p></div></section>
<section class="content-section"><div class="shell"><div class="photo-grid">{photo_html}</div></div></section>
'''

if DIST.exists(): shutil.rmtree(DIST)
DIST.mkdir(parents=True)
for sub in ("research", "policy", "presentations", "about", "photos", "assets"): (DIST / sub).mkdir()
(DIST / "index.html").write_text(layout("Home", home_body, "home"), encoding="utf-8")
(DIST / "research" / "index.html").write_text(layout("Research", research_body, "research"), encoding="utf-8")
(DIST / "policy" / "index.html").write_text(layout("Policy", policy_body, "policy"), encoding="utf-8")
(DIST / "presentations" / "index.html").write_text(layout("Presentations", presentations_body, "presentations"), encoding="utf-8")
(DIST / "about" / "index.html").write_text(layout("About", about_body, "about"), encoding="utf-8")
(DIST / "photos" / "index.html").write_text(layout("Photos", photos_body, "photos"), encoding="utf-8")
shutil.copy2(ASSETS / "site-v3.css", DIST / "assets" / "site-v3.css")
shutil.copy2(ASSETS / "site.js", DIST / "assets" / "site.js")
paths = ["", "research/", "policy/", "presentations/", "about/", "photos/"]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>https://simonamalovana.com/{p}</loc></url>\n" for p in paths) + "</urlset>\n"
(DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
rss_items = sorted([x for x in research + policy if parse_date(x["date"]) <= TODAY], key=lambda x: x["date"], reverse=True)[:15]
rss = ['<?xml version="1.0" encoding="UTF-8"?>','<rss version="2.0"><channel>',f'<title>{esc(site["name"])} — latest work</title>','<link>https://simonamalovana.com/</link>',f'<description>{esc(site["description"])}</description>']
for item in rss_items:
    link = item.get("url") or "https://simonamalovana.com/"
    rss += ["<item>",f'<title>{esc(item["title"])}</title>',f'<link>{esc(link)}</link>',f'<guid>{esc(link + "#" + quote(item["title"]))}</guid>',f'<pubDate>{parse_date(item["date"]).strftime("%a, %d %b %Y 00:00:00 +0000")}</pubDate>',"</item>"]
rss.append("</channel></rss>")
(DIST / "feed.xml").write_text("\n".join(rss), encoding="utf-8")
(DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://simonamalovana.com/sitemap.xml\n", encoding="utf-8")
print(f"Built {len(research)} research items, {len(policy_items)} policy/media items, {len(presentations)} presentations, {len(organized)} organized events.")
