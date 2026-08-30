# Canonical First 16 — macOS Local Material Manifest

Updated: 2026-08-30

This manifest records only what can currently be opened from the local movie directory. It does not place media in the repository and does not promote locator estimates to shot evidence.

Current count:

- 15 canonical sources are locally present, including the already completed *Succession* source.
- 1 canonical source, *Fleabag* S02E01, is `USER_SKIPPED_SOURCE_UNAVAILABLE`.
- 0 canonical sources remain pending download.
- The additional combined *Brooklyn Nine-Nine* S05E03–04 file is not the requested S05E14, but S05E04 contains a useful second-wave scene and should be retained.

## Canonical scene status

| ID | Local filename | Local status | Local boundary / audit note |
|---|---|---|---|
| `TSN-OPEN` | `社交网络_The_Social_Network_2010_BD720P_X264_AAC_English_CHS_ENG_BD.mp4` | LOCAL_PRESENT | Opening breakup is present; the continuous scene ends near `00:04:20`, substantially earlier than the corpus locator estimate. Exact cut boundary pending. |
| `DWP-CERULEAN` | `穿普拉达的女王_The_Devil_Wears_Prada_2006_BD720P_X264_AAC_English_CHS_ENG.mp4` | LOCAL_READY | Verified local range `00:20:14.833–00:21:24.917`. |
| `SUCCESSION-VOTE` | `继承之战S01E06.mp4` | EVIDENCE_COMPLETE_V0.1 | Verified local range `00:47:03.500–00:52:33.042`; evidence is on PR #1. |
| `FLEABAG-DINNER` | — | USER_SKIPPED_SOURCE_UNAVAILABLE | User confirmed the episode cannot be downloaded. Do not block the corpus on this scene and do not substitute subtitles or synopsis. |
| `BCS-CHUCK` | `风骚律师S01E09.mp4` | LOCAL_PRESENT | Reveal is visible around `00:42:00–00:43:20` in this edition; the corpus locator estimate runs into the following scene. Exact boundary pending. |
| `TED-DARTS` | `足球教练_第一季_2020_EP08_HD1080P_X264_AAC_English_CHS_ENG_BDYS.mp4` | LOCAL_PRESENT | Correct S01E08 file is now visible locally; scene identity and exact boundary pending. |
| `GETOUT-HYPNOSIS` | `逃出绝命镇.mp4` | LOCAL_READY | Verified local range `00:31:15.333–00:36:47.750`. |
| `AQP-BIRTH` | `寂静之地.mp4` | LOCAL_PRESENT | Labor is visible by `00:50:18`; the action continues beyond the original `00:53:40` estimate. Fireworks, birth, and final boundary still require calibration. |
| `NOBODY-BUS` | `小人物.mp4` | EVIDENCE_COMPLETE_VISUAL_V0.1 / SOUND_UNKNOWN | Verified natural local range `00:24:53.000–00:32:16.267`; 128 manually accepted visible shots. Strong for action causality/geography/state ledgers, PARTIAL for micro-performance and sound because the source is `856x480` and audio was not auditioned; see `NOBODY-2021-BUS-001`. |
| `MARRIAGE-ARGUMENT` | `婚姻故事.mp4` | LOCAL_PRESENT | Argument is underway by `01:34:00`, continues through roughly `01:41:36`, and has ended by `01:42:00`. Exact boundary pending. |
| `KNIVES-WILL` | `利刃出鞘.mp4` | LOCAL_PRESENT | Will-room setup is present by `01:07:21`; reveal and reaction cascade run to before the exterior cut near `01:12:00`. Exact boundary pending. |
| `TLOU-BEDROOM` | `最后生还者.mp4` | LOCAL_PRESENT_WITH_OVERLAY | Correct S01E06 scene; local argument is approximately `00:40:15–00:44:00`, with an exterior cut by `00:44:15`. A persistent top-edge source overlay is present. |
| `HOTD-THRONE` | `龙之家族S01E08.mp4` | LOCAL_PRESENT | Newly visible locally. The plea, Viserys entrance, throne walk, and ruling occupy approximately `00:35:50–00:44:50`; select the continuous evidence boundary before shot logging. |
| `BRIDGERTON-BANE` | `布里奇顿S02E05.mp4` | LOCAL_PRESENT | Target interaction begins around `00:42:25`; confession and near-contact continue through roughly `00:44:30`, with aftermath to about `00:45:10`. Exact boundary pending. |
| `BEAR-ORDERS` | `熊家餐馆S01E07.mp4` | EVIDENCE_COMPLETE_VISUAL_V0.1 / SOUND_UNKNOWN | Verified local range `00:02:22.768–00:19:31.379`: one visible shot from the interior hard cut to the credits hard cut. Invisible stitching and all sound facts remain `UNKNOWN`; see `BEAR-S01E07-REVIEW-001`. |
| `B99-CONFESSION` | `神烦警探S05E13-14.mp4` | LOCAL_PRESENT | S05E14 “The Box” is now present in a two-episode combined file. Verify the episode split and translate episode-relative locators before shot logging. |

## Additional local source retention decision

| Source | Decision | Candidate scene | Information gain |
|---|---|---|---|
| `神烦警探S05E03-04.mp4` | RETAIN | S05E04 “HalloVeen”, `CONTINUOUS_DRAMATIC_SEQUENCE_WITH_INTERNAL_INSERTS`, local range `00:38:01.328–00:40:57.831`; core reveal `00:39:18.204–00:40:48.789` | A competition object is reclassified as a proposal object; object reading, ring, kneeling, acceptance, embrace, and a late witness interruption remain causally ordered. This tests benevolent misdirection, relationship reclassification, reaction hold, and tonal landing; it is distinct from the S05E14 interrogation mechanism. |

S05E03 has a lower-priority candidate at `00:19:18.685–00:20:40.353`: an evaluated character's visible concession is followed by a handshake and status recognition. Its coverage is conventional and the turn depends heavily on unaudited dialogue, so it does not justify a separate evidence file before S05E04.

The combined source contains a visible SOTV mark and a top-edge Telegram promotion. They do not obscure the audited S05E04 subject action or cut points, but they remain local-source artifacts and must never enter repository media.

## Material handling

- Full-length source copies remain local and are never committed.
- Contact sheets and extracted frames are temporary local audit aids only.
- Acquisition should use a lawful full film or full episode available to the user. Availability by service or region is not asserted here.
- Every time range that is not explicitly marked `Verified local range` remains a locator estimate until a complete shot audit is performed.
