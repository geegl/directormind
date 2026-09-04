#!/usr/bin/env python3
"""Build or check the deterministic final local generalization report."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
VALIDATION_ROOT = REPOSITORY_ROOT / "research" / "validation"
REPORT_PATH = VALIDATION_ROOT / "FINAL_GENERALIZATION_VALIDATION.json"
SCHEMA_PATH = SKILL_ROOT / "references" / "final-generalization-validation.schema.json"
TEST_ROOT = SKILL_ROOT / "tests"

LIVE_CHECK_NAMES = (
    "repository syntax, references and public boundaries",
    "canonical conversion determinism",
    "generated review determinism",
    "candidate index determinism",
    "runtime promotion review",
    "exhaustive runtime integration authority",
    "Scene Evidence validation",
    "candidate promotion gates",
    "runtime Grammar build determinism",
    "runtime Grammar validation",
    "routing-case validation",
    "forward-test build determinism",
    "forward-test repository",
    "exhaustive runtime integration report",
    "unit and CLI suite",
    "whitespace",
    "versioned report scene-evidence-validation.json",
    "versioned report runtime-rule-promotion-wave1-validation.json",
    "versioned report runtime-integration-validation.json",
    "versioned report candidate-rule-validation.json",
    "versioned report director-grammar-validation.json",
    "versioned report director-routing-validation.json",
    "versioned report forward-test-validation.json",
    "versioned report exhaustive-runtime-integration-validation.json",
)

sys.path.insert(0, str(SCRIPT_DIR))
from validate_repository_boundaries import validate_repository  # noqa: E402
from validate_scene_evidence import load_json, validate_schema_subset  # noqa: E402


def _load_report(name: str) -> dict[str, Any]:
    return load_json(VALIDATION_ROOT / name)


def _count_tests(suite: unittest.TestSuite) -> int:
    return sum(
        _count_tests(item) if isinstance(item, unittest.TestSuite) else 1
        for item in suite
    )


def _source_disposition_count() -> int:
    text = (VALIDATION_ROOT / "CLOSED_CORPUS_33_STATUS.md").read_text(encoding="utf-8")
    return len(re.findall(r"^\|\s*\d+\s*\|\s*(?:First|Post-16)\s*\|", text, re.MULTILINE))


def _evidence_errors(evidence: Mapping[str, Any] | None) -> list[str]:
    if not evidence or evidence.get("schema_version") != "local-check-evidence/0.1":
        return ["LIVE_CHECK_EVIDENCE_MISSING_OR_INVALID"]
    results = evidence.get("check_results")
    if not isinstance(results, Mapping):
        return ["LIVE_CHECK_RESULTS_MISSING"]
    errors = []
    for name in LIVE_CHECK_NAMES:
        if results.get(name) != "PASS":
            errors.append(f"LIVE_CHECK_NOT_PASSED: {name}")
    extra = sorted(set(results) - set(LIVE_CHECK_NAMES))
    if extra:
        errors.append("UNEXPECTED_LIVE_CHECK_RESULTS: " + ", ".join(extra))
    return errors


def _check_passed(evidence: Mapping[str, Any] | None, name: str) -> bool:
    if not evidence:
        return False
    results = evidence.get("check_results")
    return isinstance(results, Mapping) and results.get(name) == "PASS"


def _declared_not_performed() -> dict[str, str]:
    return {
        "status": "DECLARED_NOT_PERFORMED",
        "verification": "NOT_MACHINE_VERIFIED",
    }


def _live_pr_state_required() -> dict[str, str]:
    """Avoid self-attesting remote state from a versioned pre-CI artifact."""
    return {
        "status": "VERSIONED_REPORT_DOES_NOT_ATTEST",
        "verification": "VERIFY_LIVE_PR_STATE",
    }


def build_report(live_evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    scene = _load_report("scene-evidence-validation.json")
    wave1_promotion = _load_report("runtime-rule-promotion-wave1-validation.json")
    integration = _load_report("runtime-integration-validation.json")
    candidate = _load_report("candidate-rule-validation.json")
    grammar = _load_report("director-grammar-validation.json")
    routing = _load_report("director-routing-validation.json")
    forward = _load_report("forward-test-validation.json")
    exhaustive = _load_report("exhaustive-runtime-integration-validation.json")
    boundaries = validate_repository()
    suite = unittest.defaultTestLoader.discover(str(TEST_ROOT))
    unit_test_count = _count_tests(suite)
    integration_review = load_json(
        REPOSITORY_ROOT / "research" / "grammar" / "runtime_integration.review.json"
    )
    final_status_counts = exhaustive.get("candidate_final_status_counts", {})
    moving_image_reviewed_shots = len({
        shot_id
        for item in integration_review.get("evidence_reviews", [])
        for shot_id in item.get("moving_image_reviewed_shot_ids", [])
    })
    candidate_ids = [
        item["candidate_rule_id"]
        for item in load_json(REPOSITORY_ROOT / "research" / "grammar" / "candidate_rule_index.json")["candidates"]
    ]
    validation_errors = sum(
        report["error_count"]
        for report in (
            scene,
            wave1_promotion,
            integration,
            candidate,
            grammar,
            routing,
            forward,
            exhaustive,
        )
    )
    errors = _evidence_errors(live_evidence)
    expected_report_statuses = (
        ("SCENE_VALIDATION_NOT_PASSING", scene["status"] == "PASS_STRUCTURAL"),
        ("WAVE1_PROMOTION_REVIEW_NOT_PASSING", wave1_promotion["status"] == "PASS"),
        (
            "RUNTIME_INTEGRATION_AUTHORITY_NOT_PASSING",
            integration["status"] == "PASS"
            and integration["phase_status"]
            in {"IN_PROGRESS", "PARTIAL_EVIDENCE_GAP", "COMPLETE"}
            and integration["phase_status"] == exhaustive["phase_status"],
        ),
        ("CANDIDATE_VALIDATION_NOT_PASSING", candidate["status"] == "PASS"),
        ("GRAMMAR_VALIDATION_NOT_PASSING", grammar["status"] == "PASS"),
        ("ROUTING_VALIDATION_NOT_PASSING", routing["status"] == "PASS"),
        ("FORWARD_VALIDATION_NOT_PASSING", forward["status"] == "PASS"),
        (
            "EXHAUSTIVE_INTEGRATION_REPORT_NOT_PASSING",
            exhaustive["status"] == "PASS"
            and exhaustive["phase_status"] == integration["phase_status"],
        ),
        ("REPOSITORY_BOUNDARIES_NOT_PASSING", boundaries["status"] == "PASS"),
    )
    errors.extend(code for code, passed in expected_report_statuses if not passed)

    evidence_pass = lambda name: _check_passed(live_evidence, name)
    versioned_reports_pass = all(
        evidence_pass(name)
        for name in LIVE_CHECK_NAMES
        if name.startswith("versioned report ")
    )
    local_runner_pass = not errors

    return {
        "schema_version": "final-generalization-validation/0.5",
        "status": "PASS_LOCAL" if local_runner_pass else "FAIL_LOCAL",
        "phase_status": integration["phase_status"],
        "counts": {
            "source_dispositions": _source_disposition_count(),
            "canonical_scenes": scene["total_scenes"],
            "shot_edit_units": scene["total_shots"],
            "candidate_identities": candidate["candidate_count"],
            "candidate_families": candidate["family_count"],
            "reviewed_evidence_units": integration["evidence_review_count"],
            "directly_auditioned_semantic_audio_scenes": integration[
                "directly_auditioned_evidence_count"
            ],
            "moving_image_reviewed_shots": moving_image_reviewed_shots,
            "final_candidate_dispositions": integration["candidate_final_disposition_count"],
            "pending_evidence_gap_candidates": integration["pending_evidence_gap_count"],
            "existing_material_review_required_candidates": integration[
                "existing_material_review_required_count"
            ],
            "evidence_gaps": integration["evidence_gap_count"],
            "runtime_active_families": integration["runtime_active_family_count"],
            "evidence_final_mappings": integration["evidence_final_mapping_count"],
            "positive_runtime_candidates": final_status_counts.get("POSITIVE_RUNTIME_RULE", 0),
            "supporting_evidence_candidates": final_status_counts.get("SUPPORTING_EVIDENCE", 0),
            "boundary_candidates": final_status_counts.get("BOUNDARY_OR_COUNTEREXAMPLE", 0),
            "merged_duplicate_candidates": final_status_counts.get("MERGED_DUPLICATE", 0),
            "rejected_candidates": final_status_counts.get("REJECTED_WITH_REASON", 0),
            "duplicate_candidate_ids": len(candidate_ids) - len(set(candidate_ids)),
            "eligible_candidates": grammar["eligible_candidate_count"],
            "runtime_rules": grammar["runtime_rule_count"],
            "routing_cases": routing["case_count"],
            "routing_no_applicable_rule_cases": routing["no_applicable_rule_count"],
            "routing_selected_rules": routing["selected_rule_count"],
            "forward_packages": forward["package_count"],
            "required_scene_problems": forward["required_scene_problem_count"],
            "promotion_ready_families": forward["promotion_ready_family_count"],
            "forward_selected_rules": forward["selected_rule_count"],
            "human_review_pending_packages": forward["human_review_pending_count"],
            "scene_warnings": scene["warning_count"],
            "forward_warnings": forward["warning_count"],
            "validation_errors": validation_errors,
            "validation_warnings": scene["warning_count"] + forward["warning_count"],
            "unit_tests": unit_test_count,
            "broken_references": boundaries["broken_reference_count"],
            "prohibited_repository_files": boundaries["prohibited_repository_file_count"],
            "scoped_public_string_issues": boundaries["scoped_public_string_issue_count"],
            "excluded_historical_legacy_markdown": boundaries["excluded_historical_legacy_markdown_count"],
            "invalid_json_files": sum(item["code"] == "INVALID-JSON" for item in boundaries["issues"]),
            "invalid_python_files": sum(item["code"] == "INVALID-PYTHON" for item in boundaries["issues"]),
            "whitespace_errors": boundaries["whitespace_issue_count"],
            "symlink_escapes": boundaries["symlink_escape_count"],
        },
        "checks": {
            "json_syntax": "PASS" if evidence_pass("repository syntax, references and public boundaries") and not any(item["code"] == "INVALID-JSON" for item in boundaries["issues"]) else "FAIL",
            "python_compile": "PASS" if evidence_pass("repository syntax, references and public boundaries") and not any(item["code"] == "INVALID-PYTHON" for item in boundaries["issues"]) else "FAIL",
            "converter_determinism": "PASS" if evidence_pass("canonical conversion determinism") else "FAIL",
            "renderer_determinism": "PASS" if evidence_pass("generated review determinism") else "FAIL",
            "candidate_index_determinism": "PASS" if evidence_pass("candidate index determinism") else "FAIL",
            "wave1_promotion_review": "PASS" if evidence_pass("runtime promotion review") and wave1_promotion["status"] == "PASS" else "FAIL",
            "runtime_integration_authority": "PASS" if evidence_pass("exhaustive runtime integration authority") and integration["status"] == "PASS" else "FAIL",
            "scene_validation": "PASS_STRUCTURAL" if evidence_pass("Scene Evidence validation") and scene["status"] == "PASS_STRUCTURAL" else "FAIL",
            "candidate_validation": "PASS" if evidence_pass("candidate promotion gates") and candidate["status"] == "PASS" else "FAIL",
            "grammar_validation": "PASS" if evidence_pass("runtime Grammar validation") and grammar["status"] == "PASS" else "FAIL",
            "grammar_build_determinism": "PASS" if evidence_pass("runtime Grammar build determinism") else "FAIL",
            "routing_validation": "PASS" if evidence_pass("routing-case validation") and routing["status"] == "PASS" else "FAIL",
            "forward_build_determinism": "PASS" if evidence_pass("forward-test build determinism") else "FAIL",
            "forward_validation": "PASS" if evidence_pass("forward-test repository") and forward["status"] == "PASS" else "FAIL",
            "exhaustive_integration_report": "PASS" if evidence_pass("exhaustive runtime integration report") and exhaustive["status"] == "PASS" else "FAIL",
            "unit_suite": "PASS" if evidence_pass("unit and CLI suite") else "FAIL",
            "repository_boundaries": "PASS" if evidence_pass("repository syntax, references and public boundaries") and boundaries["status"] == "PASS" else "FAIL",
            "whitespace": "PASS" if evidence_pass("whitespace") and boundaries["whitespace_issue_count"] == 0 else "FAIL",
            "versioned_reports": "PASS" if versioned_reports_pass else "FAIL",
            "ci_workflow": "LOCAL_COMMAND_PASS_WORKFLOW_NOT_HOSTED" if local_runner_pass else "LOCAL_COMMAND_FAIL_WORKFLOW_NOT_HOSTED",
            "remote_ci": "POST_COMMIT_EXTERNAL_EVIDENCE_REQUIRED",
        },
        "verification_evidence": {
            "local_check_results": "LIVE_RUNNER_RESULTS" if live_evidence else "NOT_PROVIDED",
            "public_string_scan": boundaries["public_string_scan_scope"],
            "historical_legacy_markdown": boundaries["historical_legacy_markdown_scope"],
            "external_actions": "LIVE_PR_STATE_REQUIRED_FOR_REMOTE_ACTIONS",
        },
        "external_actions": {
            "pushed": _live_pr_state_required(),
            "pull_request_created": _live_pr_state_required(),
            "merged": _declared_not_performed(),
            "deployed": _declared_not_performed(),
            "published": _declared_not_performed(),
            "media_deleted": _declared_not_performed(),
        },
        "unverified_boundaries": [
            "SIXTY_NINE_CANDIDATES_REMAIN_FIXED_CORPUS_EVIDENCE_GAPS",
            "SOUND_SOURCE_CAUSALITY_SUBJECTIVITY_AND_SUBSECOND_OFFSETS_REMAIN_UNPROVED",
            "TWENTY_SIX_OF_THIRTY_ONE_EVIDENCE_UNITS_HAVE_FINAL_DECISION_MAPPINGS",
            "FIVE_OF_SIXTEEN_FAMILIES_ARE_NOT_YET_RUNTIME_PARTICIPATING",
            "ONLY_ONE_SCENE_HAS_DIRECT_SEMANTIC_AUDIO_AUDITION",
            "FORWARD_SELECTION_IS_STRUCTURAL_NOT_CREATIVE_APPROVAL",
            "CREATIVE_QUALITY_AND_AUDIENCE_EFFECT_NOT_PROVED",
            "REMOTE_CI_RESULT_IS_POST_COMMIT_EXTERNAL_EVIDENCE",
            "PULL_REQUEST_STATE_IS_POST_COMMIT_EXTERNAL_EVIDENCE",
            "ORIGINAL_30_IMMUTABLE_LEGACY_MARKDOWN_EXCLUDED_FROM_SCOPED_STRING_SCAN",
            "EXTERNAL_ACTION_DECLARATIONS_NOT_MACHINE_VERIFIED",
        ],
        "errors": errors,
    }


def _serialized(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def validate_report(report: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    schema = load_json(SCHEMA_PATH)
    validate_schema_subset(report, schema, schema, issues)
    return issues


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args(argv)
    live_evidence = load_json(args.evidence) if args.evidence else None
    report = build_report(live_evidence)
    issues = validate_report(report)
    if issues:
        for issue in issues:
            print(f"{issue['code']} {issue['path']}: {issue['message']}", file=sys.stderr)
        return 1
    if report["status"] != "PASS_LOCAL":
        for error in report["errors"]:
            print(error, file=sys.stderr)
        return 1
    expected = _serialized(report)
    if args.check:
        if not args.report.exists() or args.report.read_text(encoding="utf-8") != expected:
            print(f"DRIFT {args.report}", file=sys.stderr)
            return 1
        print("checked final local generalization validation report")
        return 0
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(expected, encoding="utf-8")
    print("built final local generalization validation report")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
