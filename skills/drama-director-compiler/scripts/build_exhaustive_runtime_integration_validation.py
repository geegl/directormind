#!/usr/bin/env python3
"""Build the deterministic end-to-end exhaustive runtime-integration report."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
REVIEW_PATH = REPOSITORY_ROOT / "research" / "grammar" / "runtime_integration.review.json"
CANDIDATE_INDEX_PATH = REPOSITORY_ROOT / "research" / "grammar" / "candidate_rule_index.json"
MATRIX_PATH = REPOSITORY_ROOT / "research" / "grammar" / "cross_work_support_matrix.json"
GRAMMAR_PATH = REPOSITORY_ROOT / "research" / "grammar" / "director_grammar_v0.2.json"
FORWARD_INDEX_PATH = REPOSITORY_ROOT / "examples" / "forward-tests" / "index.json"
FORWARD_ROOT = FORWARD_INDEX_PATH.parent
EVIDENCE_ROOT = REPOSITORY_ROOT / "research" / "evidence"
REPORT_PATH = REPOSITORY_ROOT / "research" / "validation" / "exhaustive-runtime-integration-validation.json"

sys.path.insert(0, str(SCRIPT_DIR))
from validate_candidate_rules import validate_repository as validate_candidates  # noqa: E402
from validate_director_grammar import SCHEMA_PATH as GRAMMAR_SCHEMA_PATH  # noqa: E402
from validate_director_grammar import validate_grammar  # noqa: E402
from validate_forward_tests import INDEX_SCHEMA_PATH as FORWARD_SCHEMA_PATH  # noqa: E402
from validate_forward_tests import validate_repository as validate_forward  # noqa: E402
from validate_runtime_integration_review import SCHEMA_PATH as REVIEW_SCHEMA_PATH  # noqa: E402
from validate_runtime_integration_review import validate as validate_review  # noqa: E402
from validate_scene_evidence import _same_file_target, _write_report_atomically  # noqa: E402
from route_director_rules import route_scene  # noqa: E402


FINAL_STATUSES = {
    "POSITIVE_RUNTIME_RULE",
    "SUPPORTING_EVIDENCE",
    "BOUNDARY_OR_COUNTEREXAMPLE",
    "MERGED_DUPLICATE",
    "REJECTED_WITH_REASON",
}


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def add_issue(issues: list[dict[str, str]], code: str, path: str, message: str) -> None:
    issues.append({"level": "error", "code": code, "path": path, "message": message})


def build_report() -> dict[str, Any]:
    review = read_json(REVIEW_PATH)
    candidate_index = read_json(CANDIDATE_INDEX_PATH)
    matrix = read_json(MATRIX_PATH)
    grammar = read_json(GRAMMAR_PATH)
    forward_index = read_json(FORWARD_INDEX_PATH)
    grammar_schema = read_json(GRAMMAR_SCHEMA_PATH)
    review_report = validate_review(review, read_json(REVIEW_SCHEMA_PATH))
    candidate_report = validate_candidates(candidate_index, matrix)
    grammar_report = validate_grammar(grammar, candidate_index, matrix, grammar_schema)
    forward_report = validate_forward(
        forward_index,
        grammar,
        candidate_index,
        matrix,
        grammar_schema,
        read_json(FORWARD_SCHEMA_PATH),
    )
    issues: list[dict[str, str]] = []
    for name, report in (
        ("review", review_report),
        ("candidate", candidate_report),
        ("grammar", grammar_report),
        ("forward", forward_report),
    ):
        if report.get("status") != "PASS":
            add_issue(issues, "EXHAUSTIVE-UPSTREAM-FAIL", name, f"{name} authority did not pass.")

    dispositions = review["candidate_dispositions"]
    specs = review["runtime_rule_specs"]
    rules_by_id = {item["rule_id"]: item for item in grammar["rules"]}
    positive_rule_ids = {
        item["target_rule_id"]
        for item in dispositions
        if item["final_status"] == "POSITIVE_RUNTIME_RULE"
    }
    if set(rules_by_id) != positive_rule_ids:
        add_issue(issues, "EXHAUSTIVE-RULE-SET", "grammar.rules", "Runtime Grammar must exactly equal positive dispositions.")

    forward_by_id = {item["test_case_id"]: item for item in forward_index["cases"]}
    for spec in specs:
        rule_id = spec["rule_id"]
        positive_id = spec["candidate_rule_id"]
        related = [
            item for item in dispositions
            if (
                item["final_status"] in {"SUPPORTING_EVIDENCE", "BOUNDARY_OR_COUNTEREXAMPLE"}
                and item["target_rule_id"] == rule_id
            )
            or (
                item["final_status"] == "MERGED_DUPLICATE"
                and item["merged_into_candidate_id"] == positive_id
            )
        ]
        expected_candidate_ids = {positive_id, *(item["candidate_rule_id"] for item in related)}
        expected_shots = {*(spec["source_refs"]), *(ref for item in related for ref in item["source_refs"])}
        rule = rules_by_id.get(rule_id, {})
        lineage = rule.get("evidence_lineage", {})
        if set(lineage.get("candidate_rule_ids", [])) != expected_candidate_ids:
            add_issue(issues, "EXHAUSTIVE-LINEAGE-CANDIDATE", rule_id, "Rule candidate lineage differs from final dispositions.")
        if set(lineage.get("evidence_shot_ids", [])) != expected_shots:
            add_issue(issues, "EXHAUSTIVE-LINEAGE-SHOT", rule_id, "Rule Shot lineage differs from fresh reviewed disposition refs.")

        positive_case = forward_by_id.get(spec["positive_forward_test_id"], {})
        if (
            positive_case.get("test_mode") != "POSITIVE"
            or positive_case.get("expected_selected_rule_ids") != [rule_id]
            or not positive_case.get("changed_director_dimensions")
        ):
            add_issue(issues, "EXHAUSTIVE-POSITIVE-FORWARD", rule_id, "Positive package must select the rule and change a director decision axis.")
        boundary_case = forward_by_id.get(spec["boundary_forward_test_id"], {})
        result_path = REPOSITORY_ROOT / boundary_case.get("package_path", "") / "selected-rules.json"
        result = read_json(result_path) if result_path.is_file() else {}
        rejected = next((item for item in result.get("rejected_rules", []) if item.get("rule_id") == rule_id), {})
        expected_boundary_signals = {
            signal
            for item in related
            if item["final_status"] == "BOUNDARY_OR_COUNTEREXAMPLE"
            for signal in item["boundary_signal_ids"]
        }
        matched_boundary_signals = set(
            rejected.get("matched_not_applicable_signal_ids", [])
        )
        compiled_not_applicable_signals = set(
            rule.get("routing", {}).get("not_applicable_if_any", [])
        )
        if (
            boundary_case.get("test_mode") != "BOUNDARY_OR_NON_APPLICABLE"
            or result.get("status") != "NO_APPLICABLE_RULE"
            or "NOT_APPLICABLE_MATCH" not in rejected.get("rejection_reason_codes", [])
            or not matched_boundary_signals
            or not matched_boundary_signals.issubset(
                compiled_not_applicable_signals
            )
        ):
            add_issue(issues, "EXHAUSTIVE-BOUNDARY-FORWARD", rule_id, "Boundary package must block the rule with one or more reviewed negative signals.")

        positive_input_path = (
            REPOSITORY_ROOT
            / positive_case.get("package_path", "")
            / "routing-input.json"
        )
        positive_input = read_json(positive_input_path) if positive_input_path.is_file() else {}
        for signal_id in sorted(expected_boundary_signals):
            probe = copy.deepcopy(positive_input)
            probe["case_id"] = f"BOUNDARY-PROBE-{rule_id}-{signal_id}"
            probe["routing_signals"] = sorted(
                set(probe.get("routing_signals", [])) | {signal_id}
            )
            probe_result = route_scene(probe, grammar)
            probe_rejection = next(
                (
                    item
                    for item in probe_result.get("rejected_rules", [])
                    if item.get("rule_id") == rule_id
                ),
                {},
            )
            if (
                any(
                    item.get("rule_id") == rule_id
                    for item in probe_result.get("selected_rules", [])
                )
                or "NOT_APPLICABLE_MATCH"
                not in probe_rejection.get("rejection_reason_codes", [])
                or signal_id
                not in probe_rejection.get("matched_not_applicable_signal_ids", [])
            ):
                add_issue(
                    issues,
                    "EXHAUSTIVE-BOUNDARY-SIGNAL-PROBE",
                    f"{rule_id}:{signal_id}",
                    "Each reviewed boundary signal must independently block its target rule when applied to the positive original case.",
                )

    rejected_ids = {
        item["candidate_rule_id"]
        for item in dispositions
        if item["final_status"] == "REJECTED_WITH_REASON"
    }
    leaked_rejections = rejected_ids.intersection(
        rule["promotion_source_candidate_id"] for rule in grammar["rules"]
    )
    if leaked_rejections:
        add_issue(issues, "EXHAUSTIVE-REJECTION-LEAK", "grammar.rules", "Rejected candidates cannot become runtime rule sources.")

    family_ids = sorted(item["family_id"] for item in candidate_index["families"])
    family_results = []
    for family_id in family_ids:
        rows = [item for item in dispositions if item["family_id"] == family_id]
        participating_rows = [
            item for item in rows if item["final_status"] in FINAL_STATUSES
        ]
        active_rules = sorted({
            item["target_rule_id"]
            for item in participating_rows
            if item.get("target_rule_id")
        })
        family_results.append({
            "family_id": family_id,
            "candidate_count": len(rows),
            "final_disposition_count": sum(item["final_status"] in FINAL_STATUSES for item in rows),
            "pending_evidence_gap_count": sum(item["final_status"] == "EVIDENCE_GAP_PENDING" for item in rows),
            "existing_material_review_required_count": sum(
                item["final_status"] == "EXISTING_MATERIAL_REVIEW_REQUIRED"
                for item in rows
            ),
            "active_rule_ids": active_rules,
            "runtime_status": (
                "PARTICIPATING"
                if participating_rows
                else "IN_PROGRESS"
            ),
        })

    final_counts = Counter(item["final_status"] for item in dispositions)
    gaps = sorted(review["evidence_gaps"], key=lambda item: (item["priority"], item["gap_id"]))
    phase_status = review_report.get("phase_status", "IN_PROGRESS")
    evidence_units = [
        read_json(path)
        for path in sorted((REPOSITORY_ROOT / "research" / "evidence").rglob("*.scene-evidence.json"))
    ]
    return {
        "schema_version": "exhaustive-runtime-integration-validation/0.1",
        "status": "PASS" if not issues else "FAIL",
        "phase_status": phase_status if not issues else "IN_PROGRESS",
        "source_disposition_count": len(review["source_dispositions"]),
        "canonical_scene_evidence_count": len(review["evidence_reviews"]),
        "directly_auditioned_audio_scene_count": sum(
            item.get("audio_review_status") == "DIRECT_AUDITION_COMPLETE"
            for item in review["evidence_reviews"]
        ),
        "canonical_shot_edit_unit_count": sum(item["stats"]["shot_count"] for item in evidence_units),
        "candidate_disposition_count": len(dispositions),
        "candidate_final_status_counts": dict(sorted(final_counts.items())),
        "final_disposition_count": sum(item["final_status"] in FINAL_STATUSES for item in dispositions),
        "pending_evidence_gap_count": sum(item["final_status"] == "EVIDENCE_GAP_PENDING" for item in dispositions),
        "existing_material_review_required_count": sum(
            item["final_status"] == "EXISTING_MATERIAL_REVIEW_REQUIRED"
            for item in dispositions
        ),
        "mechanism_family_count": len(family_ids),
        "runtime_rule_count": len(grammar["rules"]),
        "positive_forward_case_count": forward_report.get("completed_positive_cases", 0),
        "boundary_forward_case_count": forward_report.get("completed_boundary_cases", 0),
        "no_applicable_rule_case_count": forward_report.get("no_applicable_rule_count", 0),
        "family_results": family_results,
        "prioritized_evidence_gaps": [
            {
                "priority": item["priority"],
                "gap_id": item["gap_id"],
                "candidate_count": len(item["candidate_rule_ids"]),
                "gap_scope": item["gap_scope"],
                "missing_evidence_type": item["missing_evidence_type"],
                "why_existing_material_cannot_close": item["why_existing_material_cannot_close"],
                "existing_review_refs": item["existing_review_refs"],
                "required_review": item["required_review"],
                "close_condition": item["close_condition"],
            }
            for item in gaps
        ],
        "error_count": len(issues),
        "issues": issues,
        "boundaries": [
            "A PASS report proves repository bindings and deterministic routing, not creative approval.",
            "All creative packages remain HUMAN_REVIEW_PENDING and do not authorize generation or publication.",
            "Semantic audio remains outside rules whose audio_dependency is false.",
            "IN_PROGRESS is mandatory while existing local material still requires direct review.",
            "PARTIAL_EVIDENCE_GAP is reserved for the state where only fixed-corpus evidence gaps remain.",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    protected_paths = [
        REVIEW_PATH,
        REVIEW_SCHEMA_PATH,
        CANDIDATE_INDEX_PATH,
        MATRIX_PATH,
        GRAMMAR_PATH,
        GRAMMAR_SCHEMA_PATH,
        FORWARD_INDEX_PATH,
        FORWARD_SCHEMA_PATH,
        *sorted(EVIDENCE_ROOT.rglob("*.scene-evidence.json")),
        *sorted(path for path in FORWARD_ROOT.rglob("*") if path.is_file()),
    ]
    if args.report.is_symlink() or any(
        _same_file_target(args.report, protected_path) for protected_path in protected_paths
    ):
        print("ERROR: --report must not overwrite or alias an input or schema file", file=sys.stderr)
        return 2
    if not args.check and args.report.exists() and args.report.resolve() != REPORT_PATH.resolve():
        print("ERROR: --report refuses to overwrite an existing noncanonical file", file=sys.stderr)
        return 2
    try:
        report = build_report()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.check:
        if not args.report.is_file() or args.report.read_text(encoding="utf-8") != rendered:
            return 1
    else:
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            _write_report_atomically(args.report, rendered)
        except OSError as exc:
            print(f"ERROR: report write failed: {exc}", file=sys.stderr)
            return 2
    sys.stdout.write(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
