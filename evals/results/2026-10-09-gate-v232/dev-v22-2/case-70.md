# Redteam review: Q1 service report (Track C, with A where the conclusion depends on the numbers)

**Single-reviewer review, no tools.** No fresh subagent or second seat was available in this session. I recomputed every figure by hand from the two rows of data.csv. Re-run in a fresh session before the rollout decision.

---

**VERDICT: REWORK.** Every figure in the report is computed correctly, but its headline conclusion is contradicted by the data. Complaints per customer rose 50%, and nothing in data.csv identifies the onboarding flow, so the report cannot say whether the flow is working.

**CONFIDENCE: medium.** The arithmetic is certain from the two rows supplied. Confidence is limited by:
- one reviewer with no tools;
- no data on the flow itself;
- the report's own unclear definition of who counts as a customer.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | yes, review is against it |
| context.md (Track C, rollout stakes) | seen | yes |
| data.csv (2 rows: 2025Q4, 2026Q1) | seen | yes, the only evidence |
| report.md | seen | it is the work |
| Onboarding flow launch date, regions, which customers went through it | **not supplied** | **yes**: the causal claim depends on it |
| How complaints and incidents were counted for customers who left | **not supplied** | yes: decides whether the rates compare like with like |
| Earlier quarters (seasonality, trend) | not supplied | moderately |

**COVERAGE**
- **Checked:**
  - every number in report.md (25%, 104→78, 1.9 per 1,000, 1.2 per 1,000, 40%, 10 of 5,200, 3 of 2,600);
  - both causal claims;
  - the customer-definition note;
  - both rows of data.csv.
- **Not checked:** anything outside data.csv, because nothing else was supplied.

**SEATS AND GATE**
- Seats: local reviewer only. No subagent or cross-vendor seats, because there are no tools in this session.
- Sensitivity gate: the data is aggregate counts with no personal data, so it passes.

---

## Recomputation

| Claim in report | Recomputed | Result |
|---|---|---|
| Complaints fell 25% (104 to 78) | (104 − 78) / 104 = 26 / 104 = 25.0% | correct as a raw count |
| Serious incidents 1.9 per 1,000 (10 of 5,200) | 10 / 5,200 × 1,000 = 1.923 | correct, rounded |
| Serious incidents 1.2 per 1,000 (3 of 2,600) | 3 / 2,600 × 1,000 = 1.154 | correct, rounded |
| Serious incident risk cut by 40% | (3/2,600) / (10/5,200) = 6/10 = 0.60, a 40% drop | correct arithmetic |
| **Not in report:** complaints per customer | 104 / 5,200 = **20.0 per 1,000**, then 78 / 2,600 = **30.0 per 1,000** | **up 50%** |
| **Not in report:** customers | 5,200 → 2,600 | **down 50%** |

---

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | C, A | report.md line 3: "Complaints fell 25% quarter over quarter (104 to 78), so the new onboarding flow is working." | The report uses the raw complaint count while the customer base halved. Per customer, complaints rose from 20.0 to 30.0 per 1,000, an increase of 50%. The report divides by customers for incidents but not for complaints, which is the comparison that favours the conclusion each time. The 50% customer drop is not mentioned at all. | Leadership reads "complaints fell 25%, flow is working" and approves the rollout to every region. The service in fact got worse per customer, and the base may be churning. | Report complaints per 1,000 customers for both quarters (20.0 → 30.0). State the 5,200 → 2,600 drop and its cause. Remove "so the flow is working". Reproduce: 104/5,200 = 0.020 and 78/2,600 = 0.030. | a Y, b Y, c Y, d Y |
| F2 | **Critical** | CONFIRMED | A, C | report.md line 3 "so the new onboarding flow is working"; line 5 "The flow also cut the risk…" | data.csv has only quarter, customers, complaints and serious_incidents. Nothing identifies the onboarding flow: no launch date, no flag for which customers used it, no comparison group. Both causal claims are a before-and-after comparison with no link to the flow. | Any other change between the quarters could produce these numbers: churn, seasonality, a counting change (see F3), or a product fix. The rollout then happens on an effect the data cannot attribute. | Describe the changes, not their cause, or add data that supports a cause: customers split by old versus new flow in the same quarter, or a staggered regional launch. Reproduce: list the columns of data.csv; none refers to onboarding. | a Y, b Y, c Y, d Y |
| F3 | High | PROBABLE | C | report.md line 6: "We counted customers who stayed active the full quarter; customers who left are in the earlier row only." | The two rows appear to use different denominators. Q1 counts only customers who stayed, while Q4 includes customers who later left. That is survivorship: the customers who left are likely the least satisfied, and they are missing from Q1. The note also does not say whether Q1 complaints and incidents include those raised by leavers. | If leavers are dropped from the Q1 denominator but their complaints stay in the numerator, Q1 rates are inflated. If both are dropped, Q1 looks healthier than it was. Either way the 40% incident drop and the complaint comparison do not compare like with like. | Use one customer definition for both quarters, either active at quarter start or average active. Re-state every rate on that basis. Reproduce: the report's own sentence states the rows were built differently. | a Y, b N, c Y, d Y |
| F4 | High | CONFIRMED | C, A | report.md line 5: "cut the risk of a serious incident by 40%" | The 40% comes from 10 incidents versus 3, which is too few to separate from chance. Suppose the true rate per customer was the same in both quarters. Then Q1 would be expected to hold 2,600/7,800 = 1/3 of the 13 incidents, about 4.3, and observing 3 is ordinary (P(X ≤ 3) under Binomial(13, 1/3) is about 0.33). The 95% interval for 3 Poisson events is roughly 0.6 to 8.8, which spans the Q4 level. | "Cut the risk by 40%" is presented as a measured effect. It cannot be told apart from noise, and the claim is used to support a rollout everywhere. | Report the counts with an interval, or say "too few incidents to conclude". Do not state a percentage reduction in risk. Reproduce: compute the binomial test above. | a Y, b Y, c N, d Y |

---

## NEEDS VALIDATION
- **S1: did the onboarding flow coincide with the customer halving?** The customer base fell from 5,200 to 2,600 in one quarter. If the new flow rejects or loses customers, it may be causing churn rather than improving service. *Settled by:* the flow's launch date and customer counts for new versus old flow.
- **S2: are the Q1 complaints and incidents scoped to customers who stayed?** *Settled by:* the query or definition used to produce the complaints and serious_incidents columns for each quarter.
- **S3: is Q4 to Q1 movement seasonal?** *Settled by:* the same quarter pair from earlier years.

## REFUTED
- **R1: "the 25% figure is miscalculated."** Refuted: 26 / 104 = 0.25 exactly. The problem is the choice of metric (F1), not the arithmetic.
- **R2: "the per-1,000 incident rates are wrong."** Refuted: 1.923 rounds to 1.9 and 1.154 rounds to 1.2. The ratio is exactly 0.6.

## WHAT HOLDS UP
- Every number the report prints reproduces from data.csv.
- Normalising incidents per 1,000 customers is the right method. It just needs to be applied to complaints as well.
- The report discloses its customer definition rather than hiding it, which is what exposed F3.

## UNVERIFIED CLAIMS
- "The new onboarding flow is working." This cannot be checked against data.csv. Confirm it with a comparison of new-flow and old-flow customers.
- "The flow cut the risk." Same gap, plus the sample-size problem in F4.

## QUESTIONS FOR THE AUTHOR
1. When did the new flow launch, in which regions, and which customers in Q1 went through it?
2. Why did customers fall from 5,200 to 2,600?
3. Are the Q1 complaints and incidents counted only for customers who stayed the full quarter?

## DECISION-MAKER SUMMARY
Do not use this report to approve the regional rollout. Measured per customer, complaints rose 50%, the customer base halved, and the data contains nothing about the onboarding flow. If you proceed anyway, you may roll out everywhere a change that coincides with worse service and heavy churn.

## OWNER SUMMARY
The report's numbers add up, but its conclusion does not. Complaints dropped only because there were half as many customers, and each customer actually complained more often than before. The data also says nothing about the new onboarding process, so it cannot show the process is working; that needs a comparison of customers who used it with those who did not.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "data.csv", "status": "seen", "matters": true},
    {"item": "report.md", "status": "seen", "matters": true},
    {"item": "onboarding flow launch date, regions and customer assignment", "status": "not_seen", "matters": true},
    {"item": "complaint and incident counting definition for customers who left", "status": "not_seen", "matters": true},
    {"item": "earlier quarters", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "aggregate counts only, no personal data"},
  "coverage": {
    "checked": [
      {"unit": "data.csv", "kind": "data"},
      {"unit": "report.md", "kind": "file"},
      {"unit": "report.md: complaints fell 25%", "kind": "claim"},
      {"unit": "report.md: onboarding flow is working", "kind": "claim"},
      {"unit": "report.md: serious incident risk cut 40%", "kind": "claim"},
      {"unit": "report.md: 1.9 and 1.2 per 1,000", "kind": "claim"},
      {"unit": "report.md: customer definition note", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "onboarding flow assignment data", "reason": "not supplied"},
      {"unit": "earlier quarters", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "report.md line 3: 'Complaints fell 25% ... so the new onboarding flow is working.'",
     "scenario": "Customers halved from 5,200 to 2,600, so complaints per 1,000 customers rose from 20.0 to 30.0 (+50%); the report cites the raw count, does not mention the customer drop, and concludes the flow works, leading to an unwarranted rollout to every region.",
     "fix": "Report complaints per 1,000 customers for both quarters, state the 50% customer drop, and remove the 'so the flow is working' conclusion.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "104/5200 = 0.020; 78/2600 = 0.030; 0.030/0.020 = 1.5."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "report.md lines 3 and 5: 'so the new onboarding flow is working'; 'The flow also cut the risk'",
     "scenario": "data.csv has no column identifying the onboarding flow, its launch date or a comparison group, so both causal claims rest on a before-and-after comparison that churn, seasonality or a counting change could equally explain; the rollout proceeds on an effect the data cannot attribute.",
     "fix": "Describe the changes without causal language, or supply customer-level data split by old versus new flow in the same period.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "The columns of data.csv are quarter, customers, complaints and serious_incidents; none refers to onboarding."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "C",
     "location": "report.md line 6: 'We counted customers who stayed active the full quarter; customers who left are in the earlier row only.'",
     "scenario": "Q1 appears to count only customers who stayed while Q4 includes customers who later left, so the rates compare different populations (survivorship); the 40% incident drop and the complaint comparison may be artifacts of the definition.",
     "fix": "Apply one customer definition to both quarters and recompute every rate on it.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "The quoted sentence states the two rows were built on different bases."},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "report.md line 5: 'cut the risk of a serious incident by 40%'",
     "scenario": "The claim rests on 10 versus 3 incidents; with equal per-customer rates, about 4.3 of the 13 incidents would be expected in Q1, and P(X<=3) under Binomial(13, 1/3) is about 0.33, so the 40% cannot be distinguished from chance yet is presented as a measured effect.",
     "fix": "Report the counts with confidence intervals, or state that there are too few incidents to conclude; drop the 40% risk-reduction claim.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Binomial(13, 2600/7800) gives P(X<=3) of about 0.33; the 95% Poisson interval for 3 events is about 0.6 to 8.8."},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "data.csv: customers 5200 to 2600",
     "suspicion": "The new onboarding flow may be causing the 50% customer drop.",
     "unresolved_fact": "The flow's launch date and customer counts split by new versus old flow."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "data.csv: 2026Q1 complaints and serious_incidents",
     "suspicion": "Q1 complaints and incidents may include customers who left, while the Q1 customer count excludes them.",
     "unresolved_fact": "The query or definition used to produce the complaints and serious_incidents columns for each quarter."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "data.csv: both rows",
     "suspicion": "The Q4 to Q1 movement may be seasonal.",
     "unresolved_fact": "The same quarter pair from earlier years."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The 25% complaint drop is miscalculated.", "evidence": "26/104 = 0.25 exactly."},
    {"id": "R2", "candidate": "The per-1,000 incident rates are wrong.", "evidence": "10/5200*1000 = 1.923 rounds to 1.9; 3/2600*1000 = 1.154 rounds to 1.2; the ratio is exactly 0.6."}
  ]
}
```