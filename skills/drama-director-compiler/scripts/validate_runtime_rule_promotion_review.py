#!/usr/bin/env python3
"""Validate the canonical Wave 1 video-review and promotion manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
REVIEW_PATH = REPOSITORY_ROOT / "research" / "grammar" / "runtime_rule_promotion_wave1.review.json"
SCHEMA_PATH = SKILL_ROOT / "references" / "runtime-rule-promotion-review.schema.json"
EVIDENCE_ROOT = REPOSITORY_ROOT / "research" / "evidence"
REPORT_PATH = REPOSITORY_ROOT / "research" / "validation" / "runtime-rule-promotion-wave1-validation.json"

sys.path.insert(0, str(SCRIPT_DIR))
from build_candidate_rule_index import classify_family  # noqa: E402
from validate_scene_evidence import validate_schema_subset  # noqa: E402


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def add_issue(issues: list[dict[str, str]], code: str, path: str, message: str) -> None:
    issues.append({"level": "error", "code": code, "path": path, "message": message})


def ids_for(evidence: dict[str, Any]) -> set[str]:
    ids = {evidence["evidence_id"], evidence["work_id"]}
    for shot in evidence["shots"]:
        ids.add(shot["shot_id"])
    for anchor in evidence.get("text_anchors", []):
        if isinstance(anchor, dict) and isinstance(anchor.get("anchor_id"), str):
            ids.add(anchor["anchor_id"])
    return ids


def validate(review: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    validate_schema_subset(review, schema, schema, issues, "$")
    evidence_by_id: dict[str, dict[str, Any]] = {}
    candidate_by_id: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for path in sorted(EVIDENCE_ROOT.rglob("*.scene-evidence.json")):
        evidence = read_json(path)
        evidence_by_id[evidence["evidence_id"]] = evidence
        for candidate in evidence["candidate_rules"]:
            candidate_by_id[candidate["candidate_rule_id"]] = (evidence, candidate)

    review_ids = [item.get("review_id") for item in review.get("evidence_reviews", [])]
    reviewed_evidence_ids = [item.get("evidence_id") for item in review.get("evidence_reviews", [])]
    review_by_evidence_id = {
        item.get("evidence_id"): item
        for item in review.get("evidence_reviews", [])
        if isinstance(item, dict) and isinstance(item.get("evidence_id"), str)
    }
    if len(review_ids) != len(set(review_ids)) or len(reviewed_evidence_ids) != len(set(reviewed_evidence_ids)):
        add_issue(issues, "WAVE1-REVIEW-ID", "evidence_reviews", "Review and evidence IDs must be unique.")
    for index, item in enumerate(review.get("evidence_reviews", [])):
        path = f"evidence_reviews[{index}]"
        evidence = evidence_by_id.get(item.get("evidence_id"))
        if evidence is None:
            add_issue(issues, "WAVE1-EVIDENCE-MISSING", path, "Reviewed evidence unit does not exist.")
            continue
        unknown_shots = sorted(set(item.get("shot_ids", [])) - ids_for(evidence))
        if unknown_shots:
            add_issue(issues, "WAVE1-SHOT-REF", path, f"Unknown reviewed Shot IDs: {unknown_shots}.")
        text_anchor = item.get("text_anchor")
        if isinstance(text_anchor, dict):
            shot_by_id = {shot.get("shot_id"): shot for shot in evidence.get("shots", []) if isinstance(shot, dict)}
            anchor_shot = shot_by_id.get(text_anchor.get("shot_id"))
            if anchor_shot is None or text_anchor.get("shot_id") not in item.get("shot_ids", []):
                add_issue(issues, "WAVE1-TEXT-SHOT", path, "Text anchor must belong to a freshly reviewed Shot.")
            elif (
                text_anchor.get("start", {}).get("seconds", -1) < anchor_shot.get("start", {}).get("seconds", 0)
                or text_anchor.get("end", {}).get("seconds", -1) > anchor_shot.get("end", {}).get("seconds", 0)
                or text_anchor.get("start", {}).get("seconds", 0) >= text_anchor.get("end", {}).get("seconds", 0)
            ):
                add_issue(issues, "WAVE1-TEXT-RANGE", path, "Text anchor must be a positive interval inside its reviewed Shot.")
        problem = item.get("scene_problem")
        if isinstance(problem, dict) and not set(problem.get("source_refs", [])).issubset(ids_for(evidence)):
            add_issue(issues, "WAVE1-PROBLEM-REF", path, "Scene-problem refs must resolve inside the reviewed evidence unit.")
        for role in item.get("roles", []):
            if role.get("shot_id") not in ids_for(evidence) or not set(role.get("source_refs", [])).issubset(ids_for(evidence)):
                add_issue(issues, "WAVE1-ROLE-REF", path, "Functional-role refs must resolve inside the reviewed evidence unit.")

    promotion_ids = [item.get("candidate_rule_id") for item in review.get("promotions", [])]
    rule_ids = [item.get("rule_id") for item in review.get("promotions", [])]
    if len(promotion_ids) != len(set(promotion_ids)) or len(rule_ids) != len(set(rule_ids)):
        add_issue(issues, "WAVE1-PROMOTION-ID", "promotions", "Promotion source and runtime rule IDs must be unique.")
    families: set[str] = set()
    for index, promotion in enumerate(review.get("promotions", [])):
        path = f"promotions[{index}]"
        source_pair = candidate_by_id.get(promotion.get("candidate_rule_id"))
        if source_pair is None:
            add_issue(issues, "WAVE1-PROMOTION-SOURCE", path, "Promotion source candidate does not exist.")
            continue
        source_evidence, source_candidate = source_pair
        family_id, _assignment = classify_family(source_candidate)
        families.add(promotion.get("family_id"))
        if family_id != promotion.get("family_id"):
            add_issue(issues, "WAVE1-FAMILY-DRIFT", path, "Promotion family differs from deterministic candidate classification.")
        if source_evidence.get("boundary_status") != "NATURAL_START_END_VERIFIED":
            add_issue(issues, "WAVE1-NATURAL-BOUNDARY", path, "Promotion source must have a picture-verified natural scene boundary.")
        if source_evidence.get("evidence_id") not in reviewed_evidence_ids:
            add_issue(issues, "WAVE1-FRESH-PICTURE-REVIEW", path, "Promotion source lacks a fresh Wave 1 picture review.")
        source_review = review_by_evidence_id.get(source_evidence.get("evidence_id"), {})
        source_problem = source_review.get("scene_problem") if isinstance(source_review, dict) else None
        if not isinstance(source_problem, dict) or source_problem.get("primary") != promotion.get("scene_problem"):
            add_issue(issues, "WAVE1-PROBLEM-BINDING", path, "Promotion scene problem must equal the freshly reviewed source problem.")
        reviewed_roles = {
            (role.get("shot_id"), role.get("appearance_id"), role.get("functional_role"), tuple(role.get("source_refs", [])))
            for role in source_review.get("roles", [])
            if isinstance(role, dict)
        }
        promoted_roles = {
            (role.get("shot_id"), role.get("appearance_id"), role.get("functional_role"), tuple(role.get("source_refs", [])))
            for role in promotion.get("functional_roles", [])
            if isinstance(role, dict)
        }
        if not promoted_roles or not promoted_roles.issubset(reviewed_roles):
            add_issue(issues, "WAVE1-ROLE-BINDING", path, "Promoted functional roles must match the freshly reviewed source roles exactly.")
        support_works = {source_evidence.get("work_id")}
        related = [*promotion.get("supporting_relations", []), promotion.get("counterexample", {})]
        for relation in related:
            target_pair = candidate_by_id.get(relation.get("source_candidate_rule_id"))
            if target_pair is None:
                add_issue(issues, "WAVE1-RELATION-SOURCE", path, "Support or boundary candidate does not exist.")
                continue
            target_evidence, target_candidate = target_pair
            target_family, _assignment = classify_family(target_candidate)
            if (
                target_evidence.get("work_id") != relation.get("work_id")
                or target_evidence.get("evidence_id") != relation.get("evidence_id")
                or target_family != promotion.get("family_id")
                or not set(relation.get("source_refs", [])).issubset(ids_for(target_evidence))
            ):
                add_issue(issues, "WAVE1-RELATION-BINDING", path, "Support or boundary relation is not exactly bound to same-family evidence.")
            if target_evidence.get("evidence_id") not in reviewed_evidence_ids:
                add_issue(issues, "WAVE1-RELATION-REVIEW", path, "Support or boundary evidence lacks fresh picture review.")
            target_review = review_by_evidence_id.get(target_evidence.get("evidence_id"), {})
            if not set(relation.get("source_refs", [])).issubset(set(target_review.get("shot_ids", []))):
                add_issue(issues, "WAVE1-RELATION-REVIEW-BINDING", path, "Support or boundary refs must be among the freshly reviewed Shots.")
            support_works.add(relation.get("work_id"))
        if len(support_works) < 3:
            add_issue(issues, "WAVE1-CROSS-WORK", path, "Promotion needs a source, unrelated support, and unrelated boundary work.")
        if promotion.get("positive_forward_test_id") == promotion.get("boundary_forward_test_id"):
            add_issue(issues, "WAVE1-FORWARD-PAIR", path, "Positive and boundary forward tests must be distinct.")

    promotion_count = len(review.get("promotions", []))
    phase_status = "COMPLETE" if promotion_count >= 3 and len(families) >= 3 else "PARTIAL" if promotion_count else "BLOCKED"
    return {
        "schema_version": "runtime-rule-promotion-wave1-validation/0.1",
        "status": "PASS" if not issues else "FAIL",
        "phase_status": phase_status if not issues else "BLOCKED",
        "promoted_rule_count": promotion_count,
        "promoted_family_count": len(families),
        "reviewed_evidence_count": len(reviewed_evidence_ids),
        "error_count": len(issues),
        "issues": issues,
        "boundaries": [
            "Picture review supports only the cited visual facts.",
            "Semantic audio remains unknown and no promoted rule depends on audio.",
            "Creative quality, generation, and publication remain HUMAN_REVIEW_PENDING or unauthorized.",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path, default=REVIEW_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = validate(read_json(args.review), read_json(args.schema))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    rendered = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.check:
        if not args.report.is_file() or args.report.read_text(encoding="utf-8") != rendered:
            return 1
    else:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
