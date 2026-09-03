# Runtime Rule Promotion Wave 1 — Checklist

Updated: 2026-09-03

Status vocabulary: `TODO`, `IN_PROGRESS`, `BLOCKED`, `VERIFIED_DONE`.

| ID | Status | Requirement | Evidence / exit condition |
|---|---|---|---|
| W1-01 | VERIFIED_DONE | Refresh `origin/main`, preserve existing work, and use `codex/runtime-rule-promotion-wave1`. | Branch is based on current `origin/main`; the pre-existing working tree was not overwritten. |
| W1-02 | VERIFIED_DONE | Freeze the 33-source corpus. | No work or media was added, downloaded, deleted, or committed. |
| W1-03 | VERIFIED_DONE | Screen the five priority mechanism families without writing from review agents. | Read-only family screening narrowed the implementation to three evidence-sufficient families; root remained sole writer. |
| W1-04 | VERIFIED_DONE | Re-open real video for every promotion source, support and boundary. | Canonical review manifest records 9 evidence units and exact Shot/time lineage; temporary frames remain outside the repository. |
| W1-05 | VERIFIED_DONE | Resolve scene problems and functional roles without hardening unknown facts. | Three scene problems and six within-Shot roles cite reviewed picture/text sources; other semantics remain `UNKNOWN`. |
| W1-06 | VERIFIED_DONE | Establish same-trigger support and a real boundary per rule. | Seven relation records cover three source candidates, four support works and three boundary works. |
| W1-07 | VERIFIED_DONE | Rebuild candidate index and cross-work matrix from canonical inputs. | 124 candidates, 16 families, 3 `CROSS_WORK_SUPPORTED`, 121 blocked; deterministic check passes. |
| W1-08 | VERIFIED_DONE | Generate real Director Grammar v0.2 runtime rules. | Grammar builder emits 3 runtime-authorized visual rules from 3 families; validator reports zero errors. |
| W1-09 | VERIFIED_DONE | Add one positive and one boundary original package for every promoted rule. | 12 packages total; 3 positive `SELECTED`, 3 target boundaries, 9 no-rule results, all `HUMAN_REVIEW_PENDING`. |
| W1-10 | VERIFIED_DONE | Bind selected rules to Director IR and material directing changes. | Positive Shot IDs carry the exact selected IDs and change Coverage/Blocking/Pacing/Edit; boundary cases reject the target rule. |
| W1-11 | VERIFIED_DONE | Preserve rights, audio and private-script boundaries. | No media/surface copy/private script change; `audio_dependency=false`; generation and publication remain unauthorized. |
| W1-12 | VERIFIED_DONE | Add adversarial and deterministic regression coverage. | Role, reviewed-Shot, text-anchor, audio, candidate, Grammar and forward-route attacks are covered. |
| W1-13 | VERIFIED_DONE | Run the final local contract against the complete working-tree diff. | 241 tests, all 21 repository checks and pre-commit `git diff --check` pass; committed-diff check is repeated after commit. |
| W1-14 | IN_PROGRESS | Commit, push and create a new PR. | New PR targets `main`; PR #3 is not reused; no merge is performed. |
| W1-15 | TODO | Wait for hosted CI on the final PR head. | Read-only workflow passes on the final pushed commit. |
| W1-16 | TODO | Obtain fresh independent read-only review. | A reviewer who wrote no rule inspects the clean checkout, concrete video evidence and positive directing changes, then returns no must-fix finding. |
| W1-17 | TODO | Stop for user merge decision. | State is `COMPLETE` only after W1-13 through W1-16 pass; `main` remains unmerged. |

## Blocked-candidate rule

The remaining 121 candidates stay blocked. A blocked row is not skipped: its
release condition remains the missing verified same-trigger support, real
boundary, canonical scene problem/roles, or equivalent evidence named by the
candidate validator. No additional work may be acquired in this phase.
