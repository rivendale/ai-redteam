# Maintained documentation audit, October 22, 2026

This pass changes navigation and presentation, not skill, prompt, scorer, runner or fixture behavior.
Historical reports, prompts, answer keys, raw usage, manifests and receipts are preserved byte-for-byte.
A dated observation remains an observation; merging candidate text does not establish a detection gain.

| Surface | Disposition and source |
|---|---|
| README opening and installation | Added a quick paste-in path and per-CLI routes. Codex `.agents/skills/` was checked against [official documentation](https://learn.chatgpt.com/docs/build-skills); the existing portable copy recipe and its [receipt](install-portable-receipt.json) remain the file-copy authority. Host loading is separate. |
| Worked example | An attributed excerpt from the [October 7 billing report](../evals/results/2026-10-07-pr9/pr-review-reports/case-10.md), including its missing-commit and missing-round caveats. No new model output. |
| Results and pending evaluation | Linked [October 16 variance](variance-2026-10-16.md), original release gates and [the October 22 comparison account](../evals/README.md#the-week-1021-lens-development-sets-added-2026-10-22). Development saturation, corrected controls, separate hold-outs and [mixed-model accounting](../evals/README.md#reviews-finished-by-a-different-model-added-2026-10-22) prevent a blanket improvement claim. Rule-ablation remains unrun, not scheduled. |
| Version and badges | [v2.3.2](https://github.com/rivendale/ai-redteam/releases/tag/v2.3.2) was published October 16, 2026. Plugin and marketplace versions still match 2.3.2. The badges point to that repository's existing checks workflow, LICENSE and latest release. No release or setting was changed. |
| CHANGELOG | Added an Unreleased inventory for every merged PR after the previous release-notes entry, through #96/#92. Kept as-run totals and later rescoring distinct. |
| Capabilities, AGENTS and llms.txt | Corrected the two-skill/version/schema descriptions; labelled 87 cases as the baseline suite, not all suites; repaired the stale README anchor. Linked each maintained fact to its owning guide or source. |
| Eval guide | Labelled baseline counts, removed the old 49-case command comment and reconciled the week-1021 pre-run status with its later comparison/corrections. Distinguished unchanged tracked hold-outs from the author-reported, unverified off-repository fixture-hygiene edit. No answer key or case was changed. |
| Eval-request pages | Moved seven requests under `eval-requests/`. Original URLs and headings remain forwarding stubs. Request status and frozen hashes are explicitly historical; they are not a current release gate. Skill references remain valid without editing skill bytes. |
| Specifications and framework mapping | Marked historical design/mapping context, preserving requirements and the October 8 source date. Gap labels from that mapping are not represented as a fresh inventory of main. |
| Agent/CLI guide and portable receipt | Kept historical CLI/version measurements dated. Native Codex paths are rechecked; old host-loader observations are not upgraded into current loading proof. |
| Action guide | [Implementation and boundary tests](pr-review-action.md) own the currently merged OSV, diagnostic, timeout and stop-reason details. One automated round is not a full High-tier review, and local tests are not provider-call evidence. |
| Catalog provenance | Kept missing pre-run lock/timestamp records explicit. A documentation refresh cannot create those records or a qualifying catalog claim. |
| Incident source snapshot | Kept vendor claims dated and linked its original unscored status to the later [development comparison](../evals/README.md#the-week-1021-lens-development-sets-added-2026-10-22). No vendor claim was remeasured. |
| Attack catalog and source credits | Preserved source links, dated vendor/research statements, observations versus claims and per-entry credits. No new threat-performance claim or fresh source measurement is implied. |
| Privacy checklist, workflow and review-method pages | Normative checklists retain their constraints. Statements such as 'verify current version' describe what a reviewer must do, not a claim that a live version was checked here. |
| Historical failure lists and offline JSON receipts | Remain dated evidence about their original work. They are not rewritten to imply fresh runs. The documentation index points to current maintained guides. |

## Link-check scope and denying control

The repository has no in-tree Markdown checker. Validation reuses the existing companion
`opensource/tools/check_links.py`, without copying or changing its implementation. It checks maintained
Markdown, skills, prompts and indexes. Frozen eval reports and synthetic inputs are excluded from the
navigation pass; the unrestricted baseline deliberately reports the missing chart in assess case-27.
That fixture stays unchanged.

Moving `week-1021-supply-chain-eval-request.md` without updating links made the checker exit 1 and name
the inbound link in `skills/pr-review/SKILL.md`. Restoring the page as a forwarding stub repairs it.
The separate baseline capabilities-to-README anchor was also repaired. The original first commit is the
[failure list](failures/polish-2026-10.md); validation details are recorded in the PR.

## Result-source boundary

The public comparison account supports 192 reviews and the no-gain conclusion. Exact requested
42/42 development and 27/29 hold-out aggregates are not in that public record as checked October 22.
They are omitted from the README until a public source can be cited; the draft PR tracks this remaining
source requirement. No private report, off-repository case or answer key is copied into the public repo.
