# Evidence-check candidate: independent eval request

> Historical evaluation request. Its status and frozen hashes describe the original request date, not current main. For October 22, 2026 observations and limits, see the [results overview](../../README.md#results) and [dated audit](../stale-audit-2026-10-22.md).


Status: candidate text frozen on 2026-10-19 UTC; skill performance remains unscored and unreleased.
Existing published results apply to the previous text. No new eval cases are authored in this PR.

The independently authored DEV set is now on main at `292b80b8d82131b059ab80051680a21ff170fea2` under
`evals/evidence/cases/`: 14 cases and 8 controls. All 14 case proofs pass and reviewer input preparation
excludes the answer keys. [Offline validation](../evidence-dev-validation.json) records the exact checks,
including five full-self-check failures caused by absent suite categories. Answer-constructed mock scores
validate the scorer only; they do not evaluate this skill or establish a gain over baseline.

Frozen `skills/redteam/SKILL.md` SHA-256: `434ac9d54b888884a6fd2e1cd60fe4d1c22f645b17b64b301b4d00eb10d1495f`. The text was unchanged after DEV access.
The owner performs the independent model comparison and host-only hold-out scoring. The coverage request remains:

| Failure area | Needed defect | Needed clean control |
|---|---|---|
| Unsupported quantity | A load-bearing figure has no supplied source or derivation | The figure recomputes from supplied inputs |
| Inconsistent comparison | A changed cohort, denominator, baseline, unit or time window drives the claim | Both sides use a stated comparable basis |
| Overclaiming | Correlation, a tuned set or a small observation is sold as a general/causal result | The conclusion stays within the supplied evidence |
| Reward hacking | A change weakens a threshold/assertion, leaks answers or hardcodes the expected result | The implementation improves real behavior, or a justified evaluator repair is independently supported |
| Evidence limits | An unavailable citation is treated as confirmed support or a confirmed falsehood | The exact unresolved fact is named without fabricated support or automatic severity inflation |

Use the existing finding states, severity questions, coverage ledger and schema. Include controls that would expose
blanket warnings. Keep answer keys out of reviewer prompts. The skill author must not grade extra findings.

Before merge, score this exact candidate against the published baseline and the independently authored additions.
Report recall, false alarms and violations with unchanged comparison rules. New model calls require separate
operator authorization; none were made while preparing this candidate.

Inspiration: [Sakana AI, The Agentic Scientist](https://pub.sakana.ai/agentic-scientist/). This candidate uses an
explicit claim/source map and an evidence audit. It does not assert a measured gain before evaluation.
