# Release notes

## Unreleased, documentation updated October 22, 2026

This inventory reconciles every first-parent PR merged since the prior release-notes entry,
including packaging work around v2.3.2 and later untagged changes. It does not declare a new skill release.

| Area | Changes and source PRs |
|---|---|
| Entry points and packaging guidance | Current three-skill README ([#74](https://github.com/rivendale/ai-redteam/pull/74)); portable Cursor/Copilot/Codex copies and receipts ([#70](https://github.com/rivendale/ai-redteam/pull/70)); dated README results correction ([#82](https://github.com/rivendale/ai-redteam/pull/82)); capability/install/result navigation updates ([#86](https://github.com/rivendale/ai-redteam/pull/86)). |
| Repeated-run evidence | Offline descriptive variance and regression controls ([#72](https://github.com/rivendale/ai-redteam/pull/72)); on-chain W1 development cases ([#76](https://github.com/rivendale/ai-redteam/pull/76)). Repeats are not new cases or rule-ablation evidence. |
| Evidence-check candidate | Independent development cases ([#77](https://github.com/rivendale/ai-redteam/pull/77)), evidence-limit/weak-evaluator cases ([#78](https://github.com/rivendale/ai-redteam/pull/78)), case-16 floor correction ([#79](https://github.com/rivendale/ai-redteam/pull/79)) and candidate skill text ([#71](https://github.com/rivendale/ai-redteam/pull/71)). Existing release results do not certify changed text. |
| Supply-chain review | Initial development cases ([#81](https://github.com/rivendale/ai-redteam/pull/81)), behavioral lens ([#80](https://github.com/rivendale/ai-redteam/pull/80)), limited safety-stop comparison ([#83](https://github.com/rivendale/ai-redteam/pull/83)), explicit model selection in the runner ([#84](https://github.com/rivendale/ai-redteam/pull/84)), more independent development cases ([#85](https://github.com/rivendale/ai-redteam/pull/85)). |
| October 21 incident lenses | Supply chain ([#87](https://github.com/rivendale/ai-redteam/pull/87)), secrets placement ([#88](https://github.com/rivendale/ai-redteam/pull/88)), runtime/TLS trust ([#89](https://github.com/rivendale/ai-redteam/pull/89)), self-hosted exposure ([#90](https://github.com/rivendale/ai-redteam/pull/90)) and authorization pretexts/refusal fallback ([#91](https://github.com/rivendale/ai-redteam/pull/91)). The [incident map](docs/incidents/2026-10-21-week.md) separates sources from review inferences. |
| Independent evaluation | Development sets, corrected controls and separated injection cases ([#92](https://github.com/rivendale/ai-redteam/pull/92)); [published 192-review aggregate](https://github.com/rivendale/ai-redteam/blob/120f1fbbf2ca698419b1111e0177b507d568e757/evals/results/2026-10-22-week1021-lenses/README.md) ([#105](https://github.com/rivendale/ai-redteam/pull/105)) established no measurable lens gain and exposed model-fallback accounting limits. |
| Bounded PR Action | Opt-in, trusted-base workflow ([#73](https://github.com/rivendale/ai-redteam/pull/73)); safe fixed diagnostics ([#93](https://github.com/rivendale/ai-redteam/pull/93)); deterministic OSV lookup independent of the model ([#94](https://github.com/rivendale/ai-redteam/pull/94)); larger output budget, bounded timeout and stop reasons ([#95](https://github.com/rivendale/ai-redteam/pull/95)). |
| Model attribution | Per-review producer/token records, safety-stop warnings and correct unpinned mixed-model detection ([#96](https://github.com/rivendale/ai-redteam/pull/96)). Mixed-model reviews are separate evidence, not pure pinned-model results. |
| Documentation polish in this PR | Two-minute opening, sourced worked example, CLI paths, dated results, badges and review-flow diagram; docs/evaluation-request indexes with legacy URL stubs; dated stale-content audit. No skill, prompt, scorer, runner, fixture or manifest behavior changes. |

<a id="plugin-232-prepared-tag-created-by-the-maintainer-after-review"></a>

## Plugin 2.3.2 (released October 16, 2026)

The plugin bundles redteam, assess and pr-review. The plugin version follows the released redteam text;
individual skill names and evaluation versions are distinct. This change updates manifests and documentation,
not any skill body. The maintainer subsequently published [v2.3.2](https://github.com/rivendale/ai-redteam/releases/tag/v2.3.2) on October 16, 2026. The original gate totals below are preserved.

### redteam

The shipped text is **redteam v2.3.2**. Its gate compared against **v2.2**, with each set evaluated separately.
All values below are the published as-run totals across the repeated runs, not fresh model output.

| Set | Candidate recall | Baseline recall | Candidate / baseline false alarms | Candidate / baseline violations | Source |
|---|---|---|---|---|---|
| Development | 240 / 252 | 235 / 252 | 8 / 11 | 39 / 61 | [gate record](evals/results/2026-10-09-gate-v232/README.md) |
| Hold-out | 53 / 60 | 56 / 60 | 3 / 4 | 8 / 17 | [gate record](evals/results/2026-10-09-gate-v232/README.md) |

The published gate requires recall no lower than baseline minus three, no increase in control false alarms,
and violations at most three-quarters of baseline when baseline is at least eight. Recomputing these rules
passes both sets; hold-out recall is exactly at its floor. The rule and the smaller-baseline exception are in
[the same gate record](evals/results/2026-10-09-gate-v232/README.md).

The [record](evals/results/2026-10-09-gate-v232/README.md) distinguishes development tuning from hold-out evaluation
and explains location-alias/scorer effects. The [later scorer account](evals/README.md)
is a re-score of the same reports, not a new skill run. Do not silently replace the original gate totals.

### assess

The bundled **assess v1.3** has an as-run hold-out result of **106 / 108**, with run totals **36, 35, 35**.
Controls passed in every run and the published rule-level floor was met. The corrected scorer gives
**36, 36, 36** on those same reports; that correction is not a new independent hold-out.
Source for the versions, counts, gate and limitations: [assess hold-out record](evals/results/2026-10-09-assess-holdout3/README.md).

### pr-review

The bundled pr-review text adds targeted reading of accepted fixes. Its [held-text comparison](evals/results/2026-10-08-prreview-held/README.md)
reports no control false alarms or violations in the limited repeated comparison. The record explicitly says
that this does not demonstrate a detection benefit. It has no qualifying independent hold-out catalog claim.

### Catalog and outstanding work

Manifest versions now agree. [Catalog provenance](docs/catalog-provenance.md) separates the published observations
from the metadata still required for a verifiable catalog result. No timestamps or pre-run lock commits have been
invented. No paid evaluations were run for this release-notes change. Rule-ablation remains pending, rather than
being inferred from repeated observations of a complete skill.
