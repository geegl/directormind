#!/usr/bin/env python3
"""Upgrade Director IR v0.1 to v0.2 using explicit scene and shot overrides."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from route_director_rules import (
    INPUT_SCHEMA_PATH,
    RESULT_SCHEMA_PATH,
    route_scene,
    schema_issues,
)
from validate_director_grammar import (
    INDEX_PATH,
    MATRIX_PATH,
    SCHEMA_PATH as GRAMMAR_SCHEMA_PATH,
    read_json,
    validate_grammar,
)
from validate_director_ir import go01_triggered, go07_triggered, scene_routing_binding_issues


MIGRATION_MODES = {"LEGACY_COMPATIBLE", "GRAMMAR_V02_ROUTED"}
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def default_reference() -> dict[str, Any]:
    return {
        "required": False,
        "reference_type": "NONE",
        "reference_id": None,
        "status": "NOT_REQUIRED",
        "rights_status": "NOT_APPLICABLE",
        "scope": "",
        "inherit": [],
        "exclude": [],
    }


def default_execution(shot: dict[str, Any]) -> dict[str, Any]:
    fallback = shot.get("fallback")
    return {
        "base_generation": {
            "mode": "AI_VIDEO",
            "owns": ["approved character identity", "location geometry", "blocking", "performance", "camera framing"],
        },
        "composite_layers": [],
        "state_versions": [],
        "continuity_owners": {
            "identity": "BASE_GENERATION",
            "surface": "BASE_GENERATION",
            "prop": "BASE_GENERATION",
            "environment": "BASE_GENERATION",
        },
        "fallback_route": {
            "decision": "SPLIT_GENERATION" if fallback else "NONE",
            "action": fallback or "",
        },
    }


def camera_contract(shot: dict[str, Any]) -> tuple[str, dict[str, str], str]:
    motion = shot.get("camera_motion", {})
    mode = str(motion.get("mode", "static"))
    reason = str(motion.get("reason", "source beat"))
    lowered = mode.lower()
    if any(word in lowered for word in ("push", "dolly", "track", "pan", "follow")):
        path = {
            "mode": mode,
            "direction": "toward or with the locked subject movement",
            "speed": "slow and constant",
            "distance": "one short framing step",
            "stability": "stabilized",
            "trigger": reason,
        }
    else:
        path = {
            "mode": mode,
            "direction": "none",
            "speed": "none",
            "distance": "none",
            "stability": "locked",
            "trigger": f"none; hold through {reason}",
        }
    start = f"Start in {shot['shot_type']} at {shot['camera_angle']}; {shot['framing']}."
    end = f"End after {shot['blocking']}; preserve {shot['continuity_out']}."
    return start, path, end


def legacy_review_required_result(scene_id: str) -> dict[str, Any]:
    """Represent an honest migration pause without inventing a v0.2 routing decision."""
    return {
        "schema_version": "director-routing-result/0.1",
        "case_id": scene_id,
        "status": "HUMAN_REVIEW_REQUIRED",
        "scene_problem": "LEGACY_SCENE_PROBLEM",
        "applied_constraint_ids": [],
        "eligible_rule_ids": [],
        "selected_rules": [],
        "rejected_rules": [],
        "conflict_trace": [],
        "selection_count": 0,
        "ir_handoff": "PAUSE_FOR_HUMAN",
        "human_review_status": "HUMAN_REVIEW_PENDING",
        "rights_boundary": {
            "surface_copy_allowed": False,
            "subject_matter_used_for_selection": False,
        },
    }


def _validated_routing_result(value: Any, scene_id: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"scene {scene_id} requires a complete routing result object")
    issues = schema_issues(value, RESULT_SCHEMA_PATH)
    if issues:
        details = "; ".join(f"{item['path']} {item['code']}" for item in issues)
        raise ValueError(f"scene {scene_id} routing result is invalid: {details}")
    return copy.deepcopy(value)


def _validated_routing_input(value: Any, scene_id: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"scene {scene_id} requires a complete routing input object")
    issues = schema_issues(value, INPUT_SCHEMA_PATH)
    if issues:
        details = "; ".join(f"{item['path']} {item['code']}" for item in issues)
        raise ValueError(f"scene {scene_id} routing input is invalid: {details}")
    return copy.deepcopy(value)


def _selected_rule_ids(routing_result: dict[str, Any]) -> set[str]:
    return {
        item["rule_id"]
        for item in routing_result.get("selected_rules", [])
        if isinstance(item, dict) and isinstance(item.get("rule_id"), str)
    }


def upgrade_ir(
    source_ir: dict[str, Any],
    overrides: dict[str, Any],
    target_grammar: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Upgrade without mutating the source or inventing a Grammar v0.2 route."""
    if not isinstance(source_ir, dict) or not isinstance(overrides, dict):
        raise ValueError("source IR and overrides must both be objects")
    ir = copy.deepcopy(source_ir)
    source_version = ir.get("schema_version")
    if source_version not in {"director-ir/0.1", "director-ir/0.2"}:
        raise ValueError("unsupported source schema")
    mode = overrides.get("migration_mode", "LEGACY_COMPATIBLE")
    if mode not in MIGRATION_MODES:
        raise ValueError(f"unsupported migration_mode: {mode}")

    routing_inputs = overrides.get("scene_routing_inputs", {})
    routing_results = overrides.get("scene_routing_results", {})
    if not isinstance(routing_inputs, dict):
        raise ValueError("scene_routing_inputs must be an object keyed by scene_id")
    if not isinstance(routing_results, dict):
        raise ValueError("scene_routing_results must be an object keyed by scene_id")
    if mode == "GRAMMAR_V02_ROUTED":
        target_grammar_path = overrides.get("target_director_grammar_path")
        if not isinstance(target_grammar_path, str) or not target_grammar_path.strip():
            raise ValueError("GRAMMAR_V02_ROUTED requires target_director_grammar_path")
        if not isinstance(target_grammar, dict) or target_grammar.get("schema_version") != "director-grammar/0.2":
            raise ValueError("GRAMMAR_V02_ROUTED requires the target Grammar v0.2 object")
        grammar_report = validate_grammar(
            target_grammar,
            read_json(INDEX_PATH),
            read_json(MATRIX_PATH),
            read_json(GRAMMAR_SCHEMA_PATH),
        )
        if grammar_report["status"] != "PASS":
            codes = sorted({item["code"] for item in grammar_report["issues"]})
            raise ValueError(f"target Grammar v0.2 is invalid: {codes}")
        ir["director_grammar_path"] = target_grammar_path
    elif routing_inputs or routing_results:
        raise ValueError("scene_routing_inputs and scene_routing_results require GRAMMAR_V02_ROUTED mode")

    ir["schema_version"] = "director-ir/0.2"
    ir["execution_medium"] = "AI_PHOTOREAL_HUMAN"
    facts = ir.setdefault("source_facts", {})
    if not isinstance(facts, dict) or not isinstance(overrides.get("source_facts", {}), dict):
        raise ValueError("source_facts and its override must be objects")
    facts["source_unit_count"] = len(ir.get("source_coverage", []))
    facts.setdefault("cross_episode_state_in", [])
    facts.setdefault("cross_episode_state_out", [])
    ir["source_facts"] = merge(facts, overrides.get("source_facts", {}))
    scene_overrides = overrides.get("scene_defaults", {})
    shot_overrides = overrides.get("shot_overrides", {})
    if not isinstance(scene_overrides, dict) or not isinstance(shot_overrides, dict):
        raise ValueError("scene_defaults and shot_overrides must be objects")
    seen_shots: set[str] = set()
    active_states: dict[str, dict[str, Any]] = {}

    for scene in ir["scenes"]:
        scene_id = scene["scene_id"]
        scene_default = scene_overrides.get(scene_id, {})
        if not isinstance(scene_default, dict):
            raise ValueError(f"scene default must be an object: {scene_id}")
        if mode == "GRAMMAR_V02_ROUTED":
            supplied_input = routing_inputs.get(scene_id)
            supplied_result = routing_results.get(scene_id)
            if source_version == "director-ir/0.2":
                if supplied_input is None:
                    supplied_input = scene.get("routing_input")
                if supplied_result is None:
                    supplied_result = scene.get("routing_result")
            scene["routing_input"] = _validated_routing_input(
                supplied_input, scene_id
            )
            scene["routing_result"] = _validated_routing_result(
                supplied_result, scene_id
            )
            expected_result = route_scene(scene["routing_input"], target_grammar or {})
            if scene["routing_result"] != expected_result:
                raise ValueError(
                    f"scene {scene_id} routing result is not bound to the target Grammar or its routing input"
                )
        else:
            current = scene.get("routing_result")
            current_input = scene.get("routing_input")
            if (
                source_version == "director-ir/0.2"
                and isinstance(current, dict)
                and not schema_issues(current, RESULT_SCHEMA_PATH)
                and isinstance(current_input, dict)
                and not schema_issues(current_input, INPUT_SCHEMA_PATH)
            ):
                scene["routing_input"] = copy.deepcopy(current_input)
                scene["routing_result"] = _validated_routing_result(current, scene_id)
            else:
                scene["routing_input"] = None
                scene["routing_result"] = legacy_review_required_result(scene_id)
        for shot in scene["shots"]:
            shot_id = shot["shot_id"]
            seen_shots.add(shot_id)
            existing_execution = shot.get("execution_plan", {}) if isinstance(shot.get("execution_plan"), dict) else {}
            existing_reference = shot.get("reference_plan", {}) if isinstance(shot.get("reference_plan"), dict) else {}
            shot["execution_plan"] = merge(default_execution(shot), existing_execution)
            shot["execution_plan"] = merge(shot["execution_plan"], scene_default.get("execution_plan", {}))
            shot["reference_plan"] = merge(default_reference(), existing_reference)
            shot["reference_plan"] = merge(shot["reference_plan"], scene_default.get("reference_plan", {}))
            explicit = shot_overrides.get(shot_id, {})
            if not isinstance(explicit, dict):
                raise ValueError(f"shot override must be an object: {shot_id}")
            if mode == "GRAMMAR_V02_ROUTED" and source_version == "director-ir/0.1" and "evidence_rule_ids" not in explicit:
                raise ValueError(f"GRAMMAR_V02_ROUTED requires explicit evidence_rule_ids for legacy shot {shot_id}")
            if "evidence_rule_ids" in explicit:
                replacement_ids = explicit["evidence_rule_ids"]
                if not isinstance(replacement_ids, list) or any(not isinstance(item, str) or not item for item in replacement_ids):
                    raise ValueError(f"shot {shot_id} evidence_rule_ids must be a list of non-empty strings")
                shot["evidence_rule_ids"] = copy.deepcopy(replacement_ids)
            removed_rule_values = explicit.get("remove_evidence_rule_ids", [])
            if not isinstance(removed_rule_values, list) or any(not isinstance(item, str) or not item for item in removed_rule_values):
                raise ValueError(f"shot {shot_id} remove_evidence_rule_ids must be a list of non-empty strings")
            removed_rules = set(removed_rule_values)
            if removed_rules:
                shot["evidence_rule_ids"] = [rule for rule in shot["evidence_rule_ids"] if rule not in removed_rules]
            if "execution_plan" in explicit:
                if not isinstance(explicit["execution_plan"], dict):
                    raise ValueError(f"shot {shot_id} execution_plan override must be an object")
                shot["execution_plan"] = merge(shot["execution_plan"], explicit["execution_plan"])
            if "reference_plan" in explicit:
                if not isinstance(explicit["reference_plan"], dict):
                    raise ValueError(f"shot {shot_id} reference_plan override must be an object")
                shot["reference_plan"] = merge(shot["reference_plan"], explicit["reference_plan"])

            explicit_states = shot["execution_plan"]["state_versions"]
            for state in explicit_states:
                if state.get("carry_forward"):
                    active_states[state["subject"]] = copy.deepcopy(state)
            explicit_subjects = {state["subject"] for state in explicit_states}
            carried = [copy.deepcopy(state) for subject, state in active_states.items() if subject not in explicit_subjects]
            shot["execution_plan"]["state_versions"] = explicit_states + carried
            for state in shot["execution_plan"]["state_versions"]:
                if state.get("owner") == "COMPOSITE" and "wardrobe" in state.get("subject", "").lower():
                    shot["execution_plan"]["continuity_owners"]["surface"] = "COMPOSITE"

            if shot.get("visible_text") and not any(
                layer.get("type") == "TEXT" for layer in shot["execution_plan"]["composite_layers"]
            ):
                shot["execution_plan"]["composite_layers"].append({
                    "layer_id": f"CMP-{shot_id}-TEXT",
                    "type": "TEXT",
                    "description": "Render only the locked visible text as a controlled post layer.",
                    "trigger": "After the base frame and prop surface are approved.",
                    "continuity_key": f"TEXT-{ir['episode_id']}",
                })
                shot["execution_plan"]["continuity_owners"]["prop"] = "SHARED"

            default_start, default_path, default_end = camera_contract(shot)
            if not shot.get("camera_start"):
                shot["camera_start"] = default_start
            existing_path = shot.get("camera_path") if isinstance(shot.get("camera_path"), dict) else {}
            shot["camera_path"] = merge(default_path, existing_path)
            if not shot.get("camera_end"):
                shot["camera_end"] = default_end
            if source_version == "director-ir/0.1" and isinstance(shot.get("audio"), dict) and shot["audio"]:
                shot["audio"] = {"legacy_unmapped": copy.deepcopy(shot["audio"])}
            if mode == "LEGACY_COMPATIBLE":
                if "GO-01" in shot["evidence_rule_ids"] and not go01_triggered(shot):
                    shot["evidence_rule_ids"].remove("GO-01")
                if "GO-07" in shot["evidence_rule_ids"] and not go07_triggered(shot):
                    shot["evidence_rule_ids"].remove("GO-07")
            elif any(rule_id.startswith("GO-") for rule_id in shot["evidence_rule_ids"]):
                raise ValueError(f"Grammar v0.2 migration cannot carry legacy seed rules in shot {shot_id}")

        if mode == "GRAMMAR_V02_ROUTED":
            routing_result = scene["routing_result"]
            selected_ids = _selected_rule_ids(routing_result)
            shot_ids = {
                rule_id
                for shot in scene["shots"]
                for rule_id in shot.get("evidence_rule_ids", [])
            }
            if routing_result["selection_count"] != len(selected_ids):
                raise ValueError(f"scene {scene_id} routing selection_count is inconsistent")
            if routing_result["status"] == "SELECTED" and (not selected_ids or shot_ids != selected_ids):
                raise ValueError(f"scene {scene_id} selected routing rules do not match shot evidence_rule_ids")
            if routing_result["status"] != "SELECTED" and (selected_ids or shot_ids):
                raise ValueError(f"scene {scene_id} non-selected routing result requires empty shot evidence_rule_ids")
            semantic_issues = scene_routing_binding_issues(scene, target_grammar or {}, f"scene {scene_id}")
            semantic_errors = [item for item in semantic_issues if item["level"] == "error"]
            if semantic_errors:
                details = "; ".join(f"{item['code']} {item['message']}" for item in semantic_errors)
                raise ValueError(f"scene {scene_id} routing result is not bound to the target Grammar: {details}")
    extra = sorted(set(shot_overrides) - seen_shots)
    if extra:
        raise ValueError(f"override contains unknown shots: {extra}")
    extra_scenes = sorted(set(routing_results) - {scene["scene_id"] for scene in ir["scenes"]})
    if extra_scenes:
        raise ValueError(f"routing results contain unknown scenes: {extra_scenes}")
    extra_input_scenes = sorted(set(routing_inputs) - {scene["scene_id"] for scene in ir["scenes"]})
    if extra_input_scenes:
        raise ValueError(f"routing inputs contain unknown scenes: {extra_input_scenes}")
    if mode == "GRAMMAR_V02_ROUTED":
        scene_ids = {scene["scene_id"] for scene in ir["scenes"]}
        missing_result_scenes = sorted(scene_ids - set(routing_results))
        missing_input_scenes = sorted(scene_ids - set(routing_inputs))
        if source_version == "director-ir/0.1" and missing_result_scenes:
            raise ValueError(f"routing results missing scenes: {missing_result_scenes}")
        if source_version == "director-ir/0.1" and missing_input_scenes:
            raise ValueError(f"routing inputs missing scenes: {missing_input_scenes}")
    extra_scene_defaults = sorted(set(scene_overrides) - {scene["scene_id"] for scene in ir["scenes"]})
    if extra_scene_defaults:
        raise ValueError(f"scene defaults contain unknown scenes: {extra_scene_defaults}")

    return ir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ir", type=Path, required=True)
    parser.add_argument("--overrides", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_ir = json.loads(args.ir.read_text(encoding="utf-8"))
    overrides = json.loads(args.overrides.read_text(encoding="utf-8"))
    protected_inputs = {args.ir.resolve(), args.overrides.resolve()}
    target_grammar = None
    if isinstance(overrides, dict) and overrides.get("migration_mode") == "GRAMMAR_V02_ROUTED":
        target_path_value = overrides.get("target_director_grammar_path")
        if not isinstance(target_path_value, str) or not target_path_value.strip():
            raise SystemExit("GRAMMAR_V02_ROUTED requires target_director_grammar_path")
        target_path = Path(target_path_value)
        if not target_path.is_absolute():
            target_path = REPOSITORY_ROOT / target_path
        if not target_path.is_file():
            raise SystemExit(f"target Grammar not found: {target_path_value}")
        protected_inputs.add(target_path.resolve())
        target_grammar = json.loads(target_path.read_text(encoding="utf-8"))
    if args.output.resolve() in protected_inputs:
        raise SystemExit("output must not overwrite any input file")
    if args.output.exists():
        raise SystemExit("output already exists; refusing to overwrite it")
    try:
        ir = upgrade_ir(source_ir, overrides, target_grammar)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(ir, ensure_ascii=False, indent=2) + "\n")
    except FileExistsError as exc:
        raise SystemExit("output already exists; refusing to overwrite it") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
