# Wave 01 Scene-Problem Research Orchestration v0.1

Date: 2026-08-30
Branch: `codex/macos-scene-coverage-wave1`
Owner: second Research Root Agent
Status: `ACTIVE / FIRST_REVIEWABLE_UNIT`

## 1. Scope and evidence boundary

This wave expands model-neutral Director IR evidence by scene problem. It does not rank or imitate directors and does not define provider prompts. A title, synopsis, subtitle, screenplay, interview, or official clip description may locate a candidate, but cannot prove shot size, blocking, camera motion, focus, edit motivation, sound design, or performance.

Locator windows below have one of three statuses:

- `LOCAL_VIDEO_VERIFIED`: the actual local video was opened, its timebase was measured, and scene boundaries were checked against frames.
- `LOCATOR_ONLY`: the work/episode and rough event window are sufficient to request material, but every shot fact remains `UNKNOWN` until the local video is inspected.
- `OFFICIAL_CLIP_LOCATOR`: a rights-holder or licensed clip confirms that the intended event exists and offers a lawful preview; the clip must still be checked for editorial truncation before it can own a scene evidence file.

No source media, audio, subtitle file, keyframe, contact sheet, script, signed URL, or private IR belongs in this public repository.

## 2. Coverage audit before selection

### Verified repository state

- The only public reference-video family is *Good Omens*: four reports support seven transfer candidates.
- All seven `GO-*` rules are still `CANDIDATE` or `OPTIONAL_CANDIDATE`; none satisfies the cross-work promotion gate.
- Public revelation has only a ten-series mechanism signal, not public shot evidence.
- Procedural competence, action/pursuit/impact, and montage/time compression have no public real-shot evidence.
- Interrogation/threat, suspense/information asymmetry, horror rule revelation, and group power change have partial or method-only coverage.
- The private forward test does not publicly reproduce shot facts and cannot close these rows.

### Audit conclusions

1. The highest-value first unit is an ensemble decision under procedural pressure, not another two-person cozy or relationship scene.
2. The first wave needs contrast pairs, not ten isolated examples:
   - orderly procedural construction versus procedural collapse;
   - institutional self-incrimination versus intimate subjective coercion;
   - witness-chain revelation versus closed-room coalition failure;
   - readable confined action versus sound-led threat;
   - real-time escalation versus montage compression.
3. A local file lowers acquisition cost but does not override information gain. The already-local *The Social Network* opening is deferred because the repository already has a two-person fracture candidate; it becomes useful later as a fast-dialogue counterexample.
4. A single scene can only create a candidate rule. Wave 01 does not promote any new default grammar before cross-work comparison and an original forward test.

## 3. First-wave slate (10 works, one continuous scene each)

| Order | Scene problem | Work and continuous scene | Locator status and requested window | Gap filled / information gain over adjacent candidate | Lawful acquisition route | Material state |
|---:|---|---|---|---|---|---|
| 1 | Group power change; failed coalition; procedural status reversal | *Succession* S01E06, board no-confidence vote from formal vote call through removal orders | `LOCAL_VIDEO_VERIFIED` `00:47:03.500–00:52:33.042` in the current 24fps local file | The vote externalizes hierarchy through ordered hands, abstention, chair control, absence, entry, and expulsion. It is more diagnostic than the *House of the Dragon* throne-room entrance because power changes through procedure rather than spectacle or protector iconography. | User-supplied local copy; HBO/HBO Max is the official series home. Media stays local. | `EVIDENCE_COMPLETE_V0.1`; 88-shot file added in this branch |
| 2 | Calm authority pressure; monologue redirects group status | *The Devil Wears Prada* (2006), cerulean-sweater correction | `LOCAL_VIDEO_VERIFIED` `00:20:14.833–00:21:24.917` in the current local edition; the earlier `00:22:30–00:25:00` locator belongs to a different timebase/edition | Provides non-physical, non-supernatural coercion in a work setting. It contrasts with both a formal interrogation and the Good Omens threat scene by testing whether a quiet monologue can control witness reactions and end a challenge without overt blocking escalation. | Current local copy; Disney+ also lists the original film. | `LOCAL_READY`; event boundary checked against local frames, shot evidence pending |
| 3 | Procedural competence; constrained object transformation | *Apollo 13* (1995), CO2-filter “square peg” assignment and build handoff | `OFFICIAL_CLIP_LOCATOR`; licensed clip is 1:05 and the task line is reported around `01:20:33`; request a continuous local window around `01:20:20–01:22:10` and adjust to cuts | Adds readable process, material inventory, task ownership, and deadline without repetitive generic inserts. It is the orderly counterexample to *The Bear* and is more bounded than a multi-location medical diagnosis. | Licensed Movieclips preview (`TM & © Universal`) links to buy/rent; use a lawfully acquired local copy for full-scene evidence. | `MISSING_LOCAL_SOURCE` |
| 4 | Procedural collapse; multi-person blocking under continuous pressure | *The Bear* S01E07 “Review”, preorder flood and kitchen order breakdown | `LOCATOR_ONLY`, rough `00:04:20–00:09:20`; whole episode contains an approximately 18-minute unbroken real-time take, so final evidence boundary must be event-based | Tests whether geography and reaction priority can remain legible without cuts while work roles fail. Paired with *Apollo 13*, it separates “process is visible” from “process is comprehensible.” It has higher contrast value than another edited office meeting. | FX provides an official S1E7 “Kitchen Nightmare” scene and identifies Hulu as the full-episode route; request the lawful local episode for an untruncated evidence scene. | `MISSING_LOCAL_SOURCE` |
| 5 | Sound-led suspense; horror rule; simultaneous protection and action | *A Quiet Place* (2018), labor/fireworks diversion | `LOCATOR_ONLY`, rough `00:48:40–00:53:40`; verify edition offsets and hard boundaries locally | Tests sound-before-image, separated family geography, threat threshold, off-screen action, and a scripted diversion. It is more informative than a generic jump scare because a known sound rule controls blocking and edits. | Paramount+ lists the 2018 film and current streaming route; use an authorized local copy. | `MISSING_LOCAL_SOURCE` |
| 6 | One-against-many action causality; impact and recovery | *Nobody* (2021), bus fight from protective decision through main fight resolution | `OFFICIAL_CLIP_LOCATOR`, rough full-film `00:27:00–00:30:30`; Universal’s official 4K bus-fight clip is about 4:20 and must be checked for truncation | Confined bus topology makes entrances, exits, weapons, injuries, reversals, and aftermath countable. It is more useful for AI fallback design than a large exterior chase because the narrative function can be preserved through inserts, reaction shots, and split impacts. | Universal Pictures publishes the official full fight clip and buy/rent links. A local authorized copy is preferred if the official clip is editorially altered. | `MISSING_LOCAL_SOURCE` |
| 7 | Polite conversation becomes subjective coercion; POV threshold | *Get Out* (2017), hypnosis and “Sunken Place” transition | `LOCAL_VIDEO_VERIFIED` `00:31:15.333–00:36:47.750` in the current local edition; the bedroom wake-up begins at the end boundary | Adds a measurable transition from objective two-person talk to subjective perceptual loss, with a recurring object/sound trigger. It gives a stronger counterpoint to institutional interrogation than another prison interview because spatial and POV grammar itself changes. | Current user-supplied local copy; Universal Pictures At Home also lists authorized editions. | `LOCAL_READY`; event boundary checked against local frames, shot evidence pending |
| 8 | Institutional interrogation; ego bait triggers self-incrimination | *Brooklyn Nine-Nine* S05E14 “The Box”, final provocation and confession | `LOCATOR_ONLY`, rough `00:19:45–00:21:35`; verify episode master | Tests a confession produced by tactic change and listener management rather than violence. Its comedy/procedural tone is a high-value counterexample to prestige-thriller interrogation and helps detect which coverage choices belong to the problem rather than the genre. | Peacock states that all episodes are available; regional availability must be checked before acquisition. An authorized local episode is acceptable. | `MISSING_LOCAL_SOURCE` |
| 9 | Public revelation; distributed witness reaction chain | *Knives Out* (2019), will reading and inheritance reveal | `LOCATOR_ONLY`, rough `01:08:45–01:12:30`; verify local edition | Provides a large ensemble with unequal prior knowledge and several simultaneous status losses. Compared with *Succession*, the decisive fact comes from an external document rather than a live coalition, allowing a clean test of reveal order versus vote order. | Prime Video lists a Lionsgate rent/buy version in some regions; availability is region-specific. Use an authorized local copy and do not rely on the screenplay for shots. | `MISSING_LOCAL_SOURCE` |
| 10 | Montage, time compression, relationship transformation | *Citizen Kane* (1941), breakfast-table montage | `OFFICIAL_CLIP_LOCATOR`; Bowdoin Kinolab identifies a `00:02:14` educational library clip; rough feature locator `00:24:00–00:26:20` remains to be checked | Same table, repeated graphic/prop positions, and changing performance states isolate time-compression logic better than an athletic training montage, where locomotion and spectacle are confounds. It adds a needed counterexample to real-time escalation. | Use the Bowdoin library clip where access is lawful or an authorized TCM/digital/disc copy. Confirm that the clip is continuous and unabridged before evidence work. | `MISSING_LOCAL_SOURCE` |

## 4. Deferred candidates and reasons

| Candidate | Decision this wave |
|---|---|
| *The Social Network* opening breakup | `DEFER`: local and operationally cheap, but overlaps the existing two-person relationship-fracture row. Promote when a fast-dialogue power-transfer counterexample is needed. |
| *Fleabag* S02E01 dinner | `DEFER`: strong family reaction chain, but *Succession* plus *Knives Out* first establish two more distinct procedural/revelation mechanisms. |
| *Better Call Saul* S01E09 reveal | `DEFER`: a readable local episode is now available, but intimate betrayal still overlaps relationship-fracture evidence; S03E05 “Chicanery” remains a later public-proof candidate. |
| *Ted Lasso* S01E08 darts | `DEFER`: public reversal is useful, but the decisive proof is concentrated in one performer; *Knives Out* better tests distributed witnesses. |
| *The Last of Us* S01E06 bedroom rejection | `DEFER`: high emotional value but adjacent to the existing bandstand separation candidate. |
| *House of the Dragon* S01E08 throne-room entrance | `DEFER`: protector entrance and ceremonial spectacle are valuable later, after procedural group power has a non-spectacle baseline. |
| *Bridgerton* S02E05 confession | `DEFER`: intimacy-without-payoff remains medium priority and requires explicit consent/readability auditing. |
| *Marriage Story* apartment argument | `DEFER`: escalation is valuable, but the first wave prioritizes unsupported high-priority rows. |

## 5. One-time material manifest

The final local inventory check found five readable MP4 containers whose byte sizes remained stable during a five-second recheck:

1. *Succession* S01E06 — duration `00:58:43.417`, 1920×1080, 24fps; analyzed now.
2. *The Devil Wears Prada* — duration `01:45:55.500`; queued for exact boundary verification.
3. *The Social Network* — duration `01:59:06.285`; retained locally but deferred by information gain.
4. *Get Out* — duration `01:44:05.084`, 1920×1080, 24fps; Wave 01 event boundary verified.
5. *Better Call Saul* S01E09 — duration `00:47:22.917`, 1920×1080, 24fps; readable but deferred by information gain.

To complete the rest of Wave 01 in one acquisition pass, obtain authorized local copies or confirmed unabridged official clips for exactly these seven works:

- *Apollo 13* (1995)
- *The Bear* S01E07 “Review”
- *A Quiet Place* (2018)
- *Nobody* (2021)
- *Brooklyn Nine-Nine* S05E14 “The Box”
- *Knives Out* (2019)
- *Citizen Kane* (1941)

If a download already in progress completes, re-run the local inventory and remove that title from the outstanding count.

Source requirements:

- stable local file with readable video stream and original audio track when available;
- full continuous event, not a recap, trailer, fan edit, reaction video, or clip with hidden cuts;
- edition/runtime noted because distributor idents and credits shift feature timestamps;
- no DRM circumvention, unauthorized ripping, or downloader credentials;
- media remains outside Git; only basename, runtime, source hash, derived cut times, and original analysis may be committed.

## 6. Research order and promotion gate

1. Integrate and review `SUC-S1E6-BOARD-VOTE-01` as the first public cross-work evidence source.
2. Analyze the already-local cerulean scene only after its exact boundaries are verified.
3. Build the *Apollo 13* / *The Bear* procedural contrast pair.
4. Build the *A Quiet Place* / *Nobody* threat-action contrast pair.
5. Build the *Get Out* / *Brooklyn Nine-Nine* coercion-interrogation contrast pair.
6. Add *Knives Out* as the public-revelation counterexample to *Succession*.
7. Add *Citizen Kane* only when the unabridged montage source is lawful and local/inspectable.

No candidate becomes a reusable default until it has exact shot evidence, a cross-work repetition or strong counterexample, applicability and non-applicability conditions, a failure mode, `UNKNOWN` items, AI risk, concrete fallback, an original locked-script forward test, and human creative review.

## 7. Verification sources used only for selection and lawful routing

- HBO official series listing: <https://www.hbo.com/series/a-z>
- Disney+ official *The Devil Wears Prada* listing: <https://www.disneyplus.com/browse/entity-35ee3632-230a-4e4b-8520-46063f9282a3>
- Licensed *Apollo 13* Movieclips scene: <https://www.youtube.com/watch?v=ry55--J4_VQ>
- FX official *The Bear* selected scenes: <https://www.fxnetworks.com/shows/the-bear/scenes>
- Paramount+ official *A Quiet Place* listing: <https://www.paramountplus.com/movies/video/4CG9_JhUUUjCuRK_fNi8k_qepjaP8mgD/>
- Universal Pictures official *Nobody* bus fight: <https://www.youtube.com/watch?v=_2un1aU7mT0>
- Universal Pictures At Home official *Get Out* listing: <https://www.universalpicturesathome.com/movies/get-out>
- Peacock official *Brooklyn Nine-Nine* listing: <https://www.peacocktv.com/stream-tv/brooklyn-nine-nine>
- Prime Video *Knives Out* listing (availability varies by region): <https://www.primevideo.com/-/zh/detail/0QD6PFD8OU1PVD62Y0CJYI7OD3>
- Bowdoin Kinolab *Citizen Kane* clip catalogue: <https://kinolab.org/Film.php?id=47>

These sources verify title/episode availability, licensed clip identity, or acquisition route only. They are not shot evidence.
