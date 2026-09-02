# Phase 1 Validator Independent Audit

Date: 2026-09-02
Scope: Phase 1 Scene Evidence validator B1/B2 only
Status: `LOCAL_REPAIR_VERIFIED / INDEPENDENT_RE_REVIEW_PENDING`

## Review finding and repair

The latest independent re-review found one P1 acceptance bypass: a scene with
`boundary_status=NATURAL_START_END_VERIFIED` and
`boundary_evidence.status=INFERRED` was accepted by the CLI with return code
`0`.

The repair now requires `boundary_evidence.status=PICTURE_OBSERVED` for all four
definite boundary states. Recursive boundary provenance must still reach both
endpoint Shots, may not pass through an UNKNOWN continuity track, and must agree
with the first and last Shot completeness values.

No A3 migration, new reference work, source-media replay, direct audio audition,
`main` merge, deployment, or release was performed.

## Direct semantic assertions

The following rows are assertions inside the 96-test unit suite. The result
column records validator report assertions, not process return codes.

| Area | Tested matrix | Asserted result |
|---|---|---|
| Definite boundary status | Each of the four definite states with `INFERRED` evidence | `BOUNDARY-DEFINITE-REQUIRES-PICTURE` error present |
| Definite boundary status | Each of the four definite states with `UNKNOWN` evidence | picture-required and UNKNOWN-boundary errors present |
| Boundary provenance | Picture evidence omits the first endpoint Shot | `BOUNDARY-START-SOURCE-MISSING` error present |
| Boundary provenance | Picture evidence omits the last endpoint Shot | `BOUNDARY-END-SOURCE-MISSING` error present |
| Boundary provenance | Endpoint is reached only through an UNKNOWN continuity track | corresponding endpoint-source error present |
| Boundary positive controls | Four definite states use picture evidence, cite both endpoints, and match Shot completeness | `passed=true` |
| Auxiliary provenance | Each of `PICTURE_OBSERVED`, `AUDIO_OBSERVED`, `TEXT_ANCHOR`, and `INFERRED` has empty `source_refs` | `AUXILIARY-SOURCE-REQUIRED` error present |
| Auxiliary provenance | Each of the same four states reaches a compatible real track through another auxiliary record | `passed=true` |
| Protected booleans | All five rights-boundary flags and both fallback locations use `0`, `1`, or strings | `SCHEMA-TYPE` error present |
| Canonical Schema | Canonical Schema is empty, malformed, weakened, or has a coerced protected constant | setup failure asserted |
| Public boundary | Release label, fingerprint wording, and a synthetic long hexadecimal token appear in a public value | matching public-boundary error present |
| Public boundary | Media name, credential label, or data URI is hidden in a measurement key | matching public-boundary error present |
| Report collision | Report is a symlink alias of an input or caller Schema | protected-output return code `2` asserted through `main()` |
| Atomic report write | Final replacement fails after an old report exists | `main()` returns `2`; old report is unchanged; temporary file is removed |
| Existing Phase 1 matrix | UNKNOWN leakage, text-anchor identity, audio directives, safe negative boundaries, quiet mode, directory discovery, wrong Schema, and repository fixture | all associated unit assertions pass |

## Process-level verification

These commands were executed against the final committed repair tree.

| Command or direct replay | Return code | Result |
|---|---:|---|
| `python3 -m json.tool skills/drama-director-compiler/references/scene-evidence.schema.json` | `0` | Schema JSON parses |
| `python3 -m py_compile skills/drama-director-compiler/scripts/validate_scene_evidence.py` | `0` | Validator compiles |
| `python3 -m unittest discover -s skills/drama-director-compiler/tests -v` | `0` | 96 tests pass |
| `python3 skills/drama-director-compiler/scripts/validate_scene_evidence.py skills/drama-director-compiler/tests/fixtures/repository-integration.scene-evidence.json` | `0` | Repository integration fixture passes |
| Direct CLI replay: natural verified boundary plus inferred boundary evidence | `1` | Re-review counterexample is rejected |
| `git diff --check origin/main...HEAD` | `0` | Complete committed PR diff has no whitespace errors |

## What remains unverified

- A new independent reviewer has not yet accepted this repair.
- Structural validation does not prove that legacy film or television
  observations are correct.
- Source media was not replayed and semantic audio was not directly auditioned.
- Creative quality, audience response, and human director approval were not
  tested.
- A3 and all later migration/generalization phases remain out of scope.

## Rollback

Before merge, revert the reopening commit and this repair with ordinary Git
revert commits. Do not rewrite shared history. No source media, production data,
credentials, accounts, permissions, payments, or production systems were
changed.
