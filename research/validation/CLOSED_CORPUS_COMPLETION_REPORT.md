# Closed Corpus Completion Report

Updated: 2026-09-01

Status: `COMPLETE / INDEPENDENT_READ_ONLY_REVIEW_PASS`

## Result

The closed local corpus remains `33` video files and approximately `52G`; no source media was added, modified, moved, or deleted. Thirty current-local legacy analyses now have deterministic adjacent Scene Evidence JSON containing `2,255` Shot/edit units and `120` candidate-rule lineage records. The remaining three sources have explicit non-conversion dispositions in `CLOSED_CORPUS_33_STATUS.md`.

The conversion is deliberately conservative. Legacy candidate-rule rows are preserved field-for-field only as non-operational lineage. Their operational rule fields are blocked pending human review, all scene-problem classifications are `UNKNOWN`, unauditioned sound remains blocked, and structural validation is not represented as creative approval.

## Change inventory

- Added the deterministic legacy converter and its regression tests.
- Extended the Scene Evidence schema with a non-operational `legacy_migration` record for candidate-rule lineage.
- Added a narrow validator guard and paired regression tests: non-operational legacy lineage must carry no operational `required_story_facts`, while ordinary candidate rules must still cite at least one supported story fact.
- Added 30 generated `*.scene-evidence.json` files beside their legacy Markdown sources.
- Replaced 13 false claims to absent TSV/ledger artifacts in seven evidence documents with explicit `ABSENT_LEGACY_ARTIFACT` records and canonical JSON/report pointers.
- Added the 33-source status register and one-time 30-scene human audio-review sheet.
- Added the full structural validation report with warnings preserved.
- Added the approved task card and updated current project status/checklist pointers.

## Behavioral evidence

- Corpus identity: `30` legacy Markdown sources map to exactly `30` same-stem JSON outputs; no new reference work is added.
- Shot/rule preservation: `2,255` Shot/edit units and `120` legacy candidate IDs are retained.
- Rule safety: `120/120` legacy rows are preserved under `legacy_migration`; operational fields are identical blocked-review placeholders with empty operational story prerequisites; provisional families are the work-neutral unique range `UNCLUSTERED-CANDIDATE-001..120`. The schema and custom validator retain the original non-empty story-fact requirement for ordinary operational candidate rules.
- Timing preservation: all displayed source start/end timecodes are preserved; `2,058/2,255` rows carry explicit frame endpoints and `311/2,255` carry explicit PTS plus time base. Missing values stay `null` instead of being guessed.
- Text preservation: ordinary slash phrases remain intact; real absolute local paths are scrubbed. The rebuilt JSON corpus contains `0` accidental `[local path omitted]` substitutions.
- Fallback preservation: `1,579` Shot/edit rows with an explicit legacy `FALLBACK:` preserve it on every mapped high-risk axis. `513` high-risk rows without an explicit legacy fallback use a provisional shot-addressed project-original fallback tied to that row's cited state/action/axis claims plus a visible warning; no missing source-specific solution is invented.
- Evidence boundary: all `30` scene problems remain `UNKNOWN`; `29` audio statuses are `BLOCKED_DIRECT_AUDITION` and *Sound of Metal* remains `SIGNAL_MEASURED_NOT_AUDITIONED`.
- Broken references: the known `13` claims are now explicit absence records across the same seven files; no stale “JSON does not exist yet” wording remains.

## Checks

| Check | Result |
|---|---|
| Deterministic conversion | PASS — 30 scenes, 2,255 Shot/edit units, 120 candidate rules |
| Deterministic `--check` | PASS — generated files match converter output |
| Skill unit/CLI tests | PASS — 66 tests |
| Full Scene Evidence validation | PASS_STRUCTURAL — 30 passed, 0 failed, 0 errors, 69 warnings preserved |
| Schema JSON syntax and Python compile | PASS |
| Known absent-artifact closure regression | PASS — 13 records across seven files, zero stale existence claims |
| Working-tree whitespace check | PASS |
| Local source presence recount | PASS — 33 video files, approximately 52G |
| Original media deletion | NONE |
| Push, merge, deploy, publish, production/account/permission/key/payment change | NONE |

## Independent read-only review

A fresh final reviewer independently reran the deterministic converter check, all 66 unit/CLI tests, full Scene Evidence validation, schema/Python parse checks, corpus and media-boundary scans, and `git diff --check`. Final verdict: `PASS`, with no remaining must-fix issue. The review did not replay source media or directly audition audio, and therefore does not expand the validation boundary described below.

## 33-source retention result

- `32 RETAIN`: 30 current-local evidence sources pending direct audio or an accepted preservation substitute, one PR-only *Succession* source, and one extra *Brooklyn Nine-Nine* source without a complete evidence unit.
- `1 DELETE_CANDIDATE_PENDING_USER_CONFIRMATION`: the *Better Call Saul* S01E09-labelled source that does not contain the requested target scene. It is also `TARGET_SCENE_UNUSABLE`.
- `0 DELETED`: this work does not authorize or perform deletion.

The 30 selected analytical envelopes total approximately `3.495` hours, but those ranges are not yet a verified local-only re-audit bundle. If space recovery is prioritized later, the safe next phase is to create and open-check a private selected-scene preservation bundle, complete or explicitly waive direct audio review, and then ask the user to approve an exact deletion list.

## Remaining risks and unverified items

- Source media was not replayed to independently re-prove all 2,255 picture observations or edit points.
- No semantic audio was directly auditioned; the audio sheet is a review plan, not completed audio evidence.
- `197` rows have no explicit legacy frame endpoint and `1,944` have no explicit PTS/time base; nulls are intentional.
- `513` high-risk rows had no source-specific legacy fallback. Their provisional fallback remains visible and must not be mistaken for a reviewed directing solution.
- The 120 legacy candidate records are not cross-work rules, runtime defaults, creative approval, or evidence of audience performance.
- *Succession* evidence is still outside the current branch; the extra B99 source remains unanalyzed; the rejected BCS source is not deletion-authorized.

## Rollback

All repository changes remain isolated on `codex/macos-first16-local-batch`. Before a local commit, restore only the files in this report's change inventory. After the isolated local commit, use a normal Git revert of that commit; do not rewrite shared history. No media rollback is required because no source media was changed. The generated 30 JSON files can be recreated deterministically from the retained Markdown using the converter.
