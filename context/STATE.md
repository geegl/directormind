# Current State

Updated: 2026-09-04

## Current phase

Exhaustive Runtime Integration is `PARTIAL_EVIDENCE_GAP` on
`codex/exhaustive-runtime-integration`. The fixed corpus is fully inventoried,
but the task is not complete: 17 of 124 candidates have evidence-backed final
dispositions and 107 still require the exact reviews listed in the canonical
gap register. Four runtime rules are active across four mechanism families.

Root is the only repository writer. Read-only reviewers replayed selected local
video intervals and did not sign the final audit. No source media was added,
deleted, moved, or committed. `main` remains unchanged. All 283 tests and 25
local repository checks pass. A new PR, hosted CI, and the final clean-checkout
independent audit are still pending.

## Current counts

| Item | Current value |
|---|---:|
| Local source dispositions | 33 |
| Canonical Scene Evidence JSON | 31 |
| Shot/edit units | 2,343 |
| Candidate identities | 124 |
| Mechanism families | 16 |
| Evidence records reviewed | 31 |
| Moving-image reviewed Shot refs | 53 |
| Final candidate dispositions | 17 |
| Candidates pending evidence | 107 |
| Precise evidence gaps | 17 |
| Evidence units with a final decision mapping | 12 |
| Runtime-active families | 4 |
| Runtime-authorized rules | 4 |
| Positive forward packages | 4 |
| Boundary forward packages | 4 |
| Total forward packages | 17 |
| Directly auditioned semantic-audio scenes | 0 |

Final dispositions currently comprise four positive rules, seven supporting
candidates, five boundary/counterexample candidates, one merged duplicate and
zero evidence-backed rejections. `EVIDENCE_GAP_PENDING` is an interim state,
not one of the five required final outcomes.

## Active runtime rules

| Rule | Family | Director decision changed |
|---|---|---|
| `DR-PERFORMANCE-OWNER-HOLD` | Screen ownership and performance hold | Coverage, blocking, reaction timing and edit |
| `DR-RELATION-RESET-AFTER-SPATIAL-CHANGE` | Spatial registration and reset | Coverage, blocking and edit |
| `DR-SHARED-FRAME-FOR-RELATION-ENDPOINT` | Proximity and relation geometry | Coverage, blocking, pacing and edit |
| `DR-COMPARATIVE-FIELD-BEFORE-RELATION` | Object state and custody | Coverage, blocking and edit |

Each active rule has exact moving-image-reviewed Shot lineage, unrelated-work
support, a real reviewed boundary, a project-original fallback, and original
positive plus boundary routing packages. All creative outputs remain
`HUMAN_REVIEW_PENDING`; none authorizes generation or publication.

## Important evidence correction

Renewed multi-frame review disproved the legacy description of
`WIRE-S01E04-OLD-CASES-001-S040`. The canonical converter now records a person
at the window in medium framing and leaves the object's identity, relation to
earlier records, camera motion, cut motivation and narrative meaning unknown.
That Shot is not part of the comparison rule's runtime lineage. The immutable
legacy Markdown remains unchanged.

## Authoritative sources

| Authority | Path | Current status |
|---|---|---|
| Live phase summary | `context/STATE.md` | ACTIVE — single current status entrypoint |
| Exhaustive dispositions and precise gaps | `research/grammar/runtime_integration.review.json` | ACTIVE — canonical authority |
| Per-scene facts | `research/evidence/**/*.scene-evidence.json` | ACTIVE — 31 records |
| Candidate lineage and grouping | `research/grammar/candidate_rule_index.json` | GENERATED — 124 candidates, 16 families |
| Cross-work support and boundaries | `research/grammar/cross_work_support_matrix.json` | GENERATED |
| Runtime directing rules | `research/grammar/director_grammar_v0.2.json` | GENERATED — 4 rules |
| Original routing packages | `examples/forward-tests/index.json` | GENERATED — 17 packages |
| Machine validation summary | `research/validation/exhaustive-runtime-integration-validation.json` | PASS / PARTIAL_EVIDENCE_GAP |
| Human-readable phase report | `research/validation/EXHAUSTIVE_RUNTIME_INTEGRATION_REPORT.md` | ACTIVE |

Generated `*.scene-evidence.generated.md` files are review views, not separate
fact sources. The 30 legacy evidence Markdown ledgers remain immutable
provenance. Material catalogs do not authorize rules.

## Remaining boundary

The existing corpus has not yet supplied enough reviewed evidence to assign
the remaining 107 candidates one of the five final outcomes or to give all 16
families a final runtime role. The 17 prioritized gaps name the exact intervals
and closure conditions needed. Sound-dependent candidates remain open until
the existing audio is directly auditioned.

## Next single action

Commit and recheck the complete branch diff, then push the new branch, open a
new PR, wait for its final-head CI, and obtain a clean-checkout read-only audit
across all 16 families. Do not merge `main`.
