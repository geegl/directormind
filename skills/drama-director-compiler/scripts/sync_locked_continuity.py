#!/usr/bin/env python3
"""Copy locked per-episode continuity outputs from the source script into Director IR."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def extract(source: Path) -> list[str]:
    text = source.read_text(encoding="utf-8")
    if "### 本集连续性输出" not in text:
        raise SystemExit(f"missing continuity output: {source}")
    tail = text.split("### 本集连续性输出", 1)[1]
    values = [line.strip().removeprefix("- ").strip() for line in tail.splitlines() if line.strip().startswith("- ")]
    if not values:
        raise SystemExit(f"empty continuity output: {source}")
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ir", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ir = json.loads(args.ir.read_text(encoding="utf-8"))
    ir.setdefault("source_facts", {})["continuity_output"] = extract(args.source)
    args.output.write_text(json.dumps(ir, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
