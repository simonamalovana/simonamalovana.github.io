# simonamalovana.com

Source for Simona Malovaná's personal website. The site is intentionally dependency-free: a small Python script turns structured JSON content into static HTML and GitHub Actions deploys it to GitHub Pages.

## Why this setup

- GitHub is the single source of truth.
- Research, policy items and events are stored once in `content/*.json`.
- Homepage `Recent` is generated automatically from dated content and removes duplicate titles.
- `Upcoming` is generated automatically from future events.
- A scheduled GitHub Action rebuilds the site daily, so events disappear from `Upcoming` after their date without manual editing.
- No database, CMS, JavaScript framework or paid hosting is required.

## Local build

```bash
python3 scripts/build_v4.py
python3 scripts/enrich_presentation_links.py
python3 -m http.server 8000 -d dist
```

Then open `http://localhost:8000`.

## Content files

- `content/research.json` — publications, working papers and work in progress
- `content/policy.json` — policy contributions, talks and media
- `content/events.json` — future public events
- `content/about.json` — biography, roles and networks
- `content/site.json` — site-wide metadata and profile links
- `content/photos.json` — press / conference photographs
- `assets/images/` — locally hosted website and press photographs
- `assets/files/` — locally hosted CV and downloadable files

## Publishing

Recommended repository name: `simonamalovana.github.io`.

1. Create a public GitHub repository with that exact name.
2. Add these files to the repository's `main` branch.
3. In **Settings → Pages**, select **GitHub Actions** as the source.
4. The site will be available at `https://simonamalovana.github.io`.
5. After review, add `simonamalovana.com` as the custom domain and only then change DNS away from Squarespace.

## Future automation

A later step can add a weekly ORCID/Crossref check that opens a GitHub issue when a new publication is detected. Publication metadata should remain reviewable rather than being silently changed by an external API.
