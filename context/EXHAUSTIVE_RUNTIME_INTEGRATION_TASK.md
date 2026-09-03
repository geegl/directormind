# DirectorMind Exhaustive Runtime Integration Task

## Goal

Integrate every item in the closed local corpus into one auditable DirectorMind decision chain. The fixed corpus is 33 registered local sources, 31 canonical Scene Evidence records, 2,343 Shot/edit units, 124 candidate mechanisms, and 16 mechanism families.

The work does not end at a target number of positive rules. Every candidate must either become a positive runtime rule, support one, constrain one as a boundary/counterexample, merge into one as a duplicate, or be rejected for an evidence-backed reason that prevents future accidental promotion.

## Required candidate outcomes

- `POSITIVE_RUNTIME_RULE`
- `SUPPORTING_EVIDENCE`
- `BOUNDARY_OR_COUNTEREXAMPLE`
- `MERGED_DUPLICATE`
- `REJECTED_WITH_REASON`

`BLOCKED_BY_UNKNOWN` is never a final outcome. An unresolved material unknown is recorded as an evidence gap and makes the phase `PARTIAL_EVIDENCE_GAP`.

## Runtime meaning

- Positive candidates are the only candidates that create selectable Grammar rules.
- Supporting candidates contribute reviewed evidence and cross-work qualification to a positive rule.
- Boundary candidates create machine-matchable negative routing guards.
- Merged duplicates contribute reviewed lineage to one canonical positive candidate and never create a second selectable rule.
- Rejected candidates enter the runtime eligibility deny registry and cannot be reintroduced by editing a derived artifact.

## Scope boundaries

- Use only the already registered local corpus. Do not add or download works or media.
- Do not commit video, audio, stills, contact sheets, subtitles, long dialogue, local media paths, credentials, personal data, or private production material.
- Do not modify the private *Hell of a Dad* script or private IR.
- Do not generate Seedance/H3 prompts or media.
- Do not merge `main`.
- Keep legacy Markdown and the Wave 1 review as historical provenance; do not delete or overwrite them.
- Do not infer Shot facts from synopsis, subtitles, legacy prose, genre, or model knowledge. Fresh review must trace to exact canonical Shot IDs and timecodes.
- Do not encode copied characters, props, locations, costumes, events, or signature compositions in runtime instructions.

## Completion formula

`COMPLETE` is recomputed from canonical data and requires all of the following:

- 124/124 candidates have one allowed final disposition and a real runtime effect.
- 16/16 families have a machine-verifiable runtime role.
- 31/31 Scene Evidence records map to final candidate decisions.
- 33/33 registered sources have an explicit source disposition.
- No unresolved material evidence gap and no `BLOCKED_BY_UNKNOWN` remain.
- Every positive rule has fresh exact Shot/timecode evidence from at least two unrelated works, one real boundary/counterexample, machine-matchable triggers, three-axis AI risk, project-original fallback, and an explicit audio boundary.
- Every positive rule has an original positive and boundary forward test; routing changes at least one of Coverage, Blocking, Reaction, Pacing, or Edit.
- Every negative boundary demonstrably blocks the target rule when its locked-fact signal is present.
- Candidate Index, Support Matrix, Runtime Grammar, Router result, and Director IR remain exactly bound to the canonical review.
- Full tests, repository checks, diff checks, hosted CI, and a fresh family-by-family independent review pass.

If any material unknown cannot be closed from the existing corpus, the only honest phase result is `PARTIAL_EVIDENCE_GAP`, accompanied by a prioritized, precise supplementation list. It must not be described as complete.

## Current implementation authority

Root Agent is the sole writer of shared repository files. Read-only agents may inspect media, evidence, code, and tests, but may not edit shared files or sign the final independent review.

## Rollback

All repository work stays on `codex/exhaustive-runtime-integration`. Before merge, rollback is an ordinary branch deletion or commit revert. Local source media is never changed or deleted.
