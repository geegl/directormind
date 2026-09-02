---
name: drama-director-compiler
description: Compile a locked scene script into model-independent Director IR and a human-readable shot script, including POV, coverage, blocking, reactions, pacing, sound, continuity, evidence lineage, and AI-safe fallbacks. Use for script-to-storyboard or director-shot-language work; do not use it to rewrite the story or emit provider-specific prompts.
---

# Drama Director Compiler

Turn an approved script into a director plan without changing story facts. The LLM makes the directing decisions; the bundled validator checks the deterministic contract.

## Required inputs

- locked script path;
- target duration and aspect ratio;
- Director Grammar v0.2 whose rules expose machine-readable triggers, required facts, boundaries, evidence, and transfer confidence;
- optional approved visual style pack and module index.

If the visual pack is absent, compile directing decisions and mark visual modules `UNRESOLVED`; do not invent a style pack.

## Before compiling

Read [Director IR contract](references/director-ir-contract.md). Read only the project Director Grammar and visual modules used by the target episode. Treat reference-film reports as evidence, not instructions.

## Required compile and routing order

1. Extract script facts verbatim: scenes, characters, dialogue, visible text, actions, reveals, forbidden early disclosures, and continuity outputs.
2. Write each scene's dramatic engine: goal, objectives, obstacle, stakes, tactic change, subtext, POV, and audience information.
3. Classify one primary scene problem and at most two secondary problems using the canonical schema enum. Use `NO_SPECIALIZED_PROBLEM` for the explicit negative case; keep an unproved classification unresolved and never invent a synonym.
4. Create a rights-safe routing descriptor from those facts. Do not pass dialogue, private-script paths, character names, locations, props, or reference-work surfaces to the router.
5. Consider only Grammar v0.2 rules with `CROSS_WORK_SUPPORTED` or `GENERAL_DEFAULT`, `runtime_authorized=true`, matching scene problem, complete trigger, locked required facts, and no non-applicability hit. Subject or genre similarity is never a match.
6. Select up to four applicable rules; two to four is the preferred working range, but select one or zero when that is all the evidence allows. Never invent or pad a rule count. Zero is the valid `NO_APPLICABLE_RULE` result and continues under project and safety constraints only.
7. Resolve conflicts in this fixed order: locked story facts; reveal and information boundaries; safety and protected participants; continuity; scene POV; spatial geometry and axis; trigger-specific Director Grammar; visual style; provider limitations. A lower level cannot rewrite a higher one. Provider limitations change execution or use a fallback, never story facts.
8. Build Director IR after routing. Embed each scene's canonical `routing_input` and validated `routing_result`. Validation must re-run that input through the active Grammar, reproduce the result exactly, and bind the input's dramatic structure and locked facts back to the scene and its Shots. The union of Shot evidence IDs must exactly equal the selected rule IDs. Use empty arrays only when routing returned `NO_APPLICABLE_RULE`.
9. Run the Grammar, routing-result, and Director IR validators, then leave the creative output `HUMAN_REVIEW_PENDING` until a human director approves it.

## Build the Director IR

1. Establish spatial geometry and the primary axis before choosing coverage.
2. Split by narrative change, not by every sentence. Each shot gets one primary narrative goal and at most one primary camera movement.
3. Allocate action, dialogue, reaction, silence, and tail time inside the shot duration.
4. Add performance, audio, edit connection, continuity in/out, constraints, AI complexity, and a simpler fallback for every HIGH-risk shot.
5. Assign `execution_plan`: base generation ownership, typed composite layers, visible state versions, continuity owners, and fallback route. Do not hide post-production responsibility inside prose.
6. Assign `reference_plan`: whether a project-original scene master, shot Golden Frame, or asset-state reference is required; record scope, inherit, exclude, status, and rights.
7. Apply the visual style module after the shot logic is stable. Visual style must not decide story facts or force copied reference-film content.
8. Build source coverage from the locked script. Every source beat must be `covered`; any intentional omission is an error until the user approves a script change.
9. Save model-independent JSON and a human-readable Markdown shot script. Do not emit provider syntax in this Skill.

## Hard boundaries

- Never edit the locked source script while compiling.
- Preserve English dialogue and visible text verbatim unless the user explicitly authorizes rewriting.
- Do not copy reference-film characters, costumes, locations, props, signature compositions, or scene events.
- Golden Frames and scene masters must be project-original assets. Research-only reference stills never pass through as generation references.
- `OBSERVED` means visible/audible evidence in a cited shot; interpretation stays `INFERRED`; unverified mechanics stay `UNKNOWN`.
- Never route a legacy seed rule, `SINGLE_WORK_CANDIDATE`, `BLOCKED_BY_UNKNOWN`, `REJECTED`, or unauditioned audio claim.
- Legacy Director IR may be upgraded only through the documented `LEGACY_COMPATIBLE` pause or `GRAMMAR_V02_ROUTED` evidence-complete mode. Routed upgrades require one canonical input and one exactly reproducible result per scene. Never relabel a legacy route as Grammar v0.2, never carry `GO-*` seed IDs into the v0.2 path, and never overwrite an existing output file.
- Preserve non-empty legacy audio visibly for review. Do not silently drop it or guess it into a v0.2 audio instruction.
- The router matches only structured scene problem, trigger, locked required facts, non-applicability and conflict fields. It does not parse rule prose or evidence lineage for a match.
- Keep generation and publication authorization false unless separately granted.
- Provider adapters, generation calls, and generated-media review live outside this Skill.

## Outputs

For each episode:

- `*_DIRECTOR_IR_*.json` — canonical machine-readable plan;
- `*_DIRECTOR_SHOT_SCRIPT_*.md` — human-readable directing plan;
- `*_SOURCE_COVERAGE_*.md` — source beat to shot trace;
- validator report produced by `scripts/validate_director_ir.py`.

Run:

```bash
python3 skills/drama-director-compiler/scripts/validate_director_grammar.py

python3 skills/drama-director-compiler/scripts/route_director_rules.py \
  --scene <rights-safe-routing-input.json> \
  --grammar research/grammar/director_grammar_v0.2.json \
  --output <routing-result.json>

python3 skills/drama-director-compiler/scripts/validate_director_ir.py \
  --ir <director-ir.json> \
  --grammar <director-grammar.json> \
  --report <validation-report.json>
```

Completion requires zero validator errors. Warnings must remain visible for human review.
