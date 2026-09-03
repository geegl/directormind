# Runtime Rule Promotion Wave 1 — Final Validation

Updated: 2026-09-04

Status: `P1_REPAIR_PASS_LOCAL / CI_AUDIT_PENDING / MAIN_UNMERGED`

## Current result

- Canonical promotion review: PASS — 9 reviewed evidence units, 3 promoted
  rules, 3 families, 3 distinct scene problems, 0 errors.
- Scene Evidence: PASS_STRUCTURAL — 31 scenes, 2,343 Shot/edit units, 0 errors,
  81 preserved warnings.
- Candidate rules: PASS — 124 candidates, 16 families, 3
  `CROSS_WORK_SUPPORTED`, 121 blocked, 0 errors.
- Director Grammar: PASS — 3 eligible candidates and 3 runtime rules.
- Forward tests: PASS — 12 packages, 3 positive selections, 3 target boundary
  cases, 9 total `NO_APPLICABLE_RULE`, 12 `HUMAN_REVIEW_PENDING`, 0 errors and
  49 warnings.
- Complete unit/CLI suite: PASS — 257 tests.
- Complete repository runner: PASS — 21 checks, including deterministic
  builders, six versioned reports, repository boundaries and final report.

The product threshold is met. The first clean-checkout review found two P1s;
both were repaired, and the repaired implementation passed complete local
validation, hosted CI and independent clean-checkout re-review.

A later independent acceptance review found two further P1 gaps. Runtime
lineage previously inherited unreviewed legacy-candidate Shots, and phase
completion counted families but not distinct scene problems. The local repair
now produces exact fresh Shot sets of 9, 9 and 13 and reports three distinct
promoted scene problems. The full 21-check contract passes; hosted CI and
independent-audit evidence for this repair are still pending.

## Independent P1 repair evidence

- B99 S016 is now recorded as an owner-dominant OTS and removed from the
  clean-single support relation. Better Call Saul S082 now explicitly proves
  pre-hold relation registration before S097–S098.
- The spatial boundary no longer asserts that a counterpart relation is both
  required and not required.
- The proximity ellipsis boundary no longer asserts continuous present time,
  and both proximity packages now have explicit project-original locked
  relationship facts.
- Forward validation rejects the two observed contradictory signal pairs,
  signals without their matching locked fact type, and `ROMANTIC_PROXIMITY`
  without locked relationship authority.

## Required final commands

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/drama-director-compiler/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/run_repository_checks.py --write-final-report
git diff --check origin/main...HEAD
```

## Remaining risks

- Semantic audio was not directly auditioned; no promoted rule depends on it.
- Only nine of the 31 evidence units were freshly replayed for these rules.
- Three scene problems use short paraphrased visible-text anchors plus picture
  evidence; the remaining uncited dialogue and story semantics are unknown.
- Structural routing and Director IR binding do not prove creative quality,
  audience effect, or production readiness.
- Hosted CI succeeded on the repaired implementation head. Independent re-review
  returned `PASS_LOCAL / NO_MUST_FIX_FINDINGS`. The final status-only commit is
  checked externally before delivery because a versioned report cannot attest
  to its own future CI result.

## Rollback

Use a normal revert commit for the isolated Wave 1 change. This returns the
Grammar and original forward tests to the prior zero-rule state without changing
source media, immutable legacy ledgers, private scripts, or `main` history.
