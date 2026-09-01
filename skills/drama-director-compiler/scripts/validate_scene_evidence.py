#!/usr/bin/env python3
"""Validate DirectorMind Scene Evidence without requiring third-party packages.

This validator checks the JSON Schema subset used by scene-evidence.schema.json
and the cross-field evidence rules that JSON Schema cannot express. Structural
success is not creative approval and does not re-prove observations from media.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


VALIDATOR_VERSION = "scene-evidence-validator/0.1"
RISK_REQUIRES_FALLBACK = {"HIGH", "CRITICAL"}
VISUAL_CLAIM_STATUSES = {"PICTURE_OBSERVED", "INFERRED", "UNKNOWN"}
AUDIO_CLAIM_STATUSES = {"AUDIO_OBSERVED", "INFERRED", "UNKNOWN"}
PROMOTED_STATUSES = {"CROSS_WORK_SUPPORTED", "GENERAL_DEFAULT"}
VERIFIED_COUNTEREXAMPLES = {
    "VERIFIED_SAME_TRIGGER_DIFFERENT_MECHANISM",
    "VERIFIED_SAME_TRIGGER_FAILURE",
}
ACTIVE_METHOD_STATUSES = {"REPOSITORY_REPRODUCIBLE", "MANUAL_REVIEW_RECORDED"}
ABSOLUTE_PATH_RE = re.compile(
    r"(?:^|[\s='\"(])(?:~[/]|/(?:[A-Za-z0-9._-]+/)+[^\s'\")]+|file:/+|[A-Za-z]:[\\/])"
)
MEDIA_OR_SUBTITLE_RE = re.compile(
    r"\.(?:mp4|mkv|mov|avi|m4v|webm|m2ts|mts|mpg|mpeg|wmv|flv|wav|mp3|m4a|aac|"
    r"flac|ogg|opus|aiff?|png|jpe?g|heic|heif|webp|gif|bmp|tiff?|srt|ssa|ass|vtt)(?:\b|$)",
    re.IGNORECASE,
)
DATA_URI_RE = re.compile(
    r"\bdata:[a-z0-9.+-]+/[a-z0-9.+-]+(?:;[^,\s]*)?,",
    re.IGNORECASE,
)
CREDENTIAL_RE = re.compile(
    r"(?:-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"\bauthorization\s*:\s*bearer\s+[A-Za-z0-9._~+/=-]{8,}\b|"
    r"\b(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret)\s*[:=]\s*[^\s,;]{8,})",
    re.IGNORECASE,
)
FINGERPRINT_LABEL_RE = re.compile(r"\b(?:sha(?:-?1|-?256|-?512)?|md5)\b", re.IGNORECASE)
LONG_HEX_RE = re.compile(r"\b[0-9a-f]{32,}\b", re.IGNORECASE)
RELEASE_LABEL_RE = re.compile(
    r"\b(?:WEB[-_. ]?DL|WEBRip|BluRay|BDRip|REMUX|HDRip|DVDRip|x264|x265|HEVC|BDYS|VINEnc|rrdyw)\b",
    re.IGNORECASE,
)
PICTURE_SEMANTIC_LEAK_RE = re.compile(
    r"\b(?:authority|challenger|witness|investigator|suspect|threat|attacker|victim|reaction|responds?|"
    r"realizes?|decides?|commands?|coerces?|consents?|afraid|angry|sad|nervous|tense|strained|"
    r"success|failure|confrontation|withdrawal|aftermath|searches?|investigates?|discovers?|corrects?)\b",
    re.IGNORECASE,
)
AUDIO_DIRECTIVE_RE = re.compile(
    r"(?:\b(?:add|use|insert|introduce|play|mute|drop|fade|bridge|cut|synchronize|trigger|drive|enter|"
    r"underscore|hold)\b[^.\n]{0,100}\b(?:audio|sound|sounds|cue|score|music|silence|voice|dialogue|"
    r"ambience|noise|alarm|ring|tone)\b|\b(?:audio|sound|sounds|cue|score|music|silence|voice|dialogue|"
    r"ambience|noise|alarm|ring|tone)\b[^.\n]{0,100}\b(?:add|use|insert|introduce|play|mute|drop|fade|enter|"
    r"bridge|cut|synchronize|trigger|drive|underscore|hold)\b|"
    r"\b(?:audio|sound|sounds|cue|score|music|silence|voice|dialogue|ambience|noise|alarm|ring|tone)\b"
    r"[^.\n]{0,60}\b(?:should|must)\s+(?:enter|begin|start|precede|lead)\b|"
    r"\bbring\s+in\b[^.\n]{0,60}\b(?:audio|sound|sounds|cue|score|music|silence|voice|dialogue|"
    r"ambience|noise|alarm|ring|tone)\b|"
    r"\bbring\b[^.\n]{0,60}\b(?:audio|sound|sounds|cue|score|music|silence|voice|dialogue|"
    r"ambience|noise|alarm|ring|tone)\b[^.\n]{0,20}\bin\b)",
    re.IGNORECASE,
)
AUDIO_UNCERTAINTY_RE = re.compile(
    r"\b(?:unknown|unverified|not (?:directly )?observed|not (?:directly )?auditioned|blocked|"
    r"not part of this candidate|outside (?:this|the) candidate|excluded from (?:this|the) candidate|"
    r"does not depend on (?:audio|sound|score|music)|no audio rule)\b",
    re.IGNORECASE,
)
AUDIO_TERM_RE = re.compile(
    r"\b(?:audio|sound|sounds|cue|score|music|silence|voice|dialogue|ambience|noise|alarm|ring|tone)\b",
    re.IGNORECASE,
)
GENERAL_UNCERTAINTY_RE = re.compile(
    r"\b(?:unknown|unverified|unproven|unconfirmed|not (?:directly )?(?:observed|auditioned|established|"
    r"verified|shown|visible)|cannot be (?:confirmed|established|verified)|remains? uncertain|blocked)\b",
    re.IGNORECASE,
)
SIGNAL_SEMANTIC_LEAK_RE = re.compile(
    r"\b(?:hearing loss|hearing state|tinnitus|subjective (?:hearing|sound|audio|POV)|audience (?:emotion|"
    r"effect|experience)|emotion|reaction cause|sound source|dialogue|intelligibility|diagnosis)\b",
    re.IGNORECASE,
)
UNKNOWN_FACT_STOPWORDS = {
    "a", "an", "and", "are", "at", "be", "been", "being", "by", "cannot", "confirmed",
    "directly", "established", "exact", "for", "from", "if", "in", "is", "not", "of", "on",
    "or", "picture", "remain", "that", "the", "this", "to", "unknown", "unconfirmed",
    "unproven", "unverified", "verified", "visible", "was", "were", "whether", "with",
}
SAFE_UNKNOWN_BOUNDARY_RE = re.compile(
    r"(?:\b(?:does not|do not|must not|should not|without|avoid)\b[^.\n]{0,80}"
    r"\b(?:depend|assum|assert|treat|identify|confirm|require)\w*\b|"
    r"\b(?:no|without|avoid|do not|must not|should not)\b[^.\n]{0,80}"
    r"\b(?:physical\s+)?(?:contact|touch|joined? hands?)\b)",
    re.IGNORECASE,
)
UNKNOWN_FACT_ALIAS_PATTERNS = {
    "axis": re.compile(r"\b(?:axis|180[- ]degree|screen direction|line of action)\b", re.IGNORECASE),
    "identity": re.compile(
        r"\b(?:identity|same (?:person|individual|body|appearance)|continuing (?:person|individual|appearance))\b",
        re.IGNORECASE,
    ),
    "contact": re.compile(
        r"\b(?:physical contact|contact|touch(?:es|ed|ing)?|hands? (?:join(?:ed|ing)?|touch(?:ed|ing)?|"
        r"meet(?:s|ing)?)|(?:join(?:ed|ing)?|hold(?:s|ing)?) hands?|reach(?:es|ed|ing)? first)\b",
        re.IGNORECASE,
    ),
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def add_issue(
    issues: list[dict[str, str]],
    level: str,
    code: str,
    path: str,
    message: str,
) -> None:
    issues.append({"level": level, "code": code, "path": path, "message": message})


def _json_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _resolve_ref(root_schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"only local JSON Schema references are supported: {ref}")
    node: Any = root_schema
    for raw_part in ref[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        node = node[part]
    if not isinstance(node, dict):
        raise ValueError(f"schema reference does not resolve to an object: {ref}")
    return node


def validate_schema_subset(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    issues: list[dict[str, str]],
    path: str = "$",
) -> None:
    """Validate the deterministic JSON Schema subset used by this project."""
    if "$ref" in schema:
        try:
            resolved = _resolve_ref(root_schema, schema["$ref"])
        except (KeyError, TypeError, ValueError) as exc:
            add_issue(issues, "error", "SCHEMA-REF", path, str(exc))
            return
        validate_schema_subset(value, resolved, root_schema, issues, path)
        return

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = [expected_type] if isinstance(expected_type, str) else expected_type
        if not any(_json_type_matches(value, item) for item in expected_types):
            add_issue(
                issues,
                "error",
                "SCHEMA-TYPE",
                path,
                f"expected type {expected_types}, got {type(value).__name__}",
            )
            return

    if "const" in schema and value != schema["const"]:
        add_issue(issues, "error", "SCHEMA-CONST", path, f"expected constant {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        add_issue(issues, "error", "SCHEMA-ENUM", path, f"value {value!r} is not in the allowed enum")

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                add_issue(issues, "error", "SCHEMA-REQUIRED", f"{path}.{key}", "required field is missing")
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                validate_schema_subset(item, properties[key], root_schema, issues, child_path)
                continue
            additional = schema.get("additionalProperties", True)
            if additional is False:
                add_issue(issues, "error", "SCHEMA-ADDITIONAL", child_path, "additional field is not allowed")
            elif isinstance(additional, dict):
                validate_schema_subset(item, additional, root_schema, issues, child_path)

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            add_issue(issues, "error", "SCHEMA-MIN-ITEMS", path, "array has too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            add_issue(issues, "error", "SCHEMA-MAX-ITEMS", path, "array has too many items")
        if schema.get("uniqueItems"):
            normalized = [json.dumps(item, ensure_ascii=False, sort_keys=True) for item in value]
            if len(normalized) != len(set(normalized)):
                add_issue(issues, "error", "SCHEMA-UNIQUE", path, "array items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_schema_subset(item, item_schema, root_schema, issues, f"{path}[{index}]")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            add_issue(issues, "error", "SCHEMA-MIN-LENGTH", path, "string is shorter than allowed")
        pattern = schema.get("pattern")
        if pattern and re.search(pattern, value) is None:
            add_issue(issues, "error", "SCHEMA-PATTERN", path, f"string does not match {pattern!r}")

    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        if "minimum" in schema and value < schema["minimum"]:
            add_issue(issues, "error", "SCHEMA-MINIMUM", path, f"value must be >= {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            add_issue(issues, "error", "SCHEMA-MAXIMUM", path, f"value must be <= {schema['maximum']}")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            add_issue(issues, "error", "SCHEMA-EXCLUSIVE-MINIMUM", path, f"value must be > {schema['exclusiveMinimum']}")


def parse_timecode(value: str) -> float | None:
    match = re.fullmatch(r"([0-9]{2,}):([0-5][0-9]):([0-5][0-9](?:\.[0-9]{1,9})?)", value)
    if match is None:
        return None
    return int(match.group(1)) * 3600 + int(match.group(2)) * 60 + float(match.group(3))


def _walk_strings(value: Any, path: str = "$") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_strings(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _walk_strings(item, f"{path}.{key}")


def _walk_claims(value: Any, path: str = "$") -> Iterator[tuple[str, dict[str, Any]]]:
    if isinstance(value, dict):
        if {"claim_id", "status", "value", "source_refs"}.issubset(value):
            yield path, value
        for key, item in value.items():
            yield from _walk_claims(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_claims(item, f"{path}[{index}]")


def _risk_level(container: dict[str, Any], axis: str) -> str | None:
    risk = container.get("AI_complexity") or container.get("AI_risk") or {}
    dimension = risk.get(axis) if isinstance(risk, dict) else None
    return dimension.get("level") if isinstance(dimension, dict) else None


def _validate_risk_fallback(
    container: dict[str, Any],
    path: str,
    issues: list[dict[str, str]],
) -> None:
    fallback = container.get("fallback") if isinstance(container.get("fallback"), dict) else {}
    if fallback.get("project_original_only") is not True:
        add_issue(
            issues,
            "error",
            "FALLBACK-PROJECT-ORIGINAL",
            f"{path}.fallback.project_original_only",
            "fallback must remain project-original only",
        )
    for axis in ("camera", "performance", "continuity"):
        level = _risk_level(container, axis)
        text = fallback.get(axis)
        if level in RISK_REQUIRES_FALLBACK and (not isinstance(text, str) or not text.strip()):
            add_issue(
                issues,
                "error",
                "HIGH-RISK-NO-FALLBACK",
                f"{path}.fallback.{axis}",
                f"{axis} risk {level} requires a concrete project-original fallback",
            )


def _validate_time_point(
    point: Any,
    path: str,
    tolerance: float,
    issues: list[dict[str, str]],
) -> None:
    if not isinstance(point, dict):
        return
    timecode = point.get("timecode")
    seconds = point.get("seconds")
    if not isinstance(timecode, str) or not isinstance(seconds, (int, float)) or isinstance(seconds, bool):
        return
    parsed = parse_timecode(timecode)
    if parsed is not None and abs(parsed - float(seconds)) > tolerance + 1e-9:
        add_issue(
            issues,
            "error",
            "TIMECODE-SECONDS-MISMATCH",
            path,
            f"timecode differs from seconds by {abs(parsed - float(seconds)):.6f}s",
        )


def _validate_public_boundary(evidence: dict[str, Any], issues: list[dict[str, str]]) -> None:
    for path, text in _walk_strings(evidence):
        if ABSOLUTE_PATH_RE.search(text):
            add_issue(issues, "error", "PUBLIC-ABSOLUTE-PATH", path, "absolute local path is prohibited")
        if MEDIA_OR_SUBTITLE_RE.search(text):
            add_issue(issues, "error", "PUBLIC-MEDIA-OR-SUBTITLE", path, "media or subtitle filename is prohibited")
        if DATA_URI_RE.search(text):
            add_issue(issues, "error", "PUBLIC-DATA-URI", path, "embedded data payload is prohibited")
        if CREDENTIAL_RE.search(text):
            add_issue(issues, "error", "PUBLIC-CREDENTIAL", path, "credential-like material is prohibited")
        if FINGERPRINT_LABEL_RE.search(text) or LONG_HEX_RE.search(text):
            add_issue(issues, "error", "PUBLIC-FINGERPRINT", path, "media fingerprint material is prohibited")
        if RELEASE_LABEL_RE.search(text):
            add_issue(issues, "error", "PUBLIC-RELEASE-LABEL", path, "raw release label is prohibited")


def _operational_rule_text(rule: dict[str, Any]) -> str:
    values: list[Any] = [
        rule.get("canonical_rule_family"),
        rule.get("trigger"),
        rule.get("director_decision"),
        rule.get("coverage"),
        rule.get("blocking"),
        rule.get("POV_effect"),
        rule.get("edit_logic"),
        rule.get("pacing"),
        rule.get("continuity"),
        rule.get("applicable_when"),
        rule.get("not_applicable_when"),
        rule.get("failure_modes"),
        rule.get("AI_risk"),
        rule.get("fallback"),
        (rule.get("audio_logic") or {}).get("value") if isinstance(rule.get("audio_logic"), dict) else None,
    ]
    return ". ".join(text for _, text in _walk_strings(values)).lower()


def _term_occurs(text: str, term: str) -> bool:
    """Match a declared surface term without substring false positives."""
    normalized = term.strip()
    plural = "" if normalized.lower().endswith("s") else r"(?:s|es)?"
    return re.search(rf"(?<!\w){re.escape(normalized)}{plural}(?!\w)", text, re.IGNORECASE) is not None


def _has_unauditioned_audio_assertion(text: str) -> bool:
    """Reject an audio-domain rule clause that does not itself state uncertainty."""
    for sentence in re.split(r"[.!?;\n]+", text):
        for clause in re.split(r"\b(?:but|however|yet|although)\b", sentence, flags=re.IGNORECASE):
            if AUDIO_TERM_RE.search(clause) and AUDIO_UNCERTAINTY_RE.search(clause) is None:
                return True
    return False


def _fact_tokens(text: str) -> set[str]:
    """Return conservative content tokens for matching an active UNKNOWN to rule prose."""
    result: set[str] = set()
    for raw_token in re.findall(r"[a-z0-9]+", text.lower().replace("-", " ")):
        if raw_token in UNKNOWN_FACT_STOPWORDS:
            continue
        token = raw_token
        if token.endswith("ies") and len(token) > 4:
            token = f"{token[:-3]}y"
        elif token.endswith("ing") and len(token) > 5:
            token = token[:-3]
        elif token.endswith("ed") and len(token) > 4:
            token = token[:-2]
        elif token.endswith("s") and len(token) > 4 and not token.endswith(("ss", "is", "us")):
            token = token[:-1]
        if len(token) > 1 and token not in UNKNOWN_FACT_STOPWORDS:
            result.add(token)
    return result


def _rule_asserts_unknown_fact(unknown_text: str, operational_text: str) -> bool:
    """Detect a close factual restatement; broad semantic inference remains a human review boundary."""
    unknown_tokens = _fact_tokens(unknown_text)
    active_alias_patterns = [
        pattern for pattern in UNKNOWN_FACT_ALIAS_PATTERNS.values() if pattern.search(unknown_text)
    ]
    if len(unknown_tokens) < 2 and not active_alias_patterns:
        return False
    for sentence in re.split(r"[.!?;\n]+", operational_text):
        clauses = re.split(r"\b(?:but|however|yet|although)\b", sentence, flags=re.IGNORECASE)
        for clause in clauses:
            if GENERAL_UNCERTAINTY_RE.search(clause) or SAFE_UNKNOWN_BOUNDARY_RE.search(clause):
                continue
            shared = unknown_tokens.intersection(_fact_tokens(clause))
            if len(shared) >= 2 and len(shared) / len(unknown_tokens) >= 0.5:
                return True
            if any(pattern.search(clause) for pattern in active_alias_patterns):
                return True
    return False


def _display_path(path: Path) -> str:
    """Return a repository-safe report path instead of an absolute host path."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def validate_semantics(evidence: dict[str, Any], issues: list[dict[str, str]]) -> None:
    tolerance_raw = evidence.get("time_tolerance_seconds", 0.001)
    tolerance = float(tolerance_raw) if isinstance(tolerance_raw, (int, float)) and not isinstance(tolerance_raw, bool) else 0.001
    evidence_id = evidence.get("evidence_id")
    source_start = evidence.get("source_start") if isinstance(evidence.get("source_start"), dict) else {}
    source_end = evidence.get("source_end") if isinstance(evidence.get("source_end"), dict) else {}
    _validate_time_point(source_start, "$.source_start", tolerance, issues)
    _validate_time_point(source_end, "$.source_end", tolerance, issues)

    shots = evidence.get("shots") if isinstance(evidence.get("shots"), list) else []
    shot_ids: set[str] = set()
    shot_by_id: dict[str, dict[str, Any]] = {}
    durations: list[float] = []
    for index, shot in enumerate(shots):
        if not isinstance(shot, dict):
            continue
        path = f"$.shots[{index}]"
        shot_id = shot.get("shot_id")
        if isinstance(shot_id, str):
            if shot_id in shot_ids:
                add_issue(issues, "error", "SHOT-ID-DUPLICATE", f"{path}.shot_id", "shot ID must be unique")
            shot_ids.add(shot_id)
            shot_by_id[shot_id] = shot
            if isinstance(evidence_id, str) and not shot_id.startswith(f"{evidence_id}-S"):
                add_issue(
                    issues,
                    "error",
                    "SHOT-ID-NAMESPACE",
                    f"{path}.shot_id",
                    "shot ID must be namespaced to its owning evidence_id",
                )
            suffix = re.search(r"-S([0-9]{3,4})$", shot_id)
            if suffix and int(suffix.group(1)) != index + 1:
                add_issue(issues, "error", "SHOT-ID-ORDER", f"{path}.shot_id", "shot ID suffix must match shot order")
        if shot.get("order") != index + 1:
            add_issue(issues, "error", "SHOT-ORDER", f"{path}.order", "shot order must be contiguous from 1")

        start = shot.get("start") or {}
        end = shot.get("end") or {}
        _validate_time_point(start, f"{path}.start", tolerance, issues)
        _validate_time_point(end, f"{path}.end", tolerance, issues)
        start_seconds = start.get("seconds")
        end_seconds = end.get("seconds")
        duration = shot.get("duration")
        if all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in (start_seconds, end_seconds, duration)):
            calculated = float(end_seconds) - float(start_seconds)
            if calculated <= 0:
                add_issue(issues, "error", "SHOT-NONPOSITIVE-SPAN", path, "shot end must be after start")
            if abs(calculated - float(duration)) > tolerance:
                add_issue(
                    issues,
                    "error",
                    "SHOT-DURATION-MISMATCH",
                    f"{path}.duration",
                    f"declared duration differs from endpoints by {abs(calculated - float(duration)):.6f}s",
                )
            durations.append(float(duration))
        start_frame = start.get("frame")
        end_frame = end.get("frame")
        if isinstance(start_frame, int) and isinstance(end_frame, int) and end_frame <= start_frame:
            add_issue(issues, "error", "SHOT-FRAME-SPAN", path, "end frame must be greater than start frame")

        if index:
            previous = shots[index - 1] if isinstance(shots[index - 1], dict) else {}
            previous_end = (previous.get("end") or {}).get("seconds")
            if isinstance(previous_end, (int, float)) and isinstance(start_seconds, (int, float)):
                delta = float(start_seconds) - float(previous_end)
                if delta > tolerance:
                    add_issue(issues, "error", "SHOT-GAP", f"{path}.start", f"gap of {delta:.6f}s after prior shot")
                elif delta < -tolerance:
                    add_issue(issues, "error", "SHOT-OVERLAP", f"{path}.start", f"overlap of {-delta:.6f}s with prior shot")
            previous_frame = (previous.get("end") or {}).get("frame")
            if isinstance(previous_frame, int) and isinstance(start_frame, int) and previous_frame != start_frame:
                code = "SHOT-FRAME-GAP" if start_frame > previous_frame else "SHOT-FRAME-OVERLAP"
                add_issue(issues, "error", code, f"{path}.start.frame", "adjacent end/start frames must match")

        _validate_risk_fallback(shot, path, issues)

    if shots:
        first_start = ((shots[0] or {}).get("start") or {}).get("seconds") if isinstance(shots[0], dict) else None
        last_end = ((shots[-1] or {}).get("end") or {}).get("seconds") if isinstance(shots[-1], dict) else None
        source_start_seconds = source_start.get("seconds")
        source_end_seconds = source_end.get("seconds")
        if isinstance(first_start, (int, float)) and isinstance(source_start_seconds, (int, float)) and abs(float(first_start) - float(source_start_seconds)) > tolerance:
            add_issue(issues, "error", "SCENE-START-MISMATCH", "$.shots[0].start", "first shot must start at source_start")
        if isinstance(last_end, (int, float)) and isinstance(source_end_seconds, (int, float)) and abs(float(last_end) - float(source_end_seconds)) > tolerance:
            add_issue(issues, "error", "SCENE-END-MISMATCH", f"$.shots[{len(shots) - 1}].end", "last shot must end at source_end")

    source_start_seconds = source_start.get("seconds")
    source_end_seconds = source_end.get("seconds")
    scene_duration = evidence.get("duration")
    if all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in (source_start_seconds, source_end_seconds, scene_duration)):
        endpoint_duration = float(source_end_seconds) - float(source_start_seconds)
        if abs(endpoint_duration - float(scene_duration)) > tolerance:
            add_issue(issues, "error", "SCENE-DURATION-MISMATCH", "$.duration", "scene duration must match source endpoints")
        if durations and abs(sum(durations) - float(scene_duration)) > tolerance:
            add_issue(issues, "error", "SHOT-DURATION-SUM", "$.shots", "shot durations must sum to scene duration")

    stats = evidence.get("stats") if isinstance(evidence.get("stats"), dict) else {}
    if stats.get("shot_count") != len(shots):
        add_issue(issues, "error", "STATS-SHOT-COUNT", "$.stats.shot_count", "shot_count must match shots length")
    if durations:
        expected_total = sum(durations)
        expected_mean = statistics.mean(durations)
        expected_median = statistics.median(durations)
        for key, expected in (("total_duration", expected_total), ("mean_duration", expected_mean), ("median_duration", expected_median)):
            actual = stats.get(key)
            if isinstance(actual, (int, float)) and not isinstance(actual, bool) and abs(float(actual) - expected) > tolerance:
                add_issue(issues, "error", f"STATS-{key.upper().replace('_', '-')}", f"$.stats.{key}", f"value must equal {expected:.9f} within tolerance")
        duration_bins = stats.get("duration_bins")
        if isinstance(duration_bins, dict) and duration_bins and sum(item for item in duration_bins.values() if isinstance(item, int)) != len(shots):
            add_issue(issues, "error", "STATS-BINS", "$.stats.duration_bins", "duration-bin counts must sum to shot_count")

    claims: dict[str, tuple[str, dict[str, Any]]] = {}
    for claim_path, claim in _walk_claims(evidence):
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str):
            continue
        if claim_id in claims:
            add_issue(issues, "error", "CLAIM-ID-DUPLICATE", f"{claim_path}.claim_id", "claim ID must be globally unique in one scene")
        claims[claim_id] = (claim_path, claim)
        status = claim.get("status")
        refs = claim.get("source_refs")
        if status in {"PICTURE_OBSERVED", "AUDIO_OBSERVED", "TEXT_ANCHOR", "INFERRED"} and (not isinstance(refs, list) or not refs):
            add_issue(issues, "error", "CLAIM-SOURCE-REQUIRED", f"{claim_path}.source_refs", f"{status} claim requires cited source evidence")
        if status == "UNKNOWN" and isinstance(refs, list) and refs:
            add_issue(issues, "error", "UNKNOWN-HAS-SOURCE", f"{claim_path}.source_refs", "UNKNOWN must not be presented as a supported fact")
        if status == "UNKNOWN" and isinstance(claim.get("value"), str) and GENERAL_UNCERTAINTY_RE.search(claim["value"]) is None:
            add_issue(
                issues,
                "error",
                "UNKNOWN-VALUE-ASSERTS-FACT",
                f"{claim_path}.value",
                "UNKNOWN claim wording must explicitly state uncertainty",
            )
        if status == "PICTURE_OBSERVED" and isinstance(claim.get("value"), str) and PICTURE_SEMANTIC_LEAK_RE.search(claim["value"]):
            add_issue(
                issues,
                "error",
                "PICTURE-SEMANTIC-LEAK",
                f"{claim_path}.value",
                "picture-observed wording contains a role, reaction, intention, emotion, or outcome label",
            )

    visual_claim_paths = [
        "$.boundary_evidence", "$.spatial_geometry", "$.axis", "$.POV", "$.audience_information",
    ]
    for index, shot in enumerate(shots):
        for key in (
            "shot_size", "camera_height", "camera_angle", "camera_motion", "camera_start", "camera_path",
            "camera_end", "focus_strategy", "axis_and_screen_direction", "blocking", "visible_action",
            "visible_state_in", "visible_state_out", "event_or_reaction", "performance_beat", "edit_in", "edit_out",
            "cut_motivation", "narrative_function",
        ):
            visual_claim_paths.append(f"$.shots[{index}].{key}")
        for zone_index, _ in enumerate(shot.get("spatial_zone", []) if isinstance(shot, dict) else []):
            visual_claim_paths.append(f"$.shots[{index}].spatial_zone[{zone_index}]")
    claim_by_path = {path: claim for path, claim in _walk_claims(evidence)}
    for path in visual_claim_paths:
        claim = claim_by_path.get(path)
        if isinstance(claim, dict) and claim.get("status") not in VISUAL_CLAIM_STATUSES:
            add_issue(issues, "error", "VISUAL-CLAIM-WRONG-TRACK", f"{path}.status", "visual fact cannot be proved by audio or text alone")

    audio_audit = evidence.get("audio_audit") if isinstance(evidence.get("audio_audit"), dict) else {}
    for key, claim in audio_audit.items():
        if key == "audio_unknowns" or not isinstance(claim, dict):
            continue
        if claim.get("status") not in AUDIO_CLAIM_STATUSES:
            add_issue(issues, "error", "AUDIO-CLAIM-WRONG-TRACK", f"$.audio_audit.{key}.status", "audio audit must use audio, inferred, or unknown status")

    picture_status = evidence.get("picture_evidence_status")
    audio_status = evidence.get("audio_evidence_status")
    text_status = evidence.get("text_anchor_status")
    for shot_index, shot in enumerate(shots):
        if not isinstance(shot, dict):
            continue
        path = f"$.shots[{shot_index}]"
        shot_picture_status = shot.get("picture_status")
        shot_audio_status = shot.get("audio_status")
        shot_text_status = shot.get("text_anchor_status")
        if picture_status == "PICTURE_UNVERIFIED" and shot_picture_status != "PICTURE_UNVERIFIED":
            add_issue(
                issues,
                "error",
                "SHOT-PICTURE-STATUS-CONFLICT",
                f"{path}.picture_status",
                "an unverified scene cannot contain an observed or partial Shot status",
            )
        if shot_picture_status == "PICTURE_UNVERIFIED":
            for relative_path, claim in _walk_claims(shot, path):
                if claim.get("status") == "PICTURE_OBSERVED":
                    add_issue(
                        issues,
                        "error",
                        "SHOT-PICTURE-CLAIM-CONFLICT",
                        f"{relative_path}.status",
                        "an unverified Shot cannot contain picture-observed claims",
                    )
        expected_audio_scene = {
            "AUDIO_OBSERVED": "AUDIO_OBSERVED",
            "SIGNAL_MEASURED_NOT_AUDITIONED": "SIGNAL_MEASURED_NOT_AUDITIONED",
            "BLOCKED_DIRECT_AUDITION": "BLOCKED_DIRECT_AUDITION",
        }.get(shot_audio_status)
        if expected_audio_scene is not None and audio_status != expected_audio_scene:
            add_issue(
                issues,
                "error",
                "SHOT-AUDIO-STATUS-CONFLICT",
                f"{path}.audio_status",
                "Shot audio status conflicts with the scene audio evidence status",
            )
        if shot_text_status == "TEXT_ANCHOR_VERIFIED" and text_status != "TEXT_ANCHOR_VERIFIED":
            add_issue(
                issues,
                "error",
                "SHOT-TEXT-STATUS-CONFLICT",
                f"{path}.text_anchor_status",
                "verified Shot text requires verified scene text-anchor status",
            )
        if shot_text_status == "TEXT_ANCHOR_PARTIAL" and text_status not in {
            "TEXT_ANCHOR_VERIFIED", "TEXT_ANCHOR_PARTIAL"
        }:
            add_issue(
                issues,
                "error",
                "SHOT-TEXT-STATUS-CONFLICT",
                f"{path}.text_anchor_status",
                "partial Shot text requires verified or partial scene text-anchor status",
            )
    if audio_status != "AUDIO_OBSERVED":
        for key, claim in audio_audit.items():
            if key == "audio_unknowns" or not isinstance(claim, dict):
                continue
            if claim.get("status") != "UNKNOWN":
                add_issue(
                    issues,
                    "error",
                    "AUDIO-AUDIT-WITHOUT-DIRECT-OBSERVATION",
                    f"$.audio_audit.{key}.status",
                    "semantic audio-audit fields must remain UNKNOWN until direct audition",
                )
            value = claim.get("value")
            if isinstance(value, str) and (
                AUDIO_DIRECTIVE_RE.search(value)
                or AUDIO_UNCERTAINTY_RE.search(value) is None
                or _has_unauditioned_audio_assertion(value)
            ):
                add_issue(
                    issues,
                    "error",
                    "AUDIO-UNKNOWN-HIDES-DIRECTIVE",
                    f"$.audio_audit.{key}.value",
                    "unknown audio fields must state uncertainty and must not prescribe sound",
                )
    for claim_path, claim in _walk_claims(evidence):
        if claim.get("status") == "PICTURE_OBSERVED" and picture_status == "PICTURE_UNVERIFIED":
            add_issue(issues, "error", "PICTURE-STATUS-CONFLICT", f"{claim_path}.status", "picture-observed claim conflicts with unverified picture status")
        if claim.get("status") == "AUDIO_OBSERVED" and audio_status != "AUDIO_OBSERVED":
            add_issue(issues, "error", "AUDIO-STATUS-CONFLICT", f"{claim_path}.status", "audio-observed claim requires direct audio observation status")
        if claim.get("status") == "TEXT_ANCHOR" and text_status in {"TEXT_ANCHOR_NOT_USED", "TEXT_ANCHOR_UNKNOWN"}:
            add_issue(issues, "error", "TEXT-STATUS-CONFLICT", f"{claim_path}.status", "text-anchor claim conflicts with scene text status")

    text_anchors = evidence.get("text_anchors") if isinstance(evidence.get("text_anchors"), list) else []
    anchor_ids = {item.get("anchor_id") for item in text_anchors if isinstance(item, dict) and isinstance(item.get("anchor_id"), str)}
    if text_status == "TEXT_ANCHOR_NOT_USED" and text_anchors:
        add_issue(issues, "error", "TEXT-ANCHORS-UNEXPECTED", "$.text_anchors", "text anchors must be empty when text was not used")
    for claim_path, claim in _walk_claims(evidence):
        if claim.get("status") == "TEXT_ANCHOR":
            missing = [ref for ref in claim.get("source_refs", []) if ref not in anchor_ids]
            if missing:
                add_issue(issues, "error", "TEXT-ANCHOR-REF-MISSING", f"{claim_path}.source_refs", f"unknown text anchor(s): {', '.join(missing)}")

    scene_problem = evidence.get("scene_problem") if isinstance(evidence.get("scene_problem"), dict) else {}
    scene_problem_status = scene_problem.get("status")
    scene_problem_refs = scene_problem.get("source_refs")
    if scene_problem_status in {"TEXT_ANCHOR", "INFERRED"} and (not isinstance(scene_problem_refs, list) or not scene_problem_refs):
        add_issue(issues, "error", "SCENE-PROBLEM-SOURCE-REQUIRED", "$.scene_problem.source_refs", "scene-problem classification requires cited evidence")
    if scene_problem_status == "UNKNOWN" and isinstance(scene_problem_refs, list) and scene_problem_refs:
        add_issue(issues, "error", "SCENE-PROBLEM-UNKNOWN-HAS-SOURCE", "$.scene_problem.source_refs", "unknown scene problem must not be presented as supported")
    if scene_problem_status == "TEXT_ANCHOR":
        missing = [ref for ref in scene_problem_refs if ref not in anchor_ids] if isinstance(scene_problem_refs, list) else []
        if missing:
            add_issue(issues, "error", "SCENE-PROBLEM-TEXT-REF-MISSING", "$.scene_problem.source_refs", f"unknown text anchor(s): {', '.join(missing)}")

    role_occurrences: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    for shot_index, shot in enumerate(shots):
        if not isinstance(shot, dict):
            continue
        for role_index, role in enumerate(shot.get("abstract_role_labels", []) if isinstance(shot.get("abstract_role_labels"), list) else []):
            if not isinstance(role, dict):
                continue
            path = f"$.shots[{shot_index}].abstract_role_labels[{role_index}]"
            appearance_id = role.get("appearance_id")
            if isinstance(appearance_id, str):
                role_occurrences.setdefault(appearance_id, []).append((path, role))
            role_status = role.get("status")
            functional_role = role.get("functional_role")
            source_refs = role.get("source_refs")
            if functional_role == "UNKNOWN" and role_status != "UNKNOWN":
                add_issue(issues, "error", "ROLE-UNKNOWN-STATUS", f"{path}.status", "UNKNOWN functional role must remain UNKNOWN")
            if functional_role != "UNKNOWN" and role_status == "UNKNOWN":
                add_issue(issues, "error", "ROLE-FUNCTION-UNSUPPORTED", f"{path}.status", "functional role needs inferred or text-anchor support")
            if role_status in {"TEXT_ANCHOR", "INFERRED"} and (not isinstance(source_refs, list) or not source_refs):
                add_issue(issues, "error", "ROLE-SOURCE-REQUIRED", f"{path}.source_refs", "functional role requires cited support")
            if role_status == "UNKNOWN" and isinstance(source_refs, list) and source_refs:
                add_issue(issues, "error", "ROLE-UNKNOWN-HAS-SOURCE", f"{path}.source_refs", "unknown role must not be presented as supported")
            if role_status == "TEXT_ANCHOR":
                missing = [ref for ref in source_refs or [] if ref not in anchor_ids]
                if missing:
                    add_issue(issues, "error", "ROLE-TEXT-REF-MISSING", f"{path}.source_refs", f"unknown text anchor(s): {', '.join(missing)}")
    methods = evidence.get("methods") if isinstance(evidence.get("methods"), list) else []
    method_ids: set[str] = set()
    method_by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(methods):
        if not isinstance(item, dict):
            continue
        path = f"$.methods[{index}]"
        method_id = item.get("method_id")
        if isinstance(method_id, str):
            if method_id in method_ids:
                add_issue(issues, "error", "METHOD-ID-DUPLICATE", f"{path}.method_id", "method ID must be unique")
            method_ids.add(method_id)
            method_by_id[method_id] = item
        if item.get("status") == "REPOSITORY_REPRODUCIBLE" and not item.get("repository_command"):
            add_issue(issues, "error", "METHOD-COMMAND-REQUIRED", f"{path}.repository_command", "repository-reproducible method needs a command")

    active_picture_method_ids = {
        method_id
        for method_id, item in method_by_id.items()
        if item.get("method_type") == "PICTURE_FRAME_REVIEW" and item.get("status") in ACTIVE_METHOD_STATUSES
    }
    active_audio_method_ids = {
        method_id
        for method_id, item in method_by_id.items()
        if item.get("method_type") == "AUDIO_DIRECT_AUDITION" and item.get("status") in ACTIVE_METHOD_STATUSES
    }
    active_text_method_ids = {
        method_id
        for method_id, item in method_by_id.items()
        if item.get("method_type") == "TEXT_ANCHOR_REVIEW" and item.get("status") in ACTIVE_METHOD_STATUSES
    }
    active_signal_method_ids = {
        method_id
        for method_id, item in method_by_id.items()
        if item.get("method_type") == "DECODED_SIGNAL_MEASUREMENT" and item.get("status") in ACTIVE_METHOD_STATUSES
    }
    if audio_status == "AUDIO_OBSERVED" and not active_audio_method_ids:
        add_issue(
            issues,
            "error",
            "AUDIO-OBSERVED-NO-DIRECT-METHOD",
            "$.audio_evidence_status",
            "AUDIO_OBSERVED requires an active AUDIO_DIRECT_AUDITION method",
        )
    if text_status in {"TEXT_ANCHOR_VERIFIED", "TEXT_ANCHOR_PARTIAL"} and not text_anchors:
        add_issue(
            issues,
            "error",
            "TEXT-STATUS-NO-ANCHOR",
            "$.text_anchor_status",
            "verified or partial text status requires at least one text anchor",
        )
    verified_or_partial_anchors = [
        item
        for item in text_anchors
        if isinstance(item, dict) and item.get("status") in {"TEXT_ANCHOR_VERIFIED", "TEXT_ANCHOR_PARTIAL"}
    ]
    if verified_or_partial_anchors and not active_text_method_ids:
        add_issue(
            issues,
            "error",
            "TEXT-ANCHOR-NO-REVIEW-METHOD",
            "$.text_anchors",
            "verified or partial text anchors require an active TEXT_ANCHOR_REVIEW method",
        )

    auxiliary = evidence.get("auxiliary_evidence") if isinstance(evidence.get("auxiliary_evidence"), list) else []
    auxiliary_ids: set[str] = set()
    auxiliary_by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(auxiliary):
        if not isinstance(item, dict):
            continue
        path = f"$.auxiliary_evidence[{index}]"
        auxiliary_id = item.get("auxiliary_id")
        if isinstance(auxiliary_id, str):
            if auxiliary_id in auxiliary_ids:
                add_issue(issues, "error", "AUXILIARY-ID-DUPLICATE", f"{path}.auxiliary_id", "auxiliary evidence ID must be unique")
            auxiliary_ids.add(auxiliary_id)
            auxiliary_by_id[auxiliary_id] = item
        _validate_time_point(item.get("start"), f"{path}.start", tolerance, issues)
        _validate_time_point(item.get("end"), f"{path}.end", tolerance, issues)
        status = item.get("status")
        if status == "AUDIO_OBSERVED" and audio_status != "AUDIO_OBSERVED":
            add_issue(issues, "error", "AUXILIARY-AUDIO-STATUS-CONFLICT", f"{path}.status", "audio-observed auxiliary evidence requires direct audio observation")
        if status == "SIGNAL_MEASURED_NOT_AUDITIONED" and audio_status != "SIGNAL_MEASURED_NOT_AUDITIONED":
            add_issue(issues, "error", "AUXILIARY-SIGNAL-STATUS-CONFLICT", f"{path}.status", "signal measurement requires matching scene audio status")
        method_id = item.get("method_id")
        if isinstance(method_id, str) and method_id not in method_ids:
            add_issue(issues, "error", "AUXILIARY-METHOD-REF-MISSING", f"{path}.method_id", f"unknown method ID: {method_id}")
        if status == "PICTURE_OBSERVED" and method_id not in active_picture_method_ids:
            add_issue(
                issues,
                "error",
                "AUXILIARY-PICTURE-METHOD",
                f"{path}.method_id",
                "picture-observed auxiliary evidence requires an active picture-review method",
            )
        if status == "AUDIO_OBSERVED" and method_id not in active_audio_method_ids:
            add_issue(
                issues,
                "error",
                "AUXILIARY-AUDIO-METHOD",
                f"{path}.method_id",
                "audio-observed auxiliary evidence requires an active direct-audition method",
            )
        if status == "TEXT_ANCHOR" and method_id not in active_text_method_ids:
            add_issue(
                issues,
                "error",
                "AUXILIARY-TEXT-METHOD",
                f"{path}.method_id",
                "text-anchor auxiliary evidence requires an active text-review method",
            )
        if status == "SIGNAL_MEASURED_NOT_AUDITIONED":
            method = method_by_id.get(method_id) if isinstance(method_id, str) else None
            if not isinstance(method, dict) or method.get("method_type") != "DECODED_SIGNAL_MEASUREMENT":
                add_issue(
                    issues,
                    "error",
                    "AUXILIARY-SIGNAL-METHOD",
                    f"{path}.method_id",
                    "decoded-signal evidence requires a DECODED_SIGNAL_MEASUREMENT method",
                )
            elif method_id not in active_signal_method_ids:
                add_issue(
                    issues,
                    "error",
                    "AUXILIARY-SIGNAL-METHOD-STATUS",
                    f"{path}.method_id",
                    "decoded-signal evidence can support validation only through an active reproducible or recorded method",
                )

    tracks = evidence.get("continuity_tracks") if isinstance(evidence.get("continuity_tracks"), list) else []
    track_ids: set[str] = set()
    track_by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(tracks):
        if not isinstance(item, dict):
            continue
        path = f"$.continuity_tracks[{index}]"
        track_id = item.get("track_id")
        if isinstance(track_id, str):
            if track_id in track_ids:
                add_issue(issues, "error", "TRACK-ID-DUPLICATE", f"{path}.track_id", "continuity track ID must be unique")
            track_ids.add(track_id)
            track_by_id[track_id] = item
        refs = item.get("source_refs")
        if item.get("status") in {"WITHIN_SHOT_OBSERVED", "CROSS_CUT_INFERRED"} and (not isinstance(refs, list) or not refs):
            add_issue(issues, "error", "TRACK-SOURCE-REQUIRED", f"{path}.source_refs", "observed or inferred continuity track needs source shots")
        if item.get("status") == "CROSS_CUT_INFERRED" and isinstance(refs, list) and len(set(refs)) < 2:
            add_issue(issues, "error", "TRACK-CROSS-CUT-SOURCE-COUNT", f"{path}.source_refs", "cross-cut track requires at least two cited appearances")
        if item.get("status") == "WITHIN_SHOT_OBSERVED" and isinstance(refs, list) and len(set(refs)) != 1:
            add_issue(
                issues,
                "error",
                "TRACK-WITHIN-SHOT-SOURCE-COUNT",
                f"{path}.source_refs",
                "within-shot continuity requires exactly one cited shot",
            )

    for appearance_id, occurrences in role_occurrences.items():
        inferred_track_ids: set[str] = set()
        for path, role in occurrences:
            identity_status = role.get("appearance_identity_status")
            track_id = role.get("appearance_track_id")
            if identity_status == "PICTURE_OBSERVED_WITHIN_SHOT" and track_id is not None:
                add_issue(
                    issues,
                    "error",
                    "ROLE-WITHIN-SHOT-HAS-TRACK",
                    f"{path}.appearance_track_id",
                    "within-shot appearance observation must not assert a cross-shot track",
                )
            elif identity_status == "INFERRED_ACROSS_CUTS":
                if not isinstance(track_id, str) or track_id not in track_by_id:
                    add_issue(
                        issues,
                        "error",
                        "ROLE-TRACK-REF-MISSING",
                        f"{path}.appearance_track_id",
                        "cross-cut appearance inference requires an existing continuity track",
                    )
                elif track_by_id[track_id].get("status") != "CROSS_CUT_INFERRED":
                    add_issue(
                        issues,
                        "error",
                        "ROLE-TRACK-STATUS",
                        f"{path}.appearance_track_id",
                        "cross-cut appearance inference requires a CROSS_CUT_INFERRED track",
                    )
                else:
                    inferred_track_ids.add(track_id)
            elif identity_status == "UNKNOWN" and isinstance(track_id, str):
                if track_id not in track_by_id or track_by_id[track_id].get("status") != "UNKNOWN":
                    add_issue(
                        issues,
                        "error",
                        "ROLE-UNKNOWN-TRACK-STATUS",
                        f"{path}.appearance_track_id",
                        "unknown appearance identity may cite only an UNKNOWN continuity track",
                    )
        if len(occurrences) > 1:
            if any(role.get("appearance_identity_status") != "INFERRED_ACROSS_CUTS" for _, role in occurrences):
                add_issue(
                    issues,
                    "error",
                    "ROLE-CROSS-CUT-IDENTITY",
                    occurrences[0][0],
                    f"repeated appearance alias {appearance_id!r} must be explicitly grouped as inferred across cuts",
                )
            if len(inferred_track_ids) != 1:
                add_issue(
                    issues,
                    "error",
                    "ROLE-CROSS-CUT-TRACK-MISMATCH",
                    occurrences[0][0],
                    f"repeated appearance alias {appearance_id!r} must use one shared inferred continuity track",
                )

    known_refs = set(shot_ids) | set(anchor_ids) | set(auxiliary_ids) | set(method_ids) | set(track_ids) | set(claims)
    for index, method in enumerate(methods):
        if not isinstance(method, dict):
            continue
        method_id = method.get("method_id")
        refs = method.get("source_refs") if isinstance(method.get("source_refs"), list) else []
        for ref in refs:
            if ref not in known_refs:
                add_issue(
                    issues,
                    "error",
                    "METHOD-SOURCE-REF-MISSING",
                    f"$.methods[{index}].source_refs",
                    f"unknown source reference: {ref}",
                )
            if ref == method_id:
                add_issue(
                    issues,
                    "error",
                    "METHOD-SELF-REFERENCE",
                    f"$.methods[{index}].source_refs",
                    "method record cannot cite itself as evidence",
                )
    safe_scene_problem_refs = scene_problem_refs if isinstance(scene_problem_refs, list) else []
    for ref in safe_scene_problem_refs:
        if ref not in known_refs:
            add_issue(issues, "error", "SCENE-PROBLEM-REF-MISSING", "$.scene_problem.source_refs", f"unknown source reference: {ref}")

    def terminal_tracks(ref: str, visiting: frozenset[str] = frozenset()) -> set[str]:
        """Resolve a reference to real evidence tracks, never to a method record alone."""
        if ref in visiting:
            return set()
        if ref in shot_ids:
            shot = shot_by_id.get(ref)
            if (
                picture_status != "PICTURE_UNVERIFIED"
                and isinstance(shot, dict)
                and shot.get("picture_status") != "PICTURE_UNVERIFIED"
            ):
                return {"PICTURE"}
            return set()
        if ref in anchor_ids:
            anchor = next((item for item in text_anchors if isinstance(item, dict) and item.get("anchor_id") == ref), None)
            return {
                "TEXT"
            } if (
                isinstance(anchor, dict)
                and anchor.get("status") != "TEXT_ANCHOR_UNKNOWN"
                and active_text_method_ids
            ) else set()
        if ref in auxiliary_by_id:
            item = auxiliary_by_id[ref]
            status = item.get("status")
            method_id = item.get("method_id")
            if status == "PICTURE_OBSERVED" and method_id in active_picture_method_ids:
                return {"PICTURE"}
            if status == "AUDIO_OBSERVED" and method_id in active_audio_method_ids:
                return {"AUDIO"}
            if status == "TEXT_ANCHOR" and method_id in active_text_method_ids:
                return {"TEXT"}
            if status == "SIGNAL_MEASURED_NOT_AUDITIONED" and method_id in active_signal_method_ids:
                return {"SIGNAL"}
            return set()
        if ref in track_by_id:
            item = track_by_id[ref]
            if item.get("status") == "UNKNOWN":
                return set()
            return {
                track
                for source_ref in item.get("source_refs", []) if isinstance(item.get("source_refs"), list)
                for track in terminal_tracks(source_ref, visiting | {ref})
            }
        if ref in claims:
            claim = claims[ref][1]
            if claim.get("status") == "UNKNOWN":
                return set()
            refs = claim.get("source_refs") if isinstance(claim.get("source_refs"), list) else []
            resolved = {
                track
                for source_ref in refs
                for track in terminal_tracks(source_ref, visiting | {ref})
            }
            required_track = {
                "PICTURE_OBSERVED": "PICTURE",
                "AUDIO_OBSERVED": "AUDIO",
                "TEXT_ANCHOR": "TEXT",
            }.get(claim.get("status"))
            if required_track is not None:
                return {required_track} if required_track in resolved else set()
            return resolved
        return set()

    for claim_path, claim in _walk_claims(evidence):
        status = claim.get("status")
        refs = claim.get("source_refs") if isinstance(claim.get("source_refs"), list) else []
        if status != "UNKNOWN":
            missing = [ref for ref in refs if ref not in known_refs]
            if missing:
                add_issue(issues, "error", "CLAIM-SOURCE-REF-MISSING", f"{claim_path}.source_refs", f"unknown source reference(s): {', '.join(missing)}")
        if status == "INFERRED":
            claim_id = claim.get("claim_id")
            if isinstance(claim_id, str) and claim_id in refs:
                add_issue(
                    issues,
                    "error",
                    "CLAIM-SELF-REFERENCE",
                    f"{claim_path}.source_refs",
                    "a claim cannot cite itself as evidence",
                )
            unknown_sources = [ref for ref in refs if ref in claims and claims[ref][1].get("status") == "UNKNOWN"]
            if unknown_sources:
                add_issue(issues, "error", "INFERRED-FROM-UNKNOWN", f"{claim_path}.source_refs", f"inference cannot cite unknown claim(s): {', '.join(unknown_sources)}")
            resolved_tracks = {
                track
                for ref in refs
                for track in terminal_tracks(ref, frozenset({claim_id}) if isinstance(claim_id, str) else frozenset())
            }
            if not resolved_tracks.intersection({"PICTURE", "AUDIO", "TEXT"}):
                add_issue(
                    issues,
                    "error",
                    "INFERRED-NO-OBSERVED-SOURCE",
                    f"{claim_path}.source_refs",
                    "inference must resolve to picture, directly auditioned audio, or text-anchor evidence",
                )
            if "SIGNAL" in resolved_tracks and isinstance(claim.get("value"), str) and SIGNAL_SEMANTIC_LEAK_RE.search(claim["value"]):
                add_issue(
                    issues,
                    "error",
                    "SIGNAL-CANNOT-PROVE-SEMANTICS",
                    f"{claim_path}.value",
                    "decoded-signal measurements cannot prove hearing, subjective, emotional, dialogue, source, or audience semantics",
                )
        if status == "PICTURE_OBSERVED":
            valid_picture_sources = set(shot_ids)
            valid_picture_sources.update(
                auxiliary_id
                for auxiliary_id, item in auxiliary_by_id.items()
                if item.get("status") == "PICTURE_OBSERVED" and item.get("method_id") in active_picture_method_ids
            )
            if refs and not any("PICTURE" in terminal_tracks(ref) for ref in refs):
                add_issue(issues, "error", "PICTURE-SOURCE-TRACK", f"{claim_path}.source_refs", "picture-observed claim needs a picture source")
        if status == "AUDIO_OBSERVED":
            valid_audio_sources = {
                auxiliary_id
                for auxiliary_id, item in auxiliary_by_id.items()
                if item.get("status") == "AUDIO_OBSERVED" and item.get("method_id") in active_audio_method_ids
            }
            if refs and not any("AUDIO" in terminal_tracks(ref) for ref in refs):
                add_issue(issues, "error", "AUDIO-SOURCE-TRACK", f"{claim_path}.source_refs", "audio-observed claim needs a directly audited audio source")

    if scene_problem_status == "INFERRED" and not {
        track for ref in safe_scene_problem_refs for track in terminal_tracks(ref)
    }:
        add_issue(
            issues,
            "error",
            "SCENE-PROBLEM-NO-OBSERVED-SOURCE",
            "$.scene_problem.source_refs",
            "inferred scene problem must resolve to observed evidence",
        )
    for occurrences in role_occurrences.values():
        for path, role in occurrences:
            if role.get("status") == "INFERRED":
                refs = role.get("source_refs") if isinstance(role.get("source_refs"), list) else []
                if not {track for ref in refs for track in terminal_tracks(ref)}:
                    add_issue(
                        issues,
                        "error",
                        "ROLE-NO-OBSERVED-SOURCE",
                        f"{path}.source_refs",
                        "inferred functional role must resolve to observed evidence",
                    )

    for index, item in enumerate(auxiliary):
        if not isinstance(item, dict):
            continue
        for ref in item.get("source_refs", []) if isinstance(item.get("source_refs"), list) else []:
            if ref not in known_refs:
                add_issue(issues, "error", "AUXILIARY-SOURCE-REF-MISSING", f"$.auxiliary_evidence[{index}].source_refs", f"unknown source reference: {ref}")
    for index, item in enumerate(tracks):
        if not isinstance(item, dict):
            continue
        for ref in item.get("source_refs", []) if isinstance(item.get("source_refs"), list) else []:
            if ref not in shot_ids:
                add_issue(issues, "error", "TRACK-SHOT-REF-MISSING", f"$.continuity_tracks[{index}].source_refs", f"unknown shot ID: {ref}")

    if evidence.get("scene_unit_type") == "SINGLE_VISIBLE_TAKE" and len(shots) != 1:
        add_issue(issues, "error", "SINGLE-VISIBLE-TAKE-SHOT-COUNT", "$.shots", "single visible take must contain exactly one visible-shot unit")
    if evidence.get("production_take_status") == "PRODUCTION_TAKE_VERIFIED":
        production_methods = [
            item for item in methods
            if isinstance(item, dict)
            and item.get("method_type") == "PRODUCTION_METHOD_VERIFICATION"
            and item.get("status") in {"REPOSITORY_REPRODUCIBLE", "MANUAL_REVIEW_RECORDED"}
        ]
        if not production_methods:
            add_issue(
                issues,
                "error",
                "PRODUCTION-TAKE-NO-METHOD",
                "$.production_take_status",
                "production-take verification requires a recorded production-method verification source",
            )

    unknown_fact_sources: list[tuple[str, str]] = []
    for claim_path, claim in claims.values():
        value = claim.get("value")
        if (
            claim.get("status") == "UNKNOWN"
            and isinstance(value, str)
            and not claim_path.startswith("$.audio_audit.")
            and ".audio_logic" not in claim_path
        ):
            unknown_fact_sources.append((claim_path, value))
    for unknown_index, item in enumerate(
        evidence.get("unknowns", []) if isinstance(evidence.get("unknowns"), list) else []
    ):
        statement = item.get("statement") if isinstance(item, dict) else None
        if isinstance(statement, str):
            unknown_fact_sources.append((f"$.unknowns[{unknown_index}].statement", statement))

    rules = evidence.get("candidate_rules") if isinstance(evidence.get("candidate_rules"), list) else []
    rule_ids: set[str] = set()
    rule_by_id: dict[str, dict[str, Any]] = {}
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            continue
        path = f"$.candidate_rules[{index}]"
        rule_id = rule.get("candidate_rule_id")
        if isinstance(rule_id, str):
            if rule_id in rule_ids:
                add_issue(issues, "error", "RULE-ID-DUPLICATE", f"{path}.candidate_rule_id", "candidate rule ID must be unique")
            rule_ids.add(rule_id)
            rule_by_id[rule_id] = rule

        for shot_id in rule.get("evidence_shot_ids", []) if isinstance(rule.get("evidence_shot_ids"), list) else []:
            if shot_id not in shot_ids:
                add_issue(issues, "error", "RULE-SHOT-REF-MISSING", f"{path}.evidence_shot_ids", f"unknown shot ID: {shot_id}")
        for auxiliary_id in rule.get("evidence_auxiliary_ids", []) if isinstance(rule.get("evidence_auxiliary_ids"), list) else []:
            if auxiliary_id not in auxiliary_ids:
                add_issue(issues, "error", "RULE-AUXILIARY-REF-MISSING", f"{path}.evidence_auxiliary_ids", f"unknown auxiliary evidence ID: {auxiliary_id}")
        rule_auxiliary_ids = rule.get("evidence_auxiliary_ids") if isinstance(rule.get("evidence_auxiliary_ids"), list) else []
        scene_ids = rule.get("evidence_scene_ids") if isinstance(rule.get("evidence_scene_ids"), list) else []
        if evidence_id not in scene_ids:
            add_issue(issues, "error", "RULE-SCENE-REF-MISSING", f"{path}.evidence_scene_ids", "rule must cite its owning scene evidence ID")
        if set(scene_ids) != {evidence_id}:
            add_issue(
                issues,
                "error",
                "RULE-EXTERNAL-SCENE-REF",
                f"{path}.evidence_scene_ids",
                "embedded source-scene rules may cite only their owning scene; cross-work lineage belongs in the future candidate index",
            )
        for method_id in rule.get("source_method_ids", []) if isinstance(rule.get("source_method_ids"), list) else []:
            if method_id not in method_ids:
                add_issue(issues, "error", "RULE-METHOD-REF-MISSING", f"{path}.source_method_ids", f"unknown method ID: {method_id}")
            elif method_by_id[method_id].get("status") not in ACTIVE_METHOD_STATUSES:
                add_issue(
                    issues,
                    "error",
                    "RULE-METHOD-INACTIVE",
                    f"{path}.source_method_ids",
                    f"rule cannot rely on inactive method: {method_id}",
                )

        required_story_facts = rule.get("required_story_facts") if isinstance(rule.get("required_story_facts"), list) else []
        has_legacy_migration = isinstance(rule.get("legacy_migration"), dict)
        if has_legacy_migration and required_story_facts:
            add_issue(
                issues,
                "error",
                "LEGACY-RULE-OPERATIONAL-FACT",
                f"{path}.required_story_facts",
                "a non-operational legacy lineage row cannot assert an operational story prerequisite",
            )
        elif not has_legacy_migration and not required_story_facts:
            add_issue(
                issues,
                "error",
                "RULE-STORY-FACT-REQUIRED",
                f"{path}.required_story_facts",
                "an operational candidate rule requires at least one supported story fact",
            )

        for fact_index, fact_ref in enumerate(required_story_facts):
            claim_id = fact_ref.get("claim_id") if isinstance(fact_ref, dict) else None
            if claim_id not in claims:
                add_issue(issues, "error", "RULE-FACT-REF-MISSING", f"{path}.required_story_facts[{fact_index}]", f"unknown claim ID: {claim_id}")
            elif claims[claim_id][1].get("status") == "UNKNOWN":
                add_issue(issues, "error", "RULE-REQUIRES-UNKNOWN", f"{path}.required_story_facts[{fact_index}]", "UNKNOWN cannot be promoted into a required story fact")

        audio_logic = rule.get("audio_logic") if isinstance(rule.get("audio_logic"), dict) else {}
        if audio_status != "AUDIO_OBSERVED" and audio_logic.get("status") != "UNKNOWN":
            add_issue(issues, "error", "RULE-AUDIO-WITHOUT-EVIDENCE", f"{path}.audio_logic", "audio rule must remain UNKNOWN without directly observed audio")
        if audio_status != "AUDIO_OBSERVED":
            audio_value = audio_logic.get("value")
            if isinstance(audio_value, str) and (
                AUDIO_DIRECTIVE_RE.search(audio_value)
                or AUDIO_UNCERTAINTY_RE.search(audio_value) is None
                or _has_unauditioned_audio_assertion(audio_value)
            ):
                add_issue(
                    issues,
                    "error",
                    "RULE-AUDIO-UNKNOWN-HIDES-DIRECTIVE",
                    f"{path}.audio_logic.value",
                    "unknown audio logic must state uncertainty and must not prescribe sound",
                )

        promotion = rule.get("promotion_status")
        counterexample_status = rule.get("counterexample_status")
        counterexample_ids = rule.get("counterexample_ids") if isinstance(rule.get("counterexample_ids"), list) else []
        signal_dependent = any(
            auxiliary_id in auxiliary_by_id
            and auxiliary_by_id[auxiliary_id].get("status") == "SIGNAL_MEASURED_NOT_AUDITIONED"
            for auxiliary_id in rule_auxiliary_ids
        )
        scene_problem_values = {
            scene_problem.get("primary"),
            *(scene_problem.get("secondary") if isinstance(scene_problem.get("secondary"), list) else []),
        }
        sound_led_without_audition = (
            rule.get("scene_problem") == "SOUND_LED_CAUSALITY"
            or "SOUND_LED_CAUSALITY" in scene_problem_values
        ) and audio_status != "AUDIO_OBSERVED"
        if (signal_dependent or sound_led_without_audition) and promotion != "BLOCKED_BY_UNKNOWN":
            add_issue(
                issues,
                "error",
                "RULE-SIGNAL-OR-SOUND-UNKNOWN-NOT-BLOCKED",
                f"{path}.promotion_status",
                "signal-dependent or unauditioned sound-led rules must remain BLOCKED_BY_UNKNOWN",
            )
        if counterexample_status in VERIFIED_COUNTEREXAMPLES:
            add_issue(
                issues,
                "error",
                "RULE-EMBEDDED-COUNTEREXAMPLE",
                f"{path}.counterexample_status",
                "verified cross-scene counterexamples must resolve in the future candidate index, not a standalone source-scene file",
            )
        if promotion in PROMOTED_STATUSES:
            add_issue(
                issues,
                "error",
                "RULE-EMBEDDED-PROMOTION",
                f"{path}.promotion_status",
                "a source-scene file cannot prove cross-work or general promotion; use the future cross-work candidate index",
            )
        if promotion == "CROSS_WORK_SUPPORTED":
            if len(set(scene_ids)) < 2:
                add_issue(issues, "error", "RULE-CROSS-WORK-SOURCE-COUNT", f"{path}.promotion_status", "cross-work support requires at least two evidence scenes")
            if counterexample_status not in VERIFIED_COUNTEREXAMPLES or not counterexample_ids:
                add_issue(issues, "error", "RULE-CROSS-WORK-COUNTEREXAMPLE", f"{path}.counterexample_status", "cross-work support requires verified same-trigger contrary evidence")
        if promotion == "GENERAL_DEFAULT":
            if len(set(scene_ids)) < 3:
                add_issue(issues, "error", "RULE-GENERAL-SOURCE-COUNT", f"{path}.promotion_status", "general default requires at least three evidence scenes")
            if counterexample_status not in VERIFIED_COUNTEREXAMPLES or not counterexample_ids:
                add_issue(issues, "error", "RULE-GENERAL-COUNTEREXAMPLE", f"{path}.counterexample_status", "general default requires a verified same-trigger counterexample")
        if promotion in PROMOTED_STATUSES and audio_status != "AUDIO_OBSERVED" and audio_logic.get("status") != "UNKNOWN":
            add_issue(issues, "error", "RULE-PROMOTION-AUDIO-UNKNOWN", f"{path}.promotion_status", "rule depending on unknown audio cannot be promoted")

        _validate_risk_fallback(rule, path, issues)

        operational_text = _operational_rule_text(rule)
        if promotion != "BLOCKED_BY_UNKNOWN":
            matched_unknown_path = next(
                (
                    unknown_path
                    for unknown_path, unknown_text in unknown_fact_sources
                    if _rule_asserts_unknown_fact(unknown_text, operational_text)
                ),
                None,
            )
            if matched_unknown_path is not None:
                add_issue(
                    issues,
                    "error",
                    "RULE-ASSERTS-UNKNOWN-FACT",
                    f"{path}.promotion_status",
                    f"operational rule text closely restates active UNKNOWN at {matched_unknown_path}; keep the rule blocked or remove the assertion",
                )
        if audio_status != "AUDIO_OBSERVED" and (
            AUDIO_DIRECTIVE_RE.search(operational_text) or _has_unauditioned_audio_assertion(operational_text)
        ):
            add_issue(
                issues,
                "error",
                "RULE-AUDIO-DIRECTIVE-WITHOUT-EVIDENCE",
                path,
                "operational rule fields cannot prescribe sound before direct audition",
            )
        rights_boundary = evidence.get("rights_boundary") if isinstance(evidence.get("rights_boundary"), dict) else {}
        surface_terms = rights_boundary.get("reference_surface_terms")
        surface_terms = surface_terms if isinstance(surface_terms, list) else []
        for term in surface_terms:
            if isinstance(term, str) and term.strip() and _term_occurs(operational_text, term):
                add_issue(
                    issues,
                    "error",
                    "RULE-SURFACE-COPY",
                    path,
                    f"reference surface term appears in operational rule text: {term!r}",
                )

    rights_boundary = evidence.get("rights_boundary") if isinstance(evidence.get("rights_boundary"), dict) else {}
    if rights_boundary.get("surface_inventory_status") != "HUMAN_REVIEWED_COMPLETE":
        add_issue(
            issues,
            "error",
            "SURFACE-INVENTORY-PENDING",
            "$.rights_boundary.surface_inventory_status",
            "surface-copy validation requires a human-reviewed reference-term inventory",
        )

    for index, item in enumerate(evidence.get("unknowns", []) if isinstance(evidence.get("unknowns"), list) else []):
        if not isinstance(item, dict):
            continue
        statement = item.get("statement")
        if isinstance(statement, str) and GENERAL_UNCERTAINTY_RE.search(statement) is None:
            add_issue(
                issues,
                "error",
                "UNKNOWN-STATEMENT-ASSERTS-FACT",
                f"$.unknowns[{index}].statement",
                "unknown register wording must explicitly state uncertainty",
            )
        for blocked_rule_id in item.get("blocks_rule_ids", []) if isinstance(item.get("blocks_rule_ids"), list) else []:
            if blocked_rule_id not in rule_ids:
                add_issue(issues, "error", "UNKNOWN-RULE-REF-MISSING", f"$.unknowns[{index}].blocks_rule_ids", f"unknown rule ID: {blocked_rule_id}")
                continue
            blocked_rule = rule_by_id[blocked_rule_id]
            if blocked_rule.get("promotion_status") != "BLOCKED_BY_UNKNOWN":
                add_issue(
                    issues,
                    "error",
                    "UNKNOWN-RULE-NOT-BLOCKED",
                    f"$.unknowns[{index}].blocks_rule_ids",
                    f"rule {blocked_rule_id} must remain BLOCKED_BY_UNKNOWN while this unknown is active",
                )

    _validate_public_boundary(evidence, issues)


def validate_evidence(evidence: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    validate_schema_subset(evidence, schema, schema, issues)
    if not any(issue["level"] == "error" and issue["code"].startswith("SCHEMA-") for issue in issues):
        validate_semantics(evidence, issues)
    for index, warning in enumerate(
        evidence.get("validation_warnings", []) if isinstance(evidence.get("validation_warnings"), list) else []
    ):
        if isinstance(warning, str):
            add_issue(
                issues,
                "warning",
                "EVIDENCE-DECLARED-WARNING",
                f"$.validation_warnings[{index}]",
                warning,
            )
    errors = [issue for issue in issues if issue["level"] == "error"]
    warnings = [issue for issue in issues if issue["level"] == "warning"]
    failed_rule_ids: set[str] = set()
    rules = evidence.get("candidate_rules") if isinstance(evidence.get("candidate_rules"), list) else []
    for issue in errors:
        match = re.match(r"^\$\.candidate_rules\[([0-9]+)\]", issue["path"])
        if match is None:
            continue
        index = int(match.group(1))
        if index < len(rules) and isinstance(rules[index], dict) and isinstance(rules[index].get("candidate_rule_id"), str):
            failed_rule_ids.add(rules[index]["candidate_rule_id"])
    return {
        "evidence_id": evidence.get("evidence_id", "UNKNOWN"),
        "passed": not errors,
        "shot_count": len(evidence.get("shots", [])) if isinstance(evidence.get("shots"), list) else 0,
        "candidate_rule_count": len(evidence.get("candidate_rules", [])) if isinstance(evidence.get("candidate_rules"), list) else 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "failed_rule_ids": sorted(failed_rule_ids),
        "issues": issues,
    }


def discover_evidence_paths(inputs: Sequence[str]) -> list[Path]:
    paths: set[Path] = set()
    for raw in inputs:
        path = Path(raw)
        if path.is_file():
            paths.add(path.resolve())
        elif path.is_dir():
            for pattern in ("scene-evidence.json", "*.scene-evidence.json"):
                paths.update(item.resolve() for item in path.rglob(pattern))
        else:
            raise FileNotFoundError(raw)
    return sorted(paths)


def validate_paths(paths: Iterable[Path], schema: dict[str, Any]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    load_errors: list[dict[str, str]] = []
    for path in paths:
        report_path = _display_path(path)
        try:
            evidence = load_json(path)
            if not isinstance(evidence, dict):
                raise ValueError("top-level JSON value must be an object")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            load_errors.append({"path": report_path, "message": str(exc)})
            continue
        result = validate_evidence(evidence, schema)
        result["path"] = report_path
        results.append(result)

    failed = sum(1 for result in results if not result["passed"]) + len(load_errors)
    warning_rows = [
        {"evidence_id": result["evidence_id"], **issue}
        for result in results
        for issue in result["issues"]
        if issue["level"] == "warning"
    ]
    failed_scene_ids = [result["evidence_id"] for result in results if not result["passed"]]
    failed_scene_ids.extend(f"LOAD::{item['path']}" for item in load_errors)
    failed_rule_ids = sorted({rule_id for result in results for rule_id in result["failed_rule_ids"]})
    return {
        "validator_version": VALIDATOR_VERSION,
        "status": "PASS_STRUCTURAL" if failed == 0 else "FAIL",
        "structural_validation_is_not_creative_approval": True,
        "total_scenes": len(results) + len(load_errors),
        "passed": sum(1 for result in results if result["passed"]),
        "failed": failed,
        "warnings": warning_rows,
        "total_shots": sum(result["shot_count"] for result in results),
        "total_candidate_rule_count": sum(result["candidate_rule_count"] for result in results),
        "error_count": sum(result["error_count"] for result in results) + len(load_errors),
        "warning_count": len(warning_rows),
        "failed_scene_ids": failed_scene_ids,
        "failed_rule_ids": failed_rule_ids,
        "load_errors": load_errors,
        "results": results,
    }


def build_parser() -> argparse.ArgumentParser:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="Scene Evidence JSON file(s) or directories")
    parser.add_argument(
        "--schema",
        default=str(script_dir.parent / "references" / "scene-evidence.schema.json"),
        help="Scene Evidence JSON Schema path",
    )
    parser.add_argument("--report", help="Optional JSON report output path")
    parser.add_argument("--quiet", action="store_true", help="Suppress stdout report")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        schema = load_json(Path(args.schema))
        paths = discover_evidence_paths(args.inputs)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"validator setup error: {exc}", file=sys.stderr)
        return 2
    if not paths:
        print("validator setup error: no Scene Evidence JSON files found", file=sys.stderr)
        return 2
    report = validate_paths(paths, schema)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.report:
        Path(args.report).write_text(rendered, encoding="utf-8")
    if not args.quiet:
        print(rendered, end="")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
