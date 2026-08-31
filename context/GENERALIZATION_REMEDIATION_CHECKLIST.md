# DirectorMind Generalization Remediation Checklist

Updated: 2026-08-31

## Task card

### Task name

DirectorMind evidence generalization phase 1: audit the existing 30 local-source evidence files, establish the remediation checklist and Scene Evidence contract, and close the validator acceptance gaps found during independent reproduction.

### 1. Why this work exists

DirectorMind already has extensive picture-led evidence, but the evidence is stored in heterogeneous Markdown tables and cannot yet be deterministically validated or safely routed into a general directing grammar. Missing references, inconsistent evidence status, cross-cut identity hardening, single-axis AI risk, and unreproducible validation claims prevent machine use.

### 2. Expected result

After a contributor writes a Scene Evidence JSON unit, running the repository validator should either produce a reproducible structural pass or precise errors for schema, timing, provenance, UNKNOWN leakage, references, fallback, audio/text boundaries, public-repository payloads, and reference-surface transfer. Tested common UNKNOWN wording must not hide a rule fact or an unauditioned sound instruction; broader semantic paraphrase remains a human-review boundary. The current 30 legacy units must first have an explicit migration register.

### 3. Out of scope for this phase

- No conversion of all 30 Markdown files to canonical JSON yet.
- No Candidate Rule index, cross-work matrix, Grammar v0.2, Skill routing change, or forward test yet.
- No new reference film or television work.
- No provider prompt, paid model, or generated media.
- No private 36-episode script or IR modification.
- No merge to `main`.

### 4. Protected content and systems

- Source video/audio, stills, contact sheets, subtitles, scripts, local paths, credentials, accounts, permissions, payments, production systems, unrelated pages, and user-owned work are not to be modified or published.
- Existing 30 evidence facts remain unchanged during this phase. The only evidence-file edit authorized in the repair pass is removal of one trailing blank line; it changes no evidence text.
- Branch / PR remains `codex/macos-first16-local-batch` / PR #3.

### 5. Completion criteria for this phase

- [x] The 30-file audit is committed with scope and limitations.
- [x] The Scene Evidence schema contains every A1/A2 requirement and validates as JSON.
- [x] The repaired repository validator implements the scoped B1 gates planned for canonical JSON and passes the repository reproduction cases.
- [x] The existing 45 tests plus the new acceptance-gap tests pass, including the CLI path and precise error paths.
- [x] Existing evidence content and unrelated functionality remain unchanged.
- [x] Commands, remaining risks, and rollback are recorded.

### 6. Current status

- Current sole implementer/writer: `/root`; prior sub-agents performed read-only corpus and validator reviews only.
- Completed before this repair: checklist, 30-file audit report, Scene Evidence schema, standard-library validator, and 45 validator tests.
- Completed in this repair: UNKNOWN-to-rule (including contact/initiator aliases), unauditioned-score-directive (including `bring in` phrasing), HEIC/SSA, data-payload, and credential-format guards; eight new test methods with paired cases; three raw release-label cells neutralized; one trailing blank line removed. PR #3 was not modified by the latest local repair.
- Not completed: canonical conversion of the 30 files and all later A3–M work.
- Validation result: schema JSON syntax, Python AST parse, and 53 unit/CLI tests pass. The latest local repair still requires a fresh independent read-only re-review before its status can be represented as independently accepted.
- Known issues: the legacy corpus has 13 broken artifact claims, 152 high-equivalent-risk Shot rows without fallback, 1,096 Shot rows without three-axis AI risk, no direct audio audit, and no three-confidence Candidate Rule.
- Next single action: run a fresh independent read-only re-review of the latest local repair. Do not start A3, update PR #3, or merge it without explicit authorization.

Rollback for this repair: revert only the isolated latest local repair commit with a normal Git revert. If it is later pushed or merged, use the same revert-commit approach and, after merge, a new pull request. Do not rewrite shared history.

## Status contract

Only these states are allowed:

- `TODO`
- `IN_PROGRESS`
- `BLOCKED`
- `VERIFIED_DONE`

`VERIFIED_DONE` requires a committed artifact plus a reproducible test or independent-review reference. A structural pass is not creative approval or proof that source-film observations are correct.

## Phase 1 validation record

- `python3 -m json.tool skills/drama-director-compiler/references/scene-evidence.schema.json` — PASS.
- Python in-memory compile / AST parse for the validator and tests — PASS.
- `python3 -m unittest discover -s skills/drama-director-compiler/tests -v` — PASS, 53 tests after the latest local repair.
- The legacy-audit table check — PASS: 30 data rows, ten data columns per row, 2,255 Shot/edit units, 120 rules, and 13 broken artifact claims.
- The earlier independent PASS was superseded by a later read-only review that reproduced contact/initiator UNKNOWN leakage and `bring in` unauditioned-music leakage. Those cases now have paired repository tests and pass locally; a fresh independent verdict on the latest working tree is pending.

Remaining validation boundary: these checks do not replay source media, directly audition audio, prove legacy picture observations, demonstrate audience effect, or constitute creative approval. No canonical per-scene JSON exists yet; A3 and later work remain outside this phase. Reference-surface inventory completeness still requires human review during migration.

## Startup and corpus freeze

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| P1 | VERIFIED_DONE | Fetch current `origin/main` without leaving the current branch or PR. | `git fetch origin main` completed on 2026-08-31; branch remains `codex/macos-first16-local-batch`. |
| P2 | VERIFIED_DONE | Read the required project context, evidence template, seed grammar, Skill, and Director IR contract. | Read in the root session before implementation. |
| P3 | VERIFIED_DONE | Audit all 30 existing local-source evidence Markdown files. | `research/validation/LEGACY_SCENE_EVIDENCE_AUDIT.md`; independent 10/10/10 review and final arithmetic review passed. |
| P4 | VERIFIED_DONE | Freeze reference acquisition and selection. | This checklist records the freeze; no new work is authorized. |

## A. Machine-readable Scene Evidence

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| A1 | VERIFIED_DONE | Add `skills/drama-director-compiler/references/scene-evidence.schema.json` with all required top-level fields and the five explicit `scene_unit_type` values. | JSON syntax check and independent 33/33 top-level field review passed. |
| A2 | VERIFIED_DONE | Standardize every Shot field: identity/time, camera start/path/end, focus, zone/axis, abstract roles, blocking/action/states, event/reaction, performance, edits, motivation/function, evidence tracks, three-axis AI risk, fallback, and unknowns. | Independent 33/33 Shot-field review and validator fixture passed. |
| A3 | TODO | Convert the existing 30 local-source evidence units to schema-valid `scene-evidence.json`, one per work directory. | 30+ JSON files pass the full validator; no new source work is added. |
| A4 | TODO | Add deterministic `render_scene_evidence.py`; JSON becomes the sole machine fact source and refreshes Markdown summary, shot table, statistics, candidate rules, UNKNOWN, and boundary. | Renderer round-trip/determinism test and generated sections match JSON. |
| A5 | TODO | Resolve the 13 missing claims found in B99, HOTD, Marriage Story, Mr. Robot, DWP, TLOU, and The Martian by committing rights-safe original analysis artifacts or replacing those references with `scene-evidence.json`. | Broken-reference scan returns zero. |

## B. Reproducible validation

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| B1 | VERIFIED_DONE | Add `validate_scene_evidence.py` covering schema, shot identity/timing, provenance, UNKNOWN leakage, rule references/boundaries, HIGH-risk fallback, surface-copy guards, and public-repository prohibitions. | Repair code rejects the repository's scoped UNKNOWN-rule, same-sentence sound-directive, HEIC/SSA, data-payload, and credential-format cases while preserving explicit safe boundaries; broad unlisted semantic paraphrase remains human-reviewed. |
| B2 | VERIFIED_DONE | Add minimum tests: valid evidence, gap, overlap, missing Shot ref, UNKNOWN promotion, HIGH without fallback, missing non-applicability, single-source GENERAL_DEFAULT, audio rule without observed audio, and reference-surface leakage. | 53/53 unit and CLI tests pass, including eight repair test methods with positive/negative subcases; fresh independent review of the latest repair remains pending. |
| B3 | TODO | Validate all 30 Scene Evidence JSON files and write `research/validation/scene-evidence-validation.json` with errors and warnings preserved. | `failed=0`; warning rows remain visible. |
| B4 | TODO | Remove or replace unreproducible validation claims, including bare `760 checks` and independent-pass statements without command, versioned validator, and repository report. | Claim-to-report/reference audit returns zero broken claims. |

## C. Multimodal evidence boundaries

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| C1 | TODO | Separate `PICTURE_OBSERVED`, `AUDIO_OBSERVED`, `TEXT_ANCHOR`, `INFERRED`, and `UNKNOWN`; text anchors cannot prove picture, performance, edit, composition, or mix. | Schema fields, validator restrictions, and tests. |
| C2 | TODO | Add the required audio-audit fields: overlap, silence, ambience, score in/out, sound-before-image, offscreen sound, bridge, subjective sound, object sound, information change, and unknowns. | Schema and converted evidence contain all fields, including explicit UNKNOWN/BLOCKED values. |
| C3 | TODO | Directly audit the eight audio-priority scenes, or mark `BLOCKED_DIRECT_AUDITION`, suppress audio rules, and emit a one-time human audio review sheet. | Timecoded review evidence or explicit blocked artifact per scene. |
| C4 | TODO | Keep Sound of Metal at `SIGNAL_MEASURED_NOT_AUDITIONED`; hearing loss, tinnitus, subjective hearing, source, information access, emotion, and audience effect remain unproven; audio rules remain blocked until direct audition. | Scene JSON, rule index, and validator agree. |

## D. Abstract roles and scene problems

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| D1 | TODO | Add functional role labels alongside appearance aliases; roles require scene facts or text anchors and otherwise remain UNKNOWN. | All converted scenes validate role provenance. |
| D2 | TODO | Use one canonical `scene_problem` primary enum and at most two secondary values; do not create work-specific synonyms. | Schema enum and corpus-wide uniqueness audit. |

## E. Candidate-rule normalization

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| E1 | TODO | Add `candidate-director-rule.schema.json` with the complete required rule contract. | Schema and tests. |
| E2 | TODO | Split `within_source_confidence`, `transfer_confidence`, and `execution_confidence`. | No legacy single confidence remains in canonical JSON. |
| E3 | TODO | Build `research/grammar/candidate_rule_index.json`, group synonyms into canonical families, preserve lineage, and label SUPPORTS/NARROWS/CONTRADICTS/COUNTEREXAMPLE/DUPLICATE. | All source candidate IDs resolve exactly once. |
| E4 | TODO | Build the cross-work support matrix in JSON and Markdown. | Deterministic JSON-to-Markdown comparison passes. |
| E5 | TODO | Require real same-trigger contrary evidence before promotion; `counterexample UNKNOWN` cannot support promotion. | Promotion validator and matrix audit pass. |

## F. Promotion discipline

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| F1 | TODO | Restrict `promotion_status` to SINGLE_WORK_CANDIDATE, CROSS_WORK_SUPPORTED, GENERAL_DEFAULT, REJECTED, or BLOCKED_BY_UNKNOWN. | Schema validation. |
| F2 | TODO | Keep complete one-work rules at SINGLE_WORK_CANDIDATE and outside runtime defaults. | Candidate index/runtime grammar separation test. |
| F3 | TODO | CROSS_WORK_SUPPORTED requires two unrelated works, same trigger, a real contrary/boundary case, and no hidden key UNKNOWN. | Promotion validator plus matrix evidence. |
| F4 | TODO | GENERAL_DEFAULT requires three unrelated works, same-trigger counterexample, two original forward tests, and human director approval. | Promotion validator plus forward-test/human-review references. |
| F5 | TODO | Block rules dependent on UNKNOWN audio, role function, or natural-scene boundary. | Negative tests and zero invalid promotions. |

## G. General Director Grammar v0.2

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| G1 | TODO | Add `research/grammar/director_grammar_v0.2.json` containing only CROSS_WORK_SUPPORTED, GENERAL_DEFAULT, and required project/safety constraints. | Grammar validator passes; no single-work runtime default. |
| G2 | TODO | Include the complete v0.2 rule field contract. | Schema/validator pass. |
| G3 | TODO | Remove reference-work-driven operational wording; work names may appear only in evidence lineage. | Surface-copy/name scan passes. |

## H. `drama-director-compiler` routing

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| H1 | TODO | Update the Skill with locked facts -> dramatic structure -> scene problem -> eligible rules -> 2-4 selections -> conflict resolution -> Director IR -> validation -> human review. | Skill diff plus routing tests. |
| H2 | TODO | Implement the fixed nine-level conflict priority from locked facts through provider limitations. | Conflict-order tests. |
| H3 | TODO | Check trigger, required facts, non-applicability, conflicts, and subject-matter similarity misuse. | Negative routing tests. |
| H4 | TODO | Add routing tests for power dialogue, fracture, public reveal, procedure, action, proximity, sound suspense, and no-applicable-rule; select at most 2-4 and copy no surface element. | Eight routing cases pass. |

## I. Project-original forward tests

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| I1 | TODO | Create rights-safe original test scripts for six required scene problems without rewriting reference plots. | Originality/surface-guard review. |
| I2 | TODO | Run a positive and boundary/non-applicable case for every promotion-ready family. | Forward-test index is complete. |
| I3 | TODO | Emit each required `examples/forward-tests/<case-id>/` package. | Package validator passes. |
| I4 | TODO | Mark unreviewed output `HUMAN_REVIEW_PENDING`; never label it production-ready or a winner. | Status scan passes. |

## J. State and single source of truth

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| J1 | TODO | Reduce `context/STATE.md` to phase, counts, blockers, latest validation, next step, and authoritative links. | Independent review confirms no per-work duplication. |
| J2 | TODO | Declare the five authoritative sources: Scene JSON, candidate index, support matrix, Grammar v0.2, and STATE. | Broken-reference scan passes. |
| J3 | TODO | Make Post-16 files material catalogs only, not simultaneous status/rule/completion authorities. | Responsibility audit passes. |

## K. Succession / PR #1 integration

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| K1 | VERIFIED_DONE | Do not merge PR #1 unchanged. | Current task explicitly prohibits it; PR #1 remains separate. |
| K2 | TODO | Cleanly migrate Succession: remove media hashes and hash-authorizing text, retain 88-shot evidence, add Scene JSON, candidate index, and support matrix entries. | Validator and forbidden-hash scan pass. |
| K3 | TODO | Resolve `SCENE_PROBLEM_MAP.md` conflicts and keep only the current route. | Rebase/conflict review passes. |
| K4 | TODO | Close PR #1 only after current-branch integration succeeds. | Current branch contains validated evidence; PR #1 is closed. |

## L. CI and final validation

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| L1 | TODO | Add minimal GitHub CI for Skill validation, Python compile, all schemas/evidence/rules/grammar/forward tests, broken refs, media/path/hash prohibitions, and whitespace. | Required check passes on PR #3. |
| L2 | TODO | Write `FINAL_GENERALIZATION_VALIDATION.json` with every required count and zero errors/broken refs/forbidden media/hashes. | Report passes its own schema and independent audit. |
| L3 | TODO | Run quick validation, units, all Scene Evidence, all Grammar, forward tests, whitespace, and GitHub CI. | Commands and results recorded. |
| L4 | TODO | Add `INDEPENDENT_GENERALIZATION_AUDIT.md` with verdict, P0/P1, non-blockers, unverified items, and merge decision. | Independent read-only reviewer issues PASS. |

## M. Final delivery

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| M1 | TODO | Deliver 30+ Scene Evidence JSON files. | Corpus count validation. |
| M2 | TODO | Deliver Scene Evidence schema, validator, and renderer. | Tests and reports pass. |
| M3 | TODO | Deliver Candidate Rule schema/index and cross-work matrix JSON/Markdown. | Rule/matrix validation passes. |
| M4 | TODO | Deliver Director Grammar v0.2 and updated Skill routing/conflict logic/tests. | Grammar/routing tests pass. |
| M5 | TODO | Deliver original forward-test packages. | Forward-test validation and human-review statuses pass. |
| M6 | TODO | Deliver full validation, independent audit, reduced STATE, clean Succession integration, CI, and updated PR description. | Checklist contains no TODO/IN_PROGRESS/BLOCKED item; user decides whether to merge. |

## Current blockers and known defects

- Existing Markdown is not yet a machine fact source; no local-source `scene-evidence.json` exists.
- Legacy field names, rule widths, evidence statuses, AI-risk axes, fallbacks, and reference links vary across the 30 files.
- Some legacy validation claims depended on deleted temporary assets or validators and are not reproducible from the repository.
- Direct semantic audio audition is absent; signal measurement is not semantic sound evidence.
- PR #1 cannot be merged unchanged because it contains prohibited media-hash material and older evidence semantics.

## Current next action

Stop and wait for the next explicit phase instruction. Do not begin A3 and do not merge PR #3.
