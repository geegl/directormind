# Legacy Scene Evidence Audit

Updated: 2026-08-31

Status: `PRE_CONVERSION_AUDIT_COMPLETE`

This is a read-only migration audit of the 30 current local-source Scene Evidence Markdown files. It does not add a reference work, re-audition audio, re-prove source-film observations, or approve any candidate rule for runtime use. The Good Omens consolidated baseline is outside this 30-file conversion batch.

## Scope and method

- Three independent read-only batches reviewed 10 evidence files each.
- Every legacy Shot table and Candidate Rule table was parsed for row count, column count, ID sequence, displayed start/end adjacency, duration consistency, evidence status, AI-risk structure, fallback coverage, rule references, broken repository references, and migration-sensitive wording.
- Semantic review specifically checked OBSERVED/INFERRED/UNKNOWN separation, cross-cut identity, audio/text status, functional-role claims, and reference-surface leakage into transferable rule fields.
- No source media was modified or committed. No audio was directly auditioned in this audit.
- Displayed Markdown timing is only a migration input. Canonical JSON timing must be rebuilt from available frame/PTS endpoints rather than accumulated rounded row durations.

## Corpus result

| Metric | Result |
|---|---:|
| Local-source evidence files audited | 30 |
| Legacy Shot/edit-unit rows | 2,255 |
| Candidate rules | 120 |
| Legacy Shot tables with 24 data columns | 30/30 |
| Legacy Candidate Rule tables with 16 data columns | 29/30 |
| Legacy Candidate Rule table missing non-applicability | 1/30: The Bear S01E07 |
| Shots with explicit camera/performance/continuity risk axes | 1,159/2,255 |
| High-equivalent-risk shots without a corresponding fallback | 152 |
| Directly auditioned scenes | 0/30 |
| Signal-measured but not auditioned scenes | 1/30: Sound of Metal |
| Verified text-anchor scenes | 0/30 |
| Broken or unresolvable repository artifact claims | 13 |
| Candidate rules with three separate confidence values | 0/120 |
| Candidate rules with a verified same-trigger contrary source | 0/120 |

Recommended `scene_unit_type` distribution:

| Type | Count |
|---|---:|
| `NATURAL_CONTINUOUS_SCENE` | 8 |
| `CONTIGUOUS_EDITORIAL_SEQUENCE` | 9 |
| `PARALLEL_INTERCUT_SEQUENCE` | 2 |
| `SINGLE_VISIBLE_TAKE` | 3 |
| `SELECTED_INTERNAL_ENVELOPE` | 8 |

The type alone is insufficient for all legacy units. Migration also needs separate boundary completeness, production-take status, and per-row completeness so that a selected internal interval with no visible cut is not misrepresented as a verified production take or a complete natural scene.

## Per-file migration register

`AI axes` is the number of Shot rows already separating camera, performance, and continuity risk. `Missing fallback` counts high-equivalent legacy risk rows without a usable per-shot fallback. Audio `BLOCKED` means direct audition is required before an audio director rule can be emitted.

| # | Evidence ID | Recommended unit type | Shots | Rule shape | AI axes | Missing fallback | Audio | Broken refs | Primary conversion blocker |
|---:|---|---|---:|---|---:|---:|---|---:|---|
| 1 | `A-QUIET-PLACE-2018-PARALLEL-BODY-STATE-RADIAL-LIGHT-001` | `SELECTED_INTERNAL_ENVELOPE` | 34 | 4×16 | 34 | 0 | BLOCKED | 0 | Parallel timing, sound causality, contact, roles, and cross-cut identity remain UNKNOWN. |
| 2 | `DM-ANDOR-S01E10-SEL-001` | `SELECTED_INTERNAL_ENVELOPE` | 121 | 4×16 | 121 | 0 | BLOCKED | 0 | Scene problem, functional roles, command/broadcast meaning, and cross-zone causality are not picture facts. |
| 3 | `APOLLO-13-1995-CONSTRAINED-MATERIAL-HANDOFF-001` | `CONTIGUOUS_EDITORIAL_SEQUENCE` | 12 | 4×16 | 0 | 8 | BLOCKED | 0 | Bare Shot IDs need namespacing; AI axes/fallbacks and cross-cut role identity need rebuilding. |
| 4 | `BETTER-CALL-SAUL-S03E05-PUBLIC-PROOF-001` | `SELECTED_INTERNAL_ENVELOPE` | 105 | 4×16 | 0 | 0 | BLOCKED | 0 | Public/legal function and reveal meaning are INFERRED; late overlay-covered pixels are UNKNOWN. |
| 5 | `DM-BODYGUARD-S01E01-SEL-001` | `SELECTED_INTERNAL_ENVELOPE` | 211 | 4×16 | 211 | 0 | BLOCKED | 0 | Existing scene-problem taxonomy is only a provisional route; role, object, authority, and causality stay UNKNOWN. |
| 6 | `BRIDGERTON-S02E05-CONTAINED-PROXIMITY-001` | `NATURAL_CONTINUOUS_SCENE` | 41 | 4×16 | 41 | 0 | BLOCKED | 0 | Proximity is visible; romance, consent, reaction cause, and physical contact are not established. |
| 7 | `B99-S05E14-THE-BOX-PRIDE-BAIT-CONFESSION-001` | `SELECTED_INTERNAL_ENVELOPE` | 22 | 4×16 | 0 | 0 | BLOCKED | 2 | Two missing TSVs; dual-clock ownership, contact wording, role semantics, and AI axes require normalization. |
| 8 | `CHERNOBYL-S01E05-HEARING-RECON-001` | `CONTIGUOUS_EDITORIAL_SEQUENCE` | 205 | 4×16 | 205 | 0 | BLOCKED | 0 | Process/collapse/hearing meaning is INFERRED; rule risks need per-axis levels rather than prose-only axes. |
| 9 | `CHILDREN-OF-MEN-2006-MOVING-CAR-EXTERIOR-DISRUPTION-001` | `SINGLE_VISIBLE_TAKE` | 1 | 4×16 | 1 | 0 | BLOCKED | 0 | Visible continuity is not production-take proof; long-occlusion identity and action attribution remain UNKNOWN. |
| 10 | `CITIZEN-KANE-1941-BREAKFAST-MONTAGE-001` | `CONTIGUOUS_EDITORIAL_SEQUENCE` | 27 | 4×16 | 0 | 12 | BLOCKED | 0 | Bare Shot/role IDs, transition-bearing edit units, boundary uncertainty, AI axes/fallbacks, and local media-name text need migration. |
| 11 | `GETOUT-2017-HYPNOSIS-SUBJECTIVE-SPACE-001` | `NATURAL_CONTINUOUS_SCENE` | 74 | 4×16 | 0 | 0 | BLOCKED | 0 | Coercion/subjectivity and object causality are not picture facts; transferable rules contain source-surface staging. |
| 12 | `HOUSE-OF-THE-DRAGON-S01E08-THRONE-ROOM-INGRESS-TO-SEATED-STATE-001` | `SELECTED_INTERNAL_ENVELOPE` | 68 | 4×16 | 68 | 0 | BLOCKED | 1 | Missing state-ledger reference; authority/relationship/contact meaning and signature object terms need separation. |
| 13 | `KNIVES-OUT-2019-WILL-READING-001` | `CONTIGUOUS_EDITORIAL_SEQUENCE` | 108 | 4×16 | 0 | 0 | BLOCKED | 0 | Public-reveal meaning, stimulus/reaction causality, identity grouping, and AI axes remain unverified. |
| 14 | `MARRIAGE-STORY-2019-APARTMENT-SEQUENCE-001` | `NATURAL_CONTINUOUS_SCENE` | 85 | 4×16 | 85 | 0 | BLOCKED | 4 | Four missing TSVs; relationship, emotion, contact/help, and cross-cut object identity remain UNKNOWN. |
| 15 | `MOONLIGHT-2016-TWO-APPEARANCE-MULTI-ZONE-EDITORIAL-001` | `CONTIGUOUS_EDITORIAL_SEQUENCE` | 79 | 4×16 | 79 | 0 | BLOCKED | 0 | Relationship/reunion/service meaning and source-specific props must not enter transferable rule text. |
| 16 | `MRR-S04E07-ACT-FOUR-VISUAL-001` | `NATURAL_CONTINUOUS_SCENE` | 201 | 4×16 | 201 | 0 | BLOCKED | 1 | Missing rule TSV; coercion/identity/psychology and cross-cut object grouping remain UNKNOWN. |
| 17 | `NOBODY-2021-BUS-001` | `NATURAL_CONTINUOUS_SCENE` | 128 | 4×16 | 0 | 80 | BLOCKED | 0 | Bare Shot IDs, extensive role/intent/outcome leakage in OBSERVED, cross-cut identity, AI axes, and fallback coverage all fail the target contract. |
| 18 | `SICARIO-2015-BORDER-CHECKPOINT-001` | `CONTIGUOUS_EDITORIAL_SEQUENCE` | 96 | 4×16 | 0 | 0 | BLOCKED | 0 | Bare Shot IDs and legacy header aliases need deterministic mapping; threat/team/weapon-function/causality remain INFERRED or UNKNOWN. |
| 19 | `SOUND-OF-METAL-SIGNAL-STATE-EE-V0.1` | `CONTIGUOUS_EDITORIAL_SEQUENCE` | 25 | 4×16 | 25 | 0 | SIGNAL ONLY | 0 | Signal entities require auxiliary evidence IDs; four audio-dependent candidates stay `BLOCKED_BY_UNKNOWN` until direct audition. |
| 20 | `TED-LASSO-S01E08-DARTS-REVERSAL-001` | `PARALLEL_INTERCUT_SEQUENCE` | 147 | 4×16 | 0 | 0 | BLOCKED | 0 | Intercut simultaneity/causality, game meaning, shared stimulus, identity, and source-specific objects remain unproved. |
| 21 | `BEAR-S01E07-REVIEW-001` | `SINGLE_VISIBLE_TAKE` | 1 | 4×15 | 0 | 1 | BLOCKED | 0 | Missing non-applicability, high-risk fallback, role-name provenance, and picture-only semantic cleanup. |
| 22 | `BEAR-S02E07-TASK-CLOSED-LOOP-001` | `CONTIGUOUS_EDITORIAL_SEQUENCE` | 114 | 4×16 | 0 | 0 | BLOCKED | 0 | Mouth movement, chart/hand identity, task ownership, object lineage, role provenance, AI axes, and expanded Shot refs need migration. |
| 23 | `THE-DEVIL-WEARS-PRADA-2006-CERULEAN-CORRECTION-001` | `SELECTED_INTERNAL_ENVELOPE` | 26 | 4×16 | 0 | 22 | BLOCKED | 1 | Missing row-level TSV claim; attention/reaction semantics, boundary status, cross-cut identity, AI axes, and fallbacks fail target gates. |
| 24 | `DM-EVID-HH-S01E06-ENSEMBLE-CONTINUOUS-REFRAMING-V0.1` | `SELECTED_INTERNAL_ENVELOPE` | 1 | 4×16 | 1 | 0 | BLOCKED | 0 | The selected row is partial at an internal endpoint; visible continuity cannot prove production take, identity, time, or place. |
| 25 | `TLOU-BEDROOM-LOCAL-001` | `NATURAL_CONTINUOUS_SCENE` | 27 | 4×16 | 27 | 0 | BLOCKED | 2 | Two absent TSV-mirror claims; relationship/refusal/trauma, role, foreground ownership, and all audio remain unproved. |
| 26 | `MARTIAN-MULTI-SPACE-OBJECT-STATE-EDITORIAL-SEQUENCE-LOCAL-001` | `CONTIGUOUS_EDITORIAL_SEQUENCE` | 59 | 4×16 | 59 | 0 | BLOCKED | 2 | Two absent TSV-mirror claims; task/failure/revision meaning, cross-cut identity/causality, and audio/text remain unproved. |
| 27 | `THE-SOCIAL-NETWORK-2010-OPENING-TWO-PERSON-EXCHANGE-001` | `NATURAL_CONTINUOUS_SCENE` | 91 | 4×16 | 0 | 0 | BLOCKED | 0 | Source-start natural boundary, relationship/dialogue/order, AI axes, role status, and expanded rule Shot refs remain unresolved. |
| 28 | `WIRE-S01E04-OLD-CASES-001` | `NATURAL_CONTINUOUS_SCENE` | 68 | 4×16 | 0 | 29 | BLOCKED | 0 | Bare Shot IDs, names/roles/search/reaction leakage, cross-cut entity hardening, AI axes, and fallback coverage fail target gates. |
| 29 | `TRUE-DETECTIVE-S01E04-MULTI-ZONE-MOBILE-ROUTE-001` | `SINGLE_VISIBLE_TAKE` | 1 | 4×16 | 1 | 0 | BLOCKED | 0 | Visible take versus production take, natural-scene boundaries, long-occlusion identity, contact, role, and absolute map remain distinct UNKNOWNs. |
| 30 | `UNBELIEVABLE-S01E02-CONTAINED-TWO-PERSON-SEQUENCE-001` | `PARALLEL_INTERCUT_SEQUENCE` | 77 | 4×16 | 0 | 0 | BLOCKED | 0 | Cross-intercut identity is inconsistently marked OBSERVED; simultaneity, causal relation, ingress, role/ethics, and AI axes remain unproved. |

## Broken-reference register

The audit found 13 missing or unresolvable artifact claims:

- Brooklyn Nine-Nine: two named TSVs.
- House of the Dragon: one state-ledger Markdown reference.
- Marriage Story: four named TSVs.
- Mr. Robot: one named Candidate Rule TSV.
- The Devil Wears Prada: one generic exact-row TSV claim.
- The Last of Us: two Shot/Rule TSV mirror claims.
- The Martian: two Shot/Rule TSV mirror claims.

These are migration defects, not evidence that the referenced temporary files still exist. A5 requires removing the claims or replacing them with `scene-evidence.json`; recreating unverified files from memory is not allowed.

## Cross-corpus blockers

### Must be corrected during JSON conversion

1. Namespace every Shot ID and transactionally rewrite rule references.
2. Rebuild timing and statistics from frame/PTS or exact endpoints with a fixed tolerance; do not sum rounded display durations.
3. Split AI risk into camera/performance/continuity and provide a corresponding project-original fallback for every HIGH/CRITICAL axis.
4. Give every claim a unique ID and resolvable provenance reference. UNKNOWN cannot become a required story fact.
5. Record cross-cut person, body-part, object, vehicle, and zone identity as `CROSS_CUT_INFERRED` or `UNKNOWN`; repeated aliases are not person IDs.
6. Separate selected-boundary status, visible-shot completeness, and production-take status.
7. Expand rule Shot ranges into complete namespaced ID arrays; phase names and time spans are not Shot IDs.
8. Split the legacy single confidence into within-source, transfer, and execution confidence. Current execution confidence is UNKNOWN for all 120 rules.
9. Keep all 120 rules at `SINGLE_WORK_CANDIDATE` or `BLOCKED_BY_UNKNOWN`; none has a verified same-trigger contrary source.
10. Treat 29 scenes as `BLOCKED_DIRECT_AUDITION`; treat Sound of Metal as `SIGNAL_MEASURED_NOT_AUDITIONED`. No current scene can emit a directly observed semantic audio rule.
11. Treat all current text tracks as `TEXT_ANCHOR_NOT_USED`; burned-in subtitles, overlays, filenames, and synopses do not become text anchors.
12. Remove source names, roles, dialogue, locations, signature props, and scene-event surface detail from operational migration rules while preserving abstract mechanics and evidence lineage.

### Schema/validator changes justified by this audit

- Added independent boundary and production-take statuses.
- Added Shot completeness.
- Added role appearance-identity status and general continuity tracks.
- Added structured auxiliary evidence for decoded-signal measurements and cut audits.
- Added versioned method records so source and rule method IDs can resolve.
- Added namespaced Shot IDs, fixed time tolerance, source-track checks, cross-cut identity checks, audio gating, semantic leakage lint, surface-copy checks, and per-axis fallback checks.

## What this audit did not verify

- It did not replay source video, re-check every accepted cut against frames, or verify production methods.
- It did not directly audition any soundtrack or validate dialogue, ambience, score, silence, sound source, subjective sound, or audio causality.
- It did not validate subtitle or script meaning and created no text anchors.
- It did not prove that a legacy candidate transfers to another work, is executable by a generation system, or improves audience response.
- It did not validate the 30 future `scene-evidence.json` files, because those files do not yet exist.

The audit is sufficient to begin deterministic conversion, not to mark A3, B3, C3, E3, F3, or any grammar-promotion item complete.
