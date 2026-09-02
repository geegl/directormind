# Validation Claim Register

Updated: 2026-09-02

Status: `FINAL_LOCAL_PASS / REMOTE_IMPLEMENTATION_CI_PASS / FINAL_REVIEW_PENDING`

This register is the reproducible source for current numerical pass claims. A
command is evidence only for the boundary named in its row. Structural checks do
not prove that the source-film observations are correct, do not directly audit
sound, and do not constitute creative approval.

| Claim | Reproduction command | Versioned evidence | Current result | Boundary |
|---|---|---|---|---|
| Canonical conversion is deterministic | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/convert_legacy_scene_evidence.py --check` | `convert_legacy_scene_evidence.py` and its tests | PASS — 31 scenes, 2,343 Shot/edit units, 124 candidate identities | Proves generated JSON equals the conservative migration input; does not replay media |
| Generated review Markdown is deterministic and round-trippable | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/render_scene_evidence.py --check` | `render_scene_evidence.py`, 31 `*.scene-evidence.generated.md` files and renderer tests | PASS — 31/31 generated files | Proves generated review fields equal canonical JSON and re-render identically |
| Legacy Markdown is not overwritten by rendering | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest skills/drama-director-compiler/tests/test_render_scene_evidence.py -v` | Renderer non-overwrite regression | PASS | Compares all existing Markdown before and after temporary rendering |
| Current repository unit/CLI behavior | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/drama-director-compiler/tests -v` | Nine versioned test modules | PASS — 223 tests | Covers the current repository test surface; not source replay or audience evaluation |
| Candidate normalization is deterministic | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/build_candidate_rule_index.py --check` | Candidate index, support matrix JSON/Markdown, builder and family reviews | PASS — 124 candidates in 16 reviewed textual mechanism families; 44 explicit reviewed overrides | Family membership is textual similarity only and cannot authorize runtime use |
| Candidate promotion gates | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_candidate_rules.py --report research/validation/candidate-rule-validation.json` | Candidate schema, validator, report and adversarial tests | PASS — 124 blocked, 0 runtime-authorized, 0 errors | Work, counterexample and test counts are independently recomputed from cited records; no UNKNOWN fact is inferred |
| Candidate schema syntax | `python3 -m json.tool skills/drama-director-compiler/references/candidate-director-rule.schema.json` | Candidate Director Rule schema | PASS | JSON syntax plus repository contract tests; third-party schema engine not required |
| Runtime grammar eligibility and safety | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_director_grammar.py --report research/validation/director-grammar-validation.json` | Grammar v0.2, strict schema, validator and report | PASS — 5 project constraints, 6 safety constraints, 0 eligible/runtime evidence rules, 0 errors | Independently recounts candidate eligibility and blocks single-work, UNKNOWN, surface-copy and unauditioned-audio instructions |
| Runtime routing cases | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_director_routing_cases.py --report research/validation/director-routing-validation.json` | Rights-safe input/result schemas, router, eight fixtures and report | PASS — 8/8 cases, 8 `NO_APPLICABLE_RULE`, 0 selected rules | Proves honest zero-rule behavior and routing gates; does not prove a real positive selection because no candidate is eligible |
| Director IR compatibility and upgrade boundary | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest skills.drama-director-compiler/tests/test_director_grammar_routing.py skills/drama-director-compiler/tests/test_director_ir_compatibility.py -v` | Canonical enum/sentinel behavior, Grammar-bound routing results, malformed-type rejection, version-scoped legacy GO triggers, two upgrade modes, non-overwrite guard, audio validator/renderer regressions | PASS — 45 tests | Proves local contract behavior on synthetic/fixture IR; does not migrate or modify private Director IR and does not make legacy audio executable |
| Original forward-test build | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/build_forward_tests.py --check` | Eight packages under `examples/forward-tests/` and deterministic builder | PASS — 8/8 packages match generated sources | Proves artifact determinism; package validation remains a separate claim |
| Original forward-test repository | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_forward_tests.py --check` | Index schema, live validator and `forward-test-validation.json` | PASS — 6 required problems, 8 packages, 0 eligible families, 0 selected, 8 pending, 0 errors, 31 warnings | Proves the no-ready/no-applicable route and complete IR binding; does not claim a positive rule selection or creative approval |
| Canonical Scene Evidence structure | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_scene_evidence.py research/evidence --quiet` | Validator `scene-evidence-validator/0.1` and `scene-evidence-validation.json` | PASS_STRUCTURAL — 31 passed, 0 failed, 0 errors, 72 warnings | Warnings remain visible; no direct semantic-audio claim is added |
| Scene Evidence schema syntax | `python3 -m json.tool skills/drama-director-compiler/references/scene-evidence.schema.json` | Scene Evidence schema | PASS | JSON syntax only |
| Versioned validation report syntax | `python3 -m json.tool research/validation/scene-evidence-validation.json` | Structural validation report | PASS | JSON syntax only |
| Current task/status authority contract | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/drama-director-compiler/tests -p test_phase1_state_contract.py -v` | Approved task card, compact STATE, catalog headers and checklist | PASS — 5 tests | Confirms current counts/catalog route and bounded external authorization |
| Repository boundary audit | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_repository_boundaries.py --quiet` | Boundary validator and automation tests | PASS — zero whole-repository file/syntax/link issues and zero current-machine/runtime scoped string issues | Original 30 immutable legacy Markdown ledgers are explicitly excluded provenance; no whole-repository zero-string claim is made |
| Final validation report | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/run_repository_checks.py` | Strict `final-generalization-validation/0.4` schema, live runner evidence and deterministic JSON | PASS_LOCAL — 33 dispositions, 31 scenes, 2,343 units, 124 candidates, 16 families, 223 tests, zero validation errors and 103 preserved warnings | A missing or failed prerequisite produces `FAIL_LOCAL`; the versioned report does not self-attest post-commit PR state or remote CI |
| Complete local automation | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/run_repository_checks.py` | Local runner, all builders/validators, temporary report comparison, tests and final report | PASS — 18 checks | Local CI-equivalent execution; does not claim a GitHub-hosted run |
| Minimal CI definition | `.github/workflows/directormind-contracts.yml` | Read-only workflow calling the complete local runner | PASS_REMOTE_IMPLEMENTATION_HEAD | First run exposed Python 3.9/3.12 sum drift; after decimal summation and cross-runtime reproduction, the corrective hosted run passed. Final documentation head remains separately gated |
| Whitespace | `git diff --check` | Current local change set | PASS | Tracked textual diff only |

## Final independent review

The first final audit rejected three evidence defects. After correction, a non-writing reviewer reran the full 18-check command, confirmed the then-current 157 tests, independently reproduced the final counts and injected failure into each of the 17 live prerequisites. Every failure produced `FAIL_LOCAL`; missing live evidence also failed. That historical verdict remains unchanged. A later compatibility repair was reviewed by three fresh non-writing agents: their first round found real route, migration, audio, type and overwrite gaps; after correction they replayed those attacks and issued `PASS_LOCAL / NO_MUST_FIX_FINDINGS`. The compatibility snapshot remains recorded in `COMPATIBILITY_REPAIR_INDEPENDENT_AUDIT.md`; the current combined suite contains 223 tests.

## Independent Phase 1 review

`research/validation/PHASE_1_INDEPENDENT_AUDIT.md` records the fresh
non-writing review. It independently reproduced the 77-test suite, renderer and
converter checks, structural validation, non-overwrite boundary and artifact
scans against the frozen Phase 1 snapshot.

## Independent Phase 2 review

`research/validation/PHASE_2_INDEPENDENT_AUDIT.md` records two failed frozen
snapshots, their narrow corrections and the final fresh non-writing PASS. The
reviewer independently replayed forged-count, provenance, type-confusion,
parent-traversal, link-escape, token-substring and ID-reuse attacks.

## Independent Phase 3 review

`research/validation/PHASE_3_INDEPENDENT_AUDIT.md` records the fresh
non-writing PASS. The reviewer independently replayed empty required-fact
mapping, short work-title leakage, omitted/dropped IR routing results and
unauditioned-audio instruction attacks, then reran the targeted and full suites.

## Independent Phase 4 review

`research/validation/PHASE_4_INDEPENDENT_AUDIT.md` records the fresh non-writing
PASS. The reviewer read all eight original scripts and replayed false-positive,
private-path, fact-drift, work-title, approval, audio-loss and JSON Unicode-escape
attacks against the complete Grammar-to-IR package chain.

## Phase 5 local migration

`research/validation/PHASE_5_SUCCESSION_MIGRATION.md` records the additive
88-unit migration, frozen original ordinal allocations, four explicit family
assignments, current-route catalog updates and local checks.
`research/validation/PHASE_5_INDEPENDENT_AUDIT.md` records the fresh non-writing
PASS and independently reproduces the no-drift, UNKNOWN/audio/runtime, count,
rights and external-action boundaries.

## Remaining evidence boundaries

- No candidate is an executable cross-work rule; the active runtime grammar therefore contains zero evidence rules.
- No real positive routing selection is claimed; all current forward-test packages exercise the honest zero-eligible branch.
- No source media, semantic audio, creative quality or audience effect has been
  revalidated by these commands.
- PR #3 remains open and unmerged. PR #1 was closed without merge after successful integration and hosted CI. The final PR #3 documentation head still requires hosted CI.
