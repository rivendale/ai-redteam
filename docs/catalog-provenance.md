# Catalog result provenance

> Dated context, October 22, 2026: Provenance record; missing pre-run metadata remains an explicit limitation, not a new result. See the [current navigation and records](README.md).


The plugin manifests were behind the current published redteam release. They now match. Published hold-out
observations are available for redteam, assess and the [paired lens comparison](https://github.com/rivendale/ai-redteam/blob/120f1fbbf2ca698419b1111e0177b507d568e757/evals/results/2026-10-22-week1021-lenses/README.md), but a `toolbox-result-1` claim also requires provenance that the
retained public run records do not establish.

| Required field | Public evidence | Status |
|---|---|---|
| Skill text / measured commit | [redteam gate](../evals/results/2026-10-09-gate-v232/README.md), [assess hold-out](../evals/results/2026-10-09-assess-holdout3/README.md) | Recorded version/commit references |
| Metrics and rule | The linked published tables and assess specification | Aggregate arithmetic can be checked; preserve as-run values |
| Actual run-start timestamp | The published records do not supply a verified run-start timestamp for this catalog claim | Unavailable; do not substitute a commit date, file timestamp or the date in a directory name |
| Public pre-run bar lock | The redteam record refers to an external decision; assess has a public Measure section | Unavailable as a verified public before-run lock |
| pr-review hold-out | [Held-text comparison](../evals/results/2026-10-08-prreview-held/README.md) has limited control evidence; the [lens aggregate](https://github.com/rivendale/ai-redteam/blob/120f1fbbf2ca698419b1111e0177b507d568e757/evals/results/2026-10-22-week1021-lenses/README.md) publishes paired planted-defect observations | The aggregate is not a qualifying catalog result: private registration and usage records do not establish the missing public pre-run provenance. |

The missing provenance prevents a passing machine-readable catalog result from being asserted here. The published gates can
be recomputed as observations without falsely labeling the record `toolbox-result-1`. The public record
does not currently establish the run-start and before-run rule evidence needed for that artifact. Future runs need actual run-start metadata and a verifiable earlier public rule commit. The missing evidence is not
proof that the experiments failed; it is a limit on the catalog claim.
