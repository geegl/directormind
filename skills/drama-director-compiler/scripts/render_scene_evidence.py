#!/usr/bin/env python3
"""Render canonical Scene Evidence JSON into deterministic review Markdown.

The canonical JSON is the only input. Legacy evidence Markdown is migration
provenance and is never opened for writing. Generated output always uses the
.scene-evidence.generated.md suffix or a caller-supplied output root.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
EVIDENCE_ROOT = REPOSITORY_ROOT / "research" / "evidence"
GENERATED_SUFFIX = ".scene-evidence.generated.md"
SNAPSHOT_START = "<!-- DIRECTORMIND_RENDER_SNAPSHOT_BEGIN -->"
SNAPSHOT_END = "<!-- DIRECTORMIND_RENDER_SNAPSHOT_END -->"


def discover_sources(paths: Iterable[Path] | None = None) -> list[Path]:
    """Return canonical Scene Evidence JSON sources in stable path order."""
    if paths:
        sources = [path.resolve() for path in paths]
    else:
        sources = [path.resolve() for path in EVIDENCE_ROOT.rglob("*.scene-evidence.json")]
    return sorted(sources, key=lambda item: item.as_posix())


def generated_path(source: Path, output_root: Path | None = None) -> Path:
    """Return a path that can never collide with a legacy Markdown source."""
    source = source.resolve()
    name = source.name.removesuffix(".scene-evidence.json") + GENERATED_SUFFIX
    if output_root is None:
        return source.with_name(name)
    output_root = output_root.resolve()
    try:
        relative_parent = source.parent.relative_to(EVIDENCE_ROOT.resolve())
    except ValueError:
        relative_parent = Path()
    return output_root / relative_parent / name


def _compact(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        if not value:
            return "—"
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    return text or "—"


def _cell(value: Any) -> str:
    return _compact(value).replace("\\", "\\\\").replace("|", "\\|")


def _risk_levels(shot: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for axis in ("camera", "performance", "continuity"):
        value = shot.get("AI_complexity", {}).get(axis)
        result[axis] = value.get("level", "UNKNOWN") if isinstance(value, dict) else "UNKNOWN"
    return result


def build_render_snapshot(evidence: dict[str, Any]) -> dict[str, Any]:
    """Select every canonical field displayed by the generated review document."""
    shots = []
    for shot in evidence.get("shots", []):
        shots.append(
            {
                "order": shot.get("order"),
                "shot_id": shot.get("shot_id"),
                "start": shot.get("start"),
                "end": shot.get("end"),
                "duration": shot.get("duration"),
                "shot_size": shot.get("shot_size"),
                "camera_angle": shot.get("camera_angle"),
                "camera_path": shot.get("camera_path"),
                "spatial_zone": shot.get("spatial_zone"),
                "picture_status": shot.get("picture_status"),
                "audio_status": shot.get("audio_status"),
                "narrative_function": shot.get("narrative_function"),
                "risk_levels": _risk_levels(shot),
                "unknowns": shot.get("unknowns", []),
            }
        )

    rules = []
    for rule in evidence.get("candidate_rules", []):
        rules.append(
            {
                "candidate_rule_id": rule.get("candidate_rule_id"),
                "canonical_rule_family": rule.get("canonical_rule_family"),
                "promotion_status": rule.get("promotion_status"),
                "scene_problem": rule.get("scene_problem"),
                "within_source_confidence": rule.get("within_source_confidence"),
                "transfer_confidence": rule.get("transfer_confidence"),
                "execution_confidence": rule.get("execution_confidence"),
                "evidence_status": rule.get("evidence_status"),
                "evidence_scene_ids": rule.get("evidence_scene_ids", []),
                "evidence_shot_ids": rule.get("evidence_shot_ids", []),
                "required_story_facts": rule.get("required_story_facts", []),
                "counterexample_status": rule.get("counterexample_status"),
                "counterexample_ids": rule.get("counterexample_ids", []),
            }
        )

    return {
        "schema_version": evidence.get("schema_version"),
        "evidence_id": evidence.get("evidence_id"),
        "work_id": evidence.get("work_id"),
        "scene_unit_type": evidence.get("scene_unit_type"),
        "boundary_status": evidence.get("boundary_status"),
        "source_start": evidence.get("source_start"),
        "source_end": evidence.get("source_end"),
        "duration": evidence.get("duration"),
        "picture_evidence_status": evidence.get("picture_evidence_status"),
        "audio_evidence_status": evidence.get("audio_evidence_status"),
        "text_anchor_status": evidence.get("text_anchor_status"),
        "production_take_status": evidence.get("production_take_status"),
        "source_identity_status": evidence.get("source_identity_status"),
        "validation_status": evidence.get("validation_status"),
        "scene_problem": evidence.get("scene_problem"),
        "stats": evidence.get("stats"),
        "shots": shots,
        "candidate_rules": rules,
        "unknowns": evidence.get("unknowns", []),
        "boundary_evidence": evidence.get("boundary_evidence"),
        "validation_warnings": evidence.get("validation_warnings", []),
    }


def render_snapshot(snapshot: dict[str, Any]) -> str:
    """Render a normalized snapshot to stable Markdown."""
    lines = [
        f"# Scene Evidence Review — {_compact(snapshot.get('evidence_id'))}",
        "",
        "> GENERATED FILE. Canonical facts come from the source Scene Evidence JSON.",
        "> Do not edit this file by hand. Legacy evidence Markdown remains immutable migration provenance.",
        "",
        "## Summary",
        "",
        "| Field | Value |",
        "|---|---|",
    ]
    for key in (
        "schema_version",
        "evidence_id",
        "work_id",
        "scene_unit_type",
        "boundary_status",
        "source_start",
        "source_end",
        "duration",
        "picture_evidence_status",
        "audio_evidence_status",
        "text_anchor_status",
        "production_take_status",
        "source_identity_status",
        "validation_status",
    ):
        lines.append(f"| {_cell(key)} | {_cell(snapshot.get(key))} |")

    lines.extend(
        [
            "",
            "## Scene problem",
            "",
            "```json",
            json.dumps(snapshot.get("scene_problem"), ensure_ascii=False, sort_keys=True, indent=2),
            "```",
            "",
            "## Statistics",
            "",
            "```json",
            json.dumps(snapshot.get("stats"), ensure_ascii=False, sort_keys=True, indent=2),
            "```",
            "",
            "## Shots",
            "",
            "| # | Shot ID | Start | End | Duration | Size | Angle | Camera path | Zone | Picture | Audio | Narrative function | AI risk C/P/K | UNKNOWN |",
            "|---:|---|---:|---:|---:|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for shot in snapshot.get("shots", []):
        risk = shot.get("risk_levels", {})
        risk_text = "/".join(
            str(risk.get(axis, "UNKNOWN")) for axis in ("camera", "performance", "continuity")
        )
        lines.append(
            "| "
            + " | ".join(
                _cell(value)
                for value in (
                    shot.get("order"),
                    shot.get("shot_id"),
                    shot.get("start"),
                    shot.get("end"),
                    shot.get("duration"),
                    shot.get("shot_size"),
                    shot.get("camera_angle"),
                    shot.get("camera_path"),
                    shot.get("spatial_zone"),
                    shot.get("picture_status"),
                    shot.get("audio_status"),
                    shot.get("narrative_function"),
                    risk_text,
                    shot.get("unknowns", []),
                )
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Candidate-rule lineage",
            "",
            "| Candidate ID | Family | Status | Scene problem | Confidence W/T/E | Evidence status | Scene refs | Shot refs | Required facts | Counterexample |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for rule in snapshot.get("candidate_rules", []):
        confidence = "/".join(
            str(rule.get(key, "UNKNOWN"))
            for key in (
                "within_source_confidence",
                "transfer_confidence",
                "execution_confidence",
            )
        )
        counterexample = {
            "status": rule.get("counterexample_status"),
            "ids": rule.get("counterexample_ids", []),
        }
        lines.append(
            "| "
            + " | ".join(
                _cell(value)
                for value in (
                    rule.get("candidate_rule_id"),
                    rule.get("canonical_rule_family"),
                    rule.get("promotion_status"),
                    rule.get("scene_problem"),
                    confidence,
                    rule.get("evidence_status"),
                    rule.get("evidence_scene_ids", []),
                    rule.get("evidence_shot_ids", []),
                    rule.get("required_story_facts", []),
                    counterexample,
                )
            )
            + " |"
        )

    for title, key in (
        ("UNKNOWN register", "unknowns"),
        ("Boundary evidence", "boundary_evidence"),
        ("Validation warnings", "validation_warnings"),
    ):
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                "```json",
                json.dumps(snapshot.get(key), ensure_ascii=False, sort_keys=True, indent=2),
                "```",
            ]
        )

    lines.extend(
        [
            "",
            SNAPSHOT_START,
            "```json",
            json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2),
            "```",
            SNAPSHOT_END,
            "",
        ]
    )
    return "\n".join(lines)


def render_evidence(evidence: dict[str, Any]) -> str:
    return render_snapshot(build_render_snapshot(evidence))


def extract_render_snapshot(markdown: str) -> dict[str, Any]:
    """Recover the displayed canonical snapshot for round-trip verification."""
    start = markdown.find(SNAPSHOT_START)
    end = markdown.find(SNAPSHOT_END)
    if start < 0 or end < 0 or end <= start:
        raise ValueError("generated Markdown does not contain the render snapshot markers")
    block = markdown[start + len(SNAPSHOT_START) : end].strip()
    if not block.startswith("```json\n") or not block.endswith("\n```"):
        raise ValueError("generated Markdown snapshot block is malformed")
    return json.loads(block[len("```json\n") : -len("\n```")])


def load_evidence(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: Scene Evidence root must be an object")
    return data


def _write(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_evidence(load_evidence(source)), encoding="utf-8")


def _check(source: Path, destination: Path) -> str | None:
    if not destination.exists():
        return f"MISSING {destination}"
    expected = render_evidence(load_evidence(source))
    actual = destination.read_text(encoding="utf-8")
    if actual != expected:
        return f"DRIFT {destination}"
    try:
        snapshot = extract_render_snapshot(actual)
    except (ValueError, json.JSONDecodeError) as exc:
        return f"ROUND_TRIP {destination}: {exc}"
    if render_snapshot(snapshot) != actual:
        return f"ROUND_TRIP {destination}: extracted snapshot does not re-render identically"
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sources = discover_sources(args.sources)
    if not sources:
        print("no Scene Evidence JSON sources found", file=sys.stderr)
        return 2
    if args.stdout:
        if len(sources) != 1 or args.check or args.output_root:
            print("--stdout requires exactly one source and no --check/--output-root", file=sys.stderr)
            return 2
        sys.stdout.write(render_evidence(load_evidence(sources[0])))
        return 0

    destinations = [(source, generated_path(source, args.output_root)) for source in sources]
    if args.check:
        failures = [
            failure
            for source, destination in destinations
            if (failure := _check(source, destination)) is not None
        ]
        for failure in failures:
            print(failure, file=sys.stderr)
        if failures:
            return 1
        print(f"checked {len(destinations)} generated Scene Evidence Markdown file(s)")
        return 0

    for source, destination in destinations:
        _write(source, destination)
    print(f"rendered {len(destinations)} generated Scene Evidence Markdown file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
