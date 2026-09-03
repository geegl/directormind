#!/usr/bin/env python3
"""Regression tests for candidate normalization and promotion gates."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from collections import Counter
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from build_candidate_rule_index import (  # noqa: E402
    FAMILY_OVERRIDES,
    build_all,
    discover_sources,
    render_matrix,
)
from validate_candidate_rules import validate_repository  # noqa: E402


INDEX_PATH = REPO_ROOT / "research" / "grammar" / "candidate_rule_index.json"
MATRIX_PATH = REPO_ROOT / "research" / "grammar" / "cross_work_support_matrix.json"
MATRIX_MARKDOWN_PATH = MATRIX_PATH.with_suffix(".md")
SCHEMA_PATH = SKILL_ROOT / "references" / "candidate-director-rule.schema.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def issue_codes(report: dict) -> set[str]:
    return {issue["code"] for issue in report["issues"]}


class CandidateRuleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = read_json(INDEX_PATH)
        cls.matrix = read_json(MATRIX_PATH)
        cls.sources = [read_json(path) for path in discover_sources()]

    def validate_mutation(self, index: dict, matrix: dict | None = None) -> set[str]:
        report = validate_repository(index, matrix or copy.deepcopy(self.matrix))
        self.assertEqual(report["status"], "FAIL")
        return issue_codes(report)

    def candidate_in_family_with_at_least(self, work_count: int) -> tuple[dict, dict]:
        families = {
            family["family_id"]: family for family in self.index["families"]
        }
        for candidate in self.index["candidates"]:
            family = families[candidate["canonical_rule_family"]]
            if len(family["work_ids"]) >= work_count:
                return candidate, family
        self.fail(f"No family has at least {work_count} unrelated works")

    def test_schema_declares_strict_split_confidence_and_promotion_contract(self) -> None:
        schema = read_json(SCHEMA_PATH)
        self.assertFalse(schema["additionalProperties"])
        required = set(schema["required"])
        self.assertIn("legacy_lineage", required)
        self.assertIn("confidence", required)
        self.assertIn("supporting_relations", required)
        self.assertIn("applicability_evidence", required)
        self.assertIn("unknown_dependencies", required)
        self.assertIn("promotion", required)
        self.assertIn("runtime_integration", required)
        confidence = schema["$defs"]["confidence"]
        self.assertFalse(confidence["additionalProperties"])
        self.assertEqual(
            set(confidence["required"]),
            {"within_source", "transfer", "execution"},
        )
        self.assertEqual(
            set(schema["$defs"]["promotion"]["properties"]["status"]["enum"]),
            {
                "SINGLE_WORK_CANDIDATE",
                "CROSS_WORK_SUPPORTED",
                "GENERAL_DEFAULT",
                "REJECTED",
                "BLOCKED_BY_UNKNOWN",
                "EVIDENCE_GAP_PENDING",
            },
        )

    def test_repository_build_is_deterministic(self) -> None:
        index, matrix, markdown = build_all()
        self.assertEqual(index, self.index)
        self.assertEqual(matrix, self.matrix)
        self.assertEqual(markdown, MATRIX_MARKDOWN_PATH.read_text(encoding="utf-8"))
        self.assertEqual(render_matrix(self.matrix), markdown)

    def test_every_source_candidate_resolves_once_with_exact_lineage(self) -> None:
        source_rules = {}
        for evidence in self.sources:
            for rule in evidence["candidate_rules"]:
                source_rules[rule["candidate_rule_id"]] = (evidence, rule)
        candidates = {
            candidate["candidate_rule_id"]: candidate
            for candidate in self.index["candidates"]
        }
        self.assertEqual(len(self.sources), 31)
        self.assertEqual(len(source_rules), 124)
        self.assertEqual(set(candidates), set(source_rules))
        for candidate_id, candidate in candidates.items():
            evidence, rule = source_rules[candidate_id]
            self.assertEqual(candidate["legacy_lineage"], rule["legacy_migration"])
            self.assertEqual(candidate["source"]["work_id"], evidence["work_id"])
            self.assertEqual(candidate["source"]["evidence_id"], evidence["evidence_id"])
            self.assertEqual(candidate["source"]["evidence_shot_ids"], rule["evidence_shot_ids"])

    def test_each_candidate_has_one_family_and_no_family_is_promotion_evidence(self) -> None:
        membership = Counter(
            candidate_id
            for family in self.index["families"]
            for candidate_id in family["member_candidate_ids"]
        )
        self.assertEqual(len(self.index["families"]), 16)
        self.assertEqual(set(membership.values()), {1})
        self.assertEqual(set(membership), {
            candidate["candidate_rule_id"] for candidate in self.index["candidates"]
        })
        self.assertIn("not promotion", self.index["normalization_policy"]["promotion_boundary"].lower())

    def test_exhaustive_dispositions_replace_blocked_as_the_runtime_authority(self) -> None:
        candidates = self.index["candidates"]
        self.assertTrue(candidates)
        review = read_json(REPO_ROOT / "research" / "grammar" / "runtime_integration.review.json")
        expected = {
            item["candidate_rule_id"]: item["final_status"]
            for item in review["candidate_dispositions"]
        }
        self.assertEqual(
            {candidate["candidate_rule_id"]: candidate["runtime_integration"]["final_status"] for candidate in candidates},
            expected,
        )
        self.assertNotIn("BLOCKED_BY_UNKNOWN", Counter(candidate["promotion"]["status"] for candidate in candidates))
        self.assertEqual(
            sum(candidate["rights_boundary"]["runtime_authorized"] for candidate in candidates),
            sum(status == "POSITIVE_RUNTIME_RULE" for status in expected.values()),
        )
        self.assertEqual(
            {tuple(candidate["confidence"]) for candidate in candidates},
            {("execution", "transfer", "within_source")},
        )
        promoted = [candidate for candidate in candidates if candidate["promotion"]["status"] == "CROSS_WORK_SUPPORTED"]
        pending = [candidate for candidate in candidates if candidate["runtime_integration"]["final_status"] == "EVIDENCE_GAP_PENDING"]
        self.assertTrue(all(not any(candidate["unknown_dependencies"].values()) for candidate in promoted))
        self.assertTrue(all("UNKNOWN" not in candidate["confidence"].values() for candidate in promoted))
        self.assertTrue(all(any(candidate["unknown_dependencies"].values()) for candidate in pending))

    def test_only_positive_runtime_sources_gain_reviewed_problem_and_roles(self) -> None:
        reviewed_ids = {
            candidate["source"]["evidence_id"]
            for candidate in self.index["candidates"]
            if candidate["promotion"]["status"] == "CROSS_WORK_SUPPORTED"
        }
        for evidence in self.sources:
            problem = evidence["scene_problem"]
            self.assertLessEqual(len(problem["secondary"]), 2)
            if evidence["evidence_id"] in reviewed_ids:
                self.assertEqual(problem["status"], "INFERRED")
                self.assertTrue(problem["source_refs"])
                self.assertTrue(any(shot["abstract_role_labels"] for shot in evidence["shots"]))
            else:
                self.assertEqual(problem["status"], "UNKNOWN")
                self.assertEqual(problem["source_refs"], [])
        promoted = [candidate for candidate in self.index["candidates"] if candidate["promotion"]["status"] == "CROSS_WORK_SUPPORTED"]
        review = read_json(REPO_ROOT / "research" / "grammar" / "runtime_integration.review.json")
        self.assertEqual(len(promoted), len(review["runtime_rule_specs"]))
        self.assertTrue(all(candidate["functional_roles"] for candidate in promoted))
        self.assertTrue(all(candidate["scene_problem"]["status"] == "INFERRED" for candidate in promoted))

    def test_repository_candidate_validation_passes(self) -> None:
        report = validate_repository(copy.deepcopy(self.index), copy.deepcopy(self.matrix))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["candidate_count"], 124)
        self.assertEqual(report["family_count"], 16)
        self.assertEqual(
            report["runtime_authorized_count"],
            sum(candidate["rights_boundary"]["runtime_authorized"] for candidate in self.index["candidates"]),
        )
        self.assertEqual(report["error_count"], 0)

    def test_unknown_candidate_cannot_be_promoted(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["promotion"]["status"] = "SINGLE_WORK_CANDIDATE"
        self.assertIn("PROMOTION-UNKNOWN-LEAK", self.validate_mutation(index))

    def test_explicit_unknown_axes_cannot_be_hidden_from_promotion(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["promotion"]["unknown_dependency_present"] = False
        codes = self.validate_mutation(index)
        self.assertIn("PROMOTION-UNKNOWN-FLAG-DRIFT", codes)

    def test_unknown_audio_role_and_boundary_each_block_promotion(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["promotion"]["status"] = "CROSS_WORK_SUPPORTED"
        candidate["rights_boundary"]["runtime_authorized"] = True
        codes = self.validate_mutation(index)
        self.assertIn("PROMOTION-AUDIO-UNKNOWN", codes)
        self.assertIn("PROMOTION-ROLE-UNKNOWN", codes)
        self.assertIn("PROMOTION-NATURAL-BOUNDARY-UNKNOWN", codes)

    def test_cross_work_promotion_requires_verified_counterexample(self) -> None:
        source_candidate, _family = self.candidate_in_family_with_at_least(2)
        index = copy.deepcopy(self.index)
        candidate = next(
            item for item in index["candidates"]
            if item["candidate_rule_id"] == source_candidate["candidate_rule_id"]
        )
        candidate["scene_problem"]["status"] = "INFERRED"
        candidate["scene_problem"]["source_refs"] = [candidate["source"]["evidence_shot_ids"][0]]
        candidate["confidence"] = {
            "within_source": "LOW",
            "transfer": "LOW",
            "execution": "LOW",
        }
        candidate["promotion"].update(
            status="CROSS_WORK_SUPPORTED",
        )
        candidate["rights_boundary"]["runtime_authorized"] = True
        self.assertIn("PROMOTION-CROSS-WORK-GATE", self.validate_mutation(index))

    def test_single_work_candidate_stays_outside_runtime_authorization(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["promotion"].update(
            status="SINGLE_WORK_CANDIDATE",
        )
        candidate["rights_boundary"]["runtime_authorized"] = False
        allowed_codes = self.validate_mutation(index)
        self.assertNotIn("PROMOTION-RUNTIME-AUTH", allowed_codes)
        candidate["rights_boundary"]["runtime_authorized"] = True
        self.assertIn("PROMOTION-RUNTIME-AUTH", self.validate_mutation(index))

    def test_unknown_counterexample_cannot_be_counted_as_verified(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["promotion"]["verified_same_trigger_counterexample_count"] = 1
        self.assertIn("PROMOTION-COUNTEREXAMPLE-COUNT", self.validate_mutation(index))

    def test_general_default_requires_forward_tests_and_human_approval(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["promotion"].update(
            status="GENERAL_DEFAULT",
        )
        candidate["rights_boundary"]["runtime_authorized"] = True
        self.assertIn("PROMOTION-GENERAL-GATE", self.validate_mutation(index))

    def test_non_unknown_functional_role_requires_provenance(self) -> None:
        index = copy.deepcopy(self.index)
        index["candidates"][0]["functional_roles"] = [
            {
                "appearance_id": "APPEARANCE-1",
                "functional_role": "authority",
                "status": "INFERRED",
                "source_refs": [],
            }
        ]
        self.assertIn("ROLE-PROVENANCE-MISSING", self.validate_mutation(index))

    def test_unknown_role_cannot_carry_hardened_role_name(self) -> None:
        index = copy.deepcopy(self.index)
        index["candidates"][0]["functional_roles"] = [
            {
                "appearance_id": "APPEARANCE-1",
                "functional_role": "authority",
                "status": "UNKNOWN",
                "source_refs": [],
            }
        ]
        self.assertIn("ROLE-UNKNOWN-HARDENED", self.validate_mutation(index))

    def test_source_lineage_drift_is_rejected(self) -> None:
        index = copy.deepcopy(self.index)
        index["candidates"][0]["legacy_lineage"]["trigger"] += " drift"
        self.assertIn("CANDIDATE-LEGACY-DRIFT", self.validate_mutation(index))

    def test_support_matrix_drift_is_rejected(self) -> None:
        matrix = copy.deepcopy(self.matrix)
        matrix["families"][0]["member_count"] += 1
        report = validate_repository(copy.deepcopy(self.index), matrix)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("MATRIX-MEMBER-COUNT", issue_codes(report))
        self.assertIn("MATRIX-NONDETERMINISTIC", issue_codes(report))

    def test_family_work_count_cannot_be_used_as_support_count(self) -> None:
        source_candidate, family = self.candidate_in_family_with_at_least(3)
        index = copy.deepcopy(self.index)
        candidate = next(
            item for item in index["candidates"]
            if item["candidate_rule_id"] == source_candidate["candidate_rule_id"]
        )
        self.assertEqual(candidate["supporting_relations"], [])
        candidate["promotion"]["verified_support_work_count"] = len(family["work_ids"])
        codes = self.validate_mutation(index)
        self.assertIn("PROMOTION-WORK-COUNT", codes)

    def test_fabricated_support_relation_does_not_count(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["supporting_relations"] = [
            {
                "relation_id": "FAKE-SUPPORT-001",
                "status": "VERIFIED",
                "relation": "SUPPORTS",
                "same_trigger_status": "VERIFIED_SAME_TRIGGER",
                "source_candidate_rule_id": "MISSING-CANDIDATE",
                "work_id": "MISSING-WORK",
                "evidence_id": "MISSING-EVIDENCE",
                "source_refs": ["MISSING-SHOT"],
                "review_status": "HUMAN_VERIFIED",
                "review_id": "FAKE-REVIEW-001",
                "review_ref": "research/validation/missing-review.md",
                "notes": "Unresolved test relation.",
            }
        ]
        candidate["promotion"]["verified_support_work_count"] = 2
        codes = self.validate_mutation(index)
        self.assertIn("SUPPORT-SOURCE-MISSING", codes)
        self.assertIn("PROMOTION-WORK-COUNT", codes)

    def test_fabricated_verified_counterexample_does_not_count(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["counterexamples"] = [
            {
                "counterexample_id": "FAKE-COUNTEREXAMPLE-001",
                "status": "VERIFIED",
                "same_trigger_status": "VERIFIED_SAME_TRIGGER",
                "relation": "COUNTEREXAMPLE",
                "source_candidate_rule_id": "MISSING-CANDIDATE",
                "work_id": "MISSING-WORK",
                "evidence_id": "MISSING-EVIDENCE",
                "source_refs": ["MISSING-SHOT"],
                "review_status": "HUMAN_VERIFIED",
                "review_id": "FAKE-REVIEW-001",
                "review_ref": "research/validation/missing-review.md",
                "notes": "Unresolved test contrary case.",
            }
        ]
        candidate["promotion"]["verified_same_trigger_counterexample_count"] = 1
        codes = self.validate_mutation(index)
        self.assertIn("COUNTEREXAMPLE-SOURCE-MISSING", codes)
        self.assertIn("PROMOTION-COUNTEREXAMPLE-COUNT", codes)

    def test_existing_sources_still_require_a_named_relation_review(self) -> None:
        source_candidate, _family = self.candidate_in_family_with_at_least(2)
        index = copy.deepcopy(self.index)
        candidate = next(
            item for item in index["candidates"]
            if item["candidate_rule_id"] == source_candidate["candidate_rule_id"]
        )
        target = next(
            item for item in index["candidates"]
            if item["canonical_rule_family"] == candidate["canonical_rule_family"]
            and item["source"]["work_id"] != candidate["source"]["work_id"]
        )
        target_ref = target["source"]["evidence_shot_ids"][0]
        candidate["supporting_relations"] = [
            {
                "relation_id": "UNREVIEWED-SUPPORT-001",
                "status": "VERIFIED",
                "relation": "SUPPORTS",
                "same_trigger_status": "VERIFIED_SAME_TRIGGER",
                "source_candidate_rule_id": target["candidate_rule_id"],
                "work_id": target["source"]["work_id"],
                "evidence_id": target["source"]["evidence_id"],
                "source_refs": [target_ref],
                "review_status": "HUMAN_VERIFIED",
                "review_id": "MISSING-REVIEW-001",
                "review_ref": "research/validation/missing-review.md",
                "notes": "Structurally linked but not independently reviewed.",
            }
        ]
        candidate["promotion"]["verified_support_work_count"] = 2
        codes = self.validate_mutation(index)
        self.assertIn("RELATION-REVIEW-REF", codes)
        self.assertIn("PROMOTION-WORK-COUNT", codes)

    def test_review_and_forward_paths_cannot_traverse_to_unrelated_files(self) -> None:
        source_candidate, _family = self.candidate_in_family_with_at_least(2)
        index = copy.deepcopy(self.index)
        candidate = next(
            item for item in index["candidates"]
            if item["candidate_rule_id"] == source_candidate["candidate_rule_id"]
        )
        target = next(
            item for item in index["candidates"]
            if item["canonical_rule_family"] == candidate["canonical_rule_family"]
            and item["source"]["work_id"] != candidate["source"]["work_id"]
        )
        target_ref = target["source"]["evidence_shot_ids"][0]
        traversal_review = (
            "research/validation/relation-reviews/../../../skills/"
            "drama-director-compiler/scripts/build_candidate_rule_index.py"
        )
        candidate["supporting_relations"] = [
            {
                "relation_id": "TRAVERSAL-SUPPORT-001",
                "status": "VERIFIED",
                "relation": "SUPPORTS",
                "same_trigger_status": "VERIFIED_SAME_TRIGGER",
                "source_candidate_rule_id": target["candidate_rule_id"],
                "work_id": target["source"]["work_id"],
                "evidence_id": target["source"]["evidence_id"],
                "source_refs": [target_ref],
                "review_status": "HUMAN_VERIFIED",
                "review_id": "TRAVERSAL-REVIEW-001",
                "review_ref": traversal_review,
                "notes": "Traversal must never count as relation review.",
            }
        ]
        candidate["promotion"].update(
            verified_support_work_count=2,
            original_forward_test_count=2,
            original_forward_tests=[
                {
                    "test_case_id": "TRAVERSAL-FORWARD-001",
                    "status": "PASS",
                    "source_ref": (
                        "examples/forward-tests/../../research/validation/"
                        "PHASE_2_FAMILY_ASSIGNMENT_REVIEW.md"
                    ),
                },
                {
                    "test_case_id": "TRAVERSAL-FORWARD-002",
                    "status": "PASS",
                    "source_ref": (
                        "examples/forward-tests/../../research/validation/"
                        "VALIDATION_CLAIM_REGISTER.md"
                    ),
                },
            ],
            human_director_review={
                "status": "APPROVED",
                "review_id": "TRAVERSAL-DIRECTOR-REVIEW-001",
                "source_ref": (
                    "research/validation/director-reviews/../../../skills/"
                    "drama-director-compiler/scripts/build_candidate_rule_index.py"
                ),
            },
        )
        codes = self.validate_mutation(index)
        self.assertIn("RELATION-REVIEW-REF", codes)
        self.assertIn("FORWARD-TEST-REF", codes)
        self.assertIn("HUMAN-REVIEW-REF", codes)
        self.assertIn("PROMOTION-WORK-COUNT", codes)
        self.assertIn("PROMOTION-FORWARD-TEST-COUNT", codes)

    def test_fake_role_and_scene_problem_refs_are_rejected(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["scene_problem"].update(
            status="INFERRED",
            source_refs=["MISSING-SHOT"],
        )
        candidate["functional_roles"] = [
            {
                "appearance_id": "APPEARANCE-1",
                "functional_role": "authority",
                "status": "INFERRED",
                "source_refs": ["MISSING-SHOT"],
            }
        ]
        codes = self.validate_mutation(index)
        self.assertIn("SCENE-PROBLEM-PROVENANCE", codes)
        self.assertIn("ROLE-PROVENANCE-MISSING", codes)

    def test_fake_audio_observation_and_arbitrary_boundary_text_are_rejected(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["operational_contract"]["audio_logic"].update(
            status="AUDIO_OBSERVED",
            source_refs=["MISSING-AUDIO"],
        )
        candidate["operational_contract"]["not_applicable_when"] = [
            "Arbitrary text must not prove a natural-scene boundary."
        ]
        candidate["promotion"]["unknown_dependency_present"] = False
        codes = self.validate_mutation(index)
        self.assertIn("AUDIO-PROVENANCE-STATUS", codes)
        self.assertIn("AUDIO-PROVENANCE-REFS", codes)
        self.assertIn("PROMOTION-UNKNOWN-FLAG-DRIFT", codes)
        self.assertTrue(candidate["unknown_dependencies"]["natural_scene_boundary"])

    def test_approval_and_forward_counts_require_existing_refs(self) -> None:
        index = copy.deepcopy(self.index)
        candidate = index["candidates"][0]
        candidate["promotion"].update(
            original_forward_test_count=2,
            original_forward_tests=[],
            human_director_review={
                "status": "APPROVED",
                "review_id": None,
                "source_ref": None,
            },
        )
        codes = self.validate_mutation(index)
        self.assertIn("PROMOTION-FORWARD-TEST-COUNT", codes)
        self.assertIn("HUMAN-REVIEW-REF", codes)

    def test_candidate_schema_is_applied_to_instances(self) -> None:
        index = copy.deepcopy(self.index)
        del index["candidates"][0]["promotion"]["original_forward_tests"]
        self.assertIn("SCHEMA-REQUIRED", self.validate_mutation(index))

    def test_hypothetical_martian_counterexample_is_not_verified(self) -> None:
        candidate = next(
            item for item in self.index["candidates"]
            if item["candidate_rule_id"].endswith("MARTIAN-MSOSES-C02")
        )
        self.assertIn("hypothetical", candidate["counterexamples"][0]["notes"].lower())
        self.assertEqual(candidate["counterexamples"][0]["status"], "UNKNOWN")
        self.assertEqual(candidate["counterexamples"][0]["same_trigger_status"], "UNKNOWN")

    def test_reviewed_family_overrides_cover_known_keyword_collisions(self) -> None:
        expected = {
            "A-QUIET-PLACE-2018-PARALLEL-BODY-STATE-RADIAL-LIGHT-001-AQP-C02-GROUP-PARALLEL-THREADS-BY-VISIBLE-STATE-CHANGE": "MULTI-THREAD-STATE-INTERCUT",
            "CITIZEN-KANE-1941-BREAKFAST-MONTAGE-001-CK-C02-REPEATED-BRIDGE-AS-ELLIPSIS-PUNCTUATION": "STATE-CHANGE-EDITING",
            "BEAR-S01E07-REVIEW-001-BEAR-C03-SUBTRACTIVE-AFTERMATH": "AFTERMATH-AND-TERMINAL-STATE",
            "WIRE-S01E04-OLD-CASES-001-WIRE-C04-LONG-TAKE-WHEN-CONTINUITY-IS-THE-PROOF": "CONTINUOUS-MOVEMENT-AND-OCCLUSION",
            "SUCCESSION-S01E06-BOARD-VOTE-001-SUC-C01": "RECEIVER-AND-REACTION-DISTRIBUTION",
            "SUCCESSION-S01E06-BOARD-VOTE-001-SUC-C02": "MULTI-THREAD-STATE-INTERCUT",
            "SUCCESSION-S01E06-BOARD-VOTE-001-SUC-C03": "RECEIVER-AND-REACTION-DISTRIBUTION",
            "SUCCESSION-S01E06-BOARD-VOTE-001-SUC-C04": "THRESHOLD-AND-ROUTE-CONTINUITY",
        }
        by_id = {
            candidate["candidate_rule_id"]: candidate
            for candidate in self.index["candidates"]
        }
        for candidate_id, family_id in expected.items():
            self.assertEqual(by_id[candidate_id]["canonical_rule_family"], family_id)
            self.assertEqual(
                by_id[candidate_id]["family_assignment_status"],
                "ROOT_REVIEWED_TEXTUAL_CLUSTER",
            )

    def test_family_review_covers_every_candidate_and_all_reviewed_overrides(self) -> None:
        candidate_ids = {
            candidate["candidate_rule_id"] for candidate in self.index["candidates"]
        }
        self.assertEqual(len(FAMILY_OVERRIDES), 46)
        self.assertLessEqual(set(FAMILY_OVERRIDES), candidate_ids)
        self.assertEqual(
            {
                candidate["family_assignment_status"]
                for candidate in self.index["candidates"]
            },
            {"ROOT_REVIEWED_TEXTUAL_CLUSTER"},
        )


if __name__ == "__main__":
    unittest.main()
