#!/usr/bin/env python3
"""Build deterministic, rights-safe DirectorMind forward-test packages."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
FORWARD_ROOT = REPOSITORY_ROOT / "examples" / "forward-tests"
GRAMMAR_PATH = REPOSITORY_ROOT / "research" / "grammar" / "director_grammar_v0.2.json"
PROMOTION_REVIEW_PATH = REPOSITORY_ROOT / "research" / "grammar" / "runtime_integration.review.json"

sys.path.insert(0, str(SCRIPT_DIR))
from render_director_ir import render_coverage, render_shot_script  # noqa: E402
from route_director_rules import route_scene  # noqa: E402
from validate_director_ir import validate as validate_ir  # noqa: E402
from validate_director_grammar import read_json  # noqa: E402


CASES: list[dict[str, Any]] = [
    {
        "case_id": "ORIGINAL-POWER-DIALOGUE",
        "title": "The Allocation Marker",
        "scene_problem": "DIALOGUE_POWER_TRANSFER",
        "coverage_tags": ["TWO_PARTY_POWER_TRANSFER"],
        "characters": ["COORDINATOR_A", "COORDINATOR_B"],
        "location": "community workshop planning room",
        "facts": [
            ("FACT-01", "decision_authority", "Only the coordinator holding the blue marker may close the allocation decision."),
            ("FACT-02", "verified_tally", "The written tally gives Coordinator B the deciding vote."),
            ("FACT-03", "authority_shift", "Coordinator A places the blue marker beside Coordinator B after the tally is checked."),
        ],
        "beats": [
            "Both coordinators verify the same three-line tally from opposite sides of a plain table.",
            "Coordinator A stops objecting and moves the blue marker across the center line.",
            "Coordinator B covers the final allocation box while Coordinator A waits without speaking.",
        ],
        "dialogue_by_shot": {
            1: [{"speaker": "COORDINATOR A", "text": "The tally is confirmed.", "verbatim": True}],
            2: [{"speaker": "COORDINATOR B", "text": "I will close the allocation.", "verbatim": True}],
        },
        "dramatic": {
            "goal": "make a verified transfer of decision authority readable",
            "objectives": ["close one allocation decision"],
            "obstacle": "the prior decision owner must accept the tally",
            "stakes": "the workshop cannot assign its next shift",
            "tactic_change": "verbal resistance becomes formal handoff",
            "subtext": "control changes only after both people acknowledge the same count",
        },
        "signals": ["authority_shift", "verified_tally"],
        "subject_tags": ["workshop_planning"],
    },
    {
        "case_id": "ORIGINAL-RELATIONSHIP-FRACTURE",
        "title": "The Removed Name Card",
        "scene_problem": "RELATIONSHIP_FRACTURE",
        "coverage_tags": [],
        "characters": ["PARTNER_A", "PARTNER_B"],
        "location": "model-making room",
        "facts": [
            ("FACT-01", "counterpart_relation", "Partner A leaves a blank name card at the shared model as an invitation to continue."),
            ("FACT-02", "repair_declined", "Partner B returns the blank card without adding a name."),
            ("FACT-03", "spatial_change", "Partner B removes their tools and exits while Partner A remains at the model."),
        ],
        "beats": [
            "Partner A aligns the blank card with the two occupied work positions.",
            "Partner B slides the untouched card back across the work surface.",
            "Partner B takes one tool case and leaves; Partner A does not follow.",
        ],
        "dramatic": {
            "goal": "show a final attempt at repair fail",
            "objectives": ["restore the shared working agreement"],
            "obstacle": "one partner will not renew the agreement",
            "stakes": "the joint project will end",
            "tactic_change": "invitation becomes departure",
            "subtext": "returning the untouched card is the answer",
        },
        "signals": ["material_spatial_change", "counterpart_relation_context_locked"],
        "subject_tags": ["partnership"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "BLOCKING", "EDIT"],
    },
    {
        "case_id": "ORIGINAL-PUBLIC-REVEAL",
        "title": "The Open Shift Board",
        "scene_problem": "PUBLIC_REVELATION",
        "coverage_tags": ["MULTI_PARTICIPANT_PUBLIC_REVELATION"],
        "characters": ["DISPATCHER", "VOLUNTEER_1", "VOLUNTEER_2", "VOLUNTEER_3"],
        "location": "neighborhood dispatch room",
        "facts": [
            ("FACT-01", "private_result", "The dispatcher has verified that seven night shifts remain uncovered."),
            ("FACT-02", "audience_information_change", "The dispatcher turns the board so all three volunteers can read the seven open rows together."),
            ("FACT-03", "group_response", "Each volunteer removes one availability token after seeing the same board."),
        ],
        "beats": [
            "The dispatcher finishes checking the back of a freestanding shift board while the volunteers wait.",
            "The board rotates toward the group and exposes seven unfilled rows at once.",
            "The volunteers read the same rows, then remove their tokens in a visible sequence.",
        ],
        "dramatic": {
            "goal": "make one verified result become public to a group",
            "objectives": ["secure coverage for the remaining shifts"],
            "obstacle": "the disclosed shortage changes willingness to help",
            "stakes": "the overnight service may remain uncovered",
            "tactic_change": "private assurance becomes public proof",
            "subtext": "the group response begins only after shared receipt of the result",
        },
        "signals": ["audience_information_change", "group_response"],
        "subject_tags": ["volunteer_dispatch"],
    },
    {
        "case_id": "ORIGINAL-PROCEDURE",
        "title": "The Third Irrigation Check",
        "scene_problem": "PROCEDURAL_COMPETENCE",
        "secondary": ["PROCEDURAL_COLLAPSE"],
        "coverage_tags": ["PROCEDURE_SUCCESS_AND_FAILURE"],
        "characters": ["GARDEN_OPERATOR", "CHECKER"],
        "location": "rooftop garden service bay",
        "facts": [
            ("FACT-01", "ordered_steps", "The operator must verify valve, pressure, then flow in that order."),
            ("FACT-02", "procedure_failure", "The first flow reading cannot be confirmed and the handoff stops."),
            ("FACT-03", "procedure_recovery", "A project-original spare gauge produces a stable reading and the checker signs the handoff."),
        ],
        "beats": [
            "The operator points to the valve mark, then the pressure mark, preserving the approved order.",
            "The flow needle oscillates; both people stop before signing and mark the reading invalid.",
            "The operator fits the approved spare gauge, obtains a stable flow mark, and the checker signs.",
        ],
        "dramatic": {
            "goal": "show a procedure fail honestly and then recover through the approved fallback",
            "objectives": ["complete the irrigation handoff"],
            "obstacle": "the final reading is unreliable",
            "stakes": "the garden cannot be left on automatic control",
            "tactic_change": "routine verification becomes fallback verification",
            "subtext": "competence is shown by stopping at uncertainty",
        },
        "signals": ["ordered_steps", "procedure_failure", "procedure_recovery"],
        "subject_tags": ["maintenance"],
    },
    {
        "case_id": "ORIGINAL-ACTION-CAUSALITY",
        "title": "The Rolling Equipment Rack",
        "scene_problem": "ACTION_CAUSALITY",
        "coverage_tags": ["ONE_TO_MANY_ACTION"],
        "characters": ["FLOOR_LEAD", "CREW_1", "CREW_2", "CREW_3"],
        "location": "empty rehearsal hall",
        "facts": [
            ("FACT-01", "cause_effect_chain", "A loose wheel stop lets an unpowered equipment rack begin rolling."),
            ("FACT-02", "one_to_many_response", "The floor lead signals three crew members to clear three marked lanes."),
            ("FACT-03", "safe_resolution", "The floor lead pushes a floor chock into the rack path after all three lanes are clear."),
        ],
        "beats": [
            "The loose stop tips away and the unpowered rack begins moving across the empty hall.",
            "The floor lead points once; three crew members move into separate marked safe zones.",
            "After all three zones are visibly occupied, the floor lead places the chock and the rack stops.",
        ],
        "dramatic": {
            "goal": "preserve one visible cause and the distinct responses of a group",
            "objectives": ["clear the rack path", "stop the rack safely"],
            "obstacle": "the rack is already moving",
            "stakes": "the marked route must be cleared before intervention",
            "tactic_change": "warning becomes coordinated clearance and then restraint",
            "subtext": "the lead acts only after every response is visible",
        },
        "signals": ["visible_action_source", "target_state_change", "result_readable"],
        "subject_tags": ["safe_physical_action"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "REACTION", "PACING", "EDIT"],
        "affected_shot_index": 2,
        "selected_shot_overrides": {
            "duration_seconds": 8,
            "shot_type": "project-original result-and-response hold",
            "framing": "shared frame holding the stopped result before the response allocation",
            "blocking": "Keep the stopped rack and cleared lanes visible before assigning the final response beat.",
            "edit_in": "enter on the locked target-state change",
            "edit_out": "cut only after the stopped result is readable",
        },
    },
    {
        "case_id": "ORIGINAL-PROXIMITY-TENSION",
        "title": "Across the Unlit Model",
        "scene_problem": "ROMANTIC_PROXIMITY",
        "coverage_tags": ["NON_CONTACT_RELATION_TENSION"],
        "characters": ["DESIGNER_A", "DESIGNER_B"],
        "location": "quiet prototype studio",
        "facts": [
            (
                "FACT-01",
                "relationship_context",
                "The two designers are former romantic partners, and their agreed no-contact distance during the joint model review is a relationship-relevant story fact.",
            ),
            ("FACT-02", "distance_change", "They approach opposite sides of the model table and stop within arm's reach."),
            ("FACT-03", "relation_endpoint", "The table remains between them and neither person touches the other."),
            (
                "FACT-04",
                "time_structure",
                "The approach and stop occur in one continuous present-time interval without ellipsis.",
            ),
        ],
        "beats": [
            "Designer A switches off the room lights, leaving only the model base illuminated.",
            "Designer B approaches the opposite side; both stop with the model centered between them.",
            "They reach toward different controls at the same moment, pause without contact, then continue the review.",
            "The review continues after the stop without a time jump.",
        ],
        "dramatic": {
            "goal": "make mutual awareness legible through distance without physical contact",
            "objectives": ["complete the joint model review"],
            "obstacle": "both people avoid acknowledging the changed relationship",
            "stakes": "the review requires continued cooperation",
            "tactic_change": "parallel work becomes a shared pause",
            "subtext": "the maintained gap carries the tension",
        },
        "signals": ["relation_distance_change", "time_structure_locked", "shared_endpoint_required"],
        "subject_tags": ["relationship_tension"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "BLOCKING", "PACING", "EDIT"],
    },
    {
        "case_id": "ORIGINAL-SOUND-SUSPENSE",
        "title": "The Archive Vent Timer",
        "scene_problem": "SOUND_LED_CAUSALITY",
        "coverage_tags": ["SOUND_DRIVEN_SUSPENSE"],
        "characters": ["ARCHIVE_CARETAKER"],
        "location": "sealed document storage room",
        "facts": [
            ("FACT-01", "audible_information", "A project-original timer emits two verified pulses before its source is visible."),
            ("FACT-02", "source_search", "The caretaker follows the repeated pulse toward a closed wall panel."),
            ("FACT-03", "source_confirmation", "Opening the panel reveals the timer beside a normal ventilation-cycle indicator."),
        ],
        "beats": [
            "Two identical timer pulses are heard while the caretaker remains still and the wall panel stays closed.",
            "A third pulse leads the caretaker to the panel; the source remains outside the visible area.",
            "The caretaker opens the panel and the timer flashes beside the normal ventilation indicator.",
        ],
        "audio_by_shot": {
            0: {
                "status": "PROJECT_ORIGINAL_LOCKED",
                "instruction": "Play exactly two equal project-original timer pulses before the wall panel is visible.",
                "source_refs": ["locked-script.md#FACT-01"],
            },
            1: {
                "status": "PROJECT_ORIGINAL_LOCKED",
                "instruction": "Play one matching project-original pulse while the timer source remains outside the visible area.",
                "source_refs": ["locked-script.md#FACT-02"],
            },
            2: {
                "status": "PROJECT_ORIGINAL_LOCKED",
                "instruction": "End the final matching pulse as the timer and normal ventilation indicator become visible together.",
                "source_refs": ["locked-script.md#FACT-03"],
            },
        },
        "dramatic": {
            "goal": "separate receipt of a verified sound cue from later source confirmation",
            "objectives": ["locate and identify the pulse"],
            "obstacle": "the source begins outside the visible area",
            "stakes": "the caretaker must decide whether the archive needs intervention",
            "tactic_change": "listening becomes a directed search",
            "subtext": "uncertainty ends only when the ordinary source is visible",
        },
        "signals": ["audible_information", "source_confirmation"],
        "subject_tags": ["offscreen_information"],
    },
    {
        "case_id": "ORIGINAL-PERFORMANCE-OWNER-HOLD",
        "title": "The Missing Safety Entry",
        "scene_problem": "INTERROGATION",
        "coverage_tags": [],
        "characters": ["REVIEWER", "TECHNICIAN"],
        "location": "plain equipment review room",
        "facts": [
            ("FACT-01", "relation_state", "The reviewer and technician are established on opposite sides of a plain table."),
            ("FACT-02", "performance_progression", "The technician checks three blank log rows, stops at the missing entry, and places both hands flat before answering."),
            ("FACT-03", "owner_endpoint", "The reviewer remains outside the critical frame until the technician finishes the visible sequence."),
        ],
        "beats": [
            "A neutral shared frame establishes both participants and the plain log sheet.",
            "One clean technician single holds the complete check-stop-hands-flat progression without a reaction cut.",
            "Only after the hands settle does a short reviewer single confirm receipt.",
        ],
        "dramatic": {
            "goal": "make one uninterrupted visible answer progression readable",
            "objectives": ["identify the missing safety entry"],
            "obstacle": "the technician must complete the visible review before the receiver responds",
            "stakes": "the equipment cannot be released until the entry is resolved",
            "tactic_change": "document checking becomes a direct answer",
            "subtext": "none asserted",
        },
        "signals": ["single_performance_progression"],
        "subject_tags": ["equipment_review"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "PACING", "EDIT"],
    },
    {
        "case_id": "ORIGINAL-PERFORMANCE-CONCURRENT-STATE",
        "title": "The Live Pressure Check",
        "scene_problem": "INTERROGATION",
        "coverage_tags": [],
        "characters": ["REVIEWER", "OPERATOR"],
        "location": "plain control bench",
        "facts": [
            ("FACT-01", "relation_state", "The reviewer and operator are established beside a project-original pressure indicator."),
            ("FACT-02", "performance_progression", "The operator gives a visible step-by-step account while checking the indicator."),
            ("FACT-03", "simultaneous_state", "The indicator and the reviewer's safety acknowledgment must remain visible throughout the account."),
        ],
        "beats": [
            "A shared frame establishes both participants and the project-original indicator.",
            "The operator continues the account while the indicator changes and the reviewer marks each safe reading.",
            "The shared work frame remains until the final mark is complete.",
        ],
        "dramatic": {
            "goal": "preserve an account together with a simultaneous safety state",
            "objectives": ["verify the pressure sequence"],
            "obstacle": "the account and indicator must be read together",
            "stakes": "the test cannot continue if a reading is missed",
            "tactic_change": "verbal account becomes synchronized checking",
            "subtext": "none asserted",
        },
        "signals": ["single_performance_progression", "simultaneous_required_action"],
        "subject_tags": ["equipment_review"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-SPATIAL-CHANGE-WITHOUT-COUNTERPART",
        "title": "The Empty Second Station",
        "scene_problem": "RELATIONSHIP_FRACTURE",
        "coverage_tags": [],
        "characters": ["MAKER_A", "MAKER_B"],
        "location": "plain assembly room",
        "facts": [
            ("FACT-01", "counterpart_relation", "Maker A leaves the room before Maker B moves from the shared bench."),
            ("FACT-02", "spatial_change", "After the exit, Maker B crosses alone to a second station visible against the same fixed wall grid."),
            ("FACT-03", "fixed_anchor", "The wall grid and empty shared bench make the solo destination unambiguous."),
        ],
        "beats": [
            "A shared view shows Maker A leave the established bench and clear the room.",
            "Maker B remains alone, then crosses to the second station against the fixed wall grid.",
            "A single frame holds the solo endpoint without adding another two-person reset.",
        ],
        "dramatic": {
            "goal": "show a solo occupancy change after the counterpart has left",
            "objectives": ["move to the second station"],
            "obstacle": "none beyond preserving the known room direction",
            "stakes": "the next task begins at the second station",
            "tactic_change": "shared occupancy becomes solo work",
            "subtext": "none asserted",
        },
        "signals": ["material_spatial_change", "counterpart_relation_context_locked", "counterpart_relation_not_required"],
        "subject_tags": ["partnership"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-PROXIMITY-ELLIPSIS",
        "title": "The Three Calendar Checks",
        "scene_problem": "ROMANTIC_PROXIMITY",
        "coverage_tags": [],
        "characters": ["PLANNER_A", "PLANNER_B"],
        "location": "plain planning room",
        "facts": [
            (
                "FACT-01",
                "relationship_context",
                "The planners are romantic partners, and their changing seating distance is a relationship-relevant story fact.",
            ),
            ("FACT-02", "distance_change", "Three dated checks show the planners at progressively different fixed seats."),
            (
                "FACT-03",
                "relation_endpoint",
                "Only the final wide must establish their relationship-relevant terminal distance across the table.",
            ),
            ("FACT-04", "time_structure", "No continuous move between the dated checks belongs to the story facts."),
        ],
        "beats": [
            "The romantic partners begin the first dated planning check at the same table.",
            "The first dated card precedes a shared near-seat planning view.",
            "A second dated card precedes isolated task views from different seats.",
            "The final dated card precedes one shared wide that proves the terminal distance.",
        ],
        "dramatic": {
            "goal": "show a changed relation endpoint across time without inventing a continuous approach",
            "objectives": ["compare three dated planning checks"],
            "obstacle": "the intermediate physical transitions are not story facts",
            "stakes": "only the terminal seating relation must be clear",
            "tactic_change": "repeated task views become a final shared endpoint",
            "subtext": "none asserted",
        },
        "signals": ["relation_distance_change", "time_structure_locked", "shared_endpoint_required", "elliptical_time_change"],
        "subject_tags": ["relationship_tension"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-ACTION-CONTINUOUS-CHAIN",
        "title": "The Continuous Cart Stop",
        "scene_problem": "ACTION_CAUSALITY",
        "coverage_tags": ["ONE_TO_MANY_ACTION"],
        "characters": ["FLOOR_LEAD", "CREW_1", "CREW_2"],
        "location": "empty project-original loading room",
        "facts": [
            ("FACT-01", "cause_effect_chain", "A loose wheel stop is visibly displaced beside a rolling cart."),
            ("FACT-02", "one_to_many_response", "The cart crosses one clear lane while both crew members remain visible."),
            ("FACT-03", "safe_resolution", "The lead places a chock and the cart stops inside the same continuous view."),
        ],
        "beats": [
            "One stable shared view establishes the stop, cart, lead, and two clear positions.",
            "The stop moves, the cart rolls, and both crew members clear the lane without leaving the frame.",
            "The lead places the chock and the stopped result remains readable in that same view.",
        ],
        "dramatic": {
            "goal": "preserve an already readable continuous action chain",
            "objectives": ["clear and stop the cart"],
            "obstacle": "the cart is already moving",
            "stakes": "the lane must be clear before the cart stops",
            "tactic_change": "clearance becomes restraint",
            "subtext": "none asserted",
        },
        "signals": ["visible_action_source", "target_state_change", "result_readable", "continuous_view_preserves_action_chain"],
        "subject_tags": ["safe_physical_action"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-REFERENT-COMPARISON",
        "title": "The Three Couplers",
        "scene_problem": "PROCEDURAL_COMPETENCE",
        "coverage_tags": ["PROCEDURE_SUCCESS_AND_FAILURE"],
        "characters": ["ASSEMBLER", "CHECKER"],
        "location": "plain project-original assembly bench",
        "facts": [
            ("FACT-01", "referent_set", "Three project-original couplers remain visible on the same marked grid."),
            ("FACT-02", "relation_constraint", "The openings must be read together against one fixed gauge before the next handling step."),
            ("FACT-03", "comparison_result", "The assembler moves to one handling relation only after the shared comparison is readable."),
        ],
        "beats": [
            "A locked field view establishes all three couplers beside one neutral gauge.",
            "The checker aligns the gauge across the three openings without removing any option.",
            "The assembler begins the next handling step only after the comparison relation is visible.",
        ],
        "dramatic": {
            "goal": "make a physical comparison explain the next handling relation",
            "objectives": ["establish the relevant coupler-to-gauge relation"],
            "obstacle": "the options are similar until compared against the gauge",
            "stakes": "the next assembly step requires the compatible part",
            "tactic_change": "field comparison becomes one readable handling relation",
            "subtext": "none asserted",
        },
        "signals": ["multiple_visible_referents", "comparative_relation_required"],
        "subject_tags": ["assembly"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "BLOCKING", "PACING", "EDIT"],
        "affected_shot_index": 1,
        "selected_shot_overrides": {
            "duration_seconds": 8,
            "shot_type": "project-original comparative field",
            "framing": "locked field containing every option and the common gauge",
            "blocking": "Keep all three couplers in place while the gauge relation is made readable.",
            "edit_in": "enter before comparison begins",
            "edit_out": "cut to the handling relation only after the shared comparison reads",
        },
    },
    {
        "case_id": "ORIGINAL-COMPARISON-NOT-REQUIRED",
        "title": "The Single Seal Check",
        "scene_problem": "PROCEDURAL_COMPETENCE",
        "coverage_tags": ["PROCEDURE_SUCCESS_AND_FAILURE"],
        "characters": ["INSPECTOR"],
        "location": "plain project-original inspection table",
        "facts": [
            ("FACT-01", "referent_set", "One sealed project-original container is the only item in the inspection area."),
            ("FACT-02", "relation_constraint", "The task is to read that container's existing seal state, not to compare multiple referents."),
            ("FACT-03", "single_item_state", "The inspector records the intact seal and leaves the container in place."),
        ],
        "beats": [
            "A neutral frame establishes one container and no alternatives.",
            "The inspector checks the existing seal in one readable detail.",
            "The same frame confirms the unchanged single-item state.",
        ],
        "dramatic": {
            "goal": "record one existing item state",
            "objectives": ["verify the seal"],
            "obstacle": "the small seal must remain readable",
            "stakes": "the record must match the visible item",
            "tactic_change": "overview becomes detail check",
            "subtext": "none asserted",
        },
        "signals": ["multiple_visible_referents", "comparative_relation_required", "comparative_field_not_required"],
        "subject_tags": ["inspection"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-THRESHOLD-STATE-CHANGE",
        "title": "The Clean-Zone Handoff",
        "scene_problem": "ACTION_CAUSALITY",
        "coverage_tags": ["ONE_TO_MANY_ACTION"],
        "characters": ["TECHNICIAN_A", "TECHNICIAN_B"],
        "location": "plain project-original clean-room threshold",
        "facts": [
            ("FACT-01", "threshold_state_change", "A sealed sample changes from corridor custody to clean-zone custody at the marked threshold."),
            ("FACT-02", "route_endpoint", "Technician B must stop with the sealed sample at the inner verification mark."),
            ("FACT-03", "after_state", "The inner indicator and Technician B's hold make the new custody and next vector visible."),
        ],
        "beats": [
            "A shared frame establishes corridor custody, the marked threshold, and the inner verification mark.",
            "The sealed sample crosses once between the two project-original technicians.",
            "The inner indicator changes and Technician B stops at the verification mark.",
        ],
        "dramatic": {
            "goal": "show a state-changing threshold handoff",
            "objectives": ["transfer the sealed sample into the clean zone"],
            "obstacle": "the handoff and landing mark must remain visible",
            "stakes": "the next test cannot begin without confirmed clean-zone custody",
            "tactic_change": "approach becomes verified transfer",
            "subtext": "none asserted",
        },
        "signals": ["threshold_changes_locked_state", "before_after_route_required"],
        "subject_tags": ["safe_handoff"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "BLOCKING", "PACING", "EDIT"],
        "affected_shot_index": 1,
        "selected_shot_overrides": {
            "duration_seconds": 9,
            "shot_type": "project-original threshold state checkpoint",
            "framing": "shared frame containing before-state, threshold, and landing mark",
            "blocking": "Keep both custody states, one crossing direction, and the inner landing mark readable.",
            "edit_in": "enter before the handoff begins",
            "edit_out": "cut after the new custody state and next vector read",
        },
    },
    {
        "case_id": "ORIGINAL-THRESHOLD-UNCHANGED",
        "title": "The Ordinary Room Entry",
        "scene_problem": "ACTION_CAUSALITY",
        "coverage_tags": ["ONE_TO_MANY_ACTION"],
        "characters": ["COURIER", "CLERK"],
        "location": "plain project-original receiving room",
        "facts": [
            ("FACT-01", "threshold_state_change", "The courier keeps the same sealed box and access state before and after an ordinary doorway."),
            ("FACT-02", "route_endpoint", "The occupied receiving desk is the only required destination fact."),
            ("FACT-03", "unchanged_state", "No custody, safety, readiness, or permission state changes at the doorway."),
        ],
        "beats": [
            "An exterior approach ends at the ordinary doorway.",
            "A cut moves directly to the courier already facing the occupied receiving desk.",
            "The unchanged sealed box remains visible at the destination.",
        ],
        "dramatic": {
            "goal": "arrive at a known destination without over-covering an ordinary entry",
            "objectives": ["reach the receiving desk"],
            "obstacle": "none at the doorway",
            "stakes": "the delivery beat begins inside",
            "tactic_change": "approach becomes arrival",
            "subtext": "none asserted",
        },
        "signals": ["threshold_changes_locked_state", "before_after_route_required", "threshold_state_unchanged"],
        "subject_tags": ["delivery"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-OBJECT-CUSTODY-CHECKPOINTS",
        "title": "The Calibrated Sensor Handoff",
        "scene_problem": "PROCEDURAL_COMPETENCE",
        "coverage_tags": ["PROCEDURE_SUCCESS_AND_FAILURE"],
        "characters": ["TECHNICIAN_A", "TECHNICIAN_B"],
        "location": "plain project-original calibration room",
        "facts": [
            ("FACT-01", "object_identity", "One project-original blue sensor is the only calibrated unit in the room."),
            ("FACT-02", "object_state_change", "Technician A transfers the calibrated sensor across a marked handoff line to Technician B."),
            ("FACT-03", "dependent_next_action", "Technician B may place the sensor in the test cradle only after the new custody state is visible."),
        ],
        "beats": [
            "A shared view plants the blue sensor with Technician A beside the marked handoff line.",
            "The transfer remains visible until Technician B has the sensor alone on the receiving side.",
            "Technician B places that same sensor in the test cradle after the custody checkpoint reads.",
        ],
        "dramatic": {
            "goal": "make one required object handoff govern the next procedure",
            "objectives": ["transfer and install the calibrated sensor"],
            "obstacle": "the next step cannot begin before custody is confirmed",
            "stakes": "the calibration record would be invalid if the wrong unit enters the cradle",
            "tactic_change": "possession becomes verified installation",
            "subtext": "none asserted",
        },
        "signals": ["portable_object_state_change", "next_action_depends_on_object_state"],
        "subject_tags": ["safe_handoff"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "BLOCKING", "EDIT"],
        "affected_shot_index": 1,
        "selected_shot_overrides": {
            "duration_seconds": 8,
            "shot_type": "project-original custody checkpoint",
            "framing": "shared handoff field containing both handlers, the object, and the marked line",
            "blocking": "Keep the sensor and both hands readable until Technician B owns the receiving side.",
            "edit_in": "enter before the transfer begins",
            "edit_out": "cut only after the new holder and state read",
        },
    },
    {
        "case_id": "ORIGINAL-OBJECT-SECONDARY-HANDLING",
        "title": "The Unchanged Pencil",
        "scene_problem": "PROCEDURAL_COMPETENCE",
        "coverage_tags": ["PROCEDURE_SUCCESS_AND_FAILURE"],
        "characters": ["TECHNICIAN_A"],
        "location": "plain project-original calibration desk",
        "facts": [
            ("FACT-01", "object_identity", "A pencil remains with Technician A throughout the written check."),
            ("FACT-02", "object_state_change", "The pencil moves between two boxes but never changes owner, function, or required state."),
            ("FACT-03", "dependent_next_action", "The next action depends only on the written reading, not on pencil custody."),
        ],
        "beats": [
            "Technician A writes two readings in one stable desk view.",
            "The pencil shifts between boxes as ordinary hand business.",
            "The unchanged pencil remains inside the person view while the completed reading becomes primary.",
        ],
        "dramatic": {
            "goal": "complete one written calibration check without over-covering secondary hand business",
            "objectives": ["record the reading"],
            "obstacle": "the written value must remain readable",
            "stakes": "the record must match the instrument",
            "tactic_change": "measurement becomes notation",
            "subtext": "none asserted",
        },
        "signals": ["portable_object_state_change", "next_action_depends_on_object_state", "object_state_not_required"],
        "subject_tags": ["inspection"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-MULTI-ZONE-WAYPOINT-ROUTE",
        "title": "The Three-Zone Filter Route",
        "scene_problem": "SUSPENSE_INFORMATION_ASYMMETRY",
        "coverage_tags": [],
        "characters": ["COURIER", "RECEIVER"],
        "location": "project-original service corridor, stair landing, and filter room",
        "facts": [
            ("FACT-01", "route_continuity", "The courier's trip from service corridor through stair landing to filter room occurs in continuous present time."),
            ("FACT-02", "zone_waypoints", "A blue door and a yellow stair rail are the two project-original waypoints that keep the three zones distinct."),
            ("FACT-03", "destination_vector", "The filter-room hatch is the required destination vector because the receiver waits beyond it."),
        ],
        "beats": [
            "A route view establishes the courier, blue door, and direction toward the stair landing.",
            "The courier crosses the yellow rail landing and the next hatch remains visibly ahead.",
            "The hatch opens into the filter room and the receiver occupies the terminal zone.",
        ],
        "dramatic": {
            "goal": "keep a three-zone delivery route readable",
            "objectives": ["reach the waiting receiver"],
            "obstacle": "each threshold hides the next room until crossed",
            "stakes": "the handoff cannot happen in the wrong service zone",
            "tactic_change": "route following becomes terminal handoff",
            "subtext": "none asserted",
        },
        "signals": ["continuous_multi_zone_route", "waypoint_orientation_required"],
        "subject_tags": ["safe_handoff"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "BLOCKING", "EDIT"],
        "affected_shot_index": 1,
        "selected_shot_overrides": {
            "duration_seconds": 8,
            "shot_type": "project-original waypoint route unit",
            "framing": "route frame containing the current landmark and next exit vector",
            "blocking": "Cross each threshold on one locked direction and expose the next waypoint before tightening.",
            "edit_in": "enter before the landing threshold",
            "edit_out": "cut after the next hatch vector reads",
        },
    },
    {
        "case_id": "ORIGINAL-SINGLE-THRESHOLD-APPROACH",
        "title": "The One-Door Delivery",
        "scene_problem": "SUSPENSE_INFORMATION_ASYMMETRY",
        "coverage_tags": [],
        "characters": ["COURIER", "RECEIVER"],
        "location": "plain project-original receiving room",
        "facts": [
            ("FACT-01", "route_continuity", "The courier approaches one ordinary doorway from a known corridor."),
            ("FACT-02", "zone_waypoints", "No intermediate waypoint or second route zone belongs to the story."),
            ("FACT-03", "destination_vector", "The visible receiving desk is the only destination."),
        ],
        "beats": [
            "One corridor view contains the courier, doorway, and visible desk beyond it.",
            "The courier crosses the single doorway without a route change.",
            "The receiver accepts the delivery at the already visible desk.",
        ],
        "dramatic": {
            "goal": "complete one short known approach",
            "objectives": ["reach the receiving desk"],
            "obstacle": "none at the doorway",
            "stakes": "the next beat begins at the desk",
            "tactic_change": "approach becomes arrival",
            "subtext": "none asserted",
        },
        "signals": ["continuous_multi_zone_route", "waypoint_orientation_required", "route_not_continuous_multi_zone"],
        "subject_tags": ["delivery"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-MOBILE-ATTENTION-HANDOFF",
        "title": "The Community Kitchen Relay",
        "scene_problem": "PROCEDURAL_COLLAPSE",
        "coverage_tags": [],
        "characters": ["COOK", "RUNNER", "CHECKER"],
        "location": "project-original community kitchen",
        "facts": [
            ("FACT-01", "current_attention_state", "The cook must finish sealing one tray before attention leaves the prep table."),
            ("FACT-02", "next_attention_owner", "The runner becomes visible at the service opening before carrying the sealed tray onward."),
            ("FACT-03", "connected_geography", "The prep table, service opening, and checker station share one continuous readable route."),
        ],
        "beats": [
            "A mobile field holds the cook until the tray seal is visibly complete.",
            "The runner enters at the service opening and the camera hands attention across the same connected route.",
            "The runner reaches the checker while the prior prep zone remains spatially attributable.",
        ],
        "dramatic": {
            "goal": "carry one changing priority through connected work zones",
            "objectives": ["seal, carry, and check the tray"],
            "obstacle": "attention cannot abandon a state before it becomes readable",
            "stakes": "the handoff sequence would become ambiguous",
            "tactic_change": "preparation becomes delivery and verification",
            "subtext": "none asserted",
        },
        "signals": ["connected_zone_attention_handoff", "next_attention_owner_visible"],
        "subject_tags": ["community_kitchen"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "BLOCKING", "PACING", "EDIT"],
        "affected_shot_index": 1,
        "selected_shot_overrides": {
            "duration_seconds": 9,
            "shot_type": "project-original mobile attention handoff",
            "framing": "mobile field linking current and next attention owners",
            "blocking": "Reveal the runner and path before leaving the completed tray state.",
            "edit_in": "continue from the current owner state",
            "edit_out": "cut only when the checker state is readable",
        },
    },
    {
        "case_id": "ORIGINAL-MOBILE-DETAIL-REQUIRED",
        "title": "The Tiny Seal Code",
        "scene_problem": "PROCEDURAL_COLLAPSE",
        "coverage_tags": [],
        "characters": ["COOK", "CHECKER"],
        "location": "plain project-original community kitchen",
        "facts": [
            ("FACT-01", "current_attention_state", "The cook presents one sealed tray at the checker station."),
            ("FACT-02", "next_attention_owner", "The checker must read a tiny three-character seal code before accepting it."),
            ("FACT-03", "connected_geography", "Both people remain at one station, but the code is unreadable in the mobile field."),
        ],
        "beats": [
            "A shared view establishes the tray and both participants at the checker station.",
            "The mobile field cannot resolve the tiny required code.",
            "A fixed project-original detail shows the code before the checker accepts the tray.",
        ],
        "dramatic": {
            "goal": "verify one small required state",
            "objectives": ["read and accept the seal code"],
            "obstacle": "the code is too small for the moving field",
            "stakes": "an unread code prevents acceptance",
            "tactic_change": "shared inspection becomes required detail",
            "subtext": "none asserted",
        },
        "signals": ["connected_zone_attention_handoff", "next_attention_owner_visible", "required_detail_not_mobile_readable"],
        "subject_tags": ["inspection"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-INITIAL-GEOMETRY-BEFORE-PROXIMITY",
        "title": "Across the Archive Table",
        "scene_problem": "ROMANTIC_PROXIMITY",
        "coverage_tags": ["NON_CONTACT_RELATION_TENSION"],
        "characters": ["ARCHIVIST_A", "ARCHIVIST_B"],
        "location": "project-original archive workroom",
        "facts": [
            ("FACT-01", "relation_start_zones", "The archivists begin on opposite room sides with a long table between them."),
            ("FACT-02", "distance_change", "Archivist B crosses the open floor and stops at the opposite end of the table."),
            ("FACT-03", "path_anchor", "The doorway, table, and open crossing path must remain readable before the stop."),
            ("FACT-04", "relationship_context", "The archivists' established personal bond makes the voluntary distance change the scene's primary relation event."),
        ],
        "beats": [
            "A room view establishes both start zones, the doorway, and the full table.",
            "The crossing path remains visible as Archivist B approaches the opposite end.",
            "Only after the distance changes does tighter shared coverage become available.",
            "The closer working distance now carries the established personal relation without copying a reference surface.",
        ],
        "dramatic": {
            "goal": "make one non-contact distance change spatially legible",
            "objectives": ["continue the archive review at the shared table"],
            "obstacle": "the room distance changes before the work can resume",
            "stakes": "the changed relation would read as a teleport without the path",
            "tactic_change": "separated work becomes close shared review",
            "subtext": "none asserted",
        },
        "signals": ["distance_change_requires_initial_geometry", "relation_path_must_read"],
        "subject_tags": ["relationship_tension"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "BLOCKING", "EDIT"],
        "affected_shot_index": 0,
        "selected_shot_overrides": {
            "duration_seconds": 8,
            "shot_type": "project-original initial relation geometry",
            "framing": "room relation frame containing both start zones and the required path",
            "blocking": "Keep the doorway, both participants, table, and open path readable before tightening.",
            "edit_in": "enter before the distance change",
            "edit_out": "cut after start zones and path are registered",
        },
    },
    {
        "case_id": "ORIGINAL-GEOMETRY-ALREADY-REGISTERED",
        "title": "The Second Archive Pass",
        "scene_problem": "ROMANTIC_PROXIMITY",
        "coverage_tags": ["NON_CONTACT_RELATION_TENSION"],
        "characters": ["ARCHIVIST_A", "ARCHIVIST_B"],
        "location": "project-original archive workroom",
        "facts": [
            ("FACT-01", "relation_start_zones", "The same uninterrupted interval has already established both archivists and the full table."),
            ("FACT-02", "distance_change", "Archivist B shifts one position along the already visible table edge."),
            ("FACT-03", "path_anchor", "The existing table and doorway anchors remain unchanged and readable."),
            ("FACT-04", "relationship_context", "The archivists' established personal bond remains the reason the small distance change matters."),
        ],
        "beats": [
            "The established shared field already contains both sides and the table path.",
            "Archivist B makes one short move along that known path.",
            "The scene uses the existing anchor instead of repeating an initial room setup.",
            "The relationship beat continues inside the already registered project-original geometry.",
        ],
        "dramatic": {
            "goal": "continue a relation change inside already known geometry",
            "objectives": ["resume the archive review"],
            "obstacle": "the distance changes slightly",
            "stakes": "the existing axis must remain stable",
            "tactic_change": "shared review shifts position",
            "subtext": "none asserted",
        },
        "signals": ["distance_change_requires_initial_geometry", "relation_path_must_read", "relation_geometry_already_registered"],
        "subject_tags": ["relationship_tension"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-STABLE-AXIS-STATE-HOLDS",
        "title": "The Two Permit Marks",
        "scene_problem": "DIALOGUE_POWER_TRANSFER",
        "coverage_tags": ["TWO_PARTY_POWER_TRANSFER"],
        "characters": ["REVIEWER_A", "REVIEWER_B"],
        "location": "plain project-original permit desk",
        "facts": [
            ("FACT-01", "stable_axis", "The seated reviewers remain on opposite sides of one marked desk axis."),
            ("FACT-02", "visible_state_progression", "Reviewer A uncovers one permit mark; Reviewer B checks it, pauses, and adds a second mark."),
            ("FACT-03", "decision_authority", "The second visible mark transfers authority to close the permit review."),
        ],
        "beats": [
            "A neutral relation view establishes the fixed desk axis and both side anchors.",
            "Opposing project-original singles hold through each visible mark-and-check progression rather than every line.",
            "A short relation reset confirms the second mark and transferred authority.",
        ],
        "dramatic": {
            "goal": "make a two-step visible authority transfer readable",
            "objectives": ["close the permit review"],
            "obstacle": "both visible checks must occur before closure",
            "stakes": "the permit cannot close after only one mark",
            "tactic_change": "inspection becomes authorization",
            "subtext": "none asserted",
        },
        "signals": ["stationary_pair_state_progression", "stable_two_side_axis"],
        "subject_tags": ["permit_review"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "PACING", "EDIT"],
        "affected_shot_index": 1,
        "selected_shot_overrides": {
            "duration_seconds": 9,
            "shot_type": "project-original stable-axis state hold",
            "framing": "opposing fixed-side single holding the complete visible check",
            "blocking": "Keep each reviewer on the locked desk side and hold through the visible state endpoint.",
            "edit_in": "enter when the next visible state owner begins",
            "edit_out": "cut at the completed mark or check, not at line count",
        },
    },
    {
        "case_id": "ORIGINAL-SINGLE-OWNER-NO-ALTERNATION",
        "title": "The Silent Permit Recount",
        "scene_problem": "DIALOGUE_POWER_TRANSFER",
        "coverage_tags": ["TWO_PARTY_POWER_TRANSFER"],
        "characters": ["REVIEWER_A", "REVIEWER_B"],
        "location": "plain project-original permit desk",
        "facts": [
            ("FACT-01", "stable_axis", "Both reviewers remain on their established desk sides."),
            ("FACT-02", "visible_state_progression", "Reviewer A alone recounts three marks and reaches the locked decision endpoint."),
            ("FACT-03", "performance_progression", "Reviewer A alone owns the uninterrupted visible recount; Reviewer B has no simultaneous required action before it ends."),
        ],
        "beats": [
            "A shared view recalls the stable desk relation.",
            "One owner-dominant tight view holds Reviewer A through the full three-mark recount.",
            "Reviewer B receives the result only after the locked endpoint.",
        ],
        "dramatic": {
            "goal": "preserve one uninterrupted visible recount",
            "objectives": ["reach the verified decision endpoint"],
            "obstacle": "the recount must remain continuously readable",
            "stakes": "an early cut could hide a missed mark",
            "tactic_change": "shared review becomes one-owner verification",
            "subtext": "none asserted",
        },
        "signals": ["stationary_pair_state_progression", "stable_two_side_axis", "single_performance_progression"],
        "subject_tags": ["permit_review"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-AFTERMATH-BY-NEXT-ACTION",
        "title": "After the Water Test",
        "scene_problem": "PUBLIC_REVELATION",
        "coverage_tags": ["MULTI_PARTICIPANT_PUBLIC_REVELATION"],
        "characters": ["OPERATOR", "CHECKER_A", "CHECKER_B"],
        "location": "project-original community pump room",
        "facts": [
            ("FACT-01", "visible_result", "A clear project-original test vessel reaches the marked safe level in view of all three participants."),
            ("FACT-02", "next_action_states", "Checker A records the level, Checker B closes the inlet, and the operator remains with the stable vessel."),
            ("FACT-03", "terminal_environment_state", "The final frame must show the stable vessel and closed inlet before the room is released."),
        ],
        "beats": [
            "One result view makes the safe level visible to the assembled group.",
            "Coverage follows only the recording and inlet-closing actions that govern the next state.",
            "The sequence ends on the stable vessel, closed inlet, and remaining operator.",
        ],
        "dramatic": {
            "goal": "allocate a verified result tail by the next required actions",
            "objectives": ["record, close, and release the pump room"],
            "obstacle": "three possible reactions do not have equal operational value",
            "stakes": "the room cannot release before the final safe state",
            "tactic_change": "shared result becomes ordered closure",
            "subtext": "none asserted",
        },
        "signals": ["consequential_result_with_multiple_next_states", "next_action_prioritization_required"],
        "subject_tags": ["pump_test"],
        "test_mode": "POSITIVE",
        "changed_director_dimensions": ["COVERAGE", "REACTION", "PACING", "EDIT"],
        "affected_shot_index": 1,
        "selected_shot_overrides": {
            "duration_seconds": 8,
            "shot_type": "project-original next-action aftermath allocation",
            "framing": "result-linked sequence of the two required next-action owners",
            "blocking": "Move from the recorded level to the inlet close, then retain the stable terminal state.",
            "edit_in": "enter after the shared result reads",
            "edit_out": "cut only after the next required action completes",
        },
    },
    {
        "case_id": "ORIGINAL-AFTERMATH-NEXT-ACTION-IMMEDIATE",
        "title": "The Live Pump Correction",
        "scene_problem": "PUBLIC_REVELATION",
        "coverage_tags": ["MULTI_PARTICIPANT_PUBLIC_REVELATION"],
        "characters": ["OPERATOR", "CHECKER_A", "CHECKER_B"],
        "location": "plain project-original community pump room",
        "facts": [
            ("FACT-01", "visible_result", "The visible level reaches a warning mark but the pump continues running."),
            ("FACT-02", "next_action_states", "All three participants must keep the live gauge, valve, and shutdown sequence visible together."),
            ("FACT-03", "terminal_environment_state", "No separate terminal aftermath exists until the immediate correction is complete."),
        ],
        "beats": [
            "A shared field shows the warning mark, running pump, and all three active positions.",
            "The operator and checkers complete the immediate shutdown without isolated reaction coverage.",
            "Only after shutdown could a later aftermath interval begin.",
        ],
        "dramatic": {
            "goal": "preserve an immediate live correction instead of treating it as aftermath",
            "objectives": ["complete the shutdown"],
            "obstacle": "all simultaneous safety states must remain visible",
            "stakes": "the correction fails if one state is hidden",
            "tactic_change": "warning becomes coordinated shutdown",
            "subtext": "none asserted",
        },
        "signals": ["consequential_result_with_multiple_next_states", "next_action_prioritization_required", "immediate_next_action_supersedes_aftermath"],
        "subject_tags": ["pump_test"],
        "test_mode": "BOUNDARY_OR_NON_APPLICABLE",
        "changed_director_dimensions": [],
    },
    {
        "case_id": "ORIGINAL-NO-APPLICABLE-RULE",
        "title": "The Empty Delivery Mark",
        "scene_problem": "NO_SPECIALIZED_PROBLEM",
        "coverage_tags": [],
        "characters": ["COURIER"],
        "location": "plain indoor receiving area",
        "facts": [
            ("FACT-01", "simple_arrival", "The courier reaches an empty floor mark."),
            ("FACT-02", "simple_stop", "The courier stops and waits without a conflict or information change."),
        ],
        "beats": [
            "The courier walks into the empty receiving area and reaches the floor mark.",
            "The courier stops, sets down a plain sealed box, and waits.",
        ],
        "dramatic": {
            "goal": "record a simple arrival",
            "objectives": ["reach the marked position"],
            "obstacle": "none asserted",
            "stakes": "the next beat waits",
            "tactic_change": "movement ends",
            "subtext": "none asserted",
        },
        "signals": ["simple_arrival", "simple_stop"],
        "subject_tags": [],
    },
]


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def package_relative(case_id: str, name: str) -> str:
    return f"examples/forward-tests/{case_id}/{name}"


def build_locked_script(spec: dict[str, Any]) -> str:
    lines = [
        f"# {spec['title']}",
        "",
        "RIGHTS_STATUS: PROJECT_ORIGINAL_SYNTHETIC",
        "PRIVATE_SOURCE_USED: false",
        f"TEST_CASE_ID: {spec['case_id']}",
        "HUMAN_REVIEW_STATUS: HUMAN_REVIEW_PENDING",
        "",
        f"Location: {spec['location']}",
        f"Participants: {', '.join(spec['characters'])}",
        "",
        "## Locked facts",
        "",
    ]
    for fact_id, _, value in spec["facts"]:
        lines.extend([f'<a id="{fact_id}"></a>', f"- {fact_id}: {value}"])
    lines.extend(["", "## Locked beats", ""])
    for index, beat in enumerate(spec["beats"], 1):
        lines.append(f"{index}. {beat}")
    dialogue_by_shot = spec.get("dialogue_by_shot", {})
    if dialogue_by_shot:
        lines.extend(["", "## Locked dialogue", ""])
        for shot_index in sorted(dialogue_by_shot):
            for line in dialogue_by_shot[shot_index]:
                lines.append(f"{line['speaker']}: {line['text']}")
    lines.extend([
        "",
        "## Boundary",
        "",
        "This compact scene exists only as a public, project-original structural test. It does not authorize generation or publication.",
        "",
    ])
    return "\n".join(lines)


def build_routing_input(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "director-routing-input/0.1",
        "case_id": spec["case_id"],
        "rights_boundary": {
            "project_original": True,
            "contains_private_script": False,
            "contains_reference_surface": False,
        },
        "locked_facts": [
            {
                "fact_id": fact_id,
                "fact_type": fact_type,
                "value": value,
                "status": "LOCKED",
                "source_ref": f"locked-script.md#{fact_id}",
            }
            for fact_id, fact_type, value in spec["facts"]
        ],
        "unknown_fact_types": [],
        "dramatic_structure": spec["dramatic"],
        "scene_problem": {
            "primary": spec["scene_problem"],
            "secondary": spec.get("secondary", []),
            "status": "LOCKED",
        },
        "routing_signals": spec["signals"],
        "priority_constraints": [],
        "subject_matter_tags": spec["subject_tags"],
    }


def shot_for(spec: dict[str, Any], index: int) -> dict[str, Any]:
    fact_id, _, fact_value = spec["facts"][index]
    shot_id = f"EP01-SC01-SH{index + 1:02d}"
    case_token = spec["case_id"].replace("ORIGINAL-", "")
    reference_required = index == 0
    return {
        "shot_id": shot_id,
        "order": index + 1,
        "duration_seconds": 5,
        "narrative_goal": fact_value,
        "source_refs": [f"locked-script.md#{fact_id}"],
        "allowed_characters": spec["characters"],
        "shot_type": "project-original coverage",
        "framing": "readable neutral frame",
        "camera_angle": "eye level",
        "camera_motion": {"mode": "LOCKED", "reason": "Preserve the locked state change without adding style claims."},
        "camera_start": "stable view before the listed beat",
        "camera_path": {
            "mode": "LOCKED",
            "direction": "NONE",
            "speed": "NONE",
            "distance": "NONE",
            "stability": "LOCKED",
            "trigger": fact_id,
        },
        "camera_end": "stable view after the listed beat",
        "focus_strategy": "keep the locked action readable",
        "blocking": spec["beats"][index],
        "performance_beats": [spec["beats"][index]],
        "dialogue": spec.get("dialogue_by_shot", {}).get(index, []),
        "visible_text": [],
        "audio": spec.get("audio_by_shot", {}).get(
            index,
            {"status": "PROJECT_ORIGINAL_ONLY", "instruction": None, "source_refs": []},
        ),
        "edit_in": "cut on the prior locked state",
        "edit_out": "cut after the new locked state is readable",
        "continuity_in": f"state before {fact_id}",
        "continuity_out": f"state after {fact_id}",
        "constraints": {
            "must_hold": [fact_value],
            "changes_here": [fact_id],
            "must_not_appear": ["research-work surface elements"],
        },
        "ai_complexity": {
            "camera": "LOW",
            "performance": "LOW",
            "continuity": "MEDIUM",
            "reasons": ["The test uses one readable state change per shot."],
        },
        "fallback": None,
        "execution_plan": {
            "base_generation": {"mode": "AI_VIDEO", "owns": ["project-original participants", "project-original location"]},
            "composite_layers": [],
            "state_versions": [],
            "continuity_owners": {
                "identity": "BASE_GENERATION",
                "surface": "BASE_GENERATION",
                "prop": "BASE_GENERATION",
                "environment": "BASE_GENERATION",
            },
            "fallback_route": {"decision": "NONE", "action": ""},
        },
        "reference_plan": {
            "required": reference_required,
            "reference_type": "SHOT_GOLDEN" if reference_required else "NONE",
            "reference_id": f"REF-{case_token}-SH01" if reference_required else None,
            "status": "PLANNED" if reference_required else "NOT_REQUIRED",
            "rights_status": "PROJECT_ORIGINAL" if reference_required else "NOT_APPLICABLE",
            "scope": "project-original identity and geometry only" if reference_required else "",
            "inherit": ["identity", "geometry"] if reference_required else [],
            "exclude": ["research stills", "source-work surfaces"] if reference_required else [],
        },
        "visual_style_module": "UNRESOLVED",
        "evidence_rule_ids": [],
        "evidence_status": "HYPOTHESIS",
        "confidence": "UNKNOWN",
    }


def build_ir(
    spec: dict[str, Any],
    routing_input: dict[str, Any],
    routing_result: dict[str, Any],
) -> dict[str, Any]:
    shots = [shot_for(spec, index) for index in range(len(spec["facts"]))]
    selected_ids = [item["rule_id"] for item in routing_result["selected_rules"]]
    if selected_ids:
        default_affected_index = {
            "ORIGINAL-PERFORMANCE-OWNER-HOLD": 1,
            "ORIGINAL-RELATIONSHIP-FRACTURE": 2,
            "ORIGINAL-PROXIMITY-TENSION": 1,
        }
        affected_index = spec.get("affected_shot_index", default_affected_index.get(spec["case_id"], 0))
        affected = shots[affected_index]
        affected["evidence_rule_ids"] = selected_ids
        affected["confidence"] = "MEDIUM"
        affected.update(spec.get("selected_shot_overrides", {}))
        if spec["case_id"] == "ORIGINAL-PERFORMANCE-OWNER-HOLD":
            affected["duration_seconds"] = 12
            affected["shot_type"] = "sustained project-original performance-owner single"
            affected["framing"] = "owner-dominant tight view holding the complete visible progression"
            affected["blocking"] = "Hold the technician alone through the check-stop-hands-flat progression; do not add a receiver cut before the hands settle."
            affected["edit_in"] = "cut from the established two-person relation into the owner single"
            affected["edit_out"] = "cut only after both hands reach the locked endpoint"
        elif spec["case_id"] == "ORIGINAL-RELATIONSHIP-FRACTURE":
            affected["duration_seconds"] = 8
            affected["shot_type"] = "project-original shared relation reset"
            affected["framing"] = "shared frame containing the mover, relation anchor, route, and exit endpoint"
            affected["blocking"] = "Keep Partner A at the model while Partner B crosses from the shared position to the exit within the same readable relation frame."
            affected["edit_in"] = "enter before the zone crossing begins"
            affected["edit_out"] = "cut after the new two-person distance and exit endpoint read"
        elif spec["case_id"] == "ORIGINAL-PROXIMITY-TENSION":
            affected["duration_seconds"] = 8
            affected["shot_type"] = "project-original continuous shared relation frame"
            affected["framing"] = "shared frame containing both start zones, the approach path, and the no-contact endpoint"
            affected["blocking"] = "Designer B approaches the fixed opposite side while Designer A remains the relation anchor; stop with the model between them and no contact."
            affected["edit_in"] = "enter before the continuous distance change begins"
            affected["edit_out"] = "hold until the shared no-contact endpoint is readable"
    duration = sum(shot["duration_seconds"] for shot in shots)
    return {
        "schema_version": "director-ir/0.2",
        "execution_medium": "AI_PHOTOREAL_HUMAN",
        "project_id": f"FORWARD-TEST-{spec['case_id']}",
        "episode_id": "EP01",
        "source_script": package_relative(spec["case_id"], "locked-script.md"),
        "target_duration_seconds": duration,
        "duration_tolerance_seconds": 0,
        "aspect_ratio": "16:9",
        "status": "HUMAN_REVIEW_PENDING",
        "dialogue_must_be_verbatim": True,
        "generation_authorized": False,
        "publication_authorized": False,
        "director_grammar_path": "research/grammar/director_grammar_v0.2.json",
        "visual_style_pack_path": None,
        "source_facts": {
            "source_unit_count": len(spec["facts"]),
            "continuity_output": ["Keep every project-original participant, prop and position consistent across this test scene."],
            "cross_episode_state_in": [],
            "cross_episode_state_out": [],
        },
        "scenes": [{
            "scene_id": "EP01-SC01",
            "source_scene": "locked-script.md",
            "title": spec["title"],
            "duration_seconds": duration,
            "location": spec["location"],
            "time_of_day": "UNSPECIFIED_AND_NOT_REQUIRED",
            "allowed_characters": spec["characters"],
            "narrative_goal": spec["dramatic"]["goal"],
            "dramatic_engine": spec["dramatic"],
            "pov": {"character": "ENSEMBLE_NEUTRAL", "identification_level": "STRUCTURAL_TEST_ONLY"},
            "audience_information": {"locked_fact_ids": [fact[0] for fact in spec["facts"]]},
            "spatial_plan": {
                "geometry": "simple project-original working area",
                "primary_axis": "one stable readable axis",
                "close_positions": "the final locked beat positions",
            },
            "routing_input": routing_input,
            "routing_result": routing_result,
            "shots": shots,
        }],
        "source_coverage": [
            {
                "source_ref": f"locked-script.md#{fact_id}",
                "description": value,
                "status": "covered",
                "covered_by": [f"EP01-SC01-SH{index + 1:02d}"],
                "notes": "Structural coverage only; human creative review remains pending.",
            }
            for index, (fact_id, _, value) in enumerate(spec["facts"])
        ],
        "unresolved": ["Human creative review has not been performed."],
    }


def case_validation(spec: dict[str, Any], routing_result: dict[str, Any], ir_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "forward-test-validation/0.1",
        "test_case_id": spec["case_id"],
        "structural_status": "PASS" if ir_report["status"] == "PASS" else "FAIL",
        "test_mode": spec.get("test_mode", "NO_MATCH_PROBE"),
        "positive_selection_claimed": spec.get("test_mode") == "POSITIVE",
        "routing_status": routing_result["status"],
        "routing_error_count": 0,
        "ir_status": ir_report["status"],
        "ir_error_count": ir_report["errors"],
        "ir_warning_count": ir_report["warnings"],
        "selection_count": routing_result["selection_count"],
        "human_review_status": "HUMAN_REVIEW_PENDING",
        "generation_authorized": False,
        "publication_authorized": False,
        "issues": ir_report["issues"],
    }


def human_review_text(spec: dict[str, Any]) -> str:
    return "\n".join([
        f"# Human review — {spec['case_id']}",
        "",
        "STATUS: HUMAN_REVIEW_PENDING",
        "DIRECTOR_APPROVAL: NOT_REVIEWED",
        "GENERATION_AUTHORIZED: false",
        "PUBLICATION_AUTHORIZED: false",
        "",
        "The automated result proves only package structure, route reproduction, source coverage, and authorization gates.",
        "A human director has not approved creative quality, execution quality, or audience effect.",
        "",
    ])


def expected_files() -> dict[Path, str]:
    grammar = read_json(GRAMMAR_PATH)
    promotion_review = read_json(PROMOTION_REVIEW_PATH)
    promotions = promotion_review["runtime_rule_specs"]
    positive_promotions = {
        item["positive_forward_test_id"]: item for item in promotions
    }
    boundary_promotions = {
        item["boundary_forward_test_id"]: item for item in promotions
    }
    outputs: dict[Path, str] = {}
    index_cases: list[dict[str, Any]] = []
    for spec in CASES:
        spec = copy.deepcopy(spec)
        case_id = spec["case_id"]
        promotion = positive_promotions.get(case_id) or boundary_promotions.get(case_id)
        test_mode = spec.get("test_mode", "NO_MATCH_PROBE")
        if promotion is None and test_mode in {"POSITIVE", "BOUNDARY_OR_NON_APPLICABLE"}:
            test_mode = "NO_MATCH_PROBE"
            spec["test_mode"] = test_mode
            spec["changed_director_dimensions"] = []
        rule_id = promotion["rule_id"] if promotion else None
        candidate_rule_id = promotion["candidate_rule_id"] if promotion else None
        family_id = promotion["family_id"] if promotion else None
        locked_script = build_locked_script(spec)
        routing_input = build_routing_input(spec)
        routing_result = route_scene(routing_input, grammar)
        selected_ids = [item["rule_id"] for item in routing_result["selected_rules"]]
        rejected_by_id = {
            item["rule_id"]: item
            for item in routing_result["rejected_rules"]
        }
        if test_mode == "POSITIVE" and selected_ids != [rule_id]:
            raise ValueError(f"positive case {case_id} did not select exactly {rule_id}: {selected_ids}")
        if test_mode == "BOUNDARY_OR_NON_APPLICABLE" and (
            routing_result["status"] != "NO_APPLICABLE_RULE"
            or "NOT_APPLICABLE_MATCH" not in rejected_by_id.get(rule_id, {}).get("rejection_reason_codes", [])
            or not set(promotion["routing"]["not_applicable_if_any"]).intersection(
                rejected_by_id.get(rule_id, {}).get("matched_not_applicable_signal_ids", [])
            )
        ):
            raise ValueError(f"boundary case {case_id} did not reject {rule_id} at its declared boundary")
        if test_mode == "BOUNDARY_OR_NON_APPLICABLE":
            counterfactual_input = copy.deepcopy(routing_input)
            blocked_signals = set(promotion["routing"]["not_applicable_if_any"])
            counterfactual_input["routing_signals"] = [
                signal
                for signal in counterfactual_input.get("routing_signals", [])
                if signal not in blocked_signals
            ]
            counterfactual = route_scene(counterfactual_input, grammar)
            if rule_id not in {
                item["rule_id"] for item in counterfactual.get("selected_rules", [])
            }:
                raise ValueError(
                    f"boundary case {case_id} has a redundant negative guard for {rule_id}"
                )
        if test_mode == "NO_MATCH_PROBE" and routing_result["status"] != "NO_APPLICABLE_RULE":
            raise ValueError(f"no-match case {case_id} unexpectedly selected a rule")
        ir = build_ir(spec, routing_input, routing_result)
        ir_report = validate_ir(ir, grammar, locked_script)
        manifest = {
            "schema_version": "forward-test-result/0.1",
            "test_case_id": case_id,
            "candidate_rule_id": candidate_rule_id,
            "canonical_rule_family": family_id,
            "rule_id": rule_id,
            "test_mode": test_mode,
            "status": "HUMAN_REVIEW_PENDING",
        }
        validation = case_validation(spec, routing_result, ir_report)
        package = FORWARD_ROOT / case_id
        outputs[package / "manifest.json"] = json_text(manifest)
        outputs[package / "locked-script.md"] = locked_script
        outputs[package / "routing-input.json"] = json_text(routing_input)
        outputs[package / "selected-rules.json"] = json_text(routing_result)
        outputs[package / "director-ir.json"] = json_text(ir)
        outputs[package / "shot-script.md"] = render_shot_script(ir)
        outputs[package / "source-coverage.md"] = render_coverage(ir)
        outputs[package / "validation.json"] = json_text(validation)
        outputs[package / "human-review.md"] = human_review_text(spec)
        index_cases.append({
            "test_case_id": case_id,
            "package_path": f"examples/forward-tests/{case_id}",
            "scene_problem": spec["scene_problem"],
            "coverage_tags": spec["coverage_tags"],
            "test_mode": test_mode,
            "positive_for_family_ids": [family_id] if test_mode == "POSITIVE" else [],
            "boundary_for_family_ids": [family_id] if test_mode == "BOUNDARY_OR_NON_APPLICABLE" else [],
            "positive_for_rule_ids": [rule_id] if test_mode == "POSITIVE" else [],
            "boundary_for_rule_ids": [rule_id] if test_mode == "BOUNDARY_OR_NON_APPLICABLE" else [],
            "expected_routing_status": routing_result["status"],
            "expected_selection_count": len(selected_ids),
            "expected_selected_rule_ids": selected_ids,
            "expected_rejected_rule_id": rule_id if test_mode == "BOUNDARY_OR_NON_APPLICABLE" else None,
            "expected_rejection_reason_codes": (
                ["NOT_APPLICABLE_MATCH"] if test_mode == "BOUNDARY_OR_NON_APPLICABLE" else []
            ),
            "changed_director_dimensions": spec.get("changed_director_dimensions", []),
            "human_review_status": "HUMAN_REVIEW_PENDING",
        })
    eligible_families = sorted({item["family_id"] for item in promotions})
    index = {
        "schema_version": "forward-test-index/0.1",
        "status": "RULE_COVERAGE_COMPLETE",
        "grammar_path": "research/grammar/director_grammar_v0.2.json",
        "candidate_index_path": "research/grammar/candidate_rule_index.json",
        "support_matrix_path": "research/grammar/cross_work_support_matrix.json",
        "promotion_ready_family_count": len(eligible_families),
        "promotion_ready_family_ids": eligible_families,
        "required_positive_boundary_pairs": len(promotions),
        "completed_positive_cases": len(promotions),
        "completed_boundary_cases": len(promotions),
        "missing_family_ids": [],
        "missing_rule_ids": [],
        "required_scene_problem_coverage": [
            "TWO_PARTY_POWER_TRANSFER",
            "MULTI_PARTICIPANT_PUBLIC_REVELATION",
            "PROCEDURE_SUCCESS_AND_FAILURE",
            "ONE_TO_MANY_ACTION",
            "NON_CONTACT_RELATION_TENSION",
            "SOUND_DRIVEN_SUSPENSE",
        ],
        "cases": index_cases,
    }
    outputs[FORWARD_ROOT / "index.json"] = json_text(index)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = expected_files()
    drift: list[str] = []
    for path, content in outputs.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                drift.append(path.relative_to(REPOSITORY_ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if drift:
        sys.stderr.write("forward-test drift:\n" + "\n".join(drift) + "\n")
        return 1
    print(f"{'checked' if args.check else 'wrote'} {len(CASES)} forward-test package(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
