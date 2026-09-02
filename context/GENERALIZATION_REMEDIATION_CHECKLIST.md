# DirectorMind Generalization Remediation Checklist

Updated: 2026-09-02

## 2026-09-01 authorized closed-corpus completion

The Phase 1 task card below is retained as historical scope. Later user-approved
tasks authorized the closed-corpus A3–M implementation without adding reference
works. On 2026-09-02 the user confirmed the new Phase 1 re-review verdict
`PASS_LOCAL / NO_MUST_FIX_FINDINGS`, authorized continuation through every
remaining checklist item, authorized corrective pushes to PR #3 and authorized
closing PR #1 after successful integration and CI. Merging `main` remains
prohibited.

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
- [x] The repaired repository validator implements every B1 gate planned for canonical JSON and passes the reopened reproduction matrix.
- [x] The combined tests cover recursive provenance, UNKNOWN leakage, boundary/anchor cross-checks, CLI safety and precise error paths.
- [x] Existing evidence content and unrelated functionality remain unchanged.
- [x] Commands, remaining risks, and rollback are recorded.

### 6. Current status

- Current sole implementer/writer: `/root`; prior sub-agents performed read-only corpus and validator reviews only.
- Completed before this repair: checklist, 30-file audit report, Scene Evidence schema, standard-library validator, and 45 validator tests.
- Phase 1 re-review status: `INDEPENDENT_RE_REVIEW_PASSED`; no P0, P1 or P2 finding remains. B1 and B2 stay `VERIFIED_DONE`.
- Completed by later closed-corpus work: A3–M local implementation, including 31 canonical Scene Evidence units, 2,343 Shot/edit units, 124 blocked candidate identities, deterministic rendering, Grammar/routing, eight original forward-test packages, Succession migration, local automation and compatibility repair.
- Integration status: the latest Phase 1 repair and the later local work are being combined on PR #3; complete post-merge validation and remote CI remain required before closure.
- Known boundaries: no source replay or direct semantic audio audition; all current candidate rules remain blocked and runtime authorization remains zero.

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
- `python3 -m py_compile skills/drama-director-compiler/scripts/validate_scene_evidence.py` — PASS.
- The isolated Phase 1 suite passed 96 tests before integration; the complete combined-suite result is recorded by the repository runner after integration.
- Repository integration fixture through the Scene Evidence CLI — PASS.
- Direct `NATURAL_START_END_VERIFIED` plus `boundary_evidence.status=INFERRED` replay — rejected with return code `1`.
- The new independent Phase 1 re-review found no remaining P0, P1 or P2 issue.
- The legacy-audit table check — PASS: 30 data rows, ten data columns per row, 2,255 Shot/edit units, 120 rules, and 13 broken artifact claims.

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
| B1 | VERIFIED_DONE | Add `validate_scene_evidence.py` covering schema, shot identity/timing, provenance, UNKNOWN leakage, rule references/boundaries, HIGH-risk fallback, surface-copy guards, and public-repository prohibitions. | Four definite boundary states require recursively grounded `PICTURE_OBSERVED` evidence; UNKNOWN, audio, anchor, public-boundary and compatibility guards remain active; independent re-review found no P0/P1/P2. |
| B2 | VERIFIED_DONE | Add minimum tests: valid evidence, gap, overlap, missing Shot ref, UNKNOWN promotion, HIGH without fallback, missing non-applicability, single-source GENERAL_DEFAULT, audio rule without observed audio, and reference-surface leakage. | Phase 1's 96-test matrix includes auxiliary, boolean, canonical-Schema, boundary, anchor, public-boundary, symlink and atomic-report coverage; it is retained in the combined repository suite. |
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
| D1 | VERIFIED_DONE | Add functional role labels alongside appearance aliases; roles require scene facts or text anchors and otherwise remain UNKNOWN. | Corpus-wide audit finds no evidence-backed role label; all 2,343 empty role-label arrays and 124 empty candidate-role arrays remain explicit non-claims. Validator rejects unsupported, fake-ref or hardened UNKNOWN roles; Phase 2 baseline and Phase 5 migration checks pass. |
| D2 | VERIFIED_DONE | Use one canonical `scene_problem` primary enum and at most two secondary values; do not create work-specific synonyms. | Seven runtime-facing schemas now expose the identical 18-value enum, including the explicit `NO_SPECIALIZED_PROBLEM` negative sentinel. Eight routing fixtures use canonical names, unknown primary/secondary values fail before routing, and a parity regression prevents schema drift. All 31 evidence classifications remain honest `LEGACY_SCENE_PROBLEM / UNKNOWN`. |

## E. Candidate-rule normalization

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| E1 | VERIFIED_DONE | Add `candidate-director-rule.schema.json` with the complete required rule contract. | Strict candidate schema is applied to all 124 instances; nested audio/risk/fallback, support, applicability, counterexample, forward-test and human-review records validate. |
| E2 | VERIFIED_DONE | Split `within_source_confidence`, `transfer_confidence`, and `execution_confidence`. | All 124 normalized candidates contain exactly the three confidence axes; every current value remains `UNKNOWN`; legacy scalar text appears only inside preserved lineage. |
| E3 | VERIFIED_DONE | Build `research/grammar/candidate_rule_index.json`, group synonyms into canonical families, preserve lineage, and label SUPPORTS/NARROWS/CONTRADICTS/COUNTEREXAMPLE/DUPLICATE. | Deterministic builder resolves all 124 unique source IDs exactly once into 16 families and preserves every legacy field; the original 120 assignments remain unchanged and the four *Succession* assignments are explicit reviewed overrides; family assignment is not promotion evidence. |
| E4 | VERIFIED_DONE | Build the cross-work support matrix in JSON and Markdown. | Deterministic JSON and generated Markdown match across 16 families and 124 candidates; all relations remain non-promotional. |
| E5 | VERIFIED_DONE | Require real same-trigger contrary evidence before promotion; `counterexample UNKNOWN` cannot support promotion. | Validator recounts only cited same-family, unrelated-work, `VERIFIED_SAME_TRIGGER` records backed by a structured named review; declared counts and the hypothetical Martian boundary cannot self-promote; current verified count is zero; final independent Phase 2 review PASS. |

## F. Promotion discipline

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| F1 | VERIFIED_DONE | Restrict `promotion_status` to SINGLE_WORK_CANDIDATE, CROSS_WORK_SUPPORTED, GENERAL_DEFAULT, REJECTED, or BLOCKED_BY_UNKNOWN. | Candidate schema and validator enforce only the five states; final independent Phase 2 review PASS. |
| F2 | VERIFIED_DONE | Keep complete one-work rules at SINGLE_WORK_CANDIDATE and outside runtime defaults. | Negative regression proves a one-work candidate cannot set runtime authorization; final independent Phase 2 review PASS. |
| F3 | VERIFIED_DONE | CROSS_WORK_SUPPORTED requires two unrelated works, same trigger, a real contrary/boundary case, and no hidden key UNKNOWN. | Family work count is never accepted as support. Validator derives support count only from cited same-family records with an exact structured review, recounts contrary cases, derives four UNKNOWN axes and rejects forged IDs/refs/counts/path traversal; final independent Phase 2 review PASS. |
| F4 | VERIFIED_DONE | GENERAL_DEFAULT requires three unrelated works, same-trigger counterexample, two original forward tests, and human director approval. | Counts are recomputed from distinct confined packages and exact manifests; approval requires a confined exact JSON record; traversal, type confusion, token and ID-reuse attacks fail; final independent Phase 2 review PASS. |
| F5 | VERIFIED_DONE | Block rules dependent on UNKNOWN audio, role function, or natural-scene boundary. | Explicit derived dependency axes and negative tests block audio, role and natural-boundary UNKNOWN; all 124 current candidates remain blocked and runtime-authorized count is zero. |

## G. General Director Grammar v0.2

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| G1 | VERIFIED_DONE | Add `research/grammar/director_grammar_v0.2.json` containing only CROSS_WORK_SUPPORTED, GENERAL_DEFAULT, and required project/safety constraints. | Grammar validator independently recounts the eligible set and passes with five project constraints, six safety constraints, zero evidence rules, and no single-work runtime default; Phase 3 independent review PASS. |
| G2 | VERIFIED_DONE | Include the complete v0.2 rule field contract. | Strict grammar schema and validator cover applicability, triggers, required facts, non-applicability, confidence, audio dependency, risk/fallback, conflict priority, evidence lineage, routing review and authorization. The IR-embedded routing result now matches the standalone formal result contract field-for-field; deletion of any required field fails regression. |
| G3 | VERIFIED_DONE | Remove reference-work-driven operational wording; work names may appear only in evidence lineage. | Full and short work-title plus evidence-ID surface scans pass outside confined lineage; the independent review reproduced the short-title attack and confirmed rejection. |

## H. `drama-director-compiler` routing

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| H1 | VERIFIED_DONE | Update the Skill with locked facts -> dramatic structure -> scene problem -> eligible rules -> 0-4 selections -> conflict resolution -> Director IR -> validation -> human review. | Skill contract follows the required order, permits zero only as a complete `NO_APPLICABLE_RULE` result, embeds the canonical input and full result in Grammar v0.2 IR, replays that route through the active Grammar, and keeps every unreviewed result pending. Legacy upgrade is explicitly split into a safe human-pause mode and an evidence-complete v0.2 routed mode. |
| H2 | VERIFIED_DONE | Implement the fixed nine-level conflict priority from locked facts through provider limitations. | Grammar schema, router and conflict-order tests enforce the exact nine-level sequence; independent review confirms lower-priority rules cannot override higher-priority constraints. |
| H3 | VERIFIED_DONE | Check trigger, required facts, non-applicability, conflicts, and subject-matter similarity misuse. | Negative routing tests reject missing/empty required-fact mappings, non-applicability hits, conflicts, subject-only matches and forged authority. IR validation replays the embedded canonical input, binds its dramatic structure and ordered facts back to scene/Shot data, and rejects cross-scene result substitution, incomplete results, count/eligibility/handoff drift, selected-rule binding drift and v0.2 use of legacy seed IDs. |
| H4 | VERIFIED_DONE | Add routing tests for power dialogue, fracture, public reveal, procedure, action, proximity, sound suspense, and no-applicable-rule; select at most 2-4 when applicable, allow zero, and copy no surface element. | Eight rights-safe original routing cases use canonical problem names and pass through the real CLI; the current zero-rule grammar returns eight truthful `NO_APPLICABLE_RULE` results and zero selected rules without padding. A synthetic canonical problem still proves that an eligible matching rule can be selected. |

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
| J1 | VERIFIED_DONE | Reduce `context/STATE.md` to phase, counts, blockers, latest validation, next step, and authoritative links. | STATE remains below the tested 100-line compact-state limit with no per-work duplication; state-contract tests and independent review pass. |
| J2 | VERIFIED_DONE | Declare the five intended authoritative locations and whether each is active or planned: Scene JSON, candidate index, support matrix, Grammar v0.2, and STATE. | STATE declares all five without pretending planned artifacts exist; state-contract test passes. |
| J3 | VERIFIED_DONE | Make acquisition and coverage files material catalogs only, not simultaneous status/rule/completion authorities. | Five catalog boundary headers and responsibility tests pass; independent review confirms no competing authority claim. |

## K. Succession / PR #1 integration

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| K1 | VERIFIED_DONE | Do not merge PR #1 unchanged. | Current task explicitly prohibits it; PR #1 remains separate. |
| K2 | VERIFIED_DONE | Cleanly migrate Succession: exclude prohibited media-fingerprint material and authorizing text, retain 88-shot evidence, add Scene JSON, candidate index, and support matrix entries. | 31-scene converter/renderer checks pass; Scene validation is 31/31 with 0 errors; candidate validation is 124/16 with 0 authorized; original 30 evidence files have no diff; fresh Phase 5 independent review PASS. |
| K3 | VERIFIED_DONE | Resolve `SCENE_PROBLEM_MAP.md` conflicts and keep only the current route. | Current authority header is preserved; only the public-revelation and group-power catalog rows receive bounded picture/UNKNOWN updates; the old map was not merged; fresh Phase 5 independent review PASS. |
| K4 | VERIFIED_DONE | Close PR #1 only after current-branch integration succeeds. | PR #1 was closed without merge after 223/223 local tests, 18/18 local checks and PR #3 hosted CI passed. The 88-unit migration remains in the current contracts on PR #3. |

## L. CI and final validation

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| L1 | VERIFIED_DONE | Add minimal GitHub CI for Skill validation, Python compile, all schemas/evidence/rules/grammar/forward tests, broken refs, scoped public-artifact prohibitions and whitespace. | Read-only workflow calls the same stdlib-only local runner with read-only repository permission; corrected quick/full commands and narrow independent re-review pass. Hosted CI is verified live after the final push, not self-attested by the versioned local report. |
| L2 | VERIFIED_DONE | Write `FINAL_GENERALIZATION_VALIDATION.json` with every required count and zero errors, broken refs, prohibited repository files or scoped current-artifact string issues. | Live-runner-backed `final-generalization-validation/0.4` passes its strict schema and records 33/31/2,343/124/16, 225 tests, zero validation errors and 103 preserved warnings. Post-commit PR state is deliberately verified live rather than self-attested. |
| L3 | VERIFIED_DONE | Run quick validation, units, all Scene Evidence, all Grammar, forward tests and whitespace through the local CI-equivalent command. | The integrated 225-test suite and all 18 local CI-equivalent checks pass, including exact comparison of five versioned validator reports and `git diff --check origin/main...HEAD`. The last pushed implementation head passed the hosted workflow; the follow-up repair and final documentation heads remain separately gated by CI under M6. |
| L4 | IN_PROGRESS | Add `INDEPENDENT_GENERALIZATION_AUDIT.md` with verdict, P0/P1, non-blockers, unverified items, and merge decision. | Historical phase audits remain immutable. A fresh non-writing reviewer must inspect the final integrated state after all local and external gates complete. |

## M. Final delivery

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| M1 | VERIFIED_DONE | Deliver 30+ Scene Evidence JSON files. | Current closed-corpus result is 31 JSON files after the in-scope *Succession* migration; deterministic count validation passes. |
| M2 | VERIFIED_DONE | Deliver Scene Evidence schema, validator, and renderer. | Phase 1 tests, deterministic reports and independent review pass. |
| M3 | VERIFIED_DONE | Deliver Candidate Rule schema/index and cross-work matrix JSON/Markdown. | Phase 2 rule/matrix validation and final independent review pass. |
| M4 | VERIFIED_DONE | Deliver Director Grammar v0.2 and updated Skill routing/conflict logic/tests. | Grammar/routing schemas, validators, eight canonical cases, exact input-to-result replay plus scene/fact/Shot binding, v0.1-only GO compatibility, safe non-overwriting upgrader modes, visible legacy-audio handling, and targeted regressions pass locally. |
| M5 | VERIFIED_DONE | Deliver original forward-test packages. | Eight deterministic packages, six required problem tags, zero false positive selections, 31 preserved visual-binding warnings and Phase 4 independent review PASS. |
| M6 | IN_PROGRESS | Deliver full validation, independent audit, reduced STATE, clean Succession integration, CI, and updated PR description. | This closes only after K4 and L2-L4 return to `VERIFIED_DONE`, the final PR #3 description is updated and no TODO/BLOCKED/IN_PROGRESS row remains. |

## Current blockers and known defects

- The 31 JSON units are deterministic machine-readable conversions, but legacy candidate semantics remain non-operational lineage pending human review.
- Explicit frame/PTS and legacy fallback gaps remain visible; converter warnings prohibit treating provisional values as source-proven facts.
- The known 13 absent legacy artifacts are closed as explicit absence records; broader historical claims outside this closed register were not re-proved.
- Direct semantic audio audition is absent; signal measurement is not semantic sound evidence.
- PR #1 was closed without merge because it contained prohibited media-fingerprint material and older evidence semantics; its 88-unit evidence was migrated through the current contracts instead.
- The runtime grammar is active but correctly contains zero evidence rules because none of the 124 candidates passes the promotion gates; all eight original packages therefore prove the no-ready/no-applicable branch, while a real positive selection remains unproved until evidence becomes eligible.
- A final read-only review found that a complete result from another scene could be substituted and that the upgrader could overwrite an unrelated existing output. Both P1s now have local fixes and regression tests; final acceptance remains blocked until the repair is pushed, hosted CI passes and the reviewer independently replays both attacks.

## Current next action

Push the locally passing follow-up P1 repair and require hosted CI success. Then obtain a fresh independent read-only verdict, close L4/M6 only on PASS, validate the final documentation head and stop without merging `main`.
