#!/usr/bin/env python3
"""Validate DirectorMind runtime Grammar v0.2 against promotion authorities."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
GRAMMAR_PATH = REPOSITORY_ROOT / "research" / "grammar" / "director_grammar_v0.2.json"
INDEX_PATH = REPOSITORY_ROOT / "research" / "grammar" / "candidate_rule_index.json"
MATRIX_PATH = REPOSITORY_ROOT / "research" / "grammar" / "cross_work_support_matrix.json"
PROMOTION_REVIEW_PATH = REPOSITORY_ROOT / "research" / "grammar" / "runtime_rule_promotion_wave1.review.json"
SCHEMA_PATH = SKILL_ROOT / "references" / "director-grammar.schema.json"
PROMOTION_REVIEW_SCHEMA_PATH = SKILL_ROOT / "references" / "runtime-rule-promotion-review.schema.json"
REPORT_PATH = REPOSITORY_ROOT / "research" / "validation" / "director-grammar-validation.json"

sys.path.insert(0, str(SCRIPT_DIR))
from validate_scene_evidence import validate_schema_subset  # noqa: E402
from validate_candidate_rules import validate_repository as validate_candidate_repository  # noqa: E402
from validate_runtime_rule_promotion_review import validate as validate_promotion_review  # noqa: E402


ELIGIBLE_PROMOTIONS = {"CROSS_WORK_SUPPORTED", "GENERAL_DEFAULT"}
CONFLICT_PRIORITY = [
    "LOCKED_STORY_FACTS",
    "REVEAL_AND_INFORMATION_BOUNDARIES",
    "SAFETY_AND_PROTECTED_PARTICIPANTS",
    "CONTINUITY",
    "SCENE_POV",
    "SPATIAL_GEOGRAPHY_AND_AXIS",
    "TRIGGER_SPECIFIC_DIRECTOR_RULES",
    "VISUAL_STYLE",
    "PROVIDER_LIMITATIONS",
]
REQUIRED_PROJECT_CODES = {
    "LOCKED_SOURCE_IS_STORY_AUTHORITY",
    "DIALOGUE_AND_VISIBLE_TEXT_VERBATIM",
    "SOURCE_COVERAGE_COMPLETE",
    "MODEL_INDEPENDENT_IR_ONLY",
    "PROJECT_ORIGINAL_REFERENCES_ONLY",
}
REQUIRED_SAFETY_CODES = {
    "UNKNOWN_CANNOT_AUTHORIZE",
    "NO_REFERENCE_SURFACE_COPY",
    "HIGH_RISK_REQUIRES_FALLBACK",
    "SUBJECT_SIMILARITY_NOT_APPLICABILITY",
    "GENERATION_AND_PUBLICATION_NOT_AUTHORIZED",
    "UNREVIEWED_OUTPUT_HUMAN_REVIEW_PENDING",
}
LEGACY_RUNTIME_IDS = {
    "DG-01", "DG-02", "DG-03", "DG-04", "DG-05",
    "GO-01", "GO-02", "GO-03", "GO-04", "GO-05", "GO-06", "GO-07",
}


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def add_issue(
    issues: list[dict[str, str]], code: str, path: str, message: str
) -> None:
    issues.append({"level": "error", "code": code, "path": path, "message": message})


def normalized_phrase(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def iter_strings(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_strings(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_strings(item, f"{path}.{key}")


def eligible_candidates(
    index: dict[str, Any], matrix: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    eligible_families = {
        family.get("family_id")
        for family in matrix.get("families", [])
        if family.get("promotion_eligibility") in ELIGIBLE_PROMOTIONS
    }
    result: dict[str, dict[str, Any]] = {}
    for candidate in index.get("candidates", []):
        promotion = candidate.get("promotion", {})
        rights = candidate.get("rights_boundary", {})
        if (
            promotion.get("status") in ELIGIBLE_PROMOTIONS
            and promotion.get("unknown_dependency_present") is False
            and rights.get("runtime_authorized") is True
            and rights.get("surface_copy_allowed") is False
            and candidate.get("canonical_rule_family") in eligible_families
        ):
            result[candidate["candidate_rule_id"]] = candidate
    return result


def fresh_lineage_by_candidate(review: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for promotion in review.get("promotions", []):
        if not isinstance(promotion, dict):
            continue
        candidate_id = promotion.get("candidate_rule_id")
        if not isinstance(candidate_id, str):
            continue
        related = [
            *promotion.get("supporting_relations", []),
            promotion.get("counterexample", {}),
        ]
        refs = [
            *promotion.get("source_refs", []),
            *[
                ref
                for relation in related
                if isinstance(relation, dict)
                for ref in relation.get("source_refs", [])
            ],
        ]
        result[candidate_id] = list(dict.fromkeys(refs))
    return result


def verified_routing_review(
    rule: dict[str, Any],
    candidate_contract: dict[str, Any],
    path: str,
    issues: list[dict[str, str]],
) -> bool:
    review = rule.get("routing_review", {})
    review_id = review.get("review_id")
    review_ref = review.get("review_ref")
    if review.get("status") not in {"HUMAN_VERIFIED", "ROOT_VIDEO_VERIFIED"} or not isinstance(review_id, str) or not isinstance(review_ref, str):
        add_issue(issues, "GRAMMAR-ROUTING-REVIEW", f"{path}.routing_review", "Machine routing fields require a named verification record.")
        return False
    if Path(review_ref).is_absolute():
        add_issue(issues, "GRAMMAR-ROUTING-REVIEW-REF", f"{path}.routing_review.review_ref", "Routing review refs must be repository-relative.")
        return False
    review_root = (REPOSITORY_ROOT / "research" / "validation" / "grammar-rule-reviews").resolve()
    resolved = (REPOSITORY_ROOT / review_ref).resolve()
    try:
        resolved.relative_to(review_root)
    except ValueError:
        add_issue(issues, "GRAMMAR-ROUTING-REVIEW-REF", f"{path}.routing_review.review_ref", "Routing review must stay inside research/validation/grammar-rule-reviews.")
        return False
    if not resolved.is_file() or resolved.suffix != ".json":
        add_issue(issues, "GRAMMAR-ROUTING-REVIEW-REF", f"{path}.routing_review.review_ref", "Routing review must be an existing JSON file.")
        return False
    try:
        review_record = read_json(resolved)
    except (OSError, ValueError, json.JSONDecodeError):
        add_issue(issues, "GRAMMAR-ROUTING-REVIEW-REF", f"{path}.routing_review.review_ref", "Routing review JSON is invalid.")
        return False
    expected = {
        "schema_version": "director-grammar-routing-review/0.1",
        "review_id": review_id,
        "rule_id": rule.get("rule_id"),
        "promotion_source_candidate_id": rule.get("promotion_source_candidate_id"),
        "status": review.get("status"),
        "candidate_trigger": candidate_contract.get("trigger"),
        "candidate_required_story_facts": candidate_contract.get("required_story_facts"),
        "routing": rule.get("routing"),
    }
    if review_record != expected:
        add_issue(issues, "GRAMMAR-ROUTING-REVIEW-MISMATCH", f"{path}.routing_review", "Routing review does not exactly bind the promoted candidate and machine routing fields.")
        return False
    return True


def validate_grammar(
    grammar: dict[str, Any],
    index: dict[str, Any],
    matrix: dict[str, Any],
    schema: dict[str, Any] | None = None,
    promotion_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if schema is not None:
        validate_schema_subset(grammar, schema, schema, issues, "$")

    if grammar.get("schema_version") != "director-grammar/0.2":
        add_issue(issues, "GRAMMAR-VERSION", "schema_version", "Expected director-grammar/0.2.")
    if "sources" in grammar:
        add_issue(issues, "GRAMMAR-LEGACY-SOURCES", "sources", "v0.1 source lists are lineage, not runtime grammar.")
    if grammar.get("conflict_priority") != CONFLICT_PRIORITY:
        add_issue(issues, "GRAMMAR-CONFLICT-ORDER", "conflict_priority", "The fixed nine-level conflict order changed.")

    fresh_lineage: dict[str, list[str]] = {}
    try:
        active_promotion_review = (
            promotion_review
            if promotion_review is not None
            else read_json(PROMOTION_REVIEW_PATH)
        )
        promotion_report = validate_promotion_review(
            active_promotion_review,
            read_json(PROMOTION_REVIEW_SCHEMA_PATH),
        )
    except (OSError, ValueError, json.JSONDecodeError):
        promotion_report = {"status": "FAIL"}
        active_promotion_review = {}
    if (
        promotion_report.get("status") != "PASS"
        or promotion_report.get("phase_status") != "COMPLETE"
    ):
        add_issue(
            issues,
            "GRAMMAR-PROMOTION-REVIEW-AUTHORITY",
            "promotion_review",
            "Runtime lineage requires a valid and complete fresh promotion-review authority.",
        )
    else:
        fresh_lineage = fresh_lineage_by_candidate(active_promotion_review)

    project_constraints = grammar.get("project_constraints", []) if isinstance(grammar.get("project_constraints"), list) else []
    safety_constraints = grammar.get("safety_constraints", []) if isinstance(grammar.get("safety_constraints"), list) else []
    all_constraints = project_constraints + safety_constraints
    constraint_ids = [item.get("constraint_id") for item in all_constraints if isinstance(item, dict)]
    if len(constraint_ids) != len(set(constraint_ids)):
        add_issue(issues, "GRAMMAR-CONSTRAINT-ID", "project_constraints/safety_constraints", "Constraint IDs must be unique.")
    project_codes = Counter(item.get("constraint_code") for item in project_constraints if isinstance(item, dict))
    safety_codes = Counter(item.get("constraint_code") for item in safety_constraints if isinstance(item, dict))
    if set(project_codes) != REQUIRED_PROJECT_CODES or any(count != 1 for count in project_codes.values()):
        add_issue(issues, "GRAMMAR-PROJECT-CONSTRAINTS", "project_constraints", "Required project constraint codes must appear exactly once.")
    if set(safety_codes) != REQUIRED_SAFETY_CODES or any(count != 1 for count in safety_codes.values()):
        add_issue(issues, "GRAMMAR-SAFETY-CONSTRAINTS", "safety_constraints", "Required safety constraint codes must appear exactly once.")
    for index_number, constraint in enumerate(all_constraints):
        for ref in constraint.get("authority_refs", []) if isinstance(constraint, dict) else []:
            target = (REPOSITORY_ROOT / ref).resolve()
            try:
                target.relative_to(REPOSITORY_ROOT.resolve())
            except ValueError:
                add_issue(issues, "GRAMMAR-AUTHORITY-PATH", f"constraints[{index_number}].authority_refs", "Authority ref must stay inside the repository.")
                continue
            if not target.is_file():
                add_issue(issues, "GRAMMAR-AUTHORITY-MISSING", f"constraints[{index_number}].authority_refs", f"Missing authority ref: {ref}.")

    candidate_report = validate_candidate_repository(index, matrix)
    candidate_authority_valid = candidate_report.get("status") == "PASS"
    if not candidate_authority_valid:
        add_issue(
            issues,
            "GRAMMAR-CANDIDATE-AUTHORITY",
            "candidate_index/support_matrix",
            "Candidate and support-matrix authorities must pass their own validator before routing.",
        )
    eligible = eligible_candidates(index, matrix) if candidate_authority_valid else {}
    rules = grammar.get("rules", []) if isinstance(grammar.get("rules"), list) else []
    seen_rule_ids: set[str] = set()
    used_candidates: list[str] = []
    known_candidate_ids = {
        candidate.get("candidate_rule_id")
        for candidate in index.get("candidates", [])
        if isinstance(candidate, dict)
    }
    known_work_ids = {
        candidate.get("source", {}).get("work_id")
        for candidate in index.get("candidates", [])
        if isinstance(candidate, dict)
    }
    known_surface_ids = set(known_candidate_ids)
    for candidate in index.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        source = candidate.get("source", {})
        known_surface_ids.add(source.get("evidence_id"))
        known_surface_ids.update(source.get("evidence_shot_ids", []))
    known_surface_ids.discard(None)

    for rule_index, rule in enumerate(rules):
        path = f"rules[{rule_index}]"
        if not isinstance(rule, dict):
            continue
        rule_id = rule.get("rule_id")
        if rule_id in seen_rule_ids:
            add_issue(issues, "GRAMMAR-RULE-ID", f"{path}.rule_id", "Rule IDs must be unique.")
        seen_rule_ids.add(rule_id)
        if rule_id in LEGACY_RUNTIME_IDS:
            add_issue(issues, "GRAMMAR-LEGACY-RUNTIME", f"{path}.rule_id", "Seed and reference-transfer rules cannot enter v0.2.")

        source_id = rule.get("promotion_source_candidate_id")
        used_candidates.append(source_id)
        if source_id not in known_candidate_ids:
            add_issue(issues, "GRAMMAR-CANDIDATE-UNKNOWN", f"{path}.promotion_source_candidate_id", "Promotion source does not exist.")
            continue
        if source_id not in eligible:
            add_issue(issues, "GRAMMAR-CANDIDATE-INELIGIBLE", f"{path}.promotion_source_candidate_id", "Promotion source is not runtime eligible.")
            continue
        candidate = eligible[source_id]
        if rule.get("promotion_status") != candidate.get("promotion", {}).get("status"):
            add_issue(issues, "GRAMMAR-PROMOTION-DRIFT", f"{path}.promotion_status", "Rule promotion status differs from its source candidate.")
        if rule.get("canonical_rule_family") != candidate.get("canonical_rule_family"):
            add_issue(issues, "GRAMMAR-FAMILY-DRIFT", f"{path}.canonical_rule_family", "Rule family differs from its source candidate.")
        expected_problem = candidate.get("scene_problem", {})
        actual_problem = rule.get("scene_problem", {})
        routing = rule.get("routing", {})
        if (
            actual_problem.get("primary") == "NO_SPECIALIZED_PROBLEM"
            or "NO_SPECIALIZED_PROBLEM" in actual_problem.get("secondary", [])
            or "NO_SPECIALIZED_PROBLEM" in routing.get("scene_problems", [])
        ):
            add_issue(
                issues,
                "GRAMMAR-NO-SPECIALIZED-RUNTIME",
                f"{path}.scene_problem",
                "NO_SPECIALIZED_PROBLEM is a negative routing sentinel and cannot authorize a runtime rule.",
            )
        if (
            actual_problem.get("primary") != expected_problem.get("primary")
            or actual_problem.get("secondary") != expected_problem.get("secondary")
        ):
            add_issue(issues, "GRAMMAR-SCENE-PROBLEM-DRIFT", f"{path}.scene_problem", "Rule scene problem differs from its promoted candidate.")
        if rule.get("confidence") != candidate.get("confidence"):
            add_issue(issues, "GRAMMAR-CONFIDENCE-DRIFT", f"{path}.confidence", "Rule confidence differs from its promoted candidate.")
        if rule.get("functional_roles") != candidate.get("functional_roles"):
            add_issue(issues, "GRAMMAR-ROLE-DRIFT", f"{path}.functional_roles", "Rule functional roles differ from its promoted candidate.")
        candidate_contract = candidate.get("operational_contract", {})
        contract_pairs = {
            "required_story_facts": rule.get("required_story_facts"),
            "director_decision": rule.get("director_decision"),
            "coverage": rule.get("coverage"),
            "blocking": rule.get("blocking"),
            "pacing": rule.get("pacing"),
            "edit_logic": rule.get("edit_logic"),
            "continuity": rule.get("continuity"),
            "applicable_when": rule.get("applicable_when"),
            "not_applicable_when": rule.get("not_applicable_when", {}).get("descriptions"),
            "failure_modes": rule.get("failure_modes"),
            "ai_risk": rule.get("ai_risk"),
            "fallback": rule.get("fallback"),
        }
        for contract_key, rule_value in contract_pairs.items():
            if rule_value != candidate_contract.get(contract_key):
                add_issue(issues, "GRAMMAR-CONTRACT-DRIFT", f"{path}.{contract_key}", f"Rule {contract_key} differs from its promoted candidate contract.")
        if rule.get("trigger", {}).get("description") != candidate_contract.get("trigger"):
            add_issue(issues, "GRAMMAR-CONTRACT-DRIFT", f"{path}.trigger.description", "Rule trigger differs from its promoted candidate contract.")
        candidate_audio = candidate_contract.get("audio_logic", {})
        rule_audio = rule.get("audio_logic", {})
        if candidate_audio.get("status") == "AUDIO_OBSERVED":
            if (
                rule_audio.get("status") != "AUDIO_OBSERVED"
                or rule_audio.get("instruction") != candidate_audio.get("value")
                or rule_audio.get("source_refs") != candidate_audio.get("source_refs")
            ):
                add_issue(issues, "GRAMMAR-AUDIO-DRIFT", f"{path}.audio_logic", "Evidence-backed audio differs from its promoted candidate contract.")
        elif rule_audio.get("status") != "NOT_DEPENDENT" or rule_audio.get("source_refs"):
            add_issue(issues, "GRAMMAR-AUDIO-DRIFT", f"{path}.audio_logic", "A non-audio candidate cannot gain an audio-dependent runtime instruction.")
        elif rule_audio.get("instruction") is not None:
            add_issue(issues, "GRAMMAR-AUDIO-DRIFT", f"{path}.audio_logic.instruction", "NOT_DEPENDENT audio must use a null instruction.")
        verified_routing_review(rule, candidate_contract, path, issues)
        lineage_ids = rule.get("evidence_lineage", {}).get("candidate_rule_ids", [])
        if source_id not in lineage_ids:
            add_issue(issues, "GRAMMAR-LINEAGE-SOURCE", f"{path}.evidence_lineage.candidate_rule_ids", "Promotion source must remain in evidence lineage.")
        lineage = rule.get("evidence_lineage", {})
        source = candidate.get("source", {})
        if source.get("work_id") not in lineage.get("work_ids", []):
            add_issue(issues, "GRAMMAR-LINEAGE-WORK", f"{path}.evidence_lineage.work_ids", "Promotion source work is missing from lineage.")
        if source.get("evidence_id") not in lineage.get("evidence_ids", []):
            add_issue(issues, "GRAMMAR-LINEAGE-EVIDENCE", f"{path}.evidence_lineage.evidence_ids", "Promotion evidence ID is missing from lineage.")
        expected_fresh_shots = fresh_lineage.get(source_id)
        actual_lineage_shots = lineage.get("evidence_shot_ids", [])
        if expected_fresh_shots is None:
            add_issue(
                issues,
                "GRAMMAR-LINEAGE-FRESH-AUTHORITY",
                f"{path}.evidence_lineage.evidence_shot_ids",
                "Runtime rule has no matching fresh promotion-review authority.",
            )
        elif set(actual_lineage_shots) != set(expected_fresh_shots):
            add_issue(
                issues,
                "GRAMMAR-LINEAGE-FRESH-SHOTS",
                f"{path}.evidence_lineage.evidence_shot_ids",
                "Runtime Shot lineage must exactly equal the promotion source, support, and counterexample fresh refs.",
            )

        declared_problems = [actual_problem.get("primary"), *actual_problem.get("secondary", [])]
        if set(routing.get("scene_problems", [])) != set(declared_problems):
            add_issue(issues, "GRAMMAR-ROUTING-PROBLEM-DRIFT", f"{path}.routing.scene_problems", "Machine routing problems differ from the human-readable contract.")
        trigger_signals = set(rule.get("trigger", {}).get("required_signals", []))
        routed_signals = set(routing.get("trigger_all_of", [])) | set(routing.get("trigger_any_of", []))
        if trigger_signals != routed_signals:
            add_issue(issues, "GRAMMAR-ROUTING-TRIGGER-DRIFT", f"{path}.routing", "Machine trigger signals differ from the human-readable contract.")
        if set(rule.get("not_applicable_when", {}).get("signals", [])) != set(routing.get("not_applicable_if_any", [])):
            add_issue(issues, "GRAMMAR-ROUTING-BOUNDARY-DRIFT", f"{path}.routing.not_applicable_if_any", "Machine non-applicability signals differ from the human-readable contract.")
        if set(rule.get("conflicts_with_rule_ids", [])) != set(routing.get("conflicts_with", [])):
            add_issue(issues, "GRAMMAR-ROUTING-CONFLICT-DRIFT", f"{path}.routing.conflicts_with", "Machine conflicts differ from the human-readable contract.")
        human_review = rule.get("human_review", {})
        if rule.get("promotion_status") == "GENERAL_DEFAULT":
            if human_review.get("status") != "APPROVED" or not human_review.get("review_id"):
                add_issue(issues, "GRAMMAR-GENERAL-REVIEW", f"{path}.human_review", "GENERAL_DEFAULT requires an approved director review.")
            if len(lineage.get("forward_test_ids", [])) < 2:
                add_issue(issues, "GRAMMAR-GENERAL-FORWARD", f"{path}.evidence_lineage.forward_test_ids", "GENERAL_DEFAULT requires two original forward tests.")
            if len(lineage.get("work_ids", [])) < 3:
                add_issue(issues, "GRAMMAR-GENERAL-WORKS", f"{path}.evidence_lineage.work_ids", "GENERAL_DEFAULT requires three unrelated works.")
        elif human_review.get("status") == "NOT_REQUIRED_FOR_CROSS_WORK" and human_review.get("review_id") is not None:
            add_issue(issues, "GRAMMAR-CROSS-WORK-REVIEW", f"{path}.human_review", "A non-required cross-work review must use a null review ID.")

    duplicate_sources = sorted(item for item, count in Counter(used_candidates).items() if count > 1)
    if duplicate_sources:
        add_issue(issues, "GRAMMAR-CANDIDATE-DUPLICATE", "rules", f"Promotion sources were reused: {duplicate_sources}.")
    if set(used_candidates) != set(eligible):
        add_issue(
            issues,
            "GRAMMAR-ELIGIBLE-SET-DRIFT",
            "rules",
            f"Runtime rules must exactly cover eligible promotion sources; expected {len(eligible)}, found {len(set(used_candidates))}.",
        )

    operational_grammar = copy.deepcopy(grammar)
    for rule in operational_grammar.get("rules", []) if isinstance(operational_grammar.get("rules"), list) else []:
        if not isinstance(rule, dict):
            continue
        rule.pop("evidence_lineage", None)
        rule.pop("promotion_source_candidate_id", None)
        if isinstance(rule.get("audio_logic"), dict):
            rule["audio_logic"]["source_refs"] = []
        for role in rule.get("functional_roles", []):
            if isinstance(role, dict):
                role["source_refs"] = []
    operational_json = json.dumps(operational_grammar, ensure_ascii=False, sort_keys=True)
    normalized_operational = normalized_phrase(operational_json)
    for surface_id in sorted(known_surface_ids):
        phrase = normalized_phrase(str(surface_id))
        if phrase and phrase in normalized_operational:
            add_issue(issues, "GRAMMAR-SURFACE-ID", "$", f"Evidence/source ID escaped lineage: {surface_id}.")
            break
    for work_id in sorted(item for item in known_work_ids if item):
        phrase = normalized_phrase(str(work_id))
        if len(phrase) >= 6 and phrase in normalized_operational:
            add_issue(issues, "GRAMMAR-WORK-SURFACE", "$", f"Reference work name escaped lineage: {work_id}.")
            break
        title_tokens = [
            token
            for token in str(work_id).split("-")
            if not re.fullmatch(r"(?:19|20)\d{2}|S\d{2}(?:E\d{2})?|E\d{2}", token)
        ]
        if not title_tokens:
            continue
        if len(title_tokens) == 1:
            title_pattern = rf"\b{re.escape(title_tokens[0].title())}\b"
            matched = re.search(title_pattern, operational_json) is not None
        else:
            title_pattern = r"\b" + r"[\s_-]+".join(re.escape(token) for token in title_tokens) + r"\b"
            matched = re.search(title_pattern, operational_json, re.IGNORECASE) is not None
        if matched:
            add_issue(issues, "GRAMMAR-WORK-SURFACE", "$", f"Reference work title escaped lineage: {' '.join(title_tokens)}.")
            break

    return {
        "schema_version": "director-grammar-validation/0.1",
        "status": "PASS" if not issues else "FAIL",
        "eligible_candidate_count": len(eligible),
        "runtime_rule_count": len(rules),
        "project_constraint_count": len(project_constraints),
        "safety_constraint_count": len(safety_constraints),
        "error_count": len(issues),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grammar", type=Path, default=GRAMMAR_PATH)
    parser.add_argument("--index", type=Path, default=INDEX_PATH)
    parser.add_argument("--matrix", type=Path, default=MATRIX_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    report = validate_grammar(
        read_json(args.grammar),
        read_json(args.index),
        read_json(args.matrix),
        read_json(args.schema),
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
