# Redteam Review: PR #214, "Prorate mid-month upgrades"

**Review conditions:** This session has no tools. I traced the code by hand and did not run it. The work was not produced in this conversation, so there is no anchoring to the author's reasoning. `billing/tax_table.json` and commit `a1b2c3d4e5` were not supplied, so every claim that depends on them is unverified.

## Pass 1: Reconstruct

The PR adds `prorated_cents(monthly_price_cents, upgrade_on, region)`. It returns the tax-inclusive charge in integer cents for the rest of the month after an upgrade on `upgrade_on`. It computes `remaining_days / 30` of the monthly price, rounds that to a cent, applies a regional tax rate from a JSON table loaded at import, and rounds again.

For it to be correct, these must hold:
1. A 30-day month is an acceptable stand-in for "the end of that calendar month". It is not.
2. The caller passes the **new** plan's price and the customer's local billing date.
3. `tax_table.json` holds decimal fractions such as `0.08`, not percents such as `8`, and contains a `"default"` key.
4. Every region the caller passes is present in the table.
5. Rounding the net amount and then the gross amount matches the referenced rounding fix.

## Pass 2: Attack (Track B)

**Correctness trace with a $30.00 plan (3000 cents), tax ignored:**

| Upgrade date | Code: days/30 → net | Spec: days to calendar month end → net |
|---|---|---|
| Jan 31 | 0/30 → **0** | 1/31 → 97 |
| Jan 15 | 16/30 → 1600 | 17/31 → 1645 |
| Feb 15 | 16/30 → 1600 | 14/28 → 1500 |
| Feb 28 (non-leap) | 3/30 → **300** | 1/28 → 107 |
| Apr 15 | 16/30 → 1600 | 16/30 → 1600 ✓ |

The code is only correct in 30-day months. It undercharges in 31-day months, including a free upgrade on the 31st, and overcharges in February. The `if remaining_days < 0` guard is dead code: `day` is at most 31, so the minimum value is 0. It looks like it handles month-length edge cases but does not.

## VERDICT

**REWORK.** The core proration ignores calendar month length, so charges are wrong in 8 of 12 months, including zero charges on the 31st and roughly 3x overcharges late in February. The tax path also fails silently on unknown regions.

**CONFIDENCE IN VERDICT:** High for the calendar defect, which I traced line by line. Medium for the tax and rounding findings, because the tax table and commit `a1b2c3d4e5` were not supplied. The code was not executed.

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `DAYS_IN_BILLING_MONTH = 30`; `remaining_days = DAYS_IN_BILLING_MONTH - upgrade_on.day + 1` | Uses a fixed 30-day month. The spec says "end of that calendar month". | 3000-cent plan: upgrade Feb 28 charges 300 instead of 107; upgrade Jan 15 charges 1600 instead of 1645. Every 28-, 29- and 31-day month is mispriced. | Use `days_in_month = calendar.monthrange(d.year, d.month)[1]` for both the numerator and the denominator. Add parametrized tests for Jan, Feb, Feb in a leap year, and Apr on days 1, 15 and last. |
| 2 | Critical | CONFIRMED | Same line, with `day == 31` | An upgrade on the 31st gives `remaining_days = 0`, so the charge is 0. | A customer upgrades on Jan/Mar/May/Jul/Aug/Oct/Dec 31 and gets the new plan's last day free. This can also be exploited by timing upgrades. | Fixed by #1. Add an explicit test for upgrade on the 31st expecting 1/31 of the price. |
| 3 | Low | CONFIRMED | `if remaining_days < 0: remaining_days = 0` | Dead branch, since the value can never be negative. It suggests edge cases are handled when they are not. | Reviewers trust the guard, and finding #2 slips through. | Remove it, or replace it with an assertion after the #1 fix. |
| 4 | High | CONFIRMED (code) / UNVERIFIED (impact) | `TAX_TABLE.get(region, TAX_TABLE["default"])`; `region="default"` | An unknown or misspelled region silently gets the default rate. Callers that omit `region` silently get default tax. Either way the regional tax is wrong and nothing is logged. | The caller passes `"CA-QC"` while the table key is `"QC"`. The customer is taxed at the default rate, which creates tax under- or over-collection and possible legal exposure. | Raise on an unknown region, or at least log and alert. Make `region` required. Test that an unknown region raises. |
| 5 | High | UNVERIFIED | `TAX_TABLE` contents, the `(1 + tax_rate)` line | The code assumes rates are fractions. If the table stores percents (e.g. `8`), the gross is 9x the net. | Table has `"default": 8.25`, so a 1600 net becomes 14800. | Show the table. Validate at load time that every rate is in `0 <= r < 1`. Add a test using the real table. |
| 6 | High | PROBABLE | `TAX_TABLE["default"]` as the `.get` fallback | The fallback argument is evaluated on every call. If the table has no `"default"` key, every call raises `KeyError`, even for valid regions. | The table update in `a1b2c3d4e5` renamed or removed `default`, and all upgrades now fail. | Validate required keys at load time. Add a test that loads the real file. |
| 7 | High | CONFIRMED | PR scope: only `billing/proration.py` changed | The PR adds no tests to production billing logic. Nothing exercises month length, the 31st, leap years, regions or rounding. | Findings #1 and #2 would have been caught by any calendar test, and regressions will go unnoticed. | Add a unit test file covering the cases in #1, #2, #4 and #8. |
| 8 | Medium | UNVERIFIED | Two `quantize(..., ROUND_HALF_UP)` calls | Net and gross are each rounded. The PR says rounding "follows the fix in" `a1b2c3d4e5`, which was not supplied. Rounding mode (HALF_UP vs HALF_EVEN) and order could both differ from that fix or from jurisdictional rules. | Totals differ by ±1 cent from invoices or ledger reconciliation produced elsewhere. | Show the commit. Add a test pinning a known half-cent case to the expected value from finance or tax rules. |
| 9 | Medium | PROBABLE | Return value `int(...)` | Only the gross total is returned. Invoices usually need the net and tax lines separately, and callers that recompute tax will diverge because of the double rounding. | An invoice shows tax as `gross - price*share`, which mismatches the ledger by a cent. | Return `(net, tax)` or a small dataclass. Confirm what invoice callers need. |
| 10 | Medium | UNVERIFIED | `upgrade_on` parameter | The date's time zone is the caller's responsibility. A UTC date near midnight can shift the day, or even the month. | A customer upgrades at 23:30 local on Jan 31 (Feb 1 UTC) and is billed for Feb. | Document and enforce that `upgrade_on` is the date in the account's billing time zone, and check the call sites. |
| 11 | Medium | UNVERIFIED | Caller / `monthly_price_cents` | The spec requires the **new** plan's price. The function cannot enforce this, and no call site was supplied. A float price would also pass through `Decimal(float)` with binary artifacts. | A caller passes the old plan's price and every upgrade is undercharged. | Review call sites. Assert that `monthly_price_cents` is a non-negative `int`. |
| 12 | Low | CONFIRMED | Module-level `TAX_TABLE = json.loads(...)` | Loaded at import, so a missing or malformed file crashes import, and rate updates need a process restart. | A tax rate changes and running workers keep charging the old rate until redeployed. | Acceptable if deploys gate table changes. Otherwise load it lazily or with a version. Document the behaviour either way. |

## WHAT HOLDS UP

- Counting the upgrade day as inclusive (`+ 1`) matches "from D to the end".
- Using `Decimal` with string conversion of the tax rate (`Decimal(str(...))`) avoids float drift in the arithmetic.
- The table path `Path(__file__).parent / "tax_table.json"` resolves to `billing/tax_table.json`, which matches the PR description.
- The arithmetic is correct in 30-day months (Apr, Jun, Sep, Nov).

## UNVERIFIED CLAIMS

- "Tax rates come from billing/tax_table.json (see the update in commit a1b2c3d4e5)." To confirm, provide the file and the diff, and check the rate format, the `default` key, and region key naming against what callers send.
- "Rounding follows the fix in that commit." To confirm, provide the commit and compare its rounding mode and order to the two `quantize` calls.
- That callers pass the new plan's price and a date in the billing time zone. To confirm, review the call sites.

## QUESTIONS FOR THE AUTHOR

1. Was 30-day proration a deliberate business decision that conflicts with the "calendar month" spec, or an oversight?
2. What format are the rates in `tax_table.json`, and does it contain `"default"`?
3. What does `a1b2c3d4e5` specify for rounding: the mode, and whether tax is rounded per line or on the total?
4. Should an unknown region fail closed, or fall back to default?

## DECISION-MAKER SUMMARY

Do not merge. The proration uses a fixed 30-day month, so most months are mispriced, upgrades on the 31st are free, and late-February upgrades are overcharged roughly threefold. Require the calendar-month fix, strict region handling, and tests, and have someone verify the tax table and rounding commit before this touches production billing.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "proration.py: DAYS_IN_BILLING_MONTH = 30; remaining_days = DAYS_IN_BILLING_MONTH - upgrade_on.day + 1", "scenario": "Fixed 30-day month instead of calendar month: 3000-cent plan upgraded Feb 28 charges 300 instead of 107; Jan 15 charges 1600 instead of 1645.", "fix": "Use calendar.monthrange(year, month)[1] for numerator and denominator; parametrized tests across 28/29/30/31-day months."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "proration.py: remaining_days computation when upgrade_on.day == 31", "scenario": "Upgrade on the 31st yields remaining_days = 0 and a zero charge for a day of service.", "fix": "Resolved by calendar-month fix; add test expecting 1/31 of price on the 31st."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "proration.py: TAX_TABLE.get(region, TAX_TABLE['default']); region='default'", "scenario": "Unknown/misspelled or omitted region silently taxed at default rate, causing wrong tax collection.", "fix": "Make region required; raise or alert on unknown region; test it."},
    {"severity": "High", "evidence_level": "UNVERIFIED", "location": "proration.py: (Decimal(1) + tax_rate) with tax_table.json contents", "scenario": "If rates are stored as percents (e.g. 8.25), gross becomes ~9x net.", "fix": "Validate 0 <= rate < 1 at load; test against the real table."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "proration.py: TAX_TABLE['default'] evaluated as .get fallback", "scenario": "If the table lacks 'default', every call raises KeyError, even for valid regions.", "fix": "Validate required keys at load; test loading the real file."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "PR scope: only billing/proration.py changed", "scenario": "No tests for billing logic; calendar and tax defects ship undetected.", "fix": "Add unit tests for month lengths, the 31st, leap years, regions, rounding."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "proration.py: two quantize(..., ROUND_HALF_UP) calls", "scenario": "Rounding order/mode may differ from commit a1b2c3d4e5 or tax rules, causing 1-cent reconciliation mismatches.", "fix": "Provide the commit; pin a half-cent test case to the expected value."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "proration.py: return int(...) gross only", "scenario": "Invoice callers recompute tax separately and diverge by a cent from the ledger.", "fix": "Return net and tax separately; confirm caller needs."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "proration.py: upgrade_on parameter", "scenario": "A UTC date near midnight shifts the billing day or month for the customer.", "fix": "Require a date in the account billing time zone; check call sites."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "callers of prorated_cents / monthly_price_cents", "scenario": "Caller passes the old plan's price, or a float price, causing undercharge or binary artifacts.", "fix": "Review call sites; assert monthly_price_cents is a non-negative int."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "proration.py: if remaining_days < 0", "scenario": "Dead branch (minimum value is 0) implies edge-case handling that does not exist.", "fix": "Remove it or replace it with an assertion after the calendar fix."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "proration.py: module-level TAX_TABLE load", "scenario": "Missing or malformed file crashes import; rate changes need a restart.", "fix": "Document or gate via deploy, or load lazily with versioning."}
  ]
}
```