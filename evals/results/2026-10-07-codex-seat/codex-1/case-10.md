**VERDICT: REWORK** — The calculation uses a fixed 30-day month, contradicting the calendar-month requirement; regional tax correctness also lacks required evidence.

**CONFIDENCE: medium** — The calendar defect is certain by inspection. Missing artifacts and no execution limit the tax and rounding review. Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.

**INPUTS LEDGER**

| Input | Status | Does the gap matter? |
|---|---|---|
| Original request and production billing context | Seen | Defines calendar days, inclusive of upgrade day, and regional tax |
| Supplied `proration.py` | Seen | Sufficient to establish the calendar defect |
| `billing/tax_table.json` | Not supplied | Yes: rates, region coverage, fallback, and representation cannot be checked |
| Commit `a1b2c3d4e5` | Not supplied | Yes: the claimed tax update and rounding fix cannot be checked |
| Tests, callers, full PR diff | Not supplied | Limits verification of input guarantees and regression coverage |

**SEATS AND GATE:** One local textual review ran. No independent or external seats ran; tools were unavailable. The supplied material contains no apparent credentials, personal records, or confidential customer data.

**RECONSTRUCTION:** The function charges a fraction of the new monthly price, rounds that amount to cents, applies a regional tax multiplier, then rounds again. It includes the upgrade day but assumes every month has 30 days. Correctness requires actual calendar-month lengths, correctly represented tax rates, valid region selection, and an agreed rounding policy. Tracks B and C apply.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | B | `proration.py:8,13–16` | Both remaining days and the denominator use 30 instead of the actual calendar-month length. | January 31, monthly price 3,100 cents: net charge is **0**, although one of 31 days remains, requiring **100 cents before tax**. February 28 in a non-leap year, price 2,800 cents: net charge is **280**, although one of 28 days remains, requiring **100 cents**. | Derive month length from the upgrade year and month. Test first and last days of 28-, 29-, 30-, and 31-day months. In a scratch copy, restore the fixed-30 calculation and confirm those tests fail. | **Confirmed:** the zero clamp cannot restore the missing January 31 charge or correct February’s denominator. |
| 2 | High | CONFIRMED missing evidence; tax correctness UNVERIFIED | B/C | Context: “Tax rates come from billing/tax_table.json … Rounding follows the fix in that commit.” | The production tax and rounding claims depend on two unavailable artifacts. Their correctness cannot be established from this file. | If a region is absent, the function silently uses the default rate. If rates use percentage points rather than fractional rates, the multiplier produces a materially wrong charge. Neither condition can be ruled out with the supplied evidence. | Supply the actual table and referenced commit. Check rate units, applicable regions, default behavior, and rounding policy; verify representative region totals against independently calculated expected charges. | **Confirmed evidence gap:** no wrong table entry is alleged; the supplied code does not resolve the gap. |

**WHAT HOLDS UP:** The calculation includes the upgrade day. With valid integer prices and correctly represented rates, `Decimal` and explicit rounding avoid ordinary binary floating-point arithmetic. In a 30-day month, the day fraction matches the stated calendar requirement.

**UNVERIFIED CLAIMS**

- **Rounding follows the referenced fix.** The function rounds twice. For a 30-day month’s last day, a 101-cent monthly price and hypothetical 10% tax produce **3 cents** here; rounding only the final total produces **4 cents**. Neither policy is established as required. Inspect the commit and approved billing policy.
- **Regional tax selection is correct.** Inspect the table and caller region mapping, including unknown regions.
- **Tests protect billing behavior.** No tests were supplied or run. Coverage remains unverified until relevant tests pass and deliberate mutations make them fail in a scratch copy.

**QUESTIONS FOR THE AUTHOR:** Provide the tax table and referenced commit. What rounding sequence and unknown-region behavior does the billing policy require?

**DECISION-MAKER SUMMARY:** Correct the calendar calculation before release. Obtain the tax and rounding artifacts and verify expected charges independently. Shipping this version causes predictable undercharges and overcharges before any uncertainty about tax is considered.

**OWNER SUMMARY:** This code charges the wrong amount in months that do not have 30 days, including charging nothing for an upgrade on the 31st. The tax rates and rounding rules also need checking before customers are billed.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "Original request and context", "status": "seen", "matters": true},
    {"item": "proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "Tests, callers, and full PR diff", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "OpenAI", "status": "ran", "cross_vendor": false}
  ],
  "sensitivity_gate": {
    "sensitive": false,
    "reason": "No apparent sensitive data in the supplied material."
  },
  "findings": [
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "proration.py:8,13-16",
      "scenario": "A January 31 upgrade on a 3100-cent monthly plan yields zero net charge instead of 100 cents; a non-leap February 28 upgrade on a 2800-cent plan yields 280 instead of 100 cents.",
      "fix": "Use the actual calendar-month length. Test boundary dates in 28-, 29-, 30-, and 31-day months and verify mutation sensitivity in a scratch copy.",
      "status": "confirmed"
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "track": "B/C",
      "location": "context.md: PR description referencing tax_table.json and commit a1b2c3d4e5",
      "scenario": "Missing artifacts prevent ruling out incorrect regional fallback, tax-rate units, or rounding behavior in production charges. No incorrect table entry has been established.",
      "fix": "Supply and inspect the tax table and commit; verify regional mappings, rate units, fallback policy, and rounding against independent expected charges.",
      "status": "confirmed"
    }
  ]
}
```