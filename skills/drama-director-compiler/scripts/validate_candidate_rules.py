#!/usr/bin/env python3
"""Validate candidate normalization, cross-work relations and promotion gates."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
EVIDENCE_ROOT = REPOSITORY_ROOT / "research" / "evidence"
INDEX_PATH = REPOSITORY_ROOT / "research" / "grammar" / "candidate_rule_index.json"
MATRIX_PATH = REPOSITORY_ROOT / "research" / "grammar" / "cross_work_support_matrix.json"
REPORT_PATH = REPOSITORY_ROOT / "research" / "validation" / "candidate-rule-validation.json"
SCHEMA_PATH = SKILL_ROOT / "references" / "candidate-director-rule.schema.json"
INTEGRATION_REVIEW_PATH = REPOSITORY_ROOT / "research" / "grammar" / "runtime_integration.review.json"

sys.path.insert(0, str(SCRIPT_DIR))
from build_candidate_rule_index import build_all, render_matrix  # noqa: E402
from validate_scene_evidence import validate_schema_subset  # noqa: E402


PROMOTION_STATES = {
    "SINGLE_WORK_CANDIDATE",
    "CROSS_WORK_SUPPORTED",
    "GENERAL_DEFAULT",
    "REJECTED",
    "BLOCKED_BY_UNKNOWN",
    "EVIDENCE_GAP_PENDING",
}
RELATIONS = {"SUPPORTS", "NARROWS", "CONTRADICTS", "COUNTEREXAMPLE", "DUPLICATE"}
CANDIDATE_KEYS = {
    "schema_version",
    "candidate_rule_id",
    "canonical_rule_family",
    "family_assignment_status",
    "relation_to_family",
    "source",
    "scene_problem",
    "functional_roles",
    "operational_contract",
    "confidence",
    "supporting_relations",
    "applicability_evidence",
    "unknown_dependencies",
    "counterexamples",
    "promotion",
    "runtime_integration",
    "rights_boundary",
    "legacy_lineage",
}


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def _issue(
    issues: list[dict[str, str]],
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append({"level": "error", "code": code, "path": path, "message": message})


def _source_candidates(
    evidence_paths: Iterable[Path] | None = None,
) -> dict[str, tuple[dict[str, Any], dict[str, Any]]]:
    paths = evidence_paths or sorted(EVIDENCE_ROOT.rglob("*.scene-evidence.json"))
    result: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for path in paths:
        evidence = _read_json(path)
        for rule in evidence["candidate_rules"]:
            rule_id = rule["candidate_rule_id"]
            if rule_id in result:
                raise ValueError(f"duplicate source candidate ID: {rule_id}")
            result[rule_id] = (evidence, rule)
    return result


def _id_sets(evidence: dict[str, Any]) -> tuple[set[str], set[str]]:
    known: set[str] = {evidence["evidence_id"], evidence["work_id"]}
    text_anchor_ids: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, str) and (
                    key.endswith("_id") or key in {"claim_id", "track_id"}
                ):
                    known.add(item)
                    if key == "text_anchor_id":
                        text_anchor_ids.add(item)
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(evidence)
    return known, text_anchor_ids


def _validate_source_refs(
    refs: Any,
    allowed: set[str],
    path: str,
    code: str,
    issues: list[dict[str, str]],
) -> bool:
    if not isinstance(refs, list) or not refs:
        _issue(issues, code, path, "Verified or inferred evidence requires non-empty source refs.")
        return False
    missing = sorted(ref for ref in refs if ref not in allowed)
    if missing:
        _issue(issues, code, path, f"Unknown source refs: {missing}.")
        return False
    return True


def _verified_review_ref(
    candidate_id: Any,
    record: dict[str, Any],
    record_id_key: str,
    path: str,
    issues: list[dict[str, str]],
) -> bool:
    if record.get("review_status") not in {"HUMAN_VERIFIED", "ROOT_VIDEO_VERIFIED"}:
        _issue(issues, "RELATION-REVIEW-MISSING", path, "Verified relation requires a named review record.")
        return False
    review_id = record.get("review_id")
    review_ref = record.get("review_ref")
    if not isinstance(review_id, str) or not review_id or not isinstance(review_ref, str):
        _issue(issues, "RELATION-REVIEW-MISSING", path, "Verified relation requires a review ID and source ref.")
        return False
    review_root = (REPOSITORY_ROOT / "research" / "validation" / "relation-reviews").resolve()
    resolved = (REPOSITORY_ROOT / review_ref).resolve()
    try:
        resolved.relative_to(review_root)
    except ValueError:
        _issue(issues, "RELATION-REVIEW-REF", path, "Relation review must remain inside research/validation/relation-reviews.")
        return False
    if not resolved.is_file() or resolved.suffix != ".json":
        _issue(issues, "RELATION-REVIEW-REF", path, "Relation review must be an existing JSON record.")
        return False
    try:
        review = _read_json(resolved)
    except (OSError, ValueError, json.JSONDecodeError):
        _issue(issues, "RELATION-REVIEW-REF", path, "Relation review JSON is invalid.")
        return False
    record_id = record.get(record_id_key)
    if len({review_id, candidate_id, record_id}) != 3:
        _issue(issues, "RELATION-REVIEW-ID-COLLISION", path, "Review, candidate and relation IDs must be distinct.")
        return False
    expected = {
        "schema_version": "candidate-relation-review/0.1",
        "review_id": review_id,
        "candidate_rule_id": candidate_id,
        "record_id": record_id,
        "status": record.get("review_status"),
        "relation": record.get("relation"),
        "same_trigger_status": record.get("same_trigger_status"),
        "source_candidate_rule_id": record.get("source_candidate_rule_id"),
        "work_id": record.get("work_id"),
        "evidence_id": record.get("evidence_id"),
        "source_refs": record.get("source_refs"),
    }
    if review != expected:
        _issue(issues, "RELATION-REVIEW-MISMATCH", path, "Relation review JSON does not exactly bind the declared record.")
        return False
    return True


def _validate_roles_problem_audio_boundary(
    candidate: dict[str, Any],
    evidence: dict[str, Any],
    path: str,
    issues: list[dict[str, str]],
) -> dict[str, bool]:
    known_refs, text_anchor_ids = _id_sets(evidence)
    problem = candidate.get("scene_problem", {})
    if len(problem.get("secondary", [])) > 2:
        _issue(issues, "SCENE-PROBLEM-SECONDARY-LIMIT", path, "At most two secondary scene problems are allowed.")
    if problem.get("status") == "UNKNOWN" and problem.get("source_refs"):
        _issue(issues, "SCENE-PROBLEM-UNKNOWN-REFS", path, "UNKNOWN scene problem must not claim proving source refs.")
    if problem.get("status") in {"TEXT_ANCHOR", "INFERRED"}:
        allowed = text_anchor_ids if problem.get("status") == "TEXT_ANCHOR" else known_refs
        _validate_source_refs(
            problem.get("source_refs"),
            allowed,
            f"{path}.scene_problem.source_refs",
            "SCENE-PROBLEM-PROVENANCE",
            issues,
        )
    for index, role in enumerate(candidate.get("functional_roles", [])):
        role_path = f"{path}.functional_roles[{index}]"
        if role.get("status") == "UNKNOWN" and role.get("functional_role") != "UNKNOWN":
            _issue(issues, "ROLE-UNKNOWN-HARDENED", role_path, "UNKNOWN role status cannot carry a functional role.")
        if role.get("status") == "UNKNOWN" and role.get("source_refs"):
            _issue(issues, "ROLE-UNKNOWN-REFS", role_path, "UNKNOWN functional role cannot claim proving refs.")
        if role.get("status") in {"TEXT_ANCHOR", "INFERRED"}:
            allowed = text_anchor_ids if role.get("status") == "TEXT_ANCHOR" else known_refs
            _validate_source_refs(
                role.get("source_refs"),
                allowed,
                f"{role_path}.source_refs",
                "ROLE-PROVENANCE-MISSING",
                issues,
            )

    contract = candidate.get("operational_contract", {})
    audio = contract.get("audio_logic", {})
    audio_dependency = contract.get("audio_dependency") is not False
    if audio.get("status") == "AUDIO_OBSERVED":
        if evidence.get("audio_evidence_status") != "AUDIO_OBSERVED":
            _issue(
                issues,
                "AUDIO-PROVENANCE-STATUS",
                f"{path}.operational_contract.audio_logic.status",
                "Candidate audio cannot be observed when its source scene was not directly auditioned.",
            )
        _validate_source_refs(
            audio.get("source_refs"),
            known_refs,
            f"{path}.operational_contract.audio_logic.source_refs",
            "AUDIO-PROVENANCE-REFS",
            issues,
        )
    elif audio.get("status") == "UNKNOWN" and audio.get("source_refs"):
        _issue(
            issues,
            "AUDIO-UNKNOWN-REFS",
            f"{path}.operational_contract.audio_logic.source_refs",
            "UNKNOWN audio cannot claim proving refs.",
        )

    boundary = candidate.get("applicability_evidence", {})
    if boundary.get("status") == "VERIFIED":
        definite_boundary_statuses = {
            "NATURAL_START_END_VERIFIED",
            "START_INTERNAL_END_VERIFIED",
            "START_VERIFIED_END_INTERNAL",
            "BOTH_INTERNAL_SELECTED",
        }
        if (
            evidence.get("boundary_status") not in definite_boundary_statuses
            or evidence.get("boundary_evidence", {}).get("status") != "PICTURE_OBSERVED"
        ):
            _issue(
                issues,
                "NATURAL-BOUNDARY-PROVENANCE",
                f"{path}.applicability_evidence.status",
                "Applicability evidence requires a picture-observed definite source interval boundary.",
            )
        _validate_source_refs(
            boundary.get("source_refs"),
            known_refs,
            f"{path}.applicability_evidence.source_refs",
            "NATURAL-BOUNDARY-PROVENANCE",
            issues,
        )
    elif boundary.get("status") == "UNKNOWN" and boundary.get("source_refs"):
        _issue(
            issues,
            "NATURAL-BOUNDARY-UNKNOWN-REFS",
            f"{path}.applicability_evidence.source_refs",
            "UNKNOWN applicability boundary cannot claim proving refs.",
        )

    return {
        "scene_problem": problem.get("status") == "UNKNOWN",
        "audio": audio_dependency and audio.get("status") != "AUDIO_OBSERVED",
        "functional_roles": not candidate.get("functional_roles")
        or any(role.get("status") == "UNKNOWN" for role in candidate.get("functional_roles", [])),
        "natural_scene_boundary": boundary.get("status") != "VERIFIED",
    }


def _verified_relations(
    candidate: dict[str, Any],
    source: dict[str, tuple[dict[str, Any], dict[str, Any]]],
    normalized: dict[str, dict[str, Any]],
    path: str,
    issues: list[dict[str, str]],
) -> tuple[set[str], int]:
    source_work = candidate.get("source", {}).get("work_id")
    support_work_ids = {source_work} if isinstance(source_work, str) else set()
    seen_relation_ids: set[str] = set()
    for index, relation in enumerate(candidate.get("supporting_relations", [])):
        relation_path = f"{path}.supporting_relations[{index}]"
        relation_id = relation.get("relation_id")
        if relation_id in seen_relation_ids:
            _issue(issues, "SUPPORT-RELATION-DUPLICATE", relation_path, "Relation ID must be unique per candidate.")
        if isinstance(relation_id, str):
            seen_relation_ids.add(relation_id)
        if relation.get("status") != "VERIFIED":
            continue
        target_id = relation.get("source_candidate_rule_id")
        target = source.get(target_id)
        target_normalized = normalized.get(target_id)
        if target is None or target_normalized is None:
            _issue(issues, "SUPPORT-SOURCE-MISSING", relation_path, "Verified support must resolve to a source candidate.")
            continue
        target_evidence, _target_rule = target
        known_refs, _text_refs = _id_sets(target_evidence)
        exact = (
            relation.get("relation") == "SUPPORTS"
            and relation.get("same_trigger_status") == "VERIFIED_SAME_TRIGGER"
            and relation.get("work_id") == target_evidence["work_id"]
            and relation.get("evidence_id") == target_evidence["evidence_id"]
            and target_evidence["work_id"] != source_work
            and target_normalized.get("canonical_rule_family")
            == candidate.get("canonical_rule_family")
            and _verified_review_ref(
                candidate.get("candidate_rule_id"),
                relation,
                "relation_id",
                relation_path,
                issues,
            )
            and _validate_source_refs(
                relation.get("source_refs"),
                known_refs,
                f"{relation_path}.source_refs",
                "SUPPORT-PROVENANCE",
                issues,
            )
        )
        if not exact:
            _issue(
                issues,
                "SUPPORT-NOT-VERIFIED-SAME-TRIGGER",
                relation_path,
                "Verified support must be a cited same-trigger SUPPORTS relation from another work.",
            )
            continue
        support_work_ids.add(target_evidence["work_id"])

    verified_counterexamples = 0
    for index, counterexample in enumerate(candidate.get("counterexamples", [])):
        counter_path = f"{path}.counterexamples[{index}]"
        if counterexample.get("status") != "VERIFIED":
            continue
        target_id = counterexample.get("source_candidate_rule_id")
        target = source.get(target_id)
        target_normalized = normalized.get(target_id)
        if target is None or target_normalized is None:
            _issue(issues, "COUNTEREXAMPLE-SOURCE-MISSING", counter_path, "Verified counterexample must resolve to a source candidate.")
            continue
        target_evidence, _target_rule = target
        known_refs, _text_refs = _id_sets(target_evidence)
        exact = (
            bool(counterexample.get("counterexample_id"))
            and counterexample.get("same_trigger_status") == "VERIFIED_SAME_TRIGGER"
            and counterexample.get("relation") in {"CONTRADICTS", "COUNTEREXAMPLE", "NARROWS"}
            and counterexample.get("work_id") == target_evidence["work_id"]
            and counterexample.get("evidence_id") == target_evidence["evidence_id"]
            and target_evidence["work_id"] != source_work
            and target_normalized.get("canonical_rule_family")
            == candidate.get("canonical_rule_family")
            and _verified_review_ref(
                candidate.get("candidate_rule_id"),
                counterexample,
                "counterexample_id",
                counter_path,
                issues,
            )
            and _validate_source_refs(
                counterexample.get("source_refs"),
                known_refs,
                f"{counter_path}.source_refs",
                "COUNTEREXAMPLE-PROVENANCE",
                issues,
            )
        )
        if not exact:
            _issue(
                issues,
                "COUNTEREXAMPLE-NOT-VERIFIED-SAME-TRIGGER",
                counter_path,
                "Verified counterexample must be cited, same-trigger and from another work.",
            )
            continue
        verified_counterexamples += 1
    return support_work_ids, verified_counterexamples


def _verified_forward_tests(
    candidate: dict[str, Any],
    path: str,
    issues: list[dict[str, str]],
) -> int:
    count = 0
    seen: set[str] = set()
    seen_refs: set[str] = set()
    promotion_review = _read_json(INTEGRATION_REVIEW_PATH)
    promotion = next(
        (
            item
            for item in promotion_review.get("runtime_rule_specs", [])
            if item.get("candidate_rule_id") == candidate.get("candidate_rule_id")
        ),
        None,
    )
    verified_modes: set[str] = set()
    for index, test in enumerate(candidate.get("promotion", {}).get("original_forward_tests", [])):
        test_path = f"{path}.promotion.original_forward_tests[{index}]"
        case_id = test.get("test_case_id")
        if case_id in seen:
            _issue(issues, "FORWARD-TEST-DUPLICATE", test_path, "Forward-test case ID must be unique.")
            continue
        if isinstance(case_id, str):
            seen.add(case_id)
        if test.get("status") != "PASS":
            continue
        source_ref = test.get("source_ref")
        if not isinstance(source_ref, str):
            _issue(issues, "FORWARD-TEST-REF", test_path, "Passing forward test must cite its repository package.")
            continue
        if source_ref in seen_refs:
            _issue(issues, "FORWARD-TEST-DUPLICATE-REF", test_path, "Each passing forward test must cite a distinct package.")
            continue
        seen_refs.add(source_ref)
        package_root = (REPOSITORY_ROOT / "examples" / "forward-tests").resolve()
        resolved = (REPOSITORY_ROOT / source_ref).resolve()
        try:
            relative = resolved.relative_to(package_root)
        except ValueError:
            _issue(issues, "FORWARD-TEST-REF", test_path, "Forward-test package must remain inside examples/forward-tests.")
            continue
        if relative == Path(".") or not resolved.is_dir():
            _issue(issues, "FORWARD-TEST-REF", test_path, "Passing forward-test ref must be a case directory.")
            continue
        manifest_path = (resolved / "manifest.json").resolve()
        try:
            manifest_path.relative_to(resolved)
        except ValueError:
            _issue(issues, "FORWARD-TEST-MANIFEST", test_path, "Forward-test manifest escapes its case directory.")
            continue
        if not manifest_path.is_file():
            _issue(issues, "FORWARD-TEST-MANIFEST", test_path, "Passing forward-test package lacks manifest.json.")
            continue
        try:
            manifest = _read_json(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError):
            _issue(issues, "FORWARD-TEST-MANIFEST", test_path, "Forward-test manifest JSON is invalid.")
            continue
        if promotion is None:
            _issue(issues, "FORWARD-TEST-PROMOTION-REVIEW", test_path, "Passing forward test lacks a canonical promotion review.")
            continue
        expected_mode = (
            "POSITIVE"
            if case_id == promotion["positive_forward_test_id"]
            else "BOUNDARY_OR_NON_APPLICABLE"
            if case_id == promotion["boundary_forward_test_id"]
            else None
        )
        expected_manifest = {
            "schema_version": "forward-test-result/0.1",
            "test_case_id": case_id,
            "candidate_rule_id": candidate.get("candidate_rule_id"),
            "canonical_rule_family": candidate.get("canonical_rule_family"),
            "rule_id": promotion["rule_id"],
            "test_mode": expected_mode,
            # The package can pass its structural routing assertion while the
            # creative result remains intentionally unapproved.
            "status": "HUMAN_REVIEW_PENDING",
        }
        if expected_mode is None or manifest != expected_manifest or case_id == candidate.get("candidate_rule_id"):
            _issue(issues, "FORWARD-TEST-MANIFEST", test_path, "Forward-test manifest does not exactly bind the case and candidate.")
            continue
        verified_modes.add(expected_mode)
        count += 1
    if candidate.get("promotion", {}).get("status") == "CROSS_WORK_SUPPORTED" and verified_modes != {"POSITIVE", "BOUNDARY_OR_NON_APPLICABLE"}:
        _issue(issues, "FORWARD-TEST-PAIR", path, "Cross-work promotion requires one distinct positive and one distinct boundary package.")
    return count


def _human_review_approved(candidate: dict[str, Any], path: str, issues: list[dict[str, str]]) -> bool:
    review = candidate.get("promotion", {}).get("human_director_review", {})
    if review.get("status") != "APPROVED":
        return False
    review_id = review.get("review_id")
    source_ref = review.get("source_ref")
    if not isinstance(review_id, str) or not review_id or not isinstance(source_ref, str):
        _issue(issues, "HUMAN-REVIEW-REF", path, "Approved human review requires an ID and repository source ref.")
        return False
    review_root = (REPOSITORY_ROOT / "research" / "validation" / "director-reviews").resolve()
    resolved = (REPOSITORY_ROOT / source_ref).resolve()
    try:
        resolved.relative_to(review_root)
    except ValueError:
        _issue(issues, "HUMAN-REVIEW-REF", path, "Human review must remain inside research/validation/director-reviews.")
        return False
    if not resolved.is_file() or resolved.suffix != ".json":
        _issue(issues, "HUMAN-REVIEW-REF", path, "Human review must be an existing JSON record.")
        return False
    try:
        review_record = _read_json(resolved)
    except (OSError, ValueError, json.JSONDecodeError):
        _issue(issues, "HUMAN-REVIEW-REF", path, "Human-review JSON is invalid.")
        return False
    if review_id == candidate.get("candidate_rule_id"):
        _issue(issues, "HUMAN-REVIEW-ID-COLLISION", path, "Review and candidate IDs must be distinct.")
        return False
    expected_review = {
        "schema_version": "director-review/0.1",
        "review_id": review_id,
        "candidate_rule_id": candidate.get("candidate_rule_id"),
        "status": "APPROVED",
    }
    if review_record != expected_review:
        _issue(issues, "HUMAN-REVIEW-MISMATCH", path, "Human-review JSON does not exactly bind the candidate and approval.")
        return False
    return True


def _validate_promotion(
    candidate: dict[str, Any],
    source: dict[str, tuple[dict[str, Any], dict[str, Any]]],
    normalized: dict[str, dict[str, Any]],
    expected_dependencies: dict[str, bool],
    path: str,
    issues: list[dict[str, str]],
) -> None:
    promotion = candidate.get("promotion", {})
    status = promotion.get("status")
    if status not in PROMOTION_STATES:
        _issue(issues, "PROMOTION-STATUS", path, f"Unsupported promotion status: {status!r}.")
        return
    unknown = promotion.get("unknown_dependency_present") is True
    support_work_ids, actual_counterexamples = _verified_relations(
        candidate, source, normalized, path, issues
    )
    actual_works = len(support_work_ids)
    actual_forward_tests = _verified_forward_tests(candidate, path, issues)
    approved = _human_review_approved(candidate, path, issues)
    integration_status = candidate.get("runtime_integration", {}).get("final_status")
    nonpositive_final = integration_status in {
        "SUPPORTING_EVIDENCE",
        "BOUNDARY_OR_COUNTEREXAMPLE",
        "MERGED_DUPLICATE",
        "REJECTED_WITH_REASON",
    }
    if promotion.get("verified_support_work_count") != actual_works:
        _issue(issues, "PROMOTION-WORK-COUNT", path, "Declared support-work count does not match cited verified support relations.")
    if promotion.get("verified_same_trigger_counterexample_count") != actual_counterexamples:
        _issue(
            issues,
            "PROMOTION-COUNTEREXAMPLE-COUNT",
            path,
            "Only identified, verified same-trigger counterexamples may count toward promotion.",
        )
    if promotion.get("original_forward_test_count") != actual_forward_tests:
        _issue(
            issues,
            "PROMOTION-FORWARD-TEST-COUNT",
            path,
            "Declared forward-test count does not match cited passing packages.",
        )
    dependencies = candidate.get("unknown_dependencies", {})
    confidence = candidate.get("confidence", {})
    if dependencies != expected_dependencies:
        _issue(
            issues,
            "PROMOTION-UNKNOWN-DEPENDENCY-DRIFT",
            path,
            "UNKNOWN dependency flags must be derived from the candidate evidence contract.",
        )
    actual_unknown = any(expected_dependencies.values()) or any(
        confidence.get(axis) == "UNKNOWN"
        for axis in ("within_source", "transfer", "execution")
    )
    if unknown != actual_unknown:
        _issue(
            issues,
            "PROMOTION-UNKNOWN-FLAG-DRIFT",
            path,
            "Promotion UNKNOWN flag must match the candidate's actual dependencies.",
        )
    pending_states = {"BLOCKED_BY_UNKNOWN", "EVIDENCE_GAP_PENDING"}
    if unknown and status not in pending_states and not nonpositive_final:
        _issue(issues, "PROMOTION-UNKNOWN-LEAK", path, "UNKNOWN-dependent positive candidate must remain pending.")
    if status not in pending_states and not nonpositive_final:
        dependency_codes = {
            "audio": "PROMOTION-AUDIO-UNKNOWN",
            "functional_roles": "PROMOTION-ROLE-UNKNOWN",
            "natural_scene_boundary": "PROMOTION-NATURAL-BOUNDARY-UNKNOWN",
        }
        for key, code in dependency_codes.items():
            if expected_dependencies[key]:
                _issue(issues, code, path, f"UNKNOWN {key.replace('_', ' ')} blocks promotion.")
    if candidate.get("scene_problem", {}).get("status") == "UNKNOWN" and status not in pending_states and not nonpositive_final:
        _issue(issues, "PROMOTION-SCENE-PROBLEM-UNKNOWN", path, "UNKNOWN scene problem cannot be promoted.")
    if any(confidence.get(axis) == "UNKNOWN" for axis in ("within_source", "transfer", "execution")):
        if status not in pending_states and not nonpositive_final:
            _issue(issues, "PROMOTION-CONFIDENCE-UNKNOWN", path, "UNKNOWN confidence dimension blocks promotion.")
    if status == "SINGLE_WORK_CANDIDATE" and actual_works != 1 and not nonpositive_final:
        _issue(issues, "PROMOTION-SINGLE-WORK", path, "SINGLE_WORK_CANDIDATE must have exactly one verified support work.")
    if status == "CROSS_WORK_SUPPORTED":
        if actual_works < 2 or actual_counterexamples < 1 or actual_unknown:
            _issue(issues, "PROMOTION-CROSS-WORK-GATE", path, "Cross-work promotion gates are incomplete.")
    if status == "GENERAL_DEFAULT":
        if actual_works < 3 or actual_counterexamples < 1 or actual_forward_tests < 2 or not approved or actual_unknown:
            _issue(issues, "PROMOTION-GENERAL-GATE", path, "General-default promotion gates are incomplete.")
    authorized = candidate.get("rights_boundary", {}).get("runtime_authorized")
    if bool(authorized) != (status in {"CROSS_WORK_SUPPORTED", "GENERAL_DEFAULT"}):
        _issue(issues, "PROMOTION-RUNTIME-AUTH", path, "Runtime authorization must exactly match eligible promotion states.")


def validate_repository(
    index: dict[str, Any],
    matrix: dict[str, Any],
    evidence_paths: Iterable[Path] | None = None,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    schema = _read_json(SCHEMA_PATH)
    source = _source_candidates(evidence_paths)
    candidates = index.get("candidates", [])
    normalized = {
        candidate.get("candidate_rule_id"): candidate
        for candidate in candidates
        if isinstance(candidate, dict) and isinstance(candidate.get("candidate_rule_id"), str)
    }
    candidate_ids = [candidate.get("candidate_rule_id") for candidate in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        _issue(issues, "INDEX-DUPLICATE-ID", "candidates", "Candidate IDs must be unique.")
    if set(candidate_ids) != set(source):
        missing = sorted(set(source) - set(candidate_ids))
        extra = sorted(set(candidate_ids) - set(source))
        _issue(issues, "INDEX-SOURCE-COVERAGE", "candidates", f"Missing={missing}; extra={extra}.")
    if index.get("source_candidate_count") != len(candidates):
        _issue(issues, "INDEX-COUNT", "source_candidate_count", "Candidate count does not match the array.")

    families = {family["family_id"]: family for family in index.get("families", [])}
    membership: Counter[str] = Counter()
    for family in families.values():
        for candidate_id in family.get("member_candidate_ids", []):
            membership[candidate_id] += 1
    for candidate_id in candidate_ids:
        if membership[candidate_id] != 1:
            _issue(issues, "INDEX-FAMILY-MEMBERSHIP", candidate_id, "Each candidate must belong to exactly one family.")

    for ordinal, candidate in enumerate(candidates):
        path = f"candidates[{ordinal}]"
        schema_issues: list[dict[str, str]] = []
        validate_schema_subset(candidate, schema, schema, schema_issues, path)
        issues.extend(schema_issues)
        if any(issue["code"].startswith("SCHEMA-") for issue in schema_issues):
            continue
        if set(candidate) != CANDIDATE_KEYS:
            _issue(issues, "CANDIDATE-FIELDS", path, "Candidate fields do not match the v0.1 contract.")
        if candidate.get("schema_version") != "candidate-director-rule/0.1":
            _issue(issues, "CANDIDATE-VERSION", path, "Candidate schema version is invalid.")
        if candidate.get("relation_to_family") not in RELATIONS:
            _issue(issues, "CANDIDATE-RELATION", path, "Family relation is invalid.")
        family_id = candidate.get("canonical_rule_family")
        if family_id not in families:
            _issue(issues, "CANDIDATE-FAMILY-MISSING", path, "Canonical family does not exist.")
            continue
        source_pair = source.get(candidate.get("candidate_rule_id"))
        if source_pair:
            evidence, source_rule = source_pair
            expected_source = {
                "work_id": evidence["work_id"],
                "evidence_id": evidence["evidence_id"],
                "source_candidate_rule_id": source_rule["candidate_rule_id"],
                "source_method_ids": source_rule["source_method_ids"],
                "evidence_shot_ids": source_rule["evidence_shot_ids"],
            }
            if candidate.get("source") != expected_source:
                _issue(issues, "CANDIDATE-SOURCE-DRIFT", path, "Source lineage does not match canonical Scene Evidence.")
            if candidate.get("legacy_lineage") != source_rule["legacy_migration"]:
                _issue(issues, "CANDIDATE-LEGACY-DRIFT", path, "Legacy lineage is not field-for-field preserved.")
            expected_dependencies = _validate_roles_problem_audio_boundary(
                candidate, evidence, path, issues
            )
            _validate_promotion(
                candidate, source, normalized, expected_dependencies, path, issues
            )

    matrix_families = {family["family_id"]: family for family in matrix.get("families", [])}
    if set(matrix_families) != set(families):
        _issue(issues, "MATRIX-FAMILY-COVERAGE", "families", "Matrix and index family IDs differ.")
    if matrix.get("candidate_count") != len(candidates):
        _issue(issues, "MATRIX-CANDIDATE-COUNT", "candidate_count", "Matrix candidate count is wrong.")
    for family_id, family in families.items():
        row = matrix_families.get(family_id)
        if not row:
            continue
        if row.get("member_count") != len(family["member_candidate_ids"]):
            _issue(issues, "MATRIX-MEMBER-COUNT", family_id, "Matrix member count is wrong.")
        if row.get("grouped_work_count") != len(set(family.get("work_ids", []))):
            _issue(issues, "MATRIX-GROUPED-WORK-COUNT", family_id, "Grouped-work count is wrong.")
        if row.get("promotion_eligibility") == "CROSS_WORK_SUPPORTED":
            if not row.get("verified_unrelated_same_trigger_counterexample_ids"):
                _issue(issues, "MATRIX-COUNTEREXAMPLE-GATE", family_id, "Eligible family lacks a verified same-trigger contrary case.")

    expected_index, expected_matrix, expected_markdown = build_all()
    if index != expected_index:
        _issue(issues, "INDEX-NONDETERMINISTIC", "index", "Checked index differs from deterministic builder output.")
    if matrix != expected_matrix:
        _issue(issues, "MATRIX-NONDETERMINISTIC", "matrix", "Checked matrix differs from deterministic builder output.")
    matrix_md_path = MATRIX_PATH.with_suffix(".md")
    if not matrix_md_path.exists() or matrix_md_path.read_text(encoding="utf-8") != expected_markdown:
        _issue(issues, "MATRIX-MARKDOWN-DRIFT", str(matrix_md_path), "Matrix Markdown differs from JSON rendering.")

    errors = [issue for issue in issues if issue["level"] == "error"]
    status_counts = Counter(
        candidate.get("promotion", {}).get("status", "MISSING") for candidate in candidates
    )
    return {
        "schema_version": "candidate-rule-validation/0.1",
        "status": "PASS" if not errors else "FAIL",
        "candidate_count": len(candidates),
        "family_count": len(families),
        "promotion_status_counts": dict(sorted(status_counts.items())),
        "runtime_authorized_count": sum(
            bool(candidate.get("rights_boundary", {}).get("runtime_authorized"))
            for candidate in candidates
        ),
        "error_count": len(errors),
        "issues": issues,
        "boundaries": [
            "Textual family clustering is not promotion evidence.",
            "Runtime-eligible visual rules require fresh picture review; semantic audio remains outside rules with audio_dependency=false.",
            "Every candidate not explicitly promoted remains blocked by its unresolved dependencies.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=INDEX_PATH)
    parser.add_argument("--matrix", type=Path, default=MATRIX_PATH)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--quiet", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _read_json(SCHEMA_PATH)
        index = _read_json(args.index)
        matrix = _read_json(args.matrix)
        report = validate_repository(index, matrix)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    if not args.quiet:
        print(
            f"{report['status']}: {report['candidate_count']} candidates, "
            f"{report['family_count']} families, {report['error_count']} errors"
        )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
