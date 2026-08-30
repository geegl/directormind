# Post-16 Local Material Manifest

Updated: 2026-08-30 14:27 +08:00

This manifest is a local receipt audit for `POST_16_ACQUISITION_BACKLOG.md`. It records source identity, container facts, and evidence-readiness only. It does not promote filenames, title cards, burned subtitles, synopsis, or locator estimates into shot or sound evidence.

## Current corpus closure

- Complete identity-matched files currently in the local `Movie/` corpus: `32` (`16` files from the first-corpus batch, including the retained *Brooklyn Nine-Nine* S05E03–04 double episode, plus `16` post-16 sources).
- Current identity-matched sources: `32`; current identity-rejected files: `0`; user-authorized replacement downloads not yet filesystem-visible: `1`.
- The former *Sicario* receipt failed picture identity and was removed by the user. One correct replacement is authorized and in progress; it remains outside the evidence pool until a completed file passes picture audit.
- Acquisition is closed except for that replacement. Anything else absent from `Movie/` is currently unavailable and skipped. The larger backlog remains a research reference, not an active download request.
- The earlier *Apollo Thirteen: Survival* documentary was deleted by the user. The completed local source is now the correct *Apollo 13* (1995) narrative feature.
- Raw downloader host labels, release strings, and source-site branding are intentionally omitted below. Media remains local and is never committed.

## Complete post-16 sources

| Target | Local receipt | Container audit | Identity boundary | Scene-problem status |
|---|---|---|---|---|
| *Citizen Kane* (1941) | `公民凯恩.mp4` | `01:59:23.834`; AVC `1920x1080`; `24.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_IDENTITY_VERIFIED`: visible source card and main title identify the work | `VISUAL_EVIDENCE_COMPLETE`: breakfast montage `00:51:52.000–00:54:13.750`, 27 contiguous edit/shot units, 21 hard-cut boundaries, five internal horizontal-blur/visible-overlap bridges; sound UNKNOWN |
| *The Wire* S01E04 | `火线S01E04.mp4` | `00:59:28.875`; AVC `1920x1080`; `24.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_WORK_AND_TARGET_MATCH`; exact season/episode number remains filename-supplied | `VISUAL_EVIDENCE_COMPLETE`: “Old Cases” `00:44:59.542–00:50:41.042`, 68 manually accepted visible shots; all sound remains `UNKNOWN` |
| *Chernobyl* S01E05 | `切尔诺贝利S01E05.mp4` | `01:08:24.960`; AVC `1920x1080`; `25.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_WORK_AND_TARGET_MATCH`; exact episode number remains filename-supplied | `LOCAL_PRESENT_BOUNDARY_REFINING`: trial/reactor reconstruction; technical explanation converted to visible causality |
| *Andor* S01E10 | `安多S01E10.mp4` | `00:42:47.750`; AVC `1920x1080`; `24.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_TARGET_MATCH`; exact episode number remains filename-supplied | `LOCAL_PRESENT_BOUNDARY_REFINING`: prison uprising/broadcast and distributed command transfer |
| *Better Call Saul* S03E05 | `风骚律师S03E05.mp4` | `00:49:20.417`; AVC `1920x1080`; `24.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_SERIES_AND_SEASON_MATCH`; exact episode number remains filename-supplied | `LOCAL_PRESENT_BOUNDARY_REFINING`: public evidence reveal, witness reaction, and status reclassification |
| *The Bear* S02E07 | `熊家餐馆S02E07.mp4` | `00:34:55.917`; AVC `1920x1080`; `24.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_WORK_AND_TARGET_MATCH`; exact season/episode number remains filename-supplied | `LOCAL_PRESENT_BOUNDARY_REFINING`: training-to-live-service competence and delegated authority; contrast to S01E07 breakdown |
| *Apollo 13* (1995) | canonical local file; raw release label omitted | `02:19:51.077`; AVC `1920x1080`; `23.976 fps`; two AAC `6ch/24 kHz` tracks | `LOCAL_VISUAL_WORK_VERIFIED`: narrative NASA mission film with Tom Hanks is visibly present; audio-language allocation is unverified | `LOCAL_PRESENT_BOUNDARY_REFINING`: limited-material filter construction; successful remote procedure |
| *The Martian* (2015) | `2015.火星救援.mp4` | `02:21:37.619`; AVC `1280x720`; `23.976 fps`; AAC `2ch/24 kHz` | `LOCAL_VISUAL_WORK_MATCH`: Mars/HAB setting and selected procedure section are visibly present | `LOCAL_PRESENT_BOUNDARY_REFINING`: procedure plan → visible failure → correction |
| *True Detective* S01E04 | `真探S01E04.mp4` | `00:57:03.875`; AVC `1920x1080`; `24.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_TARGET_MATCH`; exact episode number remains filename-supplied | `LOCAL_PRESENT_BOUNDARY_REFINING`: continuous moving-geography assault/withdrawal sequence |
| *Unbelievable* S01E02 | `难以置信S01E02.mp4` | `00:46:15.334`; AVC `1920x1080`; `24.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_TARGET_MATCH`; exact episode number remains filename-supplied | `LOCAL_PRESENT_BOUNDARY_REFINING`: trauma-informed interview as coercive-interrogation counterexample |
| *The Haunting of Hill House* S01E06 | `鬼入侵S01E06.mp4` | `00:56:40.834`; HEVC `1920x1080`; `24.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_WORK_AND_TARGET_VERIFIED`; exact episode number remains filename-supplied | `LOCAL_PRESENT_BOUNDARY_REFINING`: funeral-home ensemble long-take and time-state transitions |
| *Sound of Metal* | canonical local file; raw release label omitted | `02:00:46.698`; AVC `1920x1080`; `23.976 fps`; AAC `2ch/48 kHz` | `LOCAL_VISUAL_WORK_MATCH`; picture matches the work but the audio was not directly auditioned | `LOCAL_PRESENT_SOUND_UNAUDITED`: subjective-hearing target remains `UNKNOWN` until an audio-capable evidence pass |
| *Children of Men* (2006) | `人类之子.mp4` | `01:40:25.253`; AVC `856x480`; `30.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_WORK_MATCH`: three separated picture samples match the intended work | `LOCAL_PRESENT_BOUNDARY_REFINING`: moving-car ambush and passenger/vehicle/exterior state continuity; lower resolution limits micro-expression claims |
| *Moonlight* (2016) | canonical local file; raw release label omitted | `01:50:25.118`; AVC `1920x1080`; `23.976 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_WORK_MATCH`: separated picture samples match the intended work and final-period meeting | `LOCAL_PRESENT_BOUNDARY_REFINING`: restaurant reunion, service-action buffer, distance, gaze, and restrained reconciliation |
| *Bodyguard* S01E01 | `贴身保镖01.mp4` | `00:57:39.167`; AVC `856x480`; `24.000 fps`; AAC `2ch/44.1 kHz` | `LOCAL_VISUAL_WORK_MATCH`; exact episode number remains filename-supplied | `LOCAL_PRESENT_BOUNDARY_REFINING`: train-bomb negotiation across suspect, passengers, police, marksmen, and remote command; lower resolution limits micro-expression claims |
| *Mr. Robot* S04E07 | canonical local file; raw release label omitted | `00:56:13.504`; AVC `1920x1080`; `23.976 fps`; AAC `6ch/48 kHz` | `LOCAL_VISUAL_TARGET_MATCH`: separated picture samples match the intended three-person session; exact season/episode remains filename-supplied | `LOCAL_PRESENT_BOUNDARY_REFINING`: coercive session, adjacent-room threat, memory reveal, and three-party power changes |

## Rejected receipt and authorized replacement

The former receipt was readable, but repeated picture samples did not match the intended canonical work. The user removed it and started one replacement download. The historical audit is retained only to prevent the wrong source from being treated as evidence.

| Intended target | Receipt state | Container audit | Picture audit | Execution status |
|---|---|---|---|---|
| *Sicario* (2015) | `FORMER_LOCAL_RECEIPT_REMOVED`; raw downloader label omitted | Former file: `01:28:13.321`; AVC `720x312`; `29.970 fps`; AAC `2ch/48 kHz` | `CANONICAL_IDENTITY_REJECTED`: early, middle, and late decoded frames showed an unrelated Japanese interior ensemble work | `USER_AUTHORIZED_REPLACEMENT_IN_PROGRESS_NOT_FILESYSTEM_VISIBLE`; no *Sicario* shot fact may be claimed until the replacement passes picture identity |

## Locator and evidence discipline

- Backlog ranges remain `LOCATOR_ESTIMATE` until the local edition receives a complete visible-cut audit and natural-boundary check; *The Wire* row and any subsequently completed evidence row are explicit exceptions for visual boundaries only.
- A filename, burned subtitle, synopsis, or release label cannot prove framing, movement, editing, performance, sound, or a scene boundary.
- An audio stream existing in the container does not prove language, mix, preserved ambience, or subjective sound design; those require direct audition.
- No source media, frame, contact sheet, subtitle, dialogue transcript, raw downloader label, or private material from this audit is committed.

## Evidence order within the closed corpus

1. *Citizen Kane* — first real-shot montage/time-compression evidence in the current map.
2. *The Bear* S02E07 — same-world successful-procedure contrast to the completed S01E07 breakdown.
3. *Better Call Saul* S03E05 — public proof, witness reaction, and object-driven identity reclassification.
4. *Apollo 13* — constrained-material successful procedure and remote teaching.
5. *Chernobyl* S01E05 — technical reconstruction across present testimony and past action.
6. *Andor* S01E10 — ensemble action and command transfer across multiple zones.
7. *The Martian* — procedure failure and recovery.
8. *Children of Men* — moving-vehicle continuity, hidden-transition uncertainty, and severe-event state tracking.
9. *Unbelievable* S01E02 — non-coercive interview counterexample.
10. *Bodyguard* S01E01 — multi-authority remote coordination inside a restricted public space.
11. *Mr. Robot* S04E07 — coercive three-party session and memory-driven scene reclassification.
12. *Moonlight* — restrained reunion, service-action buffer, and minimum-action intimacy.
13. *The Haunting of Hill House* S01E06 and *True Detective* S01E04 — two different continuous-geography stress tests.
14. *Sound of Metal* — retain for an audio-capable subjective-sound audit; picture alone cannot answer its primary research question.

*Sicario* remains excluded while its one authorized replacement is incomplete. No other acquisition is requested; all other absent works are skipped until the user explicitly reopens the corpus.
