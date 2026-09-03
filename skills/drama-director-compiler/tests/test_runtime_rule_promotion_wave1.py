#!/usr/bin/env python3
"""Wave 1 real-video review, promotion, and deterministic build tests."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "drama-director-compiler"
SCRIPT_ROOT = SKILL_ROOT / "scripts"
REVIEW_PATH = REPO_ROOT / "research" / "grammar" / "runtime_rule_promotion_wave1.review.json"
SCHEMA_PATH = SKILL_ROOT / "references" / "runtime-rule-promotion-review.schema.json"

sys.path.insert(0, str(SCRIPT_ROOT))
from validate_runtime_rule_promotion_review import validate  # noqa: E402


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def issue_codes(report: dict) -> set[str]:
    return {issue["code"] for issue in report["issues"]}


class RuntimeRulePromotionWave1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.review = read_json(REVIEW_PATH)
        cls.schema = read_json(SCHEMA_PATH)

    def test_repository_review_is_complete_and_evidence_bound(self) -> None:
        report = validate(copy.deepcopy(self.review), copy.deepcopy(self.schema))
        self.assertEqual(report["status"], "PASS", report["issues"])
        self.assertEqual(report["phase_status"], "COMPLETE")
        self.assertEqual(report["promoted_rule_count"], 3)
        self.assertEqual(report["promoted_family_count"], 3)
        self.assertEqual(report["reviewed_evidence_count"], 9)

    def test_unresolved_support_shot_cannot_promote(self) -> None:
        review = copy.deepcopy(self.review)
        review["promotions"][0]["supporting_relations"][0]["source_refs"] = ["MISSING-SHOT"]
        report = validate(review, copy.deepcopy(self.schema))
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("WAVE1-RELATION-BINDING", issue_codes(report))

    def test_support_ref_must_be_in_fresh_video_review(self) -> None:
        review = copy.deepcopy(self.review)
        review["promotions"][0]["supporting_relations"][0]["source_refs"] = [
            "B99-S05E14-THE-BOX-PRIDE-BAIT-CONFESSION-001-S001"
        ]
        report = validate(review, copy.deepcopy(self.schema))
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("WAVE1-RELATION-REVIEW-BINDING", issue_codes(report))

    def test_promoted_roles_must_match_fresh_review(self) -> None:
        review = copy.deepcopy(self.review)
        review["promotions"][0]["functional_roles"][0]["appearance_id"] = "STALE-ROLE"
        report = validate(review, copy.deepcopy(self.schema))
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("WAVE1-ROLE-BINDING", issue_codes(report))

    def test_semantic_scene_problems_have_short_reviewed_text_anchors(self) -> None:
        anchored_reviews = [
            item for item in self.review["evidence_reviews"] if item["text_anchor"] is not None
        ]
        self.assertEqual(len(anchored_reviews), 3)
        for item in anchored_reviews:
            with self.subTest(evidence_id=item["evidence_id"]):
                anchor = item["text_anchor"]
                self.assertIn(anchor["shot_id"], item["shot_ids"])
                self.assertIn(anchor["anchor_id"], item["scene_problem"]["source_refs"])
                evidence_path = next(
                    REPO_ROOT.glob(f"research/evidence/**/*{item['evidence_id'].replace('-', '_')}*.scene-evidence.json"),
                    None,
                )
                if evidence_path is None:
                    evidence_path = next(
                        path
                        for path in (REPO_ROOT / "research" / "evidence").rglob("*.scene-evidence.json")
                        if read_json(path)["evidence_id"] == item["evidence_id"]
                    )
                evidence = read_json(evidence_path)
                self.assertEqual(evidence["text_anchor_status"], "TEXT_ANCHOR_VERIFIED")
                self.assertEqual([entry["anchor_id"] for entry in evidence["text_anchors"]], [anchor["anchor_id"]])
                self.assertTrue(
                    any(method["method_type"] == "TEXT_ANCHOR_REVIEW" for method in evidence["methods"])
                )

    def test_audio_dependency_cannot_be_enabled_without_audio_review(self) -> None:
        review = copy.deepcopy(self.review)
        review["promotions"][0]["audio_dependency"] = True
        report = validate(review, copy.deepcopy(self.schema))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(code.startswith("SCHEMA-") for code in issue_codes(report)))

    def test_all_wave1_builders_are_deterministic(self) -> None:
        scripts = (
            "convert_legacy_scene_evidence.py",
            "build_candidate_rule_index.py",
            "build_director_grammar.py",
            "build_forward_tests.py",
        )
        for script in scripts:
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT_ROOT / script), "--check"],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
