#!/usr/bin/env python3
"""Validate the eight rights-safe Phase 3 routing cases deterministically."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
CASES_PATH = SKILL_ROOT / "tests" / "fixtures" / "routing_cases.json"
GRAMMAR_PATH = REPOSITORY_ROOT / "research" / "grammar" / "director_grammar_v0.2.json"
REPORT_PATH = REPOSITORY_ROOT / "research" / "validation" / "director-routing-validation.json"

sys.path.insert(0, str(SCRIPT_DIR))
from route_director_rules import (  # noqa: E402
    INPUT_SCHEMA_PATH,
    RESULT_SCHEMA_PATH,
    route_scene,
    schema_issues,
)
from validate_director_grammar import (  # noqa: E402
    INDEX_PATH,
    MATRIX_PATH,
    SCHEMA_PATH,
    read_json,
    validate_grammar,
)


EXPECTED_CASE_IDS = {
    "ORIGINAL-POWER-DIALOGUE",
    "ORIGINAL-RELATIONSHIP-FRACTURE",
    "ORIGINAL-PUBLIC-REVEAL",
    "ORIGINAL-PROCEDURE",
    "ORIGINAL-ACTION-CAUSALITY",
    "ORIGINAL-PROXIMITY-TENSION",
    "ORIGINAL-SOUND-SUSPENSE",
    "ORIGINAL-NO-APPLICABLE-RULE",
}


def validate_cases(
    cases: list[dict[str, Any]], grammar: dict[str, Any]
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    results: list[dict[str, Any]] = []
    case_ids = [case.get("case_id") for case in cases if isinstance(case, dict)]
    if set(case_ids) != EXPECTED_CASE_IDS or len(case_ids) != len(EXPECTED_CASE_IDS):
        issues.append({
            "level": "error",
            "code": "ROUTING-CASE-SET",
            "path": "cases",
            "message": "The required eight unique original routing cases are not present.",
        })
    for index, case in enumerate(cases):
        input_issues = schema_issues(case, INPUT_SCHEMA_PATH)
        for issue in input_issues:
            issues.append({**issue, "path": f"cases[{index}].{issue['path']}"})
        if input_issues:
            continue
        result = route_scene(case, grammar)
        result_issues = schema_issues(result, RESULT_SCHEMA_PATH)
        for issue in result_issues:
            issues.append({**issue, "path": f"results[{index}].{issue['path']}"})
        if result.get("selection_count", 0) > 4:
            issues.append({
                "level": "error",
                "code": "ROUTING-SELECTION-CAP",
                "path": f"results[{index}].selection_count",
                "message": "Routing selected more than four evidence rules.",
            })
        if not grammar.get("rules") and (
            result.get("status") != "NO_APPLICABLE_RULE"
            or result.get("selection_count") != 0
            or result.get("ir_handoff") != "CONTINUE_WITH_PROJECT_CONSTRAINTS_ONLY"
        ):
            issues.append({
                "level": "error",
                "code": "ROUTING-ZERO-RULE-FALLBACK",
                "path": f"results[{index}]",
                "message": "A zero-rule grammar must return NO_APPLICABLE_RULE and constraints-only handoff.",
            })
        results.append({
            "case_id": result["case_id"],
            "status": result["status"],
            "selection_count": result["selection_count"],
            "ir_handoff": result["ir_handoff"],
            "human_review_status": result["human_review_status"],
        })
    results.sort(key=lambda item: item["case_id"])
    return {
        "schema_version": "director-routing-validation/0.1",
        "status": "PASS" if not issues else "FAIL",
        "case_count": len(cases),
        "no_applicable_rule_count": sum(item["status"] == "NO_APPLICABLE_RULE" for item in results),
        "selected_rule_count": sum(item["selection_count"] for item in results),
        "error_count": len(issues),
        "cases": results,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=CASES_PATH)
    parser.add_argument("--grammar", type=Path, default=GRAMMAR_PATH)
    parser.add_argument("--index", type=Path, default=INDEX_PATH)
    parser.add_argument("--matrix", type=Path, default=MATRIX_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    grammar = read_json(args.grammar)
    grammar_report = validate_grammar(
        grammar,
        read_json(args.index),
        read_json(args.matrix),
        read_json(args.schema),
    )
    if grammar_report["status"] == "PASS":
        cases = json.loads(args.cases.read_text(encoding="utf-8"))
        report = validate_cases(cases, grammar)
    else:
        report = {
            "schema_version": "director-routing-validation/0.1",
            "status": "FAIL",
            "case_count": 0,
            "no_applicable_rule_count": 0,
            "selected_rule_count": 0,
            "error_count": grammar_report["error_count"],
            "cases": [],
            "issues": grammar_report["issues"],
        }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
