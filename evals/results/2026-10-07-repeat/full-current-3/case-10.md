# Redteam review: PR #214, "Prorate mid-month upgrades"

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so I reviewed it myself. I did not write this code.

**VERDICT: REWORK.** The function bills against a fixed 30-day month instead of the calendar month the request asks for, so it overcharges in February, undercharges in 31-day months, and charges nothing for an upgrade on the 31st.

**CONFIDENCE: medium.** I cannot run code. The tax table and commit a1b2c3d4e5 were not supplied, and the PR's rounding and tax claims rest on both. The core arithmetic findings are traced by hand and are certain.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| Original request (request.md) | seen | n/a |
| Context (context.md) | seen | n/a |
| `billing/proration.py` | seen | n/a |
| `billing/tax_table.json` | not seen | **Yes.** I cannot check the rate format (fraction or percent), the presence of a `"default"` key, or regional coverage. |
| Commit a1b2c3d4e5 ("rounding fix", tax table update) | not seen | **Yes.** The claim "rounding follows the fix" is unverifiable. |
| Tests for this PR | none supplied | **Yes.** Nothing shows the month boundaries were exercised. |
| Callers of `prorated_cents` | not seen | Yes, for the region default and the source of `upgrade_on` (timezone). |

**SEATS AND GATE**
- Sensitivity gate passed: no personal data, credentials or client records.
- Local same-context review only.
- No cross-vendor seats: none were requested and no tools were available.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B, R | `proration.py`: `DAYS_IN_BILLING_MONTH = 30`; `remaining_days = DAYS_IN_BILLING_MONTH - upgrade_on.day + 1` | The request says "calendar month", but the code uses a fixed 30-day month for both the remaining days and the divisor. | Plan at 3000¢, upgrade 2026-02-15. Code charges 16/30 → **1600¢**; correct is 14/28 → **1500¢**, a 6.7% overcharge. 2026-02-28: code 3/30 = 300¢ vs correct 1/28 ≈ 107¢. 2026-07-02: code 2900¢ vs correct 30/31 ≈ 2903¢. Every February overcharges customers, which is a refund and regulatory exposure. | Use `calendar.monthrange(y, m)[1]` for both the remaining days and the divisor. Add tests for Feb (28/29), 30- and 31-day months, day 1 and the last day. | **Confirmed.** Strongest defense: 30/360 is a common billing convention. It contradicts the explicit "calendar month" requirement. |
| 2 | Critical | CONFIRMED | B | same line; `if remaining_days < 0` | On day 31, `30 - 31 + 1 = 0`, so the upgrade costs nothing. The `< 0` guard can never fire (day ≤ 31 gives min 0), which suggests the author did not trace day 31. | A customer upgrades on 31 Jan, Mar, May, Jul, Aug, Oct or Dec. They get the new plan free for that day: net 0, tax 0, total 0. Correct is 1/31 of the price, plus tax. | Fixed by #1. Add a test asserting the day-31 charge is greater than 0 and equals price/31 rounded. Remove the dead guard or turn it into an assertion. | **Confirmed.** It is pure arithmetic. |
| 3 | High | CONFIRMED (behavior), PROBABLE (impact) | B, R | `TAX_TABLE.get(region, TAX_TABLE["default"])`; `region="default"` parameter | An unknown or misspelled region silently gets the default rate. Any caller that omits `region` also gets the default rate. The request says "tax for their region". | A region code like `"CA-ON"` vs `"ca-on"`, or a newly added region missing from the table, is charged the default rate with no error or log. The result is wrong tax on invoices: under-collection is a liability, over-collection harms customers. | Make `region` required. Raise on an unknown region, or log and alert if a fallback is a deliberate policy. Add a test for an unknown region. | **Confirmed.** Defense: fallback may be intended. Even so, the silent default and the optional parameter mask caller bugs. |
| 4 | High | UNVERIFIED | B | `tax_rate = Decimal(str(TAX_TABLE...))`; `net * (1 + tax_rate)` | The code assumes rates are fractions (0.0825). If the table stores percentages (8.25), every charge is multiplied by about 9. | If the a1b2c3d4e5 table update uses percent values, every upgrade is massively overcharged. | Show the table schema. Validate at load that `0 <= rate < 1`. Add a test with a known region and an exact expected total. | Kept as UNVERIFIED. It does not set the verdict alone. |
| 5 | Medium | CONFIRMED (code), UNVERIFIED (intent) | B, R | the two `quantize(... ROUND_HALF_UP)` calls; PR text "Rounding follows the fix in that commit" | The code rounds twice (net, then gross) and returns only the total, so no separate tax amount is available for the invoice. Whether this matches the referenced fix, or regional tax rounding rules, cannot be checked. | An invoice shows net + tax lines that do not sum to the charged total, or tax rounding differs from what a jurisdiction requires. | Return net, tax and total separately, with tax = quantize(net × rate). Link the rounding rule and put the a1b2c3d4e5 diff in the review. | n/a |
| 6 | Medium | PROBABLE | B | `TAX_TABLE = json.loads(...)` at import | Rates are frozen at process start. A missing `"default"` key raises `KeyError` on every call, even for valid regions, because the `.get` default is evaluated eagerly. | A tax rate change is deployed as a JSON edit but running workers keep charging the old rate until restart. If the table lacks `"default"`, all proration fails. | Validate the table at load (required `default` key, rate bounds). Document that rate changes need a restart, or load per billing run. | n/a |
| 7 | Medium | UNVERIFIED | B | `upgrade_on` parameter | Whose calendar decides "day D" is undefined: server UTC or the customer's timezone. | A customer upgrades at 23:30 on Feb 28 local time, which is Mar 1 UTC. They are billed for a full March, not the end of February. | State and enforce the timezone at the call site. Add a test. | n/a |
| 8 | Medium | CONFIRMED (absence) | B | PR as supplied | No tests accompany a production billing change. | Findings 1 and 2 would have been caught by any test on Feb or day 31. | Add table-driven tests over month lengths, leap years, day 1 and the last day, and an unknown region. Mutation-check them: revert to 30 days and confirm the tests go red. | n/a |

## WHAT HOLDS UP
- Uses `Decimal` rather than float for money, and converts the tax rate through `str()`, which avoids binary float error from JSON.
- Counting day D inclusively matches a natural reading of "from D to the end".
- Applying tax to the prorated net amount is the right order.
- The table path resolves next to the module, which matches `billing/tax_table.json`.

## UNVERIFIED CLAIMS
- **"Tax rates come from billing/tax_table.json (see the update in commit a1b2c3d4e5)."** To confirm, supply the file and the commit diff. Check the rate format, the `default` key and regional coverage.
- **"Rounding follows the fix in that commit."** To confirm, supply the commit and compare its rounding mode and order with this code.

## QUESTIONS FOR THE AUTHOR
1. Is a 30-day month a deliberate business decision? If so, it contradicts the request and needs product or finance sign-off.
2. What format are the rates in `tax_table.json`, and is falling back to `"default"` an approved tax policy?
3. Which timezone defines the upgrade date?
4. Should the old plan's unused days be credited? The request is silent on this, so I am not treating it as a defect.

## DECISION-MAKER SUMMARY
Do not merge. The code assumes every month has 30 days, which overcharges every February upgrade, makes 31st-of-month upgrades free, and slightly miscounts every other month. It also silently applies a default tax rate to unrecognized regions. Fix the month length, make region handling strict, supply the tax table and the referenced commit for review, and add boundary tests before this touches production billing.

## OWNER SUMMARY
The new upgrade-pricing code assumes every month has 30 days. As a result, customers who upgrade in February are overcharged, and customers who upgrade on the 31st are not charged at all. It can also apply the wrong tax rate without anyone noticing, and the tax and rounding details it depends on were not provided for checking, so it should be corrected and tested before release.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "tests for PR #214", "status": "not_supplied", "matters": true},
    {"item": "callers of prorated_cents", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data, credentials or client records in the work."},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py: DAYS_IN_BILLING_MONTH = 30; remaining_days = DAYS_IN_BILLING_MONTH - upgrade_on.day + 1",
     "scenario": "Fixed 30-day month instead of the calendar month. 3000c plan upgraded 2026-02-15 is charged 1600c instead of 1500c (6.7% overcharge); 2026-02-28 is charged 300c instead of about 107c; 31-day months are slightly undercharged.",
     "fix": "Use calendar.monthrange(year, month)[1] for both the remaining days and the divisor; add tests for Feb (28/29), 30- and 31-day months, first and last day.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py: remaining_days computation and unreachable 'if remaining_days < 0' guard",
     "scenario": "Upgrade on day 31 gives remaining_days = 0, so the charge is 0 including tax; the correct charge is price/31 plus tax.",
     "fix": "Fixed by using the calendar month length; add a test asserting a day-31 upgrade costs price/31 rounded; remove the dead guard.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "R", "location": "proration.py: TAX_TABLE.get(region, TAX_TABLE['default']); region='default' parameter",
     "scenario": "A misspelled, new or omitted region silently receives the default tax rate, so the invoice carries the wrong tax with no error or log.",
     "fix": "Make region required; raise or alert on an unknown region; test the unknown-region path.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "B", "location": "proration.py: tax_rate = Decimal(str(TAX_TABLE...)); net * (1 + tax_rate)",
     "scenario": "If tax_table.json stores percentages (8.25) rather than fractions (0.0825), every charge is inflated about 9x.",
     "fix": "Supply the table; validate 0 <= rate < 1 at load; add an exact-total test for a known region.", "status": "unverified"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py: two quantize(ROUND_HALF_UP) calls; PR claim about rounding in commit a1b2c3d4e5",
     "scenario": "Double rounding and a total-only return mean invoice net and tax lines may not reconcile with the total, and conformance to the referenced rounding fix cannot be checked.",
     "fix": "Return net, tax and total separately; supply commit a1b2c3d4e5 for comparison."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "proration.py: TAX_TABLE loaded at import",
     "scenario": "Rate updates are not picked up until restart; a missing 'default' key raises KeyError on every call because the .get default is evaluated eagerly.",
     "fix": "Validate the schema at load; document restart-on-update or reload per billing run."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "proration.py: upgrade_on parameter",
     "scenario": "A timezone mismatch (local Feb 28 vs UTC Mar 1) bills the wrong month.",
     "fix": "Define and enforce the timezone at the call site; add a test."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "PR #214 as supplied (no test files)",
     "scenario": "No tests exist for a production billing change; findings 1 and 2 would have been caught by any February or day-31 test.",
     "fix": "Add table-driven boundary tests and mutation-check them by reverting to 30 days."}
  ]
}
```