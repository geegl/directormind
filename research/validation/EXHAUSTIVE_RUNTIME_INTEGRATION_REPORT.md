# Exhaustive Runtime Integration Validation Report

Status: `PARTIAL_EVIDENCE_GAP`

The repository contracts pass for the work that is actually evidenced, but
the product goal is not complete. The fixed corpus contains 33 registered
sources, 31 canonical Scene Evidence records, 2,343 Shot/edit units, 124
candidates and 16 mechanism families. Seventeen candidates now have one of the
five allowed final dispositions; 107 remain in evidence gaps and therefore
cannot be counted as final.

## Current decision result

| Outcome | Count |
|---|---:|
| `POSITIVE_RUNTIME_RULE` | 4 |
| `SUPPORTING_EVIDENCE` | 7 |
| `BOUNDARY_OR_COUNTEREXAMPLE` | 5 |
| `MERGED_DUPLICATE` | 1 |
| `REJECTED_WITH_REASON` | 0 |
| `EVIDENCE_GAP_PENDING` | 107 |

The four positive rules affect screen ownership, spatial reset, relation
endpoint coverage and comparative-field coverage. They use 53 moving-image
reviewed Shot refs across their source, support, boundary and merge lineage.
Each has one project-original positive package and one boundary package. The
boundary is effective only when the locked negative signal is present; removing
that signal causes the target rule to become selectable.

## Evidence correction found during review

The legacy description for `WIRE-S01E04-OLD-CASES-001-S040` was disproved by
multi-frame playback. The canonical converter now describes a person at a
window in medium framing and keeps object identity, relation to prior records,
camera motion, cut motivation and narrative meaning unknown. The comparison
rule uses S007 and S038 only. The legacy ledger remains unchanged.

## Prioritized supplementation

The machine-readable authority contains 17 exact gaps and closure conditions.
The highest priorities are:

1. Directly audition the existing Sound of Metal intervals for four
   sound-dependent candidates.
2. Replay one complete source-to-change-to-result action chain per affected
   work; scattered action fragments cannot prove causality.
3. Replay all threshold candidates and distinguish state-changing thresholds
   from ordinary travel continuity; the previously proposed threshold rule was
   withdrawn because its source and boundary did not satisfy this test.
4. Replay object-state candidates and separate active coverage/edit choices
   from passive prop continuity.
5. Replay spatial-reset and receiver/reaction candidates with complete
   pre-change, change and post-change intervals; add direct audio or a short
   text anchor only when the trigger is not visible.

The remaining lower-priority gaps cover continuous movement/occlusion,
aftermath, continuity versioning, procedure, proximity, multi-thread intercut,
scale/reveal, screen ownership, state-change editing, axis grammar and
subjective access. Their candidate IDs, precise review instructions and close
conditions are in `research/grammar/runtime_integration.review.json` and are
rendered in `exhaustive-runtime-integration-validation.json`.

## Proof boundary

- Local validation proves deterministic data binding and routing behavior, not
  creative quality or audience effect.
- All creative packages remain `HUMAN_REVIEW_PENDING`.
- No generation, publication, deployment, source-media deletion or main-branch
  merge is authorized or performed.
- A new PR, hosted CI and a clean-checkout family-by-family independent audit
  remain required before this branch can be handed off.

## Rollback

All changes are confined to `codex/exhaustive-runtime-integration`. Before any
merge, rollback is removal of the branch or a normal revert of its commits.
Source media and immutable legacy Markdown were not changed.
