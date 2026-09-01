#!/usr/bin/env python3
"""Build the normalized candidate index and cross-work support matrix.

The builder is deliberately conservative. It clusters the wording already
present in canonical Scene Evidence JSON, preserves every legacy lineage field,
and keeps every current candidate blocked while scene problem, functional role,
counterexample and confidence evidence remain unresolved.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
EVIDENCE_ROOT = REPOSITORY_ROOT / "research" / "evidence"
GRAMMAR_ROOT = REPOSITORY_ROOT / "research" / "grammar"
INDEX_PATH = GRAMMAR_ROOT / "candidate_rule_index.json"
MATRIX_JSON_PATH = GRAMMAR_ROOT / "cross_work_support_matrix.json"
MATRIX_MD_PATH = GRAMMAR_ROOT / "cross_work_support_matrix.md"


FAMILY_TERMS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "SPATIAL-REGISTRATION-AND-RESET",
        "Establish or restore readable geography before tighter coverage or a new state.",
        ("register", "re-register", "geometry", "geography", "room map", "spatial reset", "anchor"),
    ),
    (
        "THRESHOLD-AND-ROUTE-CONTINUITY",
        "Carry people, direction and state through routes, apertures and thresholds.",
        ("threshold", "doorway", "ingress", "exit", "departure", "route", "waypoint", "aperture"),
    ),
    (
        "OBJECT-STATE-AND-CUSTODY",
        "Keep visible object source, holder, state and handoff legible.",
        ("object", "prop", "material", "readout", "record", "paper", "device", "custody"),
    ),
    (
        "SCREEN-OWNERSHIP-AND-PERFORMANCE-HOLD",
        "Allocate sustained screen ownership when one visible performance progression is primary.",
        ("screen ownership", "sustained", "hold the performer", "clean single", "terminal owner", "longer hold"),
    ),
    (
        "RECEIVER-AND-REACTION-DISTRIBUTION",
        "Choose receiver, observer, witness or reaction coverage only when the receiving state matters.",
        ("receiver", "observer", "witness", "reaction", "receipt", "attention cascade"),
    ),
    (
        "MULTI-THREAD-STATE-INTERCUT",
        "Intercut separate zones or threads only on meaningful visible state updates.",
        ("intercut", "parallel thread", "multi-space", "remote", "separate thread", "cross-zone"),
    ),
    (
        "PROXIMITY-AND-RELATION-GEOMETRY",
        "Make distance, shared-frame and two-person relation changes visible.",
        ("proximity", "distance", "shared frame", "two-person", "relation frame", "shared relation"),
    ),
    (
        "PROCEDURAL-HANDOFF-AND-WORKFLOW",
        "Track assessment, task ownership, demonstration, work onset and handoff.",
        ("task", "procedure", "procedural", "work", "demonstration", "assessment", "operator"),
    ),
    (
        "STATE-CHANGE-EDITING",
        "Place cuts or reframes on a visible state change without inventing causality.",
        ("state change", "cut to", "punctuation", "transition", "peak", "cascade"),
    ),
    (
        "CONTINUOUS-MOVEMENT-AND-OCCLUSION",
        "Preserve orientation and state through sustained movement, occlusion or a continuous-looking route.",
        ("continuous", "long take", "moving", "mobile", "occlusion", "reacquire"),
    ),
    (
        "SCALE-AND-REVEAL-LADDER",
        "Change scale or reveal order only after the relevant relation is established.",
        ("scale", "overhead", "high/wide", "distant", "reveal", "ladder"),
    ),
    (
        "AFTERMATH-AND-TERMINAL-STATE",
        "Hold or restore the visible terminal state after a consequential change.",
        ("aftermath", "recovery", "terminal", "result", "end on", "close on"),
    ),
    (
        "ACTION-CAUSAL-CHAIN",
        "Keep source, preparation, contact or event, result and carried consequence readable.",
        ("action causality", "contact", "threat", "burst", "consequence", "preparation"),
    ),
    (
        "AXIS-AND-COVERAGE-GRAMMAR",
        "Use a stable axis and limited coverage grammar until a relation change requires reset.",
        ("axis", "opposing singles", "reverse", "coverage", "master", "angle grammar"),
    ),
    (
        "CONTINUITY-LEDGER-AND-VERSIONING",
        "Version and carry person, object, surface and location states across cuts.",
        ("version", "carry", "continuity", "state ledger", "before-state", "after-state"),
    ),
    (
        "SUBJECTIVE-ACCESS-AND-INFORMATION",
        "Control subjective or asymmetric audience access without asserting unproved semantics.",
        ("subjective", "audience information", "black field", "information access", "asymmetry"),
    ),
)


# Every override below was selected from the same 16 source-neutral mechanism
# families after a two-part, candidate-by-candidate read-only review. The
# remaining candidates were explicitly accepted in their deterministic family.
FAMILY_OVERRIDES: dict[str, str] = {
    "A-QUIET-PLACE-2018-PARALLEL-BODY-STATE-RADIAL-LIGHT-001-AQP-C01-HOLD-SUBJECT-THEN-SEPARATE-THREAT-STATES": "SCALE-AND-REVEAL-LADDER",
    "A-QUIET-PLACE-2018-PARALLEL-BODY-STATE-RADIAL-LIGHT-001-AQP-C02-GROUP-PARALLEL-THREADS-BY-VISIBLE-STATE-CHANGE": "MULTI-THREAD-STATE-INTERCUT",
    "A-QUIET-PLACE-2018-PARALLEL-BODY-STATE-RADIAL-LIGHT-001-AQP-C04-DELAY-REJOIN-WITH-EMPTY-GEOMETRY-TRACE-AND-CONTACT-RECEIPT": "THRESHOLD-AND-ROUTE-CONTINUITY",
    "APOLLO-13-1995-CONSTRAINED-MATERIAL-HANDOFF-001-AP13-C01-ASSESSMENT-RECEIVER-TO-NEW-ROOM-ACTION": "PROCEDURAL-HANDOFF-AND-WORKFLOW",
    "B99-S05E14-THE-BOX-PRIDE-BAIT-CONFESSION-001-B99-CAND-MICRO-BRACKET-HOLD-002": "SCREEN-OWNERSHIP-AND-PERFORMANCE-HOLD",
    "B99-S05E14-THE-BOX-PRIDE-BAIT-CONFESSION-001-B99-CAND-MOBILE-ZONE-CAP-004": "CONTINUOUS-MOVEMENT-AND-OCCLUSION",
    "BEAR-S01E07-REVIEW-001-BEAR-C02-RECURRING-ZONES": "SPATIAL-REGISTRATION-AND-RESET",
    "BEAR-S01E07-REVIEW-001-BEAR-C03-SUBTRACTIVE-AFTERMATH": "AFTERMATH-AND-TERMINAL-STATE",
    "BEAR-S02E07-TASK-CLOSED-LOOP-001-BEAR-S02-C03-DUAL-RESULT-RECEIPT": "RECEIVER-AND-REACTION-DISTRIBUTION",
    "BEAR-S02E07-TASK-CLOSED-LOOP-001-BEAR-S02-C04-TASK-LEDGER-OVER-CAMERA-CONTINUITY": "CONTINUITY-LEDGER-AND-VERSIONING",
    "CHERNOBYL-S01E05-HEARING-RECON-001-CHERNOBYL-CAND-RETURN-TO-FORMAL-ROOM-AFTER-PEAK-004": "AFTERMATH-AND-TERMINAL-STATE",
    "CHILDREN-OF-MEN-2006-MOVING-CAR-EXTERIOR-DISRUPTION-001-CHILDREN-CAND-APERTURE-EVENT-BEFORE-GROSS-BODY-RESPONSE-002": "ACTION-CAUSAL-CHAIN",
    "CHILDREN-OF-MEN-2006-MOVING-CAR-EXTERIOR-DISRUPTION-001-CHILDREN-CAND-CABIN-ZONES-AS-MOBILE-GEOGRAPHY-001": "SPATIAL-REGISTRATION-AND-RESET",
    "CITIZEN-KANE-1941-BREAKFAST-MONTAGE-001-CK-C01-INVARIANT-SPACE-MULTICHANNEL-DELTA": "CONTINUITY-LEDGER-AND-VERSIONING",
    "CITIZEN-KANE-1941-BREAKFAST-MONTAGE-001-CK-C02-REPEATED-BRIDGE-AS-ELLIPSIS-PUNCTUATION": "STATE-CHANGE-EDITING",
    "DM-ANDOR-S01E10-SEL-001-ANDOR-W4-C01": "SPATIAL-REGISTRATION-AND-RESET",
    "DM-EVID-HH-S01E06-ENSEMBLE-CONTINUOUS-REFRAMING-V0.1-HILL-HOUSE-ECR-C01": "CONTINUOUS-MOVEMENT-AND-OCCLUSION",
    "HOUSE-OF-THE-DRAGON-S01E08-THRONE-ROOM-INGRESS-TO-SEATED-STATE-001-HOTD-CAND-MAKE-ASSISTANCE-AND-OBJECT-STATES-COMPLETE-003": "ACTION-CAUSAL-CHAIN",
    "HOUSE-OF-THE-DRAGON-S01E08-THRONE-ROOM-INGRESS-TO-SEATED-STATE-001-HOTD-CAND-PUNCTUATE-LONG-AXIS-TRAVEL-002": "THRESHOLD-AND-ROUTE-CONTINUITY",
    "KNIVES-OUT-2019-WILL-READING-001-KNIVES-C02-DISTRIBUTE-SCREEN-OWNERSHIP-WHEN-BODIES-DIVERGE": "RECEIVER-AND-REACTION-DISTRIBUTION",
    "KNIVES-OUT-2019-WILL-READING-001-KNIVES-C03-SEATED-TO-STANDING-DENSITY-LEDGER": "SPATIAL-REGISTRATION-AND-RESET",
    "MARRIAGE-STORY-2019-APARTMENT-SEQUENCE-001-MS-APT-C02-STABLE-SEAT-ANCHORS-CARRY-DENSE-ALTERNATION": "AXIS-AND-COVERAGE-GRAMMAR",
    "MARTIAN-MULTI-SPACE-OBJECT-STATE-EDITORIAL-SEQUENCE-LOCAL-001-MARTIAN-MSOSES-C04": "CONTINUITY-LEDGER-AND-VERSIONING",
    "MRR-S04E07-ACT-FOUR-VISUAL-001-MRR-S04E07-C01-DETAIL-THEN-CONTAINER-REGISTER": "SCALE-AND-REVEAL-LADDER",
    "MRR-S04E07-ACT-FOUR-VISUAL-001-MRR-S04E07-C04-PROGRESSIVE-RELATION-REMOVAL-TO-HELD-SINGLES": "SCREEN-OWNERSHIP-AND-PERFORMANCE-HOLD",
    "NOBODY-2021-BUS-001-NOBODY-C03-SPATIAL-RESET-AFTER-BURST": "SPATIAL-REGISTRATION-AND-RESET",
    "SOUND-OF-METAL-SIGNAL-STATE-EE-V0.1-SOM-SIGNAL-CAND-ALIGN-PICTURE-AND-MEASURED-BOUNDARY-002": "STATE-CHANGE-EDITING",
    "SOUND-OF-METAL-SIGNAL-STATE-EE-V0.1-SOM-SIGNAL-CAND-HOLD-PICTURE-ACROSS-MEASURED-ENTRY-001": "SUBJECTIVE-ACCESS-AND-INFORMATION",
    "SUCCESSION-S01E06-BOARD-VOTE-001-SUC-C01": "RECEIVER-AND-REACTION-DISTRIBUTION",
    "SUCCESSION-S01E06-BOARD-VOTE-001-SUC-C02": "MULTI-THREAD-STATE-INTERCUT",
    "SUCCESSION-S01E06-BOARD-VOTE-001-SUC-C03": "RECEIVER-AND-REACTION-DISTRIBUTION",
    "SUCCESSION-S01E06-BOARD-VOTE-001-SUC-C04": "THRESHOLD-AND-ROUTE-CONTINUITY",
    "TED-LASSO-S01E08-DARTS-REVERSAL-001-TED-S01E08-C01-REGISTER-PUBLIC-OBJECT-CONTEST-GEOMETRY": "SPATIAL-REGISTRATION-AND-RESET",
    "TED-LASSO-S01E08-DARTS-REVERSAL-001-TED-S01E08-C03-SEPARATE-PERFORMER-ACTION-TARGET-STATE-AND-RESULT-CLAIM": "ACTION-CAUSAL-CHAIN",
    "THE-DEVIL-WEARS-PRADA-2006-CERULEAN-CORRECTION-001-DWP-C01-REGISTER-TRIGGER-OBJECT-BEFORE-ATTENTION-CASCADE": "RECEIVER-AND-REACTION-DISTRIBUTION",
    "THE-DEVIL-WEARS-PRADA-2006-CERULEAN-CORRECTION-001-DWP-C02-SUSTAIN-CORRECTOR-IN-SHARED-WORK-FRAME-WITH-SELECTIVE-RECEIVER-CHECKS": "SCREEN-OWNERSHIP-AND-PERFORMANCE-HOLD",
    "THE-DEVIL-WEARS-PRADA-2006-CERULEAN-CORRECTION-001-DWP-C04-END-ON-TERMINAL-OWNER-WHILE-BACKGROUND-TASK-CONTINUES": "SCREEN-OWNERSHIP-AND-PERFORMANCE-HOLD",
    "THE-SOCIAL-NETWORK-2010-OPENING-TWO-PERSON-EXCHANGE-001-TSN-C02-VARY-HOLD-LENGTH-WITHIN-FIXED-ANGLE-GRAMMAR": "AXIS-AND-COVERAGE-GRAMMAR",
    "TRUE-DETECTIVE-S01E04-MULTI-ZONE-MOBILE-ROUTE-001-TD-S01E04-C04-FUNCTIONAL-SEGMENTATION-FALLBACK-FOR-LONG-ROUTE": "CONTINUOUS-MOVEMENT-AND-OCCLUSION",
    "UNBELIEVABLE-S01E02-CONTAINED-TWO-PERSON-SEQUENCE-001-UNB-S01E02-C04-HOLD-VISIBLE-BODY-OR-HAND-OBJECT-STATE": "SCREEN-OWNERSHIP-AND-PERFORMANCE-HOLD",
    "WIRE-S01E04-OLD-CASES-001-WIRE-C01-REGISTER-RECORD-TO-LIVE-SPACE": "OBJECT-STATE-AND-CUSTODY",
    "WIRE-S01E04-OLD-CASES-001-WIRE-C02-EMBODY-HYPOTHESIS-THEN-TEST-TRACE": "PROCEDURAL-HANDOFF-AND-WORKFLOW",
    "WIRE-S01E04-OLD-CASES-001-WIRE-C03-CUT-ON-EPISTEMIC-STATE-CHANGE": "STATE-CHANGE-EDITING",
    "WIRE-S01E04-OLD-CASES-001-WIRE-C04-LONG-TAKE-WHEN-CONTINUITY-IS-THE-PROOF": "CONTINUOUS-MOVEMENT-AND-OCCLUSION",
}


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def discover_sources(root: Path = EVIDENCE_ROOT) -> list[Path]:
    return sorted(root.rglob("*.scene-evidence.json"), key=lambda item: item.as_posix())


def _lineage_problem(scene_problem: dict[str, Any]) -> str:
    notes = str(scene_problem.get("notes", ""))
    match = re.search(r"legacy primary label ([A-Z0-9_]+) is retained", notes)
    return match.group(1) if match else "LEGACY_SCENE_PROBLEM"


def _cluster_text(rule: dict[str, Any]) -> str:
    lineage = rule["legacy_migration"]
    values = [
        rule["candidate_rule_id"],
        lineage.get("trigger", ""),
        lineage.get("directing_decision", ""),
        lineage.get("coverage", ""),
        lineage.get("blocking", ""),
        lineage.get("pacing_edit", ""),
        lineage.get("applicability", ""),
    ]
    return " ".join(str(value) for value in values).lower()


def classify_family(rule: dict[str, Any]) -> tuple[str, str]:
    candidate_rule_id = rule["candidate_rule_id"]
    if candidate_rule_id in FAMILY_OVERRIDES:
        return FAMILY_OVERRIDES[candidate_rule_id], "ROOT_REVIEWED_TEXTUAL_CLUSTER"
    text = _cluster_text(rule)
    scored: list[tuple[int, int, str]] = []
    for order, (family_id, _description, terms) in enumerate(FAMILY_TERMS):
        score = sum(text.count(term) for term in terms)
        scored.append((score, -order, family_id))
    score, _order, family_id = max(scored)
    if score == 0:
        suffix = rule["candidate_rule_id"].rsplit("-", 1)[-1]
        return f"UNCLUSTERED-{suffix}", "UNCLUSTERED_PENDING_HUMAN_REVIEW"
    return family_id, "ROOT_REVIEWED_TEXTUAL_CLUSTER"


def _counterexample_record(text: str) -> dict[str, Any]:
    lowered = text.lower()
    if "different-trigger" in lowered or "triggers are not proven identical" in lowered:
        return {
            "counterexample_id": None,
            "status": "BOUNDARY_ONLY",
            "same_trigger_status": "DIFFERENT_TRIGGER",
            "relation": "NARROWS",
            "source_candidate_rule_id": None,
            "work_id": None,
            "evidence_id": None,
            "source_refs": [],
            "review_status": "NOT_REVIEWED",
            "review_id": None,
            "review_ref": None,
            "notes": text,
        }
    if re.search(r"unknown|pending|hypothes", lowered):
        return {
            "counterexample_id": None,
            "status": "UNKNOWN",
            "same_trigger_status": "UNKNOWN",
            "relation": "UNKNOWN",
            "source_candidate_rule_id": None,
            "work_id": None,
            "evidence_id": None,
            "source_refs": [],
            "review_status": "NOT_REVIEWED",
            "review_id": None,
            "review_ref": None,
            "notes": text,
        }
    return {
        "counterexample_id": None,
        "status": "BOUNDARY_ONLY",
        "same_trigger_status": "UNKNOWN",
        "relation": "NARROWS",
        "source_candidate_rule_id": None,
        "work_id": None,
        "evidence_id": None,
        "source_refs": [],
        "review_status": "NOT_REVIEWED",
        "review_id": None,
        "review_ref": None,
        "notes": text,
    }


def _candidate_record(
    evidence: dict[str, Any],
    rule: dict[str, Any],
    family_id: str,
    assignment_status: str,
) -> dict[str, Any]:
    scene_problem = evidence["scene_problem"]
    lineage_label = _lineage_problem(scene_problem)
    counterexample = _counterexample_record(rule["legacy_migration"]["counterexample"])
    return {
        "schema_version": "candidate-director-rule/0.1",
        "candidate_rule_id": rule["candidate_rule_id"],
        "canonical_rule_family": family_id,
        "family_assignment_status": assignment_status,
        "relation_to_family": "NARROWS",
        "source": {
            "work_id": evidence["work_id"],
            "evidence_id": evidence["evidence_id"],
            "source_candidate_rule_id": rule["candidate_rule_id"],
            "source_method_ids": rule["source_method_ids"],
            "evidence_shot_ids": rule["evidence_shot_ids"],
        },
        "scene_problem": {
            "primary": scene_problem["primary"],
            "secondary": scene_problem["secondary"],
            "status": scene_problem["status"],
            "source_refs": scene_problem["source_refs"],
            "lineage_label": lineage_label,
        },
        "functional_roles": [],
        "operational_contract": {
            "trigger": rule["trigger"],
            "required_story_facts": rule["required_story_facts"],
            "director_decision": rule["director_decision"],
            "coverage": rule["coverage"],
            "blocking": rule["blocking"],
            "pacing": rule["pacing"],
            "edit_logic": rule["edit_logic"],
            "continuity": rule["continuity"],
            "audio_logic": rule["audio_logic"],
            "applicable_when": rule["applicable_when"],
            "not_applicable_when": rule["not_applicable_when"],
            "failure_modes": rule["failure_modes"],
            "ai_risk": rule["AI_risk"],
            "fallback": rule["fallback"],
        },
        "confidence": {
            "within_source": rule["within_source_confidence"],
            "transfer": rule["transfer_confidence"],
            "execution": rule["execution_confidence"],
        },
        "supporting_relations": [],
        "applicability_evidence": {
            "status": "UNKNOWN",
            "source_refs": [],
            "notes": "No natural-scene non-applicability boundary is authorized before human review.",
        },
        "unknown_dependencies": {
            "scene_problem": scene_problem["status"] == "UNKNOWN",
            "audio": rule["audio_logic"].get("status") != "AUDIO_OBSERVED",
            "functional_roles": not any(
                shot.get("abstract_role_labels") for shot in evidence["shots"]
            ),
            "natural_scene_boundary": True,
        },
        "counterexamples": [counterexample],
        "promotion": {
            "status": "BLOCKED_BY_UNKNOWN",
            "reasons": [
                "Canonical scene problem remains UNKNOWN.",
                "No evidence-backed functional role is available.",
                "Within-source, transfer and execution confidence remain UNKNOWN.",
                "No unrelated same-trigger verified counterexample is registered.",
            ],
            "verified_support_work_count": 1,
            "verified_same_trigger_counterexample_count": 0,
            "original_forward_test_count": 0,
            "original_forward_tests": [],
            "human_director_review": {
                "status": "NOT_APPROVED",
                "review_id": None,
                "source_ref": None,
            },
            "unknown_dependency_present": True,
        },
        "rights_boundary": {
            "evidence_lineage_only": True,
            "surface_copy_allowed": False,
            "runtime_authorized": False,
        },
        "legacy_lineage": rule["legacy_migration"],
    }


def build_index(sources: Iterable[Path] | None = None) -> dict[str, Any]:
    evidence_units = [_read_json(path) for path in (sources or discover_sources())]
    assignments: list[tuple[dict[str, Any], dict[str, Any], str, str]] = []
    family_works: dict[str, set[str]] = defaultdict(set)
    family_descriptions = {family_id: description for family_id, description, _ in FAMILY_TERMS}

    for evidence in evidence_units:
        for rule in evidence["candidate_rules"]:
            family_id, assignment_status = classify_family(rule)
            assignments.append((evidence, rule, family_id, assignment_status))
            family_works[family_id].add(evidence["work_id"])

    candidates = [
        _candidate_record(
            evidence,
            rule,
            family_id,
            assignment_status,
        )
        for evidence, rule, family_id, assignment_status in assignments
    ]
    candidates.sort(key=lambda item: item["candidate_rule_id"])

    family_members: dict[str, list[str]] = defaultdict(list)
    for candidate in candidates:
        family_members[candidate["canonical_rule_family"]].append(candidate["candidate_rule_id"])

    families = []
    for family_id in sorted(family_members):
        families.append(
            {
                "family_id": family_id,
                "description": family_descriptions.get(
                    family_id,
                    "Unclustered candidate retained pending human normalization.",
                ),
                "member_candidate_ids": family_members[family_id],
                "work_ids": sorted(family_works[family_id]),
                "assignment_status": (
                    "ROOT_REVIEWED_TEXTUAL_CLUSTER"
                    if family_id in family_descriptions
                    else "UNCLUSTERED_PENDING_HUMAN_REVIEW"
                ),
            }
        )

    return {
        "schema_version": "candidate-rule-index/0.1",
        "status": "EVIDENCE_LINEAGE_ONLY",
        "source_scene_count": len(evidence_units),
        "source_candidate_count": len(candidates),
        "normalization_policy": {
            "source_of_truth": "research/evidence/**/*.scene-evidence.json",
            "family_assignment_basis": "Root-reviewed deterministic textual mechanism clusters over canonical legacy lineage.",
            "promotion_boundary": "Family membership is not promotion. Every current candidate remains blocked while required evidence is UNKNOWN.",
            "surface_copy_allowed": False,
        },
        "families": families,
        "candidates": candidates,
    }


def build_matrix(index: dict[str, Any]) -> dict[str, Any]:
    by_id = {candidate["candidate_rule_id"]: candidate for candidate in index["candidates"]}
    families = []
    for family in index["families"]:
        members = [by_id[candidate_id] for candidate_id in family["member_candidate_ids"]]
        relations = [
            {
                "candidate_rule_id": member["candidate_rule_id"],
                "work_id": member["source"]["work_id"],
                "relation": member["relation_to_family"],
                "scene_problem_status": member["scene_problem"]["status"],
                "unknown_dependency_present": member["promotion"]["unknown_dependency_present"],
            }
            for member in members
        ]
        families.append(
            {
                "family_id": family["family_id"],
                "description": family["description"],
                "member_count": len(members),
                "grouped_work_count": len({member["source"]["work_id"] for member in members}),
                "relation_counts": dict(sorted(Counter(item["relation"] for item in relations).items())),
                "relations": relations,
                "verified_support_relation_ids": [],
                "verified_unrelated_same_trigger_counterexample_ids": [],
                "promotion_eligibility": "BLOCKED_BY_UNKNOWN",
                "blocked_reasons": [
                    "Every member retains an UNKNOWN canonical scene problem.",
                    "No member has evidence-backed functional roles.",
                    "No unrelated same-trigger verified counterexample is registered.",
                ],
            }
        )
    return {
        "schema_version": "cross-work-support-matrix/0.1",
        "status": "NO_RULE_PROMOTED",
        "candidate_index_path": "research/grammar/candidate_rule_index.json",
        "family_count": len(families),
        "candidate_count": len(index["candidates"]),
        "families": families,
    }


def render_matrix(matrix: dict[str, Any]) -> str:
    lines = [
        "# Cross-Work Support Matrix",
        "",
        "Status: NO_RULE_PROMOTED",
        "",
        "This is a deterministic review view of cross_work_support_matrix.json. Family membership records textual mechanism similarity only; it is not evidence of transfer validity.",
        "",
        "| Family | Members | Grouped works | Relations | Verified support relations | Same-trigger unrelated counterexamples | Eligibility |",
        "|---|---:|---:|---|---:|---:|---|",
    ]
    for family in matrix["families"]:
        relations = ", ".join(
            f"{key}={value}" for key, value in family["relation_counts"].items()
        )
        lines.append(
            f"| {family['family_id']} | {family['member_count']} | "
            f"{family['grouped_work_count']} | {relations or 'none'} | "
            f"{len(family['verified_support_relation_ids'])} | "
            f"{len(family['verified_unrelated_same_trigger_counterexample_ids'])} | "
            f"{family['promotion_eligibility']} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- All current candidates remain BLOCKED_BY_UNKNOWN.",
            "- Different-trigger comparisons and internal boundaries do not count as promotion counterexamples.",
            "- Work names and source-specific content remain evidence lineage, never runtime instructions.",
            "",
        ]
    )
    return "\n".join(lines)


def _serialized(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def build_all() -> tuple[dict[str, Any], dict[str, Any], str]:
    index = build_index()
    matrix = build_matrix(index)
    return index, matrix, render_matrix(matrix)


def _check(path: Path, expected: str) -> str | None:
    if not path.exists():
        return f"MISSING {path}"
    if path.read_text(encoding="utf-8") != expected:
        return f"DRIFT {path}"
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    index, matrix, matrix_markdown = build_all()
    expected = (
        (INDEX_PATH, _serialized(index)),
        (MATRIX_JSON_PATH, _serialized(matrix)),
        (MATRIX_MD_PATH, matrix_markdown),
    )
    if args.check:
        failures = [failure for path, text in expected if (failure := _check(path, text))]
        for failure in failures:
            print(failure, file=sys.stderr)
        if failures:
            return 1
        print(
            f"checked {index['source_candidate_count']} candidates in "
            f"{matrix['family_count']} textual mechanism families"
        )
        return 0
    GRAMMAR_ROOT.mkdir(parents=True, exist_ok=True)
    for path, text in expected:
        path.write_text(text, encoding="utf-8")
    print(
        f"built {index['source_candidate_count']} candidates in "
        f"{matrix['family_count']} textual mechanism families; 0 promoted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
