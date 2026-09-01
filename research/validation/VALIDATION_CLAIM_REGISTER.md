# Validation Claim Register

Updated: 2026-09-01

Status: `PHASE_1_PASS / INDEPENDENT_READ_ONLY_REVIEW_PASS`

This register is the reproducible source for current numerical pass claims. A
command is evidence only for the boundary named in its row. Structural checks do
not prove that the source-film observations are correct, do not directly audit
sound, and do not constitute creative approval.

| Claim | Reproduction command | Versioned evidence | Current result | Boundary |
|---|---|---|---|---|
| Closed conversion is deterministic | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/convert_legacy_scene_evidence.py --check` | `convert_legacy_scene_evidence.py` and its tests | PASS — 30 scenes, 2,255 Shot/edit units, 120 candidate identities | Proves generated JSON equals the conservative legacy conversion; does not replay media |
| Generated review Markdown is deterministic and round-trippable | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/render_scene_evidence.py --check` | `render_scene_evidence.py`, 30 `*.scene-evidence.generated.md` files and renderer tests | PASS — 30/30 generated files | Proves generated review fields equal canonical JSON and re-render identically |
| Legacy Markdown is not overwritten by rendering | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest skills/drama-director-compiler/tests/test_render_scene_evidence.py -v` | Renderer non-overwrite regression | PASS | Compares all existing Markdown before and after temporary rendering |
| Current repository unit/CLI behavior | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/drama-director-compiler/tests -v` | Four versioned test modules | PASS — 77 tests | Covers the current repository test surface; not source replay or audience evaluation |
| Canonical Scene Evidence structure | `PYTHONDONTWRITEBYTECODE=1 python3 skills/drama-director-compiler/scripts/validate_scene_evidence.py research/evidence --quiet` | Validator `scene-evidence-validator/0.1` and `scene-evidence-validation.json` | PASS_STRUCTURAL — 30 passed, 0 failed, 0 errors, 69 warnings | Warnings remain visible; no direct semantic-audio claim is added |
| Scene Evidence schema syntax | `python3 -m json.tool skills/drama-director-compiler/references/scene-evidence.schema.json` | Scene Evidence schema | PASS | JSON syntax only |
| Versioned validation report syntax | `python3 -m json.tool research/validation/scene-evidence-validation.json` | Structural validation report | PASS | JSON syntax only |
| Current task/status authority contract | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest skills/drama-director-compiler/tests/test_phase1_state_contract.py -v` | Approved task card, compact STATE, catalog headers and checklist | PASS — 4 tests | Does not complete planned rule artifacts |
| Whitespace | `git diff --check` | Current local change set | PASS | Tracked textual diff only |

## Independent Phase 1 review

`research/validation/PHASE_1_INDEPENDENT_AUDIT.md` records the fresh
non-writing review. It independently reproduced the 77-test suite, renderer and
converter checks, structural validation, non-overwrite boundary and artifact
scans against the frozen Phase 1 snapshot.

## Claims not yet authorized

- No candidate is an executable cross-work rule.
- No runtime Director Grammar, routing, forward-test or CI pass is claimed.
- No source media, semantic audio, creative quality or audience effect has been
  revalidated by these commands.
- No remote PR state has been changed by this phase.
