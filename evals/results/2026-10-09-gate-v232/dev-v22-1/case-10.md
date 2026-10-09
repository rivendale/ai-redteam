**Note:** This is a same-context review with no tools, so I could not run any code. A Critical finding gets the confirm-or-refute round below, but anything high-stakes should be re-run in a fresh session with tools.

VERDICT: **REWORK**. The code divides by a fixed 30-day month instead of the real calendar month, which is the core of the request. Customers are overcharged in short months and charged nothing for the last day of 31-day months.

CONFIDENCE: **medium**. The main finding comes from tracing the arithmetic by hand and holds whatever the inputs I did not see. Confidence is limited because this is a same-context review with no tools, and the tax table and commit `a1b2c3d4e5` were not supplied.

INPUTS LEDGER:
- **Seen:**
  - The original request.
  - The context, including the quoted PR description.
  - `billing/proration.py` (the full file).
- **Not seen:**
  - `billing/tax_table.json`. **This matters** because the tax correctness, the rate format and the presence of a `default` key all depend on it.
  - Commit `a1b2c3d4e5`. **This matters** because the PR says "Rounding follows the fix in that commit", and I cannot check that.
  - The callers of `prorated_cents`. **This matters** because I cannot see whether they pass the new plan's price or a real region.
  - Any tests. None are listed among the changed files.

COVERAGE:
- **Checked:**
  - `billing/proration.py` lines 1–19.
  - `prorated_cents` at lines 11–19: day count, share, rounding, tax lookup.
  - The import-time `TAX_TABLE` load at line 7.
  - Hostile inputs: day 31, February, a missing region, a missing `default` key.
- **Not checked:**
  - `tax_table.json` (not supplied).
  - Commit `a1b2c3d4e5` (not supplied).
  - Callers and the timezone used to derive `upgrade_on` (not supplied).

SEATS AND GATE:
- I was the only reviewer, in the same context, because no subagent or tools were available.
- No external seats were used or requested.
- Sensitivity gate passed: there is no personal or confidential data in the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (hand-traced) | B | `billing/proration.py:8,13-16` | `DAYS_IN_BILLING_MONTH = 30` is used for both the remaining days and the denominator. The request says "from D to the end of *that* month", so both should use the real month length. The `< 0` clamp at lines 14-15 can never trigger: the lowest possible value is 30−31+1 = 0. | A price of 3000¢ and an upgrade on 2026-02-15 should give 14 of 28 days, so a net of 1500¢. The code computes 16/30 and charges 1600¢, a 6.7% overcharge. On 2026-02-28 it charges 3/30 (300¢) instead of 1/28 (107¢). On 2026-01-31 it charges 0¢ instead of 97¢. Every month that is not exactly 30 days long is wrong for most upgrade days. | Fix: `days = calendar.monthrange(d.year, d.month)[1]`, then `remaining = days - d.day + 1` and `share = remaining / days`. Then drop the clamp. Test (with `TAX_TABLE` stubbed to `{"default": 0}`): `prorated_cents(3000, date(2026,2,15))` should be 1500 but the code gives 1600. `prorated_cents(3000, date(2026,1,31))` should be 97 but the code gives 0. | a✔ b✔ c✔ d✔ |
| F2 | **High** | PROBABLE (the fallback is confirmed in the code; the harm depends on the unseen table) | B/R | `billing/proration.py:11,18` | An unknown or missing region silently falls back to the `default` tax rate. The `region="default"` default argument means a caller that never passes a region also gets that rate. The request says tax for *their* region. | A key that doesn't match the table, such as `"ca"` vs `"CA"` or `"US-CA"`, or a caller that forgets `region=`, charges the default rate. If that rate differs from the customer's region, they are charged the wrong tax and nothing is raised or logged. That is customer and tax-reporting harm. | Fix: make `region` required and raise on an unknown region rather than falling back. Test: stub `TAX_TABLE = {"default": 0.0, "CA": 0.0725}`. Then `prorated_cents(3000, date(2026,3,1), "ca")` should raise or return 3218, but the code returns 3000. | a✔ b✘ c✔ d✔ |
| F3 | Medium | CONFIRMED (from the context's file list) | B | PR file list (only `proration.py` changed) | A production billing change ships with no tests. | Any test that uses a February or 31-day month would have caught F1. Without tests, future changes to rounding or tax have no guard. | Add parametrized tests covering 28/29/30/31-day months, days 1 and last, and known and unknown regions. Break the code on purpose to confirm each test fails. | a✔ b✔ c✘ d✔ |
| F4 | Low | CONFIRMED (code read) | B | `billing/proration.py:7` | The tax table is read once at import. | A tax-rate update in `tax_table.json` has no effect until the process restarts, so customers are billed at stale rates in the meantime. A missing or malformed file breaks the import of the whole billing module. | Document that a restart is required, or load with a version check. Fail loudly at startup, which it already does. Test: change the file after import and observe that the old rate is still used. | a✔ b✔ c✘ d✘ |

## NEEDS VALIDATION
- **S1 – tax rate format.** If the table stores percentages such as `8.25` rather than fractions like `0.0825`, line 19 multiplies the charge by 9.25. To settle this: check the value format in `billing/tax_table.json`.
- **S2 – missing `default` key.** `TAX_TABLE["default"]` at line 18 is evaluated before `.get()` runs. If the table has no `default` key, every call raises `KeyError`, even for known regions. To settle this: check whether `tax_table.json` contains `default`.
- **S3 – rounding order.** The code rounds net to whole cents, then rounds net plus tax again, and returns a single total with no separate tax line. To settle this: see whether commit `a1b2c3d4e5` specifies this order and whether invoices need tax shown as its own line.
- **S4 – price and date inputs.** "At the new plan's price" depends on what the callers pass in, and nothing checks that the upgrade date falls in the current billing period. To settle this: read the call sites, and check which timezone is used to derive `upgrade_on`.

## REFUTED
- **"Float tax rates cause precision errors."** `Decimal(str(...))` at line 18 converts a JSON float through its short decimal string, so a value like `0.0825` stays exact. This holds.
- **"Wrong path to the tax table."** `Path(__file__).parent / "tax_table.json"` resolves to `billing/tax_table.json`, which matches the PR description.

## Confirm-or-refute round
- **F1:** The strongest defence is "30-day billing months are an intentional business convention." The original request explicitly says "end of that calendar month", so the defence fails. **Held.**
- **F2:** The strongest defence is "the table's default rate is correct for unknown regions." Even if so, a silent fallback hides caller bugs, which conflicts with "tax for their region." **Held at High**, with evidence marked PROBABLE because the table was not seen.

## WHAT HOLDS UP
- Money is handled in `Decimal` with explicit `ROUND_HALF_UP`. There is no float arithmetic on amounts.
- The `+1` makes the upgrade day inclusive, which is correct once the month length is right.
- Tax is applied on top of the net amount, as requested.

## UNVERIFIED CLAIMS
- **"Tax rates come from billing/tax_table.json (see the update in commit a1b2c3d4e5)."** To confirm: open the file and the commit.
- **"Rounding follows the fix in that commit."** To confirm: diff the commit and compare it with lines 17 and 19.

## QUESTIONS FOR THE AUTHOR
1. Was the 30-day month a deliberate business rule? The request says "calendar month."
2. What is the format of the tax table's values, and does it have a `default` key?
3. Should an unknown region fail or fall back?

## DECISION-MAKER SUMMARY
Do not merge yet. The proration uses a fixed 30-day month, so most upgrades in February and in 31-day months are mis-billed, and an upgrade on the 31st is free. Fix the month length, make the region lookup strict, and add month-boundary tests before shipping.

## OWNER SUMMARY
This change calculates upgrade charges as if every month had 30 days. Customers who upgrade in February are overcharged, and anyone who upgrades on the 31st pays nothing. It also quietly applies a fallback tax rate when a customer's region isn't recognised, and it needs tests and a check of the tax-rate file before it goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "callers of prorated_cents", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "billing/proration.py", "kind": "file"},
      {"unit": "billing/proration.py:prorated_cents", "kind": "function"}
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
     "scenario": "Fixed 30-day month: 3000c upgrade on 2026-02-15 charges 1600c net instead of 1500c; on 2026-01-31 charges 0c instead of 97c.",
     "fix": "Use calendar.monthrange(year, month)[1] for both remaining days and denominator; drop the unreachable clamp.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "With TAX_TABLE={'default': 0}: prorated_cents(3000, date(2026,2,15)) expect 1500, observe 1600; prorated_cents(3000, date(2026,1,31)) expect 97, observe 0."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "billing/proration.py:11,18",
     "scenario": "Unknown or omitted region silently charges the default tax rate instead of the customer's region rate.",
     "fix": "Make region required; raise on unknown region instead of falling back.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "With TAX_TABLE={'default': 0.0, 'CA': 0.0725}: prorated_cents(3000, date(2026,3,1), 'ca') expect error or 3218, observe 3000."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "PR file list (billing/proration.py only)",
     "scenario": "No tests ship with a production billing change; F1 would have been caught by any February test.",
     "fix": "Add parametrized tests for 28/29/30/31-day months, first and last day, known and unknown regions; mutate the code to confirm each fails.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Search the PR for test files; none are listed in the changed files."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:7",
     "scenario": "Tax table read once at import; updated rates are not applied until the process restarts.",
     "fix": "Document the restart requirement or reload on version change.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Import the module, edit tax_table.json, call prorated_cents; the old rate is used."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18-19",
     "suspicion": "Tax rate may be stored as a percentage, inflating charges.",
     "unresolved_fact": "Value format in billing/tax_table.json."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18",
     "suspicion": "Eager TAX_TABLE['default'] raises KeyError on every call if the key is absent.",
     "unresolved_fact": "Whether tax_table.json contains a 'default' key."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "billing/proration.py:17,19",
     "suspicion": "Two-stage rounding and no separate tax amount may not match the referenced rounding fix or invoice requirements.",
     "unresolved_fact": "Contents of commit a1b2c3d4e5 and the invoice tax-line requirement."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "billing/proration.py:11",
     "suspicion": "Callers may not pass the new plan's price, and the upgrade date's timezone and billing period are unchecked.",
     "unresolved_fact": "Call sites of prorated_cents and how upgrade_on is derived."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Float tax rates introduce precision errors.",
     "evidence": "Decimal(str(rate)) at line 18 converts via the short repr, so the value stays exact."},
    {"id": "C2", "candidate": "Tax table path is wrong.",
     "evidence": "Path(__file__).parent resolves to billing/, matching billing/tax_table.json."}
  ]
}
```