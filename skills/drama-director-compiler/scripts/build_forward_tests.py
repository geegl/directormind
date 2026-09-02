#!/usr/bin/env python3
"""Build deterministic, rights-safe DirectorMind forward-test packages."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
FORWARD_ROOT = REPOSITORY_ROOT / "examples" / "forward-tests"
GRAMMAR_PATH = REPOSITORY_ROOT / "research" / "grammar" / "director_grammar_v0.2.json"

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
            ("FACT-01", "repair_offer", "Partner A leaves a blank name card at the shared model as an invitation to continue."),
            ("FACT-02", "repair_declined", "Partner B returns the blank card without adding a name."),
            ("FACT-03", "departure", "Partner B removes their tools and exits while Partner A remains at the model."),
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
        "signals": ["repair_declined", "departure"],
        "subject_tags": ["partnership"],
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
        "signals": ["cause_effect_chain", "one_to_many_response"],
        "subject_tags": ["safe_physical_action"],
    },
    {
        "case_id": "ORIGINAL-PROXIMITY-TENSION",
        "title": "Across the Unlit Model",
        "scene_problem": "ROMANTIC_PROXIMITY",
        "coverage_tags": ["NON_CONTACT_RELATION_TENSION"],
        "characters": ["DESIGNER_A", "DESIGNER_B"],
        "location": "quiet prototype studio",
        "facts": [
            ("FACT-01", "shared_object", "Both designers need the same unlit model to complete a joint review."),
            ("FACT-02", "distance_change", "They approach opposite sides of the model table and stop within arm's reach."),
            ("FACT-03", "no_contact_boundary", "The table remains between them and neither person touches the other."),
        ],
        "beats": [
            "Designer A switches off the room lights, leaving only the model base illuminated.",
            "Designer B approaches the opposite side; both stop with the model centered between them.",
            "They reach toward different controls at the same moment, pause without contact, then continue the review.",
        ],
        "dramatic": {
            "goal": "make mutual awareness legible through distance without physical contact",
            "objectives": ["complete the joint model review"],
            "obstacle": "both people avoid acknowledging the changed relationship",
            "stakes": "the review requires continued cooperation",
            "tactic_change": "parallel work becomes a shared pause",
            "subtext": "the maintained gap carries the tension",
        },
        "signals": ["distance_change", "no_contact_boundary"],
        "subject_tags": ["relationship_tension"],
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
        "test_mode": "ZERO_ELIGIBLE_PROBE",
        "positive_selection_claimed": False,
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
    outputs: dict[Path, str] = {}
    index_cases: list[dict[str, Any]] = []
    for spec in CASES:
        case_id = spec["case_id"]
        locked_script = build_locked_script(spec)
        routing_input = build_routing_input(spec)
        routing_result = route_scene(routing_input, grammar)
        ir = build_ir(spec, routing_input, routing_result)
        ir_report = validate_ir(ir, grammar, locked_script)
        manifest = {
            "schema_version": "forward-test-result/0.1",
            "test_case_id": case_id,
            "candidate_rule_id": None,
            "canonical_rule_family": None,
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
            "test_mode": "ZERO_ELIGIBLE_PROBE",
            "positive_for_family_ids": [],
            "boundary_for_family_ids": [],
            "expected_routing_status": "NO_APPLICABLE_RULE",
            "expected_selection_count": 0,
            "human_review_status": "HUMAN_REVIEW_PENDING",
        })
    index = {
        "schema_version": "forward-test-index/0.1",
        "status": "NO_ELIGIBLE_FAMILIES",
        "grammar_path": "research/grammar/director_grammar_v0.2.json",
        "candidate_index_path": "research/grammar/candidate_rule_index.json",
        "support_matrix_path": "research/grammar/cross_work_support_matrix.json",
        "promotion_ready_family_count": 0,
        "promotion_ready_family_ids": [],
        "required_positive_boundary_pairs": 0,
        "completed_positive_cases": 0,
        "completed_boundary_cases": 0,
        "missing_family_ids": [],
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
