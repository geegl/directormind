#!/usr/bin/env python3
"""Validate the single canonical exhaustive runtime-integration authority."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
REVIEW_PATH = REPOSITORY_ROOT / "research" / "grammar" / "runtime_integration.review.json"
SCHEMA_PATH = SKILL_ROOT / "references" / "runtime-integration-review.schema.json"
EVIDENCE_ROOT = REPOSITORY_ROOT / "research" / "evidence"
SOURCE_REGISTER_PATH = REPOSITORY_ROOT / "research" / "validation" / "CLOSED_CORPUS_33_STATUS.md"
REPORT_PATH = REPOSITORY_ROOT / "research" / "validation" / "runtime-integration-validation.json"
FORWARD_INDEX_PATH = REPOSITORY_ROOT / "examples" / "forward-tests" / "index.json"

sys.path.insert(0, str(SCRIPT_DIR))
from build_candidate_rule_index import classify_family  # noqa: E402
from validate_scene_evidence import (  # noqa: E402
    _same_file_target,
    _write_report_atomically,
    validate_schema_subset,
)


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


def _evidence_authority() -> tuple[dict[str, dict[str, Any]], dict[str, tuple[dict[str, Any], dict[str, Any], str]]]:
    evidence_by_id: dict[str, dict[str, Any]] = {}
    candidate_by_id: dict[str, tuple[dict[str, Any], dict[str, Any], str]] = {}
    for path in sorted(EVIDENCE_ROOT.rglob("*.scene-evidence.json")):
        evidence = read_json(path)
        evidence_by_id[evidence["evidence_id"]] = evidence
        for candidate in evidence.get("candidate_rules", []):
            family_id, _assignment = classify_family(candidate)
            candidate_by_id[candidate["candidate_rule_id"]] = (evidence, candidate, family_id)
    return evidence_by_id, candidate_by_id


def _unique(values: list[Any]) -> bool:
    return len(values) == len(set(values))


def _registered_evidence_by_number() -> dict[int, str | None]:
    rows: dict[int, str | None] = {}
    for line in SOURCE_REGISTER_PATH.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*(\d+)\s*\|", line)
        if not match:
            continue
        number = int(match.group(1))
        if not 1 <= number <= 33:
            continue
        evidence = re.search(r"`([A-Z0-9][A-Z0-9._-]+)`\s*/\s*CURRENT_LOCAL_EVIDENCE", line)
        rows[number] = evidence.group(1) if evidence else None
    return rows


def validate(review: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    validate_schema_subset(review, schema, schema, issues, "$")
    evidence_by_id, candidate_by_id = _evidence_authority()
    forward_index = read_json(FORWARD_INDEX_PATH)
    forward_by_id = {
        item.get("test_case_id"): item
        for item in forward_index.get("cases", [])
        if isinstance(item, dict)
    }
    authority_candidate_ids = set(candidate_by_id)
    authority_evidence_ids = set(evidence_by_id)
    authority_family_ids = {item[2] for item in candidate_by_id.values()}

    source_rows = review.get("source_dispositions", [])
    source_numbers = [item.get("source_number") for item in source_rows if isinstance(item, dict)]
    if not _unique(source_numbers) or set(source_numbers) != set(range(1, 34)):
        add_issue(issues, "INTEGRATION-SOURCE-SET", "source_dispositions", "Source dispositions must cover rows 1 through 33 exactly once.")
    registered_evidence = _registered_evidence_by_number()
    if set(registered_evidence) != set(range(1, 34)):
        add_issue(issues, "INTEGRATION-SOURCE-REGISTER", "source_dispositions", "The canonical source register must expose rows 1 through 33 exactly once.")
    for index, item in enumerate(source_rows):
        if not isinstance(item, dict):
            continue
        number = item.get("source_number")
        if registered_evidence.get(number) != item.get("evidence_id"):
            add_issue(
                issues,
                "INTEGRATION-SOURCE-REGISTER-BINDING",
                f"source_dispositions[{index}]",
                "Source disposition evidence must exactly match the same numbered canonical register row.",
            )
    mapped_source_evidence = {
        item.get("evidence_id") for item in source_rows
        if isinstance(item, dict) and item.get("status") == "EVIDENCE_MAPPED"
    }
    if mapped_source_evidence != authority_evidence_ids:
        add_issue(issues, "INTEGRATION-SOURCE-EVIDENCE-SET", "source_dispositions", "Mapped source evidence must equal the 31 canonical evidence IDs.")
    for index, item in enumerate(source_rows):
        if not isinstance(item, dict):
            continue
        path = f"source_dispositions[{index}]"
        status = item.get("status")
        if status == "EVIDENCE_MAPPED" and item.get("evidence_id") not in authority_evidence_ids:
            add_issue(issues, "INTEGRATION-SOURCE-EVIDENCE", path, "Mapped source must name canonical evidence.")
        if status == "REJECTED_WITH_REASON" and not item.get("reason_code"):
            add_issue(issues, "INTEGRATION-SOURCE-REJECTION", path, "Rejected source needs a stable reason code.")
        if status == "EVIDENCE_GAP_PENDING" and review.get("declared_phase_status") == "COMPLETE":
            add_issue(issues, "INTEGRATION-SOURCE-GAP", path, "A complete phase cannot retain a source evidence gap.")

    evidence_reviews = review.get("evidence_reviews", [])
    review_ids = [item.get("review_id") for item in evidence_reviews if isinstance(item, dict)]
    reviewed_evidence_ids = [item.get("evidence_id") for item in evidence_reviews if isinstance(item, dict)]
    if not _unique(review_ids) or not _unique(reviewed_evidence_ids):
        add_issue(issues, "INTEGRATION-REVIEW-ID", "evidence_reviews", "Review and evidence IDs must be unique.")
    if set(reviewed_evidence_ids) != authority_evidence_ids:
        add_issue(issues, "INTEGRATION-EVIDENCE-SET", "evidence_reviews", "Evidence reviews must cover all 31 canonical evidence IDs exactly once.")
    review_by_id = {item.get("review_id"): item for item in evidence_reviews if isinstance(item, dict)}
    review_by_evidence = {item.get("evidence_id"): item for item in evidence_reviews if isinstance(item, dict)}
    reviewed_shots_by_review: dict[str, set[str]] = {}
    moving_shots_by_review: dict[str, set[str]] = {}
    for index, item in enumerate(evidence_reviews):
        if not isinstance(item, dict):
            continue
        path = f"evidence_reviews[{index}]"
        evidence = evidence_by_id.get(item.get("evidence_id"))
        if evidence is None:
            add_issue(issues, "INTEGRATION-EVIDENCE", path, "Review references unknown evidence.")
            continue
        shot_by_id = {shot.get("shot_id"): shot for shot in evidence.get("shots", []) if isinstance(shot, dict)}
        reviewed = item.get("reviewed_shots", [])
        shot_ids = [shot.get("shot_id") for shot in reviewed if isinstance(shot, dict)]
        reviewed_shots_by_review[item.get("review_id")] = set(shot_ids)
        moving_shot_ids = item.get("moving_image_reviewed_shot_ids", [])
        moving_shots_by_review[item.get("review_id")] = set(moving_shot_ids)
        if not _unique(shot_ids):
            add_issue(issues, "INTEGRATION-REVIEW-SHOT-DUPLICATE", path, "Reviewed Shot IDs must be unique.")
        if not _unique(moving_shot_ids) or not set(moving_shot_ids).issubset(set(shot_ids)):
            add_issue(
                issues,
                "INTEGRATION-MOVING-REVIEW-SHOT",
                f"{path}.moving_image_reviewed_shot_ids",
                "Moving-image reviewed Shot IDs must be unique and belong to this exact evidence review.",
            )
        for shot_index, reviewed_shot in enumerate(reviewed):
            if not isinstance(reviewed_shot, dict):
                continue
            source_shot = shot_by_id.get(reviewed_shot.get("shot_id"))
            if source_shot is None:
                add_issue(issues, "INTEGRATION-REVIEW-SHOT", f"{path}.reviewed_shots[{shot_index}]", "Reviewed Shot does not exist in the evidence record.")
                continue
            if reviewed_shot.get("start") != source_shot.get("start") or reviewed_shot.get("end") != source_shot.get("end"):
                add_issue(issues, "INTEGRATION-REVIEW-TIMECODE", f"{path}.reviewed_shots[{shot_index}]", "Reviewed Shot timecodes must exactly match canonical Shot bounds.")

    dispositions = review.get("candidate_dispositions", [])
    disposition_ids = [item.get("candidate_rule_id") for item in dispositions if isinstance(item, dict)]
    if not _unique(disposition_ids) or set(disposition_ids) != authority_candidate_ids:
        add_issue(issues, "INTEGRATION-CANDIDATE-SET", "candidate_dispositions", "Candidate dispositions must cover the canonical 124 IDs exactly once.")
    disposition_by_id = {item.get("candidate_rule_id"): item for item in dispositions if isinstance(item, dict)}
    rule_specs = review.get("runtime_rule_specs", [])
    rule_ids = [item.get("rule_id") for item in rule_specs if isinstance(item, dict)]
    rule_candidate_ids = [item.get("candidate_rule_id") for item in rule_specs if isinstance(item, dict)]
    if not _unique(rule_ids) or not _unique(rule_candidate_ids):
        add_issue(issues, "INTEGRATION-RULE-ID", "runtime_rule_specs", "Runtime rule and source-candidate IDs must be unique.")
    rule_by_id = {item.get("rule_id"): item for item in rule_specs if isinstance(item, dict)}
    positive_dispositions = {
        item.get("candidate_rule_id"): item for item in dispositions
        if isinstance(item, dict) and item.get("final_status") == "POSITIVE_RUNTIME_RULE"
    }
    positive_rule_ids = {item.get("target_rule_id") for item in positive_dispositions.values()}
    if set(rule_ids) != positive_rule_ids:
        add_issue(issues, "INTEGRATION-RULE-SET", "runtime_rule_specs", "Runtime specs must exactly equal positive candidate rule targets.")

    gaps = review.get("evidence_gaps", [])
    gap_ids = [item.get("gap_id") for item in gaps if isinstance(item, dict)]
    if not _unique(gap_ids):
        add_issue(issues, "INTEGRATION-GAP-ID", "evidence_gaps", "Evidence gap IDs must be unique.")
    gap_by_id = {item.get("gap_id"): item for item in gaps if isinstance(item, dict)}
    gap_memberships: dict[str, list[str]] = {}
    for gap_index, gap in enumerate(gaps):
        if not isinstance(gap, dict):
            continue
        gap_candidate_ids = gap.get("candidate_rule_ids", [])
        if gap.get("candidate_count") != len(gap_candidate_ids):
            add_issue(
                issues,
                "INTEGRATION-GAP-COUNT",
                f"evidence_gaps[{gap_index}]",
                "Evidence-gap candidate_count must equal the exact listed candidate set.",
            )
        for candidate_rule_id in gap_candidate_ids:
            gap_memberships.setdefault(candidate_rule_id, []).append(gap.get("gap_id"))
    pending_ids: set[str] = set()
    existing_material_review_ids: set[str] = set()
    final_ids: set[str] = set()

    for index, item in enumerate(dispositions):
        if not isinstance(item, dict):
            continue
        path = f"candidate_dispositions[{index}]"
        source = candidate_by_id.get(item.get("candidate_rule_id"))
        if source is None:
            continue
        evidence, source_candidate, family_id = source
        if item.get("evidence_id") != evidence.get("evidence_id") or item.get("family_id") != family_id:
            add_issue(issues, "INTEGRATION-CANDIDATE-BINDING", path, "Candidate evidence or family differs from canonical authority.")
        candidate_review_ids = item.get("review_ids", [])
        if any(review_id not in review_by_id for review_id in candidate_review_ids):
            add_issue(issues, "INTEGRATION-CANDIDATE-REVIEW", path, "Candidate references an unknown review.")
        allowed_refs: set[str] = set()
        for review_id in candidate_review_ids:
            review_item = review_by_id.get(review_id)
            if review_item and review_item.get("evidence_id") == item.get("evidence_id"):
                allowed_refs.update(reviewed_shots_by_review.get(review_id, set()))
            elif review_item:
                add_issue(issues, "INTEGRATION-CANDIDATE-CROSS-REVIEW", path, "Candidate review must belong to its own evidence record.")
        source_refs = set(item.get("source_refs", []))
        if not source_refs.issubset(allowed_refs):
            add_issue(issues, "INTEGRATION-CANDIDATE-SOURCE-REF", path, "Candidate source refs must be authorized by its cited fresh review.")
        canonical_candidate_refs = set(source_candidate.get("evidence_shot_ids", []))
        if not source_refs.issubset(canonical_candidate_refs):
            add_issue(
                issues,
                "INTEGRATION-CANDIDATE-CLAIM-REF",
                path,
                "Disposition refs must come only from the candidate's canonical Shot lineage.",
            )
        status = item.get("final_status")
        if status in FINAL_STATUSES:
            final_ids.add(item.get("candidate_rule_id"))
            if not source_refs:
                add_issue(issues, "INTEGRATION-FINAL-SOURCE-REF", path, "A final disposition needs at least one freshly reviewed Shot.")
            if item.get("material_unknowns"):
                add_issue(issues, "INTEGRATION-FINAL-UNKNOWN", path, "A final disposition cannot retain a material unknown.")
            if item.get("evidence_gap_id") is not None:
                add_issue(issues, "INTEGRATION-FINAL-GAP", path, "A final disposition cannot reference an evidence gap.")
            if not item.get("runtime_effect_key"):
                add_issue(issues, "INTEGRATION-FINAL-EFFECT", path, "A final disposition needs a runtime effect key.")
            moving_refs = {
                shot_id
                for review_id in candidate_review_ids
                for shot_id in moving_shots_by_review.get(review_id, set())
            }
            if not source_refs.issubset(moving_refs):
                add_issue(
                    issues,
                    "INTEGRATION-FINAL-MOVING-REVIEW",
                    path,
                    "Every final disposition Shot ref must have completed moving-image review.",
                )
        elif status == "EVIDENCE_GAP_PENDING":
            pending_ids.add(item.get("candidate_rule_id"))
            gap_id = item.get("evidence_gap_id")
            memberships = gap_memberships.get(item.get("candidate_rule_id"), [])
            if gap_id not in gap_by_id or memberships != [gap_id]:
                add_issue(issues, "INTEGRATION-PENDING-GAP", path, "Pending candidate must appear exactly once in the exact evidence gap it references.")
            if item.get("runtime_effect_key") is not None:
                add_issue(issues, "INTEGRATION-PENDING-EFFECT", path, "Pending candidate cannot claim a runtime effect.")
            if not item.get("material_unknowns"):
                add_issue(issues, "INTEGRATION-PENDING-UNKNOWN", path, "Pending candidate must name the material unknown that blocks final disposition.")
            moving_refs = {
                shot_id
                for review_id in candidate_review_ids
                for shot_id in moving_shots_by_review.get(review_id, set())
            }
            if source_refs != canonical_candidate_refs or not source_refs.issubset(moving_refs):
                add_issue(
                    issues,
                    "INTEGRATION-PENDING-REVIEW-INCOMPLETE",
                    path,
                    "A pending evidence-gap disposition is allowed only after every canonical candidate Shot has completed fresh moving-image review.",
                )
        elif status == "EXISTING_MATERIAL_REVIEW_REQUIRED":
            existing_material_review_ids.add(item.get("candidate_rule_id"))
            if item.get("evidence_gap_id") is not None:
                add_issue(
                    issues,
                    "INTEGRATION-EXISTING-REVIEW-GAP",
                    path,
                    "Unfinished review of existing material must not be mislabeled as a corpus evidence gap.",
                )
            if item.get("runtime_effect_key") is not None:
                add_issue(
                    issues,
                    "INTEGRATION-EXISTING-REVIEW-EFFECT",
                    path,
                    "Existing-material review debt cannot claim a runtime effect.",
                )
            if not item.get("material_unknowns"):
                add_issue(
                    issues,
                    "INTEGRATION-EXISTING-REVIEW-UNKNOWN",
                    path,
                    "Existing-material review debt must name the exact unresolved observation.",
                )
            moving_refs = {
                shot_id
                for review_id in candidate_review_ids
                for shot_id in moving_shots_by_review.get(review_id, set())
            }
            if source_refs != canonical_candidate_refs or not source_refs.issubset(moving_refs):
                add_issue(
                    issues,
                    "INTEGRATION-EXISTING-REVIEW-PICTURE-INCOMPLETE",
                    path,
                    "Existing-material audio review debt is valid only after every canonical candidate Shot has completed fresh moving-image review.",
                )
        if status != "EVIDENCE_GAP_PENDING" and gap_memberships.get(item.get("candidate_rule_id")):
            add_issue(issues, "INTEGRATION-FINAL-GAP-MEMBERSHIP", path, "A final candidate cannot remain listed in an evidence gap.")
        if item.get("audio_dependency") and status in FINAL_STATUSES:
            if not any(review_by_id.get(review_id, {}).get("audio_review_status") == "DIRECT_AUDITION_COMPLETE" for review_id in candidate_review_ids):
                add_issue(issues, "INTEGRATION-AUDIO-REVIEW", path, "Audio-dependent disposition requires direct audition evidence.")

        target_rule_id = item.get("target_rule_id")
        if status == "POSITIVE_RUNTIME_RULE":
            if (
                target_rule_id not in rule_by_id
                or item.get("runtime_effect_key") != f"RULE:{target_rule_id}"
                or not item.get("decision_axes")
                or item.get("merged_into_candidate_id") is not None
                or item.get("boundary_signal_ids")
                or item.get("boundary_forward_test_id") is not None
                or item.get("rejection_reason_code") is not None
            ):
                add_issue(issues, "INTEGRATION-POSITIVE-EFFECT", path, "Positive candidate must bind one runtime rule and at least one director decision axis.")
        elif status == "SUPPORTING_EVIDENCE":
            target = rule_by_id.get(target_rule_id)
            if (
                target_rule_id not in positive_rule_ids
                or item.get("runtime_effect_key") != f"SUPPORT:{target_rule_id}"
                or target is None
                or item.get("merged_into_candidate_id") is not None
                or item.get("boundary_signal_ids")
                or item.get("boundary_forward_test_id") is not None
                or item.get("rejection_reason_code") is not None
            ):
                add_issue(issues, "INTEGRATION-SUPPORT-EFFECT", path, "Supporting evidence must target a positive runtime rule.")
        elif status == "BOUNDARY_OR_COUNTEREXAMPLE":
            target = rule_by_id.get(target_rule_id)
            boundary_forward_test_id = item.get("boundary_forward_test_id")
            if (
                target_rule_id not in positive_rule_ids
                or target is None
                or not item.get("boundary_signal_ids")
                or not boundary_forward_test_id
                or boundary_forward_test_id not in forward_by_id
                or boundary_forward_test_id != target.get("boundary_forward_test_id")
                or not str(item.get("runtime_effect_key", "")).startswith(f"BOUNDARY:{target_rule_id}:")
                or item.get("merged_into_candidate_id") is not None
                or item.get("rejection_reason_code") is not None
            ):
                add_issue(issues, "INTEGRATION-BOUNDARY-EFFECT", path, "Boundary must target a positive rule and bind signals plus a forward test.")
        elif status == "MERGED_DUPLICATE":
            target_candidate_id = item.get("merged_into_candidate_id")
            target = positive_dispositions.get(target_candidate_id)
            target_rule = target.get("target_rule_id") if target else None
            if (
                target is None
                or target.get("family_id") != item.get("family_id")
                or item.get("runtime_effect_key") != f"MERGE:{target_rule}"
                or item.get("target_rule_id") is not None
                or item.get("boundary_signal_ids")
                or item.get("boundary_forward_test_id") is not None
                or item.get("rejection_reason_code") is not None
            ):
                add_issue(issues, "INTEGRATION-MERGE-EFFECT", path, "Merged duplicate must resolve directly to a same-family positive candidate.")
        elif status == "REJECTED_WITH_REASON":
            if (
                not item.get("rejection_reason_code")
                or item.get("runtime_effect_key") != f"REJECTION_GUARD:{item.get('candidate_rule_id')}"
                or item.get("target_rule_id") is not None
                or item.get("merged_into_candidate_id") is not None
                or item.get("boundary_signal_ids")
                or item.get("boundary_forward_test_id") is not None
            ):
                add_issue(issues, "INTEGRATION-REJECTION-EFFECT", path, "Rejected candidate needs a controlled reason and its own deny key.")

    relation_ids: list[str] = []
    for spec in rule_specs:
        if not isinstance(spec, dict):
            continue
        relation_ids.extend(
            item.get("relation_id")
            for item in spec.get("supporting_relations", [])
            if isinstance(item, dict)
        )
        counterexample = spec.get("counterexample")
        if isinstance(counterexample, dict):
            relation_ids.append(counterexample.get("relation_id"))
    if not _unique(relation_ids):
        add_issue(
            issues,
            "INTEGRATION-RELATION-ID",
            "runtime_rule_specs",
            "Runtime support and counterexample relation IDs must be unique.",
        )

    if set(gap_memberships) != pending_ids:
        add_issue(
            issues,
            "INTEGRATION-GAP-CANDIDATE-SET",
            "evidence_gaps",
            "Evidence-gap members must exactly equal the canonical pending-candidate set.",
        )

    for rule_index, spec in enumerate(rule_specs):
        if not isinstance(spec, dict):
            continue
        source_disposition = disposition_by_id.get(spec.get("candidate_rule_id"))
        if (
            source_disposition is None
            or source_disposition.get("final_status") != "POSITIVE_RUNTIME_RULE"
            or source_disposition.get("target_rule_id") != spec.get("rule_id")
            or source_disposition.get("family_id") != spec.get("family_id")
            or set(spec.get("source_refs", [])) != set(source_disposition.get("source_refs", []))
        ):
            add_issue(issues, "INTEGRATION-RULE-BINDING", f"runtime_rule_specs[{rule_index}]", "Runtime spec must exactly bind its positive candidate and reviewed source refs.")
        spec_source_refs = set(spec.get("source_refs", []))
        for role_index, role in enumerate(spec.get("functional_roles", [])):
            if not isinstance(role, dict):
                continue
            role_source_refs = set(role.get("source_refs", []))
            if (
                not role_source_refs
                or role.get("shot_id") not in role_source_refs
                or not role_source_refs.issubset(spec_source_refs)
            ):
                add_issue(
                    issues,
                    "INTEGRATION-FUNCTIONAL-ROLE-REF",
                    f"runtime_rule_specs[{rule_index}].functional_roles[{role_index}]",
                    "Functional-role Shot and refs must be contained in the positive candidate's fresh reviewed source refs.",
                )
        positive_case = forward_by_id.get(spec.get("positive_forward_test_id"), {})
        if (
            positive_case.get("test_mode") != "POSITIVE"
            or positive_case.get("positive_for_rule_ids") != [spec.get("rule_id")]
            or positive_case.get("boundary_for_rule_ids")
            or positive_case.get("expected_routing_status") != "SELECTED"
            or positive_case.get("expected_selected_rule_ids") != [spec.get("rule_id")]
            or positive_case.get("expected_selection_count") != 1
            or not positive_case.get("changed_director_dimensions")
        ):
            add_issue(
                issues,
                "INTEGRATION-POSITIVE-FORWARD-BINDING",
                f"runtime_rule_specs[{rule_index}].positive_forward_test_id",
                "Positive forward test must exist, target only this rule, select it, and change a director decision dimension.",
            )
        boundary_case = forward_by_id.get(spec.get("boundary_forward_test_id"), {})
        if (
            boundary_case.get("test_mode") != "BOUNDARY_OR_NON_APPLICABLE"
            or boundary_case.get("boundary_for_rule_ids") != [spec.get("rule_id")]
            or boundary_case.get("positive_for_rule_ids")
            or boundary_case.get("expected_rejected_rule_id") != spec.get("rule_id")
            or "NOT_APPLICABLE_MATCH" not in boundary_case.get("expected_rejection_reason_codes", [])
            or boundary_case.get("expected_routing_status") != "NO_APPLICABLE_RULE"
            or boundary_case.get("expected_selected_rule_ids")
            or boundary_case.get("expected_selection_count") != 0
        ):
            add_issue(
                issues,
                "INTEGRATION-BOUNDARY-FORWARD-BINDING",
                f"runtime_rule_specs[{rule_index}].boundary_forward_test_id",
                "Boundary forward test must exist, target this rule, and expect its guarded rejection.",
            )
        target_boundaries = [
            item
            for item in dispositions
            if isinstance(item, dict)
            and item.get("final_status") == "BOUNDARY_OR_COUNTEREXAMPLE"
            and item.get("target_rule_id") == spec.get("rule_id")
        ]
        compiled_boundary_signals = {
            signal
            for item in target_boundaries
            for signal in item.get("boundary_signal_ids", [])
        }
        spec_signals = set(spec.get("routing", {}).get("not_applicable_if_any", []))
        if not compiled_boundary_signals or not compiled_boundary_signals.issubset(spec_signals):
            add_issue(
                issues,
                "INTEGRATION-BOUNDARY-COMPILE",
                f"runtime_rule_specs[{rule_index}].routing.not_applicable_if_any",
                "Every reviewed boundary signal must compile into the runtime non-applicability set; additional project-original safety guards are allowed only when forward-tested.",
            )
        positive_disposition = positive_dispositions.get(spec.get("candidate_rule_id"))
        positive_source = candidate_by_id.get(spec.get("candidate_rule_id"))
        supporting_dispositions = [
            item
            for item in dispositions
            if isinstance(item, dict)
            and item.get("final_status") == "SUPPORTING_EVIDENCE"
            and item.get("target_rule_id") == spec.get("rule_id")
        ]
        supporting_by_candidate = {
            item.get("candidate_rule_id"): item for item in supporting_dispositions
        }
        spec_supporting_relations = spec.get("supporting_relations", [])
        spec_support_ids = {
            item.get("source_candidate_rule_id")
            for item in spec_supporting_relations
            if isinstance(item, dict)
        }
        if not spec_support_ids or not spec_support_ids.issubset(set(supporting_by_candidate)):
            add_issue(
                issues,
                "INTEGRATION-SUPPORT-RELATION-BINDING",
                f"runtime_rule_specs[{rule_index}].supporting_relations",
                "Every runtime support relation must bind a supporting disposition for this rule.",
            )
        for relation_index, relation in enumerate(spec_supporting_relations):
            if not isinstance(relation, dict):
                continue
            candidate_rule_id = relation.get("source_candidate_rule_id")
            disposition = supporting_by_candidate.get(candidate_rule_id)
            authority = candidate_by_id.get(candidate_rule_id)
            if (
                disposition is None
                or authority is None
                or set(relation.get("source_refs", [])) != set(disposition.get("source_refs", []))
                or relation.get("evidence_id") != authority[0].get("evidence_id")
                or relation.get("work_id") != authority[0].get("work_id")
            ):
                add_issue(
                    issues,
                    "INTEGRATION-SUPPORT-RELATION-BINDING",
                    f"runtime_rule_specs[{rule_index}].supporting_relations[{relation_index}]",
                    "Support relation candidate, work, evidence and Shots must exactly bind the reviewed disposition.",
                )

        target_boundary_by_candidate = {
            item.get("candidate_rule_id"): item for item in target_boundaries
        }
        counterexample = spec.get("counterexample", {})
        counter_candidate_id = counterexample.get("source_candidate_rule_id") if isinstance(counterexample, dict) else None
        counter_disposition = target_boundary_by_candidate.get(counter_candidate_id)
        counter_authority = candidate_by_id.get(counter_candidate_id)
        if (
            counter_candidate_id not in target_boundary_by_candidate
            or counter_disposition is None
            or counter_authority is None
            or set(counterexample.get("source_refs", [])) != set(counter_disposition.get("source_refs", []))
            or counterexample.get("evidence_id") != counter_authority[0].get("evidence_id")
            or counterexample.get("work_id") != counter_authority[0].get("work_id")
        ):
            add_issue(
                issues,
                "INTEGRATION-COUNTEREXAMPLE-RELATION-BINDING",
                f"runtime_rule_specs[{rule_index}].counterexample",
                "Runtime counterexample candidate, work, evidence and Shots must exactly bind the reviewed boundary disposition.",
            )
        unrelated_support = any(
            candidate_by_id.get(item.get("candidate_rule_id"), ({}, {}, ""))[0].get("work_id")
            != (positive_source[0].get("work_id") if positive_source else None)
            for item in supporting_dispositions
        )
        if positive_disposition is not None and not unrelated_support:
            add_issue(
                issues,
                "INTEGRATION-RULE-CROSS-WORK-SUPPORT",
                f"runtime_rule_specs[{rule_index}]",
                "Each positive runtime rule needs supporting evidence from a different work.",
            )
        if positive_disposition is not None and not target_boundaries:
            add_issue(
                issues,
                "INTEGRATION-RULE-BOUNDARY",
                f"runtime_rule_specs[{rule_index}]",
                "Each positive runtime rule needs at least one reviewed boundary disposition.",
            )

    final_family_ids = {
        item.get("family_id") for item in dispositions
        if isinstance(item, dict) and item.get("final_status") in FINAL_STATUSES and item.get("runtime_effect_key")
    }
    final_evidence_ids = {
        item.get("evidence_id") for item in dispositions
        if isinstance(item, dict) and item.get("final_status") in FINAL_STATUSES
    }
    source_gap_count = sum(
        1 for item in source_rows
        if isinstance(item, dict) and item.get("status") == "EVIDENCE_GAP_PENDING"
    )
    computed_phase_status = (
        "COMPLETE"
        if not issues
        and final_ids == authority_candidate_ids
        and not pending_ids
        and not gaps
        and final_family_ids == authority_family_ids
        and final_evidence_ids == authority_evidence_ids
        and source_gap_count == 0
        else "IN_PROGRESS"
        if existing_material_review_ids
        else "PARTIAL_EVIDENCE_GAP"
    )
    declared = review.get("declared_phase_status")
    if declared == "COMPLETE" and computed_phase_status != "COMPLETE":
        add_issue(issues, "INTEGRATION-FALSE-COMPLETE", "declared_phase_status", "COMPLETE must be derived from exhaustive live counts and zero gaps.")
    elif declared != computed_phase_status:
        add_issue(
            issues,
            "INTEGRATION-PHASE-STATUS-DRIFT",
            "declared_phase_status",
            "Declared phase status must match the live distinction between complete, external evidence gaps, and unfinished existing-material review.",
        )

    return {
        "schema_version": "runtime-integration-validation/0.1",
        "status": "PASS" if not issues else "FAIL",
        "phase_status": computed_phase_status if not issues else "IN_PROGRESS",
        "source_disposition_count": len(source_numbers),
        "evidence_review_count": len(reviewed_evidence_ids),
        "candidate_disposition_count": len(disposition_ids),
        "candidate_final_disposition_count": len(final_ids),
        "candidate_runtime_effect_count": sum(
            1 for item in dispositions
            if isinstance(item, dict) and item.get("runtime_effect_key")
        ),
        "runtime_active_family_count": len(final_family_ids),
        "evidence_final_mapping_count": len(final_evidence_ids),
        "positive_runtime_rule_count": len(positive_dispositions),
        "unresolved_candidate_count": len(pending_ids) + len(existing_material_review_ids),
        "pending_evidence_gap_count": len(pending_ids),
        "existing_material_review_required_count": len(existing_material_review_ids),
        "evidence_gap_count": len(gaps),
        "error_count": len(issues),
        "issues": issues,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, default=REVIEW_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    report_path = args.report
    protected_paths = [
        args.review,
        args.schema,
        FORWARD_INDEX_PATH,
        SOURCE_REGISTER_PATH,
        *sorted(EVIDENCE_ROOT.rglob("*.scene-evidence.json")),
    ]
    if report_path.is_symlink() or any(
        _same_file_target(report_path, protected_path) for protected_path in protected_paths
    ):
        print("ERROR: --report must not overwrite or alias an input or schema file", file=sys.stderr)
        return 2
    if (
        not args.check
        and report_path.exists()
        and report_path.resolve() != REPORT_PATH.resolve()
    ):
        print("ERROR: --report refuses to overwrite an existing noncanonical file", file=sys.stderr)
        return 2
    try:
        report = validate(read_json(args.review), read_json(args.schema))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.check:
        if not report_path.is_file() or report_path.read_text(encoding="utf-8") != rendered:
            return 1
    else:
        try:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            _write_report_atomically(report_path, rendered)
        except OSError as exc:
            print(f"ERROR: report write failed: {exc}", file=sys.stderr)
            return 2
    sys.stdout.write(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
