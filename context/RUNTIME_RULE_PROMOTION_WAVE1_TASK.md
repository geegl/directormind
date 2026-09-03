# DirectorMind Runtime Rule Promotion Wave 1 — Task Card

Updated: 2026-09-03

Status: `IN_PROGRESS / LOCAL_VALIDATION_PASS / REMOTE_AND_INDEPENDENT_PENDING`

## 1. Why this work exists

The closed corpus contains 33 local source files, 31 canonical Scene Evidence
units, 2,343 Shot/edit units, 124 candidate mechanisms and 16 textual families,
but the prior runtime Grammar contained no real directing rule. A safe empty
Grammar proved rejection behavior, not product usefulness.

## 2. Expected result

An original scene whose locked facts match one of the newly supported triggers
must receive a real `SELECTED` routing result. The selected rule must visibly
change at least one directing decision in Coverage, Blocking, Reaction, Pacing,
or Edit, and its Director IR Shot evidence IDs must exactly match the route.

This phase is `COMPLETE` only with at least three real-video-backed,
`CROSS_WORK_SUPPORTED` rules spanning at least three directing problems. One or
two rules would be `PARTIAL`; zero would be `BLOCKED`.

## 3. Out of scope

- No new film or television source, download, or media processing beyond the
  existing closed corpus.
- No `GENERAL_DEFAULT` promotion.
- No Seedance/H3 prompt, provider call, or generated media.
- No change to the private *Hell of a Dad* scripts or Director IR.
- No source video, audio, still, contact sheet, subtitle file, long dialogue,
  local path, credential, or personal data in the repository.
- No deletion of source media and no merge to `main`.

## 4. Protected content and systems

The private production scripts, production data, accounts, permissions,
credentials, payments, deployment and publication surfaces are untouched.
Legacy evidence Markdown remains immutable. Only canonical inputs and the
repository's deterministic builders may change derived JSON and review views.

## 5. Completion criteria

- [x] At least three rules are backed by fresh review of real local video.
- [x] At least three unrelated mechanism families and directing problems are
  represented.
- [x] Every rule has same-trigger cross-work support and a real boundary case.
- [x] Every rule has exact evidence/Shot/time lineage, machine triggers,
  applicability, non-applicability, three-axis confidence/risk, visual-only
  audio boundary, and project-original fallback.
- [x] Every rule has one original positive and one original boundary package.
- [x] The router actually returns `SELECTED`, and Director IR evidence IDs bind
  to the selected rules.
- [x] One full `NO_APPLICABLE_RULE` path remains.
- [x] Complete local repository runner passes before commit; the committed-diff
  whitespace check will be repeated immediately after commit.
- [ ] New PR hosted CI passes.
- [ ] A fresh non-writing reviewer checks real video and returns no must-fix
  finding from a clean checkout.

## 6. Current status

- Current sole implementer and shared-file writer: root agent.
- Completed: nine source-video replays; three canonical promotions; deterministic
  Scene Evidence, candidate, matrix, Grammar and forward-test builds; three
  positive and three boundary routes; focused validation.
- Remaining: commit, committed-diff check, new PR, hosted CI, and clean-checkout
  independent review.
- Known limitations: semantic audio remains unauditioned; the visible-text
  anchors are short paraphrases; creative quality and audience response are not
  machine-proved.
- Current validation: 241/241 tests and all 21 repository checks pass locally.
- Next single action: commit the isolated Wave 1 diff and rerun the committed-diff
  check.

## Rollback

Revert the isolated Wave 1 commit with a normal revert commit. This restores the
zero-rule Grammar and eight-package forward-test state without touching source
media, legacy evidence Markdown, private scripts, or `main` history.
