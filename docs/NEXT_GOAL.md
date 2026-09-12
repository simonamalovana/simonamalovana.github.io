# Proposed next long-running goal

## Goal: establish a reproducible, non-mutating production build and comprehensive parity gate

### Why this should be first

The live site is polished and content-rich, but its effective output is assembled by an ordered chain of a base generator and four HTML/CSS post-processors. The CI build also installs floating dependencies and mutates tracked CV source/output in its disposable checkout. Existing validators protect important migration facts but largely search generated strings; they cannot reliably detect broken internal links, malformed HTML/metadata, missing routes, accidental content loss outside hand-picked assertions, or broad accessibility regressions.

Redesigning or editing positioning before solving this would make it hard to distinguish intended product changes from build-chain regressions. A production-parity gate creates the safety rails needed for long-running autonomous development and is substantial while remaining conservative for a live site.

### Objective

Create a single documented, pinned, deterministic, and non-mutating build/test path that reproduces today's approved generated site, protects all current content and stable URLs, and gives pull requests actionable evidence about production parity, accessibility fundamentals, metadata, internal links, and artifact integrity.

This is infrastructure and test work, **not a redesign or content rewrite**.

## In scope

1. Capture an auditable manifest of expected routes, content counts, stable URLs, legacy resources, key metadata, and asset budgets from the approved baseline.
2. Provide one local/CI entry command for the current ordered build.
3. Make CV generation consume an authoritative source without rewriting tracked Python during builds; ensure a normal build leaves `git status` clean.
4. Pin Python dependencies and document intentional upgrades.
5. Add generated-site checks for:
   - valid JSON inputs and required fields/types/date formats;
   - duplicate content identifiers/titles where meaningful;
   - required routes and stable URLs;
   - internal links, fragments, and asset existence;
   - unique titles/descriptions/canonicals/Open Graph URLs;
   - parseable and accurate JSON-LD;
   - one H1, landmark/skip-link basics, controls and image alternatives;
   - sitemap/robots/RSS agreement;
   - expected corpus counts and known legacy resources;
   - HTML/image/artifact size budgets.
6. Keep existing migration/prelaunch validators until replacements demonstrate equivalent or stronger coverage.
7. Clearly quarantine/document historical V1–V3 generators without deleting provenance in the first implementation.
8. Update README developer instructions to match the real build and deployment mechanism.
9. Preserve GitHub Pages triggers, permissions, artifact path, environment, and daily date-based behavior.

## Explicitly out of scope

- visual redesign, new navigation, new homepage narrative, or new calls to action;
- content additions, removals, translations, authorship reinterpretation, or biography edits;
- URL/domain/DNS/Pages-setting changes;
- analytics, tracking, forms, embeds, CMSs, frameworks, bundlers, or webfonts;
- removing the Personal gallery or any legacy resource;
- broad external-link replacement based only on automated status codes.

## Delivery stages

### Stage 1 — Freeze and characterize baseline

- Reconfirm deployed SHA and latest successful Pages run.
- Generate from a clean checkout on the audit date and record route, semantic content, metadata, link, and asset manifests.
- Identify intended date-sensitive differences and exclude only those narrow values from reproducibility comparisons.
- Document custom-domain checks that require an unrestricted environment.

### Stage 2 — Reproducible build entry point

- Add a small orchestration command using the existing language/tooling.
- Pin ReportLab/Pillow versions with hashes or an equivalently reviewable lock mechanism.
- Refactor the CV audit into stable source data or fold already-approved corrections into the generator so builds do not edit tracked files.
- Run twice from clean state and prove stable output/clean Git state.

### Stage 3 — Quality and parity tests

- Implement fast, dependency-light structural and link checks.
- Add content-preservation assertions based on the baseline manifest.
- Add standards-based HTML/accessibility tooling only where the maintenance cost is justified; keep browser-heavy checks separate if necessary.
- Produce concise failure messages that tell an autonomous agent what invariant changed.

### Stage 4 — CI and documentation integration

- Make pull requests run the same one-command build/gate.
- Preserve non-PR Pages deployment conditions exactly.
- Optionally upload a review artifact if this does not broaden deployment permissions.
- Replace stale README setup instructions with current architecture, safe local workflow, validation, and release/rollback instructions.

### Stage 5 — Production verification

- Demonstrate no unintended semantic or visual changes through manifest comparison and representative screenshots.
- Merge only after review.
- Observe the `main` Actions build/deploy, then smoke-test all public routes, assets, custom-domain redirects, TLS, headers, RSS, sitemap, and filters from unrestricted networking.

## Acceptance criteria

- A clean checkout can build and validate with one documented command.
- The command succeeds twice consecutively and leaves no tracked modifications or untracked caches outside ignored build output.
- Dependencies are pinned; scheduled builds cannot silently select a new ReportLab/Pillow release.
- All current routes, content records, future-event behavior, images, CV, supplementary links, identity links, and legacy-resource invariants remain present.
- Generated HTML retains current semantic content and styling references. Any difference is enumerated and separately approved; no intentional perceptible change is bundled into this goal.
- The gate catches a deliberately introduced broken internal link, missing image, duplicate canonical/title, malformed JSON-LD, lost content item, missing legacy resource, and budget overflow.
- Existing migration and prelaunch validators pass.
- Pull-request CI validates without Pages deployment; `main`, schedule, and manual runs retain the current Pages deploy behavior.
- Documentation identifies the authoritative content/CV sources, production entry point, date-sensitive behavior, custom-domain ownership gap, and rollback process.
- Post-merge verification confirms the expected SHA and all smoke tests, or triggers an immediate revert.

## Validation evidence required in the pull request

- exact clean-build and test commands with results;
- before/after route/content/metadata/asset manifest comparison;
- `git status` after two builds;
- selected desktop/tablet/mobile screenshots showing parity;
- keyboard/filter smoke-test notes;
- CI run link and generated artifact summary;
- known network-limited checks clearly separated from failures;
- a rollback section naming the revert commit/process.

## Risks and controls

| Risk | Control |
| --- | --- |
| Refactoring changes emitted HTML | Compare normalized DOM/semantic manifests and screenshots; keep changes reversible |
| Date-derived Upcoming causes false diffs | Inject/document the build date for tests while retaining production semantics |
| CV bytes remain nondeterministic | Compare extracted semantic content where PDF metadata cannot be stable, then eliminate controllable timestamps |
| A stronger validator rejects valid legacy markup | Introduce checks incrementally and review exceptions; never delete content to make a test green |
| Dependency pin becomes stale | Document a scheduled, reviewed update procedure rather than floating on every daily deployment |
| Historical scripts confuse callers | Label/quarantine first; defer deletion until provenance and owner approval are clear |
| Public domain differs from reconstructed artifact | Make unrestricted post-deploy smoke testing a release gate |

## Approval needed

This goal should begin only after explicit product-owner approval. Approval should also confirm that current rendered content/appearance is the parity baseline and that any discovered editorial ambiguity will be reported rather than changed within this goal.
