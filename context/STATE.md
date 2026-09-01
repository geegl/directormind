# Current State

Updated: 2026-09-01

## Active phase

The user-approved 33-source generalization Goal is active on `codex/macos-first16-local-batch`.

Phase 1 is complete and independently reviewed: canonical JSON is the sole machine fact source, generated review Markdown is deterministic and non-overwriting, validation claims are reproducible, and project state is compact. Phase 2 candidate normalization is next.

No new reference work, media operation, remote update, merge, deployment or publication is authorized.

## Verified counts

| Item | Current verified value |
|---|---:|
| Local source dispositions | 33 |
| Canonical current-local Scene Evidence JSON | 30 |
| Shot/edit units | 2,255 |
| Legacy candidate identities | 120 |
| Structural Scene Evidence passes | 30/30 |
| Structural errors | 0 |
| Preserved warnings | 69 |
| Current unit/CLI tests including Phase 1 | 77 |
| Directly auditioned semantic-audio scenes | 0 |
| Source media deleted by the closed-corpus task | 0 |

The 120 candidate identities remain non-operational and `BLOCKED_BY_UNKNOWN`. All current scene-problem classifications remain `UNKNOWN`. Twenty-nine scenes remain `BLOCKED_DIRECT_AUDITION`; *Sound of Metal* remains `SIGNAL_MEASURED_NOT_AUDITIONED`.

## Authoritative sources

These are the only intended completion authorities. A planned source does not become authoritative until its schema, artifact and tests are checked in and validated.

| Authority | Path | Current status |
|---|---|---|
| Per-scene facts | `research/evidence/**/*.scene-evidence.json` | ACTIVE — 30 canonical JSON units |
| Candidate-rule lineage and grouping | `research/grammar/candidate_rule_index.json` | PLANNED — not yet present |
| Cross-work support and contrary evidence | `research/grammar/cross_work_support_matrix.json` | PLANNED — not yet present |
| Runtime directing rules | `research/grammar/director_grammar_v0.2.json` | PLANNED — not yet present |
| Phase, counts, blockers and next step | `context/STATE.md` | ACTIVE |

Generated `*.scene-evidence.generated.md` files are deterministic review views of canonical JSON, not separate fact sources. Legacy evidence Markdown remains immutable migration provenance. Coverage and acquisition files are material catalogs only.

## Current blockers

- Candidate Rule Schema, normalized index and support matrix do not yet exist.
- No candidate has passed cross-work promotion gates.
- Runtime Grammar v0.2 and routing are not yet implemented.
- Original positive/non-applicable forward tests do not yet exist.
- Existing *Succession* evidence remains isolated in the older PR and must be migrated through current contracts.
- Automated repository checks and final independent audit are not complete.
- Source replay and direct semantic-audio audition remain outside this Goal; structural validation cannot prove the original picture observations, sound semantics, creative quality or audience response.

## Latest validation

- Closed-corpus converter check: PASS — 30 scenes, 2,255 Shot/edit units, 120 candidate identities.
- Current unit/CLI suite: PASS — 77 tests including Phase 1 renderer and state-contract regressions.
- Full Scene Evidence validation: PASS_STRUCTURAL — 30 passed, 0 failed, 0 errors, 69 warnings.
- Phase 1 renderer: PASS locally — 30 generated files match canonical JSON, round-trip deterministically, and preserve every legacy Markdown file.
- Phase 1 independent read-only audit: PASS — no must-fix finding remains.

The current command-to-claim evidence is `research/validation/VALIDATION_CLAIM_REGISTER.md`. The versioned closed-corpus evidence is `research/validation/CLOSED_CORPUS_COMPLETION_REPORT.md` and `research/validation/scene-evidence-validation.json`. A structural pass is not human creative approval.

## Next single action

Create the isolated local Phase 1 commit, then build the Candidate Rule Schema, normalized 120-lineage index, cross-work support matrix and promotion gates without promoting UNKNOWN-dependent rules.
