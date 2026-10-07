**Same-context review, no tools. Re-run in a fresh session with the repository open before relying on this for production billing.**

VERDICT: **REWORK**. The function prorates over a fixed 30-day month instead of the calendar month the request specifies, so it misbills customers in every month that is not 30 days long, including charging nothing for upgrades on the 31st.

CONFIDENCE: **medium**. The day-count defect is confirmed by hand trace. Confidence is limited by:
- no tools: nothing was executed, and arithmetic was done by hand;
- `billing/tax_table.json` and commit `a1b2c3d4e5` were not supplied;
- no tests or call sites were supplied;
- this is a same-context review.

INPUTS LEDGER:

| Item | Status | Matters? |
|---|---|---|
| Original request (request.md) | seen | n/a |
| Context (context.md) | seen | n/a |
| `billing/proration.py` | seen | n/a |
| `billing/tax_table.json` | **not seen** | **Yes.** The tax correctness, the format of the rate (0.0825 or 8.25), and whether a `"default"` key exists all depend on it. |
| Commit `a1b2c3d4e5` ("rounding fix") | **not seen** | **Yes.** I cannot check whether the rounding here matches the fix the PR description cites. |
| Tests for this PR | **not seen**, and none listed in the changed files | Yes. There is no evidence that any behavior was exercised. |
| Callers of `prorated_cents` | not seen | Partly. They decide which price is passed in, the time zone of `upgrade_on`, and the region string. |

SEATS AND GATE:
- **Gate:** no personal, financial-record or credential data in the work, so the gate passed.
- **Seats:** only this local reviewer ran, because no subagent or cross-vendor tooling was available in this session. No seats were refused.

## Pass 1: Reconstruct

`prorated_cents` returns the tax-inclusive charge in cents for the rest of the month after an upgrade on `upgrade_on`. It works in four steps:
1. Computes remaining days against a constant 30-day month.
2. Multiplies the monthly price by `remaining/30` and rounds to whole cents.
3. Looks up a regional tax rate, falling back to `"default"`.
4. Applies the tax and rounds again.

For this to be correct, all of the following must hold:
- (a) "Month" means a 30-day month. The request says calendar month, so this already conflicts.
- (b) The caller passes the new plan's price.
- (c) Tax rates are stored as fractions.
- (d) Every billable region is present in the table under the exact key callers use.
- (e) Rounding the net amount and then rounding the gross amount matches the referenced rounding fix.
- (f) The `upgrade_on` date is computed in the correct time zone.

Track: **B** (with an R angle, since this produces customer charges).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED (hand trace) | B/R | `proration.py:8` (`DAYS_IN_BILLING_MONTH = 30`), `:13`, `:16` | The request says "days from D to the end of **that** calendar month", but the code uses a fixed 30 days for both the remaining-day count and the denominator. | **Feb 15, 2026** (28-day month), price 3000¢: correct is 14/28 × 3000 = **1500¢** net; code gives 16/30 × 3000 = **1600¢**, a 6.7% overcharge. **Feb 28**, price 2800¢: correct 100¢, code 280¢ (2.8×). **Jan 2**, price 3100¢: correct 30/31 × 3100 = 3000¢, code 29/30 × 3100 = 2997¢. Every month with 28, 29 or 31 days misbills, and February overcharges. | Use `calendar.monthrange(upgrade_on.year, upgrade_on.month)[1]` as `days_in_month`, then `remaining = days_in_month - day + 1` and `share = remaining / days_in_month`. Add parametrized tests for Feb 28 and 29 (leap 2028), Feb 15, Jan 1, Jan 31, Apr 30 and Dec 31. | confirmed. The strongest defense is that a 30-day convention is a deliberate business rule, but the request explicitly says calendar month and nothing in the PR documents such a rule. |
| 2 | **Critical** | CONFIRMED (hand trace) | B/R | `proration.py:13-15` | When the upgrade is on the 31st, `remaining_days = 30 - 31 + 1 = 0`, so the charge is 0 even though one day is owed. The `< 0` guard can never fire, because `day ≤ 31`, so it is dead code that suggests the author reasoned about this edge but missed it. | A customer upgrades on Jan 31, Mar 31, May 31 and so on, and gets the new plan for the rest of the month free. If downstream code treats a 0¢ invoice as "no charge needed", the upgrade may also go unrecorded. | This is fixed by Fix 1. Add a test asserting that Jan 31 at 3100¢ gives 100¢ net, and remove the dead guard or turn it into an assertion. | confirmed. This is the same root cause as #1 but a distinct customer-visible outcome. |
| 3 | **High** | CONFIRMED (code behavior); impact PROBABLE | B/R | `proration.py:18` (`TAX_TABLE.get(region, TAX_TABLE["default"])`) | Any region not found in the table silently gets the default rate. Causes include a typo, a case mismatch ("CA" vs "ca"), a new region, or `None` passed explicitly. The caller's own default is also `"default"`, so a caller that forgets the argument is taxed at the default rate with no signal. | A customer in a region missing from the table, or keyed differently, is under-taxed (a liability for the business) or over-taxed (harm to the customer), with no error or log. The request requires "tax for their region". | Raise on an unknown region, or at least log and alert. Make `region` a required argument. Normalize keys. Add a test that an unknown region raises. | confirmed as behavior. The defense is that a default rate is intentional, but even so, silently substituting it with no logging is unsafe for a tax calculation. |
| 4 | Medium | UNVERIFIED (table not seen) | B | `proration.py:8`, `:18-19` | The code assumes rates are stored as fractions (0.0825). If the table stores percentages (8.25), the total becomes about 9.25× the net. If the table lacks a `"default"` key, `TAX_TABLE["default"]` is evaluated eagerly on **every** call and raises `KeyError`, even for known regions. | The table format from commit a1b2c3d4e5 does not match the code's assumption, and charges are wildly wrong or every call fails. | Show the table and the commit. Add a load-time check that every rate satisfies 0 ≤ rate < 1 and that `"default"` exists. Add one test per real region against a known expected total. | not a High/Critical candidate |
| 5 | Medium | UNVERIFIED | B | `proration.py:17`, `:19` | The code rounds twice: the net to whole cents, then the gross. Whether this matches "the fix in commit a1b2c3d4e5" cannot be checked. The function also returns only the total, so an invoice cannot show a separate tax line that reconciles with net plus tax. | The referenced fix may round the tax per line, or once at the end. A 1¢ mismatch per invoice then appears against the tax ledger and reconciliation fails. | Return `(net, tax, total)` with `total == net + tax` by construction. Document the rounding rule and cite the commit. Add tests at half-cent boundaries. | n/a |
| 6 | Medium | CONFIRMED (changed-files list) | B | PR file list: only `billing/proration.py` | No tests ship with a production billing change. | Findings #1 and #2 would have been caught by any test with a non-30-day month, and regressions will go unnoticed. | Add the parametrized calendar and tax tests described above, and confirm each test fails against the current code before the fix is applied. | n/a |
| 7 | Low | PROBABLE | B | `proration.py:8` | The tax table is read once at import time. A missing or bad file breaks the import of the whole billing module, and rate updates need a process restart. | A tax-rate change is deployed as a data change, and running workers keep charging the old rate. | Load the table through a validated loader with an explicit reload or versioning strategy, and record which table version was used on each invoice. | n/a |
| 8 | Low | UNVERIFIED | B | `proration.py:11` signature | The function does not specify the time zone of `upgrade_on` and does not validate the price (negative or `None`). | An upgrade at 23:30 local time on the 31st becomes the 1st in UTC, or the reverse, which changes the charge by roughly a full month. | Document that `upgrade_on` is a date in the customer's billing time zone. Reject negative prices. | n/a |

## WHAT HOLDS UP
- Money is handled with `Decimal`, and `Decimal(str(rate))` avoids errors from converting floats.
- An upgrade on day 1 correctly charges the full month.
- The function charges at whatever price it is given and does not invent a credit for the old plan. That matches the literal request, which mentions no credit.
- The `Path(__file__).parent` lookup resolves to `billing/tax_table.json`, which is consistent with the PR description.

## UNVERIFIED CLAIMS
- **"Tax rates come from billing/tax_table.json":** I need the file to check the rate format, region keys and the `"default"` key.
- **"Rounding follows the fix in that commit":** I need the diff of a1b2c3d4e5 to compare against `:17` and `:19`.
- **That callers pass the new plan's price, the correct region key and a date in the billing time zone:** I need the call sites.

## QUESTIONS FOR THE AUTHOR
1. Is a 30-day month an intentional business rule? If so, where is it documented, given that the request says calendar month?
2. What does the tax table contain (rate format, keys, `"default"`), and what exactly did commit a1b2c3d4e5 change about rounding?
3. Should an unknown region fail, or fall back to a default? Who approved the fallback?

## DECISION-MAKER SUMMARY
Do not merge. The proration uses a fixed 30-day month, so February upgrades are overcharged by up to 2.8× and upgrades on the 31st are free. Unknown regions are also silently taxed at a default rate. If shipped as is, customers will be misbilled from the first non-30-day month, and refunds, a tax-reconciliation gap and possible complaints or regulatory attention will follow.

## OWNER SUMMARY
This change works out upgrade charges as if every month had 30 days. That overcharges customers who upgrade in February and gives a free period to anyone who upgrades on the 31st. It can also apply the wrong sales tax without any warning when a customer's region is not recognized. It should be fixed and tested against real calendar months and the actual tax rates before it goes live.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "tests for PR #214", "status": "not_seen", "matters": true},
    {"item": "callers of prorated_cents", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "source code only; no personal, financial-record or credential data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py:8,13,16",
     "scenario": "Fixed 30-day month instead of the calendar month: Feb 15 2026 at 3000c bills 1600c net instead of 1500c; Feb 28 at 2800c bills 280c instead of 100c; every 28/29/31-day month misbills.",
     "fix": "Use calendar.monthrange(year, month)[1] for both the remaining-day count and the denominator; add parametrized tests for Feb 28/29, Jan 1/31, Apr 30, Dec 31.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py:13-15",
     "scenario": "Upgrade on day 31 gives remaining_days = 0, so the customer is charged 0c for the day owed; the <0 guard is dead code.",
     "fix": "Fixed by the calendar-month change; add a test that Jan 31 at 3100c gives 100c net; remove or assert the dead guard.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "proration.py:11,18",
     "scenario": "Unknown, misspelled or differently-cased region, or an omitted region argument, silently gets the default tax rate, so the customer is under- or over-taxed with no error.",
     "fix": "Make region required, normalize keys, raise or alert on unknown region, test that an unknown region raises.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "proration.py:8,18-19",
     "scenario": "If the table stores percentages, totals are about 9.25x the net; if the 'default' key is missing, every call raises KeyError because it is evaluated eagerly.",
     "fix": "Validate at load time that 0 <= rate < 1 and that 'default' exists; add per-region tests with known expected totals.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "proration.py:17,19",
     "scenario": "Double rounding may not match the rounding fix in commit a1b2c3d4e5; with no separate tax amount, invoice tax lines can fail to reconcile by 1c.",
     "fix": "Return (net, tax, total) with total = net + tax; document the rounding rule; test half-cent boundaries.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "PR #214 file list",
     "scenario": "No tests ship with a production billing change; findings 1 and 2 would have been caught by any non-30-day-month test.",
     "fix": "Add calendar and tax tests and confirm each fails against the current code before the fix.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "proration.py:8",
     "scenario": "Tax table loaded at import: a missing file breaks module import, and rate updates are not picked up until restart.",
     "fix": "Use a validated, versioned loader and record the table version on each invoice.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "B", "location": "proration.py:11",
     "scenario": "Time zone of upgrade_on is unspecified; a UTC vs local date near month end shifts the charge by about a full month; negative price is accepted.",
     "fix": "Document upgrade_on as a date in the customer's billing time zone; validate the price.", "status": "n/a"}
  ]
}
```
