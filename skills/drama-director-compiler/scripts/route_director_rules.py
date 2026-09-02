#!/usr/bin/env python3
"""Route a rights-safe original scene descriptor through Director Grammar v0.2."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
INPUT_SCHEMA_PATH = SKILL_ROOT / "references" / "director-routing-input.schema.json"
RESULT_SCHEMA_PATH = SKILL_ROOT / "references" / "director-routing-result.schema.json"

sys.path.insert(0, str(SCRIPT_DIR))
from validate_director_grammar import (  # noqa: E402
    CONFLICT_PRIORITY,
    INDEX_PATH,
    MATRIX_PATH,
    SCHEMA_PATH as GRAMMAR_SCHEMA_PATH,
    read_json,
    validate_grammar,
)
from validate_scene_evidence import validate_schema_subset  # noqa: E402


ELIGIBLE_PROMOTIONS = {"CROSS_WORK_SUPPORTED", "GENERAL_DEFAULT"}
NO_SPECIALIZED_PROBLEM = "NO_SPECIALIZED_PROBLEM"


def _constraint_blockers(
    scene: dict[str, Any], rule_id: str
) -> list[dict[str, Any]]:
    order = {level: index for index, level in enumerate(CONFLICT_PRIORITY)}
    blockers = [
        item
        for item in scene.get("priority_constraints", [])
        if rule_id in item.get("blocked_rule_ids", [])
    ]
    return sorted(blockers, key=lambda item: (order[item["priority_level"]], item["constraint_id"]))


def _rule_rank(rule: dict[str, Any], primary: str, secondary: set[str]) -> tuple[Any, ...]:
    problems = rule.get("routing", {}).get("scene_problems", [])
    problem_rank = 0 if primary in problems else 1 if secondary.intersection(problems) else 2
    promotion_rank = 0 if rule.get("promotion_status") == "GENERAL_DEFAULT" else 1
    return (
        problem_rank,
        -len(rule.get("routing", {}).get("required_fact_types", [])),
        promotion_rank,
        rule.get("selection_rank", 999999),
        rule.get("rule_id", ""),
    )


def route_scene(scene: dict[str, Any], grammar: dict[str, Any]) -> dict[str, Any]:
    facts = scene.get("locked_facts", [])
    fact_types = {fact.get("fact_type") for fact in facts}
    fact_ids_by_type: dict[str, list[str]] = {}
    for fact in facts:
        fact_ids_by_type.setdefault(fact.get("fact_type"), []).append(fact.get("fact_id"))
    unknown_types = set(scene.get("unknown_fact_types", []))
    signals = set(scene.get("routing_signals", []))
    primary = scene.get("scene_problem", {}).get("primary", "UNKNOWN")
    secondary = set(scene.get("scene_problem", {}).get("secondary", []))
    subject_tags = set(scene.get("subject_matter_tags", []))

    candidate_rules: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    conflict_trace: list[dict[str, str]] = []

    for rule in grammar.get("rules", []):
        rule_id = rule.get("rule_id", "UNKNOWN-RULE")
        routing = rule.get("routing", {})
        reasons: set[str] = set()
        missing_types: set[str] = set()
        blocking_fact_ids: set[str] = set()
        conflicting_rule_ids: set[str] = set()

        if rule.get("promotion_status") not in ELIGIBLE_PROMOTIONS:
            reasons.add("PROMOTION_INELIGIBLE")
        if rule.get("runtime_authorized") is not True:
            reasons.add("NOT_RUNTIME_AUTHORIZED")
        if primary == NO_SPECIALIZED_PROBLEM:
            reasons.add("NO_SPECIALIZED_PROBLEM")
        problems = set(routing.get("scene_problems", []))
        if primary not in problems and not secondary.intersection(problems):
            reasons.add("SCENE_PROBLEM_MISMATCH")
        trigger_all = set(routing.get("trigger_all_of", []))
        trigger_any = set(routing.get("trigger_any_of", []))
        trigger_matches = trigger_all.issubset(signals) and (not trigger_any or bool(trigger_any & signals))
        if not trigger_matches:
            reasons.add("TRIGGER_NOT_MET")
        required_types = set(routing.get("required_fact_types", []))
        if not required_types:
            reasons.add("REQUIRED_FACT_MAPPING_MISSING")
        missing_types.update(required_types - fact_types)
        if missing_types:
            reasons.add("REQUIRED_FACT_MISSING")
        unknown_required = required_types & unknown_types
        if unknown_required:
            reasons.add("REQUIRED_FACT_UNKNOWN")
            missing_types.update(unknown_required)
        not_applicable = set(routing.get("not_applicable_if_any", [])) & signals
        if not_applicable:
            reasons.add("NOT_APPLICABLE_MATCH")
        blockers = _constraint_blockers(scene, rule_id)
        if blockers:
            reasons.add("EXPLICIT_RULE_CONFLICT")
            first = blockers[0]
            conflict_trace.append({
                "priority_level": first["priority_level"],
                "winner_id": first["constraint_id"],
                "loser_id": rule_id,
                "resolution_code": "HIGHER_PRIORITY_CONSTRAINT",
            })
        if (
            reasons
            and subject_tags.intersection(set(routing.get("audit_subject_tags", [])))
            and {"TRIGGER_NOT_MET", "SCENE_PROBLEM_MISMATCH"}.intersection(reasons)
        ):
            reasons.add("SUBJECT_SIMILARITY_ONLY")

        if reasons:
            rejected.append({
                "rule_id": rule_id,
                "rejection_reason_codes": sorted(reasons),
                "missing_fact_types": sorted(missing_types),
                "blocking_fact_ids": sorted(blocking_fact_ids),
                "conflicting_rule_ids": sorted(conflicting_rule_ids),
            })
        else:
            candidate_rules.append(rule)

    candidate_rules.sort(key=lambda item: _rule_rank(item, primary, secondary))
    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    maximum = grammar.get("selection_policy", {}).get("maximum", 4)
    for rule in candidate_rules:
        rule_id = rule["rule_id"]
        conflicts = set(rule.get("routing", {}).get("conflicts_with", []))
        conflicting = sorted(selected_ids & conflicts)
        reverse_conflicting = sorted(
            selected_rule["rule_id"]
            for selected_rule in candidate_rules
            if selected_rule.get("rule_id") in selected_ids
            and rule_id in set(selected_rule.get("routing", {}).get("conflicts_with", []))
        )
        conflicting = sorted(set(conflicting + reverse_conflicting))
        if conflicting:
            rejected.append({
                "rule_id": rule_id,
                "rejection_reason_codes": ["EXPLICIT_RULE_CONFLICT"],
                "missing_fact_types": [],
                "blocking_fact_ids": [],
                "conflicting_rule_ids": conflicting,
            })
            conflict_trace.append({
                "priority_level": "TRIGGER_SPECIFIC_DIRECTOR_RULES",
                "winner_id": conflicting[0],
                "loser_id": rule_id,
                "resolution_code": "EARLIER_DETERMINISTIC_RULE",
            })
            continue
        if len(selected) >= maximum:
            rejected.append({
                "rule_id": rule_id,
                "rejection_reason_codes": ["CAP_EXCEEDED_LOWER_PRECEDENCE"],
                "missing_fact_types": [],
                "blocking_fact_ids": [],
                "conflicting_rule_ids": [],
            })
            continue
        problems = set(rule["routing"]["scene_problems"])
        reason_codes = {
            "RUNTIME_AUTHORIZED",
            "TRIGGER_MATCH",
            "REQUIRED_FACTS_LOCKED",
            "PRIMARY_PROBLEM_MATCH" if primary in problems else "SECONDARY_PROBLEM_MATCH",
        }
        matched_fact_ids = sorted(
            fact_id
            for fact_type in rule["routing"].get("required_fact_types", [])
            for fact_id in fact_ids_by_type.get(fact_type, [])
        )
        selected.append({
            "rule_id": rule_id,
            "selection_reason_codes": sorted(reason_codes),
            "matched_fact_ids": matched_fact_ids,
        })
        selected_ids.add(rule_id)

    selected.sort(key=lambda item: item["rule_id"])
    rejected.sort(key=lambda item: item["rule_id"])
    order = {level: index for index, level in enumerate(CONFLICT_PRIORITY)}
    conflict_trace.sort(key=lambda item: (order[item["priority_level"]], item["winner_id"], item["loser_id"]))
    status = "SELECTED" if selected else "NO_APPLICABLE_RULE"
    return {
        "schema_version": "director-routing-result/0.1",
        "case_id": scene.get("case_id", "UNKNOWN-CASE"),
        "status": status,
        "scene_problem": primary,
        "applied_constraint_ids": sorted(
            item["constraint_id"]
            for key in ("project_constraints", "safety_constraints")
            for item in grammar.get(key, [])
        ),
        "eligible_rule_ids": sorted(rule.get("rule_id") for rule in grammar.get("rules", []) if rule.get("promotion_status") in ELIGIBLE_PROMOTIONS and rule.get("runtime_authorized") is True),
        "selected_rules": selected,
        "rejected_rules": rejected,
        "conflict_trace": conflict_trace,
        "selection_count": len(selected),
        "ir_handoff": "CONTINUE_WITH_SELECTED_RULES" if selected else "CONTINUE_WITH_PROJECT_CONSTRAINTS_ONLY",
        "human_review_status": "HUMAN_REVIEW_PENDING",
        "rights_boundary": {
            "surface_copy_allowed": False,
            "subject_matter_used_for_selection": False,
        },
    }


def schema_issues(value: dict[str, Any], schema_path: Path) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    schema = read_json(schema_path)
    validate_schema_subset(value, schema, schema, issues, "$")
    if schema_path == INPUT_SCHEMA_PATH and isinstance(value, dict):
        problem = value.get("scene_problem")
        if isinstance(problem, dict):
            secondary = problem.get("secondary")
            if isinstance(secondary, list) and NO_SPECIALIZED_PROBLEM in secondary:
                issues.append({
                    "level": "error",
                    "code": "ROUTING-NO-SPECIALIZED-SECONDARY",
                    "path": "$.scene_problem.secondary",
                    "message": "NO_SPECIALIZED_PROBLEM is an exclusive primary negative sentinel",
                })
            if problem.get("primary") == NO_SPECIALIZED_PROBLEM and secondary:
                issues.append({
                    "level": "error",
                    "code": "ROUTING-NO-SPECIALIZED-EXCLUSIVE",
                    "path": "$.scene_problem",
                    "message": "NO_SPECIALIZED_PROBLEM cannot be combined with secondary problems",
                })
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", type=Path, required=True)
    parser.add_argument("--grammar", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    scene = read_json(args.scene)
    grammar = read_json(args.grammar)
    issues = schema_issues(scene, INPUT_SCHEMA_PATH)
    if issues:
        sys.stdout.write(json.dumps({"status": "INVALID_INPUT", "issues": issues}, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        return 1
    grammar_report = validate_grammar(
        grammar,
        read_json(INDEX_PATH),
        read_json(MATRIX_PATH),
        read_json(GRAMMAR_SCHEMA_PATH),
    )
    if grammar_report["status"] != "PASS":
        sys.stdout.write(json.dumps({"status": "INVALID_GRAMMAR", "issues": grammar_report["issues"]}, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        return 1
    result = route_scene(scene, grammar)
    result_issues = schema_issues(result, RESULT_SCHEMA_PATH)
    if result_issues:
        sys.stdout.write(json.dumps({"status": "INVALID_RESULT", "issues": result_issues}, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        return 1
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.check:
            if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
                return 1
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
