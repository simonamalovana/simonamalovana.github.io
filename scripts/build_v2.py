#!/usr/bin/env python3
from __future__ import annotations

import json
import html
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


def esc(value=""):
    return html.escape(str(value), quote=True)


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def month_year(value):
    d = parse_date(value)
    return d.strftime("%B %Y")


def nav(active):
    links = [
        ("home", "/", "Home"),
        ("research", "/research/", "Research"),
        ("policy", "/policy/", "Policy & Talks"),
        ("about", "/about/", "About"),
        ("photos", "/photos/", "Photos"),
    ]
    out = []
    for key, href, label in links:
        cls = ' class="active" aria-current="page"' if key == active else ""
        out.append(f'<a href="{href}"{cls}>{label}</a>')
    return "".join(out)


def external_icon():
    return '<span class="external" aria-hidden="true">↗</span>'


def layout(title, body, active="", description=None, extra_head=""):
    page_title = site["name"] if title == "Home" else f"{title} — {site['name']}"
    desc = description or site["description"]
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
  <meta property="og:url" content="https://simonamalovana.com/">
  <meta property="og:image" content="{esc(site['hero_image'])}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="https://simonamalovana.com/">
  <link rel="stylesheet" href="/assets/site-v2.css">
  <link rel="alternate" type="application/rss+xml" title="Simona Malovaná — latest work" href="/feed.xml">
  {extra_head}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="shell header-inner">
      <a class="brand" href="/" aria-label="Simona Malovaná home">Simona Malovaná</a>
      <nav class="main-nav" aria-label="Main navigation">{nav(active)}<a href="https://simonamalovana.com/s/CV-Malovana.pdf">CV ↗</a></nav>
    </div>
  </header>
  <main id="main">{body}</main>
  <footer class="site-footer">
    <div class="shell footer-grid">
      <div><strong>Simona Malovaná</strong><p>{esc(site['disclaimer'])}</p></div>
      <div class="footer-links">
        <a href="{esc(site['scholar'])}">Google Scholar {external_icon()}</a>
        <a href="{esc(site['repec'])}">IDEAS/RePEc {external_icon()}</a>
        <a href="{esc(site['orcid'])}">ORCID {external_icon()}</a>
        <a href="{esc(site['github'])}">GitHub {external_icon()}</a>
      </div>
    </div>
  </footer>
  <script src="/assets/site.js" defer></script>
</body>
</html>'''


def item_card(item, compact=False):
    url = item.get("url")
    title = esc(item["title"])
    title_html = f'<a href="{esc(url)}">{title}{external_icon()}</a>' if url else title
    authors = item.get("authors", "")
    venue = item.get("venue", "")
    status = item.get("status", "")
    topics = item.get("topics", [])
    topic_html = "" if compact else "".join(f'<span class="tag">{esc(t)}</span>' for t in topics)
    authors_html = f'<p class="authors">with {esc(authors)}</p>' if authors else ""
    status_html = f'<p class="status">{esc(status)}</p>' if status else ""
    return f'''<article class="work-card" data-kind="{esc(item.get('type',''))}" data-topics="{esc('|'.join(topics).lower())}">
      <div class="work-meta"><span>{esc(month_year(item['date']))}</span><span>{esc(item.get('type','').replace('-', ' ').title())}</span></div>
      <h3>{title_html}</h3>
      {authors_html}
      <p class="venue">{esc(venue)}</p>
      {status_html}
      <div class="tags">{topic_html}</div>
    </article>'''


def latest_row(item):
    kind = item.get("type", "").replace("-", " ").title()
    url = item.get("url")
    title = esc(item["title"])
    title_html = f'<a href="{esc(url)}">{title}</a>' if url else title
    venue = item.get("venue", "")
    return f'''<article class="latest-row">
      <div class="latest-date">{esc(month_year(item['date']))}</div>
      <div><span class="eyebrow-inline">{esc(kind)}</span><h3>{title_html}</h3><p>{esc(venue)}</p></div>
    </article>'''


featured = sorted([x for x in research if x.get("featured")], key=lambda x: x["date"], reverse=True)[:3]
latest_items = [x for x in (research + policy) if parse_date(x["date"]) <= TODAY]
latest_items = sorted(latest_items, key=lambda x: x["date"], reverse=True)[:6]
upcoming = sorted([x for x in events if parse_date(x["date"]) >= TODAY], key=lambda x: x["date"])
upcoming_html = "".join(
    f'''<article class="event-row"><div class="event-date">{esc(e.get('date_label') or month_year(e['date']))}</div><div><h3>{esc(e['title'])}</h3><p>{esc(e.get('role',''))}{' · ' if e.get('role') and e.get('location') else ''}{esc(e.get('location',''))}</p></div></article>'''
    for e in upcoming
) or '<p class="muted">No public upcoming events listed at the moment.</p>'

home_body = f'''
<section class="hero">
  <div class="shell hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Economist · Central banker · Researcher</p>
      <h1>Simona<br>Malovaná</h1>
      <p class="hero-role">Executive Director, Research and Statistics<br><span>Czech National Bank</span></p>
      <p class="hero-lead">Research in monetary policy, macroprudential policy, banking and financial stability.</p>
      <div class="hero-actions">
        <a class="editorial-link" href="/research/">Research <span aria-hidden="true">→</span></a>
        <a class="editorial-link" href="/about/">About <span aria-hidden="true">→</span></a>
      </div>
      <div class="profile-links"><a href="{esc(site['scholar'])}">Google Scholar ↗</a><a href="{esc(site['repec'])}">IDEAS/RePEc ↗</a><a href="{esc(site['orcid'])}">ORCID ↗</a></div>
    </div>
    <figure class="hero-figure"><img src="{esc(site['hero_image'])}" alt="{esc(site['hero_image_alt'])}"><figcaption>Photo: Czech National Bank</figcaption></figure>
  </div>
</section>
<section class="section focus-section">
  <div class="shell">
    <div class="section-heading editorial-heading"><span class="section-number">01</span><div><p class="eyebrow">Areas of work</p><h2>Research & policy</h2></div></div>
    <div class="focus-grid">
      <article><span>01</span><h3>Monetary policy & forecasting</h3><p>Forecasting frameworks, monetary transmission and model design.</p></article>
      <article><span>02</span><h3>Financial stability & macroprudential policy</h3><p>Bank lending, borrower-based measures, distributional effects, climate and geopolitical risks.</p></article>
      <article><span>03</span><h3>Data, statistics & research</h3><p>Research strategy, official statistics, data access and reproducible analytical workflows.</p></article>
    </div>
  </div>
</section>
<section class="section selected-section">
  <div class="shell">
    <div class="section-heading split editorial-heading"><div class="heading-pair"><span class="section-number">02</span><div><p class="eyebrow">Selected work</p><h2>Research</h2></div></div><a class="section-link" href="/research/">All research →</a></div>
    <div class="card-grid">{''.join(item_card(x, compact=True) for x in featured)}</div>
  </div>
</section>
<section class="section recent-section">
  <div class="shell two-col">
    <div><div class="section-heading editorial-heading"><span class="section-number">03</span><div><p class="eyebrow">Latest</p><h2>Recent</h2></div></div>{''.join(latest_row(x) for x in latest_items)}</div>
    <aside class="upcoming-panel"><p class="eyebrow">Upcoming</p><h2>Calendar</h2>{upcoming_html}</aside>
  </div>
</section>
'''

all_topics = sorted({t for x in research for t in x.get("topics", [])})
filters = ''.join(f'<button type="button" class="chip" data-filter-topic="{esc(t.lower())}">{esc(t)}</button>' for t in all_topics)
research_sorted = sorted(research, key=lambda x: x["date"], reverse=True)
research_body = f'''
<section class="page-hero"><div class="shell page-hero-grid"><span class="page-number">01</span><div><p class="eyebrow">Research</p><h1>Research</h1><p>Monetary policy, macroprudential policy, banking, financial stability, climate and geopolitical risks.</p></div></div></section>
<section class="section"><div class="shell">
  <div class="filter-panel" data-filter-scope>
    <div class="filter-top"><div class="chips"><button type="button" class="chip active" data-filter-kind="all">All</button><button type="button" class="chip" data-filter-kind="publication">Publications</button><button type="button" class="chip" data-filter-kind="working-paper">Working papers</button><button type="button" class="chip" data-filter-kind="work-in-progress">Work in progress</button></div><input class="search-input" type="search" placeholder="Search research…" aria-label="Search research" data-filter-search></div>
    <details class="topic-filter"><summary>Filter by topic</summary><div class="chips secondary">{filters}</div></details>
  </div>
  <div class="work-list" data-filter-list>{''.join(item_card(x) for x in research_sorted)}</div>
  <p class="no-results" data-no-results hidden>No matching research items.</p>
</div></section>
'''

policy_sorted = sorted(policy, key=lambda x: x["date"], reverse=True)
policy_body = f'''
<section class="page-hero"><div class="shell page-hero-grid"><span class="page-number">02</span><div><p class="eyebrow">Policy, talks & media</p><h1>Policy, talks<br>& media</h1><p>Selected policy briefs, central-bank notes, invited talks, panels and media contributions.</p></div></div></section>
<section class="section"><div class="shell">
  <div class="filter-panel" data-filter-scope><div class="filter-top"><div class="chips"><button type="button" class="chip active" data-filter-kind="all">All</button><button type="button" class="chip" data-filter-kind="policy">Policy</button><button type="button" class="chip" data-filter-kind="talk">Talks</button><button type="button" class="chip" data-filter-kind="media">Media</button></div><input class="search-input" type="search" placeholder="Search policy & talks…" aria-label="Search policy and talks" data-filter-search></div></div>
  <div class="work-list" data-filter-list>{''.join(item_card(x) for x in policy_sorted)}</div>
  <p class="no-results" data-no-results hidden>No matching items.</p>
</div></section>
'''

roles_html = ''.join(f'''<div class="timeline-row"><div>{esc(r['period'])}</div><div><h3>{esc(r['role'])}</h3><p>{esc(r['institution'])}</p></div></div>''' for r in about["roles"])
networks_html = ''.join(f'''<li><div><strong>{esc(n['name'])}</strong><span>{esc(n.get('period',''))}</span></div></li>''' for n in about["networks"])
about_body = f'''
<section class="page-hero"><div class="shell page-hero-grid"><span class="page-number">03</span><div><p class="eyebrow">About</p><h1>About</h1>{''.join(f'<p>{esc(p)}</p>' for p in about['intro'])}</div></div></section>
<section class="section section-tint"><div class="shell two-col about-grid"><div><p class="eyebrow">Current & previous roles</p><h2>Experience</h2>{roles_html}</div><aside><p class="eyebrow">Research networks</p><h2>International collaboration</h2><ul class="network-list">{networks_html}</ul><div class="identity-links"><a href="{esc(site['orcid'])}">ORCID ↗</a><a href="{esc(site['scholar'])}">Google Scholar ↗</a><a href="{esc(site['repec'])}">IDEAS/RePEc ↗</a></div></aside></div></section>
'''

photo_html = ''.join(f'<figure><img loading="lazy" src="{esc(p["url"])}" alt="{esc(p["alt"])}"></figure>' for p in photos)
photos_body = f'''
<section class="page-hero"><div class="shell page-hero-grid"><span class="page-number">04</span><div><p class="eyebrow">Photos</p><h1>Photos</h1><p>For media and conference use. Please credit the Czech National Bank.</p></div></div></section>
<section class="section"><div class="shell"><div class="photo-grid">{photo_html}</div></div></section>
'''

if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir(parents=True)
(DIST / "research").mkdir()
(DIST / "policy").mkdir()
(DIST / "about").mkdir()
(DIST / "photos").mkdir()
(DIST / "assets").mkdir()

(DIST / "index.html").write_text(layout("Home", home_body, "home"), encoding="utf-8")
(DIST / "research" / "index.html").write_text(layout("Research", research_body, "research"), encoding="utf-8")
(DIST / "policy" / "index.html").write_text(layout("Policy & Talks", policy_body, "policy"), encoding="utf-8")
(DIST / "about" / "index.html").write_text(layout("About", about_body, "about"), encoding="utf-8")
(DIST / "photos" / "index.html").write_text(layout("Photos", photos_body, "photos"), encoding="utf-8")

for asset in ASSETS.iterdir():
    if asset.is_file(): shutil.copy2(asset, DIST / "assets" / asset.name)

urls = ["", "research/", "policy/", "about/", "photos/"]
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>https://simonamalovana.com/{u}</loc></url>\n' for u in urls) + '</urlset>\n'
(DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
(DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://simonamalovana.com/sitemap.xml\n", encoding="utf-8")

rss_items = []
for x in latest_items[:10]:
    link = x.get("url") or "https://simonamalovana.com/research/"
    rss_items.append(f'<item><title>{esc(x["title"])}</title><link>{esc(link)}</link><guid>{esc(link)}#{quote(x["title"])}</guid><pubDate>{parse_date(x["date"]).strftime("%a, %d %b %Y 00:00:00 +0000")}</pubDate><description>{esc(x.get("venue", ""))}</description></item>')
rss = f'''<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Simona Malovaná — latest work</title><link>https://simonamalovana.com/</link><description>{esc(site['description'])}</description>{''.join(rss_items)}</channel></rss>'''
(DIST / "feed.xml").write_text(rss, encoding="utf-8")
print(f"Built {DIST} with {len(research)} research items, {len(policy)} policy/talk items, and {len(upcoming)} upcoming events.")