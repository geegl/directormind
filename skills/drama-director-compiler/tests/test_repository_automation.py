#!/usr/bin/env python3
"""Regression tests for repository automation and the final local report."""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
SCRIPT_ROOT = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_ROOT))

from build_final_generalization_validation import (  # noqa: E402
    LIVE_CHECK_NAMES,
    build_report,
    validate_report,
)
from run_repository_checks import checks  # noqa: E402
from validate_repository_boundaries import validate_repository  # noqa: E402


def issue_codes(report: dict) -> set[str]:
    return {item["code"] for item in report["issues"]}


def successful_live_evidence() -> dict:
    return {
        "schema_version": "local-check-evidence/0.1",
        "check_results": {name: "PASS" for name in LIVE_CHECK_NAMES},
    }


class RepositoryAutomationTests(unittest.TestCase):
    def test_current_repository_boundary_scan_passes(self) -> None:
        report = validate_repository(REPO_ROOT)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["error_count"], 0)
        self.assertEqual(report["broken_reference_count"], 0)
        self.assertEqual(report["prohibited_repository_file_count"], 0)
        self.assertEqual(report["scoped_public_string_issue_count"], 0)
        self.assertEqual(report["public_string_scan_scope"], "CURRENT_MACHINE_AND_RUNTIME_ARTIFACTS_ONLY")
        self.assertEqual(report["excluded_historical_legacy_markdown_count"], 30)
        self.assertEqual(report["whitespace_issue_count"], 0)
        self.assertEqual(report["symlink_escape_count"], 0)

    def test_invalid_json_and_python_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "broken.json").write_text("{\n", encoding="utf-8")
            (root / "broken.py").write_text("def broken(:\n", encoding="utf-8")
            codes = issue_codes(validate_repository(root))
        self.assertIn("INVALID-JSON", codes)
        self.assertIn("INVALID-PYTHON", codes)

    def test_media_file_and_private_public_payload_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "context").mkdir()
            (root / "context" / "STATE.md").write_text(
                "private source /Users/example/source\n",
                encoding="utf-8",
            )
            (root / "clip.mp4").write_bytes(b"not actual media")
            report = validate_repository(root)
            codes = issue_codes(report)
        self.assertIn("PRIVATE-ABSOLUTE-PATH", codes)
        self.assertIn("PROHIBITED-REPOSITORY-FILE", codes)

    def test_original_legacy_markdown_is_not_treated_as_operational_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "research" / "evidence" / "legacy" / "OLD_EVIDENCE.md"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("Historical local label example.mp4 at 00:00:01.000\n", encoding="utf-8")
            legacy.with_suffix(".scene-evidence.json").write_text("{}\n", encoding="utf-8")
            report = validate_repository(root)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["excluded_historical_legacy_markdown_count"], 1)
        self.assertEqual(
            report["historical_legacy_markdown_scope"],
            "EXCLUDED_IMMUTABLE_PROVENANCE_CONVERTED_OUTPUTS_VALIDATED",
        )

    def test_broken_and_escaping_markdown_links_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "[missing](missing.md)\n[escape](../outside.md)\n",
                encoding="utf-8",
            )
            codes = issue_codes(validate_repository(root))
        self.assertIn("BROKEN-MARKDOWN-LINK", codes)
        self.assertIn("MARKDOWN-LINK-ESCAPES-REPOSITORY", codes)

    def test_full_tree_whitespace_contract_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.md").write_text("trailing space ", encoding="utf-8")
            codes = issue_codes(validate_repository(root))
        self.assertIn("TRAILING-WHITESPACE", codes)
        self.assertIn("MISSING-FINAL-NEWLINE", codes)

    def test_final_report_matches_schema_contract(self) -> None:
        report = build_report(successful_live_evidence())
        self.assertEqual(validate_report(report), [])
        self.assertEqual(report["status"], "PASS_LOCAL")

    def test_final_report_schema_rejects_count_drift(self) -> None:
        report = copy.deepcopy(build_report(successful_live_evidence()))
        report["counts"]["canonical_scenes"] -= 1
        self.assertTrue(validate_report(report))

        failed_evidence = successful_live_evidence()
        failed_evidence["check_results"]["unit and CLI suite"] = "FAIL"
        failed_report = build_report(failed_evidence)
        self.assertEqual(failed_report["status"], "FAIL_LOCAL")
        self.assertEqual(failed_report["checks"]["unit_suite"], "FAIL")
        self.assertIn("LIVE_CHECK_NOT_PASSED: unit and CLI suite", failed_report["errors"])

    def test_local_runner_covers_every_required_contract(self) -> None:
        configured_checks = checks(Path("/tmp/reports"))
        names = {item.name for item in configured_checks}
        for required in (
            "repository syntax, references and public boundaries",
            "canonical conversion determinism",
            "generated review determinism",
            "candidate index determinism",
            "Scene Evidence validation",
            "candidate promotion gates",
            "runtime Grammar validation",
            "routing-case validation",
            "forward-test build determinism",
            "forward-test repository",
            "unit and CLI suite",
            "whitespace",
        ):
            self.assertIn(required, names)
        runner = (SCRIPT_ROOT / "run_repository_checks.py").read_text(encoding="utf-8")
        self.assertIn("build_final_generalization_validation.py", runner)
        self.assertIn("local-check-evidence.json", runner)
        whitespace = next(item for item in configured_checks if item.name == "whitespace")
        self.assertEqual(
            whitespace.command,
            ("git", "diff", "--check", "origin/main...HEAD"),
        )

    def test_ci_workflow_is_read_only_and_runs_the_local_contract(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "directormind-contracts.yml").read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("uses: actions/checkout@v6", workflow)
        self.assertIn("fetch-depth: 0", workflow)
        self.assertIn("uses: actions/setup-python@v6", workflow)
        self.assertIn("run_repository_checks.py", workflow)
        for unsafe in ("pull_request_target", "secrets.", "artifact", "curl ", "pip install"):
            self.assertNotIn(unsafe, workflow)


if __name__ == "__main__":
    unittest.main()
