# Exhaustive Runtime Integration Validation Report

Status: `IN_PROGRESS`

The repository contracts pass for the evidence-backed work, but the product
goal is not complete. The fixed corpus contains 33 registered sources, 31
canonical Scene Evidence records, 2,343 Shot/edit units, 124 candidates and 16
mechanism families.

Fresh moving-image review covers 1,840 unique candidate-dependent Shot refs.
Eighty-five candidates now have one of the five allowed final outcomes; 35
have genuine fixed-corpus evidence gaps, and four candidates still require
direct audition of existing local material.

## Current decision result

| Outcome | Count |
|---|---:|
| `POSITIVE_RUNTIME_RULE` | 8 |
| `SUPPORTING_EVIDENCE` | 30 |
| `BOUNDARY_OR_COUNTEREXAMPLE` | 43 |
| `MERGED_DUPLICATE` | 2 |
| `REJECTED_WITH_REASON` | 2 |
| `EVIDENCE_GAP_PENDING` | 35 |
| `EXISTING_MATERIAL_REVIEW_REQUIRED` | 4 |

The eight runtime rules span eight source families and create final runtime
effects for 12 of 16 families. Each rule has exact fresh-reviewed Shot lineage,
unrelated-work support, a real reviewed boundary, and a project-original
fallback. Eight positive packages select one target rule each and change at
least one of Coverage, Blocking, Reaction, Pacing or Edit. Eight paired
boundary packages reject their target rules.

The validation runner also injects every distinct signal compiled from all 43
reviewed boundary dispositions into the corresponding positive scene. Each
signal independently produces `NOT_APPLICABLE_MATCH`; the proof therefore does
not depend on one convenient synthetic boundary package.

## Existing-material review still required

Four Sound of Metal candidates cite exact canonical Shot intervals and have
completed picture review, but their claims concern audible state, signal
ownership, causality or timing. Signal measurements and speech recognition can
locate intervals; neither constitutes direct audition. These rows are
`EXISTING_MATERIAL_REVIEW_REQUIRED`, not evidence gaps and not final outcomes.

This is the current reason for `IN_PROGRESS`. No audio-dependent runtime rule
has been authorized.

## Independent semantic-review correction

A family-by-family read-only review found that three promoted rules did not
actually have a same-trigger boundary in the fixed corpus. Comparative-field,
object-custody checkpoint and initial relation-geometry were therefore removed
from Runtime Grammar; their candidates now remain explicit evidence gaps. The
action-chain boundary was replaced with the reviewed continuous-view case, the
aftermath boundary with the reviewed immediate-next-action case, and the
Chernobyl aftermath support was rebound to the actual peak-through-return Shot
range. No rule was kept merely to preserve the earlier count.

## Prioritized fixed-corpus gaps

If the four existing-audio reviews are completed without resolving the
remaining 35 candidates, the honest next phase is `PARTIAL_EVIDENCE_GAP`. The
eight precise supplementation requests are:

1. Same-trigger support and a no-extra-checkpoint boundary for object custody
   and function changes — 12 candidates.
2. A same-trigger comparison scene where a separate comparative field is the
   wrong coverage choice — 8 candidates.
3. An unrelated proximity scene whose geometry is already readable, making a
   new initial master redundant — 3 candidates.
4. One versioned-object transformation and handoff plus an independent-items
   boundary — 1 candidate.
5. One revised-operation repeat plus an unchanged-repeat boundary — 1
   candidate.
6. One same-trigger multi-thread scene where a continuous field is clearer
   than intercutting — 4 candidates.
7. Same-trigger opposite scale-order evidence separating detail-first from
   geometry-first coverage — 3 candidates.
8. Unrelated subjective-access support plus a same-trigger ordinary-relation
   boundary — 3 candidates.

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
- The post-audit corrected tree passes 294 unit and CLI tests and all 25
  repository checks, including deterministic final-report regeneration.
- Final-head CI and a fresh clean-checkout review still require external
  evidence after the correction commit is pushed.
- All creative packages remain `HUMAN_REVIEW_PENDING`.
- No generation, publication, deployment, source-media deletion or main-branch
  merge is authorized or performed.
- Final-head CI and a clean-checkout family-by-family independent audit remain
  required after the last implementation commit.

## Rollback

All changes are confined to `codex/exhaustive-runtime-integration`. Before any
merge, rollback is a normal revert or removal of the branch. Source media and
immutable legacy Markdown were not changed.
