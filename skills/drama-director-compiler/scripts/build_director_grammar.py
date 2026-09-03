#!/usr/bin/env python3
"""Build Runtime Grammar v0.2 rules from the canonical promotion review."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from build_candidate_rule_index import assert_runtime_review_lineage


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
GRAMMAR_ROOT = REPOSITORY_ROOT / "research" / "grammar"
GRAMMAR_PATH = GRAMMAR_ROOT / "director_grammar_v0.2.json"
INDEX_PATH = GRAMMAR_ROOT / "candidate_rule_index.json"
REVIEW_PATH = GRAMMAR_ROOT / "runtime_integration.review.json"
ROUTING_REVIEW_ROOT = REPOSITORY_ROOT / "research" / "validation" / "grammar-rule-reviews"


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def json_text(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def review_ref(rule_id: str) -> str:
    return f"research/validation/grammar-rule-reviews/{rule_id}-ROUTING.json"


def build_rule(
    promotion: dict[str, Any],
    candidate: dict[str, Any],
    related_dispositions: list[dict[str, Any]],
    candidate_by_id: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if candidate["promotion"]["status"] != "CROSS_WORK_SUPPORTED":
        raise ValueError(f"candidate is not cross-work supported: {candidate['candidate_rule_id']}")
    contract = candidate["operational_contract"]
    routing = {
        "scene_problems": [promotion["scene_problem"]],
        "trigger_all_of": promotion["routing"]["trigger_all_of"],
        "trigger_any_of": promotion["routing"]["trigger_any_of"],
        "required_fact_types": promotion["routing"]["required_fact_types"],
        "not_applicable_if_any": promotion["routing"]["not_applicable_if_any"],
        "conflicts_with": [],
        "audit_subject_tags": [],
    }
    review_id = f"{promotion['rule_id']}-ROUTING-REVIEW"
    routing_review = {
        "schema_version": "director-grammar-routing-review/0.1",
        "review_id": review_id,
        "rule_id": promotion["rule_id"],
        "promotion_source_candidate_id": candidate["candidate_rule_id"],
        "status": "ROOT_VIDEO_VERIFIED",
        "candidate_trigger": contract["trigger"],
        "candidate_required_story_facts": contract["required_story_facts"],
        "routing": routing,
    }
    related_candidates = [
        candidate_by_id[item["candidate_rule_id"]] for item in related_dispositions
    ]
    candidate_ids = [candidate["candidate_rule_id"], *[item["candidate_rule_id"] for item in related_candidates]]
    work_ids = [candidate["source"]["work_id"], *[item["source"]["work_id"] for item in related_candidates]]
    evidence_ids = [candidate["source"]["evidence_id"], *[item["source"]["evidence_id"] for item in related_candidates]]
    evidence_shot_ids = [
        *promotion["source_refs"],
        *[ref for item in related_dispositions for ref in item["source_refs"]],
    ]
    rule = {
        "rule_id": promotion["rule_id"],
        "name": promotion["name"],
        "canonical_rule_family": candidate["canonical_rule_family"],
        "promotion_source_candidate_id": candidate["candidate_rule_id"],
        "promotion_status": candidate["promotion"]["status"],
        "runtime_authorized": True,
        "scene_problem": {
            "primary": candidate["scene_problem"]["primary"],
            "secondary": candidate["scene_problem"]["secondary"],
        },
        "functional_roles": candidate["functional_roles"],
        "trigger": {
            "description": contract["trigger"],
            "required_signals": [
                *promotion["routing"]["trigger_all_of"],
                *promotion["routing"]["trigger_any_of"],
            ],
        },
        "routing": routing,
        "routing_review": {
            "status": "ROOT_VIDEO_VERIFIED",
            "review_id": review_id,
            "review_ref": review_ref(promotion["rule_id"]),
        },
        "required_story_facts": contract["required_story_facts"],
        "applicable_when": contract["applicable_when"],
        "not_applicable_when": {
            "descriptions": contract["not_applicable_when"],
            "signals": promotion["routing"]["not_applicable_if_any"],
        },
        "conflict_levels": [
            "LOCKED_STORY_FACTS",
            "CONTINUITY",
            "SPATIAL_GEOGRAPHY_AND_AXIS",
            "TRIGGER_SPECIFIC_DIRECTOR_RULES",
        ],
        "conflicts_with_rule_ids": [],
        "selection_rank": promotion["selection_rank"],
        "director_decision": contract["director_decision"],
        "coverage": contract["coverage"],
        "blocking": contract["blocking"],
        "pacing": contract["pacing"],
        "edit_logic": contract["edit_logic"],
        "audio_logic": {"status": "NOT_DEPENDENT", "instruction": None, "source_refs": []},
        "continuity": contract["continuity"],
        "ai_risk": contract["ai_risk"],
        "failure_modes": contract["failure_modes"],
        "fallback": contract["fallback"],
        "confidence": candidate["confidence"],
        "evidence_lineage": {
            "candidate_rule_ids": list(dict.fromkeys(candidate_ids)),
            "work_ids": list(dict.fromkeys(work_ids)),
            "evidence_ids": list(dict.fromkeys(evidence_ids)),
            "evidence_shot_ids": list(dict.fromkeys(evidence_shot_ids)),
            "relation_review_ids": list(dict.fromkeys(
                item["runtime_effect_key"] for item in related_dispositions
            )),
            "counterexample_ids": [
                item["candidate_rule_id"]
                for item in related_dispositions
                if item["final_status"] == "BOUNDARY_OR_COUNTEREXAMPLE"
            ],
            "forward_test_ids": [
                promotion["positive_forward_test_id"],
                promotion["boundary_forward_test_id"],
            ],
            "director_review_id": None,
        },
        "rights_boundary": {
            "surface_copy_allowed": False,
            "subject_matter_similarity_is_trigger": False,
            "project_original_assets_only": True,
        },
        "human_review": {"status": "NOT_REQUIRED_FOR_CROSS_WORK", "review_id": None},
    }
    return rule, routing_review


def build_outputs() -> tuple[dict[str, Any], dict[Path, dict[str, Any]]]:
    grammar = read_json(GRAMMAR_PATH)
    index = read_json(INDEX_PATH)
    promotion_review = read_json(REVIEW_PATH)
    by_id = {item["candidate_rule_id"]: item for item in index["candidates"]}
    assert_runtime_review_lineage(promotion_review, by_id)
    rules: list[dict[str, Any]] = []
    reviews: dict[Path, dict[str, Any]] = {}
    for promotion in sorted(promotion_review["runtime_rule_specs"], key=lambda item: item["selection_rank"]):
        candidate = by_id.get(promotion["candidate_rule_id"])
        if candidate is None:
            raise ValueError(f"missing promoted candidate: {promotion['candidate_rule_id']}")
        related_dispositions = [
            item
            for item in promotion_review["candidate_dispositions"]
            if (
                item.get("target_rule_id") == promotion["rule_id"]
                and item.get("final_status") in {
                    "SUPPORTING_EVIDENCE",
                    "BOUNDARY_OR_COUNTEREXAMPLE",
                }
            )
            or (
                item.get("final_status") == "MERGED_DUPLICATE"
                and item.get("merged_into_candidate_id") == promotion["candidate_rule_id"]
            )
        ]
        boundary_signals = {
            signal
            for item in related_dispositions
            if item["final_status"] == "BOUNDARY_OR_COUNTEREXAMPLE"
            for signal in item["boundary_signal_ids"]
        }
        if boundary_signals != set(promotion["routing"]["not_applicable_if_any"]):
            raise ValueError(
                f"boundary signals do not compile exactly for {promotion['rule_id']}"
            )
        rule, routing_review = build_rule(
            promotion, candidate, related_dispositions, by_id
        )
        rules.append(rule)
        reviews[ROUTING_REVIEW_ROOT / f"{promotion['rule_id']}-ROUTING.json"] = routing_review
    grammar["rules"] = rules
    disposition_keys = (
        "candidate_rule_id",
        "family_id",
        "evidence_id",
        "final_status",
        "runtime_effect_key",
        "review_ids",
        "source_refs",
        "target_rule_id",
        "merged_into_candidate_id",
        "boundary_signal_ids",
        "rejection_reason_code",
        "evidence_gap_id",
    )
    dispositions = [
        {key: item[key] for key in disposition_keys}
        for item in promotion_review["candidate_dispositions"]
    ]
    final_count = sum(
        item["final_status"] != "EVIDENCE_GAP_PENDING" for item in dispositions
    )
    grammar["runtime_integration"] = {
        "authority_path": "research/grammar/runtime_integration.review.json",
        "phase_status": promotion_review["declared_phase_status"],
        "source_count": len(promotion_review["source_dispositions"]),
        "evidence_count": len(promotion_review["evidence_reviews"]),
        "candidate_count": len(dispositions),
        "final_candidate_count": final_count,
        "dispositions": dispositions,
    }
    return grammar, reviews


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        grammar, reviews = build_outputs()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    outputs = [(GRAMMAR_PATH, json_text(grammar)), *[(path, json_text(data)) for path, data in sorted(reviews.items())]]
    failures: list[str] = []
    for path, content in outputs:
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                failures.append(path.relative_to(REPOSITORY_ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    actual_reviews = set(ROUTING_REVIEW_ROOT.glob("*.json")) if ROUTING_REVIEW_ROOT.exists() else set()
    stale_reviews = sorted(actual_reviews - set(reviews))
    if args.check:
        failures.extend(path.relative_to(REPOSITORY_ROOT).as_posix() for path in stale_reviews)
    if failures:
        print("grammar builder drift:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    print(f"{'checked' if args.check else 'built'} {len(grammar['rules'])} runtime rule(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
