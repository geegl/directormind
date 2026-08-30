#!/usr/bin/env python3
"""Export the canonical per-shot visual module map from Director IR v0.2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ir = json.loads(args.ir.read_text(encoding="utf-8"))
    mapping = {
        "schema_version": "visual-module-map/0.2",
        "episode_id": ir["episode_id"],
        "shot_modules": {
            shot["shot_id"]: shot["visual_style_module"]
            for scene in ir["scenes"] for shot in scene["shots"]
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
