VERDICT: **REWORK.** The code divides every month into 30 days, but the request asks for proration over the actual calendar month. This overcharges every February upgrade after day 1, charges nothing for a day-31 upgrade, and misprices most other days in 31-day months.

CONFIDENCE: **medium.** The core defect is confirmed by hand-tracing the arithmetic, but I could not run anything in this session. Tax correctness and the rounding claim depend on `billing/tax_table.json` and commit `a1b2c3d4e5`, and neither was supplied.

INPUTS LEDGER:
- **Seen:** the original request (`request.md`), the context (`context.md`), and `billing/proration.py`, the only changed file in the PR.
- **Not seen:** `billing/tax_table.json`. **Matters**: it determines the rate values, their units, which regions exist and whether a `default` key exists.
- **Not seen:** commit `a1b2c3d4e5`. **Matters**: the PR says the rounding "follows the fix in that commit", and that claim cannot be checked.
- **Not seen:** the callers of `prorated_cents`. **Matters**: how `region`, `upgrade_on` and the price are passed in.
- **Not seen:** any tests. None appear in the changed-files list.

COVERAGE:
- **Checked:**
  - `billing/proration.py`, the whole file.
  - The function `prorated_cents`.
  - The `TAX_TABLE` load at import (line 7).
  - The constant `DAYS_IN_BILLING_MONTH` (line 8).
  - The request's requirements: days D through end of month inclusive, new plan price, tax by region.
- **Not checked:**
  - `billing/tax_table.json` (not supplied).
  - Commit `a1b2c3d4e5` (not supplied).
  - Callers and invoice rendering (not supplied).
  - Any test suite (none supplied).

SEATS AND GATE: one reviewer only, with no tools and no subagent, so nothing was executed. The work was not written in this conversation. Sensitivity gate: there is no personal or confidential data, but no external seats were available anyway.

## Pass 1: Reconstruct

The function claims to return the charge, in cents and including tax, for upgrading on `upgrade_on`. It takes the share of the month remaining, applies it to the new monthly price, rounds, adds the regional tax rate and rounds again.

For it to be correct, all of these must be true:
- the remaining share must be measured against the real length of that calendar month;
- `region` must always resolve to that customer's actual rate;
- the table values must be fractional rates, such as 0.0725 rather than 7.25;
- the two-step rounding must match the billing and tax rules.

Unstated assumptions:
- every month has 30 days (false);
- an unknown region may safely fall back to `default`;
- the caller passes the date in the correct time zone and the price as integer cents.

Track: B, with an R angle because tax is collected from customers.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (hand-traced) | B | `billing/proration.py:8`, `:13-16` | Every month is treated as 30 days. The request says days D to the end of *that calendar month*. | See the table below. Only day 1 of any month and the 30-day months come out right. | See below. | a✓ b✓ c✓ d✓ |
| F2 | Medium | PROBABLE | B/R | `billing/proration.py:11`, `:18` | An unknown or mis-cased region silently gets the `default` rate. The parameter itself defaults to `"default"`, so a caller that omits it also gets the default rate. | Table `{"default": 0, "CA": 0.0725}`. The call `prorated_cents(3000, date(2026,3,1), "ca")` returns 3000, but the expected value is 3218 (3000 × 1.0725 = 3217.5, rounded half-up). The customer is under-taxed and no error is raised. | Remove the parameter default. Normalise the region and raise on an unknown region (`TAX_TABLE[region]`), or log and fail closed. **Repro:** the call above. | a✓ b✗ c✓ d✗ |
| F3 | Medium | CONFIRMED (changed-files list) | B | PR #214 (only `billing/proration.py` changed) | Production billing logic ships with no tests. F1 is exactly the class of bug a single February date would catch. | The next edit to the proration formula or rounding reaches customers unchecked. | Add parametrised tests covering Feb 28 (2026), Feb 29 (2028), Mar 31, Mar 16, the 1st of a month, a 30-day month, an unknown region, and a known region with nonzero tax. Patch `TAX_TABLE` in the tests. Confirm the tests fail on the current code before applying the fix. | a✓ b✓ c✗ d✗ |

**F1 failure scenarios.** Price is 3000 cents and tax is 0.

| Upgrade date | Code charges | Correct charge |
|---|---|---|
| Feb 28, 2026 | 300 (3/30) | 107 (1/28), about 2.8× overcharge |
| Feb 15, 2026 | 1600 (16/30) | 1500 (14/28) |
| Feb 29, 2028 | 200 (2/30) | 103 (1/29) |
| Mar 16 | 1500 (15/30) | 1548 (16/31) |
| Mar 31 | 0 (`remaining_days` = 0) | 97 (1/31), a free day |

The `< 0` guard at lines 14-15 can never trigger, because a date's day is at most 31.

**F1 fix:**
```python
days = calendar.monthrange(upgrade_on.year, upgrade_on.month)[1]
remaining = days - upgrade_on.day + 1
share = Decimal(remaining) / Decimal(days)
```
Also drop the dead guard at lines 14-15.

**F1 reproduction:** `monkeypatch.setattr(proration, "TAX_TABLE", {"default": 0})`, then:
- `assert prorated_cents(3000, date(2026,2,28)) == 107` (it currently returns 300);
- `assert prorated_cents(3000, date(2026,3,31)) == 97` (it currently returns 0).

## NEEDS VALIDATION

- **S1. Every call may crash if the table has no `default` key.** At line 18, `TAX_TABLE["default"]` is evaluated eagerly as the argument to `.get()`. If the table lacks a `"default"` key, *every* call raises `KeyError`, even for valid regions. Settled by: whether `tax_table.json` contains `"default"`.
- **S2. Rate units.** If the table stores percentages, such as `7.25` instead of `0.0725`, the charge is about 8× the net. Settled by: the actual values in `tax_table.json`.
- **S3. Rounding.** The code rounds the net to the cent, then rounds the gross, using `ROUND_HALF_UP`. Whether this "follows the fix" is unknown. Settled by: the diff of commit `a1b2c3d4e5`, plus the jurisdictions' rule on tax rounding (per line or per invoice, half-up or half-even).
- **S4. Which date counts as day D.** A date near midnight could land in the wrong day or even the wrong month. Settled by: whether callers pass `upgrade_on` in the customer's local zone or in UTC, and which one the business intends.
- **S5. Price type.** `Decimal(float)` brings in binary artifacts. Settled by: whether every caller passes `monthly_price_cents` as an `int`.
- **S6. Stale rates.** The table is read once, at import, so a rate change takes effect only after a restart. Settled by: how `tax_table.json` updates are deployed.

## REFUTED

- **Off-by-one on day D.** Withdrawn. The `+ 1` on line 13 makes D inclusive, which matches "from D to the end of that month".
- **Imprecise tax rate from a float.** Withdrawn. `Decimal(str(x))` uses the shortest repr, so `0.0725` stays exactly `0.0725`.

## WHAT HOLDS UP

- The money arithmetic uses `Decimal` throughout, with explicit quantisation, and returns integer cents.
- Day D is counted inclusively, as the request requires.
- The function uses the new plan's price, passed in as `monthly_price_cents`, which matches the request.

## UNVERIFIED CLAIMS

- **"Tax rates come from billing/tax_table.json."** The load path is consistent with that claim. The contents and their correctness are unverified. To confirm: open the file at the PR's head.
- **"Rounding follows the fix in that commit."** Unverified. To confirm: read the diff of `a1b2c3d4e5` and compare it with lines 17 and 19.

## QUESTIONS FOR THE AUTHOR

1. Was the 30-day month deliberate, as in a 30/360 convention? If so, the request ("calendar month") must change, because the code cannot stay as it is.
2. Is falling back to the `default` tax rate for an unknown region intended, and approved by whoever owns tax compliance?
3. What did commit `a1b2c3d4e5` change about rounding? Do invoices need net and tax as separate lines, rather than one total?

## DECISION-MAKER SUMMARY

Do not merge. The proration formula assumes 30-day months, so February upgrades are overcharged (up to about 2.8× on the 28th), upgrades on the 31st are free, and most other days in 31-day months are mispriced. Fix it with the actual month length, add date-based tests, and supply the tax table and the referenced commit so the tax and rounding claims can be checked.

## OWNER SUMMARY

This change charges customers the wrong amount when they upgrade partway through a month, because it pretends every month has 30 days. Customers upgrading late in February pay far too much, and customers upgrading on the 31st pay nothing. It needs a fix and some tests before release, and the tax settings it relies on still need to be checked.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "callers of prorated_cents", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "billing/proration.py", "kind": "file"},
      {"unit": "billing/proration.py:prorated_cents", "kind": "function"},
      {"unit": "billing/proration.py:7-8 module constants", "kind": "config"},
      {"unit": "request: days D..end of calendar month, new price, regional tax", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "billing/tax_table.json", "reason": "not supplied"},
      {"unit": "commit a1b2c3d4e5", "reason": "not supplied"},
      {"unit": "callers of prorated_cents", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:8,13-16",
     "scenario": "Upgrades are prorated over a fixed 30-day month: price 3000 upgraded 2026-02-28 is charged 300 instead of 107; upgraded on Mar 31 is charged 0 instead of 97; Mar 16 is charged 1500 instead of 1548.",
     "fix": "Use calendar.monthrange(year, month)[1] as both the month length and the denominator; remove the unreachable remaining_days < 0 guard.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "With TAX_TABLE={'default': 0}: assert prorated_cents(3000, date(2026,2,28)) == 107 (observed 300); assert prorated_cents(3000, date(2026,3,31)) == 97 (observed 0)."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "billing/proration.py:11,18",
     "scenario": "A region absent from the table or mis-cased (e.g. 'ca' vs 'CA'), or a caller omitting region, silently gets the default tax rate, so the customer is under- or over-taxed with no error.",
     "fix": "Remove the region default; normalise the region and raise on an unknown region instead of falling back.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "With TAX_TABLE={'default': 0, 'CA': 0.0725}: prorated_cents(3000, date(2026,3,1), 'ca') returns 3000; expected 3218 or an error."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "PR #214 changed files (billing/proration.py only)",
     "scenario": "Billing logic ships with no tests; F1 would have been caught by any February date and future regressions will reach customers unchecked.",
     "fix": "Add parametrised tests (Feb 28 2026, Feb 29 2028, Mar 31, Mar 16, day 1, 30-day month, unknown region, taxed region) with TAX_TABLE patched; confirm they fail on the current code.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "The F1 assertions fail on the current code."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18",
     "suspicion": "TAX_TABLE['default'] is evaluated eagerly on every call, so a table without 'default' makes every call raise KeyError.",
     "unresolved_fact": "Whether billing/tax_table.json contains a 'default' key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18",
     "suspicion": "Rates stored as percentages (7.25) rather than fractions (0.0725) would multiply charges about 8x.",
     "unresolved_fact": "The value format in billing/tax_table.json."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "billing/proration.py:17,19",
     "suspicion": "Double rounding (net, then gross) with ROUND_HALF_UP may not match the referenced fix or the tax rules.",
     "unresolved_fact": "The diff of commit a1b2c3d4e5 and the per-line or per-invoice tax rounding rule."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "billing/proration.py:11",
     "suspicion": "upgrade_on may be a UTC date rather than the customer's local date, shifting day D or the month near midnight.",
     "unresolved_fact": "Which time zone callers use to derive upgrade_on."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "billing/proration.py:17",
     "suspicion": "A float monthly_price_cents passed to Decimal() brings in binary artifacts.",
     "unresolved_fact": "Whether every caller passes an int."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "billing/proration.py:7",
     "suspicion": "The tax table is read once at import, so rate changes are ignored until the process restarts.",
     "unresolved_fact": "How tax_table.json updates are deployed."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Off-by-one: day D is excluded or double-counted.",
     "evidence": "The +1 on line 13 makes D inclusive, which matches 'from D to the end of that month'."},
    {"id": "C2", "candidate": "Converting a float tax rate to Decimal loses precision.",
     "evidence": "Decimal(str(x)) uses the shortest repr, so 0.0725 becomes exactly Decimal('0.0725')."}
  ]
}
```