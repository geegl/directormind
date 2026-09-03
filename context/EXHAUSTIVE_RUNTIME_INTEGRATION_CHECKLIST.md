# Exhaustive Runtime Integration Checklist

Status values: `TODO`, `IN_PROGRESS`, `VERIFIED_DONE`, `PARTIAL_EVIDENCE_GAP`, `BLOCKED`.

| ID | Status | Requirement | Evidence |
|---|---|---|---|
| X1 | VERIFIED_DONE | Start from latest `origin/main` on `codex/exhaustive-runtime-integration`; protect prior work | Dedicated branch created; no media changed |
| X2 | VERIFIED_DONE | Recompute closed-corpus baseline | 33 sources, 31 evidence records, 2,343 Shots/edit units, 124 candidates and 16 families |
| X3 | VERIFIED_DONE | Define one canonical exhaustive review and strict validator | `runtime_integration.review.json`, schema, semantic validator, exact-set and relation-binding attacks |
| X4 | PARTIAL_EVIDENCE_GAP | Fresh moving-image review of all candidate-dependent Shots | 53 exact Shot refs across 12 finally mapped evidence records are moving-image reviewed; 107 candidates remain in precise gaps |
| X5 | PARTIAL_EVIDENCE_GAP | Directly audition every rule that depends on sound | No current runtime rule depends on audio; four Sound of Metal candidates require direct audition before final disposition |
| X6 | PARTIAL_EVIDENCE_GAP | Give 124/124 candidates exactly one final disposition | 17 final: 4 positive, 7 support, 5 boundary, 1 merge, 0 rejection; 107 remain `EVIDENCE_GAP_PENDING` |
| X7 | PARTIAL_EVIDENCE_GAP | Give 16/16 families a machine-verifiable final runtime role | 4 families active; 12 families remain in prioritized evidence gaps |
| X8 | PARTIAL_EVIDENCE_GAP | Map 31/31 evidence records and 33/33 source registrations | All 33 sources and 31 evidence records are registered/reviewed; 12 evidence records currently have final decision mappings |
| X9 | VERIFIED_DONE | Rebuild Candidate Index and Support Matrix from canonical authority | 124/124 and 16/16 deterministic builds; final/pending dispositions preserved without treating pending as final |
| X10 | VERIFIED_DONE | Rebuild Runtime Grammar with fresh-reviewed lineage only | 4 rules; Grammar Shot lineage exactly equals the approved final-disposition refs |
| X11 | VERIFIED_DONE | Bind routing signals and negative guards to locked facts | Five reviewed boundaries compile to four rule-level guards; removing each guard restores target-rule selection in the paired counterfactual |
| X12 | VERIFIED_DONE | Bind Grammar, routing result, changed dimensions and Director IR | Selected rule IDs exactly match Director IR Shot evidence IDs; each positive package changes Coverage, Blocking, Reaction, Pacing or Edit |
| X13 | VERIFIED_DONE | Generate original positive and boundary packages for every positive rule | 4 positive, 4 boundary and 9 additional no-match packages; all 17 remain `HUMAN_REVIEW_PENDING` |
| X14 | VERIFIED_DONE | Update final validation and STATE from live recomputation | Exhaustive report is `PASS` with phase `PARTIAL_EVIDENCE_GAP`; false `COMPLETE` is rejected |
| X15 | VERIFIED_DONE | Run focused tests, complete units, repository runner and PR diff check | 283 tests and all 25 local repository checks pass; working-tree whitespace check passes, with committed PR diff recheck next |
| X16 | IN_PROGRESS | Push new PR, wait for final-head CI, and run a clean-checkout family-by-family independent audit | Implementers cannot sign the final independent result; do not merge main |

## Current stop condition

The implementation may be delivered only as `PARTIAL_EVIDENCE_GAP` unless all
107 pending candidates receive a final disposition from evidence already in the
fixed corpus. The prioritized gap list is part of the deliverable; pending rows
must not be described as complete, rejected, or permanently blocked.
