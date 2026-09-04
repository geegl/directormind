#!/usr/bin/env python3
"""Exhaustive runtime-integration authority tests."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "drama-director-compiler"
SCRIPT_ROOT = SKILL_ROOT / "scripts"
REVIEW_PATH = REPO_ROOT / "research" / "grammar" / "runtime_integration.review.json"
CANDIDATE_INDEX_PATH = REPO_ROOT / "research" / "grammar" / "candidate_rule_index.json"
SCHEMA_PATH = SKILL_ROOT / "references" / "runtime-integration-review.schema.json"

sys.path.insert(0, str(SCRIPT_ROOT))
from build_candidate_rule_index import assert_runtime_review_lineage  # noqa: E402
from validate_runtime_integration_review import validate  # noqa: E402


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def issue_codes(report: dict) -> set[str]:
    return {issue["code"] for issue in report["issues"]}


class RuntimeIntegrationReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.review = read_json(REVIEW_PATH)
        cls.candidate_by_id = {
            item["candidate_rule_id"]: item
            for item in read_json(CANDIDATE_INDEX_PATH)["candidates"]
        }
        cls.schema = read_json(SCHEMA_PATH)

    def validate_copy(self, review: dict | None = None) -> dict:
        return validate(copy.deepcopy(review or self.review), copy.deepcopy(self.schema))

    def test_repository_authority_has_exact_closed_corpus_sets(self) -> None:
        report = self.validate_copy()
        pending_statuses = {
            "EVIDENCE_GAP_PENDING",
            "EXISTING_MATERIAL_REVIEW_REQUIRED",
        }
        final_count = sum(
            item["final_status"] not in pending_statuses
            for item in self.review["candidate_dispositions"]
        )
        pending_count = sum(
            item["final_status"] in pending_statuses
            for item in self.review["candidate_dispositions"]
        )
        existing_review_count = sum(
            item["final_status"] == "EXISTING_MATERIAL_REVIEW_REQUIRED"
            for item in self.review["candidate_dispositions"]
        )
        rule_count = len(self.review["runtime_rule_specs"])
        self.assertEqual(report["status"], "PASS", report["issues"])
        self.assertEqual(report["source_disposition_count"], 33)
        self.assertEqual(report["evidence_review_count"], 31)
        self.assertEqual(report["candidate_disposition_count"], 124)
        self.assertEqual(report["candidate_final_disposition_count"], final_count)
        self.assertEqual(report["unresolved_candidate_count"], pending_count)
        self.assertEqual(
            report["existing_material_review_required_count"],
            existing_review_count,
        )
        self.assertEqual(final_count + pending_count, 124)
        self.assertEqual(report["positive_runtime_rule_count"], rule_count)
        self.assertEqual(report["phase_status"], "IN_PROGRESS")

    def test_source_register_rows_cannot_be_swapped(self) -> None:
        review = copy.deepcopy(self.review)
        review["source_dispositions"][0]["evidence_id"], review["source_dispositions"][1]["evidence_id"] = (
            review["source_dispositions"][1]["evidence_id"],
            review["source_dispositions"][0]["evidence_id"],
        )
        self.assertIn("INTEGRATION-SOURCE-REGISTER-BINDING", issue_codes(self.validate_copy(review)))

    def test_missing_duplicate_and_foreign_candidates_fail(self) -> None:
        for mutation in ("missing", "duplicate", "foreign"):
            with self.subTest(mutation=mutation):
                review = copy.deepcopy(self.review)
                if mutation == "missing":
                    review["candidate_dispositions"].pop()
                elif mutation == "duplicate":
                    review["candidate_dispositions"].append(copy.deepcopy(review["candidate_dispositions"][0]))
                else:
                    review["candidate_dispositions"][0]["candidate_rule_id"] = "FOREIGN-CANDIDATE"
                self.assertIn("INTEGRATION-CANDIDATE-SET", issue_codes(self.validate_copy(review)))

    def test_candidate_family_and_evidence_are_authoritative(self) -> None:
        for key, value in (("family_id", "FOREIGN-FAMILY"), ("evidence_id", "FOREIGN-EVIDENCE")):
            with self.subTest(key=key):
                review = copy.deepcopy(self.review)
                review["candidate_dispositions"][0][key] = value
                self.assertIn("INTEGRATION-CANDIDATE-BINDING", issue_codes(self.validate_copy(review)))

    def test_fresh_source_ref_and_timecode_are_bound(self) -> None:
        review = copy.deepcopy(self.review)
        positive = next(item for item in review["candidate_dispositions"] if item["final_status"] == "POSITIVE_RUNTIME_RULE")
        positive["source_refs"] = ["MISSING-SHOT"]
        self.assertIn("INTEGRATION-CANDIDATE-SOURCE-REF", issue_codes(self.validate_copy(review)))
        review = copy.deepcopy(self.review)
        review["evidence_reviews"][0]["reviewed_shots"][0]["start"]["seconds"] += 1
        self.assertIn("INTEGRATION-REVIEW-TIMECODE", issue_codes(self.validate_copy(review)))

    def test_complete_cannot_hide_pending_or_gap(self) -> None:
        review = copy.deepcopy(self.review)
        review["declared_phase_status"] = "COMPLETE"
        report = self.validate_copy(review)
        self.assertIn("INTEGRATION-FALSE-COMPLETE", issue_codes(report))

    def test_final_disposition_cannot_use_partial_picture_review(self) -> None:
        review = copy.deepcopy(self.review)
        final = next(item for item in review["candidate_dispositions"] if item["final_status"] == "POSITIVE_RUNTIME_RULE")
        review_id = final["review_ids"][0]
        source_review = next(item for item in review["evidence_reviews"] if item["review_id"] == review_id)
        source_review["moving_image_reviewed_shot_ids"] = []
        self.assertIn("INTEGRATION-FINAL-MOVING-REVIEW", issue_codes(self.validate_copy(review)))

    def test_final_disposition_cannot_swap_away_from_functional_role_refs(self) -> None:
        review = copy.deepcopy(self.review)
        reviews = {item["review_id"]: item for item in review["evidence_reviews"]}
        final = next(
            item
            for item in review["candidate_dispositions"]
            if item["final_status"] == "POSITIVE_RUNTIME_RULE"
            and any(
                shot["shot_id"] not in item["source_refs"]
                for shot in reviews[item["review_ids"][0]]["reviewed_shots"]
            )
        )
        source_review = reviews[final["review_ids"][0]]
        replacement = next(
            item["shot_id"]
            for item in source_review["reviewed_shots"]
            if item["shot_id"] not in final["source_refs"]
        )
        final["source_refs"] = [replacement]
        spec = next(item for item in review["runtime_rule_specs"] if item["candidate_rule_id"] == final["candidate_rule_id"])
        spec["source_refs"] = [replacement]
        self.assertIn("INTEGRATION-FUNCTIONAL-ROLE-REF", issue_codes(self.validate_copy(review)))

    def test_supplemental_context_cannot_replace_canonical_candidate_lineage(self) -> None:
        review = copy.deepcopy(self.review)
        reviews = {item["review_id"]: item for item in review["evidence_reviews"]}
        final = next(
            item
            for item in review["candidate_dispositions"]
            if item["final_status"] == "POSITIVE_RUNTIME_RULE"
            and any(
                shot_id
                not in self.candidate_by_id[item["candidate_rule_id"]]["source"]["evidence_shot_ids"]
                for shot_id in reviews[item["review_ids"][0]]["moving_image_reviewed_shot_ids"]
            )
        )
        source_review = reviews[final["review_ids"][0]]
        canonical_refs = set(self.candidate_by_id[final["candidate_rule_id"]]["source"]["evidence_shot_ids"])
        replacement = next(
            shot_id
            for shot_id in source_review["moving_image_reviewed_shot_ids"]
            if shot_id not in canonical_refs
        )
        final["source_refs"] = [replacement]
        final["supplemental_context_refs"] = [replacement]
        spec = next(item for item in review["runtime_rule_specs"] if item["candidate_rule_id"] == final["candidate_rule_id"])
        spec["source_refs"] = [replacement]
        for role in spec["functional_roles"]:
            role["shot_id"] = replacement
            role["source_refs"] = [replacement]
        self.assertIn("INTEGRATION-CANDIDATE-CLAIM-REF", issue_codes(self.validate_copy(review)))
        with self.assertRaisesRegex(ValueError, "canonical candidate lineage"):
            assert_runtime_review_lineage(review, self.candidate_by_id)

    def test_functional_roles_require_fresh_promotion_source_refs(self) -> None:
        review = copy.deepcopy(self.review)
        spec = review["runtime_rule_specs"][0]
        source_disposition = next(
            item for item in review["candidate_dispositions"]
            if item["candidate_rule_id"] == spec["candidate_rule_id"]
        )
        source_review = next(
            item for item in review["evidence_reviews"]
            if item["review_id"] == source_disposition["review_ids"][0]
        )
        outside_promotion = next(
            item["shot_id"]
            for item in source_review["reviewed_shots"]
            if item["shot_id"] not in spec["source_refs"]
        )
        spec["functional_roles"][0]["shot_id"] = outside_promotion
        spec["functional_roles"][0]["source_refs"] = [outside_promotion]
        self.assertIn("INTEGRATION-FUNCTIONAL-ROLE-REF", issue_codes(self.validate_copy(review)))
        with self.assertRaisesRegex(ValueError, "functional role lacks fresh source binding"):
            assert_runtime_review_lineage(review, self.candidate_by_id)

    def test_pending_candidate_must_have_a_precise_gap(self) -> None:
        review = copy.deepcopy(self.review)
        pending = next(item for item in review["candidate_dispositions"] if item["final_status"] == "EVIDENCE_GAP_PENDING")
        pending["evidence_gap_id"] = "MISSING-GAP"
        self.assertIn("INTEGRATION-PENDING-GAP", issue_codes(self.validate_copy(review)))

    def test_pending_candidate_must_belong_to_exactly_its_named_gap(self) -> None:
        pending = next(item for item in self.review["candidate_dispositions"] if item["final_status"] == "EVIDENCE_GAP_PENDING")
        other_gap = next(item for item in self.review["evidence_gaps"] if item["gap_id"] != pending["evidence_gap_id"])

        review = copy.deepcopy(self.review)
        target = next(item for item in review["candidate_dispositions"] if item["candidate_rule_id"] == pending["candidate_rule_id"])
        target["evidence_gap_id"] = other_gap["gap_id"]
        self.assertIn("INTEGRATION-PENDING-GAP", issue_codes(self.validate_copy(review)))

        review = copy.deepcopy(self.review)
        target_gap = next(item for item in review["evidence_gaps"] if item["gap_id"] == other_gap["gap_id"])
        target_gap["candidate_rule_ids"].append(pending["candidate_rule_id"])
        self.assertIn("INTEGRATION-PENDING-GAP", issue_codes(self.validate_copy(review)))

    def test_evidence_gap_cannot_include_a_foreign_candidate(self) -> None:
        review = copy.deepcopy(self.review)
        review["evidence_gaps"][0]["candidate_rule_ids"].append("FOREIGN-CANDIDATE-NOT-IN-CORPUS")
        self.assertIn("INTEGRATION-GAP-CANDIDATE-SET", issue_codes(self.validate_copy(review)))

    def test_evidence_gap_declared_count_must_match_members(self) -> None:
        review = copy.deepcopy(self.review)
        review["evidence_gaps"][0]["candidate_count"] += 1
        self.assertIn("INTEGRATION-GAP-COUNT", issue_codes(self.validate_copy(review)))

    def test_pending_gap_requires_complete_candidate_shot_review(self) -> None:
        review = copy.deepcopy(self.review)
        pending = next(item for item in review["candidate_dispositions"] if item["final_status"] == "EVIDENCE_GAP_PENDING")
        removed = pending["source_refs"].pop()
        source_review = next(item for item in review["evidence_reviews"] if item["review_id"] == pending["review_ids"][0])
        source_review["moving_image_reviewed_shot_ids"] = [
            shot_id for shot_id in source_review["moving_image_reviewed_shot_ids"] if shot_id != removed
        ]
        self.assertIn("INTEGRATION-PENDING-REVIEW-INCOMPLETE", issue_codes(self.validate_copy(review)))

    def test_existing_material_review_debt_is_not_an_evidence_gap(self) -> None:
        existing = next(
            item
            for item in self.review["candidate_dispositions"]
            if item["final_status"] == "EXISTING_MATERIAL_REVIEW_REQUIRED"
        )
        review = copy.deepcopy(self.review)
        target = next(
            item
            for item in review["candidate_dispositions"]
            if item["candidate_rule_id"] == existing["candidate_rule_id"]
        )
        target["evidence_gap_id"] = review["evidence_gaps"][0]["gap_id"]
        self.assertIn(
            "INTEGRATION-EXISTING-REVIEW-GAP",
            issue_codes(self.validate_copy(review)),
        )

    def test_existing_material_review_debt_keeps_phase_in_progress(self) -> None:
        review = copy.deepcopy(self.review)
        review["declared_phase_status"] = "PARTIAL_EVIDENCE_GAP"
        self.assertIn(
            "INTEGRATION-PHASE-STATUS-DRIFT",
            issue_codes(self.validate_copy(review)),
        )

    def test_audio_dependency_needs_direct_audition(self) -> None:
        review = copy.deepcopy(self.review)
        positive = next(item for item in review["candidate_dispositions"] if item["final_status"] == "POSITIVE_RUNTIME_RULE")
        positive["audio_dependency"] = True
        self.assertIn("INTEGRATION-AUDIO-REVIEW", issue_codes(self.validate_copy(review)))

    def test_rejected_candidate_cannot_claim_a_rule(self) -> None:
        review = copy.deepcopy(self.review)
        rejected = next((item for item in review["candidate_dispositions"] if item["final_status"] == "REJECTED_WITH_REASON"), None)
        if rejected is None:
            self.skipTest("No evidence-backed rejected candidate has been closed yet.")
        rejected["runtime_effect_key"] = "RULE:DR-FAKE"
        self.assertIn("INTEGRATION-REJECTION-EFFECT", issue_codes(self.validate_copy(review)))

    def test_positive_rule_set_is_exact(self) -> None:
        review = copy.deepcopy(self.review)
        review["runtime_rule_specs"].pop()
        self.assertIn("INTEGRATION-RULE-SET", issue_codes(self.validate_copy(review)))

    def test_boundary_signals_are_compiled_from_reviewed_counterexamples(self) -> None:
        review = copy.deepcopy(self.review)
        spec = review["runtime_rule_specs"][0]
        spec["routing"]["not_applicable_if_any"] = ["UNREVIEWED-BOUNDARY"]
        self.assertIn("INTEGRATION-BOUNDARY-COMPILE", issue_codes(self.validate_copy(review)))

    def test_boundary_forward_test_must_exist_and_match_its_rule(self) -> None:
        review = copy.deepcopy(self.review)
        boundary = next(item for item in review["candidate_dispositions"] if item["final_status"] == "BOUNDARY_OR_COUNTEREXAMPLE")
        boundary["boundary_forward_test_id"] = "DOES-NOT-EXIST"
        self.assertIn("INTEGRATION-BOUNDARY-EFFECT", issue_codes(self.validate_copy(review)))

    def test_positive_forward_test_must_exist_and_be_bound_to_the_rule(self) -> None:
        for mutation in ("missing", "boundary-case"):
            with self.subTest(mutation=mutation):
                review = copy.deepcopy(self.review)
                spec = review["runtime_rule_specs"][0]
                spec["positive_forward_test_id"] = (
                    "DOES-NOT-EXIST"
                    if mutation == "missing"
                    else spec["boundary_forward_test_id"]
                )
                self.assertIn(
                    "INTEGRATION-POSITIVE-FORWARD-BINDING",
                    issue_codes(self.validate_copy(review)),
                )

    def test_positive_case_cannot_masquerade_as_boundary(self) -> None:
        review = copy.deepcopy(self.review)
        spec = review["runtime_rule_specs"][0]
        spec["boundary_forward_test_id"] = spec["positive_forward_test_id"]
        for disposition in review["candidate_dispositions"]:
            if (
                disposition["final_status"] == "BOUNDARY_OR_COUNTEREXAMPLE"
                and disposition["target_rule_id"] == spec["rule_id"]
            ):
                disposition["boundary_forward_test_id"] = spec["boundary_forward_test_id"]
        codes = issue_codes(self.validate_copy(review))
        self.assertNotIn("INTEGRATION-BOUNDARY-EFFECT", codes)
        self.assertIn("INTEGRATION-BOUNDARY-FORWARD-BINDING", codes)

    def test_runtime_support_relation_must_exactly_bind_final_disposition(self) -> None:
        review = copy.deepcopy(self.review)
        relation = review["runtime_rule_specs"][0]["supporting_relations"][0]
        relation["source_refs"] = [review["runtime_rule_specs"][0]["source_refs"][0]]
        self.assertIn(
            "INTEGRATION-SUPPORT-RELATION-BINDING",
            issue_codes(self.validate_copy(review)),
        )

    def test_runtime_counterexample_must_exactly_bind_final_disposition(self) -> None:
        review = copy.deepcopy(self.review)
        counterexample = review["runtime_rule_specs"][0]["counterexample"]
        counterexample["work_id"] = "FOREIGN-WORK"
        self.assertIn(
            "INTEGRATION-COUNTEREXAMPLE-RELATION-BINDING",
            issue_codes(self.validate_copy(review)),
        )

    def test_designated_counterexample_signal_must_match_evidence_and_forward_package(self) -> None:
        review = copy.deepcopy(self.review)
        spec = review["runtime_rule_specs"][0]
        spec["designated_boundary_signal_id"] = "UNREVIEWED-BOUNDARY"
        self.assertIn(
            "INTEGRATION-DESIGNATED-BOUNDARY-SIGNAL",
            issue_codes(self.validate_copy(review)),
        )

    def test_support_boundary_and_merge_must_target_positive(self) -> None:
        expectations = {
            "SUPPORTING_EVIDENCE": "INTEGRATION-SUPPORT-EFFECT",
            "BOUNDARY_OR_COUNTEREXAMPLE": "INTEGRATION-BOUNDARY-EFFECT",
            "MERGED_DUPLICATE": "INTEGRATION-MERGE-EFFECT",
        }
        for status, expected in expectations.items():
            match = next((item for item in self.review["candidate_dispositions"] if item["final_status"] == status), None)
            if match is None:
                continue
            with self.subTest(status=status):
                review = copy.deepcopy(self.review)
                target = next(item for item in review["candidate_dispositions"] if item["candidate_rule_id"] == match["candidate_rule_id"])
                if status == "MERGED_DUPLICATE":
                    target["merged_into_candidate_id"] = target["candidate_rule_id"]
                else:
                    target["target_rule_id"] = "DR-NOT-POSITIVE"
                self.assertIn(expected, issue_codes(self.validate_copy(review)))


if __name__ == "__main__":
    unittest.main()
