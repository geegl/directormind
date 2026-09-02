# Closed Corpus Completion Task

Updated: 2026-09-01

Status: `COMPLETE / INDEPENDENT_READ_ONLY_REVIEW_PASS`

## Task name

Complete the existing 33-source corpus and produce a safe source-retention decision.

## Why this work exists

The local corpus contains 33 video source files, including feature films and television episodes. Thirty current local-source scene analyses exist, but they remain in heterogeneous legacy Markdown, 13 repository-artifact claims are broken, semantic audio has not been directly auditioned, and three local sources do not have a current-branch evidence unit. The user therefore cannot yet tell which originals may be deleted without losing verification evidence.

## Expected result

Every one of the 33 local sources has an explicit disposition. The 30 current local-source analyses have deterministic, schema-valid Scene Evidence JSON. Broken artifact claims are removed or replaced by the canonical JSON. Unauditioned sound stays blocked and appears in a one-time human audio review sheet. The final report separates sources that are deletion-ready, must be retained, or are unusable. No original is deleted until the user separately confirms the exact deletion list.

## In scope

- Convert the 30 current local-source legacy evidence units without adding a reference work.
- Preserve the 2,255 legacy shot/edit units and 120 candidate-rule identities while normalizing their contract and evidence status.
- Resolve the 13 broken artifact claims registered by the legacy audit.
- Keep 29 scenes at `BLOCKED_DIRECT_AUDITION` and Sound of Metal at `SIGNAL_MEASURED_NOT_AUDITIONED` unless direct audition evidence is actually recorded.
- Produce a rights-safe 33-source status ledger, validation report, audio-review sheet, and source-retention recommendation.

## Out of scope

- No new film or episode download, selection, or analysis.
- No candidate-rule promotion, cross-work grammar, runtime routing, forward test, provider work, generated media, or product-page change.
- No update to a remote pull request, merge to `main`, deployment, or publication.
- No claim that structural validation is creative approval or that a single scene proves a general rule.

## Protected content and systems

- Do not commit source video/audio, stills, contact sheets, subtitles, scripts, long dialogue, raw release labels, absolute local media paths, credentials, or personal data.
- Do not touch production data, databases, accounts, permissions, keys, payments, deployment, or unrelated pages.
- Do not delete or modify any original video in this task. Deletion requires a separate user confirmation after the final exact list and recovery boundary are shown.

## Completion criteria

- [x] All 33 local source files have one explicit, evidence-backed disposition.
- [x] All 30 current local-source evidence units have deterministic Scene Evidence JSON.
- [x] The converted corpus contains 2,255 shot/edit units and 120 candidate rules, or every difference is explained and approved.
- [x] Full Scene Evidence validation reports zero failed scenes and preserves all warnings.
- [x] The broken-reference scan reports zero false claims to missing artifacts.
- [x] Unauditioned sound is blocked and a one-time human audio review sheet exists.
- [x] Existing unit tests and important repository behavior remain green.
- [x] The final delivery includes changes, behavioral evidence, checks, remaining risks, and rollback.
- [x] No original media deletion occurs without separate user confirmation.

## Current status

- Current accountable implementer: root agent. Explicitly authorized bounded sub-agents handled non-overlapping conversion, corpus-register, audio-sheet, broken-reference, and read-only review work; root remains the sole integrator and final verifier.
- Completed before this task: closed acquisition at 33 local video files; 30 legacy current-local analyses; legacy migration audit; Scene Evidence schema and validator; commit `54d0450` with 53 passing baseline tests.
- Completed in this task: 30 deterministic JSON units; 2,255 Shot/edit units; 120 non-operational legacy-rule lineage records; explicit migration of 2,058 frame ranges and 311 PTS/time-base ranges; closure of 13 absent-artifact claims; 30-row audio-review sheet; 33-source retention register; structural validation report; completion report.
- Validation result: converter generation and `--check` pass; 66 unit/CLI tests pass; full validator reports 30 passed, 0 failed, 0 errors, and 69 preserved warnings; schema syntax, Python compile, broken-artifact closure regression, source recount, and `git diff --check` pass.
- Not completed by design: direct audio audition, source-media replay, candidate-rule promotion, *Succession* integration, analysis of the extra B99 source, source deletion, push, merge, deploy, or publication.
- Known risk: deleting originals before direct audio review or a verified local-only preservation substitute would remove the only complete route to re-check sound and some picture claims.
- Final independent result: PASS after independently rerunning converter `--check`, 66 tests, full Scene Evidence validation, schema/Python checks, boundary scans, and whitespace checks. No must-fix issue remains.
- Successor state: the isolated local closed-corpus commit exists and remains the preserved baseline. The separately approved generalization task is now active; it does not authorize push, merge, deploy, publication, or media deletion.

## Rollback

All repository work stays on `codex/macos-first16-local-batch`. Before any future commit, the task changes can be reverted by restoring only the files listed in the final change inventory. After a commit, use a normal Git revert of that isolated commit. Do not rewrite shared history. Locally generated review artifacts outside the repository must be kept separate from source media and can be discarded without touching the originals.
