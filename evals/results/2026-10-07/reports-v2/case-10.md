**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools in this session, so nothing was run. Every arithmetic result below was traced by hand from the supplied code.

**VERDICT: REWORK.** The proration denominator is hardcoded to 30 days, but the request asks for calendar months. Every month that is not 30 days long is mis-billed, and an upgrade on the 31st is billed nothing.

**CONFIDENCE: medium.** The core defects come straight from the code and the arithmetic. Confidence is limited by three things: the tax table and commit a1b2c3d4e5 were not supplied, nothing was executed, and there was only one reviewer.

**INPUTS LEDGER:**
- **Seen:**
  - The original request (request.md).
  - The context (context.md), including the PR description quote.
  - `billing/proration.py` (supplied as `proration.py`).
- **Not seen:**
  - `billing/tax_table.json`. **This gap matters.** The tax rate format (fraction vs percent), whether a `default` key exists, and the region coverage all decide whether the tax is correct.
  - Commit `a1b2c3d4e5`. **This gap matters.** The PR says "Rounding follows the fix in that commit", so the rounding policy cannot be verified.
  - The callers of `prorated_cents`. **This gap matters.** I could not see what type `monthly_price_cents` is, which timezone `upgrade_on` uses, or whether `region` is always passed.
  - Tests. Per the context, the PR changes only `proration.py`, so there are none. That absence is itself a finding (#4).

**SEATS AND GATE:** Only one reviewer ran: this session, same-vendor, with no tools. No subagent and no cross-vendor seats were available or requested. Sensitivity gate: the material is code only, with no personal, financial-record or credential data. It was not sensitive, so no seat was refused on those grounds.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B | `proration.py`: `DAYS_IN_BILLING_MONTH = 30` and both of its uses | The request says "calendar month", but the code assumes every month has 30 days. Both the remaining-days count and the denominator are wrong in 28-, 29- and 31-day months. | Price 3000¢, upgrade on Feb 15. The code charges 16/30 = 1600¢. The correct charge is 14/28 = 1500¢, so the customer is overcharged 6.7%. Upgrade on Feb 28: the code charges 3/30 = 300¢ instead of 1/28 = 107¢. Upgrade on Jan 31: remaining = 30−31+1 = **0**, so a day of service is billed 0¢. Upgrade on Jan 1: 30/30 = 3000¢ (correct total); Jan 16: 15/30 = 1500¢ instead of 16/31 = 1548¢, an undercharge. | Use `calendar.monthrange(d.year, d.month)[1]` for both the count and the denominator. Add parameterized tests for Feb 28 and 29 (leap and non-leap years), Jan 31, Apr 30, and day 1 of each month length. | confirmed. The strongest defense, "30-day billing month is our convention", contradicts the request's explicit "calendar month" and does not explain billing 0¢ on the 31st. |
| 2 | High | CONFIRMED | B | `TAX_TABLE.get(region, TAX_TABLE["default"])` and `region="default"` in the signature | An unknown, misspelled or missing region silently gets the default rate. The request requires "tax for their region". | A caller passes `"DE "` or `"de"`, or forgets the `region` argument, and the customer is taxed at the default rate. The result is under- or over-collected tax with no error or log, which is legal exposure in production billing. | Make `region` required. Raise an error (or log loudly and alert) when the region is not in the table. Test with an unknown region and expect an error. | confirmed. A defender could say the fallback is intentional, but nothing in the request permits a fallback rate, and nothing distinguishes intentional use of the default from typos. |
| 3 | High | UNVERIFIED | B / C | `tax_rate = Decimal(str(TAX_TABLE...))`, `net * (1 + tax_rate)` | The code assumes table values are fractions such as `0.19`. If the table stores percents such as `19`, every charge is about 20× too large. If `"default"` is absent, every call to a known region still raises `KeyError`, because the `.get` default argument is evaluated eagerly. | The table, as updated in a1b2c3d4e5, stores `"DE": 19`, so a 1500¢ net is charged 30000¢. | Supply `tax_table.json`. Add a load-time schema check (every rate satisfies 0 ≤ r < 1, and `default` is present). Add a test against the real table. | Not confirmed or refuted. The settling input was not supplied. Kept as UNVERIFIED and does not set the verdict. |
| 4 | High | CONFIRMED | B | The PR's file list (context: only `proration.py` changed) | Production billing logic ships with no tests. Finding #1 would have been caught by a single February test case. | Future edits, or the rounding "fix", regress silently. | Add unit tests covering month-length edges, the rounding boundary at .5¢, tax regions, an unknown region, and day 1 and the last day of the month. | confirmed. The context lists only the one file. |
| 5 | Medium | UNVERIFIED | B | Two-stage `quantize(..., ROUND_HALF_UP)` | The code rounds the net to the cent, then rounds the gross again. It never computes or returns tax as its own amount. Many jurisdictions and invoicing systems require tax to be a separate, separately rounded line. The PR says the rounding follows a commit I could not see. | An invoice shows net + tax lines that do not sum to the charged total, or tax is off by 1¢ against the authority's rounding rule. | Return `(net, tax, total)` with tax rounded once per the documented rule. Reconcile against commit a1b2c3d4e5. | Not confirmed or refuted. The commit was not seen. |
| 6 | Medium | CONFIRMED | B | Module level: `TAX_TABLE = json.loads(... .read_text())` | The table is read at import time. A missing or malformed file crashes the whole billing module on import, and rate updates need a process restart. | A deploy ships without `tax_table.json`, or with a bad edit, and every importer of `billing` fails. A rate change takes effect only after a restart, so customers are billed at stale rates in the meantime. | Load lazily, or validate at startup with a clear error. Document the reload behavior. | n/a (Medium) |
| 7 | Medium | PROBABLE | B | `Decimal(monthly_price_cents)`, `upgrade_on.day` | There is no input validation. A float price produces binary-float artifacts in `Decimal` (for example, `Decimal(19.99)`). Negative prices or `None` are not rejected. The timezone used to compute `upgrade_on` is unspecified. | A caller passes a float, or computes the date in UTC for a customer whose local date differs, and the customer is billed for one day more or less. | Assert that the price is a non-negative `int`. Document and test which timezone defines the upgrade date. | n/a |
| 8 | Low | CONFIRMED | B | `if remaining_days < 0` | This branch is dead code: the minimum is 30−31+1 = 0. It suggests the author misjudged the edge cases, and the real problem is the 0 result itself (#1). | No direct harm. It hides the fact that day 31 yields 0. | Remove it once #1 is fixed. | n/a |
| 9 | Low | CONFIRMED | B | `from datetime import date` | The import is unused. | None. | Remove it, or use it in a type hint. | n/a |

## WHAT HOLDS UP
- **Inclusive day count.** The `+1` correctly counts day D itself ("from D to the end of that month").
- **Decimal arithmetic.** Using `Decimal`, rather than floats, for money is right, and `Decimal(str(rate))` avoids float artifacts from the JSON.
- **New plan's price.** Charging at the new plan's price with no credit for the old plan matches the request as written, which asks for no credit.
- **Table path.** `Path(__file__).parent / "tax_table.json"` resolves to `billing/tax_table.json`, which matches the PR description.

## UNVERIFIED CLAIMS
- **"Tax rates come from billing/tax_table.json (see the update in commit a1b2c3d4e5)".** To confirm, supply the file and the diff, and check the value format, the `default` key and region coverage.
- **"Rounding follows the fix in that commit".** To confirm, supply the commit and compare its rule with the two-stage HALF_UP rounding used here.
- **Pricing is tax-exclusive.** The code adds tax on top of the price. To confirm, check the pricing and terms documentation.

## QUESTIONS FOR THE AUTHOR
1. Is the 30-day month deliberate? The request says calendar month. If it is deliberate, who approved charging 0¢ for an upgrade on the 31st?
2. What format are the rates in `tax_table.json`, and does it contain `default`? What should happen for an unknown region?
3. What rounding rule did a1b2c3d4e5 establish, and must tax appear as a separate line?

## DECISION-MAKER SUMMARY
Do not merge. The code bills by a 30-day month instead of the calendar month that was asked for. February upgrades are overcharged, mid-month upgrades in 31-day months are undercharged, and an upgrade on the 31st is billed nothing. Unknown regions also silently get a default tax rate. Fix the month length, make region handling strict, add edge-case tests, and supply the tax table and the referenced commit; until then, real customer charges and tax collection will be wrong.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "callers of prorated_cents", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "absent_from_pr", "matters": true}
  ],
  "seats": [{"vendor": "same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "code only; no personal, financial-record or credential data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py: DAYS_IN_BILLING_MONTH = 30 and its uses",
      "scenario": "Price 3000c, upgrade Feb 15: charges 1600c instead of 1500c; Feb 28: 300c instead of 107c; Jan 31: remaining_days=0 so 0c for a day of service",
      "fix": "Use calendar.monthrange(year, month)[1] for count and denominator; add tests for Feb 28/29 (leap and non-leap), Jan 31, Apr 30, day 1", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py: TAX_TABLE.get(region, TAX_TABLE['default']); region='default' parameter",
      "scenario": "Misspelled, unknown or omitted region silently taxed at the default rate; wrong tax collected with no error",
      "fix": "Make region required; raise or alert on unknown region; test it", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "B", "location": "proration.py: tax_rate computation; billing/tax_table.json (not supplied)",
      "scenario": "If the table stores percents (19) rather than fractions (0.19), charges are about 20x; if 'default' is missing, every call raises KeyError",
      "fix": "Supply the table; validate at load that every rate is in [0,1) and 'default' exists; test against the real table", "status": "unresolved"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "PR file list: only proration.py changed",
      "scenario": "Production billing logic ships untested; the month-length bug and future regressions go uncaught",
      "fix": "Add unit tests for month-length edges, .5c rounding, regions, unknown region, first and last day", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "proration.py: two-stage quantize ROUND_HALF_UP",
      "scenario": "Tax not computed or rounded as its own line; invoice lines may not reconcile or may violate the jurisdiction's rounding rule; commit a1b2c3d4e5 not seen",
      "fix": "Return net, tax and total with tax rounded once per the documented rule; reconcile with the commit", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py: module-level TAX_TABLE load",
      "scenario": "Missing or malformed file crashes the import of the billing module; rate updates need a restart",
      "fix": "Validate at startup with a clear error, or load lazily; document reload behavior", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "proration.py: Decimal(monthly_price_cents), upgrade_on.day",
      "scenario": "Float price introduces binary artifacts; negative or None inputs not rejected; unspecified timezone shifts the upgrade day by one",
      "fix": "Assert price is a non-negative int; document and test the timezone that defines upgrade_on", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py: if remaining_days < 0",
      "scenario": "Dead branch (minimum is 0); masks the real day-31 zero-charge defect",
      "fix": "Remove after fixing the month-length calculation", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py: from datetime import date",
      "scenario": "Unused import; no runtime harm", "fix": "Remove or use in a type hint", "status": "n/a"}
  ]
}
```
