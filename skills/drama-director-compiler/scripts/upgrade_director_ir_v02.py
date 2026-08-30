#!/usr/bin/env python3
"""Upgrade Director IR v0.1 to v0.2 using explicit scene and shot overrides."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from validate_director_ir import go01_triggered, go07_triggered


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
            "mode": "static",
            "direction": "none",
            "speed": "none",
            "distance": "none",
            "stability": "locked",
            "trigger": f"none; hold through {reason}",
        }
    start = f"Start in {shot['shot_type']} at {shot['camera_angle']}; {shot['framing']}."
    end = f"End after {shot['blocking']}; preserve {shot['continuity_out']}."
    return start, path, end


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ir", type=Path, required=True)
    parser.add_argument("--overrides", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    ir = json.loads(args.ir.read_text(encoding="utf-8"))
    overrides = json.loads(args.overrides.read_text(encoding="utf-8"))
    if ir.get("schema_version") not in {"director-ir/0.1", "director-ir/0.2"}:
        raise SystemExit("unsupported source schema")

    ir["schema_version"] = "director-ir/0.2"
    ir["execution_medium"] = "AI_PHOTOREAL_HUMAN"
    facts = ir.setdefault("source_facts", {})
    facts["source_unit_count"] = len(ir.get("source_coverage", []))
    facts["cross_episode_state_in"] = []
    facts["cross_episode_state_out"] = []
    ir["source_facts"] = merge(facts, overrides.get("source_facts", {}))
    scene_overrides = overrides.get("scene_defaults", {})
    shot_overrides = overrides.get("shot_overrides", {})
    seen_shots: set[str] = set()
    active_states: dict[str, dict[str, Any]] = {}

    for scene in ir["scenes"]:
        scene_id = scene["scene_id"]
        scene_default = scene_overrides.get(scene_id, {})
        for shot in scene["shots"]:
            shot_id = shot["shot_id"]
            seen_shots.add(shot_id)
            shot["execution_plan"] = merge(default_execution(shot), scene_default.get("execution_plan", {}))
            shot["reference_plan"] = merge(default_reference(), scene_default.get("reference_plan", {}))
            explicit = shot_overrides.get(shot_id, {})
            removed_rules = set(explicit.get("remove_evidence_rule_ids", []))
            if removed_rules:
                shot["evidence_rule_ids"] = [rule for rule in shot["evidence_rule_ids"] if rule not in removed_rules]
            if "execution_plan" in explicit:
                shot["execution_plan"] = merge(shot["execution_plan"], explicit["execution_plan"])
            if "reference_plan" in explicit:
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

            shot["camera_start"], shot["camera_path"], shot["camera_end"] = camera_contract(shot)
            if "GO-01" in shot["evidence_rule_ids"] and not go01_triggered(shot):
                shot["evidence_rule_ids"].remove("GO-01")
            if "GO-07" in shot["evidence_rule_ids"] and not go07_triggered(shot):
                shot["evidence_rule_ids"].remove("GO-07")

    extra = sorted(set(shot_overrides) - seen_shots)
    if extra:
        raise SystemExit(f"override contains unknown shots: {extra}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ir, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
