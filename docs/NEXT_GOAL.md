# Proposed next long-running goal

## Goal: Establish a reproducible, non-mutating production build and comprehensive parity gate

### Why this should be first

The live site is polished and content-rich, but its effective output is assembled by an ordered chain of a base generator and four HTML/CSS post-processors. The CI build also installs floating dependencies and mutates tracked CV source/output in its disposable checkout. Existing validators protect important migration facts but largely search generated strings; they cannot reliably detect broken internal links, malformed HTML/metadata, missing routes, accidental content loss outside hand-picked assertions, or broad accessibility regressions.

Redesigning or editing positioning before solving this would make it hard to distinguish intended product changes from build-chain regressions. A production-parity gate creates the safety rails needed for long-running autonomous development and is substantial while remaining conservative for a live site.

### Objective

Create one authoritative, documented, pinned, repeatable, and non-mutating build/test command that reproduces today's approved generated site, protects all current public content and stable URLs, and gives pull requests actionable evidence about semantic/normalized production parity, inexpensive accessibility fundamentals, metadata, internal links, and asset integrity. CI must invoke exactly this same command.

This is infrastructure and test work, **not a redesign or content rewrite**. The autonomous task ends with a reviewable pull request; it must not merge its own work, and post-merge GitHub Pages verification is not part of its implementation Definition of Done.

## In scope

1. Capture an auditable manifest of expected routes, content counts, stable URLs, legacy resources, key metadata, and asset budgets from the approved baseline.
2. Provide one authoritative local/CI command for the current ordered build and parity gate.
3. Make CV generation consume an authoritative source without rewriting tracked Python during builds; ensure a normal build leaves `git status` clean.
4. Pin Python dependencies and document intentional upgrades.
5. Add generated-site checks for:
   - valid JSON inputs and required fields/types/date formats;
   - duplicate content identifiers/titles where meaningful;
   - required routes and stable URLs;
   - internal links, fragments, and asset existence;
   - unique titles/descriptions/canonicals/Open Graph URLs;
   - parseable and accurate JSON-LD;
   - inexpensive accessibility fundamentals already represented in the current site: landmarks, one H1, skip link, control labels/states, and image alternatives;
   - sitemap/robots/RSS agreement;
   - expected corpus counts and known legacy resources;
   - HTML/image/artifact size budgets.
6. Keep existing migration/prelaunch validators until replacements demonstrate equivalent or stronger coverage.
7. Clearly quarantine/document historical V1–V3 generators without deleting provenance in the first implementation.
8. Update README developer instructions to match the real build and deployment mechanism.
9. Preserve GitHub Pages triggers, permissions, artifact path, environment, and daily date-based behavior.
10. End with a focused, reviewable pull request containing the required parity evidence and rollback plan.

## Explicitly out of scope

- positioning changes, visual redesign, navigation changes, homepage narrative changes, or new/changed calls to action;
- content additions, removals, translations, authorship reinterpretation, biography edits, or any change to editorial meaning;
- public URL, domain, DNS, GitHub Pages configuration, or deployment-setting changes;
- analytics, tracking, forms, embeds, CMSs, frameworks, bundlers, or webfonts;
- removing the Personal gallery or any legacy resource;
- broad external-link replacement based only on automated status codes.
- full axe, Lighthouse, screen-reader, contrast, zoom/reflow, or cross-browser accessibility work, which belongs in the dedicated accessibility milestone.
- merging the implementation pull request or performing post-merge production verification as part of implementation completion.

## Delivery stages

### Stage 1 — Freeze and characterize baseline

- Reconfirm deployed SHA and latest successful Pages run.
- Generate from a clean checkout on the audit date and record route, semantic content, metadata, link, and asset manifests.
- Identify intended date-sensitive and PDF-metadata differences, then use normalized/semantic comparisons rather than forcing exact-byte reproducibility where it is not meaningful.
- Document custom-domain checks that require an unrestricted environment.

### Stage 2 — Reproducible build entry point

- Add a small orchestration command using the existing language/tooling.
- Pin ReportLab/Pillow versions with hashes or an equivalently reviewable lock mechanism.
- Refactor the CV audit into stable source data or fold already-approved corrections into the generator so builds do not edit tracked files.
- Run twice from clean state and prove normalized/semantic output equivalence and clean Git state.

### Stage 3 — Quality and parity tests

- Implement fast, dependency-light structural and link checks.
- Add content-preservation assertions based on the baseline manifest.
- Limit accessibility assertions to inexpensive structural fundamentals already represented in current markup; defer axe, Lighthouse, screen-reader, contrast, zoom/reflow, and browser accessibility work to the dedicated milestone.
- Produce concise failure messages that tell an autonomous agent what invariant changed.

### Stage 4 — CI and documentation integration

- Make pull requests run the same one-command build/gate.
- Preserve non-PR Pages deployment conditions exactly.
- Optionally upload a review artifact if this does not broaden deployment permissions.
- Replace stale README setup instructions with current architecture, safe local workflow, validation, and release/rollback instructions.

### Stage 5 — PR handoff

- Demonstrate no unintended semantic or visual changes through manifest comparison and representative screenshots.
- Prepare a focused pull request with exact validation commands/results, normalized parity evidence, known limitations, and a rollback plan.
- Stop after the pull request is reviewable. The autonomous implementation agent must not merge it.

## Implementation and PR acceptance criteria

- A clean checkout can build and validate with one authoritative documented command, and CI runs exactly that same command.
- The command succeeds twice consecutively, leaves no tracked modifications or untracked caches outside ignored build output, and produces equivalent normalized/semantic output. Exact PDF bytes and legitimate date-derived values need not match.
- Dependencies are pinned; scheduled builds cannot silently select a new ReportLab/Pillow release.
- All current routes, content records, future-event behavior, images, CV, supplementary links, identity links, and legacy-resource invariants remain present.
- Generated output retains current positioning, visual design, homepage narrative, navigation, calls to action, content/editorial meaning, public URLs, domain assumptions, Pages settings, semantic content, and styling references. Any unavoidable difference is enumerated and separately approved.
- The gate catches a deliberately introduced broken internal link, missing image, duplicate canonical/title, malformed JSON-LD, lost content item, missing legacy resource, and budget overflow.
- Accessibility coverage is limited to inexpensive structural fundamentals already represented by the current site; full browser/accessibility auditing remains deferred.
- Existing migration and prelaunch validators pass.
- Pull-request CI validates without Pages deployment; `main`, schedule, and manual runs retain the current Pages deploy behavior.
- Documentation identifies the authoritative content/CV sources, production entry point, date-sensitive behavior, custom-domain ownership gap, and rollback process.
- The work ends with a focused, reviewable pull request containing validation evidence and rollback instructions; the implementation agent does not merge it.

## Post-merge production verification

This is a separate release responsibility and is **not** part of the autonomous implementation Definition of Done. After a human reviewer/owner merges the pull request, an authorized owner or releaser should:

1. observe the `main` GitHub Actions build and Pages deployment;
2. confirm that the deployed SHA is the reviewed merge result;
3. smoke-test public routes/assets, custom-domain and `github.io` behavior, TLS/headers, RSS, sitemap, and filters from unrestricted networking; and
4. use the documented rollback procedure if production differs from the reviewed parity evidence.

## Validation evidence required in the pull request

- exact clean-build and test commands with results;
- before/after route/content/metadata/asset manifest comparison;
- `git status` and normalized/semantic output comparison after two builds;
- selected desktop/tablet/mobile screenshots showing parity;
- keyboard/filter smoke-test notes;
- pull-request CI run link and generated artifact summary;
- known network-limited checks clearly separated from failures;
- a rollback section naming the revert commit/process.

## Risks and controls

| Risk | Control |
| --- | --- |
| Refactoring changes emitted HTML | Compare normalized DOM/semantic manifests and representative screenshots; keep changes reversible |
| Date-derived Upcoming causes false diffs | Inject/document the build date for tests while retaining production semantics |
| PDF or date-derived bytes legitimately differ | Compare normalized HTML and extracted PDF semantic content; exclude only documented volatile values rather than forcing byte identity |
| A stronger validator rejects valid legacy markup | Introduce checks incrementally and review exceptions; never delete content to make a test green |
| Dependency pin becomes stale | Document a scheduled, reviewed update procedure rather than floating on every daily deployment |
| Historical scripts confuse callers | Label/quarantine first; defer deletion until provenance and owner approval are clear |
| Public domain differs from reconstructed artifact | Hand off unrestricted post-merge smoke testing to the authorized owner/releaser with explicit rollback steps |

## Approval needed

Implementation remains unapproved while this planning pull request is under review. After it is reviewed and merged, the goal should begin only through an explicit product-owner task or approval. Approval should confirm that current rendered content/appearance is the parity baseline and that any discovered editorial ambiguity will be reported rather than changed within this goal.
