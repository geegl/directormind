#!/usr/bin/env python3
"""Run the complete local DirectorMind repository contract suite."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REPOSITORY_ROOT = SKILL_ROOT.parents[1]


@dataclass(frozen=True)
class Check:
    name: str
    command: tuple[str, ...]
    quick: bool = True


def checks(report_root: Path) -> list[Check]:
    python = sys.executable
    script = "skills/drama-director-compiler/scripts"
    result = [
        Check("repository syntax, references and public boundaries", (python, f"{script}/validate_repository_boundaries.py", "--quiet")),
        Check("canonical conversion determinism", (python, f"{script}/convert_legacy_scene_evidence.py", "--check")),
        Check("generated review determinism", (python, f"{script}/render_scene_evidence.py", "--check")),
        Check("candidate index determinism", (python, f"{script}/build_candidate_rule_index.py", "--check")),
        Check("runtime promotion review", (python, f"{script}/validate_runtime_rule_promotion_review.py", "--report", str(report_root / "runtime-rule-promotion-wave1-validation.json"))),
        Check("exhaustive runtime integration authority", (python, f"{script}/validate_runtime_integration_review.py", "--report", str(report_root / "runtime-integration-validation.json"))),
        Check("Scene Evidence validation", (python, f"{script}/validate_scene_evidence.py", "research/evidence", "--report", str(report_root / "scene-evidence-validation.json"), "--quiet")),
        Check("candidate promotion gates", (python, f"{script}/validate_candidate_rules.py", "--report", str(report_root / "candidate-rule-validation.json"), "--quiet")),
        Check("runtime Grammar build determinism", (python, f"{script}/build_director_grammar.py", "--check")),
        Check("runtime Grammar validation", (python, f"{script}/validate_director_grammar.py", "--report", str(report_root / "director-grammar-validation.json"))),
        Check("routing-case validation", (python, f"{script}/validate_director_routing_cases.py", "--report", str(report_root / "director-routing-validation.json"))),
        Check("forward-test build determinism", (python, f"{script}/build_forward_tests.py", "--check")),
        Check("forward-test repository", (python, f"{script}/validate_forward_tests.py", "--report", str(report_root / "forward-test-validation.json"))),
        Check("exhaustive runtime integration report", (python, f"{script}/build_exhaustive_runtime_integration_validation.py", "--report", str(report_root / "exhaustive-runtime-integration-validation.json"))),
        Check("unit and CLI suite", (python, "-m", "unittest", "discover", "-s", "skills/drama-director-compiler/tests"), quick=False),
        Check("whitespace", ("git", "diff", "--check", "origin/main...HEAD")),
    ]
    return result


def _run(check: Check, env: dict[str, str]) -> tuple[bool, str]:
    completed = subprocess.run(
        check.command,
        cwd=REPOSITORY_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode == 0, completed.stdout.strip()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="skip the full unit/CLI suite")
    parser.add_argument(
        "--write-final-report",
        action="store_true",
        help="after every check passes, refresh the deterministic final report",
    )
    args = parser.parse_args(argv)

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="directormind-checks-") as directory:
        report_root = Path(directory)
        selected = [
            check
            for check in checks(report_root)
            if check.quick or not args.quick
        ]
        failures: list[str] = []
        live_results: dict[str, str] = {}
        for check in selected:
            passed, output = _run(check, env)
            live_results[check.name] = "PASS" if passed else "FAIL"
            print(f"{'PASS' if passed else 'FAIL'} — {check.name}")
            if not passed:
                failures.append(check.name)
                if output:
                    print(output)
                break

        if not failures:
            versioned_root = REPOSITORY_ROOT / "research" / "validation"
            versioned_report_names = (
                "scene-evidence-validation.json",
                "runtime-rule-promotion-wave1-validation.json",
                "runtime-integration-validation.json",
                "candidate-rule-validation.json",
                "director-grammar-validation.json",
                "director-routing-validation.json",
                "forward-test-validation.json",
                "exhaustive-runtime-integration-validation.json",
            )
            for name in versioned_report_names:
                generated = report_root / name
                versioned = versioned_root / name
                passed = generated.is_file() and versioned.is_file() and generated.read_bytes() == versioned.read_bytes()
                check_name = f"versioned report {name}"
                live_results[check_name] = "PASS" if passed else "FAIL"
                print(f"{'PASS' if passed else 'FAIL'} — {check_name}")
                if not passed:
                    failures.append(check_name)
                    break

        if failures:
            print(f"FAILED: {failures[0]}", file=sys.stderr)
            return 1

        final_report_count = 0
        if not args.quick:
            evidence_path = report_root / "local-check-evidence.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "schema_version": "local-check-evidence/0.1",
                        "check_results": live_results,
                    },
                    sort_keys=True,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            build = Check(
                "final validation report build" if args.write_final_report else "final validation report determinism",
                (
                    sys.executable,
                    "skills/drama-director-compiler/scripts/build_final_generalization_validation.py",
                    "--evidence",
                    str(evidence_path),
                    *(( ) if args.write_final_report else ("--check",)),
                ),
            )
            passed, output = _run(build, env)
            print(f"{'PASS' if passed else 'FAIL'} — {build.name}")
            if not passed:
                if output:
                    print(output)
                return 1
            final_report_count = 1

        total = len(selected) + len(versioned_report_names) + final_report_count
        print(f"PASS: {total} repository checks")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
