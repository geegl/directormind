# Exhaustive Runtime Integration Validation Report

Status: `PARTIAL_EVIDENCE_GAP`

The repository contracts pass for the evidence-backed work, but the product
goal is not complete. The fixed corpus contains 33 registered sources, 31
canonical Scene Evidence records, 2,343 Shot/edit units, 124 candidates and 16
mechanism families.

Fresh moving-image review covers 1,840 unique candidate-dependent Shot refs.
Fifty-five candidates now have one of the five allowed final outcomes; the
remaining 69 have genuine fixed-corpus evidence gaps. No candidate remains
waiting for direct review of identified existing material.

## Current decision result

| Outcome | Count |
|---|---:|
| `POSITIVE_RUNTIME_RULE` | 7 |
| `SUPPORTING_EVIDENCE` | 24 |
| `BOUNDARY_OR_COUNTEREXAMPLE` | 20 |
| `MERGED_DUPLICATE` | 1 |
| `REJECTED_WITH_REASON` | 3 |
| `EVIDENCE_GAP_PENDING` | 69 |
| `EXISTING_MATERIAL_REVIEW_REQUIRED` | 0 |

The seven runtime rules span seven source families and create final runtime
effects for 11 of 16 families. Each rule has exact fresh-reviewed Shot lineage,
unrelated-work support, a real reviewed boundary, and a project-original
fallback. Seven positive packages select one target rule each and change at
least one of Coverage, Blocking, Reaction, Pacing or Edit. Seven paired
boundary packages reject their target rules.

The validation runner also injects every distinct signal compiled from all 20
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
Observation's description. The validator rejects incomplete scene coverage,
missing or foreign observations, changed descriptions, and substitution of an
unrelated observation from the same Shot. This closes the independent precommit
attacks in which one unrelated observation, or deletion of the specific
00:10:13 observation, previously passed.

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
to one precise evidence gap. The spatial family was narrowed from a bulk
classification to one actual support (`TSN-2010-C01`, Shots S088-S090), one
actual boundary (`TSN-2010-C04`, Shots S090-S091), and eleven evidence gaps.
The Ted Lasso mobile-view fallback was reclassified as an evidence-backed
rejection instead of a duplicate of the authorized mobile-attention rule.

## Prioritized fixed-corpus gaps

All identified existing-material review is complete. The honest phase is now
`PARTIAL_EVIDENCE_GAP`. The fourteen precise supplementation requests are:

1. A continuous real-time route across at least three necessary zones where
   one field keeps every waypoint and the action chain readable — 19 candidates.
2. Exact reclassification evidence for mixed ensemble, recurring-zone and
   parallel-return spatial candidates — 11 candidates.
3. Same-trigger support and a no-extra-checkpoint boundary for object custody
   and function changes — 12 candidates.
4. A same-trigger comparison scene where a separate comparative field is the
   wrong coverage choice — 8 candidates.
5. An unrelated proximity scene whose geometry is already readable, making a
   new initial master redundant — 3 candidates.
6. One versioned-object transformation and handoff plus an independent-items
   boundary — 1 candidate.
7. One revised-operation repeat plus an unchanged-repeat boundary — 1
   candidate.
8. One same-trigger multi-thread scene where a continuous field is clearer
   than intercutting — 4 candidates.
9. Same-trigger opposite scale-order evidence separating detail-first from
   geometry-first coverage — 3 candidates.
10. Unrelated subjective-access support plus a same-trigger ordinary-relation
   boundary — 3 candidates.
11. An unrelated directly auditioned information-state change inside a
    necessary held picture plus a same-trigger case requiring a picture change
    — 1 candidate.
12. An unrelated picture/audio boundary alignment plus a same-trigger case
    requiring different timing — 1 candidate.
13. An unrelated picture-first audio-information handoff plus an audio-first or
    simultaneous same-trigger boundary — 1 candidate.
14. An unrelated recurring audio-state/visual-ledger sequence plus a
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
- The independent missing, truncated and same-Shot substitution audio attacks
  are rejected; 306/306 unit and CLI tests, all 25 repository checks and the
  working-tree whitespace check pass.
- Final-head GitHub CI and a new clean-checkout review remain required before
  this head can receive the final independent PASS.
- The previous PR head passed CI and an independent 16-family review; those
  results are retained as historical evidence but do not sign the new head.
- All creative packages remain `HUMAN_REVIEW_PENDING`.
- No generation, publication, deployment, source-media deletion or main-branch
  merge is authorized or performed.
- Direct audition closes the existing-material review debt but does not close
  the 69 fixed-corpus evidence gaps or justify `COMPLETE`.

## Rollback

All changes are confined to `codex/exhaustive-runtime-integration`. Before any
merge, rollback is a normal revert or removal of the branch. Source media and
immutable legacy Markdown were not changed.
