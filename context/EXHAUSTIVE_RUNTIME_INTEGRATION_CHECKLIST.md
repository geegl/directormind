# Exhaustive Runtime Integration Checklist

Status values: `TODO`, `IN_PROGRESS`, `VERIFIED_DONE`, `PARTIAL_EVIDENCE_GAP`, `BLOCKED`.

| ID | Status | Requirement | Evidence |
|---|---|---|---|
| X1 | VERIFIED_DONE | Start from latest `origin/main` on `codex/exhaustive-runtime-integration`; protect prior work | Dedicated branch created; no media changed |
| X2 | VERIFIED_DONE | Recompute closed-corpus baseline | 33 sources, 31 evidence records, 2,344 Shots/edit units, 124 candidates and 16 families; renewed frame review split the former Chernobyl S165 at its hidden cut |
| X3 | VERIFIED_DONE | Define one canonical exhaustive review and strict validator | `runtime_integration.review.json`, its schema and semantic validator cover exact sets, relation binding and structured external gaps; `runtime_integration_audio_authority.json` independently fixes the Sound observation and candidate binding authority |
| X4 | VERIFIED_DONE | Fresh moving-image review of all candidate-dependent Shots | 1,841 unique candidate-dependent Shot refs across all 31 evidence records were reopened against the fixed local corpus; exact canonical timecodes are retained |
| X5 | VERIFIED_DONE | Directly audition every rule that depends on sound | The complete Sound of Metal selection was directly auditioned across 25 Shots and recorded as 16 approximate audible-state observations; the external canonical authority fixes each candidate's exact permitted Observation set, refs and reason, and claims must exactly copy descriptions; deletion, addition, exchange and synchronized same-Shot substitution in the mutable review fail; all four remain external gaps and no runtime rule depends on audio |
| X6 | PARTIAL_EVIDENCE_GAP | Give 124/124 candidates exactly one final disposition | 63 final: 7 positive, 27 support, 23 boundary, 3 merge, 3 rejection; the remaining 61 belong to exactly one of 15 structured external evidence gaps and none await review of existing material |
| X7 | PARTIAL_EVIDENCE_GAP | Give 16/16 families a machine-verifiable final runtime role | 11 families participate through a final runtime effect; multi-thread intercut, object custody, scale/reveal, subjective access and threshold/route continuity require the listed external evidence |
| X8 | PARTIAL_EVIDENCE_GAP | Map 31/31 evidence records and 33/33 source registrations | All sources and evidence records are registered/reviewed; 27 evidence records have final decision mappings and four remain tied only to precise evidence gaps |
| X9 | VERIFIED_DONE | Rebuild Candidate Index and Support Matrix from canonical authority | 124/124 and 16/16 deterministic builds; three candidates were reclassified from spatial registration to continuous movement, and final/pending dispositions remain distinct |
| X10 | VERIFIED_DONE | Rebuild Runtime Grammar with fresh-reviewed lineage only | 7 rules; Grammar Shot lineage exactly equals the approved final-disposition refs; four false same-trigger promotions were removed after independent review |
| X11 | VERIFIED_DONE | Bind routing signals and negative guards to locked facts | 23 reviewed boundaries compile into rule-level guards; every distinct reviewed signal independently blocks its target rule when injected into that rule's positive scene |
| X12 | VERIFIED_DONE | Bind Grammar, routing result, changed dimensions and Director IR | Selected rule IDs exactly match Director IR Shot evidence IDs; each positive package changes Coverage, Blocking, Reaction, Pacing or Edit |
| X13 | VERIFIED_DONE | Generate original positive and boundary packages for every positive rule | 7 positive, 7 boundary and 15 additional no-match packages; all 29 remain `HUMAN_REVIEW_PENDING` |
| X14 | VERIFIED_DONE | Update final validation and STATE from live recomputation | Exhaustive report is structurally `PASS` with product phase `PARTIAL_EVIDENCE_GAP`; false `COMPLETE`, unstructured external gaps and unfinished-existing-review labeling are rejected |
| X15 | VERIFIED_DONE | Run focused tests, complete units, repository runner and PR diff check | The 73-test focused converter/Sound/exhaustive suite, 317/317 complete unit and CLI tests and all 25 repository checks pass; the runner rebuilt the final report and the complete committed `origin/main...HEAD` diff check returns zero |
| X16 | IN_PROGRESS | Push PR #5, wait for final-head CI, and run a clean-checkout independent P1 review | A second clean reviewer reproduced full coordinated audio-authority mutation, the hidden cut inside Chernobyl S165, the incorrect S169 description and stale PR counts. The local repair is not independently passed until a new pushed head, hosted CI and a different non-writing reviewer verify it |

## Current stop condition

The implementation is `PARTIAL_EVIDENCE_GAP`: no candidate remains awaiting
review of identified existing material, but 61 candidates still need the 15
structured external evidence additions recorded in the canonical review. No unresolved row
may be described as complete, rejected, or permanently blocked.
