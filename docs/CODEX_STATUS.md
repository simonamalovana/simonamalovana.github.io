# Codex development status

**Status date:** 12 September 2026 (UTC)
**Phase:** audit and planning complete; implementation not started.

## Approval state

**No implementation goal is approved yet.**

Codex must not redesign, rewrite, restructure, or intentionally change the deployed website until the product owner approves a goal and any relevant decisions in `docs/PLAN.md`. The present repository change adds documentation only and does not change the build, generated artifact, content, assets, workflow, or production behavior.

## Established baseline

- Public repository: `simonamalovana/simonamalovana.github.io`.
- Production branch: `main` (the local audit branch is `work`).
- Audited/deployed source SHA: `7bb73edd7ed5f034055a138f091b39bc5b65a6c3`.
- Latest observed scheduled run for that SHA: successful on 12 September 2026.
- Deployment: GitHub Actions uploads generated `dist/` to GitHub Pages for non-pull-request runs.
- Active implementation: V4 generator plus presentation/work/personal/prelaunch post-processors.
- Baseline generated surface: 7 HTML routes, 33 research records, 16 displayed policy/media records, 49 presentations, 8 organized events, 4 media photos, 16 personal photos in 2 responsive sizes, CV, RSS, sitemap, and robots.
- Reconstructed artifact size: 51 files, approximately 3.03 MiB on the audit date.

Direct access to the live domains was blocked by the audit environment's outbound proxy. Production identity is based on the matching GitHub `main` SHA, successful Actions run, workflow inspection, and local reconstruction; public-domain response headers, redirects, DNS, TLS, and rendering remain to be verified from an unrestricted environment.

## Baseline checks completed

- Inspected every tracked file category, active and historical generators/styles, structured content, assets, metadata generation, validators, workflow, full available branch/ref set, and redesign/migration/prelaunch commit history.
- Confirmed the selected production Python scripts compile.
- Reproduced the exact ordered CI build after installing ReportLab/Pillow.
- Passed migration and prelaunch validators.
- Confirmed the build produced the expected route/content/image inventory.
- Confirmed the build currently mutates tracked `scripts/build_cv.py` and the CV PDF locally; those incidental changes were restored and are documented as a risk.
- Confirmed legacy `scripts/build.py` does not compile; it is not used by production.

## Constraints for the next session

1. Read root `AGENTS.md`, `docs/PLAN.md`, and `docs/NEXT_GOAL.md` before editing.
2. Ask for/confirm goal approval and applicable product-owner decisions.
3. Reconfirm `main`/deployed SHA and a clean working tree; this status can become stale.
4. Preserve production output and content unless an owner-approved change explicitly says otherwise.
5. Use a feature branch, run the full gate, provide screenshots for perceptible changes, and document rollback.

## Recommended approval statement

The product owner can authorize the proposed work with wording such as:

> Approve the production-parity, non-mutating quality-gate goal in `docs/NEXT_GOAL.md`. Preserve current rendered behavior and content; bring back any unavoidable visible or editorial differences for separate approval.
