# DirectorMind Generalization Remediation Checklist

Updated: 2026-09-01

## 2026-09-01 authorized closed-corpus completion

The Phase 1 task card below is retained as historical scope. The later user-approved task `context/CLOSED_CORPUS_COMPLETION_TASK.md` explicitly authorized A3, A5, B3, the blocked-audio artifacts under C1–C4, and the 33-source retention decision without adding reference works. That later authorization supersedes the earlier “do not begin A3” stop line only for those named items; A4 and the remaining grammar/routing/forward-test/CI/PR work stay out of scope.

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
- Completed by the later authorized closed-corpus task: A3 deterministic conversion, A5 closure of 13 absent-artifact claims, B3 full report, explicit C1–C4 blocked-audio records, and the 33-source retention register. The working tree contains 30 JSON units, 2,255 Shot/edit units, and 120 non-operational legacy-rule lineage records.
- Validation result: schema syntax, Python compile, converter generation and `--check`, 66 unit/CLI tests, and full Scene Evidence validation pass. The report records 30 passed, 0 failed, 0 errors, and 69 warnings preserved. A fresh final independent read-only review returned PASS with no must-fix issue.
- Known issues: no source replay or direct semantic audio audition; 197 rows lack explicit legacy frame endpoints, 1,944 lack explicit PTS/time base, and 513 high-risk rows lack a source-specific legacy fallback. These values remain visible rather than guessed.
- Successor state: the isolated closed-corpus commit exists. The user-approved 33-source generalization task in `context/THIRD_PARTY_GENERALIZATION_AUDIT_TASK.md` is active; its separate external-action gates remain in force.

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
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/drama-director-compiler/tests -v` — PASS, 66 tests for the completed closed-corpus baseline.
- The legacy-audit table check — PASS: 30 data rows, ten data columns per row, 2,255 Shot/edit units, 120 rules, and 13 broken artifact claims.
- The earlier independent PASS was superseded by a later read-only review that reproduced contact/initiator UNKNOWN leakage and an unauditioned-music directive leakage. Those cases now have paired repository tests and pass locally. A subsequent non-writing read-only reviewer reran the 66-test closed-corpus baseline and issued PASS; later phases require their own fresh review.

Remaining validation boundary: these checks do not replay source media, directly audition audio, prove legacy picture observations, demonstrate audience effect, or constitute creative approval. Thirty canonical conversion JSON units now exist under the later task authorization, but their legacy rules remain non-operational and reference-surface review remains a human boundary before any promotion.

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
| A3 | VERIFIED_DONE | Convert the existing 30 local-source evidence units to schema-valid `scene-evidence.json`, one per work directory. | 30 JSON files pass deterministic converter check and full validator; 2,255 Shot/edit units and 120 legacy-rule lineage records; no new source work. |
| A4 | VERIFIED_DONE | Add deterministic `render_scene_evidence.py`; JSON becomes the sole machine fact source and refreshes a separate generated Markdown summary, shot table, statistics, candidate rules, UNKNOWN, and boundary without overwriting legacy Markdown. | 30/30 generated files pass renderer round-trip/determinism; non-overwrite regression and independent read-only audit pass. |
| A5 | VERIFIED_DONE | Resolve the 13 missing claims found in B99, HOTD, Marriage Story, Mr. Robot, DWP, TLOU, and The Martian by committing rights-safe original analysis artifacts or replacing those references with `scene-evidence.json`. | Regression verifies 13 explicit absence records across seven files, same-stem JSON/report pointers, and zero stale existence claims. |

## B. Reproducible validation

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| B1 | VERIFIED_DONE | Add `validate_scene_evidence.py` covering schema, shot identity/timing, provenance, UNKNOWN leakage, rule references/boundaries, HIGH-risk fallback, surface-copy guards, and public-repository prohibitions. | Repair code rejects the repository's scoped UNKNOWN-rule, same-sentence sound-directive, HEIC/SSA, data-payload, and credential-format cases while preserving explicit safe boundaries; broad unlisted semantic paraphrase remains human-reviewed. |
| B2 | VERIFIED_DONE | Add minimum tests: valid evidence, gap, overlap, missing Shot ref, UNKNOWN promotion, HIGH without fallback, missing non-applicability, single-source GENERAL_DEFAULT, audio rule without observed audio, and reference-surface leakage. | 66/66 unit and CLI tests pass, including migration, legacy-lineage, frame/PTS, fallback, path-scrub, and artifact-closure regressions; fresh independent review passed. |
| B3 | VERIFIED_DONE | Validate all 30 Scene Evidence JSON files and write `research/validation/scene-evidence-validation.json` with errors and warnings preserved. | `passed=30`, `failed=0`, `error_count=0`, `warning_count=69`; warning rows remain visible. |
| B4 | VERIFIED_DONE | Remove or replace unreproducible validation claims and independent-pass statements without command, versioned validator, and repository report. | Claim register maps current claims to commands and reports; 77-test full suite and independent Phase 1 audit pass. |

## C. Multimodal evidence boundaries

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| C1 | VERIFIED_DONE | Separate `PICTURE_OBSERVED`, `AUDIO_OBSERVED`, `TEXT_ANCHOR`, `INFERRED`, and `UNKNOWN`; text anchors cannot prove picture, performance, edit, composition, or mix. | Converted corpus, schema restrictions, validator, and regression tests preserve the separation; text anchors remain unused in this migration. |
| C2 | VERIFIED_DONE | Add the required audio-audit fields: overlap, silence, ambience, score in/out, sound-before-image, offscreen sound, bridge, subjective sound, object sound, information change, and unknowns. | All 30 converted units contain the complete audit structure with explicit unknown/blocked values. |
| C3 | VERIFIED_DONE | Directly audit the eight audio-priority scenes, or mark `BLOCKED_DIRECT_AUDITION`, suppress audio rules, and emit a one-time human audio review sheet. | Authorized blocked branch used: 29 `BLOCKED_DIRECT_AUDITION`, one signal-only unit, 30-row timecoded human review sheet; no semantic audio rule is authorized. |
| C4 | VERIFIED_DONE | Keep Sound of Metal at `SIGNAL_MEASURED_NOT_AUDITIONED`; hearing loss, tinnitus, subjective hearing, source, information access, emotion, and audience effect remain unproven; audio rules remain blocked until direct audition. | Scene JSON, validator, converter test, and audio sheet agree. |

## D. Abstract roles and scene problems

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| D1 | VERIFIED_DONE | Add functional role labels alongside appearance aliases; roles require scene facts or text anchors and otherwise remain UNKNOWN. | Corpus-wide audit finds no evidence-backed role label; all 2,255 empty role-label arrays and 120 empty candidate-role arrays remain explicit non-claims. Validator rejects unsupported, fake-ref or hardened UNKNOWN roles; final independent Phase 2 review PASS. |
| D2 | VERIFIED_DONE | Use one canonical `scene_problem` primary enum and at most two secondary values; do not create work-specific synonyms. | Candidate schema reuses one enum; all 30 current classifications remain canonical `LEGACY_SCENE_PROBLEM / UNKNOWN`, with no secondary synonym or proving source ref; final independent Phase 2 review PASS. |

## E. Candidate-rule normalization

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| E1 | VERIFIED_DONE | Add `candidate-director-rule.schema.json` with the complete required rule contract. | Strict candidate schema is applied to all 120 instances; nested audio/risk/fallback, support, applicability, counterexample, forward-test and human-review records validate; final independent Phase 2 review PASS. |
| E2 | VERIFIED_DONE | Split `within_source_confidence`, `transfer_confidence`, and `execution_confidence`. | All 120 normalized candidates contain exactly the three confidence axes; every current value remains `UNKNOWN`; legacy scalar text appears only inside preserved lineage; final independent Phase 2 review PASS. |
| E3 | VERIFIED_DONE | Build `research/grammar/candidate_rule_index.json`, group synonyms into canonical families, preserve lineage, and label SUPPORTS/NARROWS/CONTRADICTS/COUNTEREXAMPLE/DUPLICATE. | Deterministic builder resolves all 120 unique source IDs exactly once into 16 families and preserves every legacy field; two candidate-by-candidate read-only passes accepted 80 assignments and corrected 40 keyword collisions; family assignment is explicitly not promotion evidence; final independent Phase 2 review PASS. |
| E4 | VERIFIED_DONE | Build the cross-work support matrix in JSON and Markdown. | Deterministic JSON and generated Markdown match across 16 families and 120 candidates; final independent Phase 2 review PASS. |
| E5 | VERIFIED_DONE | Require real same-trigger contrary evidence before promotion; `counterexample UNKNOWN` cannot support promotion. | Validator recounts only cited same-family, unrelated-work, `VERIFIED_SAME_TRIGGER` records backed by a structured named review; declared counts and the hypothetical Martian boundary cannot self-promote; current verified count is zero; final independent Phase 2 review PASS. |

## F. Promotion discipline

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| F1 | VERIFIED_DONE | Restrict `promotion_status` to SINGLE_WORK_CANDIDATE, CROSS_WORK_SUPPORTED, GENERAL_DEFAULT, REJECTED, or BLOCKED_BY_UNKNOWN. | Candidate schema and validator enforce only the five states; final independent Phase 2 review PASS. |
| F2 | VERIFIED_DONE | Keep complete one-work rules at SINGLE_WORK_CANDIDATE and outside runtime defaults. | Negative regression proves a one-work candidate cannot set runtime authorization; final independent Phase 2 review PASS. |
| F3 | VERIFIED_DONE | CROSS_WORK_SUPPORTED requires two unrelated works, same trigger, a real contrary/boundary case, and no hidden key UNKNOWN. | Family work count is never accepted as support. Validator derives support count only from cited same-family records with an exact structured review, recounts contrary cases, derives four UNKNOWN axes and rejects forged IDs/refs/counts/path traversal; final independent Phase 2 review PASS. |
| F4 | VERIFIED_DONE | GENERAL_DEFAULT requires three unrelated works, same-trigger counterexample, two original forward tests, and human director approval. | Counts are recomputed from distinct confined packages and exact manifests; approval requires a confined exact JSON record; traversal, type confusion, token and ID-reuse attacks fail; final independent Phase 2 review PASS. |
| F5 | VERIFIED_DONE | Block rules dependent on UNKNOWN audio, role function, or natural-scene boundary. | Explicit derived dependency axes and negative tests block audio, role and natural-boundary UNKNOWN; all 120 current candidates remain blocked and runtime-authorized count is zero; final independent Phase 2 review PASS. |

## G. General Director Grammar v0.2

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| G1 | VERIFIED_DONE | Add `research/grammar/director_grammar_v0.2.json` containing only CROSS_WORK_SUPPORTED, GENERAL_DEFAULT, and required project/safety constraints. | Grammar validator independently recounts the eligible set and passes with five project constraints, six safety constraints, zero evidence rules, and no single-work runtime default; Phase 3 independent review PASS. |
| G2 | VERIFIED_DONE | Include the complete v0.2 rule field contract. | Strict grammar schema and validator cover applicability, triggers, required facts, non-applicability, confidence, audio dependency, risk/fallback, conflict priority, evidence lineage, routing review and authorization; positive/negative contract tests pass. |
| G3 | VERIFIED_DONE | Remove reference-work-driven operational wording; work names may appear only in evidence lineage. | Full and short work-title plus evidence-ID surface scans pass outside confined lineage; the independent review reproduced the short-title attack and confirmed rejection. |

## H. `drama-director-compiler` routing

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| H1 | VERIFIED_DONE | Update the Skill with locked facts -> dramatic structure -> scene problem -> eligible rules -> 0-4 selections -> conflict resolution -> Director IR -> validation -> human review. | Skill contract follows the required order, permits zero only as `NO_APPLICABLE_RULE`, embeds the routing result in Grammar v0.2 IR, and keeps every unreviewed result at `HUMAN_REVIEW_PENDING`; routing and IR tests pass. |
| H2 | VERIFIED_DONE | Implement the fixed nine-level conflict priority from locked facts through provider limitations. | Grammar schema, router and conflict-order tests enforce the exact nine-level sequence; independent review confirms lower-priority rules cannot override higher-priority constraints. |
| H3 | VERIFIED_DONE | Check trigger, required facts, non-applicability, conflicts, and subject-matter similarity misuse. | Negative routing tests reject missing/empty required-fact mappings, non-applicability hits, conflicts, subject-only matches and forged authority; Phase 3 independent review PASS. |
| H4 | VERIFIED_DONE | Add routing tests for power dialogue, fracture, public reveal, procedure, action, proximity, sound suspense, and no-applicable-rule; select at most 2-4 when applicable, allow zero, and copy no surface element. | Eight rights-safe original routing cases pass through the real CLI; the current zero-rule grammar returns eight truthful `NO_APPLICABLE_RULE` results and zero selected rules without padding. |

## I. Project-original forward tests

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| I1 | VERIFIED_DONE | Create rights-safe original test scripts for six required scene problems without rewriting reference plots. | Eight original packages cover the six explicit task-card problems plus relationship-fracture and no-specialized-rule probes; automated surface guards and a fresh independent read-only content review found no evident reference-surface or plot rewrite. Absolute originality remains a human/legal boundary. |
| I2 | VERIFIED_DONE | Run a positive and boundary/non-applicable case for every promotion-ready family. | The validator live-recounts zero promotion-ready families, zero required pairs, zero positive/boundary claims and zero missing families. All eight packages are truthfully labeled `ZERO_ELIGIBLE_PROBE`; any future eligible family makes this coverage fail until distinct positive and boundary packages exist. |
| I3 | VERIFIED_DONE | Emit each required `examples/forward-tests/<case-id>/` package. | Eight packages contain every required artifact plus reproducible manifests/routing inputs; live Grammar -> router -> complete IR -> renderer -> package/report binding passes deterministically. |
| I4 | VERIFIED_DONE | Mark unreviewed output `HUMAN_REVIEW_PENDING`; never label it production-ready or a winner. | All eight manifests, routing results, IRs and exact review records remain `HUMAN_REVIEW_PENDING`; generation/publication stay false and contradictory appended approvals fail validation. |

## J. State and single source of truth

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| J1 | VERIFIED_DONE | Reduce `context/STATE.md` to phase, counts, blockers, latest validation, next step, and authoritative links. | STATE is 65 lines with no per-work duplication; state-contract tests and independent review pass. |
| J2 | VERIFIED_DONE | Declare the five intended authoritative locations and whether each is active or planned: Scene JSON, candidate index, support matrix, Grammar v0.2, and STATE. | STATE declares all five without pretending planned artifacts exist; state-contract test passes. |
| J3 | VERIFIED_DONE | Make acquisition and coverage files material catalogs only, not simultaneous status/rule/completion authorities. | Five catalog boundary headers and responsibility tests pass; independent review confirms no competing authority claim. |

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
| M1 | VERIFIED_DONE | Deliver 30+ Scene Evidence JSON files. | Closed-corpus requirement is exactly 30 current-local JSON files; deterministic count validation passes. |
| M2 | VERIFIED_DONE | Deliver Scene Evidence schema, validator, and renderer. | Phase 1 tests, deterministic reports and independent review pass. |
| M3 | VERIFIED_DONE | Deliver Candidate Rule schema/index and cross-work matrix JSON/Markdown. | Phase 2 rule/matrix validation and final independent review pass. |
| M4 | VERIFIED_DONE | Deliver Director Grammar v0.2 and updated Skill routing/conflict logic/tests. | Grammar/routing schemas, validators, eight cases, IR integration tests and Phase 3 independent review pass. |
| M5 | VERIFIED_DONE | Deliver original forward-test packages. | Eight deterministic packages, six required problem tags, zero false positive selections, 31 preserved visual-binding warnings and Phase 4 independent review PASS. |
| M6 | TODO | Deliver full validation, independent audit, reduced STATE, clean Succession integration, CI, and updated PR description. | Checklist contains no TODO/IN_PROGRESS/BLOCKED item; user decides whether to merge. |

## Current blockers and known defects

- The 30 JSON units are deterministic machine-readable conversions, but legacy candidate semantics remain non-operational lineage pending human review.
- Explicit frame/PTS and legacy fallback gaps remain visible; converter warnings prohibit treating provisional values as source-proven facts.
- The known 13 absent legacy artifacts are closed as explicit absence records; broader historical claims outside this closed register were not re-proved.
- Direct semantic audio audition is absent; signal measurement is not semantic sound evidence.
- PR #1 cannot be merged unchanged because it contains prohibited media-hash material and older evidence semantics.
- The runtime grammar is active but correctly contains zero evidence rules because none of the 120 candidates passes the promotion gates; all eight original packages therefore prove the no-ready/no-applicable branch, while a real positive selection remains unproved until evidence becomes eligible.

## Current next action

Integrate the existing 88-shot *Succession* evidence through the current Scene Evidence, candidate-index and support-matrix contracts without merging or closing the older PR. Do not push, close a PR, merge, deploy, publish, or delete media.
