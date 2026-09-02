# Final Remote Delivery Evidence

Updated: 2026-09-02

Status: `NEW_P1_REPAIR_LOCAL_ONLY / FINAL_CI_AND_REVIEW_PENDING / PR_OPEN`

## Scope

This record covers only the authorized PR #3 pushes, hosted CI and PR #1 closure. It does not authorize or claim a merge to `main`, deployment, publication, media deletion or any production/account/permission/payment action.

## Evidence

- PR #3 remains open: <https://github.com/geegl/directormind/pull/3>.
- The first integrated hosted run failed at canonical conversion determinism: <https://github.com/geegl/directormind/actions/runs/33631027540>.
- The failure was reproduced as a Python 3.9 versus 3.12 float-summation representation difference affecting `stats.total_duration` in 14 generated JSON files.
- The converter now sums decimal spellings. All 31 files pass byte-for-byte under both local Python 3.9 and bundled Python 3.12; 13/13 converter tests and all 18 repository checks pass locally.
- The corrective hosted run passed: <https://github.com/geegl/directormind/actions/runs/33631468728>.
- PR #1 was then closed without merge: <https://github.com/geegl/directormind/pull/1>. Its 88-unit *Succession* evidence remains migrated through the current contracts in PR #3.
- A later final review found two P1s in routing provenance and upgrade-output protection. The follow-up repair embeds and replays canonical routing input, binds scene facts, and refuses every existing output path.
- The repair-head hosted run passed: <https://github.com/geegl/directormind/actions/runs/33635006251>.
- A fresh non-writing reviewer independently replayed both attacks and the valid paths, then issued `PASS_LOCAL / NO_MUST_FIX_FINDINGS`; see `FINAL_INTEGRATION_INDEPENDENT_AUDIT.md`.
- The independent-review documentation head passed: <https://github.com/geegl/directormind/actions/runs/33636232262>.
- PR #3's description now records the final P1 corrections, 225-test and 18-check results, independent verdict, remaining boundaries and rollback.
- A later independent review reproduced two new P1s: v0.2 route carry-through in `LEGACY_COMPATIBLE`, and destructive routing-CLI output handling. The prior merge-ready conclusion is withdrawn.
- Both new P1s are fixed locally with 55 targeted tests, 233 complete tests and 18 repository checks passing. This working tree has not yet been pushed, checked by hosted CI or reviewed from a clean checkout.

## Remaining gate

Commit and push the new repair, update PR #3, require final-head hosted CI, and obtain a new clean-checkout independent verdict with no must-fix finding. PR #3 remains open and `main` remains unmerged.

## Rollback

Use normal Git revert commits on PR #3; do not rewrite shared history. PR #1 can be reopened independently if the user later decides the closure itself must be reversed, but its old branch must not be merged unchanged.
