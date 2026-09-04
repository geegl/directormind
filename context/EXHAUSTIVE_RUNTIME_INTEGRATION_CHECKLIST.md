# Exhaustive Runtime Integration Checklist

Status values: `TODO`, `IN_PROGRESS`, `VERIFIED_DONE`, `PARTIAL_EVIDENCE_GAP`, `BLOCKED`.

| ID | Status | Requirement | Evidence |
|---|---|---|---|
| X1 | VERIFIED_DONE | Start from latest `origin/main` on `codex/exhaustive-runtime-integration`; protect prior work | Dedicated branch created; no media changed |
| X2 | VERIFIED_DONE | Recompute closed-corpus baseline | 33 sources, 31 evidence records, 2,343 Shots/edit units, 124 candidates and 16 families |
| X3 | VERIFIED_DONE | Define one canonical exhaustive review and strict validator | `runtime_integration.review.json`, schema, semantic validator, exact-set and relation-binding attacks |
| X4 | VERIFIED_DONE | Fresh moving-image review of all candidate-dependent Shots | 1,840 unique candidate-dependent Shot refs across all 31 evidence records were reopened against the fixed local corpus; exact canonical timecodes are retained |
| X5 | IN_PROGRESS | Directly audition every rule that depends on sound | No current runtime rule depends on audio; four Sound of Metal candidates remain `EXISTING_MATERIAL_REVIEW_REQUIRED` until direct human audition of their cited local intervals |
| X6 | IN_PROGRESS | Give 124/124 candidates exactly one final disposition | 55 final: 7 positive, 24 support, 20 boundary, 1 merge, 3 rejection; 65 are true evidence gaps and 4 await direct review of existing material |
| X7 | IN_PROGRESS | Give 16/16 families a machine-verifiable final runtime role | 11 families participate through a final runtime effect; multi-thread intercut, object custody, scale/reveal, subjective access and threshold/route continuity remain unresolved |
| X8 | IN_PROGRESS | Map 31/31 evidence records and 33/33 source registrations | All sources and evidence records are registered/reviewed; 26 evidence records currently have final decision mappings, with four evidence-gap records and Sound of Metal still non-final |
| X9 | VERIFIED_DONE | Rebuild Candidate Index and Support Matrix from canonical authority | 124/124 and 16/16 deterministic builds; final/pending dispositions preserved without treating pending as final |
| X10 | VERIFIED_DONE | Rebuild Runtime Grammar with fresh-reviewed lineage only | 7 rules; Grammar Shot lineage exactly equals the approved final-disposition refs; four false same-trigger promotions were removed after independent review |
| X11 | VERIFIED_DONE | Bind routing signals and negative guards to locked facts | 20 reviewed boundaries compile into rule-level guards; every distinct reviewed signal independently blocks its target rule when injected into that rule's positive scene |
| X12 | VERIFIED_DONE | Bind Grammar, routing result, changed dimensions and Director IR | Selected rule IDs exactly match Director IR Shot evidence IDs; each positive package changes Coverage, Blocking, Reaction, Pacing or Edit |
| X13 | VERIFIED_DONE | Generate original positive and boundary packages for every positive rule | 7 positive, 7 boundary and 15 additional no-match packages; all 29 remain `HUMAN_REVIEW_PENDING` |
| X14 | VERIFIED_DONE | Update final validation and STATE from live recomputation | Exhaustive report is structurally `PASS` with product phase `IN_PROGRESS`; false `COMPLETE` and false evidence-gap labeling are rejected |
| X15 | VERIFIED_DONE | Run focused tests, complete units, repository runner and PR diff check | 53 focused regressions pass; 294/294 unit and CLI tests pass; the repository runner passes 25/25 checks and rebuilds the final report; PR diff whitespace check passes |
| X16 | IN_PROGRESS | Push new PR, wait for final-head CI, and run a clean-checkout family-by-family independent audit | Implementers cannot sign the final independent result; do not merge main |

## Current stop condition

The implementation remains `IN_PROGRESS` while four candidates still require
direct audition of existing local material. After that review, it can become
`PARTIAL_EVIDENCE_GAP` only if the 65 fixed-corpus gaps remain. No unresolved
row may be described as complete, rejected, or permanently blocked.
