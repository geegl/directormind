#!/usr/bin/env python3
"""Version-scoped Director IR compatibility and migration regressions."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = REPO_ROOT / "skills" / "drama-director-compiler"
SCRIPT_ROOT = SKILL_ROOT / "scripts"
IR_SCHEMA_PATH = SKILL_ROOT / "references" / "director-ir.schema.json"
RESULT_SCHEMA_PATH = SKILL_ROOT / "references" / "director-routing-result.schema.json"
FORWARD_IR_PATH = REPO_ROOT / "examples" / "forward-tests" / "ORIGINAL-NO-APPLICABLE-RULE" / "director-ir.json"
GRAMMAR_PATH = REPO_ROOT / "research" / "grammar" / "director_grammar_v0.2.json"

sys.path.insert(0, str(SCRIPT_ROOT))
from render_director_ir import render_audio, render_shot_script  # noqa: E402
from route_director_rules import schema_issues  # noqa: E402
from upgrade_director_ir_v02 import legacy_review_required_result, upgrade_ir  # noqa: E402
from validate_director_ir import (  # noqa: E402
    audio_contract_issues,
    evidence_rule_reference_issues,
    validate as validate_ir,
)


def legacy_grammar() -> dict:
    return {
        "schema_version": "director-grammar/0.1",
        "rules": [{"rule_id": "GO-01"}, {"rule_id": "GO-07"}, {"rule_id": "DG-01"}],
    }


def legacy_shot(rule_id: str, *, characters: list[str], text: str) -> dict:
    return {
        "allowed_characters": characters,
        "blocking": text,
        "narrative_goal": "preserve the legacy test boundary",
        "dialogue": [],
        "visible_text": [],
        "evidence_rule_ids": [rule_id],
    }


class DirectorIRCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.forward_ir = json.loads(FORWARD_IR_PATH.read_text(encoding="utf-8"))
        cls.grammar = json.loads(GRAMMAR_PATH.read_text(encoding="utf-8"))

    def test_legacy_go01_trigger_is_preserved_only_for_v01(self) -> None:
        matching = legacy_shot("GO-01", characters=["Adrian"], text="Adrian files an invoice for five dollars.")
        unrelated = legacy_shot("GO-01", characters=["Courier"], text="The courier reaches a floor mark.")
        self.assertEqual(evidence_rule_reference_issues(matching, legacy_grammar(), "shot"), [])
        self.assertIn(
            "IR-GO01-TRIGGER",
            {item["code"] for item in evidence_rule_reference_issues(unrelated, legacy_grammar(), "shot")},
        )
        v02 = {"schema_version": "director-grammar/0.2", "rules": [{"rule_id": "GO-01"}]}
        self.assertNotIn(
            "IR-GO01-TRIGGER",
            {item["code"] for item in evidence_rule_reference_issues(unrelated, v02, "shot", {})},
        )

    def test_legacy_go07_trigger_is_preserved_only_for_v01(self) -> None:
        matching = legacy_shot("GO-07", characters=["A", "B"], text="Stay together, but B walks away.")
        unrelated = legacy_shot("GO-07", characters=["A", "B"], text="B walks away after the work is complete.")
        self.assertEqual(evidence_rule_reference_issues(matching, legacy_grammar(), "shot"), [])
        self.assertIn(
            "IR-GO07-TRIGGER",
            {item["code"] for item in evidence_rule_reference_issues(unrelated, legacy_grammar(), "shot")},
        )

    def test_legacy_compatible_upgrade_preserves_data_and_marks_routing_for_review(self) -> None:
        source = copy.deepcopy(self.forward_ir)
        source["schema_version"] = "director-ir/0.1"
        source["director_grammar_path"] = "research/grammar/director_grammar_seed_v0.1.json"
        shots = source["scenes"][0]["shots"]
        shots[0]["evidence_rule_ids"] = ["GO-01"]
        shots[1]["evidence_rule_ids"] = ["DG-01"]
        camera_contract = {
            key: copy.deepcopy(shots[0][key])
            for key in ("camera_start", "camera_path", "camera_end")
        }
        upgraded = upgrade_ir(source, {})
        self.assertEqual(source["schema_version"], "director-ir/0.1")
        self.assertEqual(upgraded["schema_version"], "director-ir/0.2")
        self.assertEqual(upgraded["director_grammar_path"], source["director_grammar_path"])
        self.assertIsNone(upgraded["scenes"][0]["routing_input"])
        self.assertEqual(upgraded["scenes"][0]["routing_result"]["status"], "HUMAN_REVIEW_REQUIRED")
        self.assertEqual(upgraded["scenes"][0]["routing_result"]["ir_handoff"], "PAUSE_FOR_HUMAN")
        self.assertEqual(schema_issues(upgraded["scenes"][0]["routing_result"], RESULT_SCHEMA_PATH), [])
        self.assertNotIn("GO-01", upgraded["scenes"][0]["shots"][0]["evidence_rule_ids"])
        self.assertEqual(upgraded["scenes"][0]["shots"][1]["evidence_rule_ids"], ["DG-01"])
        for key, value in camera_contract.items():
            self.assertEqual(upgraded["scenes"][0]["shots"][0][key], value)

    def test_legacy_compatible_pause_is_visible_in_human_review(self) -> None:
        source = copy.deepcopy(self.forward_ir)
        source["schema_version"] = "director-ir/0.1"
        upgraded = upgrade_ir(source, {})
        rendered = render_shot_script(upgraded)
        self.assertIn("HUMAN_REVIEW_REQUIRED", rendered)
        self.assertIn("PAUSE_FOR_HUMAN", rendered)
        self.assertIn("LEGACY_SCENE_PROBLEM", rendered)
        self.assertIn("不得按 Grammar v0.2 继续执行", rendered)

    def test_routed_upgrade_requires_explicit_complete_results_and_shot_bindings(self) -> None:
        source = copy.deepcopy(self.forward_ir)
        complete_input = copy.deepcopy(source["scenes"][0]["routing_input"])
        complete_result = copy.deepcopy(source["scenes"][0]["routing_result"])
        source["schema_version"] = "director-ir/0.1"
        source["scenes"][0].pop("routing_input")
        source["scenes"][0].pop("routing_result")
        source["scenes"][0]["shots"][0]["evidence_rule_ids"] = ["GO-01"]
        overrides = {
            "migration_mode": "GRAMMAR_V02_ROUTED",
            "target_director_grammar_path": "research/grammar/director_grammar_v0.2.json",
            "scene_routing_inputs": {"EP01-SC01": complete_input},
            "scene_routing_results": {"EP01-SC01": complete_result},
            "shot_overrides": {
                shot["shot_id"]: {"evidence_rule_ids": []}
                for shot in source["scenes"][0]["shots"]
            },
        }
        upgraded = upgrade_ir(source, overrides, self.grammar)
        self.assertEqual(schema_issues(upgraded, IR_SCHEMA_PATH), [])
        self.assertEqual(validate_ir(upgraded, self.grammar)["status"], "PASS")
        self.assertEqual(upgraded["scenes"][0]["routing_input"], complete_input)
        self.assertEqual(upgraded["scenes"][0]["routing_result"], complete_result)
        self.assertTrue(all(not shot["evidence_rule_ids"] for shot in upgraded["scenes"][0]["shots"]))

    def test_routed_upgrade_rejects_missing_or_incomplete_routing_evidence(self) -> None:
        source = copy.deepcopy(self.forward_ir)
        complete_input = copy.deepcopy(source["scenes"][0].pop("routing_input"))
        source["schema_version"] = "director-ir/0.1"
        source["scenes"][0].pop("routing_result")
        base = {
            "migration_mode": "GRAMMAR_V02_ROUTED",
            "target_director_grammar_path": "research/grammar/director_grammar_v0.2.json",
            "scene_routing_inputs": {"EP01-SC01": complete_input},
            "shot_overrides": {
                shot["shot_id"]: {"evidence_rule_ids": []}
                for shot in source["scenes"][0]["shots"]
            },
        }
        with self.assertRaisesRegex(ValueError, "complete routing result"):
            upgrade_ir(source, base, self.grammar)
        incomplete = copy.deepcopy(base)
        incomplete["scene_routing_results"] = {
            "EP01-SC01": {
                "schema_version": "director-routing-result/0.1",
                "status": "NO_APPLICABLE_RULE",
                "selected_rules": [],
                "human_review_status": "HUMAN_REVIEW_PENDING",
            }
        }
        with self.assertRaisesRegex(ValueError, "routing result is invalid"):
            upgrade_ir(source, incomplete, self.grammar)

    def test_routed_upgrade_rejects_results_not_bound_to_target_grammar(self) -> None:
        source = copy.deepcopy(self.forward_ir)
        complete_input = copy.deepcopy(source["scenes"][0].pop("routing_input"))
        source["schema_version"] = "director-ir/0.1"
        complete = copy.deepcopy(source["scenes"][0].pop("routing_result"))
        base = {
            "migration_mode": "GRAMMAR_V02_ROUTED",
            "target_director_grammar_path": "research/grammar/director_grammar_v0.2.json",
            "scene_routing_inputs": {"EP01-SC01": complete_input},
            "shot_overrides": {
                shot["shot_id"]: {"evidence_rule_ids": []}
                for shot in source["scenes"][0]["shots"]
            },
        }
        variants = {}
        paused = legacy_review_required_result("EP01-SC01")
        variants["paused"] = paused
        constraints = copy.deepcopy(complete)
        constraints["applied_constraint_ids"] = []
        variants["constraints"] = constraints
        handoff = copy.deepcopy(complete)
        handoff["ir_handoff"] = "CONTINUE_WITH_SELECTED_RULES"
        variants["handoff"] = handoff
        fake = copy.deepcopy(complete)
        fake.update({
            "status": "SELECTED",
            "eligible_rule_ids": ["FAKE-RULE"],
            "selected_rules": [{
                "rule_id": "FAKE-RULE",
                "selection_reason_codes": ["RUNTIME_AUTHORIZED"],
                "matched_fact_ids": [],
            }],
            "selection_count": 1,
            "ir_handoff": "CONTINUE_WITH_SELECTED_RULES",
        })
        variants["fake_rule"] = fake
        for name, result in variants.items():
            with self.subTest(name=name):
                overrides = copy.deepcopy(base)
                overrides["scene_routing_results"] = {"EP01-SC01": result}
                if name == "fake_rule":
                    first_shot_id = source["scenes"][0]["shots"][0]["shot_id"]
                    overrides["shot_overrides"][first_shot_id]["evidence_rule_ids"] = ["FAKE-RULE"]
                with self.assertRaisesRegex(ValueError, "not bound to the target Grammar"):
                    upgrade_ir(source, overrides, self.grammar)

        valid_overrides = copy.deepcopy(base)
        valid_overrides["scene_routing_results"] = {"EP01-SC01": complete}
        forged_grammar = {
            "schema_version": "director-grammar/0.2",
            "rules": [],
            "project_constraints": [],
            "safety_constraints": [],
        }
        with self.assertRaisesRegex(ValueError, "target Grammar v0.2 is invalid"):
            upgrade_ir(source, valid_overrides, forged_grammar)

    def test_standard_audio_rendering_remains_stable(self) -> None:
        audio = {
            "status": "PROJECT_ORIGINAL_LOCKED",
            "instruction": "Play one project-original pulse.",
            "source_refs": ["locked-script.md#FACT-01"],
        }
        self.assertEqual(
            render_audio(audio),
            "PROJECT_ORIGINAL_LOCKED: Play one project-original pulse.<br>AUDIO REF: locked-script.md#FACT-01",
        )
        self.assertEqual(audio_contract_issues(audio, "shot"), [])

    def test_legacy_audio_is_visible_and_warned_without_guessing_its_meaning(self) -> None:
        legacy = {"legacy_cue": "room tone | pause", "music": {"level": "low"}}
        rendered = render_audio(legacy)
        self.assertIn("LEGACY_UNMAPPED", rendered)
        self.assertIn("legacy_cue", rendered)
        self.assertIn("room tone \\| pause", rendered)
        self.assertIn("music", rendered)
        self.assertNotEqual(rendered, "UNKNOWN")
        self.assertEqual(
            {item["code"] for item in audio_contract_issues(legacy, "shot")},
            {"IR-AUDIO-LEGACY-UNMAPPED"},
        )

    def test_legacy_audio_with_v02_key_names_stays_unmapped_after_upgrade(self) -> None:
        source = copy.deepcopy(self.forward_ir)
        source["schema_version"] = "director-ir/0.1"
        legacy = {
            "status": "AUDIO_OBSERVED",
            "instruction": "Bring in score before picture.",
            "source_refs": [],
        }
        source["scenes"][0]["shots"][0]["audio"] = copy.deepcopy(legacy)
        upgraded = upgrade_ir(source, {})
        audio = upgraded["scenes"][0]["shots"][0]["audio"]
        self.assertEqual(audio, {"legacy_unmapped": legacy})
        self.assertEqual(
            {item["code"] for item in audio_contract_issues(audio, "shot")},
            {"IR-AUDIO-LEGACY-UNMAPPED"},
        )
        rendered = render_audio(audio)
        self.assertTrue(rendered.startswith("LEGACY_UNMAPPED:"))
        self.assertIn("Bring in score before picture.", rendered)

    def test_upgrade_cli_refuses_to_overwrite_any_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ir_path = root / "legacy.json"
            overrides_path = root / "overrides.json"
            ir_path.write_text(json.dumps(self.forward_ir), encoding="utf-8")
            overrides_path.write_text("{}", encoding="utf-8")
            for protected in (ir_path, overrides_path):
                with self.subTest(path=protected.name):
                    before = protected.read_bytes()
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(SCRIPT_ROOT / "upgrade_director_ir_v02.py"),
                            "--ir", str(ir_path),
                            "--overrides", str(overrides_path),
                            "--output", str(protected),
                        ],
                        cwd=REPO_ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("must not overwrite", result.stderr)
                    self.assertEqual(protected.read_bytes(), before)

            grammar_path = root / "grammar.json"
            grammar_path.write_text(json.dumps(self.grammar), encoding="utf-8")
            routed_overrides = {
                "migration_mode": "GRAMMAR_V02_ROUTED",
                "target_director_grammar_path": str(grammar_path),
                "scene_routing_inputs": {
                    self.forward_ir["scenes"][0]["scene_id"]: self.forward_ir["scenes"][0]["routing_input"],
                },
                "scene_routing_results": {
                    self.forward_ir["scenes"][0]["scene_id"]: self.forward_ir["scenes"][0]["routing_result"],
                },
            }
            overrides_path.write_text(json.dumps(routed_overrides), encoding="utf-8")
            before = grammar_path.read_bytes()
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_ROOT / "upgrade_director_ir_v02.py"),
                    "--ir", str(ir_path),
                    "--overrides", str(overrides_path),
                    "--output", str(grammar_path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must not overwrite", result.stderr)
            self.assertEqual(grammar_path.read_bytes(), before)

    def test_upgrade_cli_refuses_to_overwrite_existing_unrelated_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ir_path = root / "legacy.json"
            overrides_path = root / "overrides.json"
            output_path = root / "existing.json"
            ir_path.write_text(json.dumps(self.forward_ir), encoding="utf-8")
            overrides_path.write_text("{}", encoding="utf-8")
            marker = b"user-owned-existing-output\n"
            output_path.write_bytes(marker)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_ROOT / "upgrade_director_ir_v02.py"),
                    "--ir", str(ir_path),
                    "--overrides", str(overrides_path),
                    "--output", str(output_path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("already exists", result.stderr)
            self.assertEqual(output_path.read_bytes(), marker)

    def test_cross_scene_routing_substitution_is_rejected(self) -> None:
        action_path = REPO_ROOT / "examples" / "forward-tests" / "ORIGINAL-ACTION-CAUSALITY" / "director-ir.json"
        power_path = REPO_ROOT / "examples" / "forward-tests" / "ORIGINAL-POWER-DIALOGUE" / "director-ir.json"
        action = json.loads(action_path.read_text(encoding="utf-8"))
        power = json.loads(power_path.read_text(encoding="utf-8"))

        wrong_result = copy.deepcopy(action)
        wrong_result["scenes"][0]["routing_result"] = copy.deepcopy(
            power["scenes"][0]["routing_result"]
        )
        report = validate_ir(wrong_result, self.grammar)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn(
            "IR-ROUTING-REPLAY-DRIFT",
            {item["code"] for item in report["issues"]},
        )

        wrong_scene = copy.deepcopy(action)
        wrong_scene["scenes"][0]["routing_input"] = copy.deepcopy(
            power["scenes"][0]["routing_input"]
        )
        wrong_scene["scenes"][0]["routing_result"] = copy.deepcopy(
            power["scenes"][0]["routing_result"]
        )
        report = validate_ir(wrong_scene, self.grammar)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(
            {"IR-ROUTING-DRAMATIC-DRIFT", "IR-ROUTING-FACT-BINDING"}
            & {item["code"] for item in report["issues"]}
        )

        legacy = copy.deepcopy(action)
        legacy["schema_version"] = "director-ir/0.1"
        legacy["scenes"][0].pop("routing_input")
        legacy["scenes"][0].pop("routing_result")
        overrides = {
            "migration_mode": "GRAMMAR_V02_ROUTED",
            "target_director_grammar_path": "research/grammar/director_grammar_v0.2.json",
            "scene_routing_inputs": {
                "EP01-SC01": action["scenes"][0]["routing_input"],
            },
            "scene_routing_results": {
                "EP01-SC01": power["scenes"][0]["routing_result"],
            },
            "shot_overrides": {
                shot["shot_id"]: {"evidence_rule_ids": []}
                for shot in legacy["scenes"][0]["shots"]
            },
        }
        with self.assertRaisesRegex(ValueError, "not bound to the target Grammar or its routing input"):
            upgrade_ir(legacy, overrides, self.grammar)

    def test_mixed_audio_preserves_unmapped_fields_in_full_shot_render(self) -> None:
        ir = copy.deepcopy(self.forward_ir)
        ir["scenes"][0]["shots"][0]["audio"] = {
            "status": "PROJECT_ORIGINAL_ONLY",
            "instruction": None,
            "source_refs": [],
            "legacy_mix": "keep this note",
        }
        rendered = render_shot_script(ir)
        self.assertIn("PROJECT_ORIGINAL_ONLY", rendered)
        self.assertIn("LEGACY_UNMAPPED", rendered)
        self.assertIn("keep this note", rendered)
        self.assertEqual(
            {item["code"] for item in audio_contract_issues(ir["scenes"][0]["shots"][0]["audio"], "shot")},
            {"IR-AUDIO-LEGACY-EXTRAS"},
        )


if __name__ == "__main__":
    unittest.main()
