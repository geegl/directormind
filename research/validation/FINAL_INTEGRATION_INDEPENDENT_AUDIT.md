# DirectorMind Final Integration — Independent Read-Only Audit

Date: 2026-09-02

Status: `PASS_LOCAL / NO_MUST_FIX_FINDINGS / CLEAN_CHECKOUT_REVIEW_PASS`

## New review that supersedes the prior verdict

A later independent review reproduced two additional P1s on the previously
accepted branch:

| New finding | Baseline evidence | Current local repair |
|---|---|---|
| `LEGACY_COMPATIBLE` accepted a v0.2 IR carrying a schema-valid but unbound route. | Cross-scene `routing_result` substitution returned successfully; the public CLI exited zero and created mismatched executable output. | `LEGACY_COMPATIBLE` now accepts v0.1 input only. Every v0.2 source must use `GRAMMAR_V02_ROUTED` with a validated Grammar and exact `route_scene` replay. Result-only, input-plus-result and same-case forged-selection attacks are rejected; failure creates no output. |
| The routing CLI overwrote its scene input, Grammar input, symlink aliases and unrelated existing output. | Each overwrite case exited zero and changed the protected file. | Non-check writes reject resolved input aliases and every existing output, then use exclusive file creation. Four input/alias attacks and unrelated-output overwrite return non-zero without changing content; new output succeeds and `--check` remains read-only. |

## Final clean-checkout verdict

`NO_MUST_FIX_FINDINGS`

A fresh non-writing reviewer audited a clean detached checkout matching PR #3's
current implementation head. The reviewer independently confirmed:

- result-only, input-plus-result and same-case forged-selection attacks all fail
  through both the direct upgrade boundary and public CLI;
- every failed legacy-compatible CLI case returns non-zero, creates no output
  and leaves both inputs unchanged;
- the same Schema-valid forgeries also fail if presented to routed mode because
  Grammar replay or scene binding rejects them;
- valid `GRAMMAR_V02_ROUTED` direct and CLI paths succeed and the resulting IR
  validates;
- output equal to scene, equal to Grammar, both symlink aliases and unrelated
  existing output all fail without changing any protected content;
- new output succeeds, correct `--check` succeeds, and missing-output `--check`
  fails without creating a file.

The reviewer reran 55/55 targeted tests, 233/233 complete tests, all 18
repository checks and the complete committed PR whitespace check. The checkout
ended with zero changes. The hosted final implementation-head `validate` job
passed at <https://github.com/geegl/directormind/actions/runs/33641817707>.
PR #3 remained open and unmerged; `main` was not changed. No P2 was found.

## Prior review boundary

A non-writing reviewer independently inspected the committed follow-up repair on
the PR #3 branch. The reviewer did not edit repository files, commit, push,
access source media or private Director IR, merge, deploy, publish, delete, or
change any account, permission, key or payment setting. Attack files were
created only in automatically removed temporary directories.

This review does not inherit the verdict of an older audit. It replays the two
P1 findings that overturned the previous completion claim and checks the valid
paths after repair.

## Prior reviewed snapshot: must fix before completion

`NO_MUST_FIX_FINDINGS`

This verdict applies only to the earlier reviewed snapshot and is superseded by
the new findings above.

| Replayed case | Result | Evidence |
|---|---|---|
| Substitute only another scene's complete `routing_result` | Rejected | Director IR returns `FAIL` with `IR-ROUTING-REPLAY-DRIFT`. |
| Substitute another scene's `routing_input` and `routing_result` together | Rejected | Director IR returns `FAIL` on dramatic, goal and locked-fact/Shot binding. |
| Change only the embedded dramatic goal | Rejected | The scene and canonical routing input no longer bind. |
| Change one locked fact | Rejected | Director IR returns `FAIL` with `IR-ROUTING-FACT-BINDING`. |
| Upgrade to an unrelated existing output path | Rejected safely | CLI exits non-zero and the pre-existing content is byte-for-byte unchanged. |
| Validate a legitimate Grammar v0.2 IR | Passed | Fresh routing replay and Director IR validation return `PASS`. |
| Upgrade a legitimate v0.1 IR to a new output path | Passed | CLI exits zero and the generated IR validates as `PASS`. |

## Prior snapshot reproduced evidence

- Targeted Director routing and compatibility suite: 47/47 PASS.
- Complete unit/CLI suite: 225/225 PASS.
- Complete repository runner: 18/18 PASS.
- Complete committed PR whitespace check: PASS.
- Final local report: 33 dispositions, 31 Scene Evidence JSON files, 2,343
  Shot/edit units, 124 candidates, 16 families, zero runtime rules, zero
  validation errors and 103 preserved warnings.
- Repair-head hosted `validate` job: PASS at
  <https://github.com/geegl/directormind/actions/runs/33635006251>.
- PR #3 is open; PR #1 remains closed without merge; `main` is not merged.
- The repair adds no reference work, media, prompt package or private-script
  change. The eight changed Director IR files are existing project-original test
  fixtures.

## Can improve later

- No current P2 was found. Versioned status documents cannot self-attest the CI
  run triggered by their own metadata commit, so that final run is verified
  live after push.

Post-review external evidence: the independent-review documentation head later
passed the read-only hosted workflow at
<https://github.com/geegl/directormind/actions/runs/33636232262>.

## Unverified boundaries

- Source media, private scripts and private Director IR were not opened or
  replayed; semantic audio was not directly auditioned.
- The live Grammar still has zero runtime evidence rules, so there is no real
  positive rule-selection evidence.
- Structural and contract success is not creative approval, audience evidence
  or human director acceptance.

## Rollback

Use normal revert commits on the PR #3 branch. Do not rewrite shared history.
The routing-input fixtures, validator/upgrader repair and documentation update
can be reverted without touching source media, legacy evidence Markdown,
private scripts, production data or `main`.
