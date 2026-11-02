# Release notes

## Unreleased, November 2, 2026: security-audit findings mapping

No skill or prompt text changed. No paid evaluation was run.

| Area | Change |
|---|---|
| Findings mapping | [`tools/map_audit_findings.py`](tools/map_audit_findings.py) converts a Cloudflare security-audit `findings.json` array into a schema 2.3 report. The field table is [`docs/security-audit-mapping.md`](docs/security-audit-mapping.md). Tests: [`tests/test_map_audit_findings.py`](tests/test_map_audit_findings.py). |

## Unreleased, October 31, 2026: eval statistics, pre-registration, doc drift, statistical gate rule

No skill or prompt text changed. No paid evaluation was run.

| Area | Change |
|---|---|
| Eval statistics | `evals/tools/stats.py`: 95% intervals for recall and false-alarm rate clustered by case, a paired case bootstrap and an exact sign test between two texts, and a self-check that the offline checks workflow runs. Method, commands and what the v2.3.2 hold-out gate looks like with it: [evals/README.md](evals/README.md#error-bars-and-paired-comparisons-evalstoolsstatspy-added-2026-10-31). |
| Gate re-read | `stats.py compare` run on the published v2.3.2 gate reports: no detectable difference on either set, and the 3-hit floor is inside both intervals. Table, commands and a note on few-cluster bootstraps: [evals/README.md](evals/README.md#error-bars-and-paired-comparisons-evalstoolsstatspy-added-2026-10-31). The v2.3.2 gate record stays as run. |
| Pre-registration | `run_reviews.sh` writes `_meta/prereg.json` (skill and case-input hashes, model, CLI version, gate rule, UTC start) before the first review; `DRY_RUN=1` stops after it; `tests/test_run_reviews_prereg.py` tests it with a stub CLI. See [evals/README.md](evals/README.md#pre-registration-added-2026-10-31). |
| Gate rule | Recall and false alarms are now gated by an interval test with pre-registered margins (approved by the maintainer); past gate records keep their rule. The rule, its units and `stats.py gate`: [evals/README.md](evals/README.md#gate-rule). |
| Eval statistics warnings | `stats.py` prints a WARNING (also in `--json`) when an interval rests on fewer than 10 clusters, and WEAK EVIDENCE instead of SIGNIFICANT when the bootstrap and the exact sign test disagree (the plain-prompt hold-out false-alarm drop). Self-check extended. |
| Summed-hit interval | The interval of the summed-hit difference is now bootstrapped directly; it used to scale the rate interval by the planted count, which is wrong when cases plant different numbers of defects. The v2.3.2 re-read moves from [-5.0, +3.3] to [-6.0, +3.0] hits (hold-out) and from [-3.6, +15.7] to [-4.0, +16.0] (development). |
| Codex pre-registration | `run_reviews_codex.sh` writes the same `_meta/prereg.json` as `run_reviews.sh`, through the shared `evals/tools/prereg.py`, before it copies the sign-in; `GATE_MARGIN` and `GATE_FA_MARGIN` record the margins in both, and a resume is refused when the runner's bytes, `prereg.py`, `prepare.py` or the gate rule or margins changed. Tested with a stub `codex` in `tests/test_run_reviews_prereg.py`. |
| `DRY_RUN` | `DRY_RUN=0` (or `false`, `no`, `off`, empty) now means off in both runners; it used to turn the dry run on. Any other value is refused. |
| Test stubs | The stub CLIs' heredocs in the lane tests are quoted, so nothing in them expands. |
| Hygiene check | `.github/workflows/hygiene.yml` calls the shared hygiene workflow of rivendale/opensource at a pinned commit; `.hygiene.json` configures it (executable bits, invisible characters outside the case 62/63 fixtures and the recorded prompts that quote them or embed raw `.pyc` bytes, the baseline, assess and hold-out case counts, stale dated markers, the `AGENTS.md` size and sentinel, and the symlink-refusal test as root). See [docs/capabilities.md](docs/capabilities.md). |
| Doc drift | `AGENTS.md`, `README.md`, `llms.txt` and `docs/capabilities.md` no longer restate SPEC's version range or item count; they point to [docs/SPEC.md](docs/SPEC.md), which owns them. |
| Framework mapping | [docs/framework-mapping.md](docs/framework-mapping.md): LLM05, LLM07, LLM10, ASI05 and ASI09 now covered and LLM08, ASI08 partial, each with its skill section; ATLAS agent-tool and propagation techniques from the 2026.10 data release; the OWASP LLM 2026 list is marked unverified. |

### Open: skill sections marked "This candidate is unscored"

AGENTS.md rule 3 says no unscored change to a skill ships, yet these sections are in the skill text on main. Each has an
independent eval request and development cases; none has a scored, gated comparison. Owner: whoever runs the next gated
evaluation of each lens (or removes the section). Close a row by linking its gate record.

| Skill section | Eval request | Development cases |
|---|---|---|
| redteam, "Secrets placement and rotation" | [secrets](docs/eval-requests/week-1021-secrets-eval-request.md) | `evals/secrets/cases` |
| redteam, "Self-hosted service exposure" | [exposure](docs/eval-requests/week-1021-exposure-eval-request.md) | `evals/exposure/cases` |
| redteam, "Authorization pretexts and refusal fallback" | [pretext](docs/eval-requests/week-1021-pretext-eval-request.md) | `evals/pretext/cases` |
| pr-review, "Release age, install hooks and credential egress" (under "Dependency, plugin and update-payload changes") | [supply chain](docs/eval-requests/week-1021-supply-chain-eval-request.md) | `evals/supplychain/cases` |
| pr-review, "Runtime and TLS trust changes" | [runtime trust](docs/eval-requests/week-1021-runtime-trust-eval-request.md) | `evals/runtime/cases` |

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
