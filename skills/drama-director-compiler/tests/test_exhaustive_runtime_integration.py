#!/usr/bin/env python3
"""End-to-end tests for the exhaustive runtime-integration report."""

from __future__ import annotations

import json
import copy
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_ROOT = REPO_ROOT / "skills" / "drama-director-compiler" / "scripts"
REVIEW_PATH = REPO_ROOT / "research" / "grammar" / "runtime_integration.review.json"
GRAMMAR_PATH = REPO_ROOT / "research" / "grammar" / "director_grammar_v0.2.json"
FORWARD_INDEX_PATH = REPO_ROOT / "examples" / "forward-tests" / "index.json"
REPORT_PATH = REPO_ROOT / "research" / "validation" / "exhaustive-runtime-integration-validation.json"
REVIEW_VALIDATOR = SCRIPT_ROOT / "validate_runtime_integration_review.py"
REPORT_BUILDER = SCRIPT_ROOT / "build_exhaustive_runtime_integration_validation.py"

sys.path.insert(0, str(SCRIPT_ROOT))
from build_exhaustive_runtime_integration_validation import build_report  # noqa: E402
from route_director_rules import route_scene  # noqa: E402


FINAL_STATUSES = {
    "POSITIVE_RUNTIME_RULE",
    "SUPPORTING_EVIDENCE",
    "BOUNDARY_OR_COUNTEREXAMPLE",
    "MERGED_DUPLICATE",
    "REJECTED_WITH_REASON",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ExhaustiveRuntimeIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.review = read_json(REVIEW_PATH)
        cls.grammar = read_json(GRAMMAR_PATH)
        cls.forward_index = read_json(FORWARD_INDEX_PATH)
        cls.report = build_report()

    def test_live_report_is_in_progress_and_corpus_enumerated(self) -> None:
        report = self.report
        final_count = sum(item["final_status"] in FINAL_STATUSES for item in self.review["candidate_dispositions"])
        pending_count = sum(item["final_status"] == "EVIDENCE_GAP_PENDING" for item in self.review["candidate_dispositions"])
        existing_review_count = sum(
            item["final_status"] == "EXISTING_MATERIAL_REVIEW_REQUIRED"
            for item in self.review["candidate_dispositions"]
        )
        rule_count = len(self.review["runtime_rule_specs"])
        self.assertEqual(report["status"], "PASS", report["issues"])
        self.assertEqual(report["phase_status"], "IN_PROGRESS")
        self.assertEqual(report["source_disposition_count"], 33)
        self.assertEqual(report["canonical_scene_evidence_count"], 31)
        self.assertEqual(report["canonical_shot_edit_unit_count"], 2343)
        self.assertEqual(report["candidate_disposition_count"], 124)
        self.assertEqual(report["final_disposition_count"], final_count)
        self.assertEqual(report["pending_evidence_gap_count"], pending_count)
        self.assertEqual(
            report["existing_material_review_required_count"],
            existing_review_count,
        )
        self.assertEqual(final_count + pending_count + existing_review_count, 124)
        self.assertEqual(report["mechanism_family_count"], 16)
        self.assertEqual(report["runtime_rule_count"], rule_count)
        self.assertEqual(report["positive_forward_case_count"], rule_count)
        self.assertEqual(report["boundary_forward_case_count"], rule_count)

    def test_every_candidate_is_final_or_has_one_precise_unresolved_class(self) -> None:
        gap_ids = {item["gap_id"] for item in self.review["evidence_gaps"]}
        dispositions = self.review["candidate_dispositions"]
        self.assertEqual(len(dispositions), 124)
        for item in dispositions:
            with self.subTest(candidate_rule_id=item["candidate_rule_id"]):
                if item["final_status"] in FINAL_STATUSES:
                    self.assertIsNone(item["evidence_gap_id"])
                    self.assertFalse(item["material_unknowns"])
                else:
                    self.assertIn(
                        item["final_status"],
                        {
                            "EVIDENCE_GAP_PENDING",
                            "EXISTING_MATERIAL_REVIEW_REQUIRED",
                        },
                    )
                    if item["final_status"] == "EVIDENCE_GAP_PENDING":
                        self.assertIn(item["evidence_gap_id"], gap_ids)
                    else:
                        self.assertIsNone(item["evidence_gap_id"])
                    self.assertTrue(item["material_unknowns"])

    def test_all_runtime_rule_lineages_exactly_match_fresh_dispositions(self) -> None:
        dispositions = self.review["candidate_dispositions"]
        specs = {item["rule_id"]: item for item in self.review["runtime_rule_specs"]}
        grammar_rules = {item["rule_id"]: item for item in self.grammar["rules"]}
        self.assertEqual(set(grammar_rules), set(specs))
        for rule_id, spec in specs.items():
            related = [
                item
                for item in dispositions
                if (
                    item["final_status"] in {"SUPPORTING_EVIDENCE", "BOUNDARY_OR_COUNTEREXAMPLE"}
                    and item["target_rule_id"] == rule_id
                )
                or (
                    item["final_status"] == "MERGED_DUPLICATE"
                    and item["merged_into_candidate_id"] == spec["candidate_rule_id"]
                )
            ]
            expected_candidates = {spec["candidate_rule_id"], *(item["candidate_rule_id"] for item in related)}
            expected_shots = {*(spec["source_refs"]), *(ref for item in related for ref in item["source_refs"])}
            lineage = grammar_rules[rule_id]["evidence_lineage"]
            with self.subTest(rule_id=rule_id):
                self.assertEqual(set(lineage["candidate_rule_ids"]), expected_candidates)
                self.assertEqual(set(lineage["evidence_shot_ids"]), expected_shots)

    def test_independent_audit_replacements_are_bound_and_false_rules_stay_withdrawn(self) -> None:
        specs = {item["rule_id"]: item for item in self.review["runtime_rule_specs"]}
        dispositions = {
            item["candidate_rule_id"]: item
            for item in self.review["candidate_dispositions"]
        }
        withdrawn_rule_ids = {
            "DR-COMPARATIVE-FIELD-BEFORE-RELATION",
            "DR-OBJECT-CUSTODY-STATE-CHECKPOINTS",
            "DR-REGISTER-RELATION-GEOMETRY-BEFORE-PROXIMITY",
        }
        self.assertTrue(withdrawn_rule_ids.isdisjoint(specs))
        self.assertTrue(
            withdrawn_rule_ids.isdisjoint(
                {item["rule_id"] for item in self.grammar["rules"]}
            )
        )

        action = specs["DR-CONSEQUENTIAL-ACTION-VISIBLE-STATE-CHAIN"]
        self.assertEqual(
            action["counterexample"]["source_candidate_rule_id"],
            "CHILDREN-OF-MEN-2006-MOVING-CAR-EXTERIOR-DISRUPTION-001-CHILDREN-CAND-APERTURE-EVENT-BEFORE-GROSS-BODY-RESPONSE-002",
        )
        self.assertEqual(
            action["designated_boundary_signal_id"],
            "continuous_view_preserves_action_chain",
        )

        aftermath = specs["DR-AFTERMATH-BY-NEXT-ACTION"]
        self.assertEqual(
            aftermath["counterexample"]["source_candidate_rule_id"],
            "APOLLO-13-1995-CONSTRAINED-MATERIAL-HANDOFF-001-AP13-C04-DEMONSTRATION-TO-DISTRIBUTED-WORK",
        )
        self.assertEqual(
            aftermath["designated_boundary_signal_id"],
            "immediate_next_action_supersedes_aftermath",
        )

        chernobyl_id = (
            "CHERNOBYL-S01E05-HEARING-RECON-001-"
            "CHERNOBYL-CAND-RETURN-TO-FORMAL-ROOM-AFTER-PEAK-004"
        )
        chernobyl = dispositions[chernobyl_id]
        expected_refs = {
            f"CHERNOBYL-S01E05-HEARING-RECON-001-S{index:03d}"
            for index in range(170, 206)
        }
        self.assertEqual(set(chernobyl["source_refs"]), expected_refs)
        support = next(
            item
            for item in aftermath["supporting_relations"]
            if item["source_candidate_rule_id"] == chernobyl_id
        )
        self.assertEqual(set(support["source_refs"]), expected_refs)

    def test_each_rule_has_a_real_positive_and_blocking_boundary_package(self) -> None:
        cases = {item["test_case_id"]: item for item in self.forward_index["cases"]}
        for spec in self.review["runtime_rule_specs"]:
            rule_id = spec["rule_id"]
            positive = cases[spec["positive_forward_test_id"]]
            boundary = cases[spec["boundary_forward_test_id"]]
            result = read_json(REPO_ROOT / boundary["package_path"] / "selected-rules.json")
            rejected = next(item for item in result["rejected_rules"] if item["rule_id"] == rule_id)
            expected_signals = {
                signal
                for item in self.review["candidate_dispositions"]
                if item["final_status"] == "BOUNDARY_OR_COUNTEREXAMPLE" and item["target_rule_id"] == rule_id
                for signal in item["boundary_signal_ids"]
            }
            compiled_signals = set(
                next(
                    rule
                    for rule in self.grammar["rules"]
                    if rule["rule_id"] == rule_id
                )["routing"]["not_applicable_if_any"]
            )
            with self.subTest(rule_id=rule_id):
                self.assertEqual(positive["test_mode"], "POSITIVE")
                self.assertEqual(positive["expected_selected_rule_ids"], [rule_id])
                self.assertTrue(positive["changed_director_dimensions"])
                self.assertEqual(boundary["test_mode"], "BOUNDARY_OR_NON_APPLICABLE")
                self.assertEqual(result["status"], "NO_APPLICABLE_RULE")
                self.assertIn("NOT_APPLICABLE_MATCH", rejected["rejection_reason_codes"])
                self.assertTrue(rejected["matched_not_applicable_signal_ids"])
                self.assertTrue(
                    set(rejected["matched_not_applicable_signal_ids"]).issubset(
                        compiled_signals
                    )
                )
                counterfactual_input = read_json(REPO_ROOT / boundary["package_path"] / "routing-input.json")
                counterfactual_input = copy.deepcopy(counterfactual_input)
                counterfactual_input["routing_signals"] = [
                    signal
                    for signal in counterfactual_input["routing_signals"]
                    if signal not in compiled_signals
                ]
                counterfactual = route_scene(counterfactual_input, self.grammar)
                self.assertIn(rule_id, {item["rule_id"] for item in counterfactual["selected_rules"]})

            positive_input = read_json(
                REPO_ROOT / positive["package_path"] / "routing-input.json"
            )
            for signal_id in expected_signals:
                with self.subTest(rule_id=rule_id, boundary_signal=signal_id):
                    probe = copy.deepcopy(positive_input)
                    probe["routing_signals"] = sorted(
                        set(probe["routing_signals"]) | {signal_id}
                    )
                    probe_result = route_scene(probe, self.grammar)
                    self.assertNotIn(
                        rule_id,
                        {item["rule_id"] for item in probe_result["selected_rules"]},
                    )
                    probe_rejection = next(
                        item
                        for item in probe_result["rejected_rules"]
                        if item["rule_id"] == rule_id
                    )
                    self.assertIn(
                        "NOT_APPLICABLE_MATCH",
                        probe_rejection["rejection_reason_codes"],
                    )
                    self.assertIn(
                        signal_id,
                        probe_rejection["matched_not_applicable_signal_ids"],
                    )

    def test_all_sixteen_families_are_reported_without_false_completion(self) -> None:
        family_results = self.report["family_results"]
        final_count = sum(item["final_status"] in FINAL_STATUSES for item in self.review["candidate_dispositions"])
        pending_count = sum(item["final_status"] == "EVIDENCE_GAP_PENDING" for item in self.review["candidate_dispositions"])
        existing_review_count = sum(
            item["final_status"] == "EXISTING_MATERIAL_REVIEW_REQUIRED"
            for item in self.review["candidate_dispositions"]
        )
        self.assertEqual(len(family_results), 16)
        self.assertEqual(sum(item["candidate_count"] for item in family_results), 124)
        self.assertEqual(sum(item["final_disposition_count"] for item in family_results), final_count)
        self.assertEqual(sum(item["pending_evidence_gap_count"] for item in family_results), pending_count)
        self.assertEqual(
            sum(
                item["existing_material_review_required_count"]
                for item in family_results
            ),
            existing_review_count,
        )
        self.assertEqual(
            sum(item["runtime_status"] == "PARTICIPATING" for item in family_results),
            12,
        )
        self.assertEqual(
            sum(item["runtime_status"] == "IN_PROGRESS" for item in family_results),
            4,
        )

    def test_checked_in_report_is_the_live_deterministic_report(self) -> None:
        self.assertEqual(read_json(REPORT_PATH), self.report)

    def test_report_clis_cannot_overwrite_inputs_or_existing_custom_outputs(self) -> None:
        scene_evidence = next((REPO_ROOT / "research" / "evidence").rglob("*.scene-evidence.json"))
        selected_result = REPO_ROOT / "examples" / "forward-tests" / "ORIGINAL-PERFORMANCE-OWNER-HOLD" / "selected-rules.json"
        for command, protected in (
            ([sys.executable, str(REVIEW_VALIDATOR), "--report"], REVIEW_PATH),
            ([sys.executable, str(REVIEW_VALIDATOR), "--report"], scene_evidence),
            ([sys.executable, str(REPORT_BUILDER), "--report"], GRAMMAR_PATH),
            ([sys.executable, str(REPORT_BUILDER), "--report"], selected_result),
        ):
            with self.subTest(command=Path(command[1]).name, mode="protected"):
                before = protected.read_bytes()
                completed = subprocess.run(
                    [*command, str(protected)],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(protected.read_bytes(), before)

            with self.subTest(command=Path(command[1]).name, mode="existing"):
                with tempfile.TemporaryDirectory() as raw_root:
                    output = Path(raw_root) / "existing.json"
                    output.write_text("preserve me\n", encoding="utf-8")
                    completed = subprocess.run(
                        [*command, str(output)],
                        cwd=REPO_ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertEqual(output.read_text(encoding="utf-8"), "preserve me\n")

            with self.subTest(command=Path(command[1]).name, mode="symlink-alias"):
                with tempfile.TemporaryDirectory() as raw_root:
                    alias = Path(raw_root) / "alias.json"
                    alias.symlink_to(protected)
                    before = protected.read_bytes()
                    completed = subprocess.run(
                        [*command, str(alias)],
                        cwd=REPO_ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertNotEqual(completed.returncode, 0)
                    self.assertEqual(protected.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
