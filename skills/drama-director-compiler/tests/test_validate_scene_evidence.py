#!/usr/bin/env python3
"""Minimum regression tests for validate_scene_evidence.py."""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import validate_scene_evidence as validator_module  # noqa: E402
from validate_scene_evidence import load_json, main, validate_evidence  # noqa: E402


SCHEMA = load_json(SKILL_ROOT / "references" / "scene-evidence.schema.json")
EVIDENCE_ID = "TEST-WORK-SCENE-001"
REPOSITORY_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "repository-integration.scene-evidence.json"


def time_point(seconds: float, frame: int) -> dict[str, Any]:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining = seconds % 60
    return {
        "timecode": f"{hours:02d}:{minutes:02d}:{remaining:06.3f}",
        "seconds": seconds,
        "frame": frame,
        "pts": frame,
        "time_base": "1/24",
    }


def claim(claim_id: str, value: str, source_refs: list[str], status: str = "PICTURE_OBSERVED") -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "status": status,
        "value": value,
        "source_refs": source_refs,
        "notes": "Synthetic project-original validator fixture.",
    }


def risk(level: str = "LOW") -> dict[str, Any]:
    return {
        "camera": {"level": level, "reasons": ["Synthetic camera test state."]},
        "performance": {"level": "LOW", "reasons": ["Synthetic performance test state."]},
        "continuity": {"level": "LOW", "reasons": ["Synthetic continuity test state."]},
    }


def fallback(camera: str | None = None) -> dict[str, Any]:
    return {
        "camera": camera,
        "performance": None,
        "continuity": None,
        "project_original_only": True,
    }


def make_shot(order: int, start: float, end: float) -> dict[str, Any]:
    shot_id = f"{EVIDENCE_ID}-S{order:03d}"
    prefix = f"S{order:03d}"
    return {
        "shot_id": shot_id,
        "order": order,
        "completeness": "COMPLETE_VISIBLE_SHOT",
        "start": time_point(start, int(round(start * 24))),
        "end": time_point(end, int(round(end * 24))),
        "duration": end - start,
        "shot_size": claim(f"{prefix}-SIZE", "A neutral project-original relation view is visible.", [shot_id]),
        "camera_height": claim(f"{prefix}-HEIGHT", "Camera height is visually stable within the shot.", [shot_id]),
        "camera_angle": claim(f"{prefix}-ANGLE", "A neutral eye-level-like angle is visible.", [shot_id]),
        "camera_motion": claim(f"{prefix}-MOTION", "Frame edges remain stable in the sampled interval.", [shot_id]),
        "camera_start": claim(f"{prefix}-CAM-START", "The opening composition contains two abstract bodies.", [shot_id]),
        "camera_path": claim(f"{prefix}-CAM-PATH", "No discrete camera-path change is visible.", [shot_id]),
        "camera_end": claim(f"{prefix}-CAM-END", "The closing composition retains the same visible zone.", [shot_id]),
        "focus_strategy": claim(f"{prefix}-FOCUS", "Both primary body regions remain readable.", [shot_id]),
        "spatial_zone": [claim(f"{prefix}-ZONE", "Project-original zone Z-A is visible.", [shot_id])],
        "axis_and_screen_direction": claim(f"{prefix}-AXIS", "Left/right screen positions remain readable within the shot.", [shot_id]),
        "abstract_role_labels": [],
        "blocking": claim(f"{prefix}-BLOCK", "Two bodies occupy separate sides of the frame.", [shot_id]),
        "visible_action": claim(f"{prefix}-ACTION", "One head turns while the other body remains seated.", [shot_id]),
        "visible_state_in": claim(f"{prefix}-STATE-IN", "Both bodies are visible at shot start.", [shot_id]),
        "visible_state_out": claim(f"{prefix}-STATE-OUT", "Both bodies remain visible at shot end.", [shot_id]),
        "event_or_reaction": claim(f"{prefix}-EVENT", "A head-direction change is visible; cause is unknown.", [shot_id]),
        "performance_beat": claim(f"{prefix}-PERF", "Head and hand positions change within the shot.", [shot_id]),
        "edit_in": claim(f"{prefix}-EDIT-IN", "The shot begins at a visible edit boundary.", [shot_id]),
        "edit_out": claim(f"{prefix}-EDIT-OUT", "The shot ends at a visible edit boundary.", [shot_id]),
        "cut_motivation": claim(f"{prefix}-CUT-MOTIVE", "The edit may redistribute visible information.", [shot_id], "INFERRED"),
        "narrative_function": claim(f"{prefix}-FUNCTION", "The view may preserve spatial legibility.", [shot_id], "INFERRED"),
        "picture_status": "PICTURE_OBSERVED",
        "audio_status": "AUDIO_UNKNOWN",
        "text_anchor_status": "TEXT_ANCHOR_NOT_USED",
        "AI_complexity": risk(),
        "fallback": fallback(),
        "unknowns": ["Exact identity, dialogue, sound, intention, and production method remain unknown."],
    }


def make_valid_evidence() -> dict[str, Any]:
    shot_1 = f"{EVIDENCE_ID}-S001"
    shot_2 = f"{EVIDENCE_ID}-S002"
    unknown_audio_claims = {
        key: claim(f"AUDIO-{index:02d}", "Audio was not directly observed.", [], "UNKNOWN")
        for index, key in enumerate(
            (
                "dialogue_overlap",
                "silence_intervals",
                "ambience",
                "score_entry",
                "score_exit",
                "sound_before_image",
                "offscreen_sound",
                "sound_bridge",
                "subjective_sound",
                "object_sound",
                "audio_information_change",
            ),
            start=1,
        )
    }
    return {
        "schema_version": "scene-evidence/0.1",
        "evidence_id": EVIDENCE_ID,
        "work_id": "TEST-WORK",
        "scene_problem": {
            "primary": "DIALOGUE_POWER_TRANSFER",
            "secondary": [],
            "status": "INFERRED",
            "source_refs": [shot_1, shot_2],
        },
        "scene_unit_type": "NATURAL_CONTINUOUS_SCENE",
        "boundary_status": "NATURAL_START_END_VERIFIED",
        "boundary_evidence": claim("BOUNDARY-EVIDENCE", "Visible edit boundaries contain the selected scene.", [shot_1, shot_2]),
        "production_take_status": "PRODUCTION_METHOD_UNKNOWN",
        "source_identity_status": "SOURCE_OR_FILENAME_SUPPLIED",
        "source_start": time_point(0.0, 0),
        "source_end": time_point(2.0, 48),
        "duration": 2.0,
        "time_tolerance_seconds": 0.001,
        "picture_evidence_status": "PICTURE_OBSERVED",
        "audio_evidence_status": "AUDIO_UNKNOWN",
        "text_anchor_status": "TEXT_ANCHOR_NOT_USED",
        "scene_dramatic_structure": {
            "start_state": claim("DS-START", "Two abstract bodies share a project-original zone.", [shot_1]),
            "objectives": [claim("DS-OBJECTIVE", "A possible information objective is inferred.", [shot_1], "INFERRED")],
            "obstacle": claim("DS-OBSTACLE", "The obstacle is not established by picture.", [], "UNKNOWN"),
            "event_point": claim("DS-EVENT", "A visible head-direction change occurs.", [shot_1]),
            "reaction_point": claim("DS-REACTION", "A later body-state change occurs.", [shot_2]),
            "turn": claim("DS-TURN", "The ordered changes may form a turn.", [shot_1, shot_2], "INFERRED"),
            "end_state": claim("DS-END", "The bodies occupy a changed visible relation.", [shot_2]),
        },
        "spatial_geometry": claim("SCENE-GEOMETRY", "One project-original zone with two screen sides is visible.", [shot_1, shot_2]),
        "axis": claim("SCENE-AXIS", "A consistent screen-side relation is inferred across the cut.", [shot_1, shot_2], "INFERRED"),
        "POV": claim("SCENE-POV", "The coverage is inferred to be action-aligned rather than optical POV.", [shot_1, shot_2], "INFERRED"),
        "audience_information": claim("SCENE-AUDIENCE", "The audience sees both body-state changes.", [shot_1, shot_2]),
        "shots": [make_shot(1, 0.0, 1.0), make_shot(2, 1.0, 2.0)],
        "stats": {
            "unit": "VISIBLE_SHOT",
            "shot_count": 2,
            "total_duration": 2.0,
            "mean_duration": 1.0,
            "median_duration": 1.0,
            "duration_bins": {"1_to_lt_2": 2},
        },
        "audio_audit": {
            **unknown_audio_claims,
            "audio_unknowns": ["All semantic sound facts remain unknown."],
        },
        "text_anchors": [],
        "methods": [
            {
                "method_id": "METHOD-SYNTHETIC-FIXTURE",
                "method_type": "STRUCTURAL_CONVERSION",
                "status": "REPOSITORY_REPRODUCIBLE",
                "description": "Generate a project-original in-memory Scene Evidence fixture for validator tests.",
                "repository_command": "python3 -m unittest discover -s skills/drama-director-compiler/tests",
                "tool_version_status": "VERSION_RECORDED",
                "source_refs": [],
                "unknowns": [],
            }
        ],
        "auxiliary_evidence": [],
        "continuity_tracks": [],
        "candidate_rules": [
            {
                "candidate_rule_id": "TEST-C01-RELATION-COVERAGE",
                "canonical_rule_family": "RELATION-COVERAGE",
                "scene_problem": "DIALOGUE_POWER_TRANSFER",
                "trigger": "A locked project-original script requires two body-state changes to remain legible.",
                "required_story_facts": [{"claim_id": "DS-START"}],
                "director_decision": "Use project-original relation coverage that preserves both screen sides.",
                "coverage": "One relation view followed by one changed body-state view.",
                "blocking": "Assign neutral side A and side B positions in a project-original set.",
                "POV_effect": "Keep audience access to both visible state changes.",
                "edit_logic": "Cut only after the first visible state is registered.",
                "pacing": "Let each state remain readable without prescribing a source-derived duration.",
                "audio_logic": claim("RULE-AUDIO", "Audio remains unknown and is not part of this candidate.", [], "UNKNOWN"),
                "continuity": "Preserve project-original side and body-state ledgers.",
                "AI_risk": risk(),
                "fallback": fallback(),
                "applicable_when": ["Both state changes are locked project facts."],
                "not_applicable_when": ["Only one body state must be shown."],
                "failure_modes": ["A cut erases the screen-side relation."],
                "counterexample_status": "UNKNOWN",
                "counterexample_ids": [],
                "source_method_ids": ["METHOD-SYNTHETIC-FIXTURE"],
                "evidence_scene_ids": [EVIDENCE_ID],
                "evidence_shot_ids": [shot_1, shot_2],
                "evidence_auxiliary_ids": [],
                "within_source_confidence": "HIGH",
                "transfer_confidence": "LOW",
                "execution_confidence": "MEDIUM",
                "promotion_status": "SINGLE_WORK_CANDIDATE",
                "evidence_status": "HYPOTHESIS",
            }
        ],
        "unknowns": [
            {
                "unknown_id": "UNKNOWN-AUDIO",
                "statement": "Dialogue, ambience, score, and sound causality are unknown.",
                "scope": "AUDIO",
                "blocks_rule_ids": [],
            }
        ],
        "rights_boundary": {
            "media_committed": False,
            "subtitles_committed": False,
            "scripts_or_long_dialogue_committed": False,
            "contains_absolute_local_paths": False,
            "contains_media_hashes": False,
            "reference_surface_terms": ["blue teapot"],
            "surface_inventory_status": "HUMAN_REVIEWED_COMPLETE",
            "prohibited_transfer_content": ["Reference characters, locations, props, dialogue, and signature compositions."],
            "notes": "Only project-original synthetic validator content is included.",
        },
        "validation_status": "NOT_VALIDATED",
        "validation_warnings": [],
    }


def add_signal_auxiliary(evidence: dict[str, Any], method_status: str = "MANUAL_REVIEW_RECORDED") -> str:
    method_id = "METHOD-SIGNAL-001"
    auxiliary_id = "AUX-SIGNAL-001"
    evidence["audio_evidence_status"] = "SIGNAL_MEASURED_NOT_AUDITIONED"
    for shot in evidence["shots"]:
        shot["audio_status"] = "SIGNAL_MEASURED_NOT_AUDITIONED"
    evidence["methods"].append(
        {
            "method_id": method_id,
            "method_type": "DECODED_SIGNAL_MEASUREMENT",
            "status": method_status,
            "description": "Synthetic decoded-signal measurement fixture.",
            "repository_command": None,
            "tool_version_status": "VERSION_RECORDED",
            "source_refs": [],
            "unknowns": ["Signal semantics remain unknown."],
        }
    )
    evidence["auxiliary_evidence"].append(
        {
            "auxiliary_id": auxiliary_id,
            "kind": "DECODED_SIGNAL_THRESHOLD_GROUP",
            "status": "SIGNAL_MEASURED_NOT_AUDITIONED",
            "start": time_point(0.0, 0),
            "end": time_point(1.0, 24),
            "method_id": method_id,
            "measurements": {"synthetic_level": -12.0},
            "source_refs": [f"{EVIDENCE_ID}-S001"],
            "unknowns": ["Sound source, meaning, and perception remain unknown."],
        }
    )
    evidence["candidate_rules"][0]["evidence_auxiliary_ids"] = [auxiliary_id]
    return auxiliary_id


def set_unknown_array(evidence: dict[str, Any], location: str, statement: str) -> None:
    if location == "shot":
        evidence["shots"][0]["unknowns"] = [statement]
    elif location == "audio":
        evidence["audio_audit"]["audio_unknowns"] = [statement]
    elif location == "method":
        evidence["methods"][0]["unknowns"] = [statement]
    elif location == "auxiliary":
        evidence["auxiliary_evidence"] = [
            {
                "auxiliary_id": "AUX-UNKNOWN-001",
                "kind": "OTHER",
                "status": "UNKNOWN",
                "start": time_point(0.0, 0),
                "end": time_point(1.0, 24),
                "method_id": "METHOD-SYNTHETIC-FIXTURE",
                "measurements": {},
                "source_refs": [],
                "unknowns": [statement],
            }
        ]
    elif location == "continuity":
        evidence["continuity_tracks"] = [
            {
                "track_id": "TRACK-UNKNOWN-001",
                "track_kind": "VEHICLE_APPEARANCE",
                "status": "UNKNOWN",
                "statement": "Vehicle identity remains unknown.",
                "source_refs": [],
                "unknowns": [statement],
            }
        ]
    else:
        raise AssertionError(f"unsupported unknown location: {location}")


def replace_claim_status(value: Any, old: str, new: str) -> None:
    if isinstance(value, dict):
        if {"claim_id", "status", "value", "source_refs"}.issubset(value) and value.get("status") == old:
            value["status"] = new
        for child in value.values():
            replace_claim_status(child, old, new)
    elif isinstance(value, list):
        for child in value:
            replace_claim_status(child, old, new)


def error_codes(evidence: dict[str, Any]) -> set[str]:
    report = validate_evidence(evidence, SCHEMA)
    return {issue["code"] for issue in report["issues"] if issue["level"] == "error"}


class SceneEvidenceValidatorTests(unittest.TestCase):
    def test_valid_scene_evidence_passes(self) -> None:
        report = validate_evidence(make_valid_evidence(), SCHEMA)
        self.assertTrue(report["passed"], json.dumps(report["issues"], ensure_ascii=False, indent=2))

    def test_cli_accepts_valid_scene_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence_path = Path(directory) / "scene-evidence.json"
            evidence_path.write_text(json.dumps(make_valid_evidence(), ensure_ascii=False), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = main([str(evidence_path)])
            report = json.loads(stdout.getvalue())
        self.assertEqual(result, 0)
        self.assertEqual(report["status"], "PASS_STRUCTURAL")
        self.assertTrue(report["structural_validation_is_not_creative_approval"])
        self.assertEqual(report["total_scenes"], 1)
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["failed"], 0)
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["total_shots"], 2)
        self.assertEqual(report["failed_scene_ids"], [])
        self.assertEqual(report["failed_rule_ids"], [])
        self.assertEqual(report["results"][0]["path"], "scene-evidence.json")

    def test_shot_gap_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["shots"][1]["start"] = time_point(1.1, 26)
        evidence["shots"][1]["duration"] = 0.9
        self.assertIn("SHOT-GAP", error_codes(evidence))

    def test_shot_overlap_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["shots"][1]["start"] = time_point(0.9, 22)
        evidence["shots"][1]["duration"] = 1.1
        self.assertIn("SHOT-OVERLAP", error_codes(evidence))

    def test_missing_shot_reference_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["evidence_shot_ids"].append(f"{EVIDENCE_ID}-S999")
        self.assertIn("RULE-SHOT-REF-MISSING", error_codes(evidence))

    def test_unknown_promoted_to_required_fact_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["scene_dramatic_structure"]["start_state"]["status"] = "UNKNOWN"
        evidence["scene_dramatic_structure"]["start_state"]["source_refs"] = []
        self.assertIn("RULE-REQUIRES-UNKNOWN", error_codes(evidence))

    def test_high_risk_without_fallback_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["shots"][0]["AI_complexity"]["camera"]["level"] = "HIGH"
        evidence["shots"][0]["fallback"]["camera"] = None
        self.assertIn("HIGH-RISK-NO-FALLBACK", error_codes(evidence))

    def test_missing_non_applicability_fails(self) -> None:
        evidence = make_valid_evidence()
        del evidence["candidate_rules"][0]["not_applicable_when"]
        report = validate_evidence(evidence, SCHEMA)
        self.assertTrue(
            any(
                issue["code"] == "SCHEMA-REQUIRED"
                and issue["path"] == "$.candidate_rules[0].not_applicable_when"
                for issue in report["issues"]
            )
        )

    def test_single_source_general_default_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["promotion_status"] = "GENERAL_DEFAULT"
        self.assertIn("RULE-EMBEDDED-PROMOTION", error_codes(evidence))

    def test_audio_rule_without_observed_audio_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["audio_logic"] = claim(
            "RULE-AUDIO", "A sound cue drives the cut.", [f"{EVIDENCE_ID}-S001"], "INFERRED"
        )
        self.assertIn("RULE-AUDIO-WITHOUT-EVIDENCE", error_codes(evidence))

    def test_reference_surface_term_in_rule_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["director_decision"] += " Place the blue teapot at center frame."
        self.assertIn("RULE-SURFACE-COPY", error_codes(evidence))

    def test_inferred_self_reference_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["scene_dramatic_structure"]["objectives"][0]["source_refs"] = ["DS-OBJECTIVE"]
        codes = error_codes(evidence)
        self.assertIn("CLAIM-SELF-REFERENCE", codes)
        self.assertIn("INFERRED-NO-OBSERVED-SOURCE", codes)

    def test_inferred_method_only_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["scene_dramatic_structure"]["objectives"][0]["source_refs"] = [
            "METHOD-SYNTHETIC-FIXTURE"
        ]
        self.assertIn("INFERRED-NO-OBSERVED-SOURCE", error_codes(evidence))

    def test_unknown_audio_directive_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["audio_audit"]["offscreen_sound"]["value"] = (
            "Audio remains unknown; add an offscreen sound cue that drives the cut."
        )
        self.assertIn("AUDIO-UNKNOWN-HIDES-DIRECTIVE", error_codes(evidence))

    def test_unknown_rule_audio_directive_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["audio_logic"]["value"] = (
            "Audio remains unknown; add an offscreen sound cue that drives the cut."
        )
        self.assertIn("RULE-AUDIO-UNKNOWN-HIDES-DIRECTIVE", error_codes(evidence))

    def test_operational_audio_directive_without_audition_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["director_decision"] += " Add a sound cue before the image change."
        self.assertIn("RULE-AUDIO-DIRECTIVE-WITHOUT-EVIDENCE", error_codes(evidence))

    def test_blocked_direct_audition_cannot_prove_audio_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["audio_evidence_status"] = "AUDIO_OBSERVED"
        evidence["methods"].append(
            {
                "method_id": "METHOD-BLOCKED-AUDIO",
                "method_type": "AUDIO_DIRECT_AUDITION",
                "status": "BLOCKED",
                "description": "Direct audition was not performed.",
                "repository_command": None,
                "tool_version_status": "NOT_APPLICABLE",
                "source_refs": [],
                "unknowns": ["All semantic audio remains unknown."],
            }
        )
        self.assertIn("AUDIO-OBSERVED-NO-DIRECT-METHOD", error_codes(evidence))

    def test_blocked_picture_method_cannot_prove_observation(self) -> None:
        evidence = make_valid_evidence()
        evidence["methods"].append(
            {
                "method_id": "METHOD-BLOCKED-PICTURE",
                "method_type": "PICTURE_FRAME_REVIEW",
                "status": "BLOCKED",
                "description": "Picture review was not completed.",
                "repository_command": None,
                "tool_version_status": "NOT_APPLICABLE",
                "source_refs": [],
                "unknowns": ["Picture observation remains unverified."],
            }
        )
        evidence["boundary_evidence"]["source_refs"] = ["METHOD-BLOCKED-PICTURE"]
        self.assertIn("PICTURE-SOURCE-TRACK", error_codes(evidence))

    def test_audio_auxiliary_requires_direct_audition_method(self) -> None:
        evidence = make_valid_evidence()
        evidence["audio_evidence_status"] = "AUDIO_OBSERVED"
        evidence["methods"].append(
            {
                "method_id": "METHOD-DIRECT-AUDIO",
                "method_type": "AUDIO_DIRECT_AUDITION",
                "status": "MANUAL_REVIEW_RECORDED",
                "description": "Synthetic direct-audition method fixture.",
                "repository_command": None,
                "tool_version_status": "NOT_APPLICABLE",
                "source_refs": [],
                "unknowns": [],
            }
        )
        evidence["auxiliary_evidence"].append(
            {
                "auxiliary_id": "AUX-AUDIO-001",
                "kind": "AUDIO_AUDIT_EVENT",
                "status": "AUDIO_OBSERVED",
                "start": time_point(0.0, 0),
                "end": time_point(1.0, 24),
                "method_id": "METHOD-SYNTHETIC-FIXTURE",
                "measurements": {},
                "source_refs": [f"{EVIDENCE_ID}-S001"],
                "unknowns": [],
            }
        )
        self.assertIn("AUXILIARY-AUDIO-METHOD", error_codes(evidence))

    def test_malformed_rights_boundary_reports_schema_error(self) -> None:
        evidence = make_valid_evidence()
        evidence["rights_boundary"] = "bogus"
        self.assertIn("SCHEMA-TYPE", error_codes(evidence))

    def test_home_absolute_path_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["validation_warnings"] = ["See /home/alice/private/notes.txt"]
        self.assertIn("PUBLIC-ABSOLUTE-PATH", error_codes(evidence))

    def test_zero_tolerance_rejects_one_millisecond_mismatch(self) -> None:
        evidence = make_valid_evidence()
        evidence["time_tolerance_seconds"] = 0
        evidence["shots"][1]["start"]["timecode"] = "00:00:01.001"
        self.assertIn("TIMECODE-SECONDS-MISMATCH", error_codes(evidence))

    def test_within_shot_track_cannot_span_two_shots(self) -> None:
        evidence = make_valid_evidence()
        evidence["continuity_tracks"] = [
            {
                "track_id": "TRACK-PERSON-001",
                "track_kind": "PERSON_APPEARANCE",
                "status": "WITHIN_SHOT_OBSERVED",
                "statement": "Two shots are incorrectly grouped as one observed identity.",
                "source_refs": [f"{EVIDENCE_ID}-S001", f"{EVIDENCE_ID}-S002"],
                "unknowns": [],
            }
        ]
        self.assertIn("TRACK-WITHIN-SHOT-SOURCE-COUNT", error_codes(evidence))

    def test_surface_term_uses_word_boundaries(self) -> None:
        evidence = make_valid_evidence()
        evidence["rights_boundary"]["reference_surface_terms"] = ["bus"]
        evidence["candidate_rules"][0]["director_decision"] += " Preserve business-state legibility."
        self.assertNotIn("RULE-SURFACE-COPY", error_codes(evidence))

    def test_external_scene_ids_cannot_fake_embedded_promotion(self) -> None:
        evidence = make_valid_evidence()
        rule = evidence["candidate_rules"][0]
        rule["promotion_status"] = "GENERAL_DEFAULT"
        rule["counterexample_status"] = "VERIFIED_SAME_TRIGGER_FAILURE"
        rule["counterexample_ids"] = ["FAKE-COUNTEREXAMPLE"]
        rule["evidence_scene_ids"] = [EVIDENCE_ID, "FAKE-SCENE-2", "FAKE-SCENE-3"]
        codes = error_codes(evidence)
        self.assertIn("RULE-EMBEDDED-PROMOTION", codes)
        self.assertIn("RULE-EXTERNAL-SCENE-REF", codes)
        self.assertIn("RULE-EMBEDDED-COUNTEREXAMPLE", codes)

    def test_fake_verified_counterexample_fails_even_without_promotion(self) -> None:
        evidence = make_valid_evidence()
        rule = evidence["candidate_rules"][0]
        rule["counterexample_status"] = "VERIFIED_SAME_TRIGGER_FAILURE"
        rule["counterexample_ids"] = ["FAKE-COUNTEREXAMPLE"]
        self.assertIn("RULE-EMBEDDED-COUNTEREXAMPLE", error_codes(evidence))

    def test_signal_dependent_rule_must_be_blocked(self) -> None:
        evidence = make_valid_evidence()
        add_signal_auxiliary(evidence)
        self.assertIn("RULE-SIGNAL-OR-SOUND-UNKNOWN-NOT-BLOCKED", error_codes(evidence))
        evidence["candidate_rules"][0]["promotion_status"] = "BLOCKED_BY_UNKNOWN"
        self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_sound_led_rule_without_audition_must_be_blocked(self) -> None:
        evidence = make_valid_evidence()
        evidence["scene_problem"]["primary"] = "SOUND_LED_CAUSALITY"
        evidence["candidate_rules"][0]["scene_problem"] = "SOUND_LED_CAUSALITY"
        self.assertIn("RULE-SIGNAL-OR-SOUND-UNKNOWN-NOT-BLOCKED", error_codes(evidence))

    def test_alarm_first_audio_directive_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["audio_logic"]["value"] = (
            "Audio remains unknown. On the alarm sound, cut immediately."
        )
        self.assertIn("RULE-AUDIO-UNKNOWN-HIDES-DIRECTIVE", error_codes(evidence))
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["director_decision"] = "When the alarm sounds, cut immediately."
        self.assertIn("RULE-AUDIO-DIRECTIVE-WITHOUT-EVIDENCE", error_codes(evidence))

    def test_score_entry_audio_directive_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["director_decision"] = "Let the score enter before the image."
        self.assertIn("RULE-AUDIO-DIRECTIVE-WITHOUT-EVIDENCE", error_codes(evidence))

    def test_unknown_clause_cannot_hide_score_directive(self) -> None:
        values = (
            "Audio remains unknown, but let the score enter before the image.",
            "Audio remains unknown, but the music should begin before the image.",
        )
        for field in ("director_decision", "audio_logic"):
            for value in values:
                with self.subTest(field=field, value=value):
                    evidence = make_valid_evidence()
                    if field == "audio_logic":
                        evidence["candidate_rules"][0][field]["value"] = value
                        expected_path = "$.candidate_rules[0].audio_logic.value"
                        expected_code = "RULE-AUDIO-UNKNOWN-HIDES-DIRECTIVE"
                    else:
                        evidence["candidate_rules"][0][field] = value
                        expected_path = "$.candidate_rules[0]"
                        expected_code = "RULE-AUDIO-DIRECTIVE-WITHOUT-EVIDENCE"
                    report = validate_evidence(evidence, SCHEMA)
                    self.assertTrue(
                        any(
                            issue["code"] == expected_code and issue["path"] == expected_path
                            for issue in report["issues"]
                        )
                    )

    def test_uncertain_score_entry_without_directive_remains_valid(self) -> None:
        values = (
            "Whether score entry precedes the image remains unknown.",
            "Let audio remain unknown and outside this candidate.",
        )
        for value in values:
            with self.subTest(value=value):
                evidence = make_valid_evidence()
                evidence["candidate_rules"][0]["audio_logic"]["value"] = value
                self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_unknown_axis_cannot_reappear_as_rule_fact(self) -> None:
        values = (
            ("The exact cross-cut axis remains unknown.", "Maintain the same 180-degree axis across every cut."),
            ("The exact cross-cut axis remains unknown.", "The exact cross-cut axis remains unknown, but maintain the same cross-cut axis across every cut."),
            ("The axis remains unknown.", "Maintain the same 180-degree axis across every cut."),
        )
        for unknown_value, rule_value in values:
            with self.subTest(unknown_value=unknown_value, rule_value=rule_value):
                evidence = make_valid_evidence()
                evidence["axis"].update(
                    status="UNKNOWN",
                    value=unknown_value,
                    source_refs=[],
                )
                evidence["candidate_rules"][0]["continuity"] = rule_value
                report = validate_evidence(evidence, SCHEMA)
                self.assertTrue(
                    any(
                        issue["code"] == "RULE-ASSERTS-UNKNOWN-FACT"
                        and issue["path"] == "$.candidate_rules[0].promotion_status"
                        for issue in report["issues"]
                    )
                )

    def test_rule_may_repeat_unknown_as_an_explicit_boundary(self) -> None:
        evidence = make_valid_evidence()
        evidence["axis"].update(
            status="UNKNOWN",
            value="The exact cross-cut axis remains unknown.",
            source_refs=[],
        )
        evidence["candidate_rules"][0]["continuity"] = "The exact cross-cut axis remains unknown."
        self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

        evidence = make_valid_evidence()
        evidence["unknowns"][0].update(
            statement="Cross-cut identity remains unknown.",
            scope="SCENE",
            blocks_rule_ids=[],
        )
        evidence["candidate_rules"][0]["continuity"] = (
            "Use coverage that does not depend on cross-cut identity."
        )
        self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_unregistered_identity_unknown_cannot_reappear_in_rule(self) -> None:
        statements = (
            "Whether the same person returns across the cut remains unknown.",
            "Identity remains unknown.",
        )
        for statement in statements:
            with self.subTest(statement=statement):
                evidence = make_valid_evidence()
                evidence["unknowns"][0].update(
                    statement=statement,
                    scope="SCENE",
                    blocks_rule_ids=[],
                )
                evidence["candidate_rules"][0]["continuity"] = "The same person returns across the cut."
                self.assertIn("RULE-ASSERTS-UNKNOWN-FACT", error_codes(evidence))

                evidence["candidate_rules"][0]["promotion_status"] = "BLOCKED_BY_UNKNOWN"
                self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_unknown_blocks_rule_promotion(self) -> None:
        evidence = make_valid_evidence()
        rule_id = evidence["candidate_rules"][0]["candidate_rule_id"]
        evidence["unknowns"][0]["blocks_rule_ids"] = [rule_id]
        self.assertIn("UNKNOWN-RULE-NOT-BLOCKED", error_codes(evidence))

    def test_unknown_register_must_state_uncertainty(self) -> None:
        evidence = make_valid_evidence()
        evidence["unknowns"][0]["statement"] = "The same person returns across the cut."
        self.assertIn("UNKNOWN-STATEMENT-ASSERTS-FACT", error_codes(evidence))

    def test_blocked_signal_method_cannot_support_inference(self) -> None:
        evidence = make_valid_evidence()
        auxiliary_id = add_signal_auxiliary(evidence, "BLOCKED")
        evidence["candidate_rules"][0]["promotion_status"] = "BLOCKED_BY_UNKNOWN"
        evidence["scene_dramatic_structure"]["objectives"][0]["source_refs"] = [auxiliary_id]
        codes = error_codes(evidence)
        self.assertIn("AUXILIARY-SIGNAL-METHOD-STATUS", codes)
        self.assertIn("INFERRED-NO-OBSERVED-SOURCE", codes)

    def test_unverified_picture_shots_cannot_support_inference(self) -> None:
        evidence = make_valid_evidence()
        evidence["picture_evidence_status"] = "PICTURE_UNVERIFIED"
        for shot in evidence["shots"]:
            shot["picture_status"] = "PICTURE_UNVERIFIED"
        replace_claim_status(evidence, "PICTURE_OBSERVED", "INFERRED")
        self.assertIn("INFERRED-NO-OBSERVED-SOURCE", error_codes(evidence))

    def test_signal_cannot_prove_subjective_semantics(self) -> None:
        evidence = make_valid_evidence()
        auxiliary_id = add_signal_auxiliary(evidence)
        evidence["candidate_rules"][0]["promotion_status"] = "BLOCKED_BY_UNKNOWN"
        objective = evidence["scene_dramatic_structure"]["objectives"][0]
        objective["value"] = "The signal proves subjective hearing loss and audience emotion."
        objective["source_refs"] = [f"{EVIDENCE_ID}-S001", auxiliary_id]
        self.assertIn("SIGNAL-CANNOT-PROVE-SEMANTICS", error_codes(evidence))

    def test_additional_absolute_paths_and_media_extensions_fail(self) -> None:
        cases = (
            "/opt/private/notes.txt",
            "path=/Users/alice/private/notes.txt",
            "scene.webm",
            "scene.m2ts",
        )
        for value in cases:
            with self.subTest(value=value):
                evidence = make_valid_evidence()
                evidence["validation_warnings"] = [value]
                codes = error_codes(evidence)
                expected = "PUBLIC-MEDIA-OR-SUBTITLE" if value.endswith((".webm", ".m2ts")) else "PUBLIC-ABSOLUTE-PATH"
                self.assertIn(expected, codes)

    def test_additional_public_boundary_payloads_fail(self) -> None:
        cases = (
            ("contact-sheet.heic", "PUBLIC-MEDIA-OR-SUBTITLE"),
            ("subtitles.ssa", "PUBLIC-MEDIA-OR-SUBTITLE"),
            ("data:image/png;base64,AAAA", "PUBLIC-DATA-URI"),
            ("data:image/svg+xml,%3Csvg%3E", "PUBLIC-DATA-URI"),
            ("data:text/vtt,WEBVTT", "PUBLIC-DATA-URI"),
            ("-----BEGIN PRIVATE KEY-----", "PUBLIC-CREDENTIAL"),
            ("Authorization: Bearer test-fixture-token", "PUBLIC-CREDENTIAL"),
        )
        for value, expected_code in cases:
            with self.subTest(value=value):
                evidence = make_valid_evidence()
                evidence["validation_warnings"] = [value]
                report = validate_evidence(evidence, SCHEMA)
                self.assertTrue(
                    any(
                        issue["code"] == expected_code
                        and issue["path"] == "$.validation_warnings[0]"
                        for issue in report["issues"]
                    )
                )
        evidence = make_valid_evidence()
        evidence["validation_warnings"] = ["Bearer credentials are prohibited from public evidence."]
        self.assertNotIn("PUBLIC-CREDENTIAL", error_codes(evidence))

    def test_surface_copy_in_ai_risk_and_plural_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["AI_risk"]["camera"]["reasons"].append(
            "Match the blue teapots exactly."
        )
        self.assertIn("RULE-SURFACE-COPY", error_codes(evidence))

    def test_shot_track_status_conflicts_fail(self) -> None:
        evidence = make_valid_evidence()
        evidence["shots"][0]["picture_status"] = "PICTURE_UNVERIFIED"
        self.assertIn("SHOT-PICTURE-CLAIM-CONFLICT", error_codes(evidence))

        evidence = make_valid_evidence()
        evidence["shots"][0]["audio_status"] = "AUDIO_OBSERVED"
        self.assertIn("SHOT-AUDIO-STATUS-CONFLICT", error_codes(evidence))

        evidence = make_valid_evidence()
        evidence["shots"][0]["text_anchor_status"] = "TEXT_ANCHOR_VERIFIED"
        self.assertIn("SHOT-TEXT-STATUS-CONFLICT", error_codes(evidence))

    def test_verified_text_status_requires_anchor(self) -> None:
        evidence = make_valid_evidence()
        evidence["text_anchor_status"] = "TEXT_ANCHOR_VERIFIED"
        self.assertIn("TEXT-STATUS-NO-ANCHOR", error_codes(evidence))

    def test_verified_text_anchor_requires_review_method(self) -> None:
        evidence = make_valid_evidence()
        evidence["text_anchor_status"] = "TEXT_ANCHOR_VERIFIED"
        evidence["text_anchors"] = [
            {
                "anchor_id": "TEXT-ANCHOR-001",
                "status": "TEXT_ANCHOR_VERIFIED",
                "source_type": "SCRIPT",
                "paraphrase": "Synthetic text anchor.",
                "speaker_status": "UNKNOWN",
                "start": time_point(0.0, 0),
                "end": time_point(1.0, 24),
            }
        ]
        self.assertIn("TEXT-ANCHOR-NO-REVIEW-METHOD", error_codes(evidence))

    def test_declared_warnings_are_preserved_in_report(self) -> None:
        evidence = make_valid_evidence()
        evidence["validation_warnings"] = ["Human review remains pending."]
        report = validate_evidence(evidence, SCHEMA)
        self.assertEqual(report["warning_count"], 1)
        self.assertEqual(report["issues"][-1]["code"], "EVIDENCE-DECLARED-WARNING")

    def test_load_error_counts_as_scene(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            valid_path = Path(directory) / "valid.scene-evidence.json"
            invalid_path = Path(directory) / "invalid.scene-evidence.json"
            valid_path.write_text(json.dumps(make_valid_evidence()), encoding="utf-8")
            invalid_path.write_text("{", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = main([str(valid_path), str(invalid_path)])
            report = json.loads(stdout.getvalue())
        self.assertEqual(result, 1)
        self.assertEqual(report["total_scenes"], 2)
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["failed"], 1)

    def test_method_source_reference_must_resolve(self) -> None:
        evidence = make_valid_evidence()
        evidence["methods"][0]["source_refs"] = ["BOGUS-REF"]
        self.assertIn("METHOD-SOURCE-REF-MISSING", error_codes(evidence))

    def test_rule_method_must_be_active(self) -> None:
        evidence = make_valid_evidence()
        evidence["methods"][0]["status"] = "BLOCKED"
        evidence["methods"][0]["repository_command"] = None
        self.assertIn("RULE-METHOD-INACTIVE", error_codes(evidence))

    def test_shot_id_must_use_evidence_namespace(self) -> None:
        evidence = make_valid_evidence()
        evidence["shots"][0]["shot_id"] = "OTHER-NAMESPACE-S001"
        self.assertIn("SHOT-ID-NAMESPACE", error_codes(evidence))

    def test_observed_auxiliary_requires_nonempty_source_refs(self) -> None:
        evidence = make_valid_evidence()
        evidence["methods"].append(
            {
                "method_id": "METHOD-PICTURE-001",
                "method_type": "PICTURE_FRAME_REVIEW",
                "status": "MANUAL_REVIEW_RECORDED",
                "description": "Synthetic picture review fixture.",
                "repository_command": None,
                "tool_version_status": "NOT_APPLICABLE",
                "source_refs": [],
                "unknowns": [],
            }
        )
        evidence["auxiliary_evidence"] = [
            {
                "auxiliary_id": "AUX-PICTURE-001",
                "kind": "PICTURE_CUT_AUDIT",
                "status": "PICTURE_OBSERVED",
                "start": time_point(0.0, 0),
                "end": time_point(1.0, 24),
                "method_id": "METHOD-PICTURE-001",
                "measurements": {},
                "source_refs": [],
                "unknowns": [],
            }
        ]
        self.assertIn("AUXILIARY-SOURCE-REQUIRED", error_codes(evidence))

    def test_auxiliary_cycle_does_not_fake_a_real_track(self) -> None:
        evidence = make_valid_evidence()
        evidence["auxiliary_evidence"] = [
            {
                "auxiliary_id": auxiliary_id,
                "kind": "OTHER",
                "status": "INFERRED",
                "start": time_point(0.0, 0),
                "end": time_point(1.0, 24),
                "method_id": "METHOD-SYNTHETIC-FIXTURE",
                "measurements": {},
                "source_refs": [other_id],
                "unknowns": [],
            }
            for auxiliary_id, other_id in (("AUX-CYCLE-001", "AUX-CYCLE-002"), ("AUX-CYCLE-002", "AUX-CYCLE-001"))
        ]
        self.assertIn("AUXILIARY-NO-REAL-SOURCE", error_codes(evidence))

    def test_auxiliary_chain_resolves_to_real_picture_track(self) -> None:
        evidence = make_valid_evidence()
        evidence["methods"].append(
            {
                "method_id": "METHOD-PICTURE-CHAIN",
                "method_type": "PICTURE_FRAME_REVIEW",
                "status": "MANUAL_REVIEW_RECORDED",
                "description": "Synthetic picture review fixture.",
                "repository_command": None,
                "tool_version_status": "NOT_APPLICABLE",
                "source_refs": [],
                "unknowns": [],
            }
        )
        evidence["auxiliary_evidence"] = [
            {
                "auxiliary_id": "AUX-PICTURE-CHAIN",
                "kind": "PICTURE_CUT_AUDIT",
                "status": "PICTURE_OBSERVED",
                "start": time_point(0.0, 0),
                "end": time_point(1.0, 24),
                "method_id": "METHOD-PICTURE-CHAIN",
                "measurements": {},
                "source_refs": [f"{EVIDENCE_ID}-S001"],
                "unknowns": [],
            },
            {
                "auxiliary_id": "AUX-INFERRED-CHAIN",
                "kind": "OTHER",
                "status": "INFERRED",
                "start": time_point(0.0, 0),
                "end": time_point(1.0, 24),
                "method_id": "METHOD-SYNTHETIC-FIXTURE",
                "measurements": {},
                "source_refs": ["AUX-PICTURE-CHAIN"],
                "unknowns": [],
            },
        ]
        self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_every_auxiliary_source_must_resolve_to_a_real_track(self) -> None:
        for status in ("PICTURE_OBSERVED", "INFERRED"):
            with self.subTest(status=status):
                evidence = make_valid_evidence()
                method_id = "METHOD-SYNTHETIC-FIXTURE"
                if status == "PICTURE_OBSERVED":
                    method_id = "METHOD-PICTURE-MIXED"
                    evidence["methods"].append(
                        {
                            "method_id": method_id,
                            "method_type": "PICTURE_FRAME_REVIEW",
                            "status": "MANUAL_REVIEW_RECORDED",
                            "description": "Synthetic picture review fixture.",
                            "repository_command": None,
                            "tool_version_status": "NOT_APPLICABLE",
                            "source_refs": [],
                            "unknowns": [],
                        }
                    )
                evidence["auxiliary_evidence"] = [
                    {
                        "auxiliary_id": "AUX-MIXED-SOURCES",
                        "kind": "OTHER",
                        "status": status,
                        "start": time_point(0.0, 0),
                        "end": time_point(1.0, 24),
                        "method_id": method_id,
                        "measurements": {},
                        "source_refs": [f"{EVIDENCE_ID}-S001", "DS-OBSTACLE"],
                        "unknowns": [],
                    }
                ]
                self.assertIn("AUXILIARY-SOURCE-TRACK", error_codes(evidence))

    def test_boolean_const_rejects_zero_one_and_string(self) -> None:
        for value in (0, 1, "false"):
            with self.subTest(value=value):
                evidence = make_valid_evidence()
                evidence["rights_boundary"]["media_committed"] = value
                self.assertIn("SCHEMA-TYPE", error_codes(evidence))

    def test_verified_boundary_cannot_use_unknown_evidence(self) -> None:
        evidence = make_valid_evidence()
        evidence["boundary_evidence"].update(
            status="UNKNOWN",
            value="Natural scene boundaries remain unknown.",
            source_refs=[],
        )
        self.assertIn("BOUNDARY-VERIFIED-FROM-UNKNOWN", error_codes(evidence))

    def test_verified_boundary_must_reach_both_endpoint_shots(self) -> None:
        for refs, expected in (
            ([f"{EVIDENCE_ID}-S001"], "BOUNDARY-END-SOURCE-MISSING"),
            ([f"{EVIDENCE_ID}-S002"], "BOUNDARY-START-SOURCE-MISSING"),
        ):
            with self.subTest(refs=refs):
                evidence = make_valid_evidence()
                evidence["boundary_evidence"]["source_refs"] = refs
                self.assertIn(expected, error_codes(evidence))

    def test_verified_boundary_cannot_reach_endpoint_through_unknown_track(self) -> None:
        for direct_ref, wrapped_ref, expected in (
            (f"{EVIDENCE_ID}-S001", f"{EVIDENCE_ID}-S002", "BOUNDARY-END-SOURCE-MISSING"),
            (f"{EVIDENCE_ID}-S002", f"{EVIDENCE_ID}-S001", "BOUNDARY-START-SOURCE-MISSING"),
        ):
            with self.subTest(wrapped_ref=wrapped_ref):
                evidence = make_valid_evidence()
                evidence["continuity_tracks"] = [
                    {
                        "track_id": "TRACK-UNKNOWN-BOUNDARY",
                        "track_kind": "VEHICLE_APPEARANCE",
                        "status": "UNKNOWN",
                        "statement": "Boundary linkage remains unknown.",
                        "source_refs": [wrapped_ref],
                        "unknowns": ["Boundary linkage remains unknown."],
                    }
                ]
                evidence["boundary_evidence"]["source_refs"] = [direct_ref, "TRACK-UNKNOWN-BOUNDARY"]
                self.assertIn(expected, error_codes(evidence))

    def test_boundary_status_matches_first_and_last_shot_completeness(self) -> None:
        evidence = make_valid_evidence()
        evidence["scene_unit_type"] = "SELECTED_INTERNAL_ENVELOPE"
        evidence["boundary_status"] = "BOTH_INTERNAL_SELECTED"
        codes = error_codes(evidence)
        self.assertIn("BOUNDARY-START-COMPLETENESS", codes)
        self.assertIn("BOUNDARY-END-COMPLETENESS", codes)

    def test_natural_scene_unit_rejects_internal_boundary(self) -> None:
        evidence = make_valid_evidence()
        evidence["boundary_status"] = "START_INTERNAL_END_VERIFIED"
        evidence["shots"][0]["completeness"] = "PARTIAL_AT_START"
        self.assertIn("SCENE-UNIT-BOUNDARY-CONFLICT", error_codes(evidence))

    def test_boundary_status_completeness_positive_matrix(self) -> None:
        cases = (
            ("NATURAL_START_END_VERIFIED", "COMPLETE_VISIBLE_SHOT", "COMPLETE_VISIBLE_SHOT"),
            ("START_INTERNAL_END_VERIFIED", "PARTIAL_AT_START", "COMPLETE_VISIBLE_SHOT"),
            ("START_VERIFIED_END_INTERNAL", "COMPLETE_VISIBLE_SHOT", "PARTIAL_AT_END"),
            ("BOTH_INTERNAL_SELECTED", "PARTIAL_AT_START", "PARTIAL_AT_END"),
        )
        for boundary_status, first, last in cases:
            with self.subTest(boundary_status=boundary_status):
                evidence = make_valid_evidence()
                evidence["scene_unit_type"] = "CONTIGUOUS_EDITORIAL_SEQUENCE"
                evidence["boundary_status"] = boundary_status
                evidence["shots"][0]["completeness"] = first
                evidence["shots"][-1]["completeness"] = last
                self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

        evidence = make_valid_evidence()
        evidence["scene_unit_type"] = "CONTIGUOUS_EDITORIAL_SEQUENCE"
        evidence["boundary_status"] = "BOUNDARY_UNKNOWN"
        evidence["boundary_evidence"].update(
            status="UNKNOWN",
            value="Scene boundaries remain unknown.",
            source_refs=[],
        )
        self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_unknown_text_anchor_cannot_support_claim_scene_problem_or_role(self) -> None:
        for target, expected in (
            ("claim", "TEXT-ANCHOR-SOURCE-TRACK"),
            ("scene_problem", "SCENE-PROBLEM-TEXT-SOURCE-TRACK"),
            ("role", "ROLE-TEXT-SOURCE-TRACK"),
        ):
            with self.subTest(target=target):
                evidence = make_valid_evidence()
                evidence["text_anchor_status"] = "TEXT_ANCHOR_PARTIAL"
                evidence["text_anchors"] = [
                    {
                        "anchor_id": "TEXT-ANCHOR-UNKNOWN-001",
                        "status": "TEXT_ANCHOR_UNKNOWN",
                        "source_type": "SCRIPT",
                        "paraphrase": "Synthetic anchor remains unverified.",
                        "speaker_status": "UNKNOWN",
                        "start": time_point(0.0, 0),
                        "end": time_point(1.0, 24),
                    }
                ]
                evidence["methods"].append(
                    {
                        "method_id": "METHOD-TEXT-001",
                        "method_type": "TEXT_ANCHOR_REVIEW",
                        "status": "MANUAL_REVIEW_RECORDED",
                        "description": "Synthetic text review fixture.",
                        "repository_command": None,
                        "tool_version_status": "NOT_APPLICABLE",
                        "source_refs": [],
                        "unknowns": [],
                    }
                )
                if target == "claim":
                    evidence["scene_dramatic_structure"]["obstacle"].update(
                        status="TEXT_ANCHOR",
                        value="A synthetic obstacle label is anchored.",
                        source_refs=["TEXT-ANCHOR-UNKNOWN-001"],
                    )
                elif target == "scene_problem":
                    evidence["scene_problem"].update(
                        status="TEXT_ANCHOR",
                        source_refs=["TEXT-ANCHOR-UNKNOWN-001"],
                    )
                else:
                    evidence["shots"][0]["abstract_role_labels"] = [
                        {
                            "appearance_id": "BODY-A",
                            "functional_role": "receiver",
                            "status": "TEXT_ANCHOR",
                            "appearance_identity_status": "PICTURE_OBSERVED_WITHIN_SHOT",
                            "appearance_track_id": None,
                            "source_refs": ["TEXT-ANCHOR-UNKNOWN-001"],
                        }
                    ]
                self.assertIn(expected, error_codes(evidence))

    def test_inferred_sources_cannot_mix_unknown_text_anchor_with_valid_shot(self) -> None:
        for target, expected in (
            ("claim", "CLAIM-UNKNOWN-TEXT-ANCHOR"),
            ("scene_problem", "SCENE-PROBLEM-UNKNOWN-TEXT-ANCHOR"),
            ("role", "ROLE-UNKNOWN-TEXT-ANCHOR"),
        ):
            with self.subTest(target=target):
                evidence = make_valid_evidence()
                evidence["text_anchor_status"] = "TEXT_ANCHOR_PARTIAL"
                evidence["text_anchors"] = [
                    {
                        "anchor_id": "TEXT-ANCHOR-PARTIAL-001",
                        "status": "TEXT_ANCHOR_PARTIAL",
                        "source_type": "SCRIPT",
                        "paraphrase": "Synthetic reviewed anchor.",
                        "speaker_status": "UNKNOWN",
                        "start": time_point(0.0, 0),
                        "end": time_point(1.0, 24),
                    },
                    {
                        "anchor_id": "TEXT-ANCHOR-UNKNOWN-001",
                        "status": "TEXT_ANCHOR_UNKNOWN",
                        "source_type": "SCRIPT",
                        "paraphrase": "Synthetic anchor remains unverified.",
                        "speaker_status": "UNKNOWN",
                        "start": time_point(0.0, 0),
                        "end": time_point(1.0, 24),
                    },
                ]
                evidence["methods"].append(
                    {
                        "method_id": "METHOD-TEXT-001",
                        "method_type": "TEXT_ANCHOR_REVIEW",
                        "status": "MANUAL_REVIEW_RECORDED",
                        "description": "Synthetic text review fixture.",
                        "repository_command": None,
                        "tool_version_status": "NOT_APPLICABLE",
                        "source_refs": [],
                        "unknowns": [],
                    }
                )
                mixed_refs = [f"{EVIDENCE_ID}-S001", "TEXT-ANCHOR-UNKNOWN-001"]
                if target == "claim":
                    evidence["scene_dramatic_structure"]["obstacle"].update(
                        status="INFERRED",
                        value="A synthetic obstacle may be inferred.",
                        source_refs=mixed_refs,
                    )
                elif target == "scene_problem":
                    evidence["scene_problem"].update(status="INFERRED", source_refs=mixed_refs)
                else:
                    evidence["shots"][0]["abstract_role_labels"] = [
                        {
                            "appearance_id": "BODY-A",
                            "functional_role": "receiver",
                            "status": "INFERRED",
                            "appearance_identity_status": "PICTURE_OBSERVED_WITHIN_SHOT",
                            "appearance_track_id": None,
                            "source_refs": mixed_refs,
                        }
                    ]
                self.assertIn(expected, error_codes(evidence))

    def test_inferred_text_sources_require_active_review_method_even_with_valid_shot(self) -> None:
        for target, expected in (
            ("claim", "CLAIM-TEXT-NO-REVIEW-METHOD"),
            ("scene_problem", "SCENE-PROBLEM-TEXT-NO-REVIEW-METHOD"),
            ("role", "ROLE-TEXT-NO-REVIEW-METHOD"),
        ):
            with self.subTest(target=target):
                evidence = make_valid_evidence()
                evidence["text_anchor_status"] = "TEXT_ANCHOR_PARTIAL"
                evidence["text_anchors"] = [
                    {
                        "anchor_id": "TEXT-ANCHOR-PARTIAL-001",
                        "status": "TEXT_ANCHOR_PARTIAL",
                        "source_type": "SCRIPT",
                        "paraphrase": "Synthetic reviewed anchor.",
                        "speaker_status": "UNKNOWN",
                        "start": time_point(0.0, 0),
                        "end": time_point(1.0, 24),
                    }
                ]
                mixed_refs = [f"{EVIDENCE_ID}-S001", "TEXT-ANCHOR-PARTIAL-001"]
                if target == "claim":
                    evidence["scene_dramatic_structure"]["obstacle"].update(
                        status="INFERRED",
                        value="A synthetic obstacle may be inferred.",
                        source_refs=mixed_refs,
                    )
                elif target == "scene_problem":
                    evidence["scene_problem"].update(status="INFERRED", source_refs=mixed_refs)
                else:
                    evidence["shots"][0]["abstract_role_labels"] = [
                        {
                            "appearance_id": "BODY-A",
                            "functional_role": "receiver",
                            "status": "INFERRED",
                            "appearance_identity_status": "PICTURE_OBSERVED_WITHIN_SHOT",
                            "appearance_track_id": None,
                            "source_refs": mixed_refs,
                        }
                    ]
                self.assertIn(expected, error_codes(evidence))

    def test_duplicate_text_anchor_id_fails(self) -> None:
        evidence = make_valid_evidence()
        evidence["text_anchor_status"] = "TEXT_ANCHOR_UNKNOWN"
        evidence["text_anchors"] = [
            {
                "anchor_id": "TEXT-ANCHOR-DUPLICATE",
                "status": "TEXT_ANCHOR_UNKNOWN",
                "source_type": "SCRIPT",
                "paraphrase": paraphrase,
                "speaker_status": "UNKNOWN",
                "start": time_point(0.0, 0),
                "end": time_point(1.0, 24),
            }
            for paraphrase in ("First synthetic anchor.", "Second synthetic anchor.")
        ]
        self.assertIn("TEXT-ANCHOR-ID-DUPLICATE", error_codes(evidence))

    def test_partial_text_status_requires_usable_anchor_and_review_method(self) -> None:
        evidence = make_valid_evidence()
        evidence["text_anchor_status"] = "TEXT_ANCHOR_PARTIAL"
        evidence["shots"][0]["text_anchor_status"] = "TEXT_ANCHOR_PARTIAL"
        evidence["text_anchors"] = [
            {
                "anchor_id": "TEXT-ANCHOR-UNKNOWN-ONLY",
                "status": "TEXT_ANCHOR_UNKNOWN",
                "source_type": "SCRIPT",
                "paraphrase": "Synthetic anchor remains unknown.",
                "speaker_status": "UNKNOWN",
                "start": time_point(0.0, 0),
                "end": time_point(1.0, 24),
            }
        ]
        codes = error_codes(evidence)
        self.assertIn("TEXT-STATUS-NO-USABLE-ANCHOR", codes)
        self.assertIn("TEXT-ANCHOR-NO-REVIEW-METHOD", codes)

    def test_every_unknown_array_rejects_hidden_fact_and_audio_directive(self) -> None:
        cases = (
            ("Vehicle remains unknown; the vehicle is red on screen.", "UNKNOWN-HIDES-AFFIRMATIVE-FACT"),
            ("Vehicle remains unknown while the vehicle is red on screen.", "UNKNOWN-HIDES-AFFIRMATIVE-FACT"),
            ("Vehicle remains unknown, the vehicle is red on screen.", "UNKNOWN-HIDES-AFFIRMATIVE-FACT"),
            ("Vehicle remains unknown and the vehicle is red on screen.", "UNKNOWN-HIDES-AFFIRMATIVE-FACT"),
            ("Vehicle remains unknown, red vehicle visible on screen.", "UNKNOWN-HIDES-AFFIRMATIVE-FACT"),
            ("Vehicle remains unknown and red vehicle visible on screen.", "UNKNOWN-HIDES-AFFIRMATIVE-FACT"),
            ("Audio remains unknown; bring in a score.", "UNKNOWN-HIDES-AUDIO-DIRECTIVE"),
            ("Audio remains unknown, so bring in a score.", "UNKNOWN-HIDES-AUDIO-DIRECTIVE"),
            (
                "Audio remains unknown; do not add a score and bring in music.",
                "UNKNOWN-HIDES-AUDIO-DIRECTIVE",
            ),
            (
                "Audio remains unknown; do not add a score, track the music.",
                "UNKNOWN-HIDES-AUDIO-DIRECTIVE",
            ),
        )
        for location in ("shot", "audio", "method", "auxiliary", "continuity"):
            for statement, expected in cases:
                with self.subTest(location=location, statement=statement):
                    evidence = make_valid_evidence()
                    set_unknown_array(evidence, location, statement)
                    self.assertIn(expected, error_codes(evidence))

    def test_unknown_array_rejects_cross_cut_identity_assertion(self) -> None:
        for location in ("shot", "audio", "method", "auxiliary", "continuity"):
            for statement in (
                "Identity remains unknown; the same person returns across the cut.",
                "Identity remains unknown while the same person returns across the cut.",
                "Identity remains unknown, the same person continues across the cut.",
                "Identity remains unknown and the same person continues across the cut.",
            ):
                with self.subTest(location=location, statement=statement):
                    evidence = make_valid_evidence()
                    set_unknown_array(evidence, location, statement)
                    self.assertIn("UNKNOWN-HIDES-CROSS-CUT-IDENTITY", error_codes(evidence))

    def test_every_unknown_array_rejects_fact_before_uncertainty(self) -> None:
        statements = (
            "The vehicle is red on screen, identity remains unknown.",
            "Red vehicle visible on screen and identity remains unknown.",
            "Red vehicle on screen, identity remains unknown.",
            "Red vehicle in frame and identity remains unknown.",
            "Red vehicle on screen: identity remains unknown.",
            "Red vehicle in-frame, identity remains unknown.",
            "The vehicle occupies frame left, identity remains unknown.",
            "Red vehicle on screen / identity remains unknown.",
            "Vehicle in-frame / identity remains unknown.",
            "The vehicle occupies frame left—identity remains unknown.",
            "The same person continues across the cut, identity remains unknown.",
        )
        for location in ("shot", "audio", "method", "auxiliary", "continuity"):
            for statement in statements:
                with self.subTest(location=location, statement=statement):
                    evidence = make_valid_evidence()
                    set_unknown_array(evidence, location, statement)
                    self.assertIn("UNKNOWN-HIDES-AFFIRMATIVE-FACT", error_codes(evidence))

    def test_safe_negative_audio_boundary_passes(self) -> None:
        evidence = make_valid_evidence()
        evidence["audio_audit"]["audio_unknowns"] = [
            "Audio remains unknown; do not add a score."
        ]
        evidence["candidate_rules"][0]["audio_logic"]["value"] = (
            "Audio remains unknown; do not add a score."
        )
        self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_audio_track_noun_is_not_a_directive(self) -> None:
        for location in ("shot", "audio", "method", "auxiliary", "continuity"):
            for statement in (
                "The audio track remains unknown.",
                "Whether a music track is present remains unknown.",
            ):
                with self.subTest(location=location, statement=statement):
                    evidence = make_valid_evidence()
                    set_unknown_array(evidence, location, statement)
                    self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["audio_logic"]["value"] = "The audio track remains unknown."
        self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_standalone_safe_negative_unknown_boundary_passes(self) -> None:
        for location in ("shot", "audio", "method", "auxiliary", "continuity"):
            with self.subTest(location=location):
                evidence = make_valid_evidence()
                set_unknown_array(evidence, location, "Do not add a score.")
                self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_explicit_unknown_limitations_pass_in_every_unknown_array(self) -> None:
        for location in ("shot", "audio", "method", "auxiliary", "continuity"):
            for statement in (
                "Identity remains unknown and cannot be confirmed from picture.",
                "Audio remains unknown and was not directly auditioned.",
            ):
                with self.subTest(location=location, statement=statement):
                    evidence = make_valid_evidence()
                    set_unknown_array(evidence, location, statement)
                    self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_track_audio_directive_fails_without_audition(self) -> None:
        evidence = make_valid_evidence()
        evidence["candidate_rules"][0]["director_decision"] = "Track the music under the image."
        self.assertIn("RULE-AUDIO-DIRECTIVE-WITHOUT-EVIDENCE", error_codes(evidence))

    def test_safe_audio_boundary_cannot_mask_later_directive(self) -> None:
        for statement in (
            "Audio remains unknown; do not add a score but bring in music.",
            "Audio remains unknown; do not add a score, then track the music.",
            "Audio remains unknown; do not add a score or bring in music.",
            "Audio remains unknown; do not add a score plus bring in music.",
            "Audio remains unknown; do not add a score before bringing in music.",
            "Audio remains unknown; do not add a score instead bring in music.",
            "Audio remains unknown; do not add a score—bring in music instead.",
            "Audio remains unknown; do not add a score: bring in music.",
            "Audio remains unknown; do not add a score / bring in music.",
            "Audio remains unknown; do not add a score rather than bring in music.",
        ):
            for location in ("shot", "audio", "method", "auxiliary", "continuity"):
                with self.subTest(statement=statement, location=location):
                    evidence = make_valid_evidence()
                    set_unknown_array(evidence, location, statement)
                    self.assertIn("UNKNOWN-HIDES-AUDIO-DIRECTIVE", error_codes(evidence))

    def test_safe_audio_boundary_cannot_mask_rule_directive(self) -> None:
        for statement in (
            "Do not add a score and bring in music.",
            "Do not add a score, track the music.",
            "Do not add a score instead bring in music.",
            "Do not add a score—bring in music instead.",
            "Do not add a score: bring in music.",
            "Do not add a score / bring in music.",
            "Do not add a score rather than bring in music.",
        ):
            for field in ("director_decision", "audio_logic"):
                with self.subTest(statement=statement, field=field):
                    evidence = make_valid_evidence()
                    if field == "audio_logic":
                        evidence["candidate_rules"][0][field]["value"] = statement
                    else:
                        evidence["candidate_rules"][0][field] = statement
                    self.assertIn("RULE-AUDIO-DIRECTIVE-WITHOUT-EVIDENCE", error_codes(evidence))

    def test_single_token_unknown_cannot_reappear_as_rule_fact(self) -> None:
        for rule_text in (
            "Use the vehicle on screen.",
            "Vehicle remains unknown, use the vehicle on screen.",
            "Vehicle remains unknown and use the vehicle on screen.",
        ):
            with self.subTest(rule_text=rule_text):
                evidence = make_valid_evidence()
                evidence["unknowns"][0].update(
                    statement="Vehicle remains unknown.",
                    scope="SCENE",
                    blocks_rule_ids=[],
                )
                evidence["candidate_rules"][0]["director_decision"] = rule_text
                self.assertIn("RULE-ASSERTS-UNKNOWN-FACT", error_codes(evidence))

    def test_single_token_unknown_cannot_be_hidden_after_rule_fact(self) -> None:
        for rule_text in (
            "Use the vehicle on screen, vehicle remains unknown.",
            "Use the vehicle on screen and vehicle remains unknown.",
        ):
            with self.subTest(rule_text=rule_text):
                evidence = make_valid_evidence()
                evidence["unknowns"][0].update(
                    statement="Vehicle remains unknown.",
                    scope="SCENE",
                    blocks_rule_ids=[],
                )
                evidence["candidate_rules"][0]["director_decision"] = rule_text
                self.assertIn("RULE-ASSERTS-UNKNOWN-FACT", error_codes(evidence))

    def test_public_boundary_scans_measurement_keys(self) -> None:
        for key, value, expected in (
            ("private-scene.mp4", 1, "PUBLIC-MEDIA-OR-SUBTITLE"),
            ("api_key=fixture-secret", 1, "PUBLIC-CREDENTIAL"),
            ("data:image/png;base64,AAAA", 1, "PUBLIC-DATA-URI"),
            ("api_key", "fixture-secret-12345", "PUBLIC-CREDENTIAL"),
            ("access_token", "fixture-token-12345", "PUBLIC-CREDENTIAL"),
            ("client_secret", "fixture-secret-12345", "PUBLIC-CREDENTIAL"),
            ("password", "fixture-password-12345", "PUBLIC-CREDENTIAL"),
            ("refresh_token", "fixture-token-12345", "PUBLIC-CREDENTIAL"),
            ("private_key", "fixture-key-12345", "PUBLIC-CREDENTIAL"),
            ("cookie", "fixture-cookie-12345", "PUBLIC-CREDENTIAL"),
            ("authorization", "Bearer fixture-token-12345", "PUBLIC-CREDENTIAL"),
            ("x-api-key", "fixture-secret-12345", "PUBLIC-CREDENTIAL"),
            ("production_api_key", "fixture-secret-12345", "PUBLIC-CREDENTIAL"),
            ("github_token", "fixture-token-12345", "PUBLIC-CREDENTIAL"),
            ("session_cookie", "fixture-cookie-12345", "PUBLIC-CREDENTIAL"),
            ("authorization_header", "Bearer fixture-token-12345", "PUBLIC-CREDENTIAL"),
            ("auth_token", "fixture-token-12345", "PUBLIC-CREDENTIAL"),
            ("sessionCookie", "fixture-cookie-12345", "PUBLIC-CREDENTIAL"),
            ("authorizationHeader", "Bearer fixture-token-12345", "PUBLIC-CREDENTIAL"),
            ("productionApiKey", "fixture-secret-12345", "PUBLIC-CREDENTIAL"),
        ):
            with self.subTest(key=key):
                evidence = make_valid_evidence()
                add_signal_auxiliary(evidence)
                evidence["candidate_rules"][0]["promotion_status"] = "BLOCKED_BY_UNKNOWN"
                evidence["auxiliary_evidence"][0]["measurements"] = {key: value}
                self.assertIn(expected, error_codes(evidence))

        evidence = make_valid_evidence()
        add_signal_auxiliary(evidence)
        evidence["candidate_rules"][0]["promotion_status"] = "BLOCKED_BY_UNKNOWN"
        evidence["auxiliary_evidence"][0]["measurements"] = {
            "synthetic_level": -12.0,
            "token_count": 42,
        }
        self.assertTrue(validate_evidence(evidence, SCHEMA)["passed"])

    def test_report_cannot_overwrite_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence_path = Path(directory) / "scene-evidence.json"
            original = json.dumps(make_valid_evidence(), ensure_ascii=False)
            evidence_path.write_text(original, encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = main([str(evidence_path), "--report", str(evidence_path)])
            self.assertEqual(result, 2)
            self.assertEqual(evidence_path.read_text(encoding="utf-8"), original)
            self.assertIn("must not overwrite", stderr.getvalue())

    def test_report_cannot_overwrite_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence_path = Path(directory) / "scene-evidence.json"
            evidence_path.write_text(json.dumps(make_valid_evidence()), encoding="utf-8")
            schema_path = SKILL_ROOT / "references" / "scene-evidence.schema.json"
            original = schema_path.read_text(encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = main([str(evidence_path), "--report", str(schema_path), "--quiet"])
            self.assertEqual(result, 2)
            self.assertEqual(schema_path.read_text(encoding="utf-8"), original)
            self.assertIn("must not overwrite", stderr.getvalue())

    def test_report_protects_canonical_schema_when_schema_copy_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_skill_root = root / "skill"
            scripts_dir = synthetic_skill_root / "scripts"
            references_dir = synthetic_skill_root / "references"
            scripts_dir.mkdir(parents=True)
            references_dir.mkdir()
            canonical_schema = references_dir / "scene-evidence.schema.json"
            canonical_text = json.dumps(SCHEMA, ensure_ascii=False)
            canonical_schema.write_text(canonical_text, encoding="utf-8")
            schema_copy = root / "schema-copy.json"
            schema_copy.write_text(canonical_text, encoding="utf-8")
            evidence_path = root / "scene-evidence.json"
            evidence_path.write_text(json.dumps(make_valid_evidence()), encoding="utf-8")
            original_module_file = validator_module.__file__
            try:
                validator_module.__file__ = str(scripts_dir / "validate_scene_evidence.py")
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    result = main(
                        [
                            str(evidence_path),
                            "--schema",
                            str(schema_copy),
                            "--report",
                            str(canonical_schema),
                            "--quiet",
                        ]
                    )
            finally:
                validator_module.__file__ = original_module_file
            self.assertEqual(result, 2)
            self.assertEqual(canonical_schema.read_text(encoding="utf-8"), canonical_text)
            self.assertIn("must not overwrite", stderr.getvalue())

    @unittest.skipUnless(sys.platform == "darwin", "case-alias collision is a macOS filesystem regression")
    def test_report_case_alias_cannot_overwrite_input_or_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "Input.scene-evidence.json"
            input_alias = root / "input.scene-evidence.json"
            original_input = json.dumps(make_valid_evidence(), ensure_ascii=False)
            input_path.write_text(original_input, encoding="utf-8")
            if not input_alias.exists() or not os.path.samefile(input_path, input_alias):
                self.skipTest("temporary filesystem is case-sensitive")
            with contextlib.redirect_stderr(io.StringIO()):
                input_result = main([str(input_path), "--report", str(input_alias), "--quiet"])
            self.assertEqual(input_result, 2)
            self.assertEqual(input_path.read_text(encoding="utf-8"), original_input)

            schema_path = root / "Schema.json"
            schema_alias = root / "schema.json"
            original_schema = (SKILL_ROOT / "references" / "scene-evidence.schema.json").read_text(encoding="utf-8")
            schema_path.write_text(original_schema, encoding="utf-8")
            self.assertTrue(os.path.samefile(schema_path, schema_alias))
            with contextlib.redirect_stderr(io.StringIO()):
                schema_result = main(
                    [str(input_path), "--schema", str(schema_path), "--report", str(schema_alias), "--quiet"]
                )
            self.assertEqual(schema_result, 2)
            self.assertEqual(schema_path.read_text(encoding="utf-8"), original_schema)

    def test_quiet_directory_discovery_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence_path = root / "nested" / "fixture.scene-evidence.json"
            evidence_path.parent.mkdir()
            evidence_path.write_text(json.dumps(make_valid_evidence()), encoding="utf-8")
            report_path = root / "validation-report.json"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = main([str(root), "--quiet", "--report", str(report_path)])
            self.assertEqual(result, 0)
            self.assertEqual(stdout.getvalue(), "")
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["total_scenes"], 1)

    def test_wrong_schema_returns_setup_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence_path = root / "scene-evidence.json"
            evidence_path.write_text(json.dumps(make_valid_evidence()), encoding="utf-8")
            weakened_schema = json.loads(json.dumps(SCHEMA))
            weakened_boolean = weakened_schema["$defs"]["rightsBoundary"]["properties"]["media_committed"]
            weakened_boolean.pop("type")
            weakened_boolean.pop("const")
            coerced_const_schema = json.loads(json.dumps(SCHEMA))
            coerced_const_schema["$defs"]["rightsBoundary"]["properties"]["media_committed"]["const"] = 0
            bad_schemas = (
                {"$id": "scene-evidence.schema.json"},
                weakened_schema,
                coerced_const_schema,
                {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "$id": "scene-evidence.schema.json",
                    "type": 123,
                    "additionalProperties": False,
                    "required": [],
                    "properties": {},
                    "$defs": {},
                },
                {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "$id": "scene-evidence.schema.json",
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "schema_version", "evidence_id", "scene_problem", "scene_unit_type",
                        "boundary_status", "boundary_evidence", "shots", "methods",
                        "auxiliary_evidence", "candidate_rules", "unknowns", "rights_boundary",
                    ],
                    "properties": {
                        "schema_version": {"const": "scene-evidence/0.1"},
                        "evidence_id": {"$ref": 123},
                        "scene_problem": {}, "scene_unit_type": {}, "boundary_status": {},
                        "boundary_evidence": {}, "shots": {}, "methods": {},
                        "auxiliary_evidence": {}, "candidate_rules": {}, "unknowns": {},
                        "rights_boundary": {},
                    },
                    "$defs": {},
                },
            )
            for index, bad_schema in enumerate(bad_schemas):
                with self.subTest(index=index):
                    schema_path = root / f"wrong-schema-{index}.json"
                    schema_path.write_text(json.dumps(bad_schema), encoding="utf-8")
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr):
                        result = main([str(evidence_path), "--schema", str(schema_path), "--quiet"])
                    self.assertEqual(result, 2)
                    self.assertIn("validator setup error", stderr.getvalue())

    def test_weakened_schema_cannot_accept_boolean_impersonator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = make_valid_evidence()
            evidence["rights_boundary"]["media_committed"] = 1
            evidence_path = root / "scene-evidence.json"
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            weakened_schema = json.loads(json.dumps(SCHEMA))
            weakened_boolean = weakened_schema["$defs"]["rightsBoundary"]["properties"]["media_committed"]
            weakened_boolean.pop("type")
            weakened_boolean.pop("const")
            schema_path = root / "weakened-schema.json"
            schema_path.write_text(json.dumps(weakened_schema), encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = main([str(evidence_path), "--schema", str(schema_path), "--quiet"])
            self.assertEqual(result, 2)
            self.assertIn("validator setup error", stderr.getvalue())

    def test_tampered_canonical_schema_fails_closed(self) -> None:
        for replacement in (None, 0):
            with self.subTest(replacement=replacement), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                synthetic_skill_root = root / "skill"
                scripts_dir = synthetic_skill_root / "scripts"
                references_dir = synthetic_skill_root / "references"
                scripts_dir.mkdir(parents=True)
                references_dir.mkdir()
                tampered_schema = json.loads(json.dumps(SCHEMA))
                boolean_node = tampered_schema["$defs"]["rightsBoundary"]["properties"]["media_committed"]
                if replacement is None:
                    boolean_node.pop("type")
                    boolean_node.pop("const")
                else:
                    boolean_node["const"] = replacement
                canonical_path = references_dir / "scene-evidence.schema.json"
                canonical_path.write_text(json.dumps(tampered_schema), encoding="utf-8")
                evidence = make_valid_evidence()
                evidence["rights_boundary"]["media_committed"] = 1
                evidence_path = root / "scene-evidence.json"
                evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
                original_module_file = validator_module.__file__
                try:
                    validator_module.__file__ = str(scripts_dir / "validate_scene_evidence.py")
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr):
                        result = main([str(evidence_path), "--schema", str(canonical_path), "--quiet"])
                finally:
                    validator_module.__file__ = original_module_file
                self.assertEqual(result, 2)
                self.assertIn("validator setup error", stderr.getvalue())

    def test_report_write_failure_returns_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence_path = root / "scene-evidence.json"
            report_directory = root / "report-target"
            evidence_path.write_text(json.dumps(make_valid_evidence()), encoding="utf-8")
            report_directory.mkdir()
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                result = main([str(evidence_path), "--report", str(report_directory), "--quiet"])
            self.assertEqual(result, 2)
            self.assertIn("validator report write error", stderr.getvalue())

    def test_repository_scene_evidence_fixture_passes_cli(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = main([str(REPOSITORY_FIXTURE)])
        self.assertEqual(result, 0)
        report = json.loads(stdout.getvalue())
        self.assertEqual(report["total_scenes"], 1)
        self.assertEqual(report["failed"], 0)


if __name__ == "__main__":
    unittest.main()
