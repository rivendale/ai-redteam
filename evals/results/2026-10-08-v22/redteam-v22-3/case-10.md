# Redteam review: PR #214, "Prorate mid-month upgrades"

**Reviewer note:** This was a single-reviewer pass with no tools. I did not author the work, but no subagent or second seat was available, and I could not run any code. All arithmetic below was recomputed by hand from the code. Re-run with tools and tests before merging production billing code.

**VERDICT: REWORK.** The proration uses a fixed 30-day month, while the request asks for the days to the end of the calendar month. This bills customers the wrong amount in every 28-, 29- and 31-day month, and charges nothing at all for upgrades on the 31st.

**CONFIDENCE: medium.** The core defect is certain from the code alone. Confidence is limited because I had no tools, and because the tax table, the referenced commit, the callers and any tests were not supplied.

**INPUTS LEDGER**
- **Seen:**
  - The original request (request.md).
  - The context (context.md).
  - `billing/proration.py`, the full file as supplied.
- **Not seen:**
  - `billing/tax_table.json`. **This matters:** tax correctness, the `default` key, and the rate format (fraction or percent) all depend on it.
  - Commit `a1b2c3d4e5`. **This matters:** the PR says rounding "follows the fix in that commit", and I cannot check that.
  - The callers of `prorated_cents`. **This matters:** I cannot tell whether they pass `region`, or which region keys they use.
  - Any tests. **This matters:** none are listed among the changed files.

**COVERAGE**
- **Checked:**
  - `proration.py` module level (lines 7–8).
  - `prorated_cents` (lines 11–19): the main path, plus hostile dates (day 1, day 28 in February, day 31 in a 31-day month), the region fallback, and the rounding order.
  - Requirement fit against request.md.
- **Not checked:**
  - `tax_table.json` contents.
  - Commit `a1b2c3d4e5`.
  - Callers.
  - Tests.
  - Runtime behaviour (no tools).

**SEATS AND GATE:** One local reviewer ran. Cross-vendor seats were not used: the user did not request them, and no tools were available. The sensitivity gate passed; the work contains no personal or confidential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | proration.py:8, 13–16 | `DAYS_IN_BILLING_MONTH = 30` is used both as the month length and as the denominator. The request says "from D to the end of that month", which means the calendar month. The `< 0` guard on lines 14–15 is dead code: the day is never above 31, so `remaining_days` is never below 0. | **Feb 28, 2026, price 3000¢:** remaining = 3, share = 0.1, net = 300¢. The correct charge is 1/28 × 3000 = 107¢, so the customer is overcharged by about 2.8×. **Feb 15:** the code charges 16/30 (1600¢); the correct charge is 14/28 (1500¢). **Jan 31, price 3100¢:** remaining = 0, so net = 0 and the upgrade is free. The correct charge is 100¢. **Jan 2:** the code charges 29/30; the correct charge is 30/31. | **Fix:** `days_in_month = calendar.monthrange(upgrade_on.year, upgrade_on.month)[1]`, then `remaining = days_in_month - upgrade_on.day + 1` and `share = remaining / days_in_month`. Delete the dead guard. **Reproduction:** patch `TAX_TABLE = {"default": 0}` and assert that `prorated_cents(3000, date(2026,2,28)) == 107` (currently returns 300) and `prorated_cents(3100, date(2026,1,31)) == 100` (currently returns 0). Add a leap-year case: `date(2028,2,29)` with price 2900 should return 100. | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED | B | proration.py:11, 18 | `region="default"` and `TAX_TABLE.get(region, TAX_TABLE["default"])` silently apply the default rate in two cases: a caller omits `region`, or the region key is missing from the table (a new region, or a case mismatch such as `"CA"` vs `"ca"`). The request says "tax for *their* region". | A customer in a region absent from the table is taxed at the default rate, with no error and no log. This under- or over-collects tax. | **Fix:** make `region` required. Raise an error (or alert and fail closed) on an unknown region, and do not fall back. **Reproduction:** with `TAX_TABLE = {"default": 0.0, "CA": 0.0725}`, `prorated_cents(1000, date(2026,1,1), "ca")` returns 1000; it should raise or return 1073. **Severity:** stays Medium only because likelihood (d) cannot be judged without the table and the callers. It becomes Critical if any live region key is missing from the table. | a✓ b✓ c✓ d✗ |
| F3 | Medium | CONFIRMED | B | PR file list (context.md) | The production billing change ships with no tests. Only `billing/proration.py` was changed. F1 would have been caught by any test that used a February or 31-day date. | Future edits to the month or tax logic regress silently. | **Fix:** add tests that cover days 1, 15, 28 and 31, February in common and leap years, an unknown region, and rounding at the .5 boundary. Then confirm that each test fails against the current code. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1, rounding order (lines 17, 19).** The code rounds net to the cent first, then applies tax and rounds again. The PR says rounding "follows the fix in commit a1b2c3d4e5". **What would settle it:** what that commit specifies. For example, does it require round-once-on-the-gross-amount, banker's rounding, or a per-line tax rule?
- **S2, the `default` key (line 18).** `TAX_TABLE["default"]` is evaluated on every call, even when the region exists. If the table has no `"default"` key, every call raises `KeyError`. **What would settle it:** whether `tax_table.json` contains `"default"`.
- **S3, rate format (line 18).** The code treats the rate as a fraction (0.0825). If the table stores percentages (8.25), customers are charged 9.25× the net. **What would settle it:** the value format in `tax_table.json`.
- **S4, tax table loaded at import (line 7).** Rate updates need a process restart, and a missing file fails the import. **What would settle it:** how tax table updates are deployed. Is a restart guaranteed?

## REFUTED
- **"Should credit the unused days of the old plan."** Withdrawn: the request asks only for the new plan's price for days D to month end. The work matches the request on this point.
- **"Off-by-one in counting days D through the end of the month."** Withdrawn: the `+1` correctly makes the range inclusive of day D. The defect is the month length (F1), not the inclusive count.

## WHAT HOLDS UP
- Decimal arithmetic avoids float error.
- `Decimal(str(rate))` avoids binary float expansion.
- Inclusive day counting is correct.
- Using the new plan's price matches the request.
- The tax table path resolves next to `billing/proration.py`, which is consistent with the PR description.

## UNVERIFIED CLAIMS
- **"Tax rates come from billing/tax_table.json (see the update in commit a1b2c3d4e5)."** To confirm, open the commit and the file.
- **"Rounding follows the fix in that commit."** To confirm, diff the commit and compare it with lines 17 and 19.

## QUESTIONS FOR THE AUTHOR
1. Did the request intend a fixed 30-day billing month? If so, the request text needs to change, and F1 becomes drift in the specification rather than a bug.
2. What rounding rule does commit `a1b2c3d4e5` define?
3. Does every region that callers pass exist in `tax_table.json`, in the same case and stored as a fraction?

## DECISION-MAKER SUMMARY
Do not merge yet. The charge is computed against a fixed 30-day month, which overcharges February upgrades by up to about 3× and makes upgrades on the 31st free. Unknown regions also silently get the default tax rate. Fix F1, make an unknown region an error, add tests that fail on the current code, and supply the tax table and commit `a1b2c3d4e5` for a second pass.

## OWNER SUMMARY
The change works out mid-month upgrade charges as if every month had 30 days. Customers in short months pay too much, and customers who upgrade on the 31st pay nothing. Tax can also silently fall back to a generic rate when a customer's region isn't recognised, and the change has no tests, so it should be fixed and tested before it goes live.

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
      {"unit": "request.md: days D to end of calendar month at new price plus regional tax", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "billing/tax_table.json", "reason": "not supplied"},
      {"unit": "commit a1b2c3d4e5", "reason": "not supplied"},
      {"unit": "callers and tests", "reason": "not supplied"},
      {"unit": "runtime execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:8,13-16",
     "scenario": "Fixed 30-day month: upgrade on 2026-02-28 at 3000 cents charges 300 instead of 107; upgrade on 2026-01-31 at 3100 cents charges 0 instead of 100.",
     "fix": "Use calendar.monthrange(year, month)[1] for both remaining-days and denominator; remove dead <0 guard.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "With TAX_TABLE={'default': 0}: assert prorated_cents(3000, date(2026,2,28)) == 107 (observed 300); assert prorated_cents(3100, date(2026,1,31)) == 100 (observed 0)."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:11,18",
     "scenario": "A caller omitting region, or a region key absent or mis-cased in the table, is silently taxed at the default rate instead of the customer's regional rate.",
     "fix": "Make region required and raise on unknown region instead of falling back to default.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "With TAX_TABLE={'default': 0.0, 'CA': 0.0725}: prorated_cents(1000, date(2026,1,1), 'ca') returns 1000; expected an error or 1073."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "PR #214 changed files (only billing/proration.py)",
     "scenario": "Production billing logic ships untested; F1 would have been caught by any February or 31st-of-month test, and future regressions will pass unnoticed.",
     "fix": "Add tests for days 1/15/28/31, February common and leap years, unknown region, and .5 rounding boundaries; confirm each fails on the current code.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add the F1 assertions as a test file; it goes red on the current code."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "billing/proration.py:17,19",
     "suspicion": "Net is rounded before tax and then rounded again; may not match the intended rounding rule.",
     "unresolved_fact": "The rounding rule defined in commit a1b2c3d4e5 (not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18",
     "suspicion": "TAX_TABLE['default'] is evaluated eagerly on every call; a missing key raises KeyError for all regions.",
     "unresolved_fact": "Whether billing/tax_table.json contains a 'default' key."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18",
     "suspicion": "Rates are treated as fractions; percentages in the table would multiply charges by about 9x.",
     "unresolved_fact": "Value format in billing/tax_table.json."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "billing/proration.py:7",
     "suspicion": "Tax table is loaded once at import; updates need a restart and a missing file breaks import.",
     "unresolved_fact": "How tax table updates are deployed and whether a restart is guaranteed."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Upgrade should credit unused days of the old plan.",
     "evidence": "request.md asks only for the new plan's price for days D to month end; no credit is requested."},
    {"id": "C2", "candidate": "Off-by-one in inclusive day count.",
     "evidence": "The +1 correctly includes day D; the defect is the month length (F1), not the inclusive count."}
  ]
}
```