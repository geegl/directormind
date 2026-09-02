#!/usr/bin/env python3
"""Validate the deterministic parts of Drama Director IR v0.2."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
IR_SCHEMA_PATH = SKILL_ROOT / "references" / "director-ir.schema.json"
ROUTING_RESULT_SCHEMA_PATH = SKILL_ROOT / "references" / "director-routing-result.schema.json"
SCHEMA_VERSION = "director-ir/0.2"
SHOT_ID_RE = re.compile(r"^EP\d{2}-SC\d{2}-SH\d{2}$")
PLACEHOLDERS = ("待填写", "TBD", "TODO", "适当", "电影感一些")
RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}
EXECUTION_OWNERS = {"BASE_GENERATION", "COMPOSITE", "EDIT", "AUDIO", "SHARED"}
BASE_MODES = {"AI_VIDEO", "IMAGE_TO_VIDEO", "STILL", "NONE"}
COMPOSITE_TYPES = {"SHADOW", "LIQUID", "SURFACE_STATE", "TEXT", "VFX", "OTHER"}
FALLBACK_ROUTES = {"NONE", "SPLIT_GENERATION", "ROUTE_POST", "EDIT_RESTRUCTURE"}
REFERENCE_TYPES = {"NONE", "SCENE_MASTER", "SHOT_GOLDEN", "ASSET_STATE"}
MAX_DIALOGUE_WORDS_PER_SECOND = 3.2
ELIGIBLE_PROMOTIONS = {"CROSS_WORK_SUPPORTED", "GENERAL_DEFAULT"}

sys.path.insert(0, str(SCRIPT_DIR))
from validate_scene_evidence import validate_schema_subset  # noqa: E402


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def add_issue(issues: list[dict[str, str]], level: str, code: str, path: str, message: str) -> None:
    issues.append({"level": level, "code": code, "path": path, "message": message})


def has_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return any(token in value for token in PLACEHOLDERS)
    if isinstance(value, list):
        return any(has_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(has_placeholder(item) for item in value.values())
    return False


def extract_source_dialogue(source_text: str) -> list[tuple[str, str]]:
    lines: list[tuple[str, str]] = []
    pattern = re.compile(r"^([A-Z][A-Z .()]+):\s+(.+)$")
    for raw_line in source_text.splitlines():
        match = pattern.match(raw_line.strip())
        if match:
            lines.append((match.group(1).strip(), match.group(2).strip()))
    return lines


def shot_semantic_text(shot: dict[str, Any]) -> str:
    return " ".join([
        shot.get("blocking", ""),
        shot.get("narrative_goal", ""),
        " ".join(line.get("text", "") for line in shot.get("dialogue", [])),
        " ".join(shot.get("visible_text", [])),
    ]).lower()


def go01_triggered(shot: dict[str, Any]) -> bool:
    """Preserve the v0.1 seed-rule trigger exactly; never use it for Grammar v0.2."""
    characters = {name.split(" ")[0].lower() for name in shot.get("allowed_characters", [])}
    official = bool(characters & {"adrian", "evelyn", "rook", "aurelia"})
    text = shot_semantic_text(shot)
    bureaucratic = any(term in text for term in ("账单", "欠款", "收费", "程序", "报告", "合同", "索赔", "发票", "文件", "invoice", "claim", "debt", "collections"))
    mundane = any(term in text for term in ("早餐", "吐司", "鞋", "牛奶", "水管", "学校", "生日", "床", "沙发", "五美元", "麦片", "拖鞋", "咖啡", "照片", "钥匙", "five dollars", "bedroom"))
    return official and bureaucratic and mundane


def go07_triggered(shot: dict[str, Any]) -> bool:
    """Preserve the v0.1 seed-rule trigger exactly; never use it for Grammar v0.2."""
    text = shot_semantic_text(shot)
    invitation = any(term in text for term in ("留下", "一起", "愿意", "需要我", "stay", "together", "want me"))
    refusal = any(term in text for term in ("拒绝", "不能", "不愿", "不再", "won't", "cannot", "not anymore", "not ready"))
    departure = any(term in text for term in ("离开", "转身走", "走出", "leave", "walks away", "turns away"))
    return invitation and (refusal or departure)


def evidence_rule_reference_issues(
    shot: dict[str, Any],
    grammar: dict[str, Any],
    shot_path: str,
    routing_result: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Validate rule references while preserving version-scoped v0.1 behavior.

    Grammar v0.2 may legitimately route zero evidence rules and continue under
    project/safety constraints only. The old seed grammar retains its original
    non-empty, known-rule and GO-01/GO-07 trigger checks. New routing never uses
    those legacy keyword triggers.
    """
    issues: list[dict[str, str]] = []
    grammar_version = grammar.get("schema_version")
    grammar_rules = grammar.get("rules", [])
    grammar_ids = {
        rule.get("rule_id")
        for rule in grammar_rules
        if isinstance(rule, dict) and rule.get("rule_id")
    }
    evidence_ids = shot.get("evidence_rule_ids") or []
    if grammar_version == "director-grammar/0.2" and routing_result is None:
        add_issue(
            issues,
            "error",
            "IR-ROUTING-RESULT-MISSING",
            f"{shot_path}.evidence_rule_ids",
            "Grammar v0.2 evidence references require the scene routing result.",
        )
    if not evidence_ids and grammar_version != "director-grammar/0.2":
        add_issue(
            issues,
            "error",
            "IR-EVIDENCE-REF",
            f"{shot_path}.evidence_rule_ids",
            "at least one grammar rule is required for legacy grammar",
        )
    for rule_id in evidence_ids:
        if grammar_version == "director-grammar/0.2" and rule_id.startswith("GO-"):
            add_issue(
                issues,
                "error",
                "IR-LEGACY-RULE-V02",
                f"{shot_path}.evidence_rule_ids",
                f"legacy seed rule cannot enter Grammar v0.2: {rule_id}",
            )
        if rule_id not in grammar_ids:
            add_issue(
                issues,
                "error",
                "IR-EVIDENCE-UNKNOWN",
                f"{shot_path}.evidence_rule_ids",
                f"unknown grammar rule: {rule_id}",
            )
    if grammar_version == "director-grammar/0.1":
        if "GO-01" in evidence_ids and not go01_triggered(shot):
            add_issue(
                issues,
                "error",
                "IR-GO01-TRIGGER",
                f"{shot_path}.evidence_rule_ids",
                "GO-01 requires a supernatural official applying bureaucracy to a mundane problem",
            )
        if "GO-07" in evidence_ids and not go07_triggered(shot):
            add_issue(
                issues,
                "error",
                "IR-GO07-TRIGGER",
                f"{shot_path}.evidence_rule_ids",
                "GO-07 requires an invitation/stay-together beat plus refusal or departure",
            )
    return issues


def audio_contract_issues(audio: Any, shot_path: str) -> list[dict[str, str]]:
    """Keep new audio structured while making legacy payloads visible, not invalid."""
    issues: list[dict[str, str]] = []
    if not isinstance(audio, dict):
        add_issue(issues, "error", "IR-AUDIO-SHAPE", f"{shot_path}.audio", "audio must be an object")
        return issues
    if not audio:
        return issues
    standard_keys = {"status", "instruction", "source_refs"}
    present = standard_keys & set(audio)
    if present != standard_keys:
        add_issue(
            issues,
            "warning",
            "IR-AUDIO-LEGACY-UNMAPPED",
            f"{shot_path}.audio",
            "legacy audio fields are preserved for review but have not been mapped to the v0.2 audio contract",
        )
        return issues
    if not isinstance(audio.get("status"), str) or not audio["status"].strip():
        add_issue(issues, "error", "IR-AUDIO-STATUS", f"{shot_path}.audio.status", "audio status must be a non-empty string")
    instruction = audio.get("instruction")
    if instruction is not None and not isinstance(instruction, str):
        add_issue(issues, "error", "IR-AUDIO-INSTRUCTION", f"{shot_path}.audio.instruction", "audio instruction must be a string or null")
    source_refs = audio.get("source_refs")
    if not isinstance(source_refs, list) or any(not isinstance(item, str) or not item for item in source_refs):
        add_issue(issues, "error", "IR-AUDIO-SOURCE-REFS", f"{shot_path}.audio.source_refs", "audio source_refs must be a list of non-empty strings")
    extras = sorted(set(audio) - standard_keys)
    if extras:
        add_issue(
            issues,
            "warning",
            "IR-AUDIO-LEGACY-EXTRAS",
            f"{shot_path}.audio",
            "unmapped legacy audio fields remain visible: " + ", ".join(extras),
        )
    return issues


def scene_routing_binding_issues(
    scene: dict[str, Any], grammar: dict[str, Any], scene_path: str
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    if grammar.get("schema_version") != "director-grammar/0.2":
        return issues
    routing_result = scene.get("routing_result")
    if not isinstance(routing_result, dict):
        add_issue(
            issues,
            "error",
            "IR-ROUTING-RESULT-MISSING",
            f"{scene_path}.routing_result",
            "Grammar v0.2 scenes require an embedded validated routing result.",
        )
        return issues
    routing_schema = load_json(ROUTING_RESULT_SCHEMA_PATH)
    routing_schema_issues: list[dict[str, str]] = []
    validate_schema_subset(routing_result, routing_schema, routing_schema, routing_schema_issues)
    for item in routing_schema_issues:
        add_issue(
            issues,
            "error",
            "IR-ROUTING-RESULT-SCHEMA",
            f"{scene_path}.routing_result{item['path'][1:]}",
            f"{item['code']}: {item['message']}",
        )
    if routing_schema_issues:
        return issues
    status = routing_result.get("status")
    selected_items = routing_result["selected_rules"]
    selected_ids = [
        item.get("rule_id")
        for item in selected_items
        if isinstance(item, dict) and item.get("rule_id")
    ]
    if len(selected_ids) != len(set(selected_ids)):
        add_issue(issues, "error", "IR-ROUTING-DUPLICATE", f"{scene_path}.routing_result.selected_rules", "Selected routing rule IDs must be unique.")
    grammar_ids = {
        rule.get("rule_id")
        for rule in grammar.get("rules", [])
        if isinstance(rule, dict) and rule.get("rule_id")
    }
    unknown = sorted(set(selected_ids) - grammar_ids)
    if unknown:
        add_issue(issues, "error", "IR-ROUTING-UNKNOWN", f"{scene_path}.routing_result.selected_rules", f"Routing selected unknown grammar rules: {unknown}.")
    legacy_selected = sorted(rule_id for rule_id in selected_ids if rule_id.startswith("GO-"))
    if legacy_selected:
        add_issue(issues, "error", "IR-ROUTING-LEGACY-V02", f"{scene_path}.routing_result.selected_rules", f"Legacy seed rules cannot enter Grammar v0.2: {legacy_selected}.")
    if routing_result.get("selection_count") != len(selected_ids):
        add_issue(issues, "error", "IR-ROUTING-SELECTION-COUNT", f"{scene_path}.routing_result.selection_count", "selection_count must equal the selected rule count.")
    eligible_ids = routing_result["eligible_rule_ids"]
    if not set(selected_ids).issubset(set(eligible_ids)):
        add_issue(issues, "error", "IR-ROUTING-ELIGIBLE-DRIFT", f"{scene_path}.routing_result.eligible_rule_ids", "Every selected rule must be present in eligible_rule_ids.")
    expected_eligible_ids = sorted(
        rule.get("rule_id")
        for rule in grammar.get("rules", [])
        if isinstance(rule, dict)
        and rule.get("promotion_status") in ELIGIBLE_PROMOTIONS
        and rule.get("runtime_authorized") is True
        and isinstance(rule.get("rule_id"), str)
    )
    if eligible_ids != expected_eligible_ids:
        add_issue(
            issues,
            "error",
            "IR-ROUTING-ELIGIBLE-SET-DRIFT",
            f"{scene_path}.routing_result.eligible_rule_ids",
            f"eligible_rule_ids must equal the active Grammar set: {expected_eligible_ids}.",
        )
    expected_constraint_ids = sorted(
        item.get("constraint_id")
        for key in ("project_constraints", "safety_constraints")
        for item in grammar.get(key, [])
        if isinstance(item, dict) and isinstance(item.get("constraint_id"), str)
    )
    if routing_result["applied_constraint_ids"] != expected_constraint_ids:
        add_issue(
            issues,
            "error",
            "IR-ROUTING-CONSTRAINT-DRIFT",
            f"{scene_path}.routing_result.applied_constraint_ids",
            f"applied constraints must equal the active Grammar constraints: {expected_constraint_ids}.",
        )
    rejected_ids = [
        item["rule_id"]
        for item in routing_result["rejected_rules"]
        if isinstance(item, dict) and isinstance(item.get("rule_id"), str)
    ]
    if len(rejected_ids) != len(set(rejected_ids)):
        add_issue(issues, "error", "IR-ROUTING-REJECTED-DUPLICATE", f"{scene_path}.routing_result.rejected_rules", "Rejected routing rule IDs must be unique.")
    if set(selected_ids) & set(rejected_ids):
        add_issue(issues, "error", "IR-ROUTING-DECISION-OVERLAP", f"{scene_path}.routing_result", "A rule cannot be both selected and rejected.")
    if set(selected_ids) | set(rejected_ids) != set(expected_eligible_ids):
        add_issue(
            issues,
            "error",
            "IR-ROUTING-DECISION-COVERAGE",
            f"{scene_path}.routing_result",
            "Selected and rejected rows must cover every active Grammar rule exactly once.",
        )
    raw_shots = scene.get("shots")
    if not isinstance(raw_shots, list):
        add_issue(issues, "error", "IR-ROUTING-SHOTS-SHAPE", f"{scene_path}.shots", "Scene shots must be a list before routing bindings can be checked.")
        return issues
    shot_rule_ids = {
        rule_id
        for shot in raw_shots
        if isinstance(shot, dict)
        for rule_id in shot.get("evidence_rule_ids", [])
    }
    if status == "NO_APPLICABLE_RULE":
        if selected_ids or shot_rule_ids:
            add_issue(issues, "error", "IR-ROUTING-NO-MATCH-DRIFT", f"{scene_path}.routing_result", "NO_APPLICABLE_RULE requires zero selected and cited evidence rules.")
        if routing_result.get("ir_handoff") != "CONTINUE_WITH_PROJECT_CONSTRAINTS_ONLY":
            add_issue(issues, "error", "IR-ROUTING-HANDOFF", f"{scene_path}.routing_result.ir_handoff", "NO_APPLICABLE_RULE requires the constraints-only handoff.")
    elif status == "SELECTED":
        if not selected_ids or shot_rule_ids != set(selected_ids):
            add_issue(issues, "error", "IR-ROUTING-SELECTION-DRIFT", f"{scene_path}.routing_result", "Director IR must cite every selected routing rule and no unselected rule across the scene.")
        if routing_result.get("ir_handoff") != "CONTINUE_WITH_SELECTED_RULES":
            add_issue(issues, "error", "IR-ROUTING-HANDOFF", f"{scene_path}.routing_result.ir_handoff", "SELECTED requires the selected-rules handoff.")
    else:
        add_issue(issues, "error", "IR-ROUTING-PAUSED", f"{scene_path}.routing_result.status", "A paused or invalid routing result cannot proceed to Director IR compilation.")
    if routing_result.get("human_review_status") != "HUMAN_REVIEW_PENDING":
        add_issue(issues, "error", "IR-ROUTING-REVIEW", f"{scene_path}.routing_result.human_review_status", "New routing output must remain HUMAN_REVIEW_PENDING.")
    return issues


def validate(
    ir: dict[str, Any],
    grammar: dict[str, Any],
    source_text: str | None = None,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    ir_schema = load_json(IR_SCHEMA_PATH)
    ir_schema_issues: list[dict[str, str]] = []
    validate_schema_subset(ir, ir_schema, ir_schema, ir_schema_issues)
    for item in ir_schema_issues:
        add_issue(
            issues,
            "error",
            "IR-SCHEMA",
            item["path"],
            f"{item['code']}: {item['message']}",
        )
    if ir_schema_issues:
        return {
            "validator": "drama-director-compiler/0.1",
            "episode_id": ir.get("episode_id") if isinstance(ir, dict) else None,
            "status": "FAIL",
            "errors": len(issues),
            "warnings": 0,
            "scene_count": 0,
            "shot_count": 0,
            "total_duration_seconds": 0.0,
            "issues": issues,
        }
    required_top = (
        "schema_version", "execution_medium", "project_id", "episode_id", "source_script",
        "target_duration_seconds", "duration_tolerance_seconds", "aspect_ratio",
        "status", "dialogue_must_be_verbatim", "generation_authorized",
        "publication_authorized", "director_grammar_path", "visual_style_pack_path",
        "source_facts", "scenes", "source_coverage", "unresolved",
    )
    for key in required_top:
        if key not in ir:
            add_issue(issues, "error", "IR-MISSING-TOP", key, "required top-level field is missing")

    if ir.get("schema_version") != SCHEMA_VERSION:
        add_issue(issues, "error", "IR-SCHEMA-VERSION", "schema_version", f"expected {SCHEMA_VERSION}")
    if ir.get("execution_medium") != "AI_PHOTOREAL_HUMAN":
        add_issue(issues, "error", "IR-EXECUTION-MEDIUM", "execution_medium", "expected AI_PHOTOREAL_HUMAN")
    if ir.get("generation_authorized") is not False:
        add_issue(issues, "error", "IR-GENERATION-AUTH", "generation_authorized", "must remain false in this compiler stage")
    if ir.get("publication_authorized") is not False:
        add_issue(issues, "error", "IR-PUBLICATION-AUTH", "publication_authorized", "must remain false in this compiler stage")
    if ir.get("dialogue_must_be_verbatim") is not True:
        add_issue(issues, "error", "IR-DIALOGUE-LOCK", "dialogue_must_be_verbatim", "locked scripts require verbatim dialogue")
    if has_placeholder(ir):
        add_issue(issues, "error", "IR-PLACEHOLDER", "$", "unresolved placeholder text appears inside the IR")
    continuity_output = (ir.get("source_facts") or {}).get("continuity_output")
    if not isinstance(continuity_output, list) or not continuity_output or any(not isinstance(item, str) or not item.strip() for item in continuity_output):
        add_issue(issues, "error", "IR-CONTINUITY-OUTPUT", "source_facts.continuity_output", "locked per-episode continuity output is required")
    for state_key in ("cross_episode_state_in", "cross_episode_state_out"):
        state_links = (ir.get("source_facts") or {}).get(state_key)
        if not isinstance(state_links, list):
            add_issue(issues, "error", "IR-CROSS-STATE-LIST", f"source_facts.{state_key}", "cross-episode state list is required, even when empty")
        elif any(not isinstance(item, dict) or not item.get("state_id") or not item.get("episode") for item in state_links):
            add_issue(issues, "error", "IR-CROSS-STATE-ITEM", f"source_facts.{state_key}", "cross-episode state entries need state_id and episode")

    scenes = ir.get("scenes") if isinstance(ir.get("scenes"), list) else []
    shot_ids: set[str] = set()
    shot_duration = 0.0
    scene_duration = 0.0
    ir_dialogue: list[tuple[str, str]] = []
    composite_layer_ids: set[str] = set()
    state_version_ids: set[str] = set()

    for scene_index, scene in enumerate(scenes):
        scene_path = f"scenes[{scene_index}]"
        routing_result = scene.get("routing_result") if isinstance(scene, dict) else None
        routing_context = routing_result if isinstance(routing_result, dict) else {}
        shots = scene.get("shots") if isinstance(scene, dict) and isinstance(scene.get("shots"), list) else []
        declared_scene_duration = scene.get("duration_seconds", 0)
        if not isinstance(declared_scene_duration, (int, float)) or declared_scene_duration <= 0:
            add_issue(issues, "error", "IR-SCENE-DURATION", f"{scene_path}.duration_seconds", "must be positive")
            declared_scene_duration = 0
        scene_duration += float(declared_scene_duration)
        orders = [shot.get("order") for shot in shots if isinstance(shot, dict)]
        if orders != list(range(1, len(shots) + 1)):
            add_issue(issues, "error", "IR-SHOT-ORDER", f"{scene_path}.shots", "shot order must be contiguous and start at 1")

        local_duration = 0.0
        for shot_index, shot in enumerate(shots):
            shot_path = f"{scene_path}.shots[{shot_index}]"
            shot_id = shot.get("shot_id")
            if not isinstance(shot_id, str) or not SHOT_ID_RE.match(shot_id):
                add_issue(issues, "error", "IR-SHOT-ID", f"{shot_path}.shot_id", "invalid shot ID")
            elif shot_id in shot_ids:
                add_issue(issues, "error", "IR-DUPLICATE-SHOT", f"{shot_path}.shot_id", "shot ID must be unique")
            else:
                shot_ids.add(shot_id)

            duration = shot.get("duration_seconds")
            if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
                add_issue(issues, "error", "IR-SHOT-DURATION", f"{shot_path}.duration_seconds", "must be a positive finite number")
            else:
                local_duration += float(duration)
                shot_duration += float(duration)

            if not shot.get("narrative_goal"):
                add_issue(issues, "error", "IR-NARRATIVE-GOAL", f"{shot_path}.narrative_goal", "one primary narrative goal is required")
            if not shot.get("source_refs"):
                add_issue(issues, "error", "IR-SOURCE-REF", f"{shot_path}.source_refs", "at least one locked-script source reference is required")

            issues.extend(evidence_rule_reference_issues(shot, grammar, shot_path, routing_context))
            issues.extend(audio_contract_issues(shot.get("audio"), shot_path))

            dialogue = shot.get("dialogue") or []
            dialogue_words = 0
            for dialogue_index, line in enumerate(dialogue):
                if line.get("verbatim") is not True:
                    add_issue(issues, "error", "IR-DIALOGUE-NONVERBATIM", f"{shot_path}.dialogue[{dialogue_index}]", "dialogue must be marked verbatim")
                dialogue_words += len(re.findall(r"[A-Za-z0-9]+(?:['’\-][A-Za-z0-9]+)*", line.get("text", "")))
                ir_dialogue.append((line.get("speaker", "").strip(), line.get("text", "").strip()))
            if isinstance(duration, (int, float)) and duration > 0:
                dialogue_rate = dialogue_words / float(duration)
                if dialogue_rate > MAX_DIALOGUE_WORDS_PER_SECOND:
                    add_issue(
                        issues,
                        "warning",
                        "IR-DIALOGUE-DENSITY",
                        f"{shot_path}.dialogue",
                        f"{dialogue_words} words in {duration}s ({dialogue_rate:.2f} words/s) needs a table-read or more time",
                    )

            complexity = shot.get("ai_complexity") or {}
            levels = {complexity.get("camera"), complexity.get("performance"), complexity.get("continuity")}
            if not levels.issubset(RISK_LEVELS):
                add_issue(issues, "error", "IR-RISK-LEVEL", f"{shot_path}.ai_complexity", "risk levels must be LOW, MEDIUM, or HIGH")
            if "HIGH" in levels and not shot.get("fallback"):
                add_issue(issues, "error", "IR-HIGH-RISK-FALLBACK", f"{shot_path}.fallback", "HIGH-risk shot requires a concrete fallback")

            execution = shot.get("execution_plan")
            if not isinstance(execution, dict):
                add_issue(issues, "error", "IR-EXECUTION-PLAN", f"{shot_path}.execution_plan", "execution plan is required")
                execution = {}
            base = execution.get("base_generation") or {}
            base_mode = base.get("mode")
            base_owns = base.get("owns")
            if base_mode not in BASE_MODES or not isinstance(base_owns, list):
                add_issue(issues, "error", "IR-BASE-GENERATION", f"{shot_path}.execution_plan.base_generation", "mode and owns are invalid")
            elif base_mode == "NONE" and base_owns:
                add_issue(issues, "error", "IR-BASE-NONE-OWNS", f"{shot_path}.execution_plan.base_generation.owns", "NONE mode cannot own visible elements")
            elif base_mode != "NONE" and not base_owns:
                add_issue(issues, "error", "IR-BASE-OWNS-EMPTY", f"{shot_path}.execution_plan.base_generation.owns", "base generation must own at least one visible element")

            composite_layers = execution.get("composite_layers")
            if not isinstance(composite_layers, list):
                add_issue(issues, "error", "IR-COMPOSITE-LAYERS", f"{shot_path}.execution_plan.composite_layers", "must be a list")
                composite_layers = []
            for layer_index, layer in enumerate(composite_layers):
                layer_path = f"{shot_path}.execution_plan.composite_layers[{layer_index}]"
                required_layer = ("layer_id", "type", "description", "trigger", "continuity_key")
                if not isinstance(layer, dict) or any(not layer.get(key) for key in required_layer):
                    add_issue(issues, "error", "IR-COMPOSITE-LAYER", layer_path, "composite layer is incomplete")
                    continue
                layer_id = layer["layer_id"]
                if layer_id in composite_layer_ids:
                    add_issue(issues, "error", "IR-COMPOSITE-DUPLICATE", f"{layer_path}.layer_id", "layer ID must be unique")
                composite_layer_ids.add(layer_id)
                if layer.get("type") not in COMPOSITE_TYPES:
                    add_issue(issues, "error", "IR-COMPOSITE-TYPE", f"{layer_path}.type", "unknown composite type")

            state_versions = execution.get("state_versions")
            if not isinstance(state_versions, list):
                add_issue(issues, "error", "IR-STATE-VERSIONS", f"{shot_path}.execution_plan.state_versions", "must be a list")
                state_versions = []
            for state_index, state in enumerate(state_versions):
                state_path = f"{shot_path}.execution_plan.state_versions[{state_index}]"
                required_state = ("state_id", "subject", "state", "owner", "effective_from")
                if not isinstance(state, dict) or any(not state.get(key) for key in required_state):
                    add_issue(issues, "error", "IR-STATE-VERSION", state_path, "state version is incomplete")
                    continue
                state_id = state["state_id"]
                # Reuse across shots is expected only when all state facts are identical.
                state_signature = json.dumps(state, sort_keys=True, ensure_ascii=False)
                state_key = f"{state_id}\u0000{state_signature}"
                conflicting = any(existing.startswith(f"{state_id}\u0000") and existing != state_key for existing in state_version_ids)
                if conflicting:
                    add_issue(issues, "error", "IR-STATE-CONFLICT", f"{state_path}.state_id", "same state ID has conflicting definitions")
                state_version_ids.add(state_key)
                if state.get("owner") not in EXECUTION_OWNERS:
                    add_issue(issues, "error", "IR-STATE-OWNER", f"{state_path}.owner", "unknown state owner")

            continuity_owners = execution.get("continuity_owners") or {}
            for owner_key in ("identity", "surface", "prop", "environment"):
                if continuity_owners.get(owner_key) not in EXECUTION_OWNERS:
                    add_issue(issues, "error", "IR-CONTINUITY-OWNER", f"{shot_path}.execution_plan.continuity_owners.{owner_key}", "owner is missing or invalid")

            fallback_route = execution.get("fallback_route") or {}
            fallback_decision = fallback_route.get("decision")
            fallback_action = fallback_route.get("action")
            if fallback_decision not in FALLBACK_ROUTES or not isinstance(fallback_action, str):
                add_issue(issues, "error", "IR-FALLBACK-ROUTE", f"{shot_path}.execution_plan.fallback_route", "decision and action are invalid")
            elif fallback_decision == "NONE" and fallback_action:
                add_issue(issues, "error", "IR-FALLBACK-NONE-ACTION", f"{shot_path}.execution_plan.fallback_route.action", "NONE route must have an empty action")
            elif fallback_decision != "NONE" and not fallback_action:
                add_issue(issues, "error", "IR-FALLBACK-ACTION", f"{shot_path}.execution_plan.fallback_route.action", "non-NONE route needs a concrete action")
            if "HIGH" in levels and fallback_decision == "NONE":
                add_issue(issues, "error", "IR-HIGH-RISK-ROUTE", f"{shot_path}.execution_plan.fallback_route", "HIGH-risk shot requires a typed fallback route")

            reference = shot.get("reference_plan")
            if not isinstance(reference, dict):
                add_issue(issues, "error", "IR-REFERENCE-PLAN", f"{shot_path}.reference_plan", "reference plan is required")
                reference = {}
            reference_required = reference.get("required")
            reference_type = reference.get("reference_type")
            reference_id = reference.get("reference_id")
            reference_status = reference.get("status")
            rights_status = reference.get("rights_status")
            inherit = reference.get("inherit")
            exclude = reference.get("exclude")
            if not isinstance(reference_required, bool) or reference_type not in REFERENCE_TYPES:
                add_issue(issues, "error", "IR-REFERENCE-SHAPE", f"{shot_path}.reference_plan", "required/type are invalid")
            elif reference_required:
                if reference_type == "NONE" or not isinstance(reference_id, str) or not reference_id.startswith("REF-"):
                    add_issue(issues, "error", "IR-REFERENCE-REQUIRED", f"{shot_path}.reference_plan", "required reference needs a stable REF-* ID and non-NONE type")
                if reference_status not in {"PLANNED", "APPROVED"} or rights_status != "PROJECT_ORIGINAL":
                    add_issue(issues, "error", "IR-REFERENCE-RIGHTS", f"{shot_path}.reference_plan", "required reference must be planned/approved and project-original")
                if not reference.get("scope") or not isinstance(inherit, list) or not inherit or not isinstance(exclude, list) or not exclude:
                    add_issue(issues, "error", "IR-REFERENCE-SCOPE", f"{shot_path}.reference_plan", "required reference needs scope plus non-empty inherit/exclude")
            else:
                if reference_type != "NONE" or reference_id is not None or reference_status != "NOT_REQUIRED" or rights_status != "NOT_APPLICABLE":
                    add_issue(issues, "error", "IR-REFERENCE-NONE", f"{shot_path}.reference_plan", "non-required reference must use NONE/null/NOT_REQUIRED/NOT_APPLICABLE")
                if inherit not in ([], None) or exclude not in ([], None):
                    add_issue(issues, "error", "IR-REFERENCE-NONE-SCOPE", f"{shot_path}.reference_plan", "non-required reference cannot inherit or exclude")

            motion = shot.get("camera_motion") or {}
            if not isinstance(motion, dict) or not motion.get("mode") or not motion.get("reason"):
                add_issue(issues, "error", "IR-CAMERA-MOTION", f"{shot_path}.camera_motion", "camera motion needs mode and narrative reason")
            camera_path = shot.get("camera_path") or {}
            if not shot.get("camera_start") or not shot.get("camera_end"):
                add_issue(issues, "error", "IR-CAMERA-ENDPOINTS", shot_path, "camera_start and camera_end are required")
            for camera_key in ("mode", "direction", "speed", "distance", "stability", "trigger"):
                if not camera_path.get(camera_key):
                    add_issue(issues, "error", "IR-CAMERA-PATH", f"{shot_path}.camera_path.{camera_key}", "camera path field is required")
            if motion.get("mode") and camera_path.get("mode") and motion["mode"] != camera_path["mode"]:
                add_issue(issues, "error", "IR-CAMERA-MODE-MISMATCH", f"{shot_path}.camera_path.mode", "camera_motion and camera_path modes disagree")

            for field in ("continuity_in", "continuity_out", "edit_in", "edit_out"):
                if not shot.get(field):
                    add_issue(issues, "error", "IR-CONNECTION", f"{shot_path}.{field}", "connection field must not be empty")

        if abs(local_duration - float(declared_scene_duration)) > 0.01:
            add_issue(
                issues,
                "error",
                "IR-SCENE-SUM",
                f"{scene_path}.duration_seconds",
                f"declared {declared_scene_duration}, shots sum to {round(local_duration, 3)}",
            )
        issues.extend(scene_routing_binding_issues(scene, grammar, scene_path))

    target = ir.get("target_duration_seconds", 0)
    tolerance = ir.get("duration_tolerance_seconds", 0)
    if isinstance(target, (int, float)) and isinstance(tolerance, (int, float)):
        if abs(shot_duration - float(target)) > float(tolerance):
            add_issue(issues, "error", "IR-EPISODE-DURATION", "target_duration_seconds", f"shots sum to {round(shot_duration, 3)}, outside target tolerance")
    if abs(scene_duration - shot_duration) > 0.01:
        add_issue(issues, "error", "IR-EPISODE-SUM", "scenes", "scene durations and shot durations do not agree")

    coverage = ir.get("source_coverage") if isinstance(ir.get("source_coverage"), list) else []
    declared_source_units = (ir.get("source_facts") or {}).get("source_unit_count")
    if declared_source_units is not None and declared_source_units != len(coverage):
        add_issue(issues, "error", "IR-SOURCE-UNIT-COUNT", "source_facts.source_unit_count", f"declared {declared_source_units}, coverage has {len(coverage)} units")
    coverage_refs: set[str] = set()
    for index, item in enumerate(coverage):
        item_path = f"source_coverage[{index}]"
        source_ref = item.get("source_ref")
        if source_ref in coverage_refs:
            add_issue(issues, "error", "IR-COVERAGE-DUPLICATE", f"{item_path}.source_ref", "source reference must be unique")
        coverage_refs.add(source_ref)
        if item.get("status") != "covered":
            add_issue(issues, "error", "IR-COVERAGE-STATUS", f"{item_path}.status", "locked-script source beat is not covered")
        covered_by = item.get("covered_by") or []
        if not covered_by:
            add_issue(issues, "error", "IR-COVERAGE-EMPTY", f"{item_path}.covered_by", "covered source beat needs at least one shot")
        for shot_id in covered_by:
            if shot_id not in shot_ids:
                add_issue(issues, "error", "IR-COVERAGE-SHOT", f"{item_path}.covered_by", f"unknown shot ID: {shot_id}")

    visual_path = ir.get("visual_style_pack_path")
    if visual_path in (None, "UNRESOLVED"):
        add_issue(issues, "warning", "IR-VISUAL-PACK", "visual_style_pack_path", "visual style pack is not yet bound")
    for scene in scenes:
        for shot in scene.get("shots", []):
            if shot.get("visual_style_module") == "UNRESOLVED":
                add_issue(issues, "warning", "IR-VISUAL-MODULE", shot.get("shot_id", "unknown"), "visual module is unresolved")
    if not any(
        shot.get("reference_plan", {}).get("reference_type") == "SHOT_GOLDEN"
        for scene in scenes for shot in scene.get("shots", [])
    ):
        add_issue(issues, "error", "IR-GOLDEN-REFERENCE", "scenes", "at least one project-original Shot Golden reference plan is required")

    if source_text is not None:
        source_dialogue = extract_source_dialogue(source_text)
        if source_dialogue != ir_dialogue:
            mismatch_at = next(
                (index for index, pair in enumerate(zip(source_dialogue, ir_dialogue)) if pair[0] != pair[1]),
                min(len(source_dialogue), len(ir_dialogue)),
            )
            source_value = source_dialogue[mismatch_at] if mismatch_at < len(source_dialogue) else "<missing>"
            ir_value = ir_dialogue[mismatch_at] if mismatch_at < len(ir_dialogue) else "<missing>"
            add_issue(
                issues,
                "error",
                "IR-DIALOGUE-SOURCE-MISMATCH",
                "scenes[*].shots[*].dialogue",
                f"first mismatch at dialogue index {mismatch_at}: source={source_value!r}, ir={ir_value!r}",
            )

    errors = sum(issue["level"] == "error" for issue in issues)
    warnings = sum(issue["level"] == "warning" for issue in issues)
    return {
        "validator": "drama-director-compiler/0.1",
        "episode_id": ir.get("episode_id"),
        "status": "PASS" if errors == 0 else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "scene_count": len(scenes),
        "shot_count": len(shot_ids),
        "total_duration_seconds": round(shot_duration, 3),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ir", type=Path, required=True)
    parser.add_argument("--grammar", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    ir = load_json(args.ir)
    source_path = Path(ir.get("source_script", ""))
    if not source_path.is_absolute():
        source_path = Path.cwd() / source_path
    source_text = source_path.read_text(encoding="utf-8") if source_path.is_file() else None
    report = validate(ir, load_json(args.grammar), source_text)
    if source_text is None:
        add_issue(report["issues"], "error", "IR-SOURCE-MISSING", "source_script", f"source script not found: {source_path}")
        report["errors"] += 1
        report["status"] = "FAIL"
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    sys.stdout.write(output)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
