# DirectorMind Context Pack

Updated: 2026-08-30

## Objective

Build a general, model-neutral Director IR research and compilation system that can take a locked literary scene and decide:

- where shots begin and end;
- POV and audience identification;
- spatial geometry, axis, framing, and coverage;
- actor blocking, entrances, exits, and reaction priority;
- pacing, holds, interruptions, edit motivation, and sound strategy;
- continuity ownership, composite layers, AI complexity, and safer fallbacks.

Seedance and H3 adapters, generation calls, and generated-result review are separate downstream concerns. Their syntax must not shape the core directing decisions.

## Why this repository exists

The first working compiler was developed for a 36-episode AI-photoreal short drama and tested with two Golden Cases. Good Omens scenes supplied the first real-shot evidence. That proved the intermediate representation is useful, but not that one show's grammar or two project episodes cover directing in general.

The next phase therefore expands by **scene problem**, not by copying director aesthetics or trying to enumerate every genre. The ten-series market snapshot is a provisional demand signal from 10 shows/720 episodes, not a map of the whole US short-drama market.

## Canonical sources in this repo

| Purpose | Source |
|---|---|
| Compiler behavior | `skills/drama-director-compiler/SKILL.md` |
| IR field contract | `skills/drama-director-compiler/references/director-ir-contract.md` |
| Machine contract | `skills/drama-director-compiler/references/director-ir.schema.json` |
| Baseline real-shot evidence | `research/evidence/good-omens/GOOD_OMENS_DIRECTOR_EVIDENCE_V0.1.md` |
| Seed grammar | `research/grammar/director_grammar_seed_v0.1.json` |
| Coverage and research gaps | `research/coverage/SCENE_PROBLEM_MAP.md` |
| New evidence format | `research/evidence/EVIDENCE_TEMPLATE.md` |
| Private forward-test lessons | `context/research-seeds/PROJECT_FORWARD_TEST_LESSONS.md` |
| Short-drama mechanism snapshot | `context/research-seeds/TEN_SERIES_NARRATIVE_MECHANISMS_SNAPSHOT.md` |
| Live status | `context/STATE.md` |

## Research loop

1. Diagnose the highest-value missing scene problem from the coverage map.
2. Research candidate films/series and locate an exact continuous scene. Prefer contrasting works over many near-duplicates.
3. Record why the scene can test a directing question before analyzing it.
4. Use the legally available local clip. Do not assume native video understanding: inspect metadata, extract cut-aligned frames/contact sheets with `ffprobe`/`ffmpeg`, and inspect audio or transcript when needed.
5. Produce full cut coverage with exact timecodes and separate OBSERVED, INFERRED, and UNKNOWN.
6. Compare the scene against existing evidence. Record repeated pattern, single occurrence, counterexample, applicability, failure mode, and AI execution cost.
7. Add or revise a grammar rule only when evidence changes an actual directing decision. Keep uncertain rules as candidates.
8. Forward-test promoted rules on an original locked script without copying reference-film content.

## Completion standard for one evidence scene

- exact work, season/episode when applicable, clip start/end, and continuous-scene status;
- complete shot table with no unaccounted cut intervals;
- scene dramatic structure, coverage/geometry, editing rhythm, sound, and performance beats;
- evidence IDs and timecodes for every important conclusion;
- transfer conditions, counterexamples, UNKNOWN items, and AI-safe fallback;
- no raw copyrighted media or stills committed.

## Current non-goals

- claiming a complete universal directing ontology;
- ranking directors or reproducing a named director's signature look;
- writing Seedance/H3 prompts inside the compiler;
- publishing private project scripts, episode IR, or source media;
- equating English-language content with US audience performance.
