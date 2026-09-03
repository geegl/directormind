# Validation Claim Register

Updated: 2026-09-03

Status: `WAVE1_LOCAL_PASS / REMOTE_CI_AND_INDEPENDENT_REVIEW_PENDING`

This register maps current claims to reproducible evidence. A structural pass
does not prove creative quality, audience response, or production readiness.

| Claim | Reproduction command | Current result | Boundary |
|---|---|---|---|
| Canonical Wave 1 review | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_runtime_rule_promotion_review.py --check` | PASS — 9 reviewed evidence units, 3 promoted rules, 3 families, 0 errors | Confirms manifest/schema/evidence binding; independent picture judgment remains separate |
| Canonical conversion | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/convert_legacy_scene_evidence.py --check` | PASS — 31 scenes, 2,343 Shot/edit units, 124 candidate identities | Proves deterministic output from legacy inputs plus the canonical Wave 1 review |
| Generated evidence views | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/render_scene_evidence.py --check` | PASS — 31/31 | Generated Markdown is a review view; legacy Markdown is not overwritten |
| Scene Evidence structure | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_scene_evidence.py research/evidence --quiet` | PASS_STRUCTURAL — 31 passed, 0 failed, 0 errors, 81 warnings | Nine evidence units received fresh picture review; semantic audio remains unknown |
| Candidate build | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/build_candidate_rule_index.py --check` | PASS — 124 candidates, 16 families | Family assignment alone never authorizes a rule |
| Candidate promotion gates | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_candidate_rules.py --check` | PASS — 3 `CROSS_WORK_SUPPORTED`, 121 blocked, 0 errors | Eligibility is recomputed from canonical support, boundary and forward-test records |
| Grammar build | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/build_director_grammar.py --check` | PASS — 3 deterministic runtime rules | No second rule source and no manual edit of the generated Grammar |
| Runtime Grammar | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_director_grammar.py --check` | PASS — 3 eligible candidates, 3 runtime rules, 0 errors | All three are visual-only, project-original-fallback rules |
| Legacy routing fixtures | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_director_routing_cases.py --check` | PASS — 8 cases, 8 `NO_APPLICABLE_RULE` | Preserves the earlier negative fixtures; positive selection is proved separately |
| Original forward build | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/build_forward_tests.py --check` | PASS — 12 packages | Locked story text remains unchanged; derived directing outputs are deterministic |
| Original forward repository | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_forward_tests.py --check` | PASS — 3 selected, 3 target boundaries, 9 total no-rule results, 12 pending, 0 errors, 47 warnings | Positive Shot rule IDs bind exactly; creative review remains pending |
| Director IR compatibility | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/drama-director-compiler/tests -p 'test_director_*.py' -v` | PASS | Preserves prior route replay and output-safety contracts |
| Complete unit/CLI behavior | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/drama-director-compiler/tests -v` | PASS — 241 tests | Includes role, text-anchor, reviewed-Shot, candidate, Grammar and forward-route attacks |
| Repository boundaries | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_repository_boundaries.py --quiet` | PASS — 0 broken refs, prohibited files, current-artifact string issues, or whitespace issues | The 30 immutable historical ledgers remain explicitly excluded provenance |
| Complete local automation | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/run_repository_checks.py --write-final-report` | PASS — 21 checks; final report is `PASS_LOCAL` | Hosted CI is post-push evidence, not self-attested here |
| Complete committed diff | `git diff --check origin/main...HEAD` | Pending final commit | Must be rerun after the Wave 1 commit exists |

## Rule-level evidence

The source/support/boundary Shot IDs, exact timecodes, observed facts, text
anchors, unknowns, directing changes and original test pairs are recorded in
`research/validation/RUNTIME_RULE_PROMOTION_WAVE1_EVIDENCE_REVIEW.md`.
Machine authority remains
`research/grammar/runtime_rule_promotion_wave1.review.json`.

## External and independent evidence

- New PR: pending.
- Hosted CI on the new PR: pending.
- Fresh clean-checkout independent review: pending.
- Merge, deployment, publication, generation and media deletion: not performed.

## Unverified boundaries

- Only nine evidence units were freshly replayed for Wave 1.
- Semantic audio was not directly auditioned.
- Three short visible-text anchors are paraphrases; uncited dialogue remains
  unknown.
- Structural selection does not prove creative merit or audience effect.
