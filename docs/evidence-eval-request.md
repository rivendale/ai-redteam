# Evidence-check candidate: independent eval request

Status: proposed skill text, not scored or released. Existing published results apply to the previous text.
No new eval cases are authored in this PR. An independent eval author should supply the following coverage.

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
