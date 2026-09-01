#!/usr/bin/env python3
"""Repository-state tests for the approved generalization Phase 1."""

from __future__ import annotations

import re
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTEXT = REPO_ROOT / "context"
COVERAGE = REPO_ROOT / "research" / "coverage"


class PhaseOneStateContractTests(unittest.TestCase):
    def test_state_is_compact_and_declares_five_authorities(self) -> None:
        state = (CONTEXT / "STATE.md").read_text(encoding="utf-8")
        self.assertLess(len(state.splitlines()), 100)
        for source in (
            "research/evidence/**/*.scene-evidence.json",
            "research/grammar/candidate_rule_index.json",
            "research/grammar/cross_work_support_matrix.json",
            "research/grammar/director_grammar_v0.2.json",
            "context/STATE.md",
        ):
            self.assertIn(source, state)
        self.assertNotIn("## Evidence status", state)

    def test_material_and_coverage_files_declare_catalog_boundary(self) -> None:
        catalogs = (
            "FIRST_16_SCENES.md",
            "FIRST_16_LOCAL_MATERIAL_MANIFEST.md",
            "POST_16_ACQUISITION_BACKLOG.md",
            "POST_16_LOCAL_MATERIAL_MANIFEST.md",
            "SCENE_PROBLEM_MAP.md",
        )
        for name in catalogs:
            opening = "\n".join(
                (COVERAGE / name).read_text(encoding="utf-8").splitlines()[:16]
            )
            self.assertIn("Authority boundary:", opening, name)
            self.assertIn("context/STATE.md", opening, name)

    def test_approved_task_card_keeps_external_actions_gated(self) -> None:
        card = (CONTEXT / "THIRD_PARTY_GENERALIZATION_AUDIT_TASK.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Status: `ACTIVE / USER_APPROVED`", card)
        self.assertIn("First push to PR #3 requires a new explicit user confirmation", card)
        self.assertIn("Closing PR #1 requires a separate explicit user confirmation", card)
        self.assertIn("A valid grammar may contain zero promoted evidence rules", card)
        self.assertIn("Never overwrite or delete the 30 legacy evidence Markdown", card)

    def test_checklist_has_one_current_phase_and_no_stale_next_action(self) -> None:
        checklist = (CONTEXT / "GENERALIZATION_REMEDIATION_CHECKLIST.md").read_text(
            encoding="utf-8"
        )
        rows = re.findall(
            r"^\| ([A-Z]\d+|P\d+) \| (TODO|IN_PROGRESS|BLOCKED|VERIFIED_DONE) \|",
            checklist,
            re.MULTILINE,
        )
        self.assertEqual(len(rows), 57)
        self.assertEqual(
            Counter(status for _, status in rows),
            Counter({"TODO": 23, "VERIFIED_DONE": 34}),
        )
        self.assertNotIn(
            "Closed-corpus completion is independently reviewed and ready for one isolated local commit",
            checklist,
        )
        self.assertNotIn("fresh independent verdict on the latest working tree is pending", checklist)


if __name__ == "__main__":
    unittest.main()
