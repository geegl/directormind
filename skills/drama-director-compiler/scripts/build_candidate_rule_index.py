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
WAVE1_REVIEW_PATH = GRAMMAR_ROOT / "runtime_rule_promotion_wave1.review.json"
INTEGRATION_REVIEW_PATH = GRAMMAR_ROOT / "runtime_integration.review.json"
RELATION_REVIEW_ROOT = REPOSITORY_ROOT / "research" / "validation" / "relation-reviews"


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
    "BEAR-S01E07-REVIEW-001-BEAR-C02-RECURRING-ZONES": "CONTINUOUS-MOVEMENT-AND-OCCLUSION",
    "BEAR-S01E07-REVIEW-001-BEAR-C03-SUBTRACTIVE-AFTERMATH": "AFTERMATH-AND-TERMINAL-STATE",
    "BEAR-S02E07-TASK-CLOSED-LOOP-001-BEAR-S02-C03-DUAL-RESULT-RECEIPT": "RECEIVER-AND-REACTION-DISTRIBUTION",
    "BEAR-S02E07-TASK-CLOSED-LOOP-001-BEAR-S02-C04-TASK-LEDGER-OVER-CAMERA-CONTINUITY": "CONTINUITY-LEDGER-AND-VERSIONING",
    "CHERNOBYL-S01E05-HEARING-RECON-001-CHERNOBYL-CAND-RETURN-TO-FORMAL-ROOM-AFTER-PEAK-004": "AFTERMATH-AND-TERMINAL-STATE",
    "CHILDREN-OF-MEN-2006-MOVING-CAR-EXTERIOR-DISRUPTION-001-CHILDREN-CAND-APERTURE-EVENT-BEFORE-GROSS-BODY-RESPONSE-002": "ACTION-CAUSAL-CHAIN",
    "CHILDREN-OF-MEN-2006-MOVING-CAR-EXTERIOR-DISRUPTION-001-CHILDREN-CAND-CABIN-ZONES-AS-MOBILE-GEOGRAPHY-001": "CONTINUOUS-MOVEMENT-AND-OCCLUSION",
    "CITIZEN-KANE-1941-BREAKFAST-MONTAGE-001-CK-C01-INVARIANT-SPACE-MULTICHANNEL-DELTA": "CONTINUITY-LEDGER-AND-VERSIONING",
    "CITIZEN-KANE-1941-BREAKFAST-MONTAGE-001-CK-C02-REPEATED-BRIDGE-AS-ELLIPSIS-PUNCTUATION": "STATE-CHANGE-EDITING",
    "DM-ANDOR-S01E10-SEL-001-ANDOR-W4-C01": "SPATIAL-REGISTRATION-AND-RESET",
    "DM-EVID-HH-S01E06-ENSEMBLE-CONTINUOUS-REFRAMING-V0.1-HILL-HOUSE-ECR-C01": "CONTINUOUS-MOVEMENT-AND-OCCLUSION",
    "DM-EVID-HH-S01E06-ENSEMBLE-CONTINUOUS-REFRAMING-V0.1-HILL-HOUSE-ECR-C02": "CONTINUOUS-MOVEMENT-AND-OCCLUSION",
    "HOUSE-OF-THE-DRAGON-S01E08-THRONE-ROOM-INGRESS-TO-SEATED-STATE-001-HOTD-CAND-MAKE-ASSISTANCE-AND-OBJECT-STATES-COMPLETE-003": "ACTION-CAUSAL-CHAIN",
    "HOUSE-OF-THE-DRAGON-S01E08-THRONE-ROOM-INGRESS-TO-SEATED-STATE-001-HOTD-CAND-PUNCTUATE-LONG-AXIS-TRAVEL-002": "THRESHOLD-AND-ROUTE-CONTINUITY",
    "KNIVES-OUT-2019-WILL-READING-001-KNIVES-C02-DISTRIBUTE-SCREEN-OWNERSHIP-WHEN-BODIES-DIVERGE": "RECEIVER-AND-REACTION-DISTRIBUTION",
    "KNIVES-OUT-2019-WILL-READING-001-KNIVES-C03-SEATED-TO-STANDING-DENSITY-LEDGER": "SPATIAL-REGISTRATION-AND-RESET",
    "MARRIAGE-STORY-2019-APARTMENT-SEQUENCE-001-MS-APT-C02-STABLE-SEAT-ANCHORS-CARRY-DENSE-ALTERNATION": "AXIS-AND-COVERAGE-GRAMMAR",
    "MARRIAGE-STORY-2019-APARTMENT-SEQUENCE-001-MS-APT-C03-MOVEMENT-REOPENS-GEOMETRY-AND-SCREEN-OWNERSHIP": "SPATIAL-REGISTRATION-AND-RESET",
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
    "THE-SOCIAL-NETWORK-2010-OPENING-TWO-PERSON-EXCHANGE-001-TSN-C04-SHARED-FIRST-DEPARTURE-THEN-ISOLATE-SECOND-OCCUPANCY-CHANGE": "SPATIAL-REGISTRATION-AND-RESET",
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
            "audio_dependency": rule["audio_dependency"],
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
            "functional_roles": True,
            "natural_scene_boundary": True,
        },
        "counterexamples": [counterexample],
        "promotion": {
            "status": "EVIDENCE_GAP_PENDING",
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
        "runtime_integration": {},
        "rights_boundary": {
            "evidence_lineage_only": True,
            "surface_copy_allowed": False,
            "runtime_authorized": False,
        },
        "legacy_lineage": rule["legacy_migration"],
    }


def _review_ref(record_id: str) -> str:
    return f"research/validation/relation-reviews/{record_id}.json"


def assert_runtime_review_lineage(
    review: dict[str, Any],
    candidate_authority: dict[str, dict[str, Any]],
) -> None:
    """Refuse to label relations video-verified unless the authority binds them."""
    reviews = {
        item["review_id"]: item
        for item in review.get("evidence_reviews", [])
    }
    dispositions = {
        item["candidate_rule_id"]: item
        for item in review.get("candidate_dispositions", [])
    }

    def assert_relation(
        candidate_rule_id: str,
        source_refs: list[str],
        expected_status: str,
        target_rule_id: str,
        relation: dict[str, Any] | None = None,
    ) -> None:
        candidate = candidate_authority.get(candidate_rule_id)
        disposition = dispositions.get(candidate_rule_id)
        if candidate is None or disposition is None:
            raise ValueError(f"unknown reviewed relation candidate: {candidate_rule_id}")
        if (
            disposition.get("final_status") != expected_status
            or set(disposition.get("source_refs", [])) != set(source_refs)
            or disposition.get("target_rule_id") != target_rule_id
        ):
            raise ValueError(f"runtime relation does not match its final disposition: {candidate_rule_id}")
        moving_refs = {
            shot_id
            for review_id in disposition.get("review_ids", [])
            for shot_id in reviews.get(review_id, {}).get("moving_image_reviewed_shot_ids", [])
        }
        if not source_refs or not set(source_refs).issubset(moving_refs):
            raise ValueError(f"runtime relation lacks moving-image review: {candidate_rule_id}")
        canonical_refs = set(candidate.get("source", {}).get("evidence_shot_ids", []))
        if not set(source_refs).issubset(canonical_refs):
            raise ValueError(f"runtime relation leaves canonical candidate lineage: {candidate_rule_id}")
        if relation is not None:
            source = candidate["source"]
            if (
                relation.get("evidence_id") != source.get("evidence_id")
                or relation.get("work_id") != source.get("work_id")
            ):
                raise ValueError(f"runtime relation source metadata drift: {candidate_rule_id}")

    for spec in review.get("runtime_rule_specs", []):
        rule_id = spec["rule_id"]
        assert_relation(
            spec["candidate_rule_id"],
            spec["source_refs"],
            "POSITIVE_RUNTIME_RULE",
            rule_id,
        )
        moving_refs = {
            shot_id
            for review_id in dispositions[spec["candidate_rule_id"]].get("review_ids", [])
            for shot_id in reviews.get(review_id, {}).get("moving_image_reviewed_shot_ids", [])
        }
        for role in spec.get("functional_roles", []):
            role_refs = set(role.get("source_refs", []))
            if (
                not role_refs
                or role.get("shot_id") not in role_refs
                or not role_refs.issubset(set(spec["source_refs"]))
                or not role_refs.issubset(moving_refs)
            ):
                raise ValueError(f"runtime functional role lacks fresh source binding: {rule_id}")
        support_ids = {
            item["candidate_rule_id"]
            for item in review.get("candidate_dispositions", [])
            if item.get("final_status") == "SUPPORTING_EVIDENCE"
            and item.get("target_rule_id") == rule_id
        }
        relation_ids = {
            item["source_candidate_rule_id"]
            for item in spec.get("supporting_relations", [])
        }
        if not relation_ids or not relation_ids.issubset(support_ids):
            raise ValueError(f"runtime support relation set drift: {rule_id}")
        for relation in spec.get("supporting_relations", []):
            assert_relation(
                relation["source_candidate_rule_id"],
                relation["source_refs"],
                "SUPPORTING_EVIDENCE",
                rule_id,
                relation,
            )
        boundary_ids = {
            item["candidate_rule_id"]
            for item in review.get("candidate_dispositions", [])
            if item.get("final_status") == "BOUNDARY_OR_COUNTEREXAMPLE"
            and item.get("target_rule_id") == rule_id
        }
        counterexample = spec.get("counterexample", {})
        if counterexample.get("source_candidate_rule_id") not in boundary_ids:
            raise ValueError(f"runtime counterexample relation set drift: {rule_id}")
        assert_relation(
            counterexample["source_candidate_rule_id"],
            counterexample["source_refs"],
            "BOUNDARY_OR_COUNTEREXAMPLE",
            rule_id,
            counterexample,
        )


def _promoted_candidate_record(
    base: dict[str, Any],
    evidence: dict[str, Any],
    promotion: dict[str, Any],
) -> dict[str, Any]:
    support_records = [
        {
            "relation_id": item["relation_id"],
            "status": "VERIFIED",
            "relation": "SUPPORTS",
            "same_trigger_status": "VERIFIED_SAME_TRIGGER",
            "source_candidate_rule_id": item["source_candidate_rule_id"],
            "work_id": item["work_id"],
            "evidence_id": item["evidence_id"],
            "source_refs": item["source_refs"],
            "review_status": "ROOT_VIDEO_VERIFIED",
            "review_id": f"{item['relation_id']}-REVIEW",
            "review_ref": _review_ref(item["relation_id"]),
            "notes": item["notes"],
        }
        for item in promotion["supporting_relations"]
    ]
    counter = promotion["counterexample"]
    counter_record = {
        "counterexample_id": counter["relation_id"],
        "status": "VERIFIED",
        "same_trigger_status": "VERIFIED_SAME_TRIGGER",
        "relation": "NARROWS",
        "source_candidate_rule_id": counter["source_candidate_rule_id"],
        "work_id": counter["work_id"],
        "evidence_id": counter["evidence_id"],
        "source_refs": counter["source_refs"],
        "review_status": "ROOT_VIDEO_VERIFIED",
        "review_id": f"{counter['relation_id']}-REVIEW",
        "review_ref": _review_ref(counter["relation_id"]),
        "notes": counter["notes"],
    }
    roles = [
        {
            "appearance_id": role["appearance_id"],
            "functional_role": role["functional_role"],
            "status": "INFERRED",
            "source_refs": role["source_refs"],
        }
        for role in promotion["functional_roles"]
    ]
    contract = {
        "trigger": promotion["trigger"],
        "required_story_facts": promotion["required_story_facts"],
        "director_decision": promotion["director_decision"],
        "coverage": promotion["coverage"],
        "blocking": promotion["blocking"],
        "pacing": promotion["pacing"],
        "edit_logic": promotion["edit_logic"],
        "continuity": promotion["continuity"],
        "audio_logic": {
            "claim_id": f"{promotion['rule_id']}-AUDIO",
            "status": "UNKNOWN",
            "value": "This visual rule has no audio instruction or audio-dependent trigger.",
            "source_refs": [],
            "notes": "audio_dependency=false; semantic source audio remains unknown and is outside this rule.",
        },
        "audio_dependency": promotion["audio_dependency"],
        "applicable_when": promotion["applicable_when"],
        "not_applicable_when": promotion["not_applicable_when"],
        "failure_modes": promotion["failure_modes"],
        "ai_risk": promotion["ai_risk"],
        "fallback": promotion["fallback"],
    }
    forward_tests = [
        {
            "test_case_id": case_id,
            "status": "PASS",
            "source_ref": f"examples/forward-tests/{case_id}",
        }
        for case_id in (
            promotion["positive_forward_test_id"],
            promotion["boundary_forward_test_id"],
        )
    ]
    base.update(
        {
            "canonical_rule_family": promotion["family_id"],
            "family_assignment_status": "ROOT_REVIEWED_TEXTUAL_CLUSTER",
            "relation_to_family": "SUPPORTS",
            "scene_problem": {
                "primary": promotion["scene_problem"],
                "secondary": [],
                "status": "INFERRED",
                "source_refs": promotion["source_refs"],
                "lineage_label": _lineage_problem(evidence["scene_problem"]),
            },
            "functional_roles": roles,
            "operational_contract": contract,
            "confidence": promotion["confidence"],
            "supporting_relations": support_records,
            "applicability_evidence": {
                "status": "VERIFIED",
                "source_refs": evidence["boundary_evidence"]["source_refs"],
                "notes": (
                    "The canonical analytical interval has picture-observed endpoints whose "
                    "verified or explicitly internal status is recorded in Scene Evidence."
                ),
            },
            "unknown_dependencies": {
                "scene_problem": False,
                "audio": False,
                "functional_roles": False,
                "natural_scene_boundary": False,
            },
            "counterexamples": [counter_record],
            "promotion": {
                "status": "CROSS_WORK_SUPPORTED",
                "reasons": [
                    "Fresh picture review verifies the source mechanism, unrelated support, and a same-trigger boundary case.",
                    "Two project-original packages verify positive selection and non-applicability routing while creative review remains pending.",
                ],
                "verified_support_work_count": len({evidence["work_id"], *[item["work_id"] for item in promotion["supporting_relations"]]}),
                "verified_same_trigger_counterexample_count": 1,
                "original_forward_test_count": 2,
                "original_forward_tests": forward_tests,
                "human_director_review": {
                    "status": "NOT_APPROVED",
                    "review_id": None,
                    "source_ref": None,
                },
                "unknown_dependency_present": False,
            },
            "rights_boundary": {
                "evidence_lineage_only": True,
                "surface_copy_allowed": promotion["surface_copy_allowed"],
                "runtime_authorized": promotion["runtime_authorized"],
            },
        }
    )
    return base


def build_relation_reviews(index: dict[str, Any]) -> dict[Path, dict[str, Any]]:
    reviews: dict[Path, dict[str, Any]] = {}
    for candidate in index["candidates"]:
        records = [
            (record, "relation_id")
            for record in candidate["supporting_relations"]
            if record.get("status") == "VERIFIED"
        ] + [
            (record, "counterexample_id")
            for record in candidate["counterexamples"]
            if record.get("status") == "VERIFIED"
        ]
        for record, record_id_key in records:
            record_id = record[record_id_key]
            reviews[RELATION_REVIEW_ROOT / f"{record_id}.json"] = {
                "schema_version": "candidate-relation-review/0.1",
                "review_id": record["review_id"],
                "candidate_rule_id": candidate["candidate_rule_id"],
                "record_id": record_id,
                "status": record["review_status"],
                "relation": record["relation"],
                "same_trigger_status": record["same_trigger_status"],
                "source_candidate_rule_id": record["source_candidate_rule_id"],
                "work_id": record["work_id"],
                "evidence_id": record["evidence_id"],
                "source_refs": record["source_refs"],
            }
    return reviews


def build_index(sources: Iterable[Path] | None = None) -> dict[str, Any]:
    evidence_units = [_read_json(path) for path in (sources or discover_sources())]
    review = _read_json(INTEGRATION_REVIEW_PATH)
    promotions = {
        item["candidate_rule_id"]: item
        for item in review.get("runtime_rule_specs", [])
    }
    dispositions = {
        item["candidate_rule_id"]: item
        for item in review.get("candidate_dispositions", [])
    }
    if len(promotions) != len(review.get("runtime_rule_specs", [])):
        raise ValueError("duplicate promotion source candidate ID")
    if len(dispositions) != len(review.get("candidate_dispositions", [])):
        raise ValueError("duplicate runtime disposition candidate ID")
    assignments: list[tuple[dict[str, Any], dict[str, Any], str, str]] = []
    family_works: dict[str, set[str]] = defaultdict(set)
    family_descriptions = {family_id: description for family_id, description, _ in FAMILY_TERMS}

    for evidence in evidence_units:
        for rule in evidence["candidate_rules"]:
            family_id, assignment_status = classify_family(rule)
            assignments.append((evidence, rule, family_id, assignment_status))
            family_works[family_id].add(evidence["work_id"])

    candidate_authority = {
        rule["candidate_rule_id"]: {
            "source": {
                "work_id": evidence["work_id"],
                "evidence_id": evidence["evidence_id"],
                "evidence_shot_ids": rule["evidence_shot_ids"],
            }
        }
        for evidence, rule, _family_id, _assignment_status in assignments
    }
    assert_runtime_review_lineage(review, candidate_authority)

    candidates = []
    for evidence, rule, family_id, assignment_status in assignments:
        record = _candidate_record(evidence, rule, family_id, assignment_status)
        promotion = promotions.get(rule["candidate_rule_id"])
        if promotion is not None:
            if family_id != promotion["family_id"]:
                raise ValueError(
                    f"promotion family drift for {rule['candidate_rule_id']}: {family_id} != {promotion['family_id']}"
                )
            record = _promoted_candidate_record(record, evidence, promotion)
        disposition = dispositions.get(rule["candidate_rule_id"])
        if disposition is None:
            raise ValueError(f"missing runtime disposition: {rule['candidate_rule_id']}")
        record["runtime_integration"] = {
            key: disposition[key]
            for key in (
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
        }
        final_status = disposition["final_status"]
        if final_status == "REJECTED_WITH_REASON":
            record["promotion"]["status"] = "REJECTED"
        elif final_status == "EVIDENCE_GAP_PENDING":
            record["promotion"]["status"] = "EVIDENCE_GAP_PENDING"
        elif final_status == "EXISTING_MATERIAL_REVIEW_REQUIRED":
            record["promotion"]["status"] = "EXISTING_MATERIAL_REVIEW_REQUIRED"
        elif final_status != "POSITIVE_RUNTIME_RULE":
            record["promotion"]["status"] = "SINGLE_WORK_CANDIDATE"
        record["relation_to_family"] = {
            "SUPPORTING_EVIDENCE": "SUPPORTS",
            "BOUNDARY_OR_COUNTEREXAMPLE": "COUNTEREXAMPLE",
            "MERGED_DUPLICATE": "DUPLICATE",
            "REJECTED_WITH_REASON": "CONTRADICTS",
        }.get(final_status, record["relation_to_family"])
        candidates.append(record)
    unknown_promotions = sorted(set(promotions) - {item["candidate_rule_id"] for item in candidates})
    if unknown_promotions:
        raise ValueError(f"promotion sources not found: {unknown_promotions}")
    unknown_dispositions = sorted(
        set(dispositions) - {item["candidate_rule_id"] for item in candidates}
    )
    if unknown_dispositions:
        raise ValueError(f"runtime dispositions not found: {unknown_dispositions}")
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
        "status": review["declared_phase_status"],
        "source_scene_count": len(evidence_units),
        "source_candidate_count": len(candidates),
        "normalization_policy": {
            "source_of_truth": "research/evidence/**/*.scene-evidence.json",
            "family_assignment_basis": "Root-reviewed deterministic textual mechanism clusters over canonical legacy lineage.",
            "promotion_boundary": "Family membership is not promotion. Only candidates that pass fresh video review, cross-work support, same-trigger boundary, and original forward tests become runtime eligible.",
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
                "promotion_status": member["promotion"]["status"],
                "runtime_final_status": member["runtime_integration"]["final_status"],
                "runtime_effect_key": member["runtime_integration"]["runtime_effect_key"],
            }
            for member in members
        ]
        promoted = [
            member
            for member in members
            if member["promotion"]["status"] in {"CROSS_WORK_SUPPORTED", "GENERAL_DEFAULT"}
        ]
        support_ids = sorted(
            relation["relation_id"]
            for member in promoted
            for relation in member["supporting_relations"]
            if relation["status"] == "VERIFIED"
        )
        counterexample_ids = sorted(
            counterexample["counterexample_id"]
            for member in promoted
            for counterexample in member["counterexamples"]
            if counterexample["status"] == "VERIFIED"
        )
        families.append(
            {
                "family_id": family["family_id"],
                "description": family["description"],
                "member_count": len(members),
                "grouped_work_count": len({member["source"]["work_id"] for member in members}),
                "relation_counts": dict(sorted(Counter(item["relation"] for item in relations).items())),
                "relations": relations,
                "verified_support_relation_ids": support_ids,
                "verified_unrelated_same_trigger_counterexample_ids": counterexample_ids,
                "promotion_eligibility": (
                    "CROSS_WORK_SUPPORTED" if promoted else "PARTIAL_EVIDENCE_GAP"
                ),
                "blocked_reasons": (
                    []
                    if promoted
                    else [
                        "No member has passed all evidence, boundary, confidence, and forward-test gates.",
                    ]
                ),
            }
        )
    promoted_count = sum(
        candidate["promotion"]["status"] in {"CROSS_WORK_SUPPORTED", "GENERAL_DEFAULT"}
        for candidate in index["candidates"]
    )
    return {
        "schema_version": "cross-work-support-matrix/0.1",
        "status": "RUNTIME_RULES_AVAILABLE" if promoted_count else "NO_RULE_PROMOTED",
        "candidate_index_path": "research/grammar/candidate_rule_index.json",
        "family_count": len(families),
        "candidate_count": len(index["candidates"]),
        "families": families,
    }


def render_matrix(matrix: dict[str, Any]) -> str:
    lines = [
        "# Cross-Work Support Matrix",
        "",
        f"Status: {matrix['status']}",
        "",
        "This is a deterministic review view of cross_work_support_matrix.json. Family membership alone is not evidence of transfer validity; eligible rows cite fresh video review, support, boundary, and forward-test records.",
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
            "- Only POSITIVE_RUNTIME_RULE candidates are runtime authorized; every other candidate has a distinct runtime disposition or a precise EVIDENCE_GAP_PENDING entry.",
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
    relation_reviews = build_relation_reviews(index)
    expected = [
        (INDEX_PATH, _serialized(index)),
        (MATRIX_JSON_PATH, _serialized(matrix)),
        (MATRIX_MD_PATH, matrix_markdown),
        *[(path, _serialized(data)) for path, data in sorted(relation_reviews.items())],
    ]
    if args.check:
        failures = [failure for path, text in expected if (failure := _check(path, text))]
        actual_review_paths = set(RELATION_REVIEW_ROOT.glob("*.json")) if RELATION_REVIEW_ROOT.exists() else set()
        stale_reviews = sorted(actual_review_paths - set(relation_reviews))
        failures.extend(f"STALE {path}" for path in stale_reviews)
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
    RELATION_REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    for path, text in expected:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(
        f"built {index['source_candidate_count']} candidates in "
        f"{matrix['family_count']} textual mechanism families; "
        f"{sum(candidate['promotion']['status'] == 'CROSS_WORK_SUPPORTED' for candidate in index['candidates'])} promoted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
