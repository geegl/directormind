# Runtime Rule Promotion Wave 1 — Final Validation

Updated: 2026-09-03

Status: `PASS_LOCAL / REMOTE_AND_INDEPENDENT_PENDING`

## Current result

- Canonical promotion review: PASS — 9 reviewed evidence units, 3 promoted
  rules, 3 families, 0 errors.
- Scene Evidence: PASS_STRUCTURAL — 31 scenes, 2,343 Shot/edit units, 0 errors,
  81 preserved warnings.
- Candidate rules: PASS — 124 candidates, 16 families, 3
  `CROSS_WORK_SUPPORTED`, 121 blocked, 0 errors.
- Director Grammar: PASS — 3 eligible candidates and 3 runtime rules.
- Forward tests: PASS — 12 packages, 3 positive selections, 3 target boundary
  cases, 9 total `NO_APPLICABLE_RULE`, 12 `HUMAN_REVIEW_PENDING`, 0 errors and
  47 warnings.
- Complete unit/CLI suite: PASS — 241 tests.
- Complete repository runner: PASS — 21 checks, including deterministic
  builders, six versioned reports, repository boundaries and final report.

The local product threshold is met. The phase is not yet final because the
committed-diff check, hosted CI and clean-checkout independent review remain.

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
- Hosted CI and a fresh independent real-video review are not yet recorded.

## Rollback

Use a normal revert commit for the isolated Wave 1 change. This returns the
Grammar and original forward tests to the prior zero-rule state without changing
source media, immutable legacy ledgers, private scripts, or `main` history.
