# Product and technical audit plan

**Audit date:** 12 September 2026 (UTC)
**Scope:** audit, persistent instructions, and planning only; no deployed behavior changed.

## Evidence and confidence

The repository has one local branch, `work`, at commit `7bb73ed` (`Align cycling photo captions`). The public GitHub repository reports `main` at that same commit. GitHub's public Actions API reported that the scheduled `Build and deploy website` run for this SHA completed successfully on 12 September 2026. Direct HTTP retrieval of the public site was blocked by this execution environment's outbound proxy with a 403 response, and the unauthenticated Pages settings endpoint returned 404. Therefore:

- production code and the deployed commit are confirmed at high confidence;
- the current artifact is reconstructed at high confidence by executing the checked-in production workflow at that SHA;
- the custom domain's response body, DNS configuration, certificate, redirects, response headers, and pixel rendering are **not independently confirmed** in this audit and remain a release-validation item.

This distinction matters: the README describes intent, while `.github/workflows/deploy.yml`, the successful Actions run, Git history, and generated `dist/` establish the effective product.

## Current site state

### Product and routes

The deployed product is the V4 static site plus four ordered enrichment/polish passes—not any single source template. Its primary navigation is Research, Policy, Presentations, About, and CV. The footer adds scholarly profiles, GitHub, email, Personal, and Media photos.

The generated public surface is:

| Route/artifact | Purpose |
| --- | --- |
| `/` | Identity, current CNB role, research positioning, four recent items, and upcoming events |
| `/research/` | 33 publications, working papers, and works in progress with type/topic/search filters, abstracts, and resources |
| `/policy/` | 16 policy/media entries after talks are separated into presentations |
| `/presentations/` | 49 speaking entries by year plus 8 organized conferences/workshops |
| `/about/` | Four-paragraph biography, 10 current/previous roles, and 3 research networks |
| `/photos/` | Four downloadable professional/media images |
| `/personal/` | Secondary gallery of 16 photographs, each in 480 px and 800 px WebP variants |
| `/assets/files/CV-Simona-Malovana.pdf` | Generated professional CV |
| `/feed.xml`, `/sitemap.xml`, `/robots.txt` | Discovery artifacts |

As of the audit date, the homepage includes two future events (6 October and 23–24 November 2026). The daily build uses UTC runner time indirectly through Python's local `date.today()` and automatically drops events after their date.

### Visual system and interaction

The product uses a dependency-free editorial V4 style: Helvetica/system sans serif, warm paper and pale surface colors, charcoal text, muted teal accents, thin dividers, generous spacing, and a 2:3 professional portrait. Content pages favor compact chronological rows over promotional cards. CSS breakpoints at 900, 720, and 420 pixels collapse grids and wrap navigation. A small vanilla JavaScript module filters research/policy lists; all items exist in the HTML before JavaScript runs.

`assets/prelaunch.css` is a required override loaded after `site-v4.css`. It fixes mobile navigation wrapping, hero order, filter tap areas, metadata contrast, and footer layout. The final HTML is also altered after base generation to add the email and CV to the hero, separate Recent links, add a Presentations call to action, hide Personal from primary navigation, and rename Photos to Media photos.

### Content freshness

The data is unusually current for a professional site: research extends to 3 September 2026, policy/media to 31 August 2026, the biography includes a June 2026 managing-editor appointment, and events extend through November 2026. This freshness is a strength, but several future/current claims are time-sensitive and require ongoing owner verification. The action only changes whether an event appears in Upcoming; it does not archive, validate, or discover content.

### Deployment mechanism

GitHub Actions is the deployment source. Pushes to `main`, the daily `17 4 * * *` schedule, and manual dispatch run the production build; pull requests run the same build and validators but do not configure, upload, or deploy Pages. Non-PR runs upload `dist/` as a Pages artifact and deploy through the `github-pages` environment using `actions/deploy-pages@v4`. The repository does not track generated `dist/`, a `CNAME`, a package lock, or a separate Pages branch.

The current build is a chain:

1. install unpinned `reportlab` (which also supplies Pillow);
2. compile the selected scripts;
3. verify/fetch missing personal assets;
4. textually patch `build_cv.py`, then generate the CV;
5. run `build_v4.py`;
6. enrich presentations and work details;
7. create Personal and alter all footers;
8. apply prelaunch HTML/CSS polish;
9. run migration and prelaunch validators;
10. upload and deploy `dist/` for non-PR events.

## Strengths

- **Clear baseline positioning:** name, exact current role, institution, and subject areas are visible above the fold.
- **Deep professional evidence:** substantial research, policy, presentation, event-organization, role, network, and CV records support credibility.
- **Effective professional hierarchy:** primary navigation emphasizes professional material; the personal gallery remains available but secondary.
- **Strong static foundation:** no framework, CMS, webfont, database, runtime API, analytics, or client-side rendering dependency.
- **Progressive enhancement:** filtering adds utility while the full corpus remains available without JavaScript.
- **Useful discovery layer:** page-specific titles/descriptions/canonicals, Open Graph metadata, a Person JSON-LD graph, RSS, sitemap, robots, favicon, and scholarly identity links exist.
- **Baseline accessibility work:** semantic landmarks, one H1 per page, skip link, visible focus rules, `aria-current`, pressed states, live no-results messages, and descriptive photo alternatives are present.
- **Asset discipline:** main imagery is local WebP; the personal gallery has responsive sources and lazy loading; the full generated artifact is only about 3.03 MiB.
- **Migration protection:** explicit legacy-resource inventories and focused validators reduce the risk of silent content loss.
- **Deployment safety:** pull requests validate but cannot deploy; deploy jobs depend on successful builds; concurrency cancellation limits stale deployments.

## Weaknesses and risks

### Visual hierarchy and brand/positioning

1. **The homepage is credible but generic.** “Economist and researcher working on…” does not communicate the distinctive combination of executive leadership, research strategy, statistics infrastructure, forecasting, teaching, and editorial responsibility.
2. **There is no concise outcome-oriented value proposition.** Visitors see topics, but not the nature of leadership, policy influence, or what collaboration/invitation is welcome.
3. **The homepage Recent stream mixes authored work with institutional/media contributions without explaining Simona's role.** One item displays another named author in source data, which can create an authorship/endorsement ambiguity when shown under a personal Recent heading.
4. **Calls to action are fragmented.** Research, policy, profiles, CV, and email are available, but there is no explicit invitation for research collaboration, speaking/media enquiries, or supervision—and adding one requires owner intent.
5. **The design is polished but extremely restrained.** Dense chronological lists reward expert visitors but provide few editorial pathways for visitors unfamiliar with the research agenda.

### Content and information architecture

1. **Taxonomy is encoded in Python.** Broad topic mappings live separately from research JSON, so new raw topics can silently fall into “Methods & central banking.”
2. **Dates are display proxies rather than consistently precise publication dates.** Many records use the first day of a month; schema and editorial conventions are undocumented.
3. **Role semantics are inconsistent across areas.** Research authors are rendered as “with …”; policy items can name people without stating Simona's own contribution; presentations use event/details fields with different meanings.
4. **The CV has two competing notions of source.** A PDF is tracked, but CI mutates `build_cv.py` and regenerates the PDF. It is not clear whether content JSON, `build_cv.py`, or the committed PDF is authoritative.
5. **Personal and photos data use different image models.** Professional photos omit explicit dimensions in generated markup; personal images include them.
6. **The README is stale.** Its local build runs only two steps, omits dependencies/validators/post-processors, and its publishing instructions read like setup guidance even though the site is already deployed.
7. **There is no explicit content review cadence, owner/date metadata, or stale-event report.** Daily deployment can keep the shell technically current while biography and publication facts age.

### Homepage effectiveness and navigation

1. The primary navigation is concise and preserves the CV, but it has no explicit Home item; the name/logo is the only home affordance.
2. On narrow screens, navigation wraps rather than using a menu. This avoids hidden navigation and JavaScript dependency, but can produce a tall, visually busy header and uneven target geometry.
3. The homepage lacks a short “selected/featured” explanation or routes by visitor intent (researcher, organizer, media).
4. Upcoming events disappear from the homepage after their start date, even for multi-day events because only one start date drives visibility.
5. External-link arrows are visual text in some locations rather than uniformly hidden/announced semantics, and new destinations do not explain whether they are PDFs, DOI pages, videos, or event pages.

### Research, policy, publications, and presentations UX

1. Search/filter state is not represented in the URL and cannot be shared or restored on reload.
2. Only one global filter scope is supported by the JavaScript, which is fine today but is an undocumented constraint.
3. Results counts are not shown and filter changes do not explicitly announce the count, only the no-results case.
4. The presentation archive is long (49 entries) and depends on in-page year links; it lacks topical/type filters and a “back to years/top” aid.
5. Resource enrichment is string replacement against generated HTML, creating coupling between exact formatting and content.
6. Entries without public URLs can look less actionable without explaining availability; conversely, supplementary links are useful but labels/provenance need systematic review.

### Accessibility

The current checks assert selected source strings, not conformance. Important unverified or incomplete areas are:

- no automated HTML conformance, axe-core, Lighthouse, or screen-reader smoke test;
- no measured color-contrast report across all states;
- touch targets are improved only in a narrow breakpoint and may remain below 44 px elsewhere;
- no reduced-motion rule (currently low risk because there is no motion);
- focus after activating in-page year navigation and filtering has not been behaviorally tested;
- links that trigger downloads do not announce file format/size, and the CV link's arrow is literal text;
- image alternatives exist, but the portrait and social-image alt share one description despite different source images;
- `<main tabindex="-1">` supports programmatic focus, but the skip link's actual focus/scroll behavior needs browser testing;
- zoom/reflow and header wrapping at 320 px need visual verification, not string assertions.

### SEO and social metadata

1. `sitemap.xml` excludes `/personal/` even though it is a public, internally linked page with a self-canonical. This sends mixed indexing signals.
2. Person JSON-LD is duplicated unchanged on every page rather than being augmented with page-specific `WebPage`/`ProfilePage`/`CollectionPage` context.
3. Metadata lacks `og:site_name`, `og:locale`, explicit Twitter title/description/image, image dimensions/MIME, and a stable social crop validation. These are enhancements, not critical failures.
4. The Open Graph image is an 80 KiB WebP. Platform support and the actual crop/size have not been tested; a dedicated 1200×630 social asset may be safer.
5. RSS GUIDs concatenate an external URL and title fragment rather than using an owned, immutable identifier; channel freshness metadata is absent.
6. Sitemap entries have no `lastmod`, and content pages do not expose machine-readable publication metadata.
7. No custom 404 page is generated.
8. There is no Search Console/Bing verification or analytics evidence in the repository; owner intent and privacy requirements must precede any addition.

### Performance

The baseline should be fast: static HTML, about 26 KiB of CSS/JS across the active files, no fonts/framework, optimized WebP assets, and only the hero loaded eagerly. Remaining issues:

- professional images lack HTML width/height, increasing layout-shift risk on `/photos/`;
- all 32 personal variants and all professional photos are copied into every deployment (reasonable at current total size, but uncached performance headers are controlled outside the repository);
- the homepage portrait is 76 KiB and high priority, but responsive `srcset` is absent;
- no asset hashing/version query means cache invalidation relies on Pages behavior;
- no Lighthouse/WebPageTest budget or generated-size regression check exists;
- response compression, cache headers, TLS, and redirects could not be measured from this environment.

### Broken and legacy links

Local generated route/asset checks are feasible and should become automated. The migration validator protects known legacy resource URLs, but the repository has no general external-link checker. Direct public-site checks were proxy-blocked during this audit, so no claim is made that every external destination currently resolves. External checks must account for DOI redirects, Google Scholar bot defenses, publisher authentication, PDF responses, and deliberate archival links. The hard-coded legacy CV URL from the earliest generator is no longer in the active V4 navigation.

### Maintainability and deployment safety

1. **The effective template is distributed across five scripts.** Repeated regex/string transformations of emitted HTML are brittle and difficult to reason about.
2. **Obsolete build systems remain adjacent to production.** `scripts/build.py` is syntactically invalid; V2/V3 scripts and four CSS generations are easy for an autonomous agent to invoke accidentally.
3. **The workflow mutates tracked source during a build.** `apply_cv_audit.py` changed `scripts/build_cv.py` in the local reproduction, and CV generation changed the tracked PDF. CI's disposable checkout hides this non-reproducibility.
4. **Dependencies are unpinned and implicit.** Installing latest ReportLab/Pillow can change output or break a scheduled production deployment without a repository commit.
5. **Scheduled runs deploy.** A dependency release or date boundary can alter/fail production daily even when nobody merges code.
6. **Actions use version tags rather than immutable commit SHAs.** This is common but weakens supply-chain reproducibility.
7. **Validation is bespoke and output-string-oriented.** It is valuable for migration invariants but does not validate HTML, structured data, link integrity, duplicate IDs, heading order, or visual parity.
8. **No staging artifact is uploaded for pull requests.** Reviewers cannot easily inspect the exact generated result from CI.
9. **Custom-domain state is external.** There is no tracked `CNAME`; Pages API details were not publicly retrievable, so domain/DNS ownership and rollback need documentation outside inference.

## Highest-value next milestones

### Milestone 1 — Production-parity, non-mutating quality gate (proposed first goal)

Make the current build deterministic and understandable without intentionally changing rendered pages: create one documented build entry point, stop build-time source mutation, pin dependencies, add structural/local-link/metadata checks, and archive or clearly fence legacy entry points. Establish a checked baseline for every route and asset.

**Acceptance criteria**

- One command reproduces the ordered CI build from a clean checkout.
- Running it leaves tracked files unchanged.
- Dependency versions are pinned with a documented update process.
- The output retains all seven HTML routes, the CV, 33 research items, 16 policy/media items, 49 presentations, 8 organized events, four media photos, 16 personal photos/two sizes, known legacy resources, RSS, robots, and sitemap.
- Except for approved nondeterministic date-derived Upcoming content and harmless serialization, a reviewed production snapshot/DOM manifest shows no user-visible change.
- Automated checks cover JSON parsing/schema invariants, duplicate IDs, internal links/assets/fragments, one H1, titles/descriptions/canonicals/OG, image alt/dimensions policy, structured-data parsing, RSS/sitemap/robots consistency, and generated size budgets.
- Pull requests run the gate; non-PR deploy behavior remains unchanged.
- Rollback is a single revert, and the existing validators remain green.

### Milestone 2 — Verify content provenance and resolve ownership ambiguity

Create a review ledger for every current role, future event, featured/recent item, and externally linked publication/resource. Define “authored,” “co-authored,” “led,” “edited,” “featured,” and “media appearance” semantics, then correct only owner-approved ambiguities.

### Milestone 3 — Accessibility and responsive conformance pass

Test keyboard, screen reader, zoom/reflow, contrast, touch targets, filter announcements, and core flows in real browsers. Fix issues without a visual redesign; add automated axe/Lighthouse checks with sensible thresholds.

### Milestone 4 — SEO/social and resilience pass

Resolve sitemap policy for Personal, add a custom 404, improve page-specific structured data and social-image metadata/assets, and verify domain redirects/canonicals/Search Console ownership after owner decisions.

### Milestone 5 — Owner-approved positioning and homepage evolution

Only after content semantics and regression safety are established, refine the homepage narrative and calls to action around the desired balance of executive leadership, active scholarship, policy influence, teaching/editorial work, speaking, and media availability.

## Validation strategy for future work

1. **Repository:** clean status, JSON parse/schema checks, selected-script compilation, `git diff --check`, and secret/large-file review.
2. **Build:** clean isolated environment, pinned dependencies, one entry command, validators, repeat build/hash comparison, and assertion that tracked files remain unchanged.
3. **Generated site:** HTML/JSON-LD/RSS/XML validation; internal URL, asset, anchor, canonical, sitemap, and accessibility rules; item-count/content-preservation manifest.
4. **Browser:** desktop/tablet/320–375 px mobile screenshots, keyboard-only flows, filters, skip link, zoom to 200%/400%, reduced-motion mode, and JavaScript-disabled readability.
5. **External:** link checker with retries and classified failures; verify DOI/publisher/video/event/profile/CNB destinations manually where automation is blocked.
6. **Release:** review deploy diff/artifact, merge only with approval, watch the `main` Pages run, smoke-test custom domain and `github.io` redirect behavior, check TLS/security/cache headers, and retain revert instructions.
7. **Ongoing:** monthly content/link review, pre-event and post-event checks, quarterly accessibility/SEO audit, and deliberate dependency updates rather than surprise scheduled upgrades.

## Product-owner decisions (maximum five)

1. **Primary positioning:** Should the homepage lead with executive central-bank leadership, active research, or an explicitly equal combination?
2. **Contribution semantics:** Which policy/media/research items are Simona's authored work, team output under her leadership, interviews, editorial selections, or recommended institutional work—and which belong in “Recent” on her personal site?
3. **Contact intent:** Should email remain a general contact, or should the site explicitly invite speaking, media, collaboration, teaching/supervision, or none of these?
4. **Indexing and privacy:** Should `/personal/` be indexed and included in the sitemap, remain public-but-secondary with `noindex`, or require removal from the public professional site?
5. **Domain and measurement ownership:** Confirm `simonamalovana.com` as the permanent canonical domain, who controls DNS/Pages/Search Console, and whether privacy-preserving analytics are desired at all.
