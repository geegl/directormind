# Exhaustive Runtime Integration P1 — Independent Read-Only Audit

Date: 2026-09-05

Status: `REMEDIATION_PENDING_NEW_HEAD_REVIEW`

## Superseded implementation-head verdict

The first clean-checkout reviewer did not pass the initial remediation head.
The reviewer made no repository or media changes and independently found:

| Severity | Finding | Reproduced evidence | Current remediation |
|---|---|---|---|
| P1 | A shared-Shot Observation could be deleted from the recurring Sound candidate, its claims and its candidate authority at the same time. | Removing E001 from all three locations still returned exit zero and `PASS` because E002 covered the same S001/S002 pair. | Each directly auditioned Observation now independently lists the candidates it may support. Candidate authority, reverse Observation authority and copied claims must all agree exactly. All sixteen coordinated deletion cases are rejected. |
| P1 | The former Chernobyl S169 note overstated a chest-up speaker anchor as a restored whole-room field. | Six source frames across that complete interval showed the speaker in medium-close coverage against a softly blurred seated background, without the whole-room board/desk geography. | The corrected split renumbers that interval as S170, records only the narrower visible fact and explicitly withholds whole-room geography. The boundary status remains supported by the other cited room/process Shots. |
| P2 | The closed-corpus status still described *Sound of Metal* as measured but not directly auditioned. | The register said direct audition zero while the canonical runtime review, STATE and final report said one. | The register now records one directly auditioned envelope, zero measured-only envelopes and keeps deletion separately unauthorized. |

The original same-Shot ID-and-description substitution, candidate-set swap,
unauthorized addition and unique-ref deletion attacks also failed on that
reviewed head. Its 11 spatial destinations and all live counts were otherwise
independently confirmed.

## Second clean-checkout verdict

A different non-writing reviewer then attacked the first repair and again did
not pass it. That reviewer independently found:

| Severity | Finding | Reproduced evidence | Current remediation |
|---|---|---|---|
| P1 | The mutable review could still be rewritten together with the candidate. | Removing E001 from the recurring candidate, copied claim, forward binding, reverse binding and Observation body still returned `PASS`; rewriting the STAGGER row and both mutable directions from E002 to same-Shot E001 also returned `PASS`. | A separate canonical audio authority now fixes all sixteen Observations and the four candidate bindings. Review-only deletion, addition, exchange and synchronized ID/description rewrites must differ from that authority and fail. |
| P1 | The canonical Chernobyl S165 interval hid a real cut, and the former S169 description was still wrong in canonical Scene Evidence. | Adjacent frames place the cut at `00:49:36.760`; the former S169 interval shows chest-up speaker coverage rather than a whole-room field. | The converter deterministically splits S165/S166, shifts later IDs through S206, corrects the resulting S170 speaker claims, and regenerates all dependent lineage and counts. |
| P1 | PR #5 still advertised superseded counts and a prior pass. | The PR body retained old disposition counts and an obsolete approval claim. | PR text will be replaced only after the repaired head, CI and final independent verdict are available. |

The second reviewer separately confirmed the eleven spatial destinations as two
merges, three supports, three boundaries and three pending candidates in two
genuine external gaps.

## Current local repair evidence

- Focused converter, Sound and exhaustive suites: 73/73 pass.
- Complete unit and CLI suite: 317/317 pass.
- Complete report-writing repository runner: 25/25 pass.
- The complete committed `origin/main...HEAD` diff check returns zero.
- Full coordinated deletion and same-Shot synchronized substitution are rejected
  by the separate canonical authority, not only by mutable reverse bindings.
- All four legitimate Sound candidate bindings pass and remain
  `EVIDENCE_GAP_PENDING`; none enters Runtime Grammar.
- The 11 spatial candidates remain two merges, three supports, three
  boundaries and three candidates in two structured external gaps.
- Live recomputation remains 124 candidates, 63 final dispositions, 61 pending
  candidates, zero existing-material-review rows, 15 gaps, 27 evidence final
  mappings, 11 runtime-participating families and seven runtime rules.
- Chernobyl now has 206 canonical Shots and the repository total is 2,344;
  candidate-dependent moving-image refs total 1,841.
- Repository and source-media boundaries pass; no media or private script changed.

## Required next verdict

This document does not self-sign the repair. The current changes must be pushed,
the hosted workflow must pass, and a different clean-checkout non-writing
reviewer must replay the two audio attacks, verify the Chernobyl correction,
audit the 11 spatial destinations and recompute the live reports. Until then,
the result is not `NO_MUST_FIX_FINDINGS`.

## Unverified boundary

The first reviewer reopened all nine related local videos and sampled the
candidate-specific key Shots, but did not repeat a full frame-by-frame cut scan
of every complete source interval. The 11 spatial candidates declare
`audio_dependency=false`; their semantic audio was not auditioned.

## Rollback

All changes remain isolated on `codex/exhaustive-runtime-integration`. Use a
normal revert on the PR branch if the new review finds a regression. Do not
rewrite shared history, delete source media or merge `main`.
