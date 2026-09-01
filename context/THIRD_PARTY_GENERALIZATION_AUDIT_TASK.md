# Existing 33-Source Generalization Completion Task

Updated: 2026-09-01

Status: `ACTIVE / USER_APPROVED`

## Task name

Turn the existing 33-source research corpus into a verifiable, safely routable DirectorMind grammar without adding reference works.

## Why this work exists

The closed corpus already has 33 explicit source dispositions. Thirty current-local analyses have deterministic Scene Evidence JSON containing 2,255 Shot/edit units and 120 non-operational legacy candidate lineages. One *Succession* analysis remains isolated in the older PR, and two other sources retain explicit non-integration dispositions.

The remaining problem is not acquisition. The repository cannot yet decide reproducibly which candidate logic is supported across unrelated works, when it is inapplicable, how conflicts are resolved, or which rules may safely enter runtime routing. The existing candidate rows are research lineage, not executable directing instructions.

## Expected result

Given a rights-safe original scene description, DirectorMind can identify the scene problem, select no more than two to four eligible rules, explain why each applies, and reject rules that are merely similar in subject matter. When no rule passes the evidence and applicability gates, the correct result is `NO_APPLICABLE_RULE`; the system must not promote or invent a rule to satisfy a count.

The final repository contains a deterministic Scene Evidence renderer, normalized candidate index, cross-work support matrix, promotion gates, Director Grammar v0.2, routing logic, original positive and non-applicable tests, clean *Succession* integration, automated checks, final validation evidence, and a fresh read-only review by an agent that did not write the reviewed phase.

Checklist completion measures whether the contracts, validators, routing and honest blocked outcomes are implemented. It does not require a minimum number of promoted rules. A candidate may correctly remain `BLOCKED_BY_UNKNOWN` while the corresponding checklist requirement is `VERIFIED_DONE` because the blocking behavior has been proved.

## In scope

### Phase 1 — One fact source and truthful status

- Add deterministic `render_scene_evidence.py` and round-trip/determinism tests.
- Keep all legacy Markdown immutable. Render only to a separate `*.scene-evidence.generated.md` path or a caller-supplied output directory.
- Remove stale or contradictory validation claims.
- Reduce `context/STATE.md` to phase, counts, blockers, latest validation, next step and authoritative links.
- Mark acquisition and coverage files as catalogs rather than competing completion authorities.

### Phase 2 — Candidate normalization and promotion gates

- Add evidence-backed abstract roles and canonical scene-problem classification without converting UNKNOWN into fact.
- Add the Candidate Rule Schema, three separate confidence dimensions, a 120-lineage candidate index, and deterministic JSON/Markdown cross-work support matrices.
- Enforce the allowed promotion states and the single-work, cross-work, general-default, UNKNOWN, counterexample and human-review gates.

### Phase 3 — Runtime grammar and routing

- Add Director Grammar v0.2 containing only eligible rules and project/safety constraints.
- Update `drama-director-compiler` routing, conflict priority and misuse guards.
- A valid grammar may contain zero promoted evidence rules when the corpus does not satisfy promotion gates.

### Phase 4 — Rights-safe original tests

- Add original positive and non-applicable cases for every promotion-ready family.
- Exercise the real routing path and retain unreviewed creative output at `HUMAN_REVIEW_PENDING`.
- Always include a `NO_APPLICABLE_RULE` case.

### Phase 5 — Existing *Succession* evidence

- Preserve the completed rule that the old PR must never be merged unchanged.
- Migrate the existing 88-shot evidence through the current Scene Evidence, candidate-index and support-matrix contracts.
- Resolve the old scene-problem-map conflict through the current route.
- Do not close the old PR without a separate explicit user confirmation after successful local integration is shown.

### Phase 6 — Automated checks and delivery

- Add local automation and a minimal CI definition for the repository contracts.
- Produce final validation JSON and a checked-in independent audit report.
- Present the finished local branch and all remaining risks to the user before any remote action.

## Out of scope

- No new film, episode, reference work, download, source selection or corpus expansion.
- No re-distillation of the completed 30 current-local analyses unless a failing test proves a narrow correction is necessary.
- No direct semantic-audio campaign; unauditioned audio remains blocked.
- No provider prompt, paid model call, generated image/video/audio, product-page work or audience-performance claim.
- No modification of the private 36-episode locked scripts or private Director IR.
- No deletion, move, rename, trim, transcode or replacement of source media.
- No deployment, production change, database change, account or permission change, credential handling, payment or public release.
- No push, PR closure or merge without the separate authorization gates below.

## Protected content and systems

- Never commit source video/audio, stills, contact sheets, subtitles, scripts, long dialogue, raw release labels, local media paths, credentials, cookies, signed URLs or personal data.
- Never overwrite or delete the 30 legacy evidence Markdown documents. They remain migration provenance, not the active machine fact source.
- Reference characters, costumes, locations, props, dialogue, signature compositions and scene events may remain only in evidence lineage when necessary; they must never become operational generation instructions.
- Legacy candidate rows cannot enter runtime routing until every promotion gate passes.
- Structural validation is not creative approval, production authorization or proof of audience performance.

## External-action authorization gates

Approval of this task card authorizes only local, reversible repository work and local tests.

- First push to PR #3 requires a new explicit user confirmation after the exact local changes and checks are shown. That confirmation may cover later corrective pushes to the same branch during this Goal, but never a merge.
- Closing PR #1 requires a separate explicit user confirmation after the 88-shot evidence is integrated and validated locally.
- Merging `main`, deployment, publication, media deletion, or any production/account/permission/payment action always requires a separate explicit confirmation.

## Execution order and stop gates

1. Refresh the current local and remote baseline before relying on old status text; do not leave the current branch.
2. Complete Phase 1 before candidate normalization.
3. Complete scene-problem, role, candidate and promotion gates before writing runtime grammar.
4. Complete grammar and routing before forward tests.
5. Integrate *Succession* only through the current contracts, never by merging the old PR unchanged.
6. Run local validation before adding CI and final reports.
7. Use a fresh read-only agent that did not write the reviewed phase for final acceptance.
8. Stop after the local branch is complete and present external actions for user decision.

If evidence is insufficient, keep the candidate blocked and continue with the remaining safely completable work. If a requirement genuinely cannot be implemented without expanding scope, report it as a user decision boundary; do not fabricate completion. If two consecutive work waves produce no new verified requirement or risk reduction, stop and re-plan.

Only one writer may own a mutable file at a time. Root is the sole accountable integrator.

## Completion criteria

- [ ] Existing users receive correct rule selection or `NO_APPLICABLE_RULE` for original scenes.
- [ ] The 30 canonical JSON units remain deterministic at 2,255 Shot/edit units and 120 source candidate identities unless an independently proven discrepancy is approved.
- [ ] The renderer is deterministic, round-trippable and incapable of overwriting legacy Markdown.
- [ ] All 120 source candidate IDs resolve exactly once in the Candidate Rule Index.
- [ ] Candidate schema, confidence dimensions, support relations, contrary evidence and promotion gates validate.
- [ ] UNKNOWN audio, functional roles and natural-scene boundaries cannot leak into promoted rules.
- [ ] Director Grammar v0.2 contains only eligible rules and no reference-work surface instructions.
- [ ] Routing selects no more than two to four eligible rules and rejects merely similar or non-applicable rules.
- [ ] Every promotion-ready family has original positive and non-applicable tests; no-ready-family and no-applicable-rule outcomes are also tested.
- [ ] Unreviewed creative outputs remain `HUMAN_REVIEW_PENDING`.
- [ ] Legacy Markdown and original media remain unchanged.
- [ ] *Succession* is integrated through the current contracts without merging the old PR.
- [ ] Existing and new local tests pass; CI is defined but no push occurs without confirmation.
- [ ] Final validation records zero contract errors and preserves all warnings.
- [ ] A non-writing read-only agent issues the final technical verdict and lists unverified boundaries.
- [ ] Final delivery includes changes, behavioral evidence, check results, remaining risks, external side effects, resource use and rollback.

## Current status

- Current accountable implementer: root agent, sole integrator. No other writer may edit the same mutable file concurrently.
- Completed: first-party closed-corpus task and Phase 1; 22/57 generalization-checklist requirements.
- Not completed: 35/57 requirements covering roles/problems, candidate index/matrix, promotion gates, grammar, routing, forward tests, *Succession*, automated checks and final audit.
- Current validation: 30 Scene Evidence JSON files; 2,255 Shot/edit units; 120 non-operational candidate lineages; 77 tests passing including Phase 1; 30/30 structural passes; zero errors; 69 visible warnings.
- Known boundaries: all current scene problems remain UNKNOWN; direct semantic audio is absent; no candidate is yet authorized as an executable cross-work rule.
- Remote boundary: no push, PR closure or merge is authorized by this card.
- Next single action: create the isolated local Phase 1 commit, then begin candidate normalization and promotion gates.

## Rollback

Use one isolated local commit per verified phase on `codex/macos-first16-local-batch`. Before each phase commit, review the exact changed paths and run the smallest complete checks. Correct a local or later pushed phase with a normal revert or follow-up commit; never rewrite shared history. Generated review files may be discarded without touching canonical JSON, legacy Markdown or source media.
