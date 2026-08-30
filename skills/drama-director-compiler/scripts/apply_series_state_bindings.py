#!/usr/bin/env python3
"""Bind explicit cross-episode state IDs into producer and consumer Director IR files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def shot_blob(shot: dict[str, Any]) -> str:
    return json.dumps(shot, ensure_ascii=False)


def add_state(shot: dict[str, Any], state: dict[str, Any]) -> None:
    states = shot["execution_plan"]["state_versions"]
    if not any(item.get("state_id") == state["state_id"] for item in states):
        states.append(state)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checks", type=Path, required=True)
    parser.add_argument("--episodes", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(args.checks.read_text(encoding="utf-8"))
    episodes: dict[str, dict[str, Any]] = {}
    for number in range(1, 37):
        episode_id = f"EP{number:02d}"
        path = args.episodes / f"{episode_id}_DIRECTOR_IR_V0.2.json"
        ir = json.loads(path.read_text(encoding="utf-8"))
        ir["source_facts"]["cross_episode_state_in"] = []
        ir["source_facts"]["cross_episode_state_out"] = []
        episodes[episode_id] = ir

    for check in spec["checks"]:
        state_id = f"XSTATE-{check['check_id']}@v001"
        producer_id = check["producer_episode"]
        consumer_id = check["consumer_episode"]
        description = f"{producer_id} produces {' / '.join(check['producer_terms'])}; {consumer_id} consumes {' / '.join(check['consumer_terms'])}."
        producer = episodes[producer_id]
        consumer = episodes[consumer_id]
        producer["source_facts"]["cross_episode_state_out"].append({"state_id": state_id, "episode": consumer_id, "description": description})
        consumer["source_facts"]["cross_episode_state_in"].append({"state_id": state_id, "episode": producer_id, "description": description})

        producer_shot = producer["scenes"][-1]["shots"][-1]
        consumer_shots = [shot for scene in consumer["scenes"] for shot in scene["shots"]]
        consumer_shot = next(
            (shot for shot in consumer_shots if any(term in shot_blob(shot) for term in check["consumer_terms"])),
            consumer_shots[0],
        )
        add_state(producer_shot, {"state_id": state_id, "subject": "cross-episode continuity anchor", "state": description, "owner": "SHARED", "effective_from": producer_shot["shot_id"], "carry_forward": True})
        add_state(consumer_shot, {"state_id": state_id, "subject": "cross-episode continuity anchor", "state": description, "owner": "SHARED", "effective_from": consumer_shot["shot_id"], "carry_forward": False})

    for episode_id, ir in episodes.items():
        path = args.episodes / f"{episode_id}_DIRECTOR_IR_V0.2.json"
        path.write_text(json.dumps(ir, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
