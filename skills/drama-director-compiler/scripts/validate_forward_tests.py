#!/usr/bin/env python3
"""Validate project-original forward-test packages against live authorities."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]
FORWARD_ROOT = REPOSITORY_ROOT / "examples" / "forward-tests"
INDEX_PATH = FORWARD_ROOT / "index.json"
INDEX_SCHEMA_PATH = SKILL_ROOT / "references" / "forward-test-index.schema.json"
GRAMMAR_PATH = REPOSITORY_ROOT / "research" / "grammar" / "director_grammar_v0.2.json"
REPORT_PATH = REPOSITORY_ROOT / "research" / "validation" / "forward-test-validation.json"

sys.path.insert(0, str(SCRIPT_DIR))
from render_director_ir import render_coverage, render_shot_script  # noqa: E402
from route_director_rules import INPUT_SCHEMA_PATH, route_scene, schema_issues  # noqa: E402
from validate_director_grammar import (  # noqa: E402
    INDEX_PATH as CANDIDATE_INDEX_PATH,
    MATRIX_PATH,
    SCHEMA_PATH as GRAMMAR_SCHEMA_PATH,
    eligible_candidates,
    iter_strings,
    normalized_phrase,
    read_json,
    validate_grammar,
)
from validate_director_ir import validate as validate_ir  # noqa: E402
from validate_scene_evidence import validate_schema_subset  # noqa: E402


REQUIRED_FILES = {
    "manifest.json",
    "locked-script.md",
    "routing-input.json",
    "selected-rules.json",
    "director-ir.json",
    "shot-script.md",
    "source-coverage.md",
    "validation.json",
    "human-review.md",
}
REQUIRED_COVERAGE_TAGS = {
    "TWO_PARTY_POWER_TRANSFER",
    "MULTI_PARTICIPANT_PUBLIC_REVELATION",
    "PROCEDURE_SUCCESS_AND_FAILURE",
    "ONE_TO_MANY_ACTION",
    "NON_CONTACT_RELATION_TENSION",
    "SOUND_DRIVEN_SUSPENSE",
}
MUTUALLY_EXCLUSIVE_ROUTING_SIGNALS = {
    frozenset({"counterpart_relation_required", "counterpart_relation_not_required"}),
    frozenset({"continuous_present_time", "elliptical_time_change"}),
}
ROUTING_SIGNAL_FACT_TYPES = {
    "relation_already_registered": "relation_state",
    "single_performance_progression": "performance_progression",
    "simultaneous_required_action": "simultaneous_state",
    "material_spatial_change": "spatial_change",
    "counterpart_relation_required": "counterpart_relation",
    "counterpart_relation_not_required": "counterpart_absent",
    "counterpart_relation_context_locked": "counterpart_relation",
    "counterpart_absent_at_changed_endpoint": "counterpart_endpoint_state",
    "relation_distance_change": "distance_change",
    "continuous_present_time": "continuous_time_change",
    "shared_endpoint_required": "relation_endpoint",
    "elliptical_time_change": "time_ellipsis",
    "time_structure_locked": "time_structure",
    "distance_change_across_ellipsis": "time_structure",
    "visible_action_source": "action_source",
    "target_state_change": "target_state",
    "result_readable": "visible_result",
    "continuous_view_preserves_action_chain": "visible_result",
    "multiple_visible_referents": "referent_set",
    "comparative_relation_required": "relation_constraint",
    "comparative_field_not_required": "single_item_state",
    "threshold_changes_locked_state": "threshold_state_change",
    "before_after_route_required": "route_endpoint",
    "threshold_state_unchanged": "unchanged_state",
}
REQUIRED_CASE_IDS = {
    "ORIGINAL-POWER-DIALOGUE",
    "ORIGINAL-RELATIONSHIP-FRACTURE",
    "ORIGINAL-PUBLIC-REVEAL",
    "ORIGINAL-PROCEDURE",
    "ORIGINAL-ACTION-CAUSALITY",
    "ORIGINAL-PROXIMITY-TENSION",
    "ORIGINAL-SOUND-SUSPENSE",
    "ORIGINAL-PERFORMANCE-OWNER-HOLD",
    "ORIGINAL-PERFORMANCE-CONCURRENT-STATE",
    "ORIGINAL-SPATIAL-CHANGE-WITHOUT-COUNTERPART",
    "ORIGINAL-PROXIMITY-ELLIPSIS",
    "ORIGINAL-ACTION-CONTINUOUS-CHAIN",
    "ORIGINAL-REFERENT-COMPARISON",
    "ORIGINAL-COMPARISON-NOT-REQUIRED",
    "ORIGINAL-THRESHOLD-STATE-CHANGE",
    "ORIGINAL-THRESHOLD-UNCHANGED",
    "ORIGINAL-NO-APPLICABLE-RULE",
}
FORBIDDEN_STATUS_RE = re.compile(r"\b(PRODUCTION_READY|WINNER|CREATIVE_SUCCESS)\b", re.IGNORECASE)
FORBIDDEN_PATH_RE = re.compile(
    r"(?:https?://|file://|/Users/|/private/|/tmp/|/var/|/home/|~/|[A-Za-z]:\\|(?:private|secret|internal)/[A-Za-z0-9._/-]+|\.codex(?:/|\\b))",
    re.IGNORECASE,
)
FORBIDDEN_MEDIA_RE = re.compile(r"\.(?:mp4|mov|mkv|avi|webm|mp3|wav|flac|aac|jpg|jpeg|png|heic|gif|srt|ass|ssa)\b", re.IGNORECASE)


def issue(issues: list[dict[str, str]], code: str, path: str, message: str) -> None:
    issues.append({"level": "error", "code": code, "path": path, "message": message})


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def safe_package_path(value: str, issues: list[dict[str, str]], path: str) -> Path | None:
    if not isinstance(value, str) or Path(value).is_absolute() or ".." in Path(value).parts:
        issue(issues, "FORWARD-PACKAGE-PATH", path, "Package path must be a confined repository-relative path.")
        return None
    unresolved = REPOSITORY_ROOT / value
    if unresolved.is_symlink():
        issue(issues, "FORWARD-PACKAGE-PATH", path, "Package path cannot be a symbolic link.")
        return None
    resolved = unresolved.resolve()
    try:
        relative = resolved.relative_to(FORWARD_ROOT.resolve())
    except ValueError:
        issue(issues, "FORWARD-PACKAGE-PATH", path, "Package path escapes examples/forward-tests.")
        return None
    if relative == Path(".") or not resolved.is_dir():
        issue(issues, "FORWARD-PACKAGE-PATH", path, "Package path must be one real case directory.")
        return None
    return resolved


def known_surface_tokens(candidate_index: dict[str, Any]) -> tuple[set[str], set[str]]:
    ids: set[str] = set()
    work_titles: set[str] = set()
    for candidate in candidate_index.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        ids.add(str(candidate.get("candidate_rule_id", "")))
        source = candidate.get("source", {})
        for key in ("work_id", "evidence_id", "source_candidate_rule_id"):
            value = source.get(key)
            if isinstance(value, str):
                ids.add(value)
        ids.update(value for value in source.get("evidence_shot_ids", []) if isinstance(value, str))
        work_id = source.get("work_id")
        if isinstance(work_id, str):
            title = re.sub(r"-(?:19|20)\d{2}(?:-.+)?$", "", work_id)
            title = re.sub(r"-S\d{2}E\d{2}(?:-.+)?$", "", title)
            words = [word for word in title.split("-") if word]
            normalized_title = normalized_phrase(" ".join(words))
            if len(words) >= 2 or len(normalized_title) >= 5:
                work_titles.add(normalized_title)
    ids.discard("")
    work_titles.discard("")
    return ids, work_titles


def required_metadata_values(text: str, key: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    ]


def expected_human_review_text(case_id: str) -> str:
    return "\n".join([
        f"# Human review — {case_id}",
        "",
        "STATUS: HUMAN_REVIEW_PENDING",
        "DIRECTOR_APPROVAL: NOT_REVIEWED",
        "GENERATION_AUTHORIZED: false",
        "PUBLICATION_AUTHORIZED: false",
        "",
        "The automated result proves only package structure, route reproduction, source coverage, and authorization gates.",
        "A human director has not approved creative quality, execution quality, or audience effect.",
        "",
    ])


def surface_issues(
    package: Path,
    candidate_index: dict[str, Any],
    issues: list[dict[str, str]],
) -> None:
    known_ids, title_tokens = known_surface_tokens(candidate_index)
    for file_path in sorted(package.iterdir()):
        relative = file_path.resolve().relative_to(REPOSITORY_ROOT.resolve()).as_posix()
        if file_path.is_symlink() or not file_path.is_file():
            issue(issues, "FORWARD-FILE-BOUNDARY", relative, "Package entries must be regular files, not links or directories.")
            continue
        if file_path.name not in REQUIRED_FILES:
            issue(issues, "FORWARD-FILE-SET", relative, "Unexpected package file.")
            continue
        text = file_path.read_text(encoding="utf-8")
        scan_text = text
        if file_path.suffix == ".json":
            try:
                decoded = json.loads(text)
            except json.JSONDecodeError:
                decoded = None
            if decoded is not None:
                if file_path.name == "manifest.json" and isinstance(decoded, dict):
                    decoded = dict(decoded)
                    decoded["candidate_rule_id"] = None
                scan_text = json.dumps(decoded, ensure_ascii=False, sort_keys=True)
                scan_text += "\n" + "\n".join(value for _, value in iter_strings(decoded))
        if FORBIDDEN_STATUS_RE.search(scan_text):
            issue(issues, "FORWARD-APPROVAL-CLAIM", relative, "Unreviewed package contains a prohibited success label.")
        if FORBIDDEN_PATH_RE.search(scan_text):
            issue(issues, "FORWARD-PRIVATE-PATH", relative, "Package contains an external URL or private/local path.")
        if FORBIDDEN_MEDIA_RE.search(scan_text):
            issue(issues, "FORWARD-MEDIA-REF", relative, "Package contains a media/subtitle filename reference.")
        normalized = normalized_phrase(scan_text)
        for surface_id in known_ids:
            token = normalized_phrase(surface_id)
            if token and token in normalized:
                issue(issues, "FORWARD-SURFACE-ID", relative, "A research evidence identity escaped into an original package.")
                break
        for title in title_tokens:
            if title in normalized:
                issue(issues, "FORWARD-WORK-SURFACE", relative, "A reference-work title escaped into an original package.")
                break


def expected_case_validation(
    entry: dict[str, Any],
    routing_result: dict[str, Any],
    ir_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "forward-test-validation/0.1",
        "test_case_id": entry["test_case_id"],
        "structural_status": "PASS" if ir_report["status"] == "PASS" else "FAIL",
        "test_mode": entry["test_mode"],
        "positive_selection_claimed": entry["test_mode"] == "POSITIVE",
        "routing_status": routing_result["status"],
        "routing_error_count": 0,
        "ir_status": ir_report["status"],
        "ir_error_count": ir_report["errors"],
        "ir_warning_count": ir_report["warnings"],
        "selection_count": routing_result["selection_count"],
        "human_review_status": "HUMAN_REVIEW_PENDING",
        "generation_authorized": False,
        "publication_authorized": False,
        "issues": ir_report["issues"],
    }


def validate_package(
    entry: dict[str, Any],
    package: Path,
    grammar: dict[str, Any],
    candidate_index: dict[str, Any],
    zero_eligible: bool,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    issues: list[dict[str, str]] = []
    case_id = entry.get("test_case_id")
    relative_package = package.resolve().relative_to(REPOSITORY_ROOT.resolve()).as_posix()
    actual_files = {path.name for path in package.iterdir()}
    if actual_files != REQUIRED_FILES:
        issue(issues, "FORWARD-FILE-SET", relative_package, f"Expected exact file set: {sorted(REQUIRED_FILES)}.")
    surface_issues(package, candidate_index, issues)
    try:
        manifest = read_json(package / "manifest.json")
        routing_input = read_json(package / "routing-input.json")
        saved_routing = read_json(package / "selected-rules.json")
        ir = read_json(package / "director-ir.json")
        saved_validation = read_json(package / "validation.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        issue(issues, "FORWARD-JSON", relative_package, f"Package JSON cannot be read: {exc}.")
        return {"test_case_id": case_id, "status": "FAIL"}, issues

    expected_manifest = {
        "schema_version": "forward-test-result/0.1",
        "test_case_id": case_id,
        "candidate_rule_id": (
            None
            if not entry.get("positive_for_rule_ids") and not entry.get("boundary_for_rule_ids")
            else next(
                candidate.get("candidate_rule_id")
                for candidate in candidate_index.get("candidates", [])
                if candidate.get("canonical_rule_family")
                in set(entry.get("positive_for_family_ids", []) + entry.get("boundary_for_family_ids", []))
                and candidate.get("promotion", {}).get("status") == "CROSS_WORK_SUPPORTED"
            )
        ),
        "canonical_rule_family": (
            (entry.get("positive_for_family_ids") or entry.get("boundary_for_family_ids") or [None])[0]
        ),
        "rule_id": (
            (entry.get("positive_for_rule_ids") or entry.get("boundary_for_rule_ids") or [None])[0]
        ),
        "test_mode": entry.get("test_mode"),
        "status": "HUMAN_REVIEW_PENDING",
    }
    if manifest != expected_manifest:
        issue(issues, "FORWARD-MANIFEST", f"{relative_package}/manifest.json", "Forward-test manifest does not exactly bind its rule-level purpose.")
    if package.name != case_id:
        issue(issues, "FORWARD-CASE-ID", relative_package, "Directory and case IDs differ.")
    input_issues = schema_issues(routing_input, INPUT_SCHEMA_PATH)
    for item in input_issues:
        issue(issues, "FORWARD-ROUTING-INPUT", f"{relative_package}/routing-input.json:{item['path']}", item["message"])
    if routing_input.get("case_id") != case_id or routing_input.get("scene_problem", {}).get("primary") != entry.get("scene_problem"):
        issue(issues, "FORWARD-ROUTING-BINDING", f"{relative_package}/routing-input.json", "Routing input does not bind the indexed case and scene problem.")
    signal_set = set(routing_input.get("routing_signals", []))
    for signal_pair in MUTUALLY_EXCLUSIVE_ROUTING_SIGNALS:
        if signal_pair.issubset(signal_set):
            issue(
                issues,
                "FORWARD-SIGNAL-CONTRADICTION",
                f"{relative_package}/routing-input.json",
                f"Routing input asserts mutually exclusive signals: {sorted(signal_pair)}.",
            )
    fact_types = {
        fact.get("fact_type")
        for fact in routing_input.get("locked_facts", [])
        if isinstance(fact, dict)
    }
    for signal in sorted(signal_set):
        required_fact_type = ROUTING_SIGNAL_FACT_TYPES.get(signal)
        if required_fact_type is not None and required_fact_type not in fact_types:
            issue(
                issues,
                "FORWARD-SIGNAL-AUTHORITY",
                f"{relative_package}/routing-input.json",
                f"Routing signal {signal} requires locked fact type {required_fact_type}.",
            )
    if (
        routing_input.get("scene_problem", {}).get("primary") == "ROMANTIC_PROXIMITY"
        and "relationship_context" not in fact_types
    ):
        issue(
            issues,
            "FORWARD-SCENE-PROBLEM-AUTHORITY",
            f"{relative_package}/routing-input.json",
            "ROMANTIC_PROXIMITY requires an explicit project-original relationship fact in the locked script.",
        )
    locked_text = (package / "locked-script.md").read_text(encoding="utf-8")
    expected_headers = {
        "RIGHTS_STATUS": "PROJECT_ORIGINAL_SYNTHETIC",
        "PRIVATE_SOURCE_USED": "false",
        "TEST_CASE_ID": case_id,
        "HUMAN_REVIEW_STATUS": "HUMAN_REVIEW_PENDING",
    }
    for key, expected_value in expected_headers.items():
        if required_metadata_values(locked_text, key) != [expected_value]:
            issue(issues, "FORWARD-RIGHTS-HEADER", f"{relative_package}/locked-script.md", f"{key} must appear exactly once with its required value.")
    script_fact_pairs = [
        (match.group(1), match.group(2))
        for match in re.finditer(r"^- (FACT-[0-9]+): (.+)$", locked_text, re.MULTILINE)
    ]
    script_facts = {fact_id: value for fact_id, value in script_fact_pairs}
    input_fact_pairs = [
        (fact.get("fact_id"), fact.get("value"))
        for fact in routing_input.get("locked_facts", [])
        if isinstance(fact, dict)
    ]
    input_facts = {fact_id: value for fact_id, value in input_fact_pairs}
    if (
        len(script_fact_pairs) != len(script_facts)
        or len(input_fact_pairs) != len(input_facts)
        or script_facts != input_facts
    ):
        issue(issues, "FORWARD-LOCKED-FACT-DRIFT", f"{relative_package}/locked-script.md", "Script fact IDs and values must exactly equal the structured routing facts.")
    for fact in routing_input.get("locked_facts", []):
        source_ref = fact.get("source_ref", "")
        expected_prefix = "locked-script.md#"
        anchor = source_ref[len(expected_prefix):] if isinstance(source_ref, str) and source_ref.startswith(expected_prefix) else ""
        if not anchor or f'<a id="{anchor}"></a>' not in locked_text:
            issue(issues, "FORWARD-FACT-ANCHOR", f"{relative_package}/routing-input.json", "Locked fact source reference does not resolve to this package script.")

    live_routing = route_scene(routing_input, grammar)
    if saved_routing != live_routing:
        issue(issues, "FORWARD-ROUTING-DRIFT", f"{relative_package}/selected-rules.json", "Saved rule selection differs from the live canonical router result.")
    if live_routing.get("human_review_status") != "HUMAN_REVIEW_PENDING":
        issue(issues, "FORWARD-ROUTING-REVIEW", f"{relative_package}/selected-rules.json", "Routing output must remain HUMAN_REVIEW_PENDING.")
    if live_routing.get("status") != entry.get("expected_routing_status") or live_routing.get("selection_count") != entry.get("expected_selection_count"):
        issue(issues, "FORWARD-ROUTING-EXPECTATION", f"{relative_package}/selected-rules.json", "Live routing result differs from the indexed expectation.")
    live_selected_ids = [item.get("rule_id") for item in live_routing.get("selected_rules", [])]
    if live_selected_ids != entry.get("expected_selected_rule_ids"):
        issue(issues, "FORWARD-RULE-SELECTION", f"{relative_package}/selected-rules.json", "Selected rule IDs differ from the rule-level expectation.")
    expected_rejected_id = entry.get("expected_rejected_rule_id")
    if expected_rejected_id:
        rejected = next(
            (item for item in live_routing.get("rejected_rules", []) if item.get("rule_id") == expected_rejected_id),
            None,
        )
        if rejected is None or not set(entry.get("expected_rejection_reason_codes", [])).issubset(
            rejected.get("rejection_reason_codes", [])
        ):
            issue(issues, "FORWARD-RULE-BOUNDARY", f"{relative_package}/selected-rules.json", "Boundary rule was not rejected for the declared reason.")
        target_rule = next(
            (item for item in grammar.get("rules", []) if item.get("rule_id") == expected_rejected_id),
            None,
        )
        if target_rule is not None:
            counterfactual_input = copy.deepcopy(routing_input)
            blocked_signals = set(target_rule.get("routing", {}).get("not_applicable_if_any", []))
            counterfactual_input["routing_signals"] = [
                signal
                for signal in counterfactual_input.get("routing_signals", [])
                if signal not in blocked_signals
            ]
            counterfactual = route_scene(counterfactual_input, grammar)
            if expected_rejected_id not in {
                item.get("rule_id") for item in counterfactual.get("selected_rules", [])
            }:
                issue(
                    issues,
                    "FORWARD-BOUNDARY-CAUSALITY",
                    f"{relative_package}/routing-input.json",
                    "Removing only the reviewed negative signal must make the target rule selectable.",
                )
    if zero_eligible and (live_routing.get("status") != "NO_APPLICABLE_RULE" or live_routing.get("selection_count") != 0):
        issue(issues, "FORWARD-ZERO-ELIGIBLE", f"{relative_package}/selected-rules.json", "Zero eligible families cannot produce a positive selection.")

    expected_script_path = f"{relative_package}/locked-script.md"
    if ir.get("source_script") != expected_script_path:
        issue(issues, "FORWARD-IR-SOURCE", f"{relative_package}/director-ir.json", "IR source_script must point to its own locked-script.md.")
    if ir.get("director_grammar_path") != "research/grammar/director_grammar_v0.2.json":
        issue(issues, "FORWARD-IR-GRAMMAR", f"{relative_package}/director-ir.json", "IR must bind the canonical Grammar v0.2 path.")
    if ir.get("status") != "HUMAN_REVIEW_PENDING" or ir.get("generation_authorized") is not False or ir.get("publication_authorized") is not False:
        issue(issues, "FORWARD-IR-AUTHORIZATION", f"{relative_package}/director-ir.json", "IR review and external-action gates drifted.")
    scenes = ir.get("scenes", [])
    if (
        len(scenes) != 1
        or scenes[0].get("routing_input") != routing_input
        or scenes[0].get("routing_result") != live_routing
    ):
        issue(issues, "FORWARD-IR-ROUTING", f"{relative_package}/director-ir.json", "IR must embed the canonical routing input and its complete live routing result exactly once.")
    input_refs = {fact.get("source_ref") for fact in routing_input.get("locked_facts", [])}
    coverage_refs = {item.get("source_ref") for item in ir.get("source_coverage", [])}
    if input_refs != coverage_refs:
        issue(issues, "FORWARD-COVERAGE-FACTS", f"{relative_package}/director-ir.json", "IR coverage must exactly cover every locked routing fact.")
    coverage_by_ref = {
        item.get("source_ref"): item.get("description")
        for item in ir.get("source_coverage", [])
        if isinstance(item, dict)
    }
    expected_coverage_values = {
        fact.get("source_ref"): fact.get("value")
        for fact in routing_input.get("locked_facts", [])
        if isinstance(fact, dict)
    }
    if coverage_by_ref != expected_coverage_values:
        issue(issues, "FORWARD-COVERAGE-VALUE-DRIFT", f"{relative_package}/director-ir.json", "IR coverage descriptions must exactly preserve every locked fact value.")
    if "SOUND_DRIVEN_SUSPENSE" in entry.get("coverage_tags", []):
        audio_fact_refs = {
            fact.get("source_ref")
            for fact in routing_input.get("locked_facts", [])
            if isinstance(fact, dict) and fact.get("fact_type") == "audible_information"
        }
        audio_records = [
            shot.get("audio", {})
            for scene in ir.get("scenes", [])
            if isinstance(scene, dict)
            for shot in scene.get("shots", [])
            if isinstance(shot, dict)
        ]
        bound_audio_refs = {
            source_ref
            for audio in audio_records
            if isinstance(audio, dict)
            and audio.get("status") == "PROJECT_ORIGINAL_LOCKED"
            and isinstance(audio.get("instruction"), str)
            and audio.get("instruction").strip()
            for source_ref in audio.get("source_refs", [])
        }
        if not audio_fact_refs or not audio_fact_refs.issubset(bound_audio_refs):
            issue(issues, "FORWARD-SOUND-AUDIO", f"{relative_package}/director-ir.json", "Locked audible facts must bind to explicit project-original IR audio instructions.")
    ir_report = validate_ir(ir, grammar, locked_text)
    if ir_report["status"] != "PASS":
        issue(issues, "FORWARD-IR-VALIDATION", f"{relative_package}/director-ir.json", "Complete Director IR validation failed.")
    expected_shot_script = render_shot_script(ir)
    expected_coverage = render_coverage(ir)
    if (package / "shot-script.md").read_text(encoding="utf-8") != expected_shot_script:
        issue(issues, "FORWARD-SHOT-RENDER", f"{relative_package}/shot-script.md", "Shot script differs from deterministic IR rendering.")
    if (package / "source-coverage.md").read_text(encoding="utf-8") != expected_coverage:
        issue(issues, "FORWARD-COVERAGE-RENDER", f"{relative_package}/source-coverage.md", "Coverage Markdown differs from deterministic IR rendering.")
    selected_shot_rule_ids = {
        rule_id
        for scene in ir.get("scenes", [])
        for shot in scene.get("shots", [])
        for rule_id in shot.get("evidence_rule_ids", [])
    }
    if entry.get("test_mode") == "POSITIVE":
        if not entry.get("changed_director_dimensions") or selected_shot_rule_ids != set(entry.get("expected_selected_rule_ids", [])):
            issue(issues, "FORWARD-DIRECTOR-CHANGE", f"{relative_package}/director-ir.json", "Positive case must name changed directing dimensions and bind selected rules to affected Shots.")
        changed_shots = [
            shot
            for scene in ir.get("scenes", [])
            for shot in scene.get("shots", [])
            if shot.get("evidence_rule_ids")
        ]
        if not changed_shots or all(shot.get("shot_type") == "project-original coverage" for shot in changed_shots):
            issue(issues, "FORWARD-DIRECTOR-CHANGE", f"{relative_package}/director-ir.json", "Selected rule did not materially change the generated Shot plan.")
    expected_validation = expected_case_validation(entry, live_routing, ir_report)
    if saved_validation != expected_validation:
        issue(issues, "FORWARD-VALIDATION-DRIFT", f"{relative_package}/validation.json", "Saved package validation differs from live recomputation.")
    review_text = (package / "human-review.md").read_text(encoding="utf-8")
    if review_text != expected_human_review_text(case_id):
        issue(issues, "FORWARD-HUMAN-REVIEW", f"{relative_package}/human-review.md", "Human-review record must exactly preserve the pending and unauthorized state.")
    return {
        "test_case_id": case_id,
        "status": "PASS" if not issues else "FAIL",
        "scene_problem": entry.get("scene_problem"),
        "routing_status": live_routing.get("status"),
        "selection_count": live_routing.get("selection_count", 0),
        "human_review_status": live_routing.get("human_review_status"),
        "ir_warning_count": ir_report["warnings"],
    }, issues


def validate_repository(
    index: dict[str, Any],
    grammar: dict[str, Any],
    candidate_index: dict[str, Any],
    matrix: dict[str, Any],
    grammar_schema: dict[str, Any],
    index_schema: dict[str, Any],
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    schema_raw_issues: list[dict[str, str]] = []
    validate_schema_subset(index, index_schema, index_schema, schema_raw_issues, "$")
    for item in schema_raw_issues:
        issue(issues, "FORWARD-INDEX-SCHEMA", item["path"], item["message"])
    grammar_report = validate_grammar(grammar, candidate_index, matrix, grammar_schema)
    if grammar_report["status"] != "PASS":
        issue(issues, "FORWARD-GRAMMAR", "grammar", "Canonical grammar authorities fail before forward testing.")
    eligible = eligible_candidates(candidate_index, matrix) if grammar_report["status"] == "PASS" else {}
    eligible_families = sorted({candidate["canonical_rule_family"] for candidate in eligible.values()})
    zero_eligible = not eligible_families
    if index.get("promotion_ready_family_ids") != eligible_families or index.get("promotion_ready_family_count") != len(eligible_families):
        issue(issues, "FORWARD-ELIGIBLE-DRIFT", "promotion_ready_family_ids", "Index does not match the live eligible family set.")
    expected_status = "NO_ELIGIBLE_FAMILIES" if zero_eligible else "RULE_COVERAGE_COMPLETE"
    if index.get("status") != expected_status:
        issue(issues, "FORWARD-INDEX-STATUS", "status", "Index status does not match the live eligible family set.")
    entries = index.get("cases", []) if isinstance(index.get("cases"), list) else []
    case_ids = [entry.get("test_case_id") for entry in entries if isinstance(entry, dict)]
    if len(case_ids) != len(set(case_ids)) or set(case_ids) != REQUIRED_CASE_IDS:
        issue(issues, "FORWARD-CASE-SET", "cases", "The required unique original cases are not present.")
    tags = {tag for entry in entries if isinstance(entry, dict) for tag in entry.get("coverage_tags", [])}
    if tags != REQUIRED_COVERAGE_TAGS or set(index.get("required_scene_problem_coverage", [])) != REQUIRED_COVERAGE_TAGS:
        issue(issues, "FORWARD-COVERAGE-TAGS", "required_scene_problem_coverage", "The six required original scene problems are not covered exactly.")
    indexed_dirs = {entry.get("test_case_id") for entry in entries if isinstance(entry, dict)}
    actual_dirs = {path.name for path in FORWARD_ROOT.iterdir() if path.is_dir()}
    if indexed_dirs != actual_dirs:
        issue(issues, "FORWARD-DIRECTORY-SET", "examples/forward-tests", "Indexed and actual case directories differ.")
    root_files = {path.name for path in FORWARD_ROOT.iterdir() if path.is_file()}
    if root_files != {"index.json"}:
        issue(issues, "FORWARD-ROOT-FILE-SET", "examples/forward-tests", "Only index.json may exist beside the case directories.")

    positive_by_family: dict[str, set[str]] = {family: set() for family in eligible_families}
    boundary_by_family: dict[str, set[str]] = {family: set() for family in eligible_families}
    eligible_rule_ids = sorted(rule["rule_id"] for rule in grammar.get("rules", []))
    positive_by_rule: dict[str, set[str]] = {rule_id: set() for rule_id in eligible_rule_ids}
    boundary_by_rule: dict[str, set[str]] = {rule_id: set() for rule_id in eligible_rule_ids}
    results: list[dict[str, Any]] = []
    for entry_index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            issue(issues, "FORWARD-INDEX-ENTRY", f"cases[{entry_index}]", "Case entry must be an object.")
            continue
        if zero_eligible and (
            entry.get("test_mode") != "ZERO_ELIGIBLE_PROBE"
            or entry.get("positive_for_family_ids")
            or entry.get("boundary_for_family_ids")
        ):
            issue(issues, "FORWARD-FALSE-POSITIVE", f"cases[{entry_index}]", "Zero-eligible packages cannot claim positive or boundary family coverage.")
        for family in entry.get("positive_for_family_ids", []):
            if family in positive_by_family:
                positive_by_family[family].add(entry["test_case_id"])
        for family in entry.get("boundary_for_family_ids", []):
            if family in boundary_by_family:
                boundary_by_family[family].add(entry["test_case_id"])
        for rule_id in entry.get("positive_for_rule_ids", []):
            if rule_id in positive_by_rule:
                positive_by_rule[rule_id].add(entry["test_case_id"])
        for rule_id in entry.get("boundary_for_rule_ids", []):
            if rule_id in boundary_by_rule:
                boundary_by_rule[rule_id].add(entry["test_case_id"])
        package = safe_package_path(entry.get("package_path"), issues, f"cases[{entry_index}].package_path")
        if package is None:
            continue
        result, package_issues = validate_package(entry, package, grammar, candidate_index, zero_eligible)
        results.append(result)
        issues.extend(package_issues)

    missing_families = sorted(
        family
        for family in eligible_families
        if not positive_by_family[family]
        or not boundary_by_family[family]
        or positive_by_family[family] & boundary_by_family[family]
    )
    missing_rules = sorted(
        rule_id
        for rule_id in eligible_rule_ids
        if not positive_by_rule[rule_id]
        or not boundary_by_rule[rule_id]
        or positive_by_rule[rule_id] & boundary_by_rule[rule_id]
    )
    completed_positive = sum(bool(values) for values in positive_by_rule.values())
    completed_boundary = sum(bool(values) for values in boundary_by_rule.values())
    if (
        index.get("required_positive_boundary_pairs") != len(eligible_rule_ids)
        or index.get("completed_positive_cases") != completed_positive
        or index.get("completed_boundary_cases") != completed_boundary
        or index.get("missing_family_ids") != missing_families
        or index.get("missing_rule_ids") != missing_rules
    ):
        issue(issues, "FORWARD-RULE-COVERAGE-DRIFT", "rule coverage", "Rule positive/boundary coverage counts do not match live package bindings.")
    if missing_families or missing_rules:
        issue(issues, "FORWARD-RULE-COVERAGE-MISSING", "missing_rule_ids", "Every eligible rule needs distinct positive and boundary packages.")
    results.sort(key=lambda item: str(item.get("test_case_id")))
    return {
        "schema_version": "forward-test-repository-validation/0.1",
        "status": "PASS" if not issues else "FAIL",
        "package_count": len(results),
        "required_scene_problem_count": len(REQUIRED_COVERAGE_TAGS),
        "promotion_ready_family_count": len(eligible_families),
        "required_positive_boundary_pairs": len(eligible_rule_ids),
        "completed_positive_cases": completed_positive,
        "completed_boundary_cases": completed_boundary,
        "missing_family_count": len(missing_families),
        "missing_rule_count": len(missing_rules),
        "no_applicable_rule_count": sum(result.get("routing_status") == "NO_APPLICABLE_RULE" for result in results),
        "selected_rule_count": sum(int(result.get("selection_count", 0)) for result in results),
        "human_review_pending_count": sum(result.get("human_review_status") == "HUMAN_REVIEW_PENDING" for result in results),
        "structural_pass_count": sum(result.get("status") == "PASS" for result in results),
        "warning_count": sum(int(result.get("ir_warning_count", 0)) for result in results),
        "error_count": len(issues),
        "cases": results,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=INDEX_PATH)
    parser.add_argument("--grammar", type=Path, default=GRAMMAR_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = validate_repository(
        read_json(args.index),
        read_json(args.grammar),
        read_json(CANDIDATE_INDEX_PATH),
        read_json(MATRIX_PATH),
        read_json(GRAMMAR_SCHEMA_PATH),
        read_json(INDEX_SCHEMA_PATH),
    )
    rendered = json_text(report)
    if args.check:
        if not args.report.is_file() or args.report.read_text(encoding="utf-8") != rendered:
            return 1
    else:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
