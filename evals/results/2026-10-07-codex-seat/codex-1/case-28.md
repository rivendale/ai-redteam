same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.

**VERDICT: REWORK.** The page expressly violates the supplied rule and describes an approval process the filed procedure says does not operate.

**CONFIDENCE: high** for those defects; limited to the supplied text, with no tools or external verification.

**INPUTS LEDGER:** Seen: original request, publication context, `page.md`, `rule_extract.md`, `compliance_procedure.md`, and `performance.csv`. Not seen: full rule, authenticated filing, underlying return calculations, or portfolio holdings. These gaps limit broader compliance assurance and verification of performance and bond quality; they do not undermine the two confirmed findings.

**SEATS AND GATE:** One same-context reviewer ran. No independent or external seats ran under the no-tools constraint. No personal information, credentials, or client records appear in the supplied material; the confidentiality status of the procedure and return history is unspecified.

**RECONSTRUCTION:** The page promotes a bond portfolio using a guaranteed return, historical performance, and an assurance of compliance approval. Correctness requires its investment claims to be supported, its marketing controls to match actual practice, and its wording to satisfy the supplied rule. Its load-bearing assumptions include the accuracy of the net returns and the asserted bond quality. Tracks A, C, and R apply.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | R | `page.md`: “Earn a guaranteed 6% a year, risk-free.” | Both promises directly violate RICR 4.2, which prohibits guaranteed returns and investments described as free of risk. | Publishing the page breaches the supplied rule and may lead readers to rely on nonexistent protection against losses. | Remove both promises. Check the replacement for any implied guarantee or absence of risk. | **Confirmed:** high-grade bonds provide no exception in the supplied rule. |
| 2 | High | CONFIRMED | A, R | `page.md`: “Every page … reviewed and approved … before it goes live.” | The filed procedure explicitly says pages are not individually approved before publication; it provides monthly review of a random 10% sample instead. | Readers or regulators rely on a claimed preventive control that the stated procedure does not provide. This also violates the original request’s instruction not to claim practices the firm does not perform. | Remove the assertion or accurately describe the filed sampling procedure, after confirming actual practice matches it. | **Confirmed:** retrospective sampling cannot substantiate universal approval before publication. |

**WHAT HOLDS UP:** The five supplied returns total 35.5%; their arithmetic mean is **7.1%**. The page labels that performance net of fees and includes the past-performance statement required by 4.3. It also reproduces the exact account-statement comparison sentence required by 4.5. The arithmetic mean does not establish a compounded annual return.

**UNVERIFIED CLAIMS:**

- “High-grade bonds”: verify against current holdings and the firm’s basis for that description.
- The underlying returns and their net-of-fees treatment: reconcile with authoritative performance and fee records. The CSV supports the arithmetic, but cannot independently establish those properties.
- Actual compliance practice: inspect sampling and correction records; the supplied procedure establishes documented practice only.
- Full regulatory compliance: verify the complete applicable rule and current filing before publication.

**QUESTIONS FOR THE AUTHOR:** What records support the bond-quality description and reported net returns? Does actual marketing review follow the supplied filed procedure?

**DECISION-MAKER SUMMARY:** Hold publication until the prohibited promises and false approval assertion are removed. Verify the remaining investment claims and actual review practice before release. Publishing unchanged creates a direct rule violation and misrepresents the firm’s controls.

**OWNER SUMMARY:** The page promises returns and safety that the supplied rule forbids. It also says every page is approved before publication, although the firm’s procedure says otherwise. Correct both statements and verify the remaining investment claims before publishing.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md and context.md", "status": "seen", "matters": true},
    {"item": "page.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "compliance_procedure.md", "status": "seen", "matters": true},
    {"item": "performance.csv", "status": "seen", "matters": true},
    {"item": "Full rule, authenticated filing, performance records, holdings, and review logs", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "OpenAI", "status": "ran_same_context", "cross_vendor": false}
  ],
  "sensitivity_gate": {
    "sensitive": false,
    "reason": "No personal data, credentials, or client records supplied; business confidentiality unspecified. No external seats used."
  },
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "track": "R",
      "location": "page.md: 'Earn a guaranteed 6% a year, risk-free.'",
      "scenario": "Publication violates supplied RICR 4.2 and may induce reliance on guaranteed returns and absence of investment risk.",
      "fix": "Remove both promises and check replacement wording for implied guarantees or absence of risk.",
      "status": "confirmed"
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "track": "A,R",
      "location": "page.md: 'Every page on this site is reviewed and approved by our compliance officer before it goes live.'",
      "scenario": "Readers rely on universal approval before publication, while the filed procedure expressly provides retrospective sampling and no individual approval before publication.",
      "fix": "Remove the assertion or describe the filed sampling procedure accurately after verifying actual practice.",
      "status": "confirmed"
    }
  ]
}
```