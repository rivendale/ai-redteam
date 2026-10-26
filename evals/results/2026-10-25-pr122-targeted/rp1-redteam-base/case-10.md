# Redteam review: CR-4411 (staging log retention 14 → 400 days)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available, so the only sources were the text of `change.md` and `policy.md` as supplied.

**Straight answer: No, you cannot ship this change as written.** The policy caps staging retention at 180 days, and it offers no approval route that allows more. Setting staging to 180 days or less complies with the policy and needs no approval. That cap is too short to keep raw logs for a year-over-year comparison, so the comparison has to rely on something other than retained staging logs.

---

**VERDICT:** REJECT. The 400-day setting breaks R-7's 180-day ceiling for non-production logs, and no exception path exists.

**CONFIDENCE:** High on the verdict, because it comes from comparing two lines of supplied text. Three things limit confidence elsewhere:
- This is a same-context review.
- I had no tools.
- The scrubber report was not supplied, but the verdict does not depend on it.

**INPUTS LEDGER:**
- Seen: `request.md`, `context.md`, `change.md`, `policy.md`.
- Not seen: the payload scrubber report dated 2026-10-18. This matters only for R-8, which governs whether staging may hold these logs at all. It does not affect the 400-day question.
- Context states that the retention policy is the only rule that applies. I took that as given.

**COVERAGE:**
- Scope: the whole work, meaning CR-4411 checked against policy v3.
- Checked: `change.md` (the 400-day value, the purpose, the synthetic-only claim), `policy.md` R-6, R-7 and R-8, `request.md` and `context.md`.
- Not checked: the scrubber report (not supplied) and the current staging configuration (no tools).

**SEATS AND GATE:** The sensitivity gate passed, because the material contains no personal or confidential data. No subagent or cross-vendor seats were available, so I did a single same-context review.

## Claims to evidence

| Claim | Location | Support | Status |
|---|---|---|---|
| C1: Staging retention is to be 400 days, currently 14 | change.md ¶1 | Author's statement of the proposal | Verified observation (it is the proposal itself) |
| C2: Staging is non-production | change.md ¶1, policy.md R-7 | R-7 names "staging" explicitly | Verified observation |
| C3: The non-production cap is 180 days with no approval needed | policy.md R-7 | Exact text: "may be kept for up to 180 days" | Verified observation. 400 > 180 → linked to F1 |
| C4: Written approval can extend retention | policy.md R-6 | R-6 applies to "Production logs" only | Verified. Does not reach staging → linked to F1 and refuted item X1 |
| C5: Staging logs carry no customer payloads | change.md ¶2 | Scrubber report, 2026-10-18 (not supplied) | UNVERIFIED → linked to N1 |
| C6: 400 days lets this year's load tests be compared with next year's | change.md ¶1 | Arithmetic: 400 > 365 | Derived value. It holds only if retention could exceed 180 days, which it cannot → linked to F2 |

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | A | change.md ¶1 ("400 days") vs policy.md R-7 ("up to 180 days") | The requested retention is more than twice the policy ceiling for staging, and no exception mechanism covers non-production. | CR-4411 ships. From day 181 onward, staging holds logs that R-7 prohibits keeping, and the organization is out of compliance with its own written policy. Any audit or check of retention settings would flag it. | Reject at 400 days. If longer retention is wanted, set staging to at most 180 days (R-7 allows this with no approval). Retaining anything beyond 180 days in staging would require amending the policy, not approving the CR. | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED | A | change.md ¶1 (stated purpose) | The goal, a year-over-year comparison, cannot be met by any retention setting the policy allows in staging, because 180 days is less than one year. The CR picked a mechanism the policy rules out. | Someone "compromises" at 180 days expecting the comparison to work. The logs from this year's load test are deleted before next year's test runs. | Before the 180-day window closes, extract the load-test results the comparison actually needs, such as metrics, latency or throughput summaries, or reports, and store them as test artifacts. See N2 on whether those count as "logs". | a✓ b✓ c✗ d✓ |

**Severity note on F1:** This is internal policy compliance rather than an external regulation. I scored (c) as yes because the context names policy compliance as the stake. If you weigh it lower, F1 becomes High, and the verdict stays the same either way.

**Siblings searched (F1):** I checked every rule in policy.md for any route that permits more than 180 days in non-production.
- R-6 is production-only.
- R-8 only restricts further.
- No sibling route exists.

**Security:** Not a security finding, because no trust boundary is crossed. It is a compliance defect.

## Needs validation

- **N1:** Does staging really contain no customer payloads? This depends on the scrubber report, which was not supplied. A 2026-10-18 report is also a one-time check and does not cover logs written after that date. If payloads are present, R-8 forbids keeping them in staging at any retention, including the current 14 days. That would be a separate problem from this CR.
- **N2:** Do derived load-test summaries or reports count as "logs" under the policy? The policy does not define the term. If they are not logs, the F2 workaround is unrestricted. If they are, the same 180-day cap applies to them.

## Refuted

- **X1: "Get the data owner's written approval and ship."** R-6's approval clause covers production logs only. R-7 says no approval is required up to 180 days and provides nothing beyond that, so approval cannot authorize 400 days in staging.
- **X2: "The synthetic-only claim makes the retention limit irrelevant."** R-7 caps all non-production logs regardless of content. Whether payloads are present matters only under R-8.

## What holds up

The CR correctly identifies staging as non-production, and it states a clear, legitimate purpose. Moving from 14 days to any value up to 180 days complies with the policy and needs no sign-off.

## Unverified claims

- "Synthetic test traffic only; no customer payloads." To confirm, read the scrubber report, and check that it covers the full retention window, not just a snapshot.

## Questions for the author

None would change the verdict. The 180-day ceiling is in the text, and only a policy amendment changes it.

## Decision-maker summary

Do not ship CR-4411 at 400 days, because it violates R-7's 180-day cap and no approval can override that. Either ship it at 180 days or less and preserve load-test summaries separately for the year-over-year comparison, or propose a policy amendment. Shipping as written puts staging out of policy from day 181.

## Owner summary

The change asks to keep test-environment logs for 400 days, but the retention policy allows at most 180 days there, and nobody can sign off an exception. Keeping logs for up to 180 days is allowed right away. To compare this year's tests with next year's, save the test results themselves rather than the raw logs, or ask for the policy to be changed.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "change.md", "status": "seen", "matters": true},
    {"item": "policy.md", "status": "seen", "matters": true},
    {"item": "payload scrubber report 2026-10-18", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "change.md", "kind": "document"},
      {"unit": "policy.md", "kind": "document"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "policy.md:R-6", "kind": "section"},
      {"unit": "policy.md:R-7", "kind": "section"},
      {"unit": "policy.md:R-8", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "payload scrubber report 2026-10-18", "reason": "not_supplied"},
      {"unit": "current staging retention config", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "change.md ¶1 ('400 days') vs policy.md R-7 ('up to 180 days')",
     "scenario": "CR-4411 ships; from day 181 staging retains logs R-7 prohibits, putting the organization out of compliance with its only applicable retention rule. No approval path exists for non-production (R-6 covers production only).",
     "fix": "Reject 400 days. Set staging retention to at most 180 days (no approval needed under R-7); anything longer requires a policy amendment.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every rule in policy.md for a route permitting >180 days in non-production",
                           "found": "none; R-6 is production-only, R-8 only restricts further"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "change.md ¶1 (stated purpose: compare this year's load tests with next year's)",
     "scenario": "A compromise at 180 days is adopted expecting it to serve the comparison; this year's load-test logs are deleted before next year's test, so the goal fails.",
     "fix": "Extract the load-test results the comparison needs (metrics, summaries, reports) into test artifacts before 180 days elapse; confirm they are not 'logs' under the policy (N2).",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "N1", "status": "needs_validation", "track": "A", "location": "change.md ¶2",
     "suspicion": "Staging logs may contain customer payloads despite the claim; the scrubber report is a one-time check from 2026-10-18.",
     "unresolved_fact": "Contents and coverage of the payload scrubber report; if payloads exist, R-8 forbids keeping them in staging at any retention."},
    {"id": "N2", "status": "needs_validation", "track": "A", "location": "policy.md (no definition of 'logs')",
     "suspicion": "Derived load-test summaries might fall under the 180-day cap.",
     "unresolved_fact": "Whether the policy's term 'logs' covers derived test reports and metrics."}
  ],
  "refuted": [
    {"id": "X1", "candidate": "Data-owner written approval can authorize 400 days in staging.",
     "evidence": "R-6's approval clause applies only to 'Production logs'; R-7 provides no approval route beyond 180 days."},
    {"id": "X2", "candidate": "Synthetic-only content makes the retention cap irrelevant.",
     "evidence": "R-7 caps all non-production logs regardless of content; content matters only under R-8."}
  ]
}
```