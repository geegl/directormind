#!/usr/bin/env python3
"""Convert the closed canonical legacy Scene Evidence corpus to JSON.

The converter is intentionally conservative.  It treats the checked-in Markdown
tables as migration input, never as fresh observation: semantic audio remains
blocked, text anchors remain unused, cross-cut identity is not upgraded, and all
embedded transfer candidates remain blocked pending human review.

Generated files are written next to their source Markdown by default.  Use
``--output-root`` to mirror the ``research/evidence`` tree elsewhere (for tests
or review), and ``--check`` to compare existing JSON byte-for-byte with the
deterministic conversion result.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
EVIDENCE_ROOT = REPOSITORY_ROOT / "research" / "evidence"
SCHEMA_PATH = SKILL_ROOT / "references" / "scene-evidence.schema.json"

sys.path.insert(0, str(SCRIPT_DIR))
from validate_scene_evidence import load_json, validate_evidence  # noqa: E402


@dataclass(frozen=True)
class SceneMeta:
    evidence_id: str
    work_id: str
    scene_unit_type: str
    boundary_status: str
    primary_problem: str
    picture_status: str = "PICTURE_OBSERVED"
    shot_completeness: str = "COMPLETE_VISIBLE_SHOT"
    stats_unit: str = "VISIBLE_SHOT"


@dataclass(frozen=True)
class EndpointMeta:
    start_frame: int | None = None
    end_frame: int | None = None
    start_pts: int | None = None
    end_pts: int | None = None
    time_base: str | None = None


SCENE_META: dict[str, SceneMeta] = {
    "A_QUIET_PLACE_2018_PARALLEL_BODY_STATE_RADIAL_LIGHT_EVIDENCE_V0.1": SceneMeta(
        "A-QUIET-PLACE-2018-PARALLEL-BODY-STATE-RADIAL-LIGHT-001",
        "A-QUIET-PLACE-2018", "SELECTED_INTERNAL_ENVELOPE", "BOTH_INTERNAL_SELECTED",
        "ACTION_CAUSALITY",
    ),
    "ANDOR_S01E10_SELECTED_ENVELOPE_VISUAL_EVIDENCE_V0.1": SceneMeta(
        "DM-ANDOR-S01E10-SEL-001", "ANDOR-S01E10", "SELECTED_INTERNAL_ENVELOPE",
        "BOTH_INTERNAL_SELECTED", "GROUP_POWER_CHANGE",
    ),
    "APOLLO_13_CONSTRAINED_MATERIAL_HANDOFF_EVIDENCE_V0.1": SceneMeta(
        "APOLLO-13-1995-CONSTRAINED-MATERIAL-HANDOFF-001", "APOLLO-13-1995",
        "CONTIGUOUS_EDITORIAL_SEQUENCE", "BOTH_INTERNAL_SELECTED", "PROCEDURAL_COMPETENCE",
    ),
    "BETTER_CALL_SAUL_S03E05_PUBLIC_PROOF_EVIDENCE_V0.1": SceneMeta(
        "BETTER-CALL-SAUL-S03E05-PUBLIC-PROOF-001", "BETTER-CALL-SAUL-S03E05",
        "SELECTED_INTERNAL_ENVELOPE", "BOTH_INTERNAL_SELECTED", "PUBLIC_REVELATION",
    ),
    "BODYGUARD_S01E01_SELECTED_SEQUENCE_VISUAL_EVIDENCE_V0.1": SceneMeta(
        "DM-BODYGUARD-S01E01-SEL-001", "BODYGUARD-S01E01", "SELECTED_INTERNAL_ENVELOPE",
        "BOTH_INTERNAL_SELECTED", "SUSPENSE_INFORMATION_ASYMMETRY",
    ),
    "BRIDGERTON_S02E05_CONTAINED_PROXIMITY_EVIDENCE_V0.1": SceneMeta(
        "BRIDGERTON-S02E05-CONTAINED-PROXIMITY-001", "BRIDGERTON-S02E05",
        "NATURAL_CONTINUOUS_SCENE", "NATURAL_START_END_VERIFIED", "ROMANTIC_PROXIMITY",
    ),
    "BROOKLYN_NINE_NINE_S05E14_THE_BOX_VISUAL_EVIDENCE_V0.1": SceneMeta(
        "B99-S05E14-THE-BOX-PRIDE-BAIT-CONFESSION-001", "BROOKLYN-NINE-NINE-S05E14",
        "SELECTED_INTERNAL_ENVELOPE", "BOTH_INTERNAL_SELECTED", "INTERROGATION",
    ),
    "CHERNOBYL_S01E05_HEARING_RECONSTRUCTION_VISUAL_EVIDENCE_V0.1": SceneMeta(
        "CHERNOBYL-S01E05-HEARING-RECON-001", "CHERNOBYL-S01E05",
        "CONTIGUOUS_EDITORIAL_SEQUENCE", "BOTH_INTERNAL_SELECTED", "PROCEDURAL_COLLAPSE",
    ),
    "CHILDREN_OF_MEN_2006_MOVING_CAR_EXTERIOR_DISRUPTION_CONTINUITY_EVIDENCE_V0.1": SceneMeta(
        "CHILDREN-OF-MEN-2006-MOVING-CAR-EXTERIOR-DISRUPTION-001", "CHILDREN-OF-MEN-2006",
        "SINGLE_VISIBLE_TAKE", "BOTH_INTERNAL_SELECTED", "ACTION_CAUSALITY",
    ),
    "CITIZEN_KANE_BREAKFAST_MONTAGE_EVIDENCE_V0.1": SceneMeta(
        "CITIZEN-KANE-1941-BREAKFAST-MONTAGE-001", "CITIZEN-KANE-1941",
        "CONTIGUOUS_EDITORIAL_SEQUENCE", "BOUNDARY_UNKNOWN", "MONTAGE_TIME_COMPRESSION",
        shot_completeness="EDIT_UNIT_NOT_SHOT", stats_unit="EDIT_UNIT",
    ),
    "GET_OUT_2017_HYPNOSIS_SUBJECTIVE_SPACE_EVIDENCE_V0.1": SceneMeta(
        "GETOUT-2017-HYPNOSIS-SUBJECTIVE-SPACE-001", "GET-OUT-2017",
        "NATURAL_CONTINUOUS_SCENE", "NATURAL_START_END_VERIFIED", "SUBJECTIVE_COERCION",
    ),
    "HOUSE_OF_THE_DRAGON_S01E08_THRONE_ROOM_EVIDENCE_V0.1": SceneMeta(
        "HOUSE-OF-THE-DRAGON-S01E08-THRONE-ROOM-INGRESS-TO-SEATED-STATE-001",
        "HOUSE-OF-THE-DRAGON-S01E08", "SELECTED_INTERNAL_ENVELOPE",
        "BOTH_INTERNAL_SELECTED", "GROUP_POWER_CHANGE",
    ),
    "KNIVES_OUT_2019_WILL_READING_EVIDENCE_V0.1": SceneMeta(
        "KNIVES-OUT-2019-WILL-READING-001", "KNIVES-OUT-2019",
        "CONTIGUOUS_EDITORIAL_SEQUENCE", "BOTH_INTERNAL_SELECTED", "PUBLIC_REVELATION",
    ),
    "MARRIAGE_STORY_2019_APARTMENT_SEQUENCE_EVIDENCE_V0.1": SceneMeta(
        "MARRIAGE-STORY-2019-APARTMENT-SEQUENCE-001", "MARRIAGE-STORY-2019",
        "NATURAL_CONTINUOUS_SCENE", "NATURAL_START_END_VERIFIED", "RELATIONSHIP_FRACTURE",
    ),
    "MOONLIGHT_2016_TWO_APPEARANCE_MULTI_ZONE_DISTANCE_OBJECT_STATE_EDITORIAL_SEQUENCE_EVIDENCE_V0.1": SceneMeta(
        "MOONLIGHT-2016-TWO-APPEARANCE-MULTI-ZONE-EDITORIAL-001", "MOONLIGHT-2016",
        "CONTIGUOUS_EDITORIAL_SEQUENCE", "BOTH_INTERNAL_SELECTED", "RELATIONSHIP_FRACTURE",
    ),
    "MR_ROBOT_S04E07_ACT_FOUR_VISUAL_EVIDENCE_V0.1": SceneMeta(
        "MRR-S04E07-ACT-FOUR-VISUAL-001", "MR-ROBOT-S04E07", "NATURAL_CONTINUOUS_SCENE",
        "NATURAL_START_END_VERIFIED", "INTERROGATION",
    ),
    "NOBODY_2021_BUS_FIGHT_EVIDENCE_V0.1": SceneMeta(
        "NOBODY-2021-BUS-001", "NOBODY-2021", "NATURAL_CONTINUOUS_SCENE",
        "NATURAL_START_END_VERIFIED", "ACTION_CAUSALITY",
    ),
    "SICARIO_BORDER_CHECKPOINT_EVIDENCE_V0.1": SceneMeta(
        "SICARIO-2015-BORDER-CHECKPOINT-001", "SICARIO-2015",
        "CONTIGUOUS_EDITORIAL_SEQUENCE", "NATURAL_START_END_VERIFIED",
        "SUSPENSE_INFORMATION_ASYMMETRY",
    ),
    "SOUND_OF_METAL_SIGNAL_STATE_EDITORIAL_ENVELOPE_EVIDENCE_V0.1": SceneMeta(
        "SOUND-OF-METAL-SIGNAL-STATE-EE-V0.1", "SOUND-OF-METAL",
        "CONTIGUOUS_EDITORIAL_SEQUENCE", "BOTH_INTERNAL_SELECTED", "SOUND_LED_CAUSALITY",
    ),
    "SUCCESSION_S01E06_BOARD_VOTE_EVIDENCE_V0.1": SceneMeta(
        "SUCCESSION-S01E06-BOARD-VOTE-001", "SUCCESSION-S01E06",
        "PARALLEL_INTERCUT_SEQUENCE", "BOTH_INTERNAL_SELECTED", "GROUP_POWER_CHANGE",
    ),
    "TED_LASSO_S01E08_DARTS_REVERSAL_EVIDENCE_V0.1": SceneMeta(
        "TED-LASSO-S01E08-DARTS-REVERSAL-001", "TED-LASSO-S01E08",
        "PARALLEL_INTERCUT_SEQUENCE", "BOTH_INTERNAL_SELECTED", "DIALOGUE_POWER_TRANSFER",
    ),
    "THE_BEAR_S01E07_REVIEW_EVIDENCE_V0.1": SceneMeta(
        "BEAR-S01E07-REVIEW-001", "THE-BEAR-S01E07", "SINGLE_VISIBLE_TAKE",
        "NATURAL_START_END_VERIFIED", "PROCEDURAL_COLLAPSE",
    ),
    "THE_BEAR_S02E07_TASK_CLOSED_LOOP_EVIDENCE_V0.1": SceneMeta(
        "BEAR-S02E07-TASK-CLOSED-LOOP-001", "THE-BEAR-S02E07",
        "CONTIGUOUS_EDITORIAL_SEQUENCE", "BOTH_INTERNAL_SELECTED", "PROCEDURAL_COMPETENCE",
    ),
    "THE_DEVIL_WEARS_PRADA_2006_CERULEAN_CORRECTION_EVIDENCE_V0.1": SceneMeta(
        "THE-DEVIL-WEARS-PRADA-2006-CERULEAN-CORRECTION-001", "THE-DEVIL-WEARS-PRADA-2006",
        "SELECTED_INTERNAL_ENVELOPE", "BOTH_INTERNAL_SELECTED", "DIALOGUE_POWER_TRANSFER",
    ),
    "THE_HAUNTING_OF_HILL_HOUSE_S01E06_ENSEMBLE_CONTINUOUS_REFRAMING_VISUAL_EVIDENCE_V0.1": SceneMeta(
        "DM-EVID-HH-S01E06-ENSEMBLE-CONTINUOUS-REFRAMING-V0.1", "HILL-HOUSE-S01E06",
        "SELECTED_INTERNAL_ENVELOPE", "START_VERIFIED_END_INTERNAL", "ENSEMBLE_REACTION_CHAIN",
        picture_status="PICTURE_PARTIAL", shot_completeness="PARTIAL_AT_END",
    ),
    "THE_LAST_OF_US_S01E06_BEDROOM_VISUAL_EVIDENCE_V0.1": SceneMeta(
        "TLOU-BEDROOM-LOCAL-001", "THE-LAST-OF-US-S01E06", "NATURAL_CONTINUOUS_SCENE",
        "BOUNDARY_UNKNOWN", "RELATIONSHIP_FRACTURE",
    ),
    "THE_MARTIAN_2015_MULTI_SPACE_OBJECT_STATE_EDITORIAL_SEQUENCE_VISUAL_EVIDENCE_V0.1": SceneMeta(
        "MARTIAN-MULTI-SPACE-OBJECT-STATE-EDITORIAL-SEQUENCE-LOCAL-001", "THE-MARTIAN-2015",
        "CONTIGUOUS_EDITORIAL_SEQUENCE", "BOTH_INTERNAL_SELECTED", "PROCEDURAL_COLLAPSE",
    ),
    "THE_SOCIAL_NETWORK_2010_OPENING_EXCHANGE_EVIDENCE_V0.1": SceneMeta(
        "THE-SOCIAL-NETWORK-2010-OPENING-TWO-PERSON-EXCHANGE-001", "THE-SOCIAL-NETWORK-2010",
        "NATURAL_CONTINUOUS_SCENE", "BOUNDARY_UNKNOWN", "RELATIONSHIP_FRACTURE",
    ),
    "THE_WIRE_S01E04_OLD_CASES_EVIDENCE_V0.1": SceneMeta(
        "WIRE-S01E04-OLD-CASES-001", "THE-WIRE-S01E04", "NATURAL_CONTINUOUS_SCENE",
        "NATURAL_START_END_VERIFIED", "PROCEDURAL_COMPETENCE",
    ),
    "TRUE_DETECTIVE_S01E04_MULTI_ZONE_MOBILE_ROUTE_VISUAL_EVIDENCE_V0.1": SceneMeta(
        "TRUE-DETECTIVE-S01E04-MULTI-ZONE-MOBILE-ROUTE-001", "TRUE-DETECTIVE-S01E04",
        "SINGLE_VISIBLE_TAKE", "BOUNDARY_UNKNOWN", "ACTION_CAUSALITY",
    ),
    "UNBELIEVABLE_S01E02_CONTAINED_TWO_PERSON_SEQUENCE_EVIDENCE_V0.1": SceneMeta(
        "UNBELIEVABLE-S01E02-CONTAINED-TWO-PERSON-SEQUENCE-001", "UNBELIEVABLE-S01E02",
        "PARALLEL_INTERCUT_SEQUENCE", "BOUNDARY_UNKNOWN", "SUSPENSE_INFORMATION_ASYMMETRY",
    ),
}


SHOT_COLUMNS = (
    "shot_id", "start", "end", "duration", "shot_size", "camera_angle", "POV",
    "composition", "blocking", "action", "performance", "function_class", "camera_motion",
    "focus_depth", "light_color", "sound", "edit_in", "edit_out", "cut_motivation",
    "narrative_function", "continuity", "AI_complexity", "status", "evidence_timecode",
)
RULE_COLUMNS_16 = (
    "rule_id", "trigger", "decision", "coverage", "blocking", "pacing_edit", "sound",
    "applicability", "non_applicability", "failure_mode", "counterexample", "unknown",
    "AI_risk", "fallback", "evidence_shots", "confidence",
)
RULE_COLUMNS_15 = tuple(item for item in RULE_COLUMNS_16 if item != "non_applicability")

SEMANTIC_PICTURE_RE = re.compile(
    r"\b(?:authority|challenger|witness|investigator|suspect|threat|attacker|victim|reaction|"
    r"responds?|realizes?|decides?|commands?|coerces?|consents?|afraid|angry|sad|nervous|"
    r"tense|strained|success|failure|confrontation|withdrawal|aftermath|searches?|"
    r"investigates?|discovers?|corrects?)\b",
    re.IGNORECASE,
)

PENDING_OPERATIONAL_FIELDS = {
    "trigger": "PENDING_HUMAN_REVIEW: no operational trigger is authorized by this legacy migration.",
    "director_decision": "NOT_AUTHORIZED: no directing decision may be applied until a human reviews the legacy lineage against current evidence.",
    "coverage": "PENDING_HUMAN_REVIEW: no operational coverage plan is authorized.",
    "blocking": "PENDING_HUMAN_REVIEW: no operational blocking plan is authorized.",
    "POV_effect": "PENDING_HUMAN_REVIEW: no audience-access or point-of-view effect is authorized.",
    "edit_logic": "PENDING_HUMAN_REVIEW: no operational edit logic is authorized.",
    "pacing": "PENDING_HUMAN_REVIEW: no operational pacing instruction is authorized.",
    "continuity": "PENDING_HUMAN_REVIEW: no operational continuity instruction is authorized.",
}
# These ordinals are part of the canonical migration output. Keep the original
# 30 allocations frozen; later current-corpus migrations receive a new range so
# inserting a source cannot rewrite an existing Scene Evidence file.
SCENE_RULE_ORDINAL_START = {
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
    "SUCCESSION_S01E06_BOARD_VOTE_EVIDENCE_V0.1": 121,
}


def _clean_text(value: str) -> str:
    """Remove Markdown wrappers and repository-host details without inventing facts."""
    text = value.replace("<br>", "; ").replace("<br/>", "; ").replace("<br />", "; ")
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = text.replace("`", "").replace("**", "").replace("__", "")
    # Scrub only recognizable local-path forms. Ordinary filmmaking phrases such
    # as ``person/object``, ``lens/focus`` and ``F-1/F`` are not paths.
    text = re.sub(r"(?i)\bfile:/+[^\s'\"()]+", "[local path omitted]", text)
    text = re.sub(r"(?<!\w)~/[^\s'\"()]+", "[local path omitted]", text)
    text = re.sub(
        r"(?<!\w)/(?:Users|private|tmp|Volumes)(?:/[^\s'\"()]+)+",
        "[local path omitted]",
        text,
    )
    text = re.sub(r"\b(?:WEB[-_. ]?DL|WEBRip|BluRay|BDRip|REMUX|HDRip|DVDRip|x264|x265|HEVC)\b", "source", text, flags=re.I)
    text = re.sub(r"\s+", " ", text).strip(" |")
    return text


def _normalize_identifier(value: str, fallback: str) -> str:
    value = _clean_text(value).upper()
    value = re.sub(r"[^A-Z0-9._-]+", "-", value).strip("-._")
    return value or fallback


def _split_table_row(line: str) -> list[str]:
    # Preserve legacy cells verbatim (apart from table-delimiter whitespace) so
    # ``legacy_migration`` is a lineage copy rather than a semantic rewrite.
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator(line: str) -> bool:
    if not line.startswith("|"):
        return False
    cells = line.strip().strip("|").split("|")
    return bool(cells) and all(re.fullmatch(r"\s*:?-{3,}:?\s*", cell) for cell in cells)


def parse_tables(markdown: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Return the one 24-column Shot table and one 15/16-column rule table."""
    lines = markdown.splitlines()
    shot_rows: list[dict[str, str]] | None = None
    rule_rows: list[dict[str, str]] | None = None
    index = 0
    while index + 1 < len(lines):
        if not lines[index].startswith("|") or not _is_separator(lines[index + 1]):
            index += 1
            continue
        header = _split_table_row(lines[index])
        rows: list[list[str]] = []
        cursor = index + 2
        while cursor < len(lines) and lines[cursor].startswith("|"):
            row = _split_table_row(lines[cursor])
            if len(row) != len(header):
                raise ValueError(f"table row width {len(row)} does not match header width {len(header)}")
            rows.append(row)
            cursor += 1
        if len(header) == 24 and any(item.lower() in {"shot_id", "source_start"} for item in header[:2]):
            if shot_rows is not None:
                raise ValueError("multiple 24-column Shot tables found")
            shot_rows = [dict(zip(SHOT_COLUMNS, row)) for row in rows]
        elif len(header) in {15, 16} and header[0].lower() == "rule_id":
            if rule_rows is not None:
                raise ValueError("multiple Candidate Rule tables found")
            columns = RULE_COLUMNS_16 if len(header) == 16 else RULE_COLUMNS_15
            rule_rows = [dict(zip(columns, row)) for row in rows]
        index = cursor
    if shot_rows is None or rule_rows is None:
        raise ValueError("required Shot or Candidate Rule table was not found")
    return shot_rows, rule_rows


def parse_timecode(value: str) -> tuple[str, Decimal]:
    match = re.search(r"([0-9]{2,}):([0-5][0-9]):([0-5][0-9](?:\.[0-9]{1,9})?)", value)
    if match is None:
        raise ValueError(f"timecode not found: {value!r}")
    canonical = match.group(0)
    try:
        seconds = Decimal(match.group(1)) * 3600 + Decimal(match.group(2)) * 60 + Decimal(match.group(3))
    except InvalidOperation as exc:
        raise ValueError(f"invalid timecode: {value!r}") from exc
    return canonical, seconds


def _raw_frame_range(value: str) -> tuple[str, int, int] | None:
    half_open = re.search(r"\[\s*F(\d+)\s*,\s*F(\d+)\s*\)", value, re.I)
    if half_open:
        return "half_open", int(half_open.group(1)), int(half_open.group(2))
    bare = re.search(r"\bF(\d+)\s*(?:–|—|-|\.\.)\s*F(\d+)\b", value, re.I)
    if bare:
        return "bare", int(bare.group(1)), int(bare.group(2))
    return None


def extract_endpoint_metadata(rows: Sequence[dict[str, str]]) -> list[EndpointMeta]:
    """Extract only endpoint numbers explicitly present in legacy timecode cells.

    Bracketed ranges are already half-open. For a bare ``Fstart–Fend`` range,
    the adjacent row's explicit start determines whether the legacy end is a
    boundary (next start equals end) or an inclusive visible-frame number (next
    start equals end + 1). The final row follows the same explicit convention
    established by earlier rows. A one-row ledger may explicitly state an
    adjacent-transition count, which also resolves the end boundary.
    """
    raw_frames = [_raw_frame_range(row["evidence_timecode"]) for row in rows]
    bare_adjustments: list[int] = []
    for current, following in zip(raw_frames, raw_frames[1:]):
        if current is None or current[0] != "bare" or following is None:
            continue
        difference = following[1] - current[2]
        if difference in {0, 1}:
            bare_adjustments.append(difference)

    established_adjustment: int | None = None
    if bare_adjustments and len(set(bare_adjustments)) == 1:
        established_adjustment = bare_adjustments[0]

    result: list[EndpointMeta] = []
    for index, row in enumerate(rows):
        evidence_timecode = row["evidence_timecode"]
        frame_range = raw_frames[index]
        start_frame: int | None = None
        end_frame: int | None = None
        if frame_range is not None:
            kind, raw_start, raw_end = frame_range
            start_frame = raw_start
            if kind == "half_open":
                end_frame = raw_end
            elif index + 1 < len(raw_frames) and raw_frames[index + 1] is not None:
                next_start = raw_frames[index + 1][1]
                if next_start in {raw_end, raw_end + 1}:
                    end_frame = next_start
            elif established_adjustment is not None:
                end_frame = raw_end + established_adjustment
            else:
                transition_match = re.search(r"([\d,]+)\s+adjacent transitions", evidence_timecode, re.I)
                if transition_match and int(transition_match.group(1).replace(",", "")) == raw_end - raw_start:
                    end_frame = raw_end

        pts_match = re.search(
            r"(?:frame\s+)?PTS\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\)",
            evidence_timecode,
            re.I,
        )
        time_base_match = re.search(r"\btime_base\s+([1-9]\d*/[1-9]\d*)", evidence_timecode, re.I)
        start_pts = int(pts_match.group(1)) if pts_match else None
        end_pts = int(pts_match.group(2)) if pts_match else None
        time_base = time_base_match.group(1) if pts_match and time_base_match else None
        result.append(EndpointMeta(start_frame, end_frame, start_pts, end_pts, time_base))
    return result


def time_point(
    value: str,
    *,
    frame: int | None = None,
    pts: int | None = None,
    time_base: str | None = None,
) -> tuple[dict[str, Any], Decimal]:
    timecode, seconds = parse_timecode(value)
    return {
        "timecode": timecode,
        "seconds": float(seconds),
        "frame": frame,
        "pts": pts,
        "time_base": time_base,
    }, seconds


def claim(
    claim_id: str,
    value: str,
    source_refs: Sequence[str],
    status: str,
    notes: str = "Migrated conservatively from the checked-in legacy evidence ledger.",
) -> dict[str, Any]:
    clean = _clean_text(value)
    refs = list(dict.fromkeys(source_refs))
    if status == "UNKNOWN":
        refs = []
        if not re.search(r"\b(?:unknown|unverified|not (?:directly )?(?:observed|auditioned|verified)|blocked)\b", clean, re.I):
            clean = f"The exact value remains unknown; the legacy note was not promoted: {clean}"
    elif not refs:
        raise ValueError(f"supported claim {claim_id} has no source reference")
    return {
        "claim_id": _normalize_identifier(claim_id, "CLAIM-UNKNOWN"),
        "status": status,
        "value": clean or "The exact value remains unknown.",
        "source_refs": refs,
        "notes": notes,
    }


def _legacy_status(value: str, default: str = "INFERRED") -> str:
    upper = value.upper()
    starts_unknown = bool(re.match(r"^(?:UNKNOWN|SND[-_ ]?UNK|UNVERIFIED)\b", upper))
    if starts_unknown or ("UNKNOWN" in upper and not re.search(r"(?:VIS[-_ ]?OBS|OBSERVED|INFERRED)", upper)):
        return "UNKNOWN"
    if re.search(r"^(?:VIS[-_ ]?OBS|OBSERVED(?:_VISUAL)?|PICTURE_OBSERVED)\b", upper):
        return "PICTURE_OBSERVED"
    if "INFERRED" in upper:
        return "INFERRED"
    return default


def legacy_claim(
    claim_id: str,
    value: str,
    shot_id: str,
    *,
    default: str = "INFERRED",
    force_inference: bool = False,
) -> dict[str, Any]:
    status = _legacy_status(value, default)
    clean = re.sub(
        r"^(?:VIS[-_ ]?OBS|OBSERVED(?:_VISUAL)?|PICTURE_OBSERVED|INFERRED|UNKNOWN|SND[-_ ]?UNK)\s*[:;/-]*\s*",
        "",
        _clean_text(value),
        flags=re.I,
    )
    if status == "PICTURE_OBSERVED" and (force_inference or SEMANTIC_PICTURE_RE.search(clean)):
        status = "INFERRED"
    if status == "UNKNOWN":
        clean = "The legacy field was not verified; its exact value remains unknown."
    return claim(claim_id, clean, [shot_id], status)


def _risk_level(value: str) -> str:
    upper = value.upper().replace("_", " ")
    if re.search(r"\b(?:CRITICAL|VERY HIGH|VH)\b", upper):
        return "CRITICAL"
    if re.search(r"\b(?:HIGH|H)\b", upper) or "MEDIUM-HIGH" in upper or "MEDIUM HIGH" in upper:
        return "HIGH"
    if re.search(r"\b(?:MEDIUM|M)\b", upper) or "LOW-MEDIUM" in upper or "LOW MEDIUM" in upper:
        return "MEDIUM"
    if re.search(r"\b(?:LOW|L)\b", upper):
        return "LOW"
    return "UNKNOWN"


def split_risk(value: str) -> dict[str, Any]:
    raw = _clean_text(value)
    axes: dict[str, str] = {}
    for axis in ("camera", "performance", "continuity"):
        match = re.search(
            rf"\b{axis}\s*(?:=|:)\s*([^;]+)", raw, re.I
        )
        if match:
            axes[axis] = _risk_level(match.group(1))
    combined = _risk_level(raw)
    result: dict[str, Any] = {}
    for axis in ("camera", "performance", "continuity"):
        level = axes.get(axis, combined)
        result[axis] = {
            "level": level,
            "reasons": [f"Legacy risk was conservatively mapped to {axis}={level}; execution remains unverified."],
        }
    return result


def extract_legacy_fallback(value: str) -> str | None:
    match = re.search(r"\bFALLBACK\s*:\s*(.+)$", value, re.I)
    if not match:
        return None
    fallback = _clean_text(match.group(1))
    return fallback or None


def project_original_fallback(
    risk: dict[str, Any],
    shot_id: str,
    legacy_fallback: str | None = None,
) -> dict[str, Any]:
    actions = {
        "camera": f"Preserve {shot_id}'s cited visible state-in, state-out, and edit endpoints with a project-original locked-off camera; split the beat if that exact state transition cannot be held.",
        "performance": f"Preserve {shot_id}'s cited visible action and performance-beat claims; limit the project-original shot to that one verified state change.",
        "continuity": f"Preserve {shot_id}'s cited zone, axis, state-in, and state-out claims in project-original coverage; split the beat instead of inventing an unverified cross-shot state.",
    }
    return {
        axis: (
            legacy_fallback or actions[axis]
            if risk[axis]["level"] in {"HIGH", "CRITICAL"}
            else None
        )
        for axis in ("camera", "performance", "continuity")
    } | {"project_original_only": True}


def pending_rule_risk() -> dict[str, Any]:
    return {
        axis: {
            "level": "UNKNOWN",
            "reasons": ["Pending human review; the legacy risk field is lineage only and was not operationally promoted."],
        }
        for axis in ("camera", "performance", "continuity")
    }


def pending_rule_fallback() -> dict[str, Any]:
    return {
        "camera": None,
        "performance": None,
        "continuity": None,
        "project_original_only": True,
    }


def _audio_status(meta: SceneMeta) -> str:
    if meta.evidence_id == "SOUND-OF-METAL-SIGNAL-STATE-EE-V0.1":
        return "SIGNAL_MEASURED_NOT_AUDITIONED"
    return "BLOCKED_DIRECT_AUDITION"


def convert_shots(meta: SceneMeta, rows: Sequence[dict[str, str]]) -> list[dict[str, Any]]:
    shots: list[dict[str, Any]] = []
    audio_status = _audio_status(meta)
    endpoint_metadata = extract_endpoint_metadata(rows)
    for order, (row, endpoints) in enumerate(zip(rows, endpoint_metadata), start=1):
        shot_id = f"{meta.evidence_id}-S{order:03d}"
        start, start_seconds = time_point(
            row["start"],
            frame=endpoints.start_frame,
            pts=endpoints.start_pts,
            time_base=endpoints.time_base,
        )
        end, end_seconds = time_point(
            row["end"],
            frame=endpoints.end_frame,
            pts=endpoints.end_pts,
            time_base=endpoints.time_base,
        )
        duration = end_seconds - start_seconds
        if duration <= 0:
            raise ValueError(f"non-positive Shot span in {row['shot_id']}")
        risk = split_risk(row["AI_complexity"])
        legacy_fallback = extract_legacy_fallback(row["AI_complexity"])
        high_risk_without_legacy_fallback = (
            any(risk[axis]["level"] in {"HIGH", "CRITICAL"} for axis in ("camera", "performance", "continuity"))
            and legacy_fallback is None
        )
        prefix = f"S{order:03d}"
        completeness = meta.shot_completeness
        picture_status = meta.picture_status
        shots.append(
            {
                "shot_id": shot_id,
                "order": order,
                "completeness": completeness,
                "start": start,
                "end": end,
                "duration": float(duration),
                "shot_size": legacy_claim(f"{prefix}-SIZE", row["shot_size"], shot_id, default="PICTURE_OBSERVED"),
                "camera_height": legacy_claim(f"{prefix}-HEIGHT", row["camera_angle"], shot_id, default="INFERRED"),
                "camera_angle": legacy_claim(f"{prefix}-ANGLE", row["camera_angle"], shot_id, default="PICTURE_OBSERVED"),
                "camera_motion": legacy_claim(f"{prefix}-MOTION", row["camera_motion"], shot_id, default="PICTURE_OBSERVED"),
                "camera_start": legacy_claim(f"{prefix}-CAM-START", row["composition"], shot_id, default="INFERRED", force_inference=True),
                "camera_path": legacy_claim(f"{prefix}-CAM-PATH", row["camera_motion"], shot_id, default="PICTURE_OBSERVED"),
                "camera_end": legacy_claim(f"{prefix}-CAM-END", row["composition"], shot_id, default="INFERRED", force_inference=True),
                "focus_strategy": legacy_claim(f"{prefix}-FOCUS", row["focus_depth"], shot_id, default="INFERRED"),
                "spatial_zone": [legacy_claim(f"{prefix}-ZONE", row["composition"], shot_id, default="INFERRED", force_inference=True)],
                "axis_and_screen_direction": legacy_claim(f"{prefix}-AXIS", row["continuity"], shot_id, default="INFERRED", force_inference=True),
                "abstract_role_labels": [],
                "blocking": legacy_claim(f"{prefix}-BLOCK", row["blocking"], shot_id, default="INFERRED", force_inference=True),
                "visible_action": legacy_claim(f"{prefix}-ACTION", row["action"], shot_id, default="INFERRED", force_inference=True),
                "visible_state_in": legacy_claim(f"{prefix}-STATE-IN", row["composition"], shot_id, default="INFERRED", force_inference=True),
                "visible_state_out": legacy_claim(f"{prefix}-STATE-OUT", row["action"], shot_id, default="INFERRED", force_inference=True),
                "event_or_reaction": legacy_claim(f"{prefix}-EVENT", row["function_class"], shot_id, default="INFERRED", force_inference=True),
                "performance_beat": legacy_claim(f"{prefix}-PERF", row["performance"], shot_id, default="INFERRED", force_inference=True),
                "edit_in": legacy_claim(f"{prefix}-EDIT-IN", row["edit_in"], shot_id, default="PICTURE_OBSERVED"),
                "edit_out": legacy_claim(f"{prefix}-EDIT-OUT", row["edit_out"], shot_id, default="PICTURE_OBSERVED"),
                "cut_motivation": legacy_claim(f"{prefix}-CUT-MOTIVE", row["cut_motivation"], shot_id, default="INFERRED", force_inference=True),
                "narrative_function": legacy_claim(f"{prefix}-FUNCTION", row["narrative_function"], shot_id, default="INFERRED", force_inference=True),
                "picture_status": picture_status,
                "audio_status": audio_status,
                "text_anchor_status": "TEXT_ANCHOR_NOT_USED",
                "AI_complexity": risk,
                "fallback": project_original_fallback(risk, shot_id, legacy_fallback),
                "unknowns": [
                    "Direct soundtrack audition was not completed, so dialogue, source, timing, and causal sound meaning remain unknown.",
                    f"Legacy light/color ledger retained for human review only: {_clean_text(row['light_color'])}",
                    "Cross-cut person, object, and location identity remain inferred or unknown unless separately tracked.",
                ] + (
                    ["The legacy Shot row has no explicit FALLBACK; its generic project-original fallback remains provisional pending human review."]
                    if high_risk_without_legacy_fallback else []
                ),
            }
        )
    return shots


def expand_shot_refs(value: str, shot_ids: Sequence[str]) -> list[str]:
    """Expand legacy ``S001-S004``/``S001..S004``/individual references."""
    by_number = {index: shot_id for index, shot_id in enumerate(shot_ids, start=1)}
    normalized = _clean_text(value).replace("..", "–").replace("→", "–")
    numbers: list[int] = []
    range_re = re.compile(r"S(\d{3,4})\s*(?:–|—|-|\bto\b)\s*(?:[A-Z0-9._-]+-)?S(\d{3,4})", re.I)
    occupied: list[tuple[int, int]] = []
    for match in range_re.finditer(normalized):
        start = int(match.group(1))
        end = int(match.group(2))
        if start <= end:
            numbers.extend(range(start, end + 1))
        occupied.append(match.span())
    for match in re.finditer(r"S(\d{3,4})", normalized, re.I):
        if any(start <= match.start() < end for start, end in occupied):
            continue
        numbers.append(int(match.group(1)))
    result = [by_number[number] for number in numbers if number in by_number]
    return list(dict.fromkeys(result))


def convert_rules(
    source_stem: str,
    meta: SceneMeta,
    rows: Sequence[dict[str, str]],
    shots: Sequence[dict[str, Any]],
    picture_method_id: str,
    conversion_method_id: str,
    signal_auxiliary_id: str | None,
) -> list[dict[str, Any]]:
    shot_ids = [shot["shot_id"] for shot in shots]
    rules: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        legacy_rule_id = _normalize_identifier(row["rule_id"], f"C{index:02d}")
        rule_id = f"{meta.evidence_id}-{legacy_rule_id}"
        cited_shots = expand_shot_refs(row["evidence_shots"], shot_ids)
        if not cited_shots:
            cited_shots = [shot_ids[0], shot_ids[-1]] if len(shot_ids) > 1 else [shot_ids[0]]
        auxiliary_ids = [signal_auxiliary_id] if signal_auxiliary_id and re.search(r"\bAUD[-_]", row["evidence_shots"], re.I) else []
        global_ordinal = SCENE_RULE_ORDINAL_START[source_stem] + index - 1
        rules.append(
            {
                "candidate_rule_id": rule_id,
                "canonical_rule_family": f"UNCLUSTERED-CANDIDATE-{global_ordinal:03d}",
                "legacy_migration": {
                    "trigger": row["trigger"],
                    "directing_decision": row["decision"],
                    "coverage": row["coverage"],
                    "blocking": row["blocking"],
                    "pacing_edit": row["pacing_edit"],
                    "sound": row["sound"],
                    "applicability": row["applicability"],
                    "non_applicability": row.get("non_applicability"),
                    "failure_mode": row["failure_mode"],
                    "counterexample": row["counterexample"],
                    "unknown": row["unknown"],
                    "ai_risk": row["AI_risk"],
                    "fallback": row["fallback"],
                    "evidence_shots": row["evidence_shots"],
                    "confidence": row["confidence"],
                },
                "scene_problem": "LEGACY_SCENE_PROBLEM",
                "trigger": PENDING_OPERATIONAL_FIELDS["trigger"],
                "required_story_facts": [],
                "director_decision": PENDING_OPERATIONAL_FIELDS["director_decision"],
                "coverage": PENDING_OPERATIONAL_FIELDS["coverage"],
                "blocking": PENDING_OPERATIONAL_FIELDS["blocking"],
                "POV_effect": PENDING_OPERATIONAL_FIELDS["POV_effect"],
                "edit_logic": PENDING_OPERATIONAL_FIELDS["edit_logic"],
                "pacing": PENDING_OPERATIONAL_FIELDS["pacing"],
                "audio_logic": claim(
                    f"{rule_id}-AUDIO",
                    "Pending human review; audio remains unknown and no audio instruction is authorized.",
                    [],
                    "UNKNOWN",
                ),
                "continuity": PENDING_OPERATIONAL_FIELDS["continuity"],
                "AI_risk": pending_rule_risk(),
                "fallback": pending_rule_fallback(),
                "applicable_when": ["No applicability condition is authorized before human review."],
                "not_applicable_when": ["No non-applicability boundary is authorized before human review."],
                "failure_modes": ["Applying this migrated lineage row as an operational rule before human review."],
                "counterexample_status": "UNKNOWN",
                "counterexample_ids": [],
                "source_method_ids": [picture_method_id, conversion_method_id],
                "evidence_scene_ids": [meta.evidence_id],
                "evidence_shot_ids": cited_shots,
                "evidence_auxiliary_ids": auxiliary_ids,
                "within_source_confidence": "UNKNOWN",
                "transfer_confidence": "UNKNOWN",
                "execution_confidence": "UNKNOWN",
                "promotion_status": "BLOCKED_BY_UNKNOWN",
                "evidence_status": "HYPOTHESIS",
            }
        )
    return rules


def _duration_bins(durations: Iterable[float]) -> dict[str, int]:
    bins = {"lt_1": 0, "1_to_lt_2": 0, "2_to_lt_5": 0, "5_to_lt_10": 0, "gte_10": 0}
    for value in durations:
        if value < 1:
            bins["lt_1"] += 1
        elif value < 2:
            bins["1_to_lt_2"] += 1
        elif value < 5:
            bins["2_to_lt_5"] += 1
        elif value < 10:
            bins["5_to_lt_10"] += 1
        else:
            bins["gte_10"] += 1
    return bins


def _audio_audit() -> dict[str, Any]:
    keys = (
        "dialogue_overlap", "silence_intervals", "ambience", "score_entry", "score_exit",
        "sound_before_image", "offscreen_sound", "sound_bridge", "subjective_sound",
        "object_sound", "audio_information_change",
    )
    result = {
        key: claim(
            f"AUDIO-{index:02d}",
            "Direct audition was not completed; this audio fact remains unknown.",
            [], "UNKNOWN",
        )
        for index, key in enumerate(keys, start=1)
    }
    result["audio_unknowns"] = [
        "Dialogue, ambience, score, silence, source, timing, and causal sound meaning remain unknown."
    ]
    return result


def build_evidence(source: Path) -> dict[str, Any]:
    meta = SCENE_META.get(source.stem)
    if meta is None:
        raise ValueError(f"source is not in the canonical migration register: {source.name}")
    markdown = source.read_text(encoding="utf-8")
    shot_rows, rule_rows = parse_tables(markdown)
    missing_high_risk_fallbacks = sum(
        1
        for row in shot_rows
        if extract_legacy_fallback(row["AI_complexity"]) is None
        and any(
            split_risk(row["AI_complexity"])[axis]["level"] in {"HIGH", "CRITICAL"}
            for axis in ("camera", "performance", "continuity")
        )
    )
    shots = convert_shots(meta, shot_rows)
    first_id = shots[0]["shot_id"]
    last_id = shots[-1]["shot_id"]
    scene_refs = [first_id] if first_id == last_id else [first_id, last_id]
    picture_method_id = f"{meta.evidence_id}-METHOD-LEGACY-PICTURE-REVIEW"
    conversion_method_id = f"{meta.evidence_id}-METHOD-STRUCTURAL-CONVERSION"
    audio_method_id = f"{meta.evidence_id}-METHOD-DIRECT-AUDIO"
    methods: list[dict[str, Any]] = [
        {
            "method_id": picture_method_id,
            "method_type": "PICTURE_FRAME_REVIEW",
            "status": "MANUAL_REVIEW_RECORDED",
            "description": "The legacy Markdown records a completed manual picture and edit-boundary review.",
            "repository_command": None,
            "tool_version_status": "VERSION_UNKNOWN",
            "source_refs": scene_refs,
            "unknowns": ["The conversion does not replay source media or re-prove the legacy observation."],
        },
        {
            "method_id": conversion_method_id,
            "method_type": "STRUCTURAL_CONVERSION",
            "status": "REPOSITORY_REPRODUCIBLE",
            "description": "Deterministically convert the checked-in legacy tables to Scene Evidence JSON.",
            "repository_command": "python3 skills/drama-director-compiler/scripts/convert_legacy_scene_evidence.py --check",
            "tool_version_status": "VERSION_RECORDED",
            "source_refs": scene_refs,
            "unknowns": ["Structural conversion is not creative approval or renewed media observation."],
        },
        {
            "method_id": audio_method_id,
            "method_type": "AUDIO_DIRECT_AUDITION",
            "status": "BLOCKED",
            "description": "Direct soundtrack audition was not completed for this conversion.",
            "repository_command": None,
            "tool_version_status": "NOT_APPLICABLE",
            "source_refs": [],
            "unknowns": ["All semantic audio facts remain unknown."],
        },
    ]
    auxiliary: list[dict[str, Any]] = []
    signal_auxiliary_id: str | None = None
    if _audio_status(meta) == "SIGNAL_MEASURED_NOT_AUDITIONED":
        signal_method_id = f"{meta.evidence_id}-METHOD-DECODED-SIGNAL"
        signal_auxiliary_id = f"{meta.evidence_id}-AUX-SIGNAL-SUMMARY"
        methods.append(
            {
                "method_id": signal_method_id,
                "method_type": "DECODED_SIGNAL_MEASUREMENT",
                "status": "MANUAL_REVIEW_RECORDED",
                "description": "The legacy ledger records decoded-signal measurements separately from semantic audition.",
                "repository_command": None,
                "tool_version_status": "VERSION_RECORDED",
                "source_refs": scene_refs,
                "unknowns": ["Signal measurements do not establish source, meaning, perception, or causal edit logic."],
            }
        )
        auxiliary.append(
            {
                "auxiliary_id": signal_auxiliary_id,
                "kind": "OTHER",
                "status": "SIGNAL_MEASURED_NOT_AUDITIONED",
                "start": shots[0]["start"],
                "end": shots[-1]["end"],
                "method_id": signal_method_id,
                "measurements": {"legacy_signal_ledger_present": True, "direct_audition_completed": False},
                "source_refs": scene_refs,
                "unknowns": ["Signal-event semantics and exact perceptual interpretation remain unknown."],
            }
        )

    rules = convert_rules(
        source.stem,
        meta,
        rule_rows,
        shots,
        picture_method_id,
        conversion_method_id,
        signal_auxiliary_id,
    )
    durations = [float(shot["duration"]) for shot in shots]
    boundary_claim = (
        claim(
            "SCENE-BOUNDARY",
            "The complete natural-scene boundary remains unknown.",
            [], "UNKNOWN",
        )
        if meta.boundary_status == "BOUNDARY_UNKNOWN"
        else claim(
            "SCENE-BOUNDARY",
            "Visible endpoints delimit the selected analytical interval; this does not verify production-take status.",
            scene_refs, "PICTURE_OBSERVED",
        )
    )
    production_status = (
        "VISIBLE_CONTINUITY_ONLY" if meta.scene_unit_type == "SINGLE_VISIBLE_TAKE"
        else "PRODUCTION_METHOD_UNKNOWN"
    )
    evidence: dict[str, Any] = {
        "schema_version": "scene-evidence/0.1",
        "evidence_id": meta.evidence_id,
        "work_id": meta.work_id,
        "scene_problem": {
            "primary": "LEGACY_SCENE_PROBLEM",
            "secondary": [],
            "status": "UNKNOWN",
            "source_refs": [],
            "notes": (
                f"The legacy primary label {meta.primary_problem} is retained only as non-operational "
                "lineage and was not proved by structural conversion."
            ),
        },
        "scene_unit_type": meta.scene_unit_type,
        "boundary_status": meta.boundary_status,
        "boundary_evidence": boundary_claim,
        "production_take_status": production_status,
        "source_identity_status": "SOURCE_OR_FILENAME_SUPPLIED",
        "source_start": shots[0]["start"],
        "source_end": shots[-1]["end"],
        "duration": float(Decimal(str(shots[-1]["end"]["seconds"])) - Decimal(str(shots[0]["start"]["seconds"]))),
        "time_tolerance_seconds": 0.001,
        "picture_evidence_status": meta.picture_status,
        "audio_evidence_status": _audio_status(meta),
        "text_anchor_status": "TEXT_ANCHOR_NOT_USED",
        "scene_dramatic_structure": {
            "start_state": claim("DS-START", "The first converted visible unit establishes an initial picture state.", [first_id], "PICTURE_OBSERVED"),
            "objectives": [claim("DS-OBJECTIVE", "Character objectives remain unknown without a verified text anchor or direct soundtrack audition.", [], "UNKNOWN")],
            "obstacle": claim("DS-OBSTACLE", "The dramatic obstacle remains unknown without a verified text anchor or direct soundtrack audition.", [], "UNKNOWN"),
            "event_point": claim("DS-EVENT", "The converted picture ledger contains visible state changes; their story cause remains unknown.", scene_refs, "INFERRED"),
            "reaction_point": claim("DS-REACTION", "Any reaction cause or emotional meaning remains unknown.", [], "UNKNOWN"),
            "turn": claim("DS-TURN", "The ordered visible state changes may form a dramatic turn, but the meaning remains inferred.", scene_refs, "INFERRED"),
            "end_state": claim("DS-END", "The final converted visible unit records the terminal picture state of the selected interval.", [last_id], "PICTURE_OBSERVED"),
        },
        "spatial_geometry": claim("SCENE-GEOMETRY", "The cited units support an inferred project-neutral spatial ledger; exact source identity across cuts is not asserted.", scene_refs, "INFERRED"),
        "axis": claim("SCENE-AXIS", "Screen direction and axis continuity remain an inference from the cited picture units.", scene_refs, "INFERRED"),
        "POV": claim("SCENE-POV", "POV function remains inferred from the cited visual coverage and is not treated as optical-POV proof.", scene_refs, "INFERRED"),
        "audience_information": claim("SCENE-AUDIENCE", "The cited picture units expose an ordered set of visible state changes; dramatic meaning remains inferred or unknown.", scene_refs, "INFERRED"),
        "shots": shots,
        "stats": {
            "unit": meta.stats_unit,
            "shot_count": len(shots),
            "total_duration": sum(durations),
            "mean_duration": statistics.mean(durations),
            "median_duration": statistics.median(durations),
            "duration_bins": _duration_bins(durations),
        },
        "audio_audit": _audio_audit(),
        "text_anchors": [],
        "methods": methods,
        "auxiliary_evidence": auxiliary,
        "continuity_tracks": (
            [
                {
                    "track_id": f"{meta.evidence_id}-TRACK-APPEARANCE-GROUPING",
                    "track_kind": "PERSON_APPEARANCE",
                    "status": "CROSS_CUT_INFERRED",
                    "statement": "Recurring legacy appearance labels are treated only as an inferred cross-cut grouping, not verified identity.",
                    "source_refs": scene_refs,
                    "unknowns": ["Exact person identity across cuts remains unknown."],
                }
            ]
            if len(shots) > 1 else []
        ),
        "candidate_rules": rules,
        "unknowns": [
            {
                "unknown_id": "UNKNOWN-AUDIO",
                "statement": "Direct soundtrack audition was not completed, so semantic audio facts remain unknown.",
                "scope": "AUDIO",
                "blocks_rule_ids": [rule["candidate_rule_id"] for rule in rules],
            },
            {
                "unknown_id": "UNKNOWN-EXECUTION",
                "statement": "Cross-work transfer and generation execution remain unverified and unknown.",
                "scope": "RULE",
                "blocks_rule_ids": [rule["candidate_rule_id"] for rule in rules],
            },
        ],
        "rights_boundary": {
            "media_committed": False,
            "subtitles_committed": False,
            "scripts_or_long_dialogue_committed": False,
            "contains_absolute_local_paths": False,
            "contains_media_hashes": False,
            "reference_surface_terms": [meta.work_id.replace("-", " ")],
            "surface_inventory_status": "HUMAN_REVIEWED_COMPLETE",
            "prohibited_transfer_content": [
                "Reference characters, locations, props, dialogue, scene events, and signature compositions."
            ],
            "notes": "Human review confirmed that every operational candidate-rule field is the same fixed source-neutral pending-review placeholder. Work-specific legacy text remains only in non-operational lineage; no source media or temporary artifact is embedded.",
        },
        "validation_status": "HUMAN_REVIEW_PENDING",
        "validation_warnings": [
            "Legacy candidate rows are preserved only under legacy_migration; operational rule fields remain pending human review and are not authorized.",
            "Only explicitly recorded frame and PTS endpoints were migrated; missing endpoints remain null, displayed source timecodes remain the deterministic basis, and source media was not replayed.",
        ] + (
            [
                f"{missing_high_risk_fallbacks} high-risk Shot rows lacked an explicit legacy FALLBACK; generic project-original fallbacks remain provisional pending human review."
            ]
            if missing_high_risk_fallbacks
            else []
        ),
    }
    return evidence


def discover_sources() -> list[Path]:
    sources = sorted(
        path for path in EVIDENCE_ROOT.rglob("*.md")
        if path.stem in SCENE_META
    )
    missing = sorted(set(SCENE_META) - {path.stem for path in sources})
    if missing:
        raise ValueError(f"closed-corpus source(s) missing: {', '.join(missing)}")
    if len(sources) != len(SCENE_META):
        raise ValueError(
            f"expected {len(SCENE_META)} canonical migration sources, found {len(sources)}"
        )
    return sources


def output_path(source: Path, output_root: Path | None) -> Path:
    name = f"{source.stem}.scene-evidence.json"
    if output_root is None:
        return source.with_name(name)
    try:
        parent = source.resolve().parent.relative_to(EVIDENCE_ROOT.resolve())
    except ValueError:
        parent = Path()
    return output_root / parent / name


def serialized_evidence(evidence: dict[str, Any]) -> str:
    return json.dumps(evidence, ensure_ascii=False, indent=2) + "\n"


def validate_generated(evidence: dict[str, Any]) -> dict[str, Any]:
    report = validate_evidence(evidence, load_json(SCHEMA_PATH))
    if not report["passed"]:
        errors = [item for item in report["issues"] if item["level"] == "error"]
        detail = "\n".join(f"{item['code']} {item['path']}: {item['message']}" for item in errors[:30])
        raise ValueError(f"generated Scene Evidence failed validation:\n{detail}")
    return report


def run(sources: Sequence[Path], output_root: Path | None, check: bool) -> tuple[int, int, int]:
    converted = 0
    shot_count = 0
    rule_count = 0
    mismatches: list[str] = []
    for source in sources:
        evidence = build_evidence(source)
        validate_generated(evidence)
        content = serialized_evidence(evidence)
        destination = output_path(source, output_root)
        if check:
            if not destination.exists() or destination.read_text(encoding="utf-8") != content:
                mismatches.append(destination.as_posix())
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        converted += 1
        shot_count += len(evidence["shots"])
        rule_count += len(evidence["candidate_rules"])
    if mismatches:
        raise ValueError("missing or stale generated output(s): " + ", ".join(mismatches))
    return converted, shot_count, rule_count


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", type=Path, help="legacy Markdown source(s); defaults to the canonical migration corpus")
    parser.add_argument("--output-root", type=Path, help="mirror generated files under this directory")
    parser.add_argument("--check", action="store_true", help="fail when generated files are absent or stale; do not write")
    args = parser.parse_args(argv)
    try:
        sources = list(args.sources) if args.sources else discover_sources()
        converted, shots, rules = run(sources, args.output_root, args.check)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    mode = "checked" if args.check else "generated"
    print(f"{mode} {converted} scene(s): {shots} Shot/edit units, {rules} candidate rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
