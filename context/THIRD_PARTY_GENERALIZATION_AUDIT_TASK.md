# Existing 33-Source Generalization Completion Task

Updated: 2026-09-02

Status: `FINAL_INDEPENDENT_REVIEW_IN_PROGRESS / REMOTE_IMPLEMENTATION_CI_PASSED`

Compatibility repair status: `LOCAL_COMPLETE / INDEPENDENT_READ_ONLY_REVIEW_PASS`

## Task name

Turn the existing 33-source research corpus into a verifiable, safely routable DirectorMind grammar without adding reference works.

## Why this work exists

The closed corpus has 33 explicit source dispositions. Thirty-one current-local analyses now have deterministic Scene Evidence JSON containing 2,343 Shot/edit units and 124 non-operational legacy candidate lineages. The existing *Succession* analysis has been migrated through the current contracts without merging the older PR; two other sources retain explicit non-integration dispositions.

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
- No merge, deployment, publication, media deletion or other production/account action under the bounded PR authorization below.

## Protected content and systems

- Never commit source video/audio, stills, contact sheets, subtitles, scripts, long dialogue, raw release labels, local media paths, credentials, cookies, signed URLs or personal data.
- Never overwrite or delete the 30 legacy evidence Markdown documents. They remain migration provenance, not the active machine fact source.
- Reference characters, costumes, locations, props, dialogue, signature compositions and scene events may remain only in evidence lineage when necessary; they must never become operational generation instructions.
- Legacy candidate rows cannot enter runtime routing until every promotion gate passes.
- Structural validation is not creative approval, production authorization or proof of audience performance.

## External-action authorization gates

The user expanded this task's bounded authorization on 2026-09-02:

- Pushes and corrective pushes to the existing PR #3 branch are authorized for this Goal.
- Closing PR #1 is authorized after the 88-shot evidence is integrated, local validation passes and PR #3 CI passes.
- Merging `main`, deployment, publication, media deletion, or any production/account/permission/payment action remains prohibited without a separate explicit confirmation.

## Execution order and stop gates

1. Refresh the current local and remote baseline before relying on old status text; do not leave the current branch.
2. Complete Phase 1 before candidate normalization.
3. Complete scene-problem, role, candidate and promotion gates before writing runtime grammar.
4. Complete grammar and routing before forward tests.
5. Integrate *Succession* only through the current contracts, never by merging the old PR unchanged.
6. Run local validation before adding CI and final reports.
7. Use a fresh read-only agent that did not write the reviewed phase for final acceptance.
8. Push the verified result to PR #3, require final CI success, close PR #1, run the final independent read-only review, then stop for the user's merge decision.

If evidence is insufficient, keep the candidate blocked and continue with the remaining safely completable work. If a requirement genuinely cannot be implemented without expanding scope, report it as a user decision boundary; do not fabricate completion. If two consecutive work waves produce no new verified requirement or risk reduction, stop and re-plan.

Only one writer may own a mutable file at a time. Root is the sole accountable integrator.

## Completion criteria

- [x] Existing users receive correct rule selection or `NO_APPLICABLE_RULE` for original scenes; the current zero-eligible grammar truthfully returns `NO_APPLICABLE_RULE` for all eight original cases.
- [x] The original 30 legacy Markdown sources remain unchanged; their canonical JSON is regenerated only by the deterministic converter, including narrow boundary/UNKNOWN corrections required by the stricter Phase 1 validator. The existing *Succession* ledger adds exactly 88 Shot units and four blocked candidate identities for a deterministic 31 / 2,343 / 124 current total.
- [x] The renderer is deterministic, round-trippable and incapable of overwriting legacy Markdown.
- [x] All 124 source candidate IDs resolve exactly once in the Candidate Rule Index.
- [x] Candidate schema, confidence dimensions, support relations, contrary evidence and promotion gates validate.
- [x] UNKNOWN audio, functional roles and natural-scene boundaries cannot leak into promoted rules.
- [x] Director Grammar v0.2 contains only eligible rules and no reference-work surface instructions.
- [x] Routing selects no more than two to four eligible rules and rejects merely similar or non-applicable rules.
- [x] Every promotion-ready family has original positive and non-applicable tests; no-ready-family and no-applicable-rule outcomes are also tested.
- [x] Unreviewed creative outputs remain `HUMAN_REVIEW_PENDING`.
- [x] The original 30 legacy Markdown documents and original media remain unchanged; the migrated *Succession* input is a sanitized rights-safe ledger.
- [x] *Succession* is integrated through the current contracts without merging the old PR.
- [ ] Existing and new local tests pass and the final PR #3 head passes the defined remote CI workflow.
- [x] Final validation records zero contract errors and preserves all warnings.
- [ ] A non-writing read-only agent issues a fresh verdict on the final integrated state and lists unverified boundaries.
- [x] Final delivery package includes changes, behavioral evidence, check results, remaining risks, external side effects, resource use and rollback.

## Approved post-completion compatibility repair

A later independent audit found four narrow gaps in the completed local implementation. The user approved the repair on 2026-09-01 without reopening corpus acquisition; the later 2026-09-02 authorization above governs the bounded PR actions:

1. use one canonical `scene_problem` enum across Scene Evidence, candidate, Grammar, routing input/result, Director IR, and forward-test schemas;
2. preserve GO-01/GO-07 trigger validation only for legacy Grammar v0.1 and prevent those seed rules from entering Grammar v0.2;
3. make every Grammar v0.2 scene carry the complete formal `routing_result` and prove exact selected-rule-to-Shot binding;
4. split the v0.1-to-v0.2 upgrader into an honest legacy-compatible pause and an evidence-complete routed mode, while rendering legacy audio visibly instead of dropping or guessing it.

This repair may change only the affected schemas, the router and Grammar validator needed to enforce the canonical negative sentinel, the Director IR validator/renderer/upgrader, routing fixtures, regression tests, deterministic derived evidence required by the stricter validator, current validation reports, and truthful status/contract documentation. These edits enforce the already approved contracts; they do not add rules or change corpus conclusions. The repair does not authorize new reference works, re-distillation, media or private-IR access, source deletion, production, database, account, permission, key, payment, deployment, publication, or merging `main`.

Repair completion requires targeted compatibility tests, the full local suite, the 18-check repository runner, an updated strict final report, and a new read-only review by agents that did not write the repair. The repair must preserve the existing 33/31/2,343/124/16/0 corpus and runtime counts.

## Current status

- Current accountable implementer: root agent, sole integrator. No other writer may edit the same mutable file concurrently.
- Completed: all implementation phases are present locally; the stricter Phase 1 repair has been integrated with the later closed-corpus work.
- Remaining: obtain the fresh independent read-only verdict, update the final evidence, push the final documentation head and require its hosted CI success.
- Current validation: the integrated Scene validator passes 100/100 tests, the corrected converter passes 13/13 tests on Python 3.9 and 3.12, the complete suite passes 223/223, all 18 local repository checks pass, and the PR #3 implementation head passes hosted CI.
- Known boundaries: all current scene problems remain UNKNOWN; direct semantic audio is absent; no candidate is yet authorized as an executable cross-work rule.
- Remote boundary: PR #3 push and PR #1 closure are authorized in the order above. Merging `main` and all deployment/publication/production actions remain prohibited.
- Next single action: run the fresh independent read-only final review; then record its verdict and validate the final documentation head.

## Rollback

Use one isolated local commit per verified phase on `codex/macos-first16-local-batch`. Before each phase commit, review the exact changed paths and run the smallest complete checks. Correct a local or later pushed phase with a normal revert or follow-up commit; never rewrite shared history. Generated review files may be discarded without touching canonical JSON, legacy Markdown or source media.
