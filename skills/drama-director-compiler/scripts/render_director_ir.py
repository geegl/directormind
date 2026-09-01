#!/usr/bin/env python3
"""Render Director IR JSON into reviewable Markdown artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def esc(value: Any) -> str:
    text = str(value).replace("\n", "<br>").replace("|", "\\|")
    return text


def joined(values: list[Any]) -> str:
    return "；".join(esc(value) for value in values) if values else "—"


def dialogue_text(lines: list[dict[str, Any]]) -> str:
    return "<br>".join(f"{esc(line['speaker'])}: {esc(line['text'])}" for line in lines) if lines else "—"


def render_shot_script(ir: dict[str, Any]) -> str:
    lines = [
        f"# {ir['episode_id']} 导演分镜 v0.2",
        "",
        f"- 来源：`{ir['source_script']}`",
        f"- 状态：`{ir['status']}`",
        f"- 规格：{ir['aspect_ratio']}｜目标 {ir['target_duration_seconds']} 秒",
        f"- 执行媒介：`{ir['execution_medium']}`",
        f"- 生成授权：`{str(ir['generation_authorized']).lower()}`",
        f"- 视觉风格包：`{ir['visual_style_pack_path']}`",
        "",
        "> 本文由Director IR确定性渲染；JSON是单一事实源。原剧本对白和可见文字保持锁定。",
        "",
    ]
    for scene in ir["scenes"]:
        lines.extend([
            f"## {scene['scene_id']}｜{scene['title']}｜{scene['duration_seconds']}秒",
            "",
            f"**场景目标：** {scene['narrative_goal']}",
            "",
            f"**POV：** {scene['pov'].get('character', 'UNKNOWN')} / {scene['pov'].get('identification_level', 'UNKNOWN')}",
            "",
            f"**空间：** {scene['spatial_plan'].get('geometry', 'UNKNOWN')}；轴线：{scene['spatial_plan'].get('primary_axis', 'UNKNOWN')}",
            "",
            "| 镜头 | 秒 | 叙事功能 | 景别/机位/运动 | 调度与表演 | 锁定对白/文字 | 声音与衔接 | 执行/参考 | 规则 | AI风险/降级 |",
            "|---|---:|---|---|---|---|---|---|---|---|",
        ])
        for shot in scene["shots"]:
            risk = shot["ai_complexity"]
            risk_text = f"摄{risk['camera']}/表{risk['performance']}/连{risk['continuity']}"
            if shot.get("fallback"):
                risk_text += f"<br>降级：{esc(shot['fallback'])}"
            path = shot["camera_path"]
            camera = (
                f"{esc(shot['shot_type'])}<br>START: {esc(shot['camera_start'])}<br>"
                f"PATH: {esc(path['mode'])} / {esc(path['direction'])} / {esc(path['speed'])} / {esc(path['distance'])}<br>"
                f"END: {esc(shot['camera_end'])}"
            )
            performance = f"{esc(shot['blocking'])}<br>{joined(shot['performance_beats'])}"
            locked = dialogue_text(shot["dialogue"])
            if shot["visible_text"]:
                locked += f"<br>TEXT: {joined(shot['visible_text'])}"
            audio = shot.get("audio") if isinstance(shot.get("audio"), dict) else {}
            audio_text = esc(audio.get("status", "UNKNOWN"))
            if audio.get("instruction"):
                audio_text += f": {esc(audio['instruction'])}"
            if audio.get("source_refs"):
                audio_text += f"<br>AUDIO REF: {joined(audio['source_refs'])}"
            connection = f"AUDIO: {audio_text}<br>IN: {esc(shot['edit_in'])}<br>OUT: {esc(shot['edit_out'])}"
            execution = shot["execution_plan"]
            layer_types = [layer["type"] for layer in execution["composite_layers"]]
            state_ids = [state["state_id"] for state in execution["state_versions"]]
            reference = shot["reference_plan"]
            execution_text = (
                f"BASE: {esc(execution['base_generation']['mode'])}"
                f"<br>POST: {joined(layer_types)}"
                f"<br>STATE: {joined(state_ids)}"
                f"<br>REF: {esc(reference['reference_type'])}/{esc(reference['status'])}"
            )
            rules = joined(shot["evidence_rule_ids"])
            lines.append(
                f"| {shot['shot_id']} | {shot['duration_seconds']} | {esc(shot['narrative_goal'])} | "
                f"{camera} | {performance} | {locked} | {connection} | {execution_text} | {rules} | {risk_text} |"
            )
        lines.extend(["", f"**场景结束状态：** {scene['spatial_plan'].get('close_positions', 'UNKNOWN')}", ""])

    if ir["unresolved"]:
        lines.extend(["## 待人工确认", ""])
        lines.extend(f"- {item}" for item in ir["unresolved"])
        lines.append("")
    return "\n".join(lines)


def render_coverage(ir: dict[str, Any]) -> str:
    lines = [
        f"# {ir['episode_id']} 原剧本覆盖表 v0.2",
        "",
        f"来源：`{ir['source_script']}`",
        "",
        "| 原剧本证据ID | 锁定内容 | 状态 | 覆盖镜头 | 说明 |",
        "|---|---|---|---|---|",
    ]
    for item in ir["source_coverage"]:
        lines.append(
            f"| {esc(item['source_ref'])} | {esc(item['description'])} | {esc(item['status'])} | "
            f"{joined(item['covered_by'])} | {esc(item['notes']) or '—'} |"
        )
    lines.extend(["", "> `covered`只证明Director IR有对应镜头，不证明生成结果已经通过人工视觉验收。", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ir", type=Path, required=True)
    parser.add_argument("--shot-script", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    args = parser.parse_args()
    ir = json.loads(args.ir.read_text(encoding="utf-8"))
    args.shot_script.parent.mkdir(parents=True, exist_ok=True)
    args.coverage.parent.mkdir(parents=True, exist_ok=True)
    args.shot_script.write_text(render_shot_script(ir), encoding="utf-8")
    args.coverage.write_text(render_coverage(ir), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
