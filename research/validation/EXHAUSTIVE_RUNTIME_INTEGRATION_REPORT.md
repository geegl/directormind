# Exhaustive Runtime Integration Validation Report

Status: `PARTIAL_EVIDENCE_GAP`

The repository contracts pass for the evidence-backed work, but the product
goal is not complete. The fixed corpus contains 33 registered sources, 31
canonical Scene Evidence records, 2,343 Shot/edit units, 124 candidates and 16
mechanism families.

Fresh moving-image review covers 1,840 unique candidate-dependent Shot refs.
Sixty-three candidates now have one of the five allowed final outcomes; the
remaining 61 have genuine external evidence gaps. No candidate remains
waiting for direct review of identified existing material.

## Current decision result

| Outcome | Count |
|---|---:|
| `POSITIVE_RUNTIME_RULE` | 7 |
| `SUPPORTING_EVIDENCE` | 27 |
| `BOUNDARY_OR_COUNTEREXAMPLE` | 23 |
| `MERGED_DUPLICATE` | 3 |
| `REJECTED_WITH_REASON` | 3 |
| `EVIDENCE_GAP_PENDING` | 61 |
| `EXISTING_MATERIAL_REVIEW_REQUIRED` | 0 |

The seven runtime rules span seven source families and create final runtime
effects for 11 of 16 families. Each rule has exact fresh-reviewed Shot lineage,
unrelated-work support, a real reviewed boundary, and a project-original
fallback. Seven positive packages select one target rule each and change at
least one of Coverage, Blocking, Reaction, Pacing or Edit. Seven paired
boundary packages reject their target rules.

The validation runner also injects every distinct signal compiled from all 23
reviewed boundary dispositions into the corresponding positive scene. Each
signal independently produces `NOT_APPLICABLE_MATCH`; the proof therefore does
not depend on one convenient synthetic boundary package.

## Existing-material audio review completed

The complete Sound of Metal selection was directly auditioned and mapped to all
25 canonical Shots through 16 source-neutral observations at approximately
one-second precision. The direct track remains separate from decoded-signal
measurements. It supports only audible surface states such as muffled/clearer
speech, quieter intervals, drums and changing outdoor/indoor ambience.

Those 16 observations collectively cover all 25 auditioned Shots. Candidate
audio claims are structured as an Observation ID plus an exact copy of that
Observation's description. A separate four-row candidate authority now records
the exact permitted Observation set, reason and directly auditioned Shot refs
for each sound-dependent candidate. Each Observation also independently names
the candidates it may support. The validator requires both directions,
candidate IDs and claims to agree exactly and rejects missing, added, swapped,
same-Shot-substituted or coordinately deleted entries even when the attacker
also copies or removes the corresponding claim.

It does not prove speaker identity, sound-source ownership, subjective hearing,
narrative causality, edit intent or the legacy millisecond offsets. The four
audio-dependent candidates therefore move to four separate precise evidence
gaps rather than Runtime Grammar. No audio-dependent runtime rule is authorized.

## Independent semantic-review correction

A family-by-family read-only review found that three promoted rules did not
actually have a same-trigger boundary in the fixed corpus. Comparative-field,
object-custody checkpoint and initial relation-geometry were therefore removed
from Runtime Grammar; their candidates now remain explicit evidence gaps. The
action-chain boundary was replaced with the reviewed continuous-view case, the
aftermath boundary with the reviewed immediate-next-action case, and the
Chernobyl aftermath support was rebound to the actual peak-through-return Shot
range. No rule was kept merely to preserve the earlier count.

A second independent review found that the waypoint rule also lacked a real
same-trigger boundary. It was withdrawn and all 19 related candidates returned
to one precise evidence gap. A later P1 review then reopened the eleven spatial
classification debts against existing video. Eight are now closed: two mobile
attention variants are merged duplicates, three cases support existing runtime
rules, and three cases add the `simultaneous_required_action` negative boundary
to performance-owner routing. Three candidates remain in two new external gaps,
each with the missing evidence type, reason existing material cannot close it,
and exact existing review refs. The Ted Lasso mobile-view fallback remains an
evidence-backed rejection rather than a duplicate.

The first clean-checkout reviewer of this remediation also found that the
Chernobyl S169 note incorrectly called a chest-up speaker anchor a whole-room
field. The note now records the narrower visible fact and explicitly withholds
whole-room geography; the multi-Shot room/process alternation and the
candidate's boundary status remain supported by the other cited Shots.

## Prioritized fixed-corpus gaps

All identified existing-material review is complete. The honest phase is now
`PARTIAL_EVIDENCE_GAP`. The fifteen structured supplementation requests are:

1. A continuous real-time route across at least three necessary zones where
   one field keeps every waypoint and the action chain readable — 19 candidates.
2. Unrelated same-trigger support and a withholding boundary for registering a
   public object-mediated contest or reveal — 1 candidate.
3. A same-trigger distinct-location return where immediate anchor and relation
   restoration is the wrong choice — 2 candidates.
4. Same-trigger support and a no-extra-checkpoint boundary for object custody
   and function changes — 12 candidates.
5. A same-trigger comparison scene where a separate comparative field is the
   wrong coverage choice — 8 candidates.
6. An unrelated proximity scene whose geometry is already readable, making a
   new initial master redundant — 3 candidates.
7. One versioned-object transformation and handoff plus an independent-items
   boundary — 1 candidate.
8. One revised-operation repeat plus an unchanged-repeat boundary — 1
   candidate.
9. One same-trigger multi-thread scene where a continuous field is clearer
   than intercutting — 4 candidates.
10. Same-trigger opposite scale-order evidence separating detail-first from
   geometry-first coverage — 3 candidates.
11. Unrelated subjective-access support plus a same-trigger ordinary-relation
   boundary — 3 candidates.
12. An unrelated directly auditioned information-state change inside a
    necessary held picture plus a same-trigger case requiring a picture change
    — 1 candidate.
13. An unrelated picture/audio boundary alignment plus a same-trigger case
    requiring different timing — 1 candidate.
14. An unrelated picture-first audio-information handoff plus an audio-first or
    simultaneous same-trigger boundary — 1 candidate.
15. An unrelated recurring audio-state/visual-ledger sequence plus a
    same-trigger case where one stable audio state is clearer — 1 candidate.

Exact candidate IDs, required reviews and closure conditions are in
`research/grammar/runtime_integration.review.json` and the deterministic JSON
validation report.

## Evidence correction retained

Renewed multi-frame review disproved the legacy description for
`WIRE-S01E04-OLD-CASES-001-S040`. The canonical converter records only a person
at a window in medium framing and keeps object identity, relation to prior
records, camera motion, cut motivation and narrative meaning unknown. The
immutable legacy ledger remains unchanged.

## Proof boundary

- Structural `PASS` proves deterministic data binding and routing behavior,
  not product completion, creative quality or audience effect.
- Directed tests reject ID-and-description synchronized same-Shot audio
  substitution, candidate swaps, single-sided and coordinated deletions,
  missing and added authorizations, false external-gap labeling and phase-status
  drift. All 314 unit and CLI tests and
  all 25 repository checks pass and rebuild the final report. Hosted CI and the
  independent clean-checkout review still remain pending at this report state.
- The prior full 16-family and Sound reviews remain historical evidence, but
  they do not sign off the current P1 remediation head.
- All creative packages remain `HUMAN_REVIEW_PENDING`.
- No generation, publication, deployment, source-media deletion or main-branch
  merge is authorized or performed.
- Existing-material review closes the eleven classification debts but does not
  close the 61 external evidence-gap candidates or justify `COMPLETE`.

## Rollback

All changes are confined to `codex/exhaustive-runtime-integration`. Before any
merge, rollback is a normal revert or removal of the branch. Source media and
immutable legacy Markdown were not changed.
