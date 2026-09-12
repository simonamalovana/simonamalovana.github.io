# Repository instructions for Codex

## Product purpose and audience

This repository produces Simona Malovaná's live professional website. It presents her work as an economist, central-bank leader, researcher, editor, teacher, and speaker. The primary audiences are central bankers and policymakers, academic researchers and prospective collaborators, conference and media organizers, students, and journalists.

Treat the site as a professional record, not as a marketing microsite. Accuracy, provenance, legibility, and production continuity matter more than novelty.

## Product and content hierarchy

Preserve this hierarchy unless the product owner approves a change:

1. Identity and current Czech National Bank leadership role.
2. Research: publications, working papers, work in progress, topics, abstracts, and supplementary resources.
3. Policy contributions and media.
4. Presentations, panels, seminars, and organized events.
5. Biography, appointments, affiliations, and research networks.
6. CV, direct email, scholarly profiles, and media photographs.
7. Personal photography as a deliberately secondary footer destination.

The homepage should answer, quickly: who Simona is, what she does now, what she researches, what is recent, what is upcoming, and how to inspect her record or contact her.

## Production constraints

- This is an existing live GitHub Pages site. Assume every merge to `main` can affect production.
- The production artifact is generated; `dist/` is ignored and must not be committed.
- Preserve URLs, valid content, downloads, metadata, and responsive behavior. Do not remove an item merely because it looks old, duplicated, or peripheral: determine whether it represents a distinct version, venue, resource, or legacy URL first.
- Use `content/legacy_resource_links.json` and both validation scripts as migration safeguards. Keep the stable `/personal/`, `/photos/`, `/presentations/`, and CV URLs unless a reviewed redirect strategy exists.
- Never treat `README.md`, an old build script, or a branch name as proof of production state. Confirm the workflow, the deployed commit/run, and the generated artifact.
- Keep changes reversible and narrowly scoped. Separate behavior-preserving infrastructure work from visual or editorial changes.
- Never put a `try`/`catch` block around imports.

## Repository map

- `content/*.json`: canonical structured website content and link inventories.
- `assets/site-v4.css`: active base visual system.
- `assets/prelaunch.css`: active final override layer, loaded after `site-v4.css`.
- `assets/site.js`: dependency-free research/policy filtering.
- `assets/images/`: professional and responsive personal WebP images.
- `assets/files/CV-Simona-Malovana.pdf`: committed CV fallback/source artifact.
- `scripts/build_v4.py`: active base HTML, metadata, sitemap, robots, and RSS generator.
- `scripts/enrich_presentation_links.py`, `scripts/enrich_work_details.py`, `scripts/build_personal.py`, `scripts/prelaunch_polish.py`: ordered post-processors that form part of the active build.
- `scripts/build_cv.py`: ReportLab CV generator; `scripts/apply_cv_audit.py` currently rewrites it before execution.
- `scripts/validate_migration.py` and `scripts/validate_prelaunch.py`: required regression checks.
- `scripts/build.py`, `scripts/build_v2.py`, `scripts/build_v3.py`, and older CSS files: historical implementations, not production entry points.
- `.github/workflows/deploy.yml`: authoritative CI/build/deploy sequence.
- `dist/`: ignored local output and the Pages artifact in CI.

## Deployment

`.github/workflows/deploy.yml` runs on pushes to `main`, pull requests targeting `main`, a daily `04:17 UTC` schedule, and manual dispatch. The build job installs ReportLab, runs the ordered generation/post-processing pipeline, and runs both validators. Pull requests stop after validation. Non-PR runs configure Pages, upload `dist/`, and deploy it through `actions/deploy-pages` to the `github-pages` environment. The schedule is functional behavior: it removes past events from the generated homepage without a content commit.

Do not change the deploy branch, Pages method, custom-domain assumptions, action permissions, schedule, or environment without product-owner approval and a rollback plan. Do not add a second deployment mechanism.

## Safe local validation

Start with read-only checks and a clean tree:

```bash
git status --short --branch
python3 -m json.tool content/site.json >/dev/null
python3 -m py_compile scripts/apply_cv_audit.py scripts/fetch_personal_assets.py scripts/build_v4.py scripts/enrich_presentation_links.py scripts/enrich_work_details.py scripts/build_personal.py scripts/prelaunch_polish.py scripts/validate_migration.py scripts/validate_prelaunch.py
```

To reproduce CI, install `reportlab` in an isolated environment and run the commands in `.github/workflows/deploy.yml` in their exact order. Important: `scripts/apply_cv_audit.py` rewrites tracked `scripts/build_cv.py`, and `scripts/build_cv.py` rewrites the tracked PDF. Record the pre-build status and inspect or restore incidental tracked changes after the run; never commit generated drift unintentionally.

After generation, always run:

```bash
python3 scripts/validate_migration.py
python3 scripts/validate_prelaunch.py
python3 -m http.server 8000 -d dist
```

For any user-visible change, inspect at representative desktop, tablet, and narrow-mobile widths; exercise keyboard navigation and filters; and capture a screenshot when the environment supports it. Validate every internal URL and asset. Check changed external links with conservative timeouts, but distinguish a server failure from bot blocking or sandbox/network limitations.

## Accessibility, SEO, and performance expectations

- Target WCAG 2.2 AA: semantic landmarks and headings, keyboard access, visible focus, a working skip link, meaningful link text, accurate image alternatives, status announcements, sufficient contrast, and touch targets near 44 CSS pixels where practical.
- Do not use color, hover, or JavaScript as the only way to obtain information. Core content must remain readable when JavaScript is unavailable.
- Test reflow and horizontal overflow at 320, 375, 768, 1024, and wide desktop widths. Respect zoom, reduced-motion preferences if motion is introduced, and content growth.
- Every public HTML route must have a unique, truthful title, description, canonical URL, Open Graph URL/title/description/image, and valid structured data. Keep `robots.txt`, `sitemap.xml`, and `feed.xml` aligned with all indexable routes.
- Use absolute public URLs in social metadata and ensure the social image is appropriately sized and crop-safe. Never publish future or unapproved biographical claims merely to make metadata appear fresh.
- Prefer local, optimized assets. Set intrinsic image dimensions where possible, preserve responsive gallery sources, avoid render-blocking additions, and measure rather than guess about performance.

## Design consistency

The current visual language is restrained, editorial, and institutional: warm off-white surfaces, dark neutral text, a muted teal accent, generous whitespace, fine rules, compact sans-serif typography, left-aligned lists, a formal portrait, and minimal animation. Preserve the information-dense research/presentation treatment and the distinction between professional media photos and personal photography.

Extend existing tokens and patterns before inventing new ones. Avoid gradients, ornamental effects, generic dashboard cards, novelty interactions, icon libraries, remote font dependencies, and gratuitous motion. Do not add React, a CSS framework, a CMS, a package manager, a bundler, or a database for work that static Python, HTML, CSS, and small vanilla JavaScript can handle.

## Content and link discipline

- Treat the JSON files as canonical. Keep dates in `YYYY-MM-DD` form and follow the existing schemas.
- Verify names, titles, employment dates, authorship, publication status, affiliations, email, events, and claims against an authoritative source or explicit owner input.
- Preserve diacritics and the English/Czech wording of titles. Do not silently translate publication or media titles.
- Check that the homepage's date-derived Recent and Upcoming sections behave correctly on the current date and immediately around event dates.
- When changing a URL, determine whether supplementary resources, alternate versions, DOI destinations, or legacy destinations must remain exposed.
- Never fabricate a link, credential, publication state, metric, quotation, or event.

## Git and workflow rules

- Work on a feature branch; do not force-push or commit directly to `main`.
- Begin and end with `git status`. Review `git diff --check`, the full diff, and generated validation output before committing.
- Keep commits focused and use imperative commit subjects. Do not mix audits, content edits, redesigns, and deployment changes in one commit.
- Do not commit `dist/`, caches, local environments, downloaded duplicates, secrets, or unrelated formatting churn.
- Do not rewrite, delete, or squash historical branches/commits as cleanup. Historical V2/V3/V4 and migration work is useful provenance.
- Pull requests must explain production impact, validation performed, screenshots for perceptible changes, content/link provenance, known limitations, and rollback approach.
- A green pull-request build validates generation but does not deploy. A merged/pushed `main` build does deploy; verify its Pages run and public routes after release.

## Product-owner approval gates

Obtain explicit approval before:

- redesigning the visual identity, information architecture, navigation, homepage positioning, or personal/professional balance;
- adding, removing, materially rewriting, or translating biographical, employment, research, policy, presentation, media, contact, disclaimer, or personal content;
- changing the public domain, URL structure, CV URL, redirects, analytics/tracking, cookies, forms, or third-party embeds;
- changing GitHub Pages settings, the deployment mechanism/schedule/permissions, dependency strategy, or introducing a framework/service;
- publishing claims or events that cannot be verified, or accepting a known accessibility, SEO, link-integrity, or production-parity regression.

Routine typo fixes, verified link repairs, test improvements, and behavior-preserving maintenance may proceed through review, provided existing content and production output remain protected.
