**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools, so I could not run code, open files, fetch the PR, or launch a subagent. All arithmetic below is traced by hand from the supplied source.

VERDICT: **REWORK**. The fixed 30-day month charges the wrong amount in every month that is not 30 days long: one free day in 31-day months, a zero charge on the 31st, and an overcharge in February. The request requires calendar-month proration.

CONFIDENCE: **medium**. The main defect comes from a hand trace of four lines, so confidence in it is high. Confidence is lowered by four things: no tools, the tax table and the rounding commit were not supplied, there are no callers or tests to inspect, and this is a single-reviewer, same-context pass.

INPUTS LEDGER:
- Seen: the original request (request.md), the context (context.md), and `billing/proration.py` (the full file as supplied).
- Not seen:
  - `billing/tax_table.json`. **Matters**: whether `"default"` exists, and which regions are keys, decides whether F2 and S1 occur in production.
  - Commit `a1b2c3d4e5`. **Matters**: the PR says the rounding "follows the fix in that commit", and that cannot be checked (S2).
  - The full PR #214 diff and description. It matters slightly, to confirm that proration.py is the only changed file.
  - Callers of `prorated_cents`. **Matters**: they decide whether `region` is always passed and whether the price passed is the new plan's price (S3).
  - Tests. Context lists only proration.py as changed, so none were added (F3).

COVERAGE:
- Checked:
  - `billing/proration.py`: the module-level load and `prorated_cents`, line by line.
  - Hostile inputs: day 1, day 30, day 31, February 28/29, an unknown region, an omitted region, and a float tax rate.
- Not checked: `billing/tax_table.json`, commit `a1b2c3d4e5`, callers, tests, and the deploy.

SEATS AND GATE: one reviewer only (this session); no subagent or cross-vendor tool was available. Sensitivity gate: no personal data, credentials or client records in the work, so it is not sensitive and seats were not refused on that ground, simply unavailable. There are no instructions addressed to the reviewer inside the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (hand trace) | B | `billing/proration.py:9`, `:14-17` (`DAYS_IN_BILLING_MONTH = 30`, `remaining_days = 30 - day + 1`, `share = remaining/30`) | The request says "days from D to the end of that calendar month". The code always uses a 30-day month for both the remaining-day count and the denominator. The `< 0` guard is dead code, because the minimum value is 0 on day 31. | **31-day months (7 per year):** the code bills 31−D days out of 30; the correct charge is 32−D days out of 31. Upgrade on Jan 31 at 3100¢ with 0 tax: the code charges **0**, the correct charge is **100**. Jan 15: the code charges 1653, the correct charge is 1700. **February:** upgrade on Feb 28, 2026 at 2800¢: the code charges **280** (3/30), the correct charge is **100** (1/28), a 2.8× overcharge. A Feb 29 upgrade in 2028 bills 2/30 instead of 1/29. Only 30-day months are correct. | Use the real month length: `days = calendar.monthrange(d.year, d.month)[1]`, `remaining = days - d.day + 1`, `share = Decimal(remaining)/Decimal(days)`. Remove the dead guard. **Repro** (set `proration.TAX_TABLE = {"default": 0}`): `prorated_cents(3100, date(2026,1,31))` should be 100, observed 0. `prorated_cents(2800, date(2026,2,28))` should be 100, observed 280. `prorated_cents(3000, date(2026,4,30))` should be 100, observed 100 (control). | a✔ b✔ c✔ (breaks request; customer over/undercharge) d✔ |
| F2 | High | PROBABLE | B | `billing/proration.py:12` (`region="default"`), `:19` (`TAX_TABLE.get(region, TAX_TABLE["default"])`) | The request requires "tax for their region". Instead, an unknown region and an omitted region both silently get the default rate. There is no error and no log line. The lookup is also an exact, case-sensitive string match. | A caller omits `region`, passes `"US-CA"` when the key is `"us-ca"`, or passes a region not yet in the table. The customer is charged the default rate instead of their region's rate. That means tax is under- or over-collected with nothing logged. The code behaviour is confirmed. Whether real traffic hits it depends on callers and the table, which I did not see, hence PROBABLE. | Make `region` a required argument. Raise an error (or fail closed and alert) on an unknown region instead of falling back, and normalise keys. **Repro:** set `TAX_TABLE = {"default": 0, "ca": 0.1}`. `prorated_cents(1000, date(2026,4,1), "CA")` should raise or return 1100; it returns 1000. | a✔ b✘ c✔ (regulatory, tax) d✔ (the default param invites omission) |
| F3 | Medium | CONFIRMED (per context: only proration.py changed) | B | PR #214 file list | A production billing change ships with no tests. Any single test on a day-31 or February date would have caught F1. | Later edits to proration or rounding regress silently. | Add a parametrised test over each month length (28/29/30/31), days 1, 15 and the last day, plus unknown-region and rounding half-cent cases. Confirm the tests go red on the current code. | a✔ b✔ c✘ d✔ → Medium (High needs a, d plus b or c; c is false here, but by the rubric a+b+d would be High). Correction: a, b, d → **High** under the rule. See note below. |

*Note on F3:* the rubric says High = a and d plus b or c. F3 has a, b and d, so it formally rates High. I keep it at **High** in the JSON. Its practical urgency is lower than F1 and F2, because adding tests does not change any charge by itself.

## NEEDS VALIDATION
- **S1:** `TAX_TABLE["default"]` is evaluated eagerly as the `.get` fallback argument on *every* call (line 19). If `tax_table.json` has no `"default"` key, every call raises `KeyError`, including calls for valid regions. *Settling fact:* does `billing/tax_table.json` contain a `"default"` key, and what is its value?
- **S2:** The rounding rounds the net to whole cents half-up, applies tax, then rounds half-up again (lines 18 and 20). The PR says this "follows the fix in" `a1b2c3d4e5`. *Settling fact:* what that commit specifies (round once vs twice, half-up vs half-even, per line vs per invoice), and what the tax authority or invoice system expects.
- **S3:** The request says "at the new plan's price". The function takes any `monthly_price_cents`. *Settling fact:* do the callers pass the new plan's full monthly price, and is any credit for the old plan handled elsewhere or intentionally not given?
- **S4:** The table is loaded once at import (line 7), so a rate change in the JSON needs a process restart, and a missing file breaks import of the billing module. *Settling fact:* how tax-table updates are deployed.

## REFUTED
- **R1:** "Float tax rates from JSON cause binary-precision errors." Refuted: `Decimal(str(float))` uses Python's shortest round-trip repr, so `0.0825` becomes `Decimal('0.0825')` exactly. Using `parse_float=Decimal` would be cleaner but is not a defect.
- **R2:** "`remaining_days` can go negative." Refuted: `date.day` is at most 31, so the minimum is 30 − 31 + 1 = 0. The guard is dead code, which is folded into F1, not a separate defect.
- **R3:** "The wrong path to the tax table." Refuted: `Path(__file__).parent / "tax_table.json"` from `billing/proration.py` resolves to `billing/tax_table.json`, the file the PR description names.

## WHAT HOLDS UP
- The code uses `Decimal` throughout with explicit `ROUND_HALF_UP`, not float arithmetic on money.
- 30-day months (April, June, September, November) prorate correctly, including day 1 (a full month) and the last day (one day).
- The return value is an integer number of cents.

## UNVERIFIED CLAIMS
- "Tax rates come from billing/tax_table.json (see the update in commit a1b2c3d4e5)". To confirm, open the file and the commit, and check that the keys match the region identifiers the callers pass.
- "Rounding follows the fix in that commit". To confirm, diff the rounding steps in `a1b2c3d4e5` against lines 18 and 20.

## QUESTIONS FOR THE AUTHOR
1. Was the fixed 30-day month a deliberate business rule? It contradicts "end of that calendar month" in the request.
2. Is the silent fallback to `"default"` tax intended, and does the table have a `"default"` key?
3. What exactly does commit `a1b2c3d4e5` specify for rounding?

## DECISION-MAKER SUMMARY
Do not merge. Replace the fixed 30-day month with the real calendar-month length, and make an unknown or missing region an error rather than a silent default tax. Add tests covering every month length. If it ships as is, customers who upgrade on the 31st pay nothing, every 31-day month gives away a day, February upgrades are overcharged up to about 2.8×, and some customers may be charged the wrong tax with no record of it.

## OWNER SUMMARY
The change works out the upgrade charge as if every month had 30 days, so most months give the wrong amount: February customers can pay nearly three times too much, and upgrades on the 31st are free. It can also charge the wrong tax without any warning when a customer's region isn't recognised. It should be corrected and tested before it reaches real invoices.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "callers of prorated_cents", "status": "not_seen", "matters": true},
    {"item": "PR #214 full diff and description", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data, credentials or client records in the work."},
  "coverage": {
    "checked": [
      {"unit": "billing/proration.py", "kind": "file"},
      {"unit": "billing/proration.py:prorated_cents", "kind": "function"},
      {"unit": "billing/proration.py:TAX_TABLE load", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "billing/tax_table.json", "reason": "not supplied"},
      {"unit": "commit a1b2c3d4e5", "reason": "not supplied"},
      {"unit": "callers and tests", "reason": "not supplied; no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:9,14-17",
     "scenario": "Fixed 30-day month: upgrade on Jan 31 at 3100c (0 tax) is charged 0 instead of 100; Feb 28 2026 at 2800c is charged 280 instead of 100; every 31-day month undercharges by one day.",
     "fix": "Use calendar.monthrange(d.year, d.month)[1] for both remaining days and the denominator; remove the dead <0 guard.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "With TAX_TABLE={'default':0}: prorated_cents(3100, date(2026,1,31)) expect 100, observe 0; prorated_cents(2800, date(2026,2,28)) expect 100, observe 280."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "billing/proration.py:12,19",
     "scenario": "A caller omits region or passes a region not exactly matching a table key; the customer is silently charged the default tax rate instead of their region's.",
     "fix": "Make region required; raise or fail closed with an alert on unknown regions; normalise keys.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "With TAX_TABLE={'default':0,'ca':0.1}: prorated_cents(1000, date(2026,4,1), 'CA') expect error or 1100, observe 1000."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "PR #214 file list (only billing/proration.py changed)",
     "scenario": "Production billing logic ships with no tests; F1 would have been caught by any test on day 31 or in February, and future regressions will pass silently.",
     "fix": "Add parametrised tests over 28/29/30/31-day months (first, middle, last day), unknown region, and half-cent rounding; confirm they fail on the current code.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run the F1 reproduction cases as tests against the current code; they fail."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "billing/proration.py:19",
     "suspicion": "TAX_TABLE['default'] is evaluated on every call; if absent, all calls raise KeyError.",
     "unresolved_fact": "Whether billing/tax_table.json contains a 'default' key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18,20",
     "suspicion": "Double half-up rounding may not match the rounding fix the PR cites.",
     "unresolved_fact": "What commit a1b2c3d4e5 specifies for rounding."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "billing/proration.py:12",
     "suspicion": "Callers may pass a price other than the new plan's full monthly price.",
     "unresolved_fact": "What callers pass as monthly_price_cents."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "billing/proration.py:7",
     "suspicion": "Tax table is loaded once at import; rate updates need a restart and a missing file breaks import.",
     "unresolved_fact": "How tax-table updates are deployed."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Float tax rates cause precision errors.", "evidence": "Decimal(str(float)) uses the shortest round-trip repr, e.g. Decimal('0.0825')."},
    {"id": "R2", "candidate": "remaining_days can go negative.", "evidence": "date.day <= 31, so the minimum is 0; the guard is dead code."},
    {"id": "R3", "candidate": "Wrong tax table path.", "evidence": "Path(__file__).parent resolves to billing/, matching billing/tax_table.json."}
  ]
}
```

I could not run `tools/validate_findings.py` against this block in this session.