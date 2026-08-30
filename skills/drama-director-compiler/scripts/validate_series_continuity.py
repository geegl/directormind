#!/usr/bin/env python3
"""Validate explicit producer-to-consumer continuity anchors across the 36 episodes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checks", type=Path, required=True)
    parser.add_argument("--episodes", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(args.checks.read_text(encoding="utf-8"))
    results = []
    for check in spec["checks"]:
        producer_id = check["producer_episode"]
        consumer_id = check["consumer_episode"]
        producer_ir = json.loads((args.episodes / f"{producer_id}_DIRECTOR_IR_V0.2.json").read_text(encoding="utf-8"))
        producer_blob = "\n".join(producer_ir["source_facts"]["continuity_output"])
        consumer_ir = json.loads((args.episodes / f"{consumer_id}_DIRECTOR_IR_V0.2.json").read_text(encoding="utf-8"))
        consumer_source = Path(consumer_ir_path := consumer_ir["source_script"])
        consumer_blob = consumer_source.read_text(encoding="utf-8")
        producer_ir_blob = json.dumps(producer_ir, ensure_ascii=False)
        consumer_ir_blob = json.dumps(consumer_ir, ensure_ascii=False)
        state_id = f"XSTATE-{check['check_id']}@v001"
        producer_missing = [term for term in check["producer_terms"] if term not in producer_blob]
        consumer_missing = [term for term in check["consumer_terms"] if term not in consumer_blob]
        producer_ir_missing = [term for term in check["producer_terms"] if term not in producer_ir_blob]
        consumer_ir_missing = [term for term in check["consumer_terms"] if term not in consumer_ir_blob]
        producer_state_missing = state_id not in producer_ir_blob
        consumer_state_missing = state_id not in consumer_ir_blob
        results.append({
            "check_id": check["check_id"],
            "producer_episode": producer_id,
            "consumer_episode": consumer_id,
            "state_id": state_id,
            "status": "PASS" if not producer_missing and not consumer_missing and not producer_ir_missing and not consumer_ir_missing and not producer_state_missing and not consumer_state_missing else "FAIL",
            "producer_missing": producer_missing,
            "consumer_missing": consumer_missing,
            "producer_ir_missing": producer_ir_missing,
            "consumer_ir_missing": consumer_ir_missing,
            "producer_state_missing": producer_state_missing,
            "consumer_state_missing": consumer_state_missing,
            "consumer_source": consumer_ir_path,
        })
    failures = [result for result in results if result["status"] == "FAIL"]
    report = {"schema_version": "director-series-continuity-report/0.2", "status": "PASS" if not failures else "FAIL", "check_count": len(results), "pass_count": len(results) - len(failures), "failure_count": len(failures), "results": results}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "check_count", "pass_count", "failure_count")}, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
