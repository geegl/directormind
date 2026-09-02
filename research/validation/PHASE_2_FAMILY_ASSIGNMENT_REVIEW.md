# Phase 2 Family Assignment Review

Updated: 2026-09-01

Status: `ROOT_INTEGRATED / PROMOTION_NEUTRAL`

## Scope

All 120 existing candidate identities were reviewed against their preserved
legacy trigger, directing decision, coverage, blocking, edit/pacing and
applicability text. The review selected only among the 16 source-neutral
mechanism families already declared by the Phase 2 builder. It did not replay
media, add a source work, change legacy lineage or authorize a runtime rule.

## Result

- 120/120 candidate identities received an explicit family decision.
- 80 deterministic keyword assignments were accepted after reading the full
  preserved mechanism text.
- 40 keyword-collision assignments were corrected in the versioned
  `FAMILY_OVERRIDES` register in `build_candidate_rule_index.py`.
- 0 candidates required a new work-specific family.
- 0 family decisions count as cross-work support, same-trigger evidence,
  counterexample evidence or promotion approval.

The two non-writing review passes divided the sorted candidate register into
the first and final 60 identities. Root integrated their decisions and retained
the complete executable mapping in the builder. Regression tests require all
120 output records to carry `ROOT_REVIEWED_TEXTUAL_CLUSTER`, require exactly 40
reviewed overrides, and spot-check the four originally reproduced keyword
collisions:

- multi-thread state change is not object custody;
- ellipsis punctuation is not axis coverage;
- subtractive aftermath is not threshold continuity;
- continuity proved by uninterrupted movement is not a version ledger.

## Boundary

Family assignment is a retrieval and comparison aid only. The current matrix
continues to label every candidate relation `NARROWS`; no family member is
counted as `SUPPORTS`. Promotion work counts come only from separately cited,
same-family, same-trigger support relations with a named human-review artifact.
