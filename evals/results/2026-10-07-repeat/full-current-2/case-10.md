**Note:** No tools were available in this session, so nothing was run. The arithmetic below was traced by hand. This was a single reviewer with no fresh subagent and no cross-vendor seats.

**VERDICT: REWORK.** The code prorates over a fixed 30-day month instead of the calendar month the request specifies. Customers are overcharged in February, charged nothing on the 31st, and mispriced most other days.

**CONFIDENCE: medium.** The core proration defect is confirmed by tracing the code. The tax and rounding assessment is limited because `billing/tax_table.json` and commit `a1b2c3d4e5` were not supplied, and no code or tests could be run.

**INPUTS LEDGER:**
- Seen: request.md, context.md, `billing/proration.py`.
- Not seen: `billing/tax_table.json`. **This matters.** The rate format (fraction or percent), the presence of a `"default"` key and region coverage all determine whether the tax is right.
- Not seen: commit `a1b2c3d4e5`. **This matters.** The PR says rounding "follows the fix in that commit", so whether the code conforms cannot be checked.
- Not seen: any tests. **This matters.** Per context, the PR changes only `proration.py`, so the PR appears to include no tests.

**SEATS AND GATE:** One reviewer ran: this instance, with no tools. No cross-vendor seats were used because none were requested and none were available. Sensitivity gate: the code holds no personal data, credentials or confidential records, so the gate passed.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (hand trace) | B | `proration.py` `DAYS_IN_BILLING_MONTH = 30`, `remaining_days = 30 - upgrade_on.day + 1`, `share = remaining/30` | The request says "from D to the end of that month". The code uses a fixed 30-day month for both the remaining days and the denominator. | $30 plan (3000¢), no tax: **2026-02-28**: code charges 300¢ for 3 days, but 1 day of 28 is 107¢ (2.8× overcharge). **2026-02-15**: code 1600¢, correct 1500¢. **2026-01-31**: code 0¢ (free upgrade), correct 97¢. **2026-01-02**: code 2900¢, correct 2903¢. Every month that is not 30 days long is wrong. | Use `days_in_month = calendar.monthrange(d.year, d.month)[1]`, `remaining = days_in_month - d.day + 1` and `share = remaining / days_in_month`. Test the 1st, 15th and last day of Feb 2026, Feb 2028 (leap year), a 30-day month and a 31-day month. | confirmed. Defender's case: "30-day billing month is a house convention". Refuted by the request's explicit "end of that month". A zero charge on the 31st cannot be intended under any convention. |
| 2 | High | PROBABLE | B | `TAX_TABLE.get(region, TAX_TABLE["default"])` | An unknown or misspelled region silently gets the default rate. The request says "tax for their region". | A new region like `"CA-QC"`, or a casing mismatch like `"de"` vs `"DE"`, is missing from the table. That customer is billed at the default rate with no error or log. Undercollecting is a tax liability, and overcollecting is a customer harm. | Raise on unknown regions, or log and alert, and make `"default"` an explicit opt-in. Test that an unknown region raises. | confirmed. Defender's case: "default is the intended catch-all". That may hold for untaxed regions, but a silent fallback cannot tell "intentionally default" apart from "data missing". |
| 3 | High | UNVERIFIED | B | `tax_rate = Decimal(str(TAX_TABLE.get(...)))`, `net * (1 + tax_rate)` | The code assumes rates are fractions (`0.0825`). The table was not supplied. | If the table stores percents (`8.25`), every charge is about 9.25× the net amount. If `"default"` is absent, the expression raises `KeyError` on every call, even for valid regions, because the default argument is evaluated eagerly. | Supply the table. Add a load-time assertion that every rate is in [0, 1) and that `"default"` exists. Test a known region against the expected cents. | confirmed as a finding of missing input. The severity rests on the unseen file. |
| 4 | High | CONFIRMED (per context: only `proration.py` changed) | B | PR file list | The PR adds no tests to production billing code. | Finding 1 shipped unnoticed, which is consistent with no date-boundary tests existing. Future regressions will also go unnoticed. | Add tests for finding 1's dates, finding 2's unknown region and rounding at .5 boundaries. Mutate `30` → `31` and confirm the tests go red. | confirmed |
| 5 | Medium | UNVERIFIED | B / R | The two `quantize(... ROUND_HALF_UP)` calls; the single returned `int` | Net and gross are each rounded, and tax is never computed or returned as its own amount. The PR claims this "follows the fix in a1b2c3d4e5", which was not seen. | An invoice usually shows net and tax as separate lines. If the invoice recomputes tax as `round(net * rate)`, then net + tax can differ by 1¢ from this function's total. Some jurisdictions also require tax to be shown or rounded per line. | Return `(net_cents, tax_cents)` with `tax = round(net * rate)` and `total = net + tax`. Show the commit `a1b2c3d4e5` diff and confirm the rounding rule it sets. | — |
| 6 | Medium | PROBABLE | B | `upgrade_on.day` | The day comes from a bare date in an unstated timezone. | An upgrade at 23:30 on Jan 31 in New York is Feb 1 in UTC. The customer is billed for the wrong month's remainder: a full February instead of one January day. | Document and enforce the timezone, either the customer's billing timezone or UTC, at the call site. Test a timestamp near midnight. | — |
| 7 | Low | CONFIRMED | B | `if remaining_days < 0: remaining_days = 0` | This is dead code. `day ≤ 31` gives a minimum of 0, so the condition never fires. It looks like a guard but hides the day-31 zero-charge path from finding 1. | A reader assumes edge cases are handled. | Remove it once finding 1 is fixed, and validate inputs instead. | — |
| 8 | Low | PROBABLE | B | Module level `TAX_TABLE = json.loads(...)` | The table loads at import time. | A missing or malformed file breaks import of the whole billing module. A table update needs a process restart to take effect. | Load the table lazily or through a config service, and validate it on load. | — |
| 9 | Low | PROBABLE | B | `Decimal(monthly_price_cents)` | A float price passes through without error, and Decimal carries the binary-float error into the charge. Negative prices are accepted. | A caller passes `2999.99` or `-100`, and the charge is wrong or negative. | Assert the price is an `int` ≥ 0. | — |

## WHAT HOLDS UP
- Using `Decimal` for money, and `Decimal(str(rate))` rather than converting the float directly, is correct.
- `ROUND_HALF_UP` is an explicit, deterministic rounding mode.
- `remaining = days - D + 1` correctly counts day D itself. Only the month length is wrong.
- The table path (`Path(__file__).parent / "tax_table.json"`) resolves to `billing/tax_table.json`, which matches the PR description.
- The code charges the new plan's price for the remaining days with no credit for the old plan. That matches the request as worded; see question 3.

## UNVERIFIED CLAIMS
- "Tax rates come from billing/tax_table.json." To settle it, supply the file and check the rate format, the `"default"` key and region coverage.
- "Rounding follows the fix in commit a1b2c3d4e5." To settle it, supply the commit diff and compare it against the two quantize calls.

## QUESTIONS FOR THE AUTHOR
1. Is the daily rate meant to be `price / days_in_calendar_month`, as the request implies, or a deliberate 30-day convention? If it is a 30-day convention, how should the 31st be billed?
2. Are tax table rates fractions or percents, and what should happen for a region that is not in the table?
3. Is any credit for the unused portion of the old plan handled elsewhere? It is not in the request or this PR.
4. What timezone is `upgrade_on` in?

## DECISION-MAKER SUMMARY
Do not merge. The code divides every month into 30 days, so February upgrades are overcharged by up to about 2.8×, upgrades on the 31st are free, and other days are slightly off. The tax handling also cannot be confirmed without the tax table and the referenced commit. Merging as is puts wrong charges on real customer invoices and may misstate collected tax.

## OWNER SUMMARY
The change that charges customers for part of a month when they upgrade calculates the amount wrongly in most months. Some customers would pay too much, and some who upgrade on the last day of a 31-day month would pay nothing. It needs a fix, tests, and a check of the tax-rate file it depends on before it goes live.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-instance-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "source code only; no personal or confidential data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py: DAYS_IN_BILLING_MONTH = 30 and remaining_days/share lines",
     "scenario": "Fixed 30-day month instead of calendar month: 3000c plan upgraded 2026-02-28 charged 300c instead of 107c; 2026-01-31 charged 0c instead of 97c; 2026-02-15 charged 1600c instead of 1500c.",
     "fix": "Use calendar.monthrange(year, month)[1] for remaining days and denominator; test first/mid/last day of Feb (leap and non-leap), 30- and 31-day months.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "B", "location": "proration.py: TAX_TABLE.get(region, TAX_TABLE[\"default\"])",
     "scenario": "Unknown or misspelled region silently billed at default tax rate; under- or over-collection with no error.",
     "fix": "Raise or alert on unknown region; test that an unknown region raises.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "B", "location": "proration.py: tax_rate / net * (1 + tax_rate); billing/tax_table.json (not supplied)",
     "scenario": "If rates are stored as percents, charges are ~9.25x net; if 'default' key is missing, every call raises KeyError.",
     "fix": "Supply the table; assert 0 <= rate < 1 and 'default' present at load; test a known region's expected cents.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "PR file list (only billing/proration.py changed)",
     "scenario": "No tests for production billing; the month-length bug shipped undetected and regressions will too.",
     "fix": "Add date-boundary, region and rounding tests; mutate 30->31 to confirm they go red.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "proration.py: two quantize calls; single int return",
     "scenario": "Tax not returned separately; invoice net+tax lines can differ by 1c from the total; conformity with commit a1b2c3d4e5 unknown.",
     "fix": "Return (net_cents, tax_cents) with total = net + tax; check against commit a1b2c3d4e5.", "status": ""},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "proration.py: upgrade_on.day",
     "scenario": "Timezone of upgrade_on unstated; a near-midnight upgrade is billed against the wrong month.",
     "fix": "Define and enforce the billing timezone at the call site; test near-midnight timestamps.", "status": ""},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py: if remaining_days < 0",
     "scenario": "Dead guard (minimum is 0) that implies edge cases are handled while day 31 yields a zero charge.",
     "fix": "Remove after the calendar fix; validate inputs instead.", "status": ""},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "proration.py: module-level TAX_TABLE load",
     "scenario": "Missing or malformed file breaks module import; table updates need a restart.",
     "fix": "Load lazily with validation.", "status": ""},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "proration.py: Decimal(monthly_price_cents)",
     "scenario": "Float or negative price accepted, producing an imprecise or negative charge.",
     "fix": "Assert price is a non-negative int.", "status": ""}
  ]
}
```