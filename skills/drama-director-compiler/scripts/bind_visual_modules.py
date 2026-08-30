#!/usr/bin/env python3
"""Bind an approved visual style pack and per-shot modules into Director IR."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ir", type=Path, required=True)
    parser.add_argument("--style-pack", required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    ir = json.loads(args.ir.read_text(encoding="utf-8"))
    mapping = json.loads(args.mapping.read_text(encoding="utf-8"))
    modules = mapping.get("shot_modules", {})
    if not isinstance(modules, dict) or not modules:
        raise SystemExit("mapping must contain a non-empty shot_modules object")

    shots = [shot for scene in ir["scenes"] for shot in scene["shots"]]
    shot_ids = {shot["shot_id"] for shot in shots}
    missing = sorted(shot_ids - modules.keys())
    extra = sorted(modules.keys() - shot_ids)
    if missing or extra:
        raise SystemExit(f"visual mapping mismatch: missing={missing}, extra={extra}")

    for shot in shots:
        module_id = modules[shot["shot_id"]]
        if not isinstance(module_id, str) or not module_id.startswith("VIS-"):
            raise SystemExit(f"invalid visual module for {shot['shot_id']}: {module_id!r}")
        shot["visual_style_module"] = module_id

    ir["visual_style_pack_path"] = args.style_pack
    ir["unresolved"] = [
        item for item in ir.get("unresolved", [])
        if not item.startswith("Bind approved visual style module IDs")
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ir, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
