#!/usr/bin/env python3
"""Regression tests for the closed-corpus legacy Scene Evidence converter."""

from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from convert_legacy_scene_evidence import (  # noqa: E402
    PENDING_OPERATIONAL_FIELDS,
    SCENE_META,
    SCENE_RULE_ORDINAL_START,
    _clean_text,
    _normalize_identifier,
    build_evidence,
    discover_sources,
    extract_legacy_fallback,
    main,
    output_path,
    parse_timecode,
    parse_tables,
    split_risk,
    validate_generated,
)


LEGACY_FIELDS = {
    "trigger": "trigger",
    "directing_decision": "decision",
    "coverage": "coverage",
    "blocking": "blocking",
    "pacing_edit": "pacing_edit",
    "sound": "sound",
    "applicability": "applicability",
    "non_applicability": "non_applicability",
    "failure_mode": "failure_mode",
    "counterexample": "counterexample",
    "unknown": "unknown",
    "ai_risk": "AI_risk",
    "fallback": "fallback",
    "evidence_shots": "evidence_shots",
    "confidence": "confidence",
}

FROZEN_ORIGINAL_ORDINALS = {
    "ANDOR_S01E10_SELECTED_ENVELOPE_VISUAL_EVIDENCE_V0.1": 1,
    "APOLLO_13_CONSTRAINED_MATERIAL_HANDOFF_EVIDENCE_V0.1": 5,
    "A_QUIET_PLACE_2018_PARALLEL_BODY_STATE_RADIAL_LIGHT_EVIDENCE_V0.1": 9,
    "BETTER_CALL_SAUL_S03E05_PUBLIC_PROOF_EVIDENCE_V0.1": 13,
    "BODYGUARD_S01E01_SELECTED_SEQUENCE_VISUAL_EVIDENCE_V0.1": 17,
    "BRIDGERTON_S02E05_CONTAINED_PROXIMITY_EVIDENCE_V0.1": 21,
    "BROOKLYN_NINE_NINE_S05E14_THE_BOX_VISUAL_EVIDENCE_V0.1": 25,
    "CHERNOBYL_S01E05_HEARING_RECONSTRUCTION_VISUAL_EVIDENCE_V0.1": 29,
    "CHILDREN_OF_MEN_2006_MOVING_CAR_EXTERIOR_DISRUPTION_CONTINUITY_EVIDENCE_V0.1": 33,
    "CITIZEN_KANE_BREAKFAST_MONTAGE_EVIDENCE_V0.1": 37,
    "GET_OUT_2017_HYPNOSIS_SUBJECTIVE_SPACE_EVIDENCE_V0.1": 41,
    "HOUSE_OF_THE_DRAGON_S01E08_THRONE_ROOM_EVIDENCE_V0.1": 45,
    "KNIVES_OUT_2019_WILL_READING_EVIDENCE_V0.1": 49,
    "MARRIAGE_STORY_2019_APARTMENT_SEQUENCE_EVIDENCE_V0.1": 53,
    "MOONLIGHT_2016_TWO_APPEARANCE_MULTI_ZONE_DISTANCE_OBJECT_STATE_EDITORIAL_SEQUENCE_EVIDENCE_V0.1": 57,
    "MR_ROBOT_S04E07_ACT_FOUR_VISUAL_EVIDENCE_V0.1": 61,
    "NOBODY_2021_BUS_FIGHT_EVIDENCE_V0.1": 65,
    "SICARIO_BORDER_CHECKPOINT_EVIDENCE_V0.1": 69,
    "SOUND_OF_METAL_SIGNAL_STATE_EDITORIAL_ENVELOPE_EVIDENCE_V0.1": 73,
    "TED_LASSO_S01E08_DARTS_REVERSAL_EVIDENCE_V0.1": 77,
    "THE_BEAR_S01E07_REVIEW_EVIDENCE_V0.1": 81,
    "THE_BEAR_S02E07_TASK_CLOSED_LOOP_EVIDENCE_V0.1": 85,
    "THE_DEVIL_WEARS_PRADA_2006_CERULEAN_CORRECTION_EVIDENCE_V0.1": 89,
    "THE_HAUNTING_OF_HILL_HOUSE_S01E06_ENSEMBLE_CONTINUOUS_REFRAMING_VISUAL_EVIDENCE_V0.1": 93,
    "THE_LAST_OF_US_S01E06_BEDROOM_VISUAL_EVIDENCE_V0.1": 97,
    "THE_MARTIAN_2015_MULTI_SPACE_OBJECT_STATE_EDITORIAL_SEQUENCE_VISUAL_EVIDENCE_V0.1": 101,
    "THE_SOCIAL_NETWORK_2010_OPENING_EXCHANGE_EVIDENCE_V0.1": 105,
    "THE_WIRE_S01E04_OLD_CASES_EVIDENCE_V0.1": 109,
    "TRUE_DETECTIVE_S01E04_MULTI_ZONE_MOBILE_ROUTE_VISUAL_EVIDENCE_V0.1": 113,
    "UNBELIEVABLE_S01E02_CONTAINED_TWO_PERSON_SEQUENCE_EVIDENCE_V0.1": 117,
}


class LegacySceneEvidenceConverterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sources = discover_sources()

    def test_canonical_register_has_exactly_thirty_one_sources(self) -> None:
        self.assertEqual(len(SCENE_META), 31)
        self.assertEqual(len(self.sources), 31)
        self.assertEqual({path.stem for path in self.sources}, set(SCENE_META))

    def test_legacy_tables_have_expected_corpus_counts(self) -> None:
        shots = 0
        rules = 0
        for source in self.sources:
            shot_rows, rule_rows = parse_tables(source.read_text(encoding="utf-8"))
            shots += len(shot_rows)
            rules += len(rule_rows)
        self.assertEqual(shots, 2343)
        self.assertEqual(rules, 124)

    def test_path_scrubbing_preserves_slash_phrases_and_scrubs_real_local_paths(self) -> None:
        ordinary = "person/object lens/focus head/torso/arm accepted F-1/F boundary"
        self.assertEqual(_clean_text(ordinary), ordinary)
        for value in (
            "file:///Users/name/source/movie.mov",
            "~/Movies/source/movie.mov",
            "/Users/name/Movies/movie.mov",
            "/private/tmp/movie.mov",
            "/tmp/movie.mov",
            "/Volumes/Media/movie.mov",
        ):
            self.assertIn("[local path omitted]", _clean_text(f"source {value}"), value)
            self.assertNotIn(value, _clean_text(f"source {value}"), value)

    def test_all_converted_evidence_validates_and_keeps_boundaries(self) -> None:
        converted = [build_evidence(source) for source in self.sources]
        candidate_ids: list[str] = []
        canonical_families: list[str] = []
        operational_signatures: set[tuple[str, ...]] = set()
        for source, evidence in zip(self.sources, converted):
            report = validate_generated(evidence)
            self.assertTrue(report["passed"], evidence["evidence_id"])
            warning_issues = [item for item in report["issues"] if item["level"] == "warning"]
            self.assertEqual(len(warning_issues), len(evidence["validation_warnings"]))
            self.assertGreaterEqual(len(evidence["validation_warnings"]), 2)
            self.assertTrue(any("legacy_migration" in warning for warning in evidence["validation_warnings"]))
            self.assertTrue(any("frame and PTS" in warning for warning in evidence["validation_warnings"]))
            self.assertEqual(evidence["text_anchor_status"], "TEXT_ANCHOR_NOT_USED")
            self.assertEqual(evidence["text_anchors"], [])
            self.assertEqual(evidence["scene_problem"]["primary"], "LEGACY_SCENE_PROBLEM")
            self.assertEqual(evidence["scene_problem"]["status"], "UNKNOWN")
            self.assertEqual(evidence["scene_problem"]["source_refs"], [])
            self.assertIn(SCENE_META[source.stem].primary_problem, evidence["scene_problem"]["notes"])
            for shot in evidence["shots"]:
                self.assertTrue(shot["shot_id"].startswith(f"{evidence['evidence_id']}-S"))
                for axis in ("camera", "performance", "continuity"):
                    if shot["AI_complexity"][axis]["level"] in {"HIGH", "CRITICAL"}:
                        self.assertTrue(shot["fallback"][axis])
            for rule in evidence["candidate_rules"]:
                candidate_ids.append(rule["candidate_rule_id"])
                canonical_families.append(rule["canonical_rule_family"])
                self.assertEqual(rule["promotion_status"], "BLOCKED_BY_UNKNOWN")
                self.assertEqual(rule["within_source_confidence"], "UNKNOWN")
                self.assertEqual(rule["transfer_confidence"], "UNKNOWN")
                self.assertEqual(rule["execution_confidence"], "UNKNOWN")
                self.assertEqual(rule["scene_problem"], "LEGACY_SCENE_PROBLEM")
                self.assertEqual(rule["required_story_facts"], [])
                for key, value in PENDING_OPERATIONAL_FIELDS.items():
                    self.assertEqual(rule[key], value)
                self.assertTrue(all(rule["AI_risk"][axis]["level"] == "UNKNOWN" for axis in ("camera", "performance", "continuity")))
                self.assertTrue(all(rule["fallback"][axis] is None for axis in ("camera", "performance", "continuity")))
                self.assertEqual(rule["applicable_when"], ["No applicability condition is authorized before human review."])
                self.assertEqual(rule["not_applicable_when"], ["No non-applicability boundary is authorized before human review."])
                self.assertEqual(rule["failure_modes"], ["Applying this migrated lineage row as an operational rule before human review."])
                self.assertEqual(rule["audio_logic"]["status"], "UNKNOWN")
                self.assertEqual(rule["audio_logic"]["source_refs"], [])
                operational_signatures.add(tuple(rule[key] for key in PENDING_OPERATIONAL_FIELDS))
                operational_text = " ".join(rule[key] for key in PENDING_OPERATIONAL_FIELDS).lower()
                for term in evidence["rights_boundary"]["reference_surface_terms"]:
                    self.assertNotIn(term.lower(), operational_text)

            self.assertEqual(evidence["rights_boundary"]["surface_inventory_status"], "HUMAN_REVIEWED_COMPLETE")
            self.assertIn("fixed source-neutral pending-review placeholder", evidence["rights_boundary"]["notes"])

        self.assertEqual(len(candidate_ids), 124)
        self.assertEqual(len(candidate_ids), len(set(candidate_ids)))
        self.assertEqual(len(operational_signatures), 1)
        self.assertEqual(
            set(canonical_families),
            {f"UNCLUSTERED-CANDIDATE-{index:03d}" for index in range(1, 125)},
        )
        self.assertEqual(len(set(canonical_families)), 124)
        statuses = [item["audio_evidence_status"] for item in converted]
        self.assertEqual(statuses.count("BLOCKED_DIRECT_AUDITION"), 30)
        self.assertEqual(statuses.count("SIGNAL_MEASURED_NOT_AUDITIONED"), 1)

    def test_existing_ordinals_are_frozen_and_succession_uses_new_slots(self) -> None:
        self.assertEqual(
            {
                stem: ordinal
                for stem, ordinal in SCENE_RULE_ORDINAL_START.items()
                if not stem.startswith("SUCCESSION_")
            },
            FROZEN_ORIGINAL_ORDINALS,
        )
        self.assertEqual(
            SCENE_RULE_ORDINAL_START[
                "UNBELIEVABLE_S01E02_CONTAINED_TWO_PERSON_SEQUENCE_EVIDENCE_V0.1"
            ],
            117,
        )
        self.assertEqual(
            SCENE_RULE_ORDINAL_START[
                "SUCCESSION_S01E06_BOARD_VOTE_EVIDENCE_V0.1"
            ],
            121,
        )

    def test_succession_migration_preserves_eighty_eight_units_and_four_lineage_rows(self) -> None:
        source = next(path for path in self.sources if path.stem.startswith("SUCCESSION_"))
        shot_rows, rule_rows = parse_tables(source.read_text(encoding="utf-8"))
        evidence = build_evidence(source)
        self.assertEqual(len(shot_rows), 88)
        self.assertEqual(len(rule_rows), 4)
        self.assertEqual(len(evidence["shots"]), 88)
        self.assertEqual(len(evidence["candidate_rules"]), 4)
        self.assertEqual([shot["order"] for shot in evidence["shots"]], list(range(1, 89)))
        self.assertAlmostEqual(evidence["duration"], 329.542, places=3)
        for previous, following in zip(evidence["shots"], evidence["shots"][1:]):
            self.assertEqual(previous["end"]["seconds"], following["start"]["seconds"])
        self.assertEqual(
            [row["rule_id"] for row in rule_rows],
            ["SUC-C01", "SUC-C02", "SUC-C03", "SUC-C04"],
        )
        self.assertEqual(evidence["scene_problem"]["status"], "UNKNOWN")
        self.assertEqual(evidence["audio_evidence_status"], "BLOCKED_DIRECT_AUDITION")
        self.assertTrue(
            all(rule["promotion_status"] == "BLOCKED_BY_UNKNOWN" for rule in evidence["candidate_rules"])
        )
        self.assertTrue(
            all(not shot["abstract_role_labels"] for shot in evidence["shots"])
        )
        source_text = source.read_text(encoding="utf-8")
        self.assertNotRegex(
            source_text,
            r"(?i)(/Users/|/Volumes/|/private/|file://|https?://|\.(?:mp4|mkv|mov|wav|mp3)\b)",
        )

    def test_legacy_rule_lineage_is_field_for_field_lossless(self) -> None:
        for source in self.sources:
            _shot_rows, rule_rows = parse_tables(source.read_text(encoding="utf-8"))
            evidence = build_evidence(source)
            for order, (legacy, converted) in enumerate(zip(rule_rows, evidence["candidate_rules"]), start=1):
                normalized = _normalize_identifier(legacy["rule_id"], f"C{order:02d}")
                self.assertEqual(converted["candidate_rule_id"], f"{evidence['evidence_id']}-{normalized}")
                ordinal = SCENE_RULE_ORDINAL_START[source.stem] + order - 1
                self.assertEqual(converted["canonical_rule_family"], f"UNCLUSTERED-CANDIDATE-{ordinal:03d}")
                expected = {target: legacy.get(source_key) for target, source_key in LEGACY_FIELDS.items()}
                self.assertEqual(converted["legacy_migration"], expected)
                operational_text = " ".join(converted[key] for key in PENDING_OPERATIONAL_FIELDS)
                self.assertNotIn(normalized, operational_text)

    def test_shot_order_timecodes_and_explicit_frame_pts_are_preserved(self) -> None:
        frame_rows = 0
        pts_rows = 0
        for source in self.sources:
            shot_rows, _rule_rows = parse_tables(source.read_text(encoding="utf-8"))
            evidence = build_evidence(source)
            for order, (legacy, converted) in enumerate(zip(shot_rows, evidence["shots"]), start=1):
                self.assertEqual(converted["order"], order)
                self.assertEqual(converted["start"]["timecode"], parse_timecode(legacy["start"])[0])
                self.assertEqual(converted["end"]["timecode"], parse_timecode(legacy["end"])[0])
                frame_match = re.search(r"\[\s*F(\d+)\s*,\s*F(\d+)\s*\)", legacy["evidence_timecode"], re.I)
                bare_match = re.search(r"\bF(\d+)\s*(?:–|—|-|\.\.)\s*F(\d+)\b", legacy["evidence_timecode"], re.I)
                if frame_match or bare_match:
                    frame_rows += 1
                    match = frame_match or bare_match
                    self.assertEqual(converted["start"]["frame"], int(match.group(1)))
                    self.assertIsInstance(converted["end"]["frame"], int)
                else:
                    self.assertIsNone(converted["start"]["frame"])
                    self.assertIsNone(converted["end"]["frame"])
                pts_match = re.search(r"(?:frame\s+)?PTS\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", legacy["evidence_timecode"], re.I)
                if pts_match:
                    pts_rows += 1
                    time_base = re.search(r"\btime_base\s+([1-9]\d*/[1-9]\d*)", legacy["evidence_timecode"], re.I)
                    self.assertIsNotNone(time_base)
                    self.assertEqual(converted["start"]["pts"], int(pts_match.group(1)))
                    self.assertEqual(converted["end"]["pts"], int(pts_match.group(2)))
                    self.assertEqual(converted["start"]["time_base"], time_base.group(1))
                    self.assertEqual(converted["end"]["time_base"], time_base.group(1))
                else:
                    self.assertIsNone(converted["start"]["pts"])
                    self.assertIsNone(converted["end"]["pts"])
                    self.assertIsNone(converted["start"]["time_base"])
                    self.assertIsNone(converted["end"]["time_base"])
            for previous, following in zip(evidence["shots"], evidence["shots"][1:]):
                if previous["end"]["frame"] is not None and following["start"]["frame"] is not None:
                    self.assertEqual(previous["end"]["frame"], following["start"]["frame"])
            self.assertEqual(evidence["source_start"], evidence["shots"][0]["start"])
            self.assertEqual(evidence["source_end"], evidence["shots"][-1]["end"])
        self.assertEqual(frame_rows, 2058)
        self.assertEqual(pts_rows, 311)

    def test_explicit_shot_fallbacks_survive_high_risk_axis_mapping(self) -> None:
        explicit_fallback_rows = 0
        missing_fallback_rows = 0
        high_risk_rows = 0
        high_risk_missing_fallback = 0
        high_axis_counts = {"camera": 0, "performance": 0, "continuity": 0}
        for source in self.sources:
            shot_rows, _rule_rows = parse_tables(source.read_text(encoding="utf-8"))
            evidence = build_evidence(source)
            source_missing_high_risk_fallbacks = 0
            for legacy, shot in zip(shot_rows, evidence["shots"]):
                fallback = extract_legacy_fallback(legacy["AI_complexity"])
                risk = split_risk(legacy["AI_complexity"])
                if fallback is not None:
                    explicit_fallback_rows += 1
                else:
                    missing_fallback_rows += 1
                high_axes = [axis for axis in ("camera", "performance", "continuity") if risk[axis]["level"] in {"HIGH", "CRITICAL"}]
                for axis in high_axes:
                    high_axis_counts[axis] += 1
                    if fallback is not None:
                        self.assertEqual(shot["fallback"][axis], fallback)
                if high_axes:
                    high_risk_rows += 1
                    if fallback is None:
                        high_risk_missing_fallback += 1
                        source_missing_high_risk_fallbacks += 1
                        self.assertFalse(any("no explicit FALLBACK" in item for item in shot["unknowns"]))
                        for axis in high_axes:
                            self.assertIn(shot["shot_id"], shot["fallback"][axis])
            if source_missing_high_risk_fallbacks:
                self.assertTrue(
                    any(
                        warning.startswith(f"{source_missing_high_risk_fallbacks} high-risk Shot rows")
                        for warning in evidence["validation_warnings"]
                    )
                )
        self.assertEqual(explicit_fallback_rows, 1579)
        self.assertEqual(missing_fallback_rows, 764)
        self.assertEqual(high_risk_rows, 1922)
        self.assertEqual(high_risk_missing_fallback, 599)
        self.assertEqual(high_axis_counts, {"camera": 1034, "performance": 1788, "continuity": 1669})

    def test_sound_of_metal_signal_is_auxiliary_not_semantic_audio(self) -> None:
        source = next(path for path in self.sources if path.stem.startswith("SOUND_OF_METAL"))
        evidence = build_evidence(source)
        self.assertEqual(evidence["audio_evidence_status"], "SIGNAL_MEASURED_NOT_AUDITIONED")
        self.assertEqual(len(evidence["auxiliary_evidence"]), 1)
        self.assertEqual(evidence["auxiliary_evidence"][0]["status"], "SIGNAL_MEASURED_NOT_AUDITIONED")
        self.assertTrue(all(rule["promotion_status"] == "BLOCKED_BY_UNKNOWN" for rule in evidence["candidate_rules"]))

    def test_bear_missing_non_applicability_is_preserved_as_null_lineage(self) -> None:
        source = next(path for path in self.sources if path.stem == "THE_BEAR_S01E07_REVIEW_EVIDENCE_V0.1")
        evidence = build_evidence(source)
        self.assertEqual(len(evidence["candidate_rules"]), 4)
        self.assertTrue(all(rule["legacy_migration"]["non_applicability"] is None for rule in evidence["candidate_rules"]))
        self.assertTrue(all(rule["not_applicable_when"] == ["No non-applicability boundary is authorized before human review."] for rule in evidence["candidate_rules"]))

    def test_known_absent_legacy_artifact_claims_are_closed(self) -> None:
        expected = {
            "brooklyn-nine-nine/BROOKLYN_NINE_NINE_S05E14_THE_BOX_VISUAL_EVIDENCE_V0.1.md": 2,
            "house-of-the-dragon/HOUSE_OF_THE_DRAGON_S01E08_THRONE_ROOM_EVIDENCE_V0.1.md": 1,
            "marriage-story/MARRIAGE_STORY_2019_APARTMENT_SEQUENCE_EVIDENCE_V0.1.md": 4,
            "mr-robot/MR_ROBOT_S04E07_ACT_FOUR_VISUAL_EVIDENCE_V0.1.md": 1,
            "the-devil-wears-prada/THE_DEVIL_WEARS_PRADA_2006_CERULEAN_CORRECTION_EVIDENCE_V0.1.md": 1,
            "the-last-of-us/THE_LAST_OF_US_S01E06_BEDROOM_VISUAL_EVIDENCE_V0.1.md": 2,
            "the-martian/THE_MARTIAN_2015_MULTI_SPACE_OBJECT_STATE_EDITORIAL_SEQUENCE_VISUAL_EVIDENCE_V0.1.md": 2,
        }
        total = 0
        for relative, count in expected.items():
            source = REPO_ROOT / "research" / "evidence" / relative
            text = source.read_text(encoding="utf-8")
            self.assertEqual(text.count("ABSENT_LEGACY_ARTIFACT"), count, relative)
            self.assertNotIn("does not claim that JSON exists yet", text, relative)
            self.assertNotIn("will be the canonical machine-readable conversion output", text, relative)
            self.assertTrue(source.with_suffix(".scene-evidence.json").is_file(), relative)
            self.assertIn("research/validation/scene-evidence-validation.json", text, relative)
            total += count
        self.assertEqual(total, 13)

    def test_output_name_and_cli_check_are_deterministic(self) -> None:
        source = self.sources[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(main([str(source), "--output-root", str(root)]), 0)
            destination = output_path(source, root)
            self.assertEqual(destination.name, f"{source.stem}.scene-evidence.json")
            first = destination.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main([str(source), "--output-root", str(root), "--check"]), 0)
                self.assertEqual(main([str(source), "--output-root", str(root)]), 0)
            self.assertEqual(destination.read_bytes(), first)
            payload = json.loads(destination.read_text(encoding="utf-8"))
            payload["validation_status"] = "NOT_VALIDATED"
            destination.write_text(json.dumps(payload), encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(source), "--output-root", str(root), "--check"]), 1)


if __name__ == "__main__":
    unittest.main()
