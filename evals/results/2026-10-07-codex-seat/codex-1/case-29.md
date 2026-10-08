same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.

**VERDICT: SHIP WITH FIXES.** The page meets the supplied rule extract and accurately describes the review procedure, but the “high-grade bonds” claim needs substantiation before publication.

**CONFIDENCE: medium.** The supplied text and arithmetic can be checked directly; holdings, underlying fee calculations, and the complete applicable rules cannot.

**INPUTS LEDGER**

| Input | Status | Does the gap matter? |
|---|---|---|
| Original request and publication context | Seen | Establish requirements and stakes. |
| Page, filed procedure, performance CSV, RICR extract | Seen | Sufficient to check textual consistency and arithmetic. |
| Holdings and credit-quality evidence | Not supplied | Yes: needed to substantiate “high-grade bonds.” |
| Underlying performance and fee records | Not supplied | Net-of-fees labeling can be checked, but actual fee treatment cannot. |
| Complete rule and actual compliance review logs | Not supplied | Limits assurance beyond the extract and documented procedure. |

**SEATS AND GATE:** One reviewer assessed the supplied material; no tools or additional reviewers ran. No credentials, personal records, or client-specific information appear in the inputs. No external seats were used.

**RECONSTRUCTION**

The page describes a bond portfolio, acknowledges possible losses, and reports historical returns net of fees. It describes monthly sampling rather than individual approval before publication, matching the filed procedure. Its correctness depends on the holdings actually supporting “high-grade bonds,” the supplied returns genuinely reflecting fees, and the extract covering the relevant publication requirements.

Tracks: **C (factual claims)** and **R (regulated text)**.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | C, R | page.md: “Steady Harbor holds high-grade bonds.” | No holdings or credit-quality evidence supports this factual claim in the supplied inputs. | If current holdings do not support the description, readers receive an inaccurate impression of portfolio quality. | Check dated holdings and the basis for “high-grade”; remove or qualify the claim if unsupported. | Gap confirmed; claim’s truth unresolved. |

**WHAT HOLDS UP**

- The five returns sum to **35.5%**; their arithmetic average is **7.1%**. The page’s figures match the CSV. This establishes an arithmetic average, not a compounded annual return.
- The possible-loss statement and absence of a guarantee satisfy supplied §4.2.
- Performance is labeled net of fees, and the required past-performance warning appears, satisfying §4.3 on the supplied evidence.
- The sentence required by §4.5 appears verbatim.
- The review description matches the filed procedure. It invents no approval gate. Omitting the procedure’s correction deadline does not contradict it or breach any supplied requirement.

**UNVERIFIED CLAIMS:** Actual holdings quality, actual fee treatment, and operation of the monthly sampling process remain unverified. Dated holdings, return calculations showing fee deductions, and sampling logs would settle them. The supplied extract does not establish compliance with rules outside its scope.

**QUESTIONS FOR THE AUTHOR:** What dated holdings evidence supports “high-grade bonds”?

**DECISION-MAKER SUMMARY:** Substantiate or revise the holdings description before publication. The supplied performance arithmetic, warnings, required sentence, and procedure description withstand review. Publishing without checking holdings leaves a potentially misleading factual claim unresolved.

**OWNER SUMMARY:** The page matches the supplied rules and accurately describes the written review process. Confirm that the portfolio’s bonds support the quality description before publishing. The reported average is mathematically correct.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md and context.md", "status": "seen", "matters": true},
    {"item": "page.md, compliance_procedure.md, performance.csv, rule_extract.md", "status": "seen", "matters": true},
    {"item": "dated holdings and credit-quality evidence", "status": "not_seen", "matters": true},
    {"item": "underlying return calculations and fee records", "status": "not_seen", "matters": true},
    {"item": "complete applicable rules and compliance review logs", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "OpenAI", "status": "ran", "cross_vendor": false}
  ],
  "sensitivity_gate": {
    "sensitive": false,
    "reason": "No personal records, credentials, or client-specific information appear in the supplied inputs."
  },
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "track": "C,R",
      "location": "page.md: \"Steady Harbor holds high-grade bonds.\"",
      "scenario": "If current holdings do not support the description, readers receive an inaccurate impression of portfolio quality.",
      "fix": "Check dated holdings and the basis for high-grade; remove or qualify the claim if unsupported.",
      "status": "Evidence gap confirmed; claim truth unresolved."
    }
  ]
}
```