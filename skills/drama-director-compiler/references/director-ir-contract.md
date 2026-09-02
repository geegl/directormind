# Director IR contract v0.2

Director IR is the model-independent boundary between a locked script and provider adapters. It records why a shot exists, how actors and camera behave, what must remain continuous, and which evidence supports non-obvious decisions.

## Top-level contract

Required fields:

- `schema_version`: `director-ir/0.2`;
- `project_id`, `episode_id`, `source_script`;
- `target_duration_seconds`, `duration_tolerance_seconds`, `aspect_ratio`;
- `status`: normally `DRAFT_FOR_HUMAN_REVIEW` before approval;
- `execution_medium`: `AI_PHOTOREAL_HUMAN` for this project;
- `dialogue_must_be_verbatim`, `generation_authorized`, `publication_authorized`;
- `director_grammar_path`, `visual_style_pack_path`;
- `source_facts`, `scenes`, `source_coverage`, `unresolved`.

The source script remains the story authority. Director IR may interpret presentation but cannot add, delete, reorder, or reveal story facts without an explicit approved deviation.

## Routing result and scene-problem vocabulary

All Scene Evidence, candidate, Grammar, routing-input, routing-result, Director IR, and forward-test schemas use the same canonical `scene_problem` enum. `NO_SPECIALIZED_PROBLEM` is the explicit negative sentinel; a caller may not introduce a synonym or an unregistered value.

Every Grammar v0.2 scene embeds both the canonical routing input and the full routing result: schema version, case ID, status, canonical scene problem, applied constraints, eligible rules, selected and rejected rules, conflict trace, selection count, IR handoff, human-review status, and rights boundary. Validation re-runs the embedded input through the active Grammar and requires the result to match exactly. The input's dramatic structure and ordered locked facts must also bind back to the scene and its Shots. The selected IDs must be a subset of eligible IDs, the count must agree, and their set must exactly match the union of Shot `evidence_rule_ids`. A paused, partial, mismatched, or malformed route cannot proceed as a v0.2 compilation.

## Scene contract

Each scene contains:

- stable `scene_id`, source-scene reference, title, duration and location/time;
- allowed characters;
- one narrative goal;
- dramatic engine: objectives, obstacle, stakes, open/close tactics, trigger, subtext;
- POV character, identification level, and audience information;
- spatial plan: geometry, axis, zones, entrances/exits, anchors, opening and closing positions;
- the canonical Grammar v0.2 `routing_input`, validated by `director-routing-input.schema.json` and bound to the scene's dramatic structure and locked facts;
- the validated Grammar v0.2 `routing_result`, freshly reproducible from that input and the active Grammar, with the same complete contract as `director-routing-result.schema.json`, kept at `HUMAN_REVIEW_PENDING` until human approval;
- ordered shots.

Use I/L/A staging as a planning vocabulary, not a mandatory pose. Establish a new axis only through visible movement, a camera crossing, or a new interacting subject.

## Shot contract

Each shot contains:

- `shot_id`, `order`, `duration_seconds`, `narrative_goal`;
- exact allowed characters and source references;
- shot type, framing, angle, camera start/path/end, focus strategy;
- blocking and visible performance beats;
- verbatim dialogue and visible text when present;
- audio, edit in/out, continuity in/out;
- three constraint groups: `must_hold`, `changes_here`, `must_not_appear`;
- AI complexity split into camera, performance, and continuity;
- `fallback` for HIGH-risk execution;
- `execution_plan` that assigns base generation, composite layers, state versions, continuity ownership, and a typed fallback route;
- `reference_plan` that declares any project-original reference frame requirement and its inherit/exclude scope;
- visual module ID or `UNRESOLVED`;
- Director Grammar evidence rule IDs, evidence status, and confidence. Across one scene, the union of Shot evidence IDs must exactly equal the embedded routing result's selected IDs. The arrays may be empty only when that result is `NO_APPLICABLE_RULE`; project and safety constraints remain active and must not be disguised as evidence rule IDs.

One shot has one primary narrative goal and no more than one primary camera movement. Static is a valid camera decision. `Top-Down` is an angle, not a movement. Rack focus is a focus change, not a zoom or dolly.

`camera_start`, `camera_path`, and `camera_end` are explicit contracts. A motion label without direction, speed, distance, stability, trigger, and endpoint is incomplete.

## Reaction and timing

An important event needs reaction space only when reaction changes audience understanding, relationship, or rhythm. Do not add reaction shots mechanically after every line. A reaction may occur inside a two-shot or held master.

Dialogue, action, reaction, silence, and tail time must fit inside the declared duration. Provider timing is outside this contract.

## Audio compatibility

New v0.2 audio uses `status`, `instruction`, and `source_refs`. During v0.1 upgrade, every non-empty audio object is preserved intact under `legacy_unmapped`, even when its old keys happen to share the new names. Validation keeps it visible as `IR-AUDIO-LEGACY-UNMAPPED`, and the deterministic renderer prints its complete stable JSON as `LEGACY_UNMAPPED`. A native v0.2 mixed object renders the standard contract plus every extra legacy field. This compatibility path preserves review data; it does not turn unauditioned audio into evidence or an executable instruction.

## v0.1 to v0.2 upgrade boundary

`upgrade_director_ir_v02.py` has two explicit modes:

- `LEGACY_COMPATIBLE` is the default safe path for v0.1 input only. Every v0.1 source receives a fresh complete `HUMAN_REVIEW_REQUIRED` / `PAUSE_FOR_HUMAN` marker even if the old payload contains a route-shaped object. The mode preserves its Grammar path, existing camera/execution/reference plans and cross-episode state, keeps v0.1 GO-01/GO-07 trigger behavior, removes only invalid uses of those two seed rules, and wraps non-empty old audio as unmapped review data. The pause is visible in rendered Markdown and does not claim Grammar v0.2 routing. A v0.2 source is rejected in this mode because its executable route cannot be trusted without replay.
- `GRAMMAR_V02_ROUTED` requires a target Grammar path whose actual JSON passes the repository Grammar schema, candidate authority, support-matrix and safety-constraint validator; one canonical routing input and one complete routing result per migrated legacy scene; and explicit evidence IDs for every legacy Shot. It re-runs every supplied input through the target Grammar and requires an exact result match. It rejects incomplete or paused results, cross-scene substitutions, forged eligible/constraint/rule sets, unknown scenes or shots, legacy `GO-*` IDs, wrong handoffs, and any mismatch between selected rules and Shot evidence IDs before writing output.

Neither mode invents a route. The CLI writes only to a new output path and refuses to overwrite any existing file, including the source IR, overrides file, or target Grammar file. A legacy-compatible pause must be reviewed and explicitly routed before it can enter the Grammar v0.2 compile path.

The routing CLI follows the same output boundary outside `--check`: `--output` may not resolve to the scene or Grammar input and may not already exist. It creates the new file exclusively so a path that appears between validation and writing is rejected instead of overwritten. `--check` only compares an existing result and never creates or changes a file.

## Evidence statuses

- `OBSERVED`: directly visible or audible in the cited source shot.
- `INFERRED`: interpretation supported by observed evidence.
- `HYPOTHESIS`: transfer proposal awaiting a project test.
- `UNKNOWN`: evidence absent or mechanism cannot be determined.

Director textbook methods are `METHOD_REFERENCE`, not proof that a specific reference-film shot used the method intentionally.

## AI complexity

Assess three dimensions separately:

- `camera`: camera path, focus transitions, lens/depth coordination;
- `performance`: dialogue, micro-expression, synchronized actions;
- `continuity`: identity, prop, geography, multi-character contact and state carry.

Every HIGH dimension requires a fallback that preserves narrative function with simpler execution. The fallback must be concrete, usually a split into safer shots, not a vague request to simplify.

## Execution ownership

`execution_plan` keeps five responsibilities explicit:

- `base_generation`: `AI_VIDEO`, `IMAGE_TO_VIDEO`, `STILL`, or `NONE`, plus the visible elements it owns;
- `composite_layers`: typed `SHADOW`, `LIQUID`, `SURFACE_STATE`, `TEXT`, `VFX`, or `OTHER` layers with a trigger and continuity key;
- `state_versions`: visible state IDs such as dry/damp/soaked wardrobe or closed/open prop state, their owner, the shot from which they apply, and whether they carry forward;
- `continuity_owners`: identity, surface, prop, and environment responsibility assigned to `BASE_GENERATION`, `COMPOSITE`, `EDIT`, `AUDIO`, or `SHARED`;
- `fallback_route`: `NONE`, `SPLIT_GENERATION`, `ROUTE_POST`, or `EDIT_RESTRUCTURE` with a concrete action.

Composite ownership does not authorize generation or post-production. It only prevents a downstream adapter from asking one model call to own incompatible layers.

## Project-original reference plan

`reference_plan` records:

- whether a reference is required;
- type: `SCENE_MASTER`, `SHOT_GOLDEN`, `ASSET_STATE`, or `NONE`;
- stable planned or approved reference ID;
- scope and `inherit` / `exclude` fields;
- status: `PLANNED`, `APPROVED`, or `NOT_REQUIRED`;
- rights status: `PROJECT_ORIGINAL` or `NOT_APPLICABLE`.

Research-only film stills can inform the visual style pack but cannot be named as generation references. A required but not-yet-created Golden Frame may remain `PLANNED` during storyboard compilation; generation remains blocked until the actual reference is approved.

## Validation boundary

The validator checks the full IR schema, canonical embedded routing input, exact Grammar replay, scene/fact binding, complete embedded routing-result schema, selection binding, shape, IDs, duration, evidence references, source coverage, placeholders, authorization, audio compatibility, and fallback presence. For Grammar v0.2, zero evidence rules is a valid constraints-only handoff only when the complete routing result is `NO_APPLICABLE_RULE`. It cannot judge acting quality, whether reported reference shots are accurate, or whether the visual style is aesthetically successful.
