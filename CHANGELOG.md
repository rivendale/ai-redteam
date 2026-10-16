# Release notes

## Plugin 2.3.2 (prepared; tag created by the maintainer after review)

The plugin bundles redteam, assess and pr-review. The plugin version follows the released redteam text;
individual skill names and evaluation versions are distinct. This change updates manifests and documentation,
not any skill body. It does not create a release tag.

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
