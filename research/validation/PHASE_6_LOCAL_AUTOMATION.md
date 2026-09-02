# Phase 6 — Local Automation and Final Validation

Updated: 2026-09-02

Status: `NEW_P1_REPAIR_LOCAL_PASS / FINAL_CI_AND_REVIEW_PENDING`

## Result

The repository now has one stdlib-only local check command and a minimal read-only GitHub Actions workflow that calls the same command. No package installation, cache, secret, artifact upload, provider call or business-network request is required.

The workflow was pushed to PR #3. The first hosted run exposed a cross-version floating-point sum difference between local Python 3.9 and hosted Python 3.12. After the converter switched to decimal-text summation and gained a regression assertion, both runtimes produced byte-identical canonical output and the corrective hosted run passed.

## Added contracts

- `validate_repository_boundaries.py` checks all JSON syntax, compiles all Python in memory, validates real Markdown links, rejects repository media-like files by extension or file signature, rejects symlink escape, checks all text-file whitespace, and scans a declared current machine/runtime artifact scope for private paths, media/subtitle filenames, signed-link-like material, credential-like values and media-fingerprint tokens.
- The scoped public-string scan deliberately excludes the original 30 immutable legacy evidence Markdown ledgers and test/validator attack fixtures. It reports that exclusion explicitly instead of claiming a whole-repository string pass. The legacy operational outputs remain covered by canonical conversion plus the Scene, Grammar and forward-test validators. The newly migrated *Succession* Markdown is directly scanned.
- `run_repository_checks.py` runs every builder and validator independently, writes live validator reports only to a temporary directory, compares all five outputs byte-for-byte with the versioned reports, runs the entire test suite, checks whitespace, then passes the actual result map into the final-report builder.
- `FINAL_GENERALIZATION_VALIDATION.json` can reach `PASS_LOCAL` only with a complete all-PASS live result map. A missing or failed check propagates to `FAIL_LOCAL`. External-action fields are executor declarations marked `NOT_MACHINE_VERIFIED`, not machine evidence.
- `.github/workflows/directormind-contracts.yml` uses read-only repository permission and the same local runner.

## Reproduced local results

- Quick runner: PASS — 16 checks; it intentionally does not validate the full-suite final report.
- Full runner: PASS — 18 checks.
- Unit/CLI suite: PASS — 233 tests after the new legacy-mode and routing-output matrices were added.
- Scene Evidence: 31/31 pass, 2,343 Shot/edit units, 124 candidate lineages, zero errors, 72 warnings.
- Candidate index: 124 candidates, 16 families, all blocked, zero runtime-authorized, zero errors.
- Grammar: five project constraints, six safety constraints, zero eligible/runtime evidence rules, zero errors.
- Routing: eight cases, eight `NO_APPLICABLE_RULE`, zero selected, zero errors.
- Forward tests: eight packages, six required scene problems, zero ready families, zero selected, eight pending, zero errors, 31 warnings.
- Repository boundaries: PASS — the report distinguishes whole-repository file/syntax/link checks from the zero-issue scoped current-artifact string scan and lists 30 excluded immutable legacy ledgers.
- Final report: `final-generalization-validation/0.4` is `PASS_LOCAL` from the full runner's complete live result map; zero validation errors and 103 preserved Scene-plus-forward warnings.

## Post-completion compatibility repair

The current local runner also covers the later narrow repair: one canonical scene-problem vocabulary across seven schemas; canonical routing input plus exact result replay and scene/fact/Shot binding; GO-01/GO-07 trigger checks confined to legacy Grammar v0.1; explicit safe-pause versus evidence-complete v0.2 upgrade modes; refusal to overwrite any existing output; and visible warning/rendering of unmapped legacy audio. The repair changes no corpus counts, source media, private Director IR, external state, or runtime authorization count.

## Boundaries

- Remote CI and pull-request state are post-commit external evidence. The versioned local report deliberately does not self-attest them; verify the final PR head and live PR state after push.
- The original 30 immutable legacy Markdown ledgers are excluded from the direct string scan. An initial independent review found pattern matches inside that historical provenance; they are not classified as a current-artifact zero result, and changing those protected files remains outside this task.
- Source media was not replayed, audio was not directly auditioned, and no positive rule selection can exist while the eligible set is empty.
- Structural checks do not prove creative quality or audience effect.

## Hosted result

- First integrated run: FAIL at canonical conversion determinism; 14 files differed only in the final representation of `stats.total_duration`.
- Corrective evidence: all 31 conversions pass byte-for-byte under Python 3.9 and Python 3.12; 13/13 converter tests and 18/18 repository checks pass locally.
- Corrective hosted run: PASS; the read-only `validate` job completed successfully.
- Follow-up routing/upgrade repair run: PASS; the same read-only `validate` job completed successfully.
- Independent-review documentation run: PASS; the same read-only `validate` job completed successfully.
- PR #1: CLOSED WITHOUT MERGE only after the corrective hosted run passed; the current 88-unit migration stays in PR #3.
- PR #3 remains open with its description updated; `main` remains unmerged for the user's separate decision.

## Independent result

Earlier audit snapshots and their hosted runs remain historical evidence only. A later independent review reproduced two new P1s: v0.2 `LEGACY_COMPATIBLE` accepted unbound executable routing, and the routing CLI overwrote inputs, symlink aliases and arbitrary existing outputs. Both are repaired locally; 55 targeted tests, 233 complete tests and all 18 repository checks pass. `FINAL_INTEGRATION_INDEPENDENT_AUDIT.md` records the superseding FAIL state. Final-head CI and a fresh clean-checkout review remain required.

## External effects and rollback

The authorized PR #3 pushes and PR #1 closure occurred. No merge, deployment, publication, account/permission change, payment, source-media action or deletion occurred. Live PR state is recorded separately because a versioned artifact cannot self-attest the CI run created after its own commit.

After the Phase 6 files are committed in isolation, use a normal revert of that commit to remove the local runner, boundary validator, final-report builder/schema/report, workflow, tests and status updates. Do not rewrite shared history or touch the Phase 5 migration.
