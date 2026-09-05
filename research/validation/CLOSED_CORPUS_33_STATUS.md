# Closed Corpus — 33 Local Source Status

Updated: 2026-09-05

Status: `READ_ONLY_CORPUS_REGISTER_COMPLETE / NO_DELETE_AUTHORIZED`

## Exhaustive Runtime Integration note

All 31 existing evidence units were reopened from their local source videos for
the exhaustive integration review. The complete selected *Sound of Metal*
envelope was also directly auditioned across its 25 canonical Shots and recorded
as 16 approximate audible-state observations. This adds no work and changes no
retention decision. The other 30 evidence units do not have direct semantic
audio review. Exact candidate-level review scope is recorded in
`runtime_integration.review.json` and the exhaustive validation report.

This register covers the 33 media files currently in the closed local corpus. A row is one local source file, not necessarily one different feature film: episodic sources and combined episode files are counted as files. *Fleabag* S02E01 is not included because no local file exists. No source media, still, audio excerpt, subtitle, dialogue transcript, raw release label, download-site label, or absolute local path is recorded here.

## Counting boundary

- First batch local files: `16` = 14 accepted canonical targets + 1 retained extra *Brooklyn Nine-Nine* S05E03–04 source + 1 target-scene-rejected *Better Call Saul* S01E09 source.
- Post-16 local files: `17`, all accepted into the closed evidence pool.
- Accepted or retained sources: `32/33`.
- Target-scene-rejected sources: `1/33`.
- Pending downloads: `0`.
- Current-branch local-source evidence units: `31`; each has a rights-safe Markdown migration source and adjacent deterministic Scene Evidence JSON. The retained extra B99 source and rejected BCS source have no current evidence file.

## Status vocabulary

- `CURRENT_LOCAL_EVIDENCE`: a legacy Scene Evidence Markdown file and adjacent deterministic Scene Evidence JSON exist in the current branch; the JSON passes the repository structural validator. This does not prove source replay, direct audio audition, creative approval, or cross-work rule validity.
- `NO_SCENE_EVIDENCE`: no Scene Evidence file exists for this local source.
- `BLOCKED_DIRECT_AUDITION`: audio has not been directly auditioned and cannot support an observed semantic sound claim.
- `SIGNAL_MEASURED_NOT_AUDITIONED`: decoded-signal measurements exist, but nobody directly auditioned the audio and no semantic sound conclusion is established.
- `DIRECT_AUDITION_COMPLETE`: the selected evidence envelope was directly auditioned and its approximate audible states are bound to exact source-local time ranges; this does not authorize deletion.
- Every `Current delete` value is `NO`. This register is not deletion authorization.

Deletion blockers used below:

- `G2`: direct sound audit or an explicitly accepted local-only preservation substitute is incomplete.
- `G5`: the retained source has no complete evidence unit yet.
- `G6`: the requested target scene was rejected; final source-retention/deletion disposition still requires explicit user approval.
- `G7`: direct audition is complete, but a separate per-source deletion and recovery review plus explicit user approval has not occurred.

## Per-source register

| # | Batch | Local source entry | Target / source status | Existing evidence | Picture analysis | Sound status | Current delete | Blocker |
|---:|---|---|---|---|---|---|---|---|
| 1 | First | *The Social Network* (2010) | ACCEPTED_TARGET | `THE-SOCIAL-NETWORK-2010-OPENING-TWO-PERSON-EXCHANGE-001` / CURRENT_LOCAL_EVIDENCE | Complete visual envelope / 91 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 2 | First | *The Devil Wears Prada* (2006) | ACCEPTED_TARGET | `THE-DEVIL-WEARS-PRADA-2006-CERULEAN-CORRECTION-001` / CURRENT_LOCAL_EVIDENCE | Complete visual envelope / 26 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 3 | First | *Succession* S01E06 | ACCEPTED_TARGET | `SUCCESSION-S01E06-BOARD-VOTE-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual ledger / 88 visible shots; four candidate lineages remain blocked | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 4 | First | *Better Call Saul* S01E09-labelled source | TARGET_SCENE_REJECTED / exact episode identity UNKNOWN | NO_SCENE_EVIDENCE | Requested Chuck/Jimmy target scene not present in audited ranges | TARGET_SCENE_NOT_AVAILABLE / SOURCE_AUDIO_NOT_AUDITIONED | NO | G6 |
| 5 | First | *Ted Lasso* S01E08 | ACCEPTED_TARGET | `TED-LASSO-S01E08-DARTS-REVERSAL-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 147 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 6 | First | *Get Out* (2017) | ACCEPTED_TARGET | `GETOUT-2017-HYPNOSIS-SUBJECTIVE-SPACE-001` / CURRENT_LOCAL_EVIDENCE | Complete visual envelope / 74 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 7 | First | *A Quiet Place* (2018) | ACCEPTED_TARGET | `A-QUIET-PLACE-2018-PARALLEL-BODY-STATE-RADIAL-LIGHT-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 34 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 8 | First | *Nobody* (2021) | ACCEPTED_TARGET | `NOBODY-2021-BUS-001` / CURRENT_LOCAL_EVIDENCE | Complete visual envelope / 128 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 9 | First | *Marriage Story* (2019) | ACCEPTED_TARGET | `MARRIAGE-STORY-2019-APARTMENT-SEQUENCE-001` / CURRENT_LOCAL_EVIDENCE | Complete visual envelope / 85 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 10 | First | *Knives Out* (2019) | ACCEPTED_TARGET | `KNIVES-OUT-2019-WILL-READING-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 108 visible units | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 11 | First | *The Last of Us* S01E06-labelled source | ACCEPTED_TARGET / episode identity source-supplied | `TLOU-BEDROOM-LOCAL-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 27 visible shots; covered pixels remain UNKNOWN | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 12 | First | *House of the Dragon* S01E08 | ACCEPTED_TARGET | `HOUSE-OF-THE-DRAGON-S01E08-THRONE-ROOM-INGRESS-TO-SEATED-STATE-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 68 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 13 | First | *Bridgerton* S02E05 | ACCEPTED_TARGET | `BRIDGERTON-S02E05-CONTAINED-PROXIMITY-001` / CURRENT_LOCAL_EVIDENCE | Complete visual envelope / 41 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 14 | First | *The Bear* S01E07 | ACCEPTED_TARGET | `BEAR-S01E07-REVIEW-001` / CURRENT_LOCAL_EVIDENCE | One complete visible-shot envelope; production-take status UNKNOWN | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 15 | First | *Brooklyn Nine-Nine* S05E13–14 combined source | ACCEPTED_TARGET | `B99-S05E14-THE-BOX-PRIDE-BAIT-CONFESSION-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 22 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 16 | First | *Brooklyn Nine-Nine* S05E03–04 combined source | RETAINED_EXTRA_SOURCE | NO_SCENE_EVIDENCE | S05E04 candidate range located; no complete shot evidence unit | NOT_DIRECTLY_AUDITIONED | NO | G2, G5 |
| 17 | Post-16 | *Citizen Kane* (1941) | ACCEPTED_TARGET | `CITIZEN-KANE-1941-BREAKFAST-MONTAGE-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 27 edit-shot units | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 18 | Post-16 | *The Wire* S01E04 | ACCEPTED_TARGET | `WIRE-S01E04-OLD-CASES-001` / CURRENT_LOCAL_EVIDENCE | Complete visual envelope / 68 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 19 | Post-16 | *Chernobyl* S01E05 | ACCEPTED_TARGET | `CHERNOBYL-S01E05-HEARING-RECON-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 205 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 20 | Post-16 | *Andor* S01E10 | ACCEPTED_TARGET | `DM-ANDOR-S01E10-SEL-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 121 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 21 | Post-16 | *Better Call Saul* S03E05 | ACCEPTED_TARGET | `BETTER-CALL-SAUL-S03E05-PUBLIC-PROOF-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 105 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 22 | Post-16 | *The Bear* S02E07 | ACCEPTED_TARGET | `BEAR-S02E07-TASK-CLOSED-LOOP-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 114 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 23 | Post-16 | *Apollo 13* (1995) | ACCEPTED_TARGET | `APOLLO-13-1995-CONSTRAINED-MATERIAL-HANDOFF-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 12 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 24 | Post-16 | *Sicario* (2015), verified replacement | ACCEPTED_TARGET / former wrong receipt already removed by user | `SICARIO-2015-BORDER-CHECKPOINT-001` / CURRENT_LOCAL_EVIDENCE | Complete visual envelope / 96 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 25 | Post-16 | *The Martian* (2015) | ACCEPTED_TARGET | `MARTIAN-MULTI-SPACE-OBJECT-STATE-EDITORIAL-SEQUENCE-LOCAL-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 59 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 26 | Post-16 | *True Detective* S01E04 | ACCEPTED_TARGET | `TRUE-DETECTIVE-S01E04-MULTI-ZONE-MOBILE-ROUTE-001` / CURRENT_LOCAL_EVIDENCE | One complete visible-shot envelope; production-take status UNKNOWN | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 27 | Post-16 | *Unbelievable* S01E02 | ACCEPTED_TARGET | `UNBELIEVABLE-S01E02-CONTAINED-TWO-PERSON-SEQUENCE-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 77 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 28 | Post-16 | *The Haunting of Hill House* S01E06 | ACCEPTED_TARGET | `DM-EVID-HH-S01E06-ENSEMBLE-CONTINUOUS-REFRAMING-V0.1` / CURRENT_LOCAL_EVIDENCE | One partial-at-end visible-shot analytical envelope; endpoint and production-take status UNKNOWN | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 29 | Post-16 | *Sound of Metal* | ACCEPTED_TARGET | `SOUND-OF-METAL-SIGNAL-STATE-EE-V0.1` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 25 visible shots | DIRECT_AUDITION_COMPLETE | NO | G7 |
| 30 | Post-16 | *Children of Men* (2006) | ACCEPTED_TARGET | `CHILDREN-OF-MEN-2006-MOVING-CAR-EXTERIOR-DISRUPTION-001` / CURRENT_LOCAL_EVIDENCE | One complete visible-shot envelope; production-take status UNKNOWN | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 31 | Post-16 | *Moonlight* (2016) | ACCEPTED_TARGET | `MOONLIGHT-2016-TWO-APPEARANCE-MULTI-ZONE-EDITORIAL-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 79 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 32 | Post-16 | *Bodyguard* S01E01 | ACCEPTED_TARGET | `DM-BODYGUARD-S01E01-SEL-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 211 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |
| 33 | Post-16 | *Mr. Robot* S04E07 | ACCEPTED_TARGET | `MRR-S04E07-ACT-FOUR-VISUAL-001` / CURRENT_LOCAL_EVIDENCE | Complete selected visual envelope / 201 visible shots | BLOCKED_DIRECT_AUDITION | NO | G2 |

## Current retention recommendation

- `RETAIN_FOR_REAUDIT`: `31` current-local evidence sources. Their picture analysis is preserved in JSON. Direct sound audition remains incomplete for 30; *Sound of Metal* has one directly auditioned selected envelope but still lacks a separate deletion/recovery decision. The full sources remain the only complete route to re-check picture or sound.
- `RETAIN_UNTIL_ANALYZE_OR_ABANDON`: `1` extra *Brooklyn Nine-Nine* source with no complete evidence unit.
- `DELETE_CANDIDATE_PENDING_USER_CONFIRMATION`: `1` *Better Call Saul* S01E09-labelled source. It is unusable for the requested target scene, but it is not deleted or authorized for deletion by this report.

Thus the current operational disposition is `32 RETAIN / 1 DELETE_CANDIDATE_PENDING_USER_CONFIRMATION / 0 DELETED`. “Delete candidate” is a recommendation for a separate exact-file confirmation, not a claim that deletion is currently safe or authorized.

## Deletion decision gate

No original is currently declared safe for direct deletion. A source can enter a later delete-candidate list only after all applicable conditions below are proven:

1. Its accepted analysis is present in the current branch, converted to canonical JSON, and passes the repository validator without hiding UNKNOWN facts.
2. All evidence and rule references resolve; the corpus-wide broken-reference count is zero.
3. Sound has either been directly auditioned and recorded with exact source-local timecodes, or the user explicitly accepts a documented local-only preservation substitute and the loss of future full-source re-auditability.
4. Any retained source without a complete evidence unit receives a final retain/analyze/abandon disposition. The rejected BCS source receives a separate explicit deletion decision; rejection alone is not deletion authorization.
5. The source-to-evidence inventory is re-counted immediately before deletion, and the user approves the exact source list in a separate step.

## Rollback principle

- Prefer a verified external archive or a recoverable move to Trash before permanent deletion.
- Keep any local-only re-audit bundle outside the public repository and verify it opens before removing the full source.
- Do not permanently empty Trash in the same action as the first removal check.
- If the exact target, backup, or unique evidence ownership cannot be proven, retain the source and report the blocker.

## Self-consistency check

| Check | Result |
|---|---:|
| Register rows | 33 |
| First-batch rows | 16 |
| Post-16 rows | 17 |
| Accepted or retained | 32 |
| Target-scene rejected | 1 |
| Current-local evidence | 31 |
| Old-PR-only evidence | 0 |
| No scene evidence | 2 |
| Directly auditioned | 1 |
| Signal measured but not auditioned | 0 |
| Broken artifact claims still asserted as present | 0 |
| Explicit absent-legacy-artifact records | 13 |
| Pending downloads | 0 |
| Currently authorized for direct deletion | 0 |

The arithmetic closes: `16 + 17 = 33`, `32 + 1 = 33`, and `31 + 0 + 2 = 33`.
