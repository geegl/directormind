# Phase 1 Validator Independent Audit

Date: 2026-09-02  
Scope: Phase 1 Scene Evidence validator B1/B2 only  
Audited implementation commit: `40c7aa2`  
Independent reviewer: `phase1_final_acceptance_40c7aa2`  
Verdict: `PASS_LOCAL / NO_MUST_FIX_FINDINGS`

## Scope and method

The reviewer inspected a clean, fixed commit and made no repository changes. Counterexamples were replayed in memory or in automatically cleaned temporary directories. The review did not migrate legacy evidence, add reference works, merge `main`, replay source media, or directly audition audio.

Exit-code contract:

- `0`: structurally valid input or safe positive boundary.
- `1`: invalid Scene Evidence rejected.
- `2`: validator setup, protected-output, Schema, or report-write failure.

## Counterexample results

| P1 area | Replayed counterexample or positive control | Expected and actual exit code |
|---|---|---:|
| Auxiliary provenance | `PICTURE_OBSERVED`, `AUDIO_OBSERVED`, `TEXT_ANCHOR`, or `INFERRED` with empty `source_refs` | `1` |
| Auxiliary provenance | Method-only source, self/cyclic source, UNKNOWN source, or valid source mixed with an incompatible source | `1` |
| Auxiliary provenance | Each of the four supported statuses recursively reaches its compatible real evidence track | `0` |
| Strict boolean `const` | A protected boolean field is supplied as `0`, `1`, or a string | `1` |
| Schema authority | A caller Schema weakens or coerces a protected boolean `const` | `2` |
| Schema authority | The canonical Schema copy is empty, malformed, weakened, or changes `false` to `0` | `2` |
| Boundary cross-check | A definite boundary cites UNKNOWN boundary evidence | `1` |
| Boundary cross-check | First or last Shot is omitted, or is reached only through an UNKNOWN continuity track | `1` |
| Boundary cross-check | `boundary_status`, `scene_unit_type`, or first/last Shot completeness conflict | `1` |
| Boundary cross-check | The supported definite/selected/unknown boundary matrix is internally consistent | `0` |
| Text anchors | Duplicate `anchor_id` | `1` |
| Text anchors | `TEXT_ANCHOR_UNKNOWN` directly supports Claim, Scene Problem, or Role | `1` |
| Text anchors | A valid Shot is mixed with `TEXT_ANCHOR_UNKNOWN` for Claim, Scene Problem, or Role | `1` |
| Text anchors | A text source is used without an active `TEXT_ANCHOR_REVIEW` method | `1` |
| UNKNOWN leakage | Each of the five UNKNOWN arrays hides a fact after uncertainty with punctuation or conjunction variants | `1` for every array |
| UNKNOWN leakage | Each of the five UNKNOWN arrays states a picture fact before uncertainty, including `on screen`, `in-frame`, and `frame left` variants | `1` for every array |
| UNKNOWN leakage | Each of the five UNKNOWN arrays asserts the same identity across a cut | `1` for every array |
| UNKNOWN leakage | Each of the five UNKNOWN arrays hides an unauditioned audio instruction | `1` for every array |
| Safe UNKNOWN boundary | `Do not add a score.` | `0` for every array |
| Safe UNKNOWN boundary | `Identity remains unknown and cannot be confirmed from picture.` | `0` for every array |
| Safe UNKNOWN boundary | `Audio remains unknown and was not directly auditioned.` | `0` for every array |
| Single-token UNKNOWN | A rule restates `Vehicle remains unknown` as `Use the vehicle on screen`, before or after the uncertainty phrase | `1` |
| Audio directives | `bring in`, `bringing in`, or imperative `track` is used without direct audition | `1` |
| Audio directives | A safe negative masks a later directive through comma, `and`, `or`, `plus`, `before`, `instead`, `rather than`, colon, slash, or dash | `1` |
| Safe audio wording | Standalone `do not add a score` and noun phrase `audio track remains unknown` | `0` |
| Public boundary | A JSON key or value contains an absolute path, media/subtitle filename, data URI, release label, or credential material | `1` |
| Public boundary | Exact, prefixed, hyphenated, snake-case, or camel-case credential labels are used as measurement keys | `1` |
| Public boundary | Ordinary `synthetic_level` and `token_count` measurement keys | `0` |
| Report safety | `--report` aliases an input, caller Schema, or canonical Schema by exact path, symlink, or filesystem case alias | `2` |
| Report safety | Atomic report creation/replacement fails | `2` |
| CLI behavior | `--quiet` with valid input and writable report | `0` |
| CLI behavior | Directory discovery finds and validates the repository-file fixture | `0` |
| CLI behavior | Wrong or non-canonical Schema | `2` |
| Integration fixture | `tests/fixtures/repository-integration.scene-evidence.json` | `0` |

## Required checks

| Command | Exit code | Result |
|---|---:|---|
| `python3 -m json.tool skills/drama-director-compiler/references/scene-evidence.schema.json` | `0` | PASS |
| `python3 -m py_compile skills/drama-director-compiler/scripts/validate_scene_evidence.py` | `0` | PASS |
| `python3 -m unittest discover -s skills/drama-director-compiler/tests -v` | `0` | PASS, 90 tests |
| `git diff --check` | `0` | PASS |

The reviewer confirmed `HEAD=40c7aa2` and a clean worktree before and after the audit.

## Remaining boundaries

- Structural validation does not prove that legacy film/television observations are correct.
- Source media was not replayed and semantic audio was not directly auditioned.
- Creative quality, audience response, and human director approval were not tested.
- A3 migration, later generalization phases, remote CI, merge, deployment, and release were not performed.

## Rollback

Before merge, revert the Phase 1 validator commits and the final status/report commit with ordinary Git revert commits. Do not rewrite shared history. No source media, production data, credentials, accounts, permissions, payments, or remote production systems were changed.
