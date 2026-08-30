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

## Scene contract

Each scene contains:

- stable `scene_id`, source-scene reference, title, duration and location/time;
- allowed characters;
- one narrative goal;
- dramatic engine: objectives, obstacle, stakes, open/close tactics, trigger, subtext;
- POV character, identification level, and audience information;
- spatial plan: geometry, axis, zones, entrances/exits, anchors, opening and closing positions;
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
- Director Grammar evidence rule IDs, evidence status, and confidence.

One shot has one primary narrative goal and no more than one primary camera movement. Static is a valid camera decision. `Top-Down` is an angle, not a movement. Rack focus is a focus change, not a zoom or dolly.

`camera_start`, `camera_path`, and `camera_end` are explicit contracts. A motion label without direction, speed, distance, stability, trigger, and endpoint is incomplete.

## Reaction and timing

An important event needs reaction space only when reaction changes audience understanding, relationship, or rhythm. Do not add reaction shots mechanically after every line. A reaction may occur inside a two-shot or held master.

Dialogue, action, reaction, silence, and tail time must fit inside the declared duration. Provider timing is outside this contract.

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

The validator checks shape, IDs, duration, evidence references, source coverage, placeholders, authorization, and fallback presence. It cannot judge acting quality, whether reported reference shots are accurate, or whether the visual style is aesthetically successful.
