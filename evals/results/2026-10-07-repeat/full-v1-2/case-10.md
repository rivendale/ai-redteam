**Review setup:** This PR was not written in this conversation, so there is no shared-author anchoring. No tools were available, so nothing was run. Every CONFIRMED finding comes from tracing the code by hand. `billing/tax_table.json` and commit `a1b2c3d4e5` were not supplied, so claims that depend on them are UNVERIFIED.

## Pass 1: Reconstruct

The PR claims `prorated_cents` returns what a customer owes when upgrading on day D. That should be the new plan's monthly price × (days from D through month end, inclusive) ÷ (days in that month), plus regional tax, in integer cents. For this to be correct, four things must hold:

- The denominator is the actual number of days in the calendar month.
- `TAX_TABLE[region]` holds a fractional rate (0.0825, not 8.25) and contains a `"default"` key.
- The caller passes the *new* plan's price and the customer-local date.
- The two-step rounding matches what commit `a1b2c3d4e5` specifies.

The first assumption is false.

## VERDICT: REWORK

The proration uses a fixed 30-day month instead of the calendar month. Almost every upgrade is mischarged, and upgrades on the 31st are free.

**CONFIDENCE IN VERDICT: high.** The core defect is a hand trace of plain arithmetic. Confidence in the tax and rounding findings is low, because the tax table and the referenced commit were not provided.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `DAYS_IN_BILLING_MONTH = 30`; `remaining_days = DAYS_IN_BILLING_MONTH - upgrade_on.day + 1`; `share = .../Decimal(DAYS_IN_BILLING_MONTH)` | The request says "calendar month", but the code hardcodes 30 days for both the remaining-days count and the denominator. | Price 3000¢. **Jan 31:** remaining = 30−31+1 = **0**, so the charge is **0** (free upgrade). Correct is 1/31 → 97¢. **Jan 15:** charges 16/30 → 1600¢; correct is 17/31 → 1645¢. **Feb 28, 2026:** charges 3/30 → 300¢; correct is 1/28 → 107¢ (2.8× overcharge). **Feb 29, 2028:** charges 2/30; correct is 1/29. | `days_in_month = calendar.monthrange(d.year, d.month)[1]`, then `remaining = days_in_month - d.day + 1`. Add parametrized tests for the 1st, 15th, 30th and 31st of a 31-day month, Feb 28 in a non-leap year, Feb 28 and 29 in a leap year, and a 30-day month. |
| 2 | Medium | CONFIRMED | `if remaining_days < 0: remaining_days = 0` | Dead and misleading guard. `day ≤ 31`, so `remaining_days ≥ 0` always. The real bug is the value 0 on the 31st, which this guard silently treats as legitimate. | Day 31 yields 0 without any error, which hides finding 1. | Remove the guard. After fixing #1, assert `1 <= remaining <= days_in_month`. |
| 3 | High | PROBABLE | `TAX_TABLE.get(region, TAX_TABLE["default"])` | An unknown region silently falls back to the default rate. | A typo, a new region not yet in the table, a `None` region, or a case mismatch (`"CA"` vs `"ca"`) charges the wrong tax and nothing is logged. In production billing this is a tax-compliance error, not a cosmetic one. | Raise on unknown regions, or log and alert. Require an explicit region rather than `region="default"`. Test that an unknown region raises. |
| 4 | High | UNVERIFIED | Same line, plus `tax_table.json` (not supplied) | `TAX_TABLE["default"]` is evaluated eagerly on every call. If the table has no `"default"` key, every call raises `KeyError`, including calls for valid regions. If rates are stored as percentages (8.25), the multiplier `1 + 8.25` charges about 9× the price. | Either one breaks all charges or grossly overcharges. | Inspect `tax_table.json`. Validate at load time that `"default"` exists and that every rate satisfies `0 <= r < 1`. |
| 5 | Medium | UNVERIFIED | Two `quantize(..., ROUND_HALF_UP)` calls | Net is rounded to the cent, then tax is applied to the rounded net and the result is rounded again. The PR says rounding "follows the fix in a1b2c3d4e5", but that commit was not provided. Double rounding and half-up versus half-even rounding can differ by 1¢. Some jurisdictions mandate a specific rule. | 1¢ discrepancies between invoices and ledgers or tax reports, accumulating across customers. | Read `a1b2c3d4e5` and confirm the intended order and mode. Add golden tests on .5-boundary values, e.g. price 1001¢ on a day giving a share that lands on x.5¢. |
| 6 | Medium | PROBABLE | `return int(net * (1 + tax_rate))` | Only a combined total is returned. The tax amount is not exposed separately. | The invoice and tax reporting need the tax line. Callers then recompute it (`total - net`) with possibly different rounding, or cannot itemize at all. | Return `(net_cents, tax_cents)` or a small dataclass, with `total = net + tax`. |
| 7 | Medium | CONFIRMED | `TAX_TABLE = json.loads(...)` at module import | The table is loaded once at import. | A missing or malformed file crashes import of the whole billing module. A tax-rate update (such as the one the PR cites) does not take effect until every process restarts, so stale rates get charged. | Load lazily or with an explicit reload. Fail clearly with the file path. Document the deploy and restart requirement. |
| 8 | Medium | CONFIRMED (absence) | PR scope: only `proration.py` | No tests are included. The 31st and February cases would have caught #1 immediately. | The regression ships unnoticed. | Add the tests listed in #1, #3, #4 and #5. |
| 9 | Low | UNVERIFIED | `upgrade_on` and `monthly_price_cents` parameters | The function does not control which timezone defines "day D", or that the price passed is the *new* plan's price in integer cents. | An upgrade at 23:30 local time recorded as UTC the next day charges for a different D, and on the 31st/1st boundary it lands in a different month. A float or dollar price (`19.99`) passes through `Decimal(float)`. | Check call sites. Type-check that the price is `int`. Document and enforce that `upgrade_on` is the customer-local date. |
| 10 | Low | CONFIRMED | `json.loads` then `Decimal(str(...))` | Rates go through float. `str(float)` round-trips short decimals correctly, so the practical risk is low, but it is fragile. | A rate like `0.1` is fine. A long rate could pick up float artifacts. | `json.loads(..., parse_float=Decimal)`. |

## WHAT HOLDS UP

- The inclusive day count (`- day + 1`) correctly includes day D, as the request requires.
- Computation uses `Decimal` throughout. There is no binary-float arithmetic on money once inside the function.
- Tax is applied after proration, which is the correct order.
- The table path `Path(__file__).parent / "tax_table.json"` resolves to `billing/tax_table.json`, which matches the PR description.

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| "Tax rates come from billing/tax_table.json (see the update in a1b2c3d4e5)" | Open the file. Check that a `"default"` key exists, that rates are fractions, and that region keys match whatever the callers pass. |
| "Rounding follows the fix in that commit" | Diff `a1b2c3d4e5` against the two `quantize` calls: rounding order, rounding mode, and rounding unit. |
| Callers pass the new plan's price in integer cents, and a customer-local date | Grep the call sites of `prorated_cents`. |

## QUESTIONS FOR THE AUTHOR

1. Was the 30-day month intentional, for example a business-defined "billing month"? If so, the request's "calendar month" is wrong. If not, #1 stands.
2. What does `a1b2c3d4e5` specify for rounding order and mode?
3. Should an unknown region fail, or fall back to a default? Does finance or tax sign off on the fallback?
4. Do invoices need the tax amount separately?

## DECISION-MAKER SUMMARY

Do not merge. The fixed 30-day denominator mischarges almost every mid-month upgrade, by up to about 2.8× in February, and makes upgrades on the 31st free. The fix is small (`calendar.monthrange`) but needs tests. Before re-review, someone must check the tax table and the referenced rounding commit, because silent default-region fallback and an unchecked rate format could produce wrong tax on every charge.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "proration.py: DAYS_IN_BILLING_MONTH = 30; remaining_days and share computation", "scenario": "Fixed 30-day month instead of calendar month: upgrade on Jan 31 at 3000c charges 0 (should be ~97c); Jan 15 charges 1600c (should be 1645c); Feb 28 2026 charges 300c (should be 107c).", "fix": "Use calendar.monthrange(d.year, d.month)[1] for both remaining days and denominator; add tests for 1st/15th/30th/31st, Feb 28 non-leap, Feb 28/29 leap, 30-day months."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "proration.py: TAX_TABLE.get(region, TAX_TABLE[\"default\"])", "scenario": "Unknown, misspelled, None, or case-mismatched region silently gets the default tax rate, producing incorrect tax with no signal.", "fix": "Raise or alert on unknown region; make region required; test that an unknown region raises."},
    {"severity": "High", "evidence_level": "UNVERIFIED", "location": "proration.py: TAX_TABLE[\"default\"] eager lookup; billing/tax_table.json (not supplied)", "scenario": "Missing 'default' key makes every call raise KeyError; rates stored as percentages (8.25) multiply the charge by ~9.25.", "fix": "Inspect tax_table.json; validate at load that 'default' exists and every rate is 0 <= r < 1."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "proration.py: two quantize(..., ROUND_HALF_UP) calls", "scenario": "Double rounding (net, then total) and half-up mode may differ from the rule in commit a1b2c3d4e5, giving 1c discrepancies versus ledger and tax reports.", "fix": "Compare against commit a1b2c3d4e5; add golden tests at .5c boundaries."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "proration.py: return statement", "scenario": "Only the combined total is returned, so invoices and tax reports cannot itemize tax, or recompute it with inconsistent rounding.", "fix": "Return net_cents and tax_cents separately."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "proration.py: remaining_days < 0 guard", "scenario": "The guard is unreachable (day <= 31); the 31st yields 0 days silently, which masks the main bug.", "fix": "Remove the guard; after the fix, assert 1 <= remaining <= days_in_month."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "proration.py: module-level TAX_TABLE load", "scenario": "A missing or malformed file crashes module import; tax-rate updates are not picked up until processes restart, so stale rates are charged.", "fix": "Lazy or explicit reload with a clear error; document the restart requirement."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "PR scope: no test files", "scenario": "No tests cover month-length, leap-year, region, or rounding cases; the day-31 free upgrade would ship unnoticed.", "fix": "Add the parametrized tests listed above."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "location": "proration.py: upgrade_on and monthly_price_cents parameters / call sites", "scenario": "A UTC-vs-local date shifts D across a month boundary; a float or dollar price passed in yields a wrong amount.", "fix": "Check call sites; enforce int cents and a customer-local date."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "proration.py: json.loads then Decimal(str(rate))", "scenario": "Rates pass through float; usually exact via str(), but fragile for long rates.", "fix": "json.loads(..., parse_float=Decimal)."}
  ]
}
```