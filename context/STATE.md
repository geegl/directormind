# Current State

Updated: 2026-09-03

## Current phase

Runtime Rule Promotion Wave 1 is in P1 repair verification on
`codex/runtime-rule-promotion-wave1`, based on the current `origin/main` and
published as PR #4.
The locally verified implementation now produces three real `CROSS_WORK_SUPPORTED`
runtime rules from nine newly replayed evidence units and three mechanism
families. This meets the numerical product threshold for `COMPLETE`, but the
first independent clean-checkout review replayed all nine units and found two
P1s: an OTS mislabeled as clean-single support, and contradictory/unbound
original routing facts. Both are repaired locally. Final status remains pending
until the repair commit's complete diff, hosted CI and independent re-review all
pass. The repaired local contract is green at 244 tests and 21 repository checks.

Only the root agent writes shared files. The independent reviewer remained
read-only and issued the initial P1 findings. No source media was added,
deleted, moved, or committed. `main` remains unchanged and must not be merged by
this task.

## Current counts

| Item | Current value |
|---|---:|
| Local source dispositions | 33 |
| Canonical current-local Scene Evidence JSON | 31 |
| Shot/edit units | 2,343 |
| Candidate identities | 124 |
| Mechanism families | 16 |
| Freshly replayed evidence units | 9 |
| `CROSS_WORK_SUPPORTED` candidates | 3 |
| Runtime-authorized rules | 3 |
| Runtime-rule families | 3 |
| Candidates still blocked | 121 |
| Forward-test packages | 12 |
| Positive `SELECTED` packages | 3 |
| Boundary/non-applicable packages | 3 |
| `NO_APPLICABLE_RULE` packages | 9 |
| Directly auditioned semantic-audio scenes | 0 |

The three runtime rules address performance ownership, spatial relation reset,
and proximity endpoint coverage. They are visual-only (`audio_dependency=false`),
forbid surface copying, use project-original fallbacks, and remain
`HUMAN_REVIEW_PENDING` in every creative package.

## Authoritative sources

| Authority | Path | Current status |
|---|---|---|
| Per-scene facts | `research/evidence/**/*.scene-evidence.json` | ACTIVE — 31 canonical JSON units |
| Wave 1 video-review and promotion decisions | `research/grammar/runtime_rule_promotion_wave1.review.json` | ACTIVE — 9 reviews, 3 promotions |
| Candidate-rule lineage and grouping | `research/grammar/candidate_rule_index.json` | ACTIVE — 124 candidates, 16 families |
| Cross-work support and contrary evidence | `research/grammar/cross_work_support_matrix.json` | ACTIVE — 3 supported families with real boundaries |
| Runtime directing rules | `research/grammar/director_grammar_v0.2.json` | ACTIVE — 3 runtime rules |
| Original positive and boundary tests | `examples/forward-tests/index.json` | ACTIVE — 12 packages |
| Phase checklist and evidence | `context/RUNTIME_RULE_PROMOTION_WAVE1_CHECKLIST.md` | ACTIVE |
| Phase, counts, blockers and next step | `context/STATE.md` | ACTIVE |

Generated `*.scene-evidence.generated.md` files are review views, not separate
fact sources. The 30 legacy evidence Markdown ledgers remain immutable
provenance. Material catalogs do not authorize rules.

## Verified boundaries

- Fresh review used the local source videos and exact canonical Shot intervals.
  Temporary review frames remain outside the repository.
- Three short visible-text anchors are stored only as paraphrases. No subtitle
  file, dialogue transcript, still, contact sheet, or local media path is
  committed.
- Semantic audio was not directly auditioned and cannot support any promoted
  rule.
- Scene-problem labels and functional roles are `INFERRED`, with exact picture
  and text sources; unproved motive, identity, contact, lens and audio facts
  remain `UNKNOWN`.
- Structural selection proves routing behavior, not creative quality, audience
  effect, generation approval, or publication approval.
- B99 S016 is recorded as an owner-dominant OTS with a foreground counterpart,
  not clean-single support. The performance rule instead uses the verified
  Mr. Robot source plus Better Call Saul cross-work support.
- Boundary routing signals now exclude mutually contradictory positive and
  non-applicable claims. Romantic proximity classification and continuous-time
  or elliptical signals resolve to explicit project-original locked facts.

## Next single action

Commit the two P1 repairs, rerun the complete committed-diff check, push to PR
#4, wait for hosted CI on that repaired head, and obtain a fresh clean-checkout
re-review verdict. Stop without merging `main`.
