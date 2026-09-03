#!/usr/bin/env python3
"""Project-original forward-test package contract tests."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "drama-director-compiler"
SCRIPT_ROOT = SKILL_ROOT / "scripts"
FORWARD_ROOT = REPO_ROOT / "examples" / "forward-tests"
INDEX_PATH = FORWARD_ROOT / "index.json"
REPORT_PATH = REPO_ROOT / "research" / "validation" / "forward-test-validation.json"

sys.path.insert(0, str(SCRIPT_ROOT))
import validate_forward_tests as forward_validator  # noqa: E402
from validate_director_grammar import (  # noqa: E402
    INDEX_PATH as CANDIDATE_INDEX_PATH,
    MATRIX_PATH,
    SCHEMA_PATH as GRAMMAR_SCHEMA_PATH,
    read_json,
)


def issue_codes(report: dict) -> set[str]:
    return {issue["code"] for issue in report["issues"]}


class ForwardTestContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = read_json(INDEX_PATH)
        cls.grammar = read_json(REPO_ROOT / "research" / "grammar" / "director_grammar_v0.2.json")
        cls.candidate_index = read_json(CANDIDATE_INDEX_PATH)
        cls.matrix = read_json(MATRIX_PATH)
        cls.grammar_schema = read_json(GRAMMAR_SCHEMA_PATH)
        cls.index_schema = read_json(SKILL_ROOT / "references" / "forward-test-index.schema.json")

    def validate(self, index: dict | None = None) -> dict:
        return forward_validator.validate_repository(
            copy.deepcopy(index if index is not None else self.index),
            copy.deepcopy(self.grammar),
            copy.deepcopy(self.candidate_index),
            copy.deepcopy(self.matrix),
            copy.deepcopy(self.grammar_schema),
            copy.deepcopy(self.index_schema),
        )

    def validate_temp_mutation(self, mutate) -> dict:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir).resolve()
            copied = temp_root / "examples" / "forward-tests"
            shutil.copytree(FORWARD_ROOT, copied)
            mutate(copied)
            with patch.object(forward_validator, "REPOSITORY_ROOT", temp_root), patch.object(
                forward_validator, "FORWARD_ROOT", copied
            ):
                return self.validate()

    def test_repository_forward_packages_pass_live_validation(self) -> None:
        report = self.validate()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["package_count"], 12)
        self.assertEqual(report["required_scene_problem_count"], 6)
        self.assertEqual(report["promotion_ready_family_count"], 3)
        self.assertEqual(report["required_positive_boundary_pairs"], 3)
        self.assertEqual(report["completed_positive_cases"], 3)
        self.assertEqual(report["completed_boundary_cases"], 3)
        self.assertEqual(report["no_applicable_rule_count"], 9)
        self.assertEqual(report["selected_rule_count"], 3)
        self.assertEqual(report["human_review_pending_count"], 12)

    def test_builder_and_repository_report_are_deterministic(self) -> None:
        build = subprocess.run(
            [sys.executable, str(SCRIPT_ROOT / "build_forward_tests.py"), "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(build.returncode, 0, build.stderr)
        validate = subprocess.run(
            [sys.executable, str(SCRIPT_ROOT / "validate_forward_tests.py"), "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(validate.returncode, 0, validate.stderr)

    def test_rule_level_positive_coverage_cannot_be_removed(self) -> None:
        index = copy.deepcopy(self.index)
        entry = next(item for item in index["cases"] if item["test_case_id"] == "ORIGINAL-PERFORMANCE-OWNER-HOLD")
        entry["positive_for_rule_ids"] = []
        report = self.validate(index)
        self.assertIn("FORWARD-RULE-COVERAGE-MISSING", issue_codes(report))

    def test_live_eligible_family_drift_cannot_hide_behind_zero_index(self) -> None:
        fake = {"FAKE-CANDIDATE": {"canonical_rule_family": "FAMILY-NOW-ELIGIBLE"}}
        with patch.object(forward_validator, "eligible_candidates", return_value=fake):
            report = self.validate()
        self.assertIn("FORWARD-ELIGIBLE-DRIFT", issue_codes(report))
        self.assertIn("FORWARD-RULE-COVERAGE-MISSING", issue_codes(report))

    def test_each_promoted_rule_has_selected_and_boundary_packages(self) -> None:
        positive = {
            item["positive_for_rule_ids"][0]: item
            for item in self.index["cases"]
            if item["positive_for_rule_ids"]
        }
        boundary = {
            item["boundary_for_rule_ids"][0]: item
            for item in self.index["cases"]
            if item["boundary_for_rule_ids"]
        }
        self.assertEqual(set(positive), {rule["rule_id"] for rule in self.grammar["rules"]})
        self.assertEqual(set(boundary), set(positive))
        for rule_id, entry in positive.items():
            package = FORWARD_ROOT / entry["test_case_id"]
            result = read_json(package / "selected-rules.json")
            ir = read_json(package / "director-ir.json")
            self.assertEqual([item["rule_id"] for item in result["selected_rules"]], [rule_id])
            cited = {
                cited_rule
                for scene in ir["scenes"]
                for shot in scene["shots"]
                for cited_rule in shot["evidence_rule_ids"]
            }
            self.assertEqual(cited, {rule_id})
            self.assertTrue(entry["changed_director_dimensions"])
        for rule_id, entry in boundary.items():
            result = read_json(FORWARD_ROOT / entry["test_case_id"] / "selected-rules.json")
            rejected = next(item for item in result["rejected_rules"] if item["rule_id"] == rule_id)
            self.assertIn("NOT_APPLICABLE_MATCH", rejected["rejection_reason_codes"])

    def test_saved_routing_result_cannot_drift_from_live_router(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "ORIGINAL-ACTION-CAUSALITY" / "selected-rules.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["status"] = "SELECTED"
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        report = self.validate_temp_mutation(mutate)
        self.assertIn("FORWARD-ROUTING-DRIFT", issue_codes(report))

    def test_mutually_exclusive_routing_signals_are_rejected(self) -> None:
        cases = (
            (
                "ORIGINAL-SPATIAL-CHANGE-WITHOUT-COUNTERPART",
                "counterpart_relation_required",
            ),
            ("ORIGINAL-PROXIMITY-ELLIPSIS", "continuous_present_time"),
        )
        for case_id, contradictory_signal in cases:
            with self.subTest(case_id=case_id):
                def mutate(root: Path) -> None:
                    path = root / case_id / "routing-input.json"
                    data = json.loads(path.read_text(encoding="utf-8"))
                    data["routing_signals"].append(contradictory_signal)
                    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

                report = self.validate_temp_mutation(mutate)
                self.assertIn("FORWARD-SIGNAL-CONTRADICTION", issue_codes(report))

    def test_romantic_scene_problem_requires_locked_relationship_authority(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "ORIGINAL-PROXIMITY-TENSION" / "routing-input.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["locked_facts"][0]["fact_type"] = "shared_object"
            data["locked_facts"][0]["value"] = "Both designers need the same model for a joint review."
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        report = self.validate_temp_mutation(mutate)
        self.assertIn("FORWARD-SCENE-PROBLEM-AUTHORITY", issue_codes(report))

    def test_runtime_signals_require_matching_locked_fact_authority(self) -> None:
        cases = (
            (
                "ORIGINAL-SPATIAL-CHANGE-WITHOUT-COUNTERPART",
                "counterpart_absent",
                "counterpart_relation",
            ),
            ("ORIGINAL-PROXIMITY-ELLIPSIS", "time_ellipsis", "calendar_state"),
        )
        for case_id, fact_type, replacement in cases:
            with self.subTest(case_id=case_id):
                def mutate(root: Path) -> None:
                    path = root / case_id / "routing-input.json"
                    data = json.loads(path.read_text(encoding="utf-8"))
                    fact = next(
                        item for item in data["locked_facts"]
                        if item["fact_type"] == fact_type
                    )
                    fact["fact_type"] = replacement
                    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

                report = self.validate_temp_mutation(mutate)
                self.assertIn("FORWARD-SIGNAL-AUTHORITY", issue_codes(report))

    def test_ir_cannot_add_rule_or_enable_external_action(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "ORIGINAL-PROCEDURE" / "director-ir.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["generation_authorized"] = True
            data["scenes"][0]["shots"][0]["evidence_rule_ids"] = ["FAKE-RULE"]
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        report = self.validate_temp_mutation(mutate)
        codes = issue_codes(report)
        self.assertIn("FORWARD-IR-AUTHORIZATION", codes)
        self.assertIn("FORWARD-IR-VALIDATION", codes)

    def test_sound_fact_cannot_disappear_from_ir_audio(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "ORIGINAL-SOUND-SUSPENSE" / "director-ir.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["scenes"][0]["shots"][0]["audio"] = {
                "status": "PROJECT_ORIGINAL_ONLY",
                "instruction": None,
                "source_refs": [],
            }
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        report = self.validate_temp_mutation(mutate)
        self.assertIn("FORWARD-SOUND-AUDIO", issue_codes(report))

    def test_locked_fact_must_resolve_to_same_package_script(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "ORIGINAL-POWER-DIALOGUE" / "routing-input.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["locked_facts"][0]["source_ref"] = "locked-script.md#MISSING"
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        report = self.validate_temp_mutation(mutate)
        self.assertIn("FORWARD-FACT-ANCHOR", issue_codes(report))

    def test_locked_script_fact_value_cannot_drift_from_routing_and_ir(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "ORIGINAL-ACTION-CAUSALITY" / "locked-script.md"
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                "A loose wheel stop lets an unpowered equipment rack begin rolling.",
                "The equipment rack remains locked and never moves.",
            )
            path.write_text(text, encoding="utf-8")

        report = self.validate_temp_mutation(mutate)
        self.assertIn("FORWARD-LOCKED-FACT-DRIFT", issue_codes(report))

    def test_reference_identity_and_private_path_are_rejected(self) -> None:
        candidate = self.candidate_index["candidates"][0]
        evidence_id = candidate["source"]["evidence_id"]

        def mutate(root: Path) -> None:
            path = root / "ORIGINAL-PUBLIC-REVEAL" / "locked-script.md"
            text = path.read_text(encoding="utf-8").replace(
                "PRIVATE_SOURCE_USED: false", "PRIVATE_SOURCE_USED: true"
            )
            path.write_text(
                text + f"\n{evidence_id}\nNobody\n/tmp/project-notes.txt\nprivate/story.md\n",
                encoding="utf-8",
            )

        report = self.validate_temp_mutation(mutate)
        codes = issue_codes(report)
        self.assertIn("FORWARD-SURFACE-ID", codes)
        self.assertIn("FORWARD-WORK-SURFACE", codes)
        self.assertIn("FORWARD-PRIVATE-PATH", codes)
        self.assertIn("FORWARD-RIGHTS-HEADER", codes)

    def test_json_unicode_escapes_cannot_hide_path_media_or_work_title(self) -> None:
        def mutate(root: Path) -> None:
            path = root / "ORIGINAL-NO-APPLICABLE-RULE" / "director-ir.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["scenes"][0]["shots"][0]["constraints"]["must_not_appear"].extend(
                ["/tmp/project-notes.txt", "reference.mov", "Nobody"]
            )
            text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            text = text.replace("/tmp/project-notes.txt", "\\u002ftmp\\u002fproject-notes.txt")
            text = text.replace("reference.mov", "reference\\u002emov")
            text = text.replace("Nobody", "Nob\\u006fdy")
            path.write_text(text, encoding="utf-8")

        report = self.validate_temp_mutation(mutate)
        codes = issue_codes(report)
        self.assertIn("FORWARD-PRIVATE-PATH", codes)
        self.assertIn("FORWARD-MEDIA-REF", codes)
        self.assertIn("FORWARD-WORK-SURFACE", codes)

    def test_render_and_validation_reports_cannot_be_hand_edited(self) -> None:
        def mutate(root: Path) -> None:
            shot = root / "ORIGINAL-SOUND-SUSPENSE" / "shot-script.md"
            shot.write_text(shot.read_text(encoding="utf-8") + "manual drift\n", encoding="utf-8")
            validation = root / "ORIGINAL-SOUND-SUSPENSE" / "validation.json"
            data = json.loads(validation.read_text(encoding="utf-8"))
            data["selection_count"] = 1
            validation.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        report = self.validate_temp_mutation(mutate)
        codes = issue_codes(report)
        self.assertIn("FORWARD-SHOT-RENDER", codes)
        self.assertIn("FORWARD-VALIDATION-DRIFT", codes)

    def test_review_and_manifest_must_remain_pending(self) -> None:
        def mutate(root: Path) -> None:
            manifest_path = root / "ORIGINAL-NO-APPLICABLE-RULE" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["status"] = "PASS"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            review_path = root / "ORIGINAL-NO-APPLICABLE-RULE" / "human-review.md"
            review_path.write_text(
                review_path.read_text(encoding="utf-8")
                + "STATUS: APPROVED\nDIRECTOR_APPROVAL: APPROVED\nGENERATION_AUTHORIZED: true\nPUBLICATION_AUTHORIZED: true\n",
                encoding="utf-8",
            )

        report = self.validate_temp_mutation(mutate)
        codes = issue_codes(report)
        self.assertIn("FORWARD-MANIFEST", codes)
        self.assertIn("FORWARD-HUMAN-REVIEW", codes)


if __name__ == "__main__":
    unittest.main()
