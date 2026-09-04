# Current State

Updated: 2026-09-04

## Current phase

Exhaustive Runtime Integration is `PARTIAL_EVIDENCE_GAP` on
`codex/exhaustive-runtime-integration` and PR #5. The fixed corpus remains 33
registered sources, 31 canonical Scene Evidence records, 2,343 Shot/edit
units, 124 candidates and 16 mechanism families.

Fresh moving-image review covers all 1,840 unique candidate-dependent Shot refs.
Of 124 candidates, 55 have final outcomes and 69 have fixed-corpus evidence gaps.
Direct human audition of the complete Sound of Metal selection covers all 25
Shots through 16 approximate observations. Candidate audio claims exactly bind
their source descriptions, but unrelated support and boundaries remain missing.

Root is the only repository writer. The prior full 16-family audit and latest
clean-checkout Sound/validator delta audit both found no must-fix; the latest
implementation head also passed GitHub CI. No source media changed or entered
Git. `main` remains unchanged.

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
| Final candidate dispositions | 55 |
| Candidates pending evidence | 69 |
| Candidates awaiting direct review of existing material | 0 |
| Precise evidence gaps | 14 |
| Evidence units with a final decision mapping | 26 |
| Runtime-participating families | 11 |
| Runtime-authorized rules | 7 |
| Positive forward packages | 7 |
| Boundary forward packages | 7 |
| Total forward packages | 29 |
| Directly auditioned semantic-audio scenes | 1 |

Final dispositions comprise seven positive rules, 24 supporting candidates, 20
boundary/counterexample candidates, one merged duplicate and three
evidence-backed rejections. `EVIDENCE_GAP_PENDING` and
`EXISTING_MATERIAL_REVIEW_REQUIRED` are interim states, not final outcomes. The
seven runtime rules retain fresh-reviewed lineage, support, boundaries and
paired tests; all creative packages remain `HUMAN_REVIEW_PENDING`.

## Important evidence boundaries

Renewed review corrected `WIRE-S01E04-OLD-CASES-001-S040` to the visible
person-at-window observation while leaving identity and story meaning unknown.
Signal measurements and speech recognition remain navigation aids, not direct
audition. The direct track proves surface states at about one-second precision;
speaker identity, source ownership, subjectivity, causality, edit intent and
subsecond alignment remain unknown. The validator rejects incomplete coverage,
missing observations and claims that differ from their source descriptions.
withdrew three previously promoted rules:
their claimed comparative-field, object-custody and initial-geometry boundaries
did not share the positive rule's trigger. A second review withdrew waypoint
coverage for the same reason, corrected one spatial support and one spatial
boundary, moved eleven unrelated spatial candidates back to evidence gaps, and
rejected one unsupported moving-shot fallback. The 69 gap candidates are now
grouped into fourteen precise requests.

## Authoritative sources

| Authority | Path | Current status |
|---|---|---|
| Live phase summary | `context/STATE.md` | ACTIVE — single current status entrypoint |
| Exhaustive dispositions and precise gaps | `research/grammar/runtime_integration.review.json` | ACTIVE — canonical authority |
| Per-scene facts | `research/evidence/**/*.scene-evidence.json` | ACTIVE — 31 records |
| Candidate lineage and grouping | `research/grammar/candidate_rule_index.json` | GENERATED — 124 candidates, 16 families |
| Cross-work support and boundaries | `research/grammar/cross_work_support_matrix.json` | GENERATED |
| Runtime directing rules | `research/grammar/director_grammar_v0.2.json` | GENERATED — 7 rules |
| Original routing packages | `examples/forward-tests/index.json` | GENERATED — 29 packages |
| Machine validation summary | `research/validation/exhaustive-runtime-integration-validation.json` | PASS / PARTIAL_EVIDENCE_GAP |
| Human-readable phase report | `research/validation/EXHAUSTIVE_RUNTIME_INTEGRATION_REPORT.md` | ACTIVE |

Generated `*.scene-evidence.generated.md` files are review views, not separate
fact sources. The 30 legacy evidence Markdown ledgers remain immutable
provenance. Material catalogs do not authorize rules.

## Remaining boundary

All review possible against the currently identified local material is now
recorded. The remaining 69 candidates require the fourteen precise additions
listed in the canonical review; the four Sound candidates specifically need
unrelated directly auditioned support and same-trigger contrary cases. Five
families still lack a final runtime effect, so `COMPLETE` remains prohibited.

Next: keep PR #5 open and await user direction. Do not merge `main` or call the
goal complete while the 69 fixed-corpus evidence gaps remain.
