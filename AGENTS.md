# DirectorMind Agent Contract

Before work, read in order:

1. `context/00_START_HERE.md`
2. `context/STATE.md`
3. the relevant Skill under `skills/`

## Evidence boundary

- `OBSERVED` requires visible or audible evidence from a cited local clip and exact clip/shot timecodes.
- `INFERRED` is an interpretation supported by observed shots.
- `UNKNOWN` remains unknown when the clip, cut, focus change, sound cue, or production method cannot be verified.
- A synopsis, genre label, screenplay, subtitle, textbook, director interview, or model guess cannot prove a shot fact.
- A single occurrence is a candidate, never a universal rule. Record counterexamples and failure conditions.

## Public-repository boundary

Do not commit source video/audio, film or TV stills, contact sheets, copyrighted scripts or long dialogue, private production scripts/IR, credentials, cookies, signed URLs, or personal data. Source media remains local. Commit only original analysis, small paraphrased evidence, schemas, code, and rights-safe documentation.

Do not copy reference characters, costumes, locations, props, signature compositions, or scene events into generation instructions. Extract decision logic, not surface imitation.

## Collaboration

- Work on a `codex/<host>-<topic>` branch; do not push research work directly to `main`.
- Pull before choosing a scene and search existing evidence IDs to avoid duplicate work.
- One evidence file owns one continuous scene. Do not overwrite another agent's evidence file; correct it through an explicit audit note or follow-up commit.
- Grammar changes must cite evidence IDs and preserve status, triggers, boundaries, counterexamples, AI risks, and confidence.
- Structural validation is not human creative approval, generation authorization, or proof of audience performance.

Run the smallest relevant validation before committing. Keep raw-media processing outside the repository.
