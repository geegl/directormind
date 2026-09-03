# Runtime Rule Promotion Wave 1 — Evidence Review

Updated: 2026-09-03

Status: `ROOT_VIDEO_REVIEW_RECORDED / INDEPENDENT_RE_REVIEW_PASSED`

The canonical authority is
`research/grammar/runtime_rule_promotion_wave1.review.json`. This document is a
human-readable review view. Real local video was reopened and exact canonical
Shot intervals were checked at start, midpoint and end. The host did not provide
`ffmpeg`/`ffprobe`, so the equivalent local decode/frame inspection used Apple's
AVFoundation. Temporary review images were kept outside the repository.

Three short visible subtitles were reviewed only to establish broad scene
context; the repository retains paraphrases rather than subtitle text. Semantic
audio was not auditioned. All promoted rules therefore declare
`audio_dependency=false` and contain no sound conclusion.

## DR-PERFORMANCE-OWNER-HOLD

- Family/problem: `SCREEN-OWNERSHIP-AND-PERFORMANCE-HOLD` / `INTERROGATION`.
- Promotion source: *Mr. Robot* S04E07. The natural scene is bounded by S001 and
  S201. S194 (`00:45:46.827–00:46:54.228`), S197
  (`00:47:05.865–00:47:47.907`) and S199
  (`00:47:54.789–00:48:15.059`) visibly move from registered relation coverage
  into long clean performance-owner singles. Start/mid/end frames show posture,
  gaze and facial-state progression without a required concurrent task state.
- Text boundary: one short paraphrased visible-text anchor inside S197
  (`00:47:26.800–00:47:29.000`) establishes direct questioning; all other
  dialogue meaning and all sound remain unknown.
- Cross-work support: *Better Call Saul* S03E05 S082 and S097–S098
  (`00:45:45.083–00:47:31.750`) first registers the two-person spatial
  relation, then holds a clean owner single before returning to relation
  coverage.
- Excluded adjacent evidence: *Brooklyn Nine-Nine* S05E14 S016
  (`00:42:02.958–00:42:20.083`) sustains an owner-dominant OTS, but retains the
  counterpart's foreground shoulder. It is not counted as cross-work support
  for the clean-single decision.
- Real boundary: *The Devil Wears Prada* S016 and S019
  (`00:20:26.000–00:20:48.958`) require concurrent material and other-body task
  state. A clean isolated hold would hide required information, so shared work
  coverage and selective checks are the fallback behavior.
- Director decision changed: after relation registration, delay routine receiver
  cuts and give the principal visible progression a sustained clean single.
- Original tests: `ORIGINAL-PERFORMANCE-OWNER-HOLD` selects the rule and changes
  Coverage, Pacing and Edit; `ORIGINAL-PERFORMANCE-CONCURRENT-STATE` rejects it.

## DR-RELATION-RESET-AFTER-SPATIAL-CHANGE

- Family/problem: `SPATIAL-REGISTRATION-AND-RESET` /
  `RELATIONSHIP_FRACTURE`.
- Promotion source: *Marriage Story*. S049
  (`01:35:25.833–01:35:38.958`) registers the two-person room relation; S058–S061
  (`01:36:04.542–01:36:44.708`) carry sitting/standing and zone changes; S082–S085
  (`01:40:53.292–01:41:26.792`) preserve the changed level-and-distance endpoint.
- Text boundary: one short paraphrased visible-text anchor inside S071
  (`01:38:29.800–01:38:31.500`) records direct personal conflict; other dialogue
  meaning, emotional cause and all sound remain unknown.
- Cross-work support: *The Last of Us* S01E06 S015–S019
  (`00:41:10.125–00:41:40.167`) moves from a shared seated relation through a
  standing change and back to a readable shared geometry.
- Real boundary: *The Social Network* S090–S091
  (`00:03:55.860–00:04:03.618`) shows the second occupancy change only after the
  counterpart has left; a fixed room anchor is sufficient, so a two-person reset
  is not applicable.
- Director decision changed: keep mover, counterpart, route and endpoint in a
  readable relation frame whenever a material spatial change invalidates the old
  geometry.
- Original tests: `ORIGINAL-RELATIONSHIP-FRACTURE` selects the rule and changes
  Blocking, Coverage and Edit; `ORIGINAL-SPATIAL-CHANGE-WITHOUT-COUNTERPART`
  rejects it.

## DR-SHARED-FRAME-FOR-RELATION-ENDPOINT

- Family/problem: `PROXIMITY-AND-RELATION-GEOMETRY` / `ROMANTIC_PROXIMITY`.
- Promotion source: *Bridgerton* S02E05. S001
  (`00:42:07.380–00:42:14.253`) registers separation; S024–S026
  (`00:43:40.973–00:44:07.834`) show an approach in shared coverage and hold the
  changed non-contact endpoint.
- Text boundary: one short paraphrased visible-text anchor inside S017
  (`00:43:03.336–00:43:05.338`) establishes relationship stakes; motive,
  consent, exact contact and all sound remain unknown.
- Cross-work support: *Marriage Story* S082–S085
  (`01:40:53.292–01:41:26.792`) makes a continuous level/distance change and its
  shared endpoint readable.
- Real boundary: *Citizen Kane* S001 versus S026–S027
  (`00:51:52.000–00:54:13.750`) separates early and late distance states through
  many intervening edits. Only terminal geometry is required; the rule must not
  invent a continuous approach.
- Director decision changed: keep the continuous path and two-person endpoint in
  one readable shared frame, while refusing to infer contact.
- Original tests: `ORIGINAL-PROXIMITY-TENSION` selects the rule and changes
  Coverage, Blocking, Pacing and Edit; `ORIGINAL-PROXIMITY-ELLIPSIS` rejects it.

## Evidence boundary

Picture observations support only the cited visible geometry, duration, body
state, coverage and edit facts. Scene problems, functional roles and mechanism
transfer are explicitly inferred from those facts and the three limited text
anchors. Lens choice, intention, off-frame action, cross-cut identity, uncited
dialogue, semantic sound, creative merit and audience response remain unproved.
