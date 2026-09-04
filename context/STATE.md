# Current State

Updated: 2026-09-04

## Current phase

Exhaustive Runtime Integration is `IN_PROGRESS` on
`codex/exhaustive-runtime-integration` and PR #5. The fixed corpus remains 33
registered sources, 31 canonical Scene Evidence records, 2,343 Shot/edit
units, 124 candidates and 16 mechanism families.

Fresh moving-image review now covers all 1,840 unique candidate-dependent Shot
refs. Of the 124 candidates, 108 have evidence-backed final outcomes, 12 have
genuine fixed-corpus evidence gaps, and four Sound of Metal candidates still
require direct human audition of exact intervals already present locally.
Because review of existing material is unfinished, the product phase is not
`PARTIAL_EVIDENCE_GAP` yet and must not be called complete.

Root is the only repository writer. Read-only agents reviewed local picture
material and the sound-evidence boundary but did not sign a final audit. No
source media was added, deleted, moved, or committed. `main` remains unchanged.

## Current counts

| Item | Current value |
|---|---:|
| Local source dispositions | 33 |
| Canonical Scene Evidence JSON | 31 |
| Shot/edit units | 2,343 |
| Candidate identities | 124 |
| Mechanism families | 16 |
| Evidence records reviewed | 31 |
| Moving-image reviewed Shot refs | 1,840 |
| Final candidate dispositions | 108 |
| Candidates pending evidence | 12 |
| Candidates awaiting direct review of existing material | 4 |
| Precise evidence gaps | 5 |
| Evidence units with a final decision mapping | 30 |
| Runtime-participating families | 13 |
| Runtime-authorized rules | 11 |
| Positive forward packages | 11 |
| Boundary forward packages | 11 |
| Total forward packages | 29 |
| Directly auditioned semantic-audio scenes | 0 |

Final dispositions comprise 11 positive rules, 36 supporting candidates, 56
boundary/counterexample candidates, three merged duplicates and two
evidence-backed rejections. `EVIDENCE_GAP_PENDING` and
`EXISTING_MATERIAL_REVIEW_REQUIRED` are interim states, not final outcomes.

## Active runtime rules

The 11 rules cover performance ownership, spatial reset, relation endpoints,
comparative fields, causal action, object custody, waypoint routes, mobile
attention, initial relation geometry, stable-axis state holds and aftermath.
Each has exact fresh-reviewed lineage, unrelated-work support, a real boundary,
a project-original fallback and paired forward tests. All creative packages
remain `HUMAN_REVIEW_PENDING` and authorize neither generation nor publication.

## Important evidence boundaries

Renewed review corrected `WIRE-S01E04-OLD-CASES-001-S040` to the visible
person-at-window observation while leaving identity and story meaning unknown.
Signal measurements and speech recognition remain navigation aids, not direct
audition. The 12 external-gap candidates are grouped into five precise requests:
versioned object handoff, revised repeat, multi-thread natural boundary,
same-trigger scale order, and cross-work subjective access.

## Authoritative sources

| Authority | Path | Current status |
|---|---|---|
| Live phase summary | `context/STATE.md` | ACTIVE — single current status entrypoint |
| Exhaustive dispositions and precise gaps | `research/grammar/runtime_integration.review.json` | ACTIVE — canonical authority |
| Per-scene facts | `research/evidence/**/*.scene-evidence.json` | ACTIVE — 31 records |
| Candidate lineage and grouping | `research/grammar/candidate_rule_index.json` | GENERATED — 124 candidates, 16 families |
| Cross-work support and boundaries | `research/grammar/cross_work_support_matrix.json` | GENERATED |
| Runtime directing rules | `research/grammar/director_grammar_v0.2.json` | GENERATED — 11 rules |
| Original routing packages | `examples/forward-tests/index.json` | GENERATED — 29 packages |
| Machine validation summary | `research/validation/exhaustive-runtime-integration-validation.json` | PASS / IN_PROGRESS |
| Human-readable phase report | `research/validation/EXHAUSTIVE_RUNTIME_INTEGRATION_REPORT.md` | ACTIVE |

Generated `*.scene-evidence.generated.md` files are review views, not separate
fact sources. The 30 legacy evidence Markdown ledgers remain immutable
provenance. Material catalogs do not authorize rules.

## Remaining boundary

Four exact Sound of Metal candidate intervals need direct human audition of the
existing local audio. The model environment cannot establish audible state,
ownership, causality or edit intent by reading waveforms or transcripts. After
that review, the phase can become `PARTIAL_EVIDENCE_GAP` if the 12 fixed-corpus
gaps remain; all 16 families and 124 candidates still prevent `COMPLETE`.

## Next single action

Commit and push the verified local tree to PR #5, wait for final-head CI, then
obtain a clean-checkout read-only audit across all 16 families. Local evidence
is 292/292 unit and CLI tests plus 25/25 repository checks. Do not merge `main`.
