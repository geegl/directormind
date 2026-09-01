#!/usr/bin/env python3
"""Runtime Grammar v0.2 and rights-safe routing contract tests."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "drama-director-compiler"
SCRIPT_ROOT = SKILL_ROOT / "scripts"
GRAMMAR_PATH = REPO_ROOT / "research" / "grammar" / "director_grammar_v0.2.json"
INDEX_PATH = REPO_ROOT / "research" / "grammar" / "candidate_rule_index.json"
MATRIX_PATH = REPO_ROOT / "research" / "grammar" / "cross_work_support_matrix.json"
GRAMMAR_SCHEMA_PATH = SKILL_ROOT / "references" / "director-grammar.schema.json"
INPUT_SCHEMA_PATH = SKILL_ROOT / "references" / "director-routing-input.schema.json"
RESULT_SCHEMA_PATH = SKILL_ROOT / "references" / "director-routing-result.schema.json"
CASES_PATH = SKILL_ROOT / "tests" / "fixtures" / "routing_cases.json"

sys.path.insert(0, str(SCRIPT_ROOT))
from route_director_rules import route_scene, schema_issues  # noqa: E402
from validate_director_grammar import read_json, validate_grammar  # noqa: E402
from validate_director_ir import (  # noqa: E402
    evidence_rule_reference_issues,
    scene_routing_binding_issues,
)
from validate_director_routing_cases import validate_cases  # noqa: E402


def issue_codes(report: dict) -> set[str]:
    return {issue["code"] for issue in report["issues"]}


def synthetic_rule(rule_id: str, problem: str, signal: str, fact_type: str) -> dict:
    return {
        "rule_id": rule_id,
        "promotion_status": "CROSS_WORK_SUPPORTED",
        "runtime_authorized": True,
        "selection_rank": 1,
        "routing": {
            "scene_problems": [problem],
            "trigger_all_of": [signal],
            "trigger_any_of": [],
            "required_fact_types": [fact_type],
            "not_applicable_if_any": [],
            "conflicts_with": [],
            "audit_subject_tags": [],
        },
    }


def full_synthetic_rule() -> dict:
    return {
        "rule_id": "DR-SYNTHETIC-CAUSAL-CLARITY",
        "name": "Preserve a verified causal chain",
        "canonical_rule_family": "SYNTHETIC-FAMILY",
        "promotion_source_candidate_id": "SYNTHETIC-CANDIDATE-1",
        "promotion_status": "CROSS_WORK_SUPPORTED",
        "runtime_authorized": True,
        "scene_problem": {"primary": "ACTION_CAUSALITY", "secondary": []},
        "functional_roles": [],
        "trigger": {"description": "A locked action contains a visible cause and result.", "required_signals": ["cause_effect_chain"]},
        "routing": {
            "scene_problems": ["ACTION_CAUSALITY"],
            "trigger_all_of": ["cause_effect_chain"],
            "trigger_any_of": [],
            "required_fact_types": ["cause_effect_chain"],
            "not_applicable_if_any": ["simultaneous_unresolved_causes"],
            "conflicts_with": [],
            "audit_subject_tags": ["physical_action"],
        },
        "required_story_facts": ["The cause and result are both locked facts."],
        "applicable_when": ["The target scene independently proves the cause and result."],
        "not_applicable_when": {"descriptions": ["Causality remains unresolved."], "signals": ["simultaneous_unresolved_causes"]},
        "conflict_levels": ["LOCKED_STORY_FACTS", "PROVIDER_LIMITATIONS"],
        "conflicts_with_rule_ids": [],
        "selection_rank": 1,
        "director_decision": "Keep the locked cause legible before its result.",
        "coverage": "Give each necessary causal state readable coverage.",
        "blocking": "Keep the action path consistent with the locked geometry.",
        "pacing": "Allow each information change to register.",
        "edit_logic": "Do not reverse the locked causal order.",
        "audio_logic": {"status": "NOT_DEPENDENT", "instruction": None, "source_refs": []},
        "continuity": "Carry the verified object and position states across the cut.",
        "ai_risk": {
            "camera": {"level": "LOW", "reasons": ["A stable view is sufficient."]},
            "performance": {"level": "LOW", "reasons": ["No synchronized dialogue is required."]},
            "continuity": {"level": "MEDIUM", "reasons": ["Cause and result states must match."]},
        },
        "failure_modes": ["The result appears before its cause is readable."],
        "fallback": {
            "camera": "Use two stable views.",
            "performance": "Separate action from reaction.",
            "continuity": "Use a clean state-matching insert.",
            "project_original_only": True,
        },
        "confidence": {"within_source": "HIGH", "transfer": "MEDIUM", "execution": "MEDIUM"},
        "evidence_lineage": {
            "candidate_rule_ids": ["SYNTHETIC-CANDIDATE-1"],
            "work_ids": ["SYNTHETIC-WORK-ALPHA", "SYNTHETIC-WORK-BETA"],
            "evidence_ids": ["SYNTHETIC-EVIDENCE-ALPHA", "SYNTHETIC-EVIDENCE-BETA"],
            "evidence_shot_ids": ["SYNTHETIC-SHOT-ALPHA", "SYNTHETIC-SHOT-BETA"],
            "relation_review_ids": ["SYNTHETIC-RELATION-REVIEW"],
            "counterexample_ids": ["SYNTHETIC-COUNTEREXAMPLE"],
            "forward_test_ids": [],
            "director_review_id": "SYNTHETIC-DIRECTOR-REVIEW",
        },
        "rights_boundary": {
            "surface_copy_allowed": False,
            "subject_matter_similarity_is_trigger": False,
            "project_original_assets_only": True,
        },
        "human_review": {"status": "APPROVED", "review_id": "SYNTHETIC-DIRECTOR-REVIEW"},
        "routing_review": {
            "status": "HUMAN_VERIFIED",
            "review_id": "SYNTHETIC-ROUTING-REVIEW",
            "review_ref": "research/validation/grammar-rule-reviews/synthetic.json",
        },
    }


def full_synthetic_candidate() -> dict:
    rule = full_synthetic_rule()
    return {
        "candidate_rule_id": "SYNTHETIC-CANDIDATE-1",
        "canonical_rule_family": "SYNTHETIC-FAMILY",
        "promotion": {"status": "CROSS_WORK_SUPPORTED", "unknown_dependency_present": False},
        "rights_boundary": {"runtime_authorized": True, "surface_copy_allowed": False},
        "source": {
            "work_id": "SYNTHETIC-WORK-ALPHA",
            "evidence_id": "SYNTHETIC-EVIDENCE-ALPHA",
            "evidence_shot_ids": ["SYNTHETIC-SHOT-ALPHA"],
        },
        "scene_problem": {"primary": "ACTION_CAUSALITY", "secondary": []},
        "functional_roles": [],
        "confidence": copy.deepcopy(rule["confidence"]),
        "operational_contract": {
            "trigger": rule["trigger"]["description"],
            "required_story_facts": copy.deepcopy(rule["required_story_facts"]),
            "director_decision": rule["director_decision"],
            "coverage": rule["coverage"],
            "blocking": rule["blocking"],
            "pacing": rule["pacing"],
            "edit_logic": rule["edit_logic"],
            "continuity": rule["continuity"],
            "audio_logic": {"status": "UNKNOWN", "value": "No audio dependency.", "source_refs": []},
            "applicable_when": copy.deepcopy(rule["applicable_when"]),
            "not_applicable_when": copy.deepcopy(rule["not_applicable_when"]["descriptions"]),
            "failure_modes": copy.deepcopy(rule["failure_modes"]),
            "ai_risk": copy.deepcopy(rule["ai_risk"]),
            "fallback": copy.deepcopy(rule["fallback"]),
        },
    }


def validate_synthetic_grammar(
    grammar: dict, index: dict, matrix: dict, schema: dict
) -> dict:
    with patch(
        "validate_director_grammar.validate_candidate_repository",
        return_value={"status": "PASS"},
    ), patch(
        "validate_director_grammar.verified_routing_review",
        return_value=True,
    ):
        return validate_grammar(grammar, index, matrix, schema)


class DirectorGrammarRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.grammar = read_json(GRAMMAR_PATH)
        cls.index = read_json(INDEX_PATH)
        cls.matrix = read_json(MATRIX_PATH)
        cls.schema = read_json(GRAMMAR_SCHEMA_PATH)
        cls.cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    def test_repository_zero_rule_grammar_is_valid(self) -> None:
        report = validate_grammar(
            copy.deepcopy(self.grammar),
            copy.deepcopy(self.index),
            copy.deepcopy(self.matrix),
            copy.deepcopy(self.schema),
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["eligible_candidate_count"], 0)
        self.assertEqual(report["runtime_rule_count"], 0)
        self.assertEqual(report["project_constraint_count"], 5)
        self.assertEqual(report["safety_constraint_count"], 6)

    def test_required_constraint_cannot_be_removed(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        grammar["safety_constraints"].pop()
        report = validate_grammar(grammar, self.index, self.matrix, self.schema)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("GRAMMAR-SAFETY-CONSTRAINTS", issue_codes(report))

    def test_conflict_priority_is_fixed(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        grammar["conflict_priority"][0], grammar["conflict_priority"][1] = grammar["conflict_priority"][1], grammar["conflict_priority"][0]
        report = validate_grammar(grammar, self.index, self.matrix, self.schema)
        self.assertIn("GRAMMAR-CONFLICT-ORDER", issue_codes(report))

    def test_ineligible_candidate_cannot_enter_runtime(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        rule = full_synthetic_rule()
        rule["promotion_source_candidate_id"] = self.index["candidates"][0]["candidate_rule_id"]
        rule["evidence_lineage"]["candidate_rule_ids"] = [rule["promotion_source_candidate_id"]]
        grammar["rules"] = [rule]
        report = validate_grammar(grammar, self.index, self.matrix, self.schema)
        self.assertIn("GRAMMAR-CANDIDATE-INELIGIBLE", issue_codes(report))

    def test_synthetic_eligible_rule_proves_validator_is_not_hardcoded_empty(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        grammar["rules"] = [full_synthetic_rule()]
        index = {"candidates": [full_synthetic_candidate()]}
        matrix = {"families": [{"family_id": "SYNTHETIC-FAMILY", "promotion_eligibility": "CROSS_WORK_SUPPORTED"}]}
        report = validate_synthetic_grammar(grammar, index, matrix, self.schema)
        self.assertEqual(report["status"], "PASS", report["issues"])
        self.assertEqual(report["runtime_rule_count"], 1)

    def test_runtime_instruction_cannot_drift_from_promoted_contract(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        rule = full_synthetic_rule()
        rule["coverage"] = "Invent a different operational plan."
        grammar["rules"] = [rule]
        index = {"candidates": [full_synthetic_candidate()]}
        matrix = {"families": [{"family_id": "SYNTHETIC-FAMILY", "promotion_eligibility": "CROSS_WORK_SUPPORTED"}]}
        report = validate_synthetic_grammar(grammar, index, matrix, self.schema)
        self.assertIn("GRAMMAR-CONTRACT-DRIFT", issue_codes(report))

    def test_reference_work_name_outside_lineage_is_rejected(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        rule = full_synthetic_rule()
        rule["name"] = "Use Synthetic Work Alpha staging"
        grammar["rules"] = [rule]
        index = {"candidates": [full_synthetic_candidate()]}
        matrix = {"families": [{"family_id": "SYNTHETIC-FAMILY", "promotion_eligibility": "CROSS_WORK_SUPPORTED"}]}
        report = validate_synthetic_grammar(grammar, index, matrix, self.schema)
        self.assertIn("GRAMMAR-WORK-SURFACE", issue_codes(report))

    def test_reference_work_name_in_top_level_title_is_rejected(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        grammar["title"] = "Recreate the Nobody bus fight staging"
        report = validate_grammar(grammar, self.index, self.matrix, self.schema)
        self.assertIn("GRAMMAR-WORK-SURFACE", issue_codes(report))

    def test_empty_machine_required_fact_mapping_cannot_route(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        rule = full_synthetic_rule()
        rule["routing"]["required_fact_types"] = []
        grammar["rules"] = [rule]
        index = {"candidates": [full_synthetic_candidate()]}
        matrix = {"families": [{"family_id": "SYNTHETIC-FAMILY", "promotion_eligibility": "CROSS_WORK_SUPPORTED"}]}
        report = validate_synthetic_grammar(grammar, index, matrix, self.schema)
        self.assertTrue(
            any("required_fact_types" in issue["path"] for issue in report["issues"]),
            report["issues"],
        )
        scene = copy.deepcopy(self.cases[4])
        result = route_scene(scene, grammar)
        self.assertEqual(result["selection_count"], 0)
        self.assertIn("REQUIRED_FACT_MAPPING_MISSING", result["rejected_rules"][0]["rejection_reason_codes"])

    def test_unauditioned_audio_cannot_hide_inside_not_dependent(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        rule = full_synthetic_rule()
        rule["audio_logic"]["instruction"] = "Begin with an alert before its source is visible."
        grammar["rules"] = [rule]
        index = {"candidates": [full_synthetic_candidate()]}
        matrix = {"families": [{"family_id": "SYNTHETIC-FAMILY", "promotion_eligibility": "CROSS_WORK_SUPPORTED"}]}
        report = validate_synthetic_grammar(grammar, index, matrix, self.schema)
        self.assertIn("GRAMMAR-AUDIO-DRIFT", issue_codes(report))

    def test_machine_routing_mapping_requires_confined_human_review(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        grammar["rules"] = [full_synthetic_rule()]
        index = {"candidates": [full_synthetic_candidate()]}
        matrix = {"families": [{"family_id": "SYNTHETIC-FAMILY", "promotion_eligibility": "CROSS_WORK_SUPPORTED"}]}
        with patch(
            "validate_director_grammar.validate_candidate_repository",
            return_value={"status": "PASS"},
        ):
            report = validate_grammar(grammar, index, matrix, self.schema)
        self.assertIn("GRAMMAR-ROUTING-REVIEW-REF", issue_codes(report))

    def test_forged_candidate_and_matrix_cannot_authorize_routing(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        grammar["rules"] = [full_synthetic_rule()]
        index = {"candidates": [full_synthetic_candidate()]}
        matrix = {"families": [{"family_id": "SYNTHETIC-FAMILY", "promotion_eligibility": "CROSS_WORK_SUPPORTED"}]}
        report = validate_grammar(grammar, index, matrix, self.schema)
        self.assertIn("GRAMMAR-CANDIDATE-AUTHORITY", issue_codes(report))

    def test_eight_original_cases_return_no_applicable_rule(self) -> None:
        self.assertEqual(len(self.cases), 8)
        for case in self.cases:
            with self.subTest(case=case["case_id"]):
                self.assertEqual(schema_issues(case, INPUT_SCHEMA_PATH), [])
                result = route_scene(case, self.grammar)
                self.assertEqual(schema_issues(result, RESULT_SCHEMA_PATH), [])
                self.assertEqual(result["status"], "NO_APPLICABLE_RULE")
                self.assertEqual(result["selection_count"], 0)
                self.assertEqual(result["selected_rules"], [])
                self.assertEqual(result["ir_handoff"], "CONTINUE_WITH_PROJECT_CONSTRAINTS_ONLY")
                self.assertEqual(result["human_review_status"], "HUMAN_REVIEW_PENDING")

    def test_routing_case_report_is_deterministic_and_complete(self) -> None:
        first = validate_cases(copy.deepcopy(self.cases), copy.deepcopy(self.grammar))
        second = validate_cases(copy.deepcopy(self.cases), copy.deepcopy(self.grammar))
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "PASS")
        self.assertEqual(first["case_count"], 8)
        self.assertEqual(first["no_applicable_rule_count"], 8)
        self.assertEqual(first["selected_rule_count"], 0)

    def test_router_selects_at_most_four_without_filling(self) -> None:
        scene = copy.deepcopy(self.cases[4])
        grammar = copy.deepcopy(self.grammar)
        grammar["rules"] = [
            synthetic_rule(f"DR-SYNTH-{index}", "ACTION_CAUSALITY", "cause_effect_chain", "cause_effect_chain")
            for index in range(1, 7)
        ]
        result = route_scene(scene, grammar)
        self.assertEqual(result["status"], "SELECTED")
        self.assertEqual(result["selection_count"], 4)
        self.assertEqual(len([item for item in result["rejected_rules"] if "CAP_EXCEEDED_LOWER_PRECEDENCE" in item["rejection_reason_codes"]]), 2)

    def test_required_unknown_and_non_applicable_gates_reject(self) -> None:
        scene = copy.deepcopy(self.cases[4])
        rule = synthetic_rule("DR-SYNTH-GATED", "ACTION_CAUSALITY", "cause_effect_chain", "cause_effect_chain")
        rule["routing"]["required_fact_types"].append("hidden_state")
        rule["routing"]["not_applicable_if_any"] = ["cause_effect_chain"]
        scene["unknown_fact_types"] = ["hidden_state"]
        grammar = copy.deepcopy(self.grammar)
        grammar["rules"] = [rule]
        result = route_scene(scene, grammar)
        reasons = set(result["rejected_rules"][0]["rejection_reason_codes"])
        self.assertIn("REQUIRED_FACT_MISSING", reasons)
        self.assertIn("REQUIRED_FACT_UNKNOWN", reasons)
        self.assertIn("NOT_APPLICABLE_MATCH", reasons)

    def test_subject_similarity_never_selects_a_rule(self) -> None:
        scene = copy.deepcopy(self.cases[0])
        scene["subject_matter_tags"] = ["shared_topic"]
        rule = synthetic_rule("DR-SUBJECT-ONLY", "DIFFERENT_PROBLEM", "different_signal", "authority_shift")
        rule["routing"]["audit_subject_tags"] = ["shared_topic"]
        grammar = copy.deepcopy(self.grammar)
        grammar["rules"] = [rule]
        result = route_scene(scene, grammar)
        self.assertEqual(result["selection_count"], 0)
        self.assertIn("SUBJECT_SIMILARITY_ONLY", result["rejected_rules"][0]["rejection_reason_codes"])
        self.assertFalse(result["rights_boundary"]["subject_matter_used_for_selection"])

    def test_highest_priority_constraint_wins_conflict_trace(self) -> None:
        scene = copy.deepcopy(self.cases[4])
        scene["priority_constraints"] = [
            {"constraint_id": "LOWER", "priority_level": "PROVIDER_LIMITATIONS", "statement": "execution limit", "blocked_rule_ids": ["DR-CONFLICT"]},
            {"constraint_id": "HIGHER", "priority_level": "LOCKED_STORY_FACTS", "statement": "locked fact", "blocked_rule_ids": ["DR-CONFLICT"]},
        ]
        grammar = copy.deepcopy(self.grammar)
        grammar["rules"] = [synthetic_rule("DR-CONFLICT", "ACTION_CAUSALITY", "cause_effect_chain", "cause_effect_chain")]
        result = route_scene(scene, grammar)
        self.assertEqual(result["selection_count"], 0)
        self.assertEqual(result["conflict_trace"][0]["priority_level"], "LOCKED_STORY_FACTS")
        self.assertEqual(result["conflict_trace"][0]["winner_id"], "HIGHER")

    def test_every_conflict_level_outranks_all_levels_below_it(self) -> None:
        levels = self.grammar["conflict_priority"]
        for winner_index, winner_level in enumerate(levels):
            with self.subTest(level=winner_level):
                scene = copy.deepcopy(self.cases[4])
                scene["priority_constraints"] = [
                    {
                        "constraint_id": f"C-{index}",
                        "priority_level": level,
                        "statement": "abstract constraint",
                        "blocked_rule_ids": ["DR-ORDER"],
                    }
                    for index, level in reversed(list(enumerate(levels[winner_index:], start=winner_index)))
                ]
                grammar = copy.deepcopy(self.grammar)
                grammar["rules"] = [synthetic_rule("DR-ORDER", "ACTION_CAUSALITY", "cause_effect_chain", "cause_effect_chain")]
                result = route_scene(scene, grammar)
                self.assertEqual(result["conflict_trace"][0]["priority_level"], winner_level)

    def test_explicit_rule_conflict_is_deterministic(self) -> None:
        scene = copy.deepcopy(self.cases[4])
        first = synthetic_rule("DR-A-FIRST", "ACTION_CAUSALITY", "cause_effect_chain", "cause_effect_chain")
        second = synthetic_rule("DR-B-SECOND", "ACTION_CAUSALITY", "cause_effect_chain", "cause_effect_chain")
        second["routing"]["conflicts_with"] = ["DR-A-FIRST"]
        grammar = copy.deepcopy(self.grammar)
        grammar["rules"] = [second, first]
        result = route_scene(scene, grammar)
        self.assertEqual([item["rule_id"] for item in result["selected_rules"]], ["DR-A-FIRST"])
        rejected = next(item for item in result["rejected_rules"] if item["rule_id"] == "DR-B-SECOND")
        self.assertEqual(rejected["rejection_reason_codes"], ["EXPLICIT_RULE_CONFLICT"])

    def test_cli_is_deterministic_and_check_mode_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            scene_path = root / "scene.json"
            output_path = root / "routing.json"
            scene_path.write_text(json.dumps(self.cases[0], ensure_ascii=False), encoding="utf-8")
            command = [
                sys.executable,
                str(SCRIPT_ROOT / "route_director_rules.py"),
                "--scene", str(scene_path),
                "--grammar", str(GRAMMAR_PATH),
                "--output", str(output_path),
            ]
            first = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            before = output_path.read_bytes()
            check = subprocess.run(command + ["--check"], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertEqual(output_path.read_bytes(), before)

    def test_director_ir_allows_no_rule_for_v02_but_preserves_legacy_behavior(self) -> None:
        shot = {"evidence_rule_ids": []}
        no_match = {
            "schema_version": "director-routing-result/0.1",
            "status": "NO_APPLICABLE_RULE",
            "selected_rules": [],
            "human_review_status": "HUMAN_REVIEW_PENDING",
        }
        self.assertEqual(
            evidence_rule_reference_issues(shot, self.grammar, "shot", no_match),
            [],
        )
        self.assertEqual(
            {issue["code"] for issue in evidence_rule_reference_issues(shot, self.grammar, "shot")},
            {"IR-ROUTING-RESULT-MISSING"},
        )
        legacy = {"schema_version": "director-grammar/0.1", "rules": []}
        self.assertEqual(
            {issue["code"] for issue in evidence_rule_reference_issues(shot, legacy, "shot")},
            {"IR-EVIDENCE-REF"},
        )

    def test_v02_ir_rejects_unknown_rule_id_without_legacy_keyword_logic(self) -> None:
        shot = {"evidence_rule_ids": ["GO-01"]}
        no_match = {
            "schema_version": "director-routing-result/0.1",
            "status": "NO_APPLICABLE_RULE",
            "selected_rules": [],
            "human_review_status": "HUMAN_REVIEW_PENDING",
        }
        codes = {
            issue["code"]
            for issue in evidence_rule_reference_issues(shot, self.grammar, "shot", no_match)
        }
        self.assertEqual(codes, {"IR-EVIDENCE-UNKNOWN"})

    def test_selected_routing_rule_cannot_be_dropped_from_ir(self) -> None:
        grammar = copy.deepcopy(self.grammar)
        grammar["rules"] = [{"rule_id": "DR-SELECTED"}]
        scene = {
            "routing_result": {
                "schema_version": "director-routing-result/0.1",
                "status": "SELECTED",
                "selected_rules": [{"rule_id": "DR-SELECTED"}],
                "human_review_status": "HUMAN_REVIEW_PENDING",
            },
            "shots": [{"evidence_rule_ids": []}],
        }
        codes = {issue["code"] for issue in scene_routing_binding_issues(scene, grammar, "scene")}
        self.assertEqual(codes, {"IR-ROUTING-SELECTION-DRIFT"})
        scene["shots"][0]["evidence_rule_ids"] = ["DR-SELECTED"]
        self.assertEqual(scene_routing_binding_issues(scene, grammar, "scene"), [])


if __name__ == "__main__":
    unittest.main()
