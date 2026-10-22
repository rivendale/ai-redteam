# Catalog result provenance

> Dated context, October 22, 2026: Provenance record; missing pre-run metadata remains an explicit limitation, not a new result. See the [current navigation and records](README.md).


The plugin manifests were behind the current published redteam release. They now match. Published hold-out
observations are available for redteam and assess, but a `toolbox-result-1` claim also requires provenance that the
retained public run records do not establish.

| Required field | Public evidence | Status |
|---|---|---|
| Skill text / measured commit | [redteam gate](../evals/results/2026-10-09-gate-v232/README.md), [assess hold-out](../evals/results/2026-10-09-assess-holdout3/README.md) | Recorded version/commit references |
| Metrics and rule | The linked published tables and assess specification | Recomputable; preserve as-run values |
| Actual run-start timestamp | Usage records have duration/usage, but the runner does not retain a start timestamp | Unavailable; do not substitute a commit date, file timestamp or the date in a directory name |
| Public pre-run bar lock | The redteam record refers to an external decision; assess has a public Measure section | Unavailable as a verified public before-run lock |
| pr-review hold-out | [held-text comparison](../evals/results/2026-10-08-prreview-held/README.md) has a limited control comparison | `eval: {"none": "No qualifying independent hold-out result is published."}` |

The missing provenance prevents a passing machine-readable catalog result from being asserted here. The gate can
be recomputed as an observation without falsely labeling the record `toolbox-result-1`. The original run-start records are unavailable, so these historical runs cannot currently complete
that artifact. Future runs need actual run-start metadata and a verifiable earlier public rule commit. The missing evidence is not
proof that the experiments failed; it is a limit on the catalog claim.
