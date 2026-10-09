VERDICT: **REWORK**. The function prorates against a fixed 30-day month instead of the calendar month the request specifies. Upgrades on the 31st are charged nothing, and every month that is not 30 days long is mispriced, including February overcharges.

CONFIDENCE: **medium**. The defects were traced by hand and the arithmetic is deterministic, but nothing was run because this session has no tools. I am a single reviewer with no fresh-subagent or cross-vendor seat. The tax table and the commit cited for rounding were not supplied.

INPUTS LEDGER:
- Seen: the original request (request.md), the context (context.md, including the quoted PR description), and `billing/proration.py`.
- Not seen:
  - `billing/tax_table.json`. **Matters**, because the format and keys of the tax rates decide S1, S2 and F3.
  - Commit `a1b2c3d4e5`. **Matters**, because the PR says rounding "follows the fix in that commit" and I cannot check that claim.
  - Callers of `prorated_cents`. **Matters**, because they decide whether `region` is always passed (F3).
  - Any tests. **Matters**: the context lists only `proration.py` as changed, so the PR appears to add none (F4).

COVERAGE:
- Scope: the PR diff, which is the single file `billing/proration.py`, reviewed in full.
- Checked: module-level loading of `TAX_TABLE` (line 7), the `DAYS_IN_BILLING_MONTH` constant (line 8), and `prorated_cents` lines 13–19, covering remaining-days, the clamp, the share, net rounding, the tax lookup and the final rounding.
- Hand-traced inputs: 2026-01-01, 01-15, 01-30, 01-31, 02-15 and 02-28.
- Not checked: the tax table, the commit and the callers (`not_supplied`). Running anything (`no_tools`).

SEATS AND GATE:
- One reviewer only (this instance). No subagent or cross-vendor seats were available.
- The sensitivity gate passed. The code holds no personal or confidential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (hand trace) | B | proration.py:13 (with dead clamp at 14–15) | The remaining-day count is `30 - day + 1`, not `days_in_month - day + 1`. | **Upgrade on the 31st** (seven months a year): `remaining_days = 0`, so the charge is 0 for a day the customer uses. **Upgrade on 2026-02-28**: `remaining_days = 3` for a month that has 1 day left, so a 2800¢ plan is charged 280¢ pre-tax instead of 100¢. The `< 0` clamp can never fire because day ≤ 31, so it guards nothing. | Fix: `days_in_month = calendar.monthrange(d.year, d.month)[1]` and `remaining = days_in_month - d.day + 1`. Repro 1: `prorated_cents(3100, date(2026,1,31))` should return `100*(1+t)` rounded; it returns `0`, whatever the tax rate. Repro 2: `prorated_cents(2800, date(2026,2,28))` should return `round(100*(1+t))`; it returns `round(280*(1+t))`. | y/y/y/y |
| F2 | Critical | CONFIRMED (hand trace) | B | proration.py:8, 16 | The share denominator is a fixed 30, not the calendar month's length. | Every 28-, 29- and 31-day month is mispriced. **2026-02-15** at 3000¢: the code charges 16/30, which is 1600¢; the correct charge is 14/28, which is 1500¢, so the customer is overcharged. **2026-01-15** at 3100¢: the code charges 1653¢; the correct charge is 17/31, which is 1700¢, so the customer is undercharged. **2026-01-30** at 3100¢: 103¢ against a correct 200¢. | Fix: use the same `days_in_month` as the denominator. Repro: `prorated_cents(3000, date(2026,2,15), r)` for a region with rate 0 should return 1500; it returns 1600. | y/y/y/y |
| F3 | Medium | PROBABLE | B | proration.py:11 (`region="default"`), 18 | A missing or unknown region silently falls back to the default tax rate instead of failing. | A caller omits `region`, or passes a region absent from the table (new, misspelled, or the wrong case). The customer is charged the default rate rather than "tax for their region", and no error or log is produced. Whether this happens in production depends on the table and the callers, neither of which was supplied. | Fix: make `region` required and raise on an unknown region, or log and alert. Repro: `prorated_cents(3000, date(2026,1,1), "NOT_A_REGION")` should raise; it returns the default-taxed amount. | y/n/y/n |
| F4 | Medium | CONFIRMED (PR file list in context) | B | PR #214 file list | The PR changes only `proration.py` and adds no test for a billing calculation. | Any test covering month ends or February would have caught F1 and F2. Without tests, a regression in production billing would go unnoticed. | Fix: add table-driven tests for day 1, the 15th, day 30 and day 31 across 28-, 29-, 30- and 31-day months, plus an unknown region. Repro: list the files changed in PR #214; no test file appears. | y/y/n/y |

**Siblings for F1 and F2:**
- I searched every use of `DAYS_IN_BILLING_MONTH` in the supplied file and found lines 13 and 16. Each is recorded above as its own finding.
- Other modules that might import the constant were not supplied.
- Neither finding is a security finding.

## NEEDS VALIDATION
- **S1, line 18.** `TAX_TABLE.get(region, TAX_TABLE["default"])` evaluates `TAX_TABLE["default"]` eagerly on every call. If `tax_table.json` has no `"default"` key, every call raises `KeyError`, even for regions that are listed. *Settles it:* whether the table contains a `"default"` key.
- **S2, line 18.** The code treats the rate as a fraction (for example 0.2). If the table stores percentages (for example 20), every charge is multiplied by 21. *Settles it:* the format of the values in `tax_table.json`.
- **S3, lines 17 and 19.** The amount is rounded twice: the net is rounded to cents, then tax is applied and the result rounded again. The PR says rounding "follows the fix in commit a1b2c3d4e5". *Settles it:* the contents of that commit, and whether tax is required to be computed on the rounded net or on the unrounded amount.
- **S4, line 7.** The table is read once at import time. Updated rates take effect only after a restart, and a missing file breaks the import of the whole billing module. *Settles it:* how the table is deployed and updated.

## REFUTED
- **"Off-by-one: the upgrade day should be excluded."** The request says "from D to the end of that month", which includes day D, so the `+1` is correct. Day 1 gives a full month as expected (30/30 in the code; the correct calendar ratio, such as 31/31, also gives a full month).
- **"Float imprecision in the tax rate."** `Decimal(str(rate))` avoids binary float error, and all the arithmetic uses Decimal.

## WHAT HOLDS UP
- Decimal arithmetic is used throughout, with explicit ROUND_HALF_UP.
- Day D is counted inclusively.
- Tax is applied to the prorated amount, not the full monthly price.
- Path resolution puts the table in `billing/`, which matches the PR description.

## UNVERIFIED CLAIMS
- "Tax rates come from billing/tax_table.json (see the update in commit a1b2c3d4e5)." To confirm, open the file and the commit.
- "Rounding follows the fix in that commit." To confirm, diff the commit and compare it with lines 17 and 19.

## QUESTIONS FOR THE AUTHOR
1. Why a fixed 30-day month, when the request specifies the calendar month?
2. What does `tax_table.json` contain? Specifically, does it have a `"default"` key, and are rates stored as fractions or percentages?
3. Is double rounding (net first, then gross) the intended rule from commit a1b2c3d4e5?

## DECISION-MAKER SUMMARY
Do not merge. Proration uses a 30-day month, so upgrades on the 31st are billed nothing, February upgrades are overcharged, and every 31-day month is mispriced. Fix it with `calendar.monthrange` and add month-end tests. If it ships as is, customers are billed incorrectly on every non-30-day month, and February overcharges create refund and complaint exposure.

## OWNER SUMMARY
The new upgrade-billing code assumes every month has 30 days. As a result, some customers would be charged nothing, others too much and others too little, depending on the date and month they upgrade. It needs to be corrected and tested before release, and the tax rate file it relies on should be checked as well.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "callers of prorated_cents", "status": "not_seen", "matters": true},
    {"item": "tests for proration", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-instance", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "billing/proration.py", "kind": "file"},
      {"unit": "proration.py:prorated_cents", "kind": "function"},
      {"unit": "proration.py:DAYS_IN_BILLING_MONTH", "kind": "config"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md (incl. PR description)", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "billing/tax_table.json", "reason": "not_supplied"},
      {"unit": "commit a1b2c3d4e5", "reason": "not_supplied"},
      {"unit": "callers of prorated_cents", "reason": "not_supplied"},
      {"unit": "execution of any code", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:13-15",
     "scenario": "Upgrade on the 31st yields remaining_days=0 and a charge of 0; upgrade on 2026-02-28 counts 3 remaining days instead of 1 (2800c plan charged 280c pre-tax instead of 100c). The <0 clamp is unreachable.",
     "fix": "Compute days_in_month = calendar.monthrange(d.year, d.month)[1]; remaining = days_in_month - d.day + 1.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "prorated_cents(3100, date(2026,1,31)): expected round(100*(1+t)), observed 0 for any tax rate t.",
     "security": false,
     "siblings_searched": {"searched": "all uses of DAYS_IN_BILLING_MONTH in billing/proration.py", "found": "line 16 denominator, recorded as F2"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:8,16",
     "scenario": "Share uses /30 for every month: 2026-02-15 at 3000c charges 1600c instead of 1500c (overcharge); 2026-01-15 at 3100c charges 1653c instead of 1700c.",
     "fix": "Use the calendar month length as the denominator.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "prorated_cents(3000, date(2026,2,15), region_with_rate_0): expected 1500, observed 1600.",
     "security": false,
     "siblings_searched": {"searched": "all uses of DAYS_IN_BILLING_MONTH in billing/proration.py", "found": "line 13 numerator, recorded as F1"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "billing/proration.py:11,18",
     "scenario": "A caller omits region or passes one absent from the table; the default tax rate is applied silently instead of the customer's regional rate.",
     "fix": "Make region required; raise or alert on unknown regions.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "prorated_cents(3000, date(2026,1,1), 'NOT_A_REGION'): expected an error, observed the default-taxed amount."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "PR #214 file list (only billing/proration.py changed)",
     "scenario": "No tests accompany a production billing calculation; month-end and February errors (F1, F2) ship undetected.",
     "fix": "Add table-driven tests over days 1/15/30/31 in 28-, 29-, 30- and 31-day months and an unknown-region case.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "List files changed in PR #214: no test file present."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18",
     "suspicion": "TAX_TABLE['default'] is evaluated eagerly; a table without a 'default' key makes every call raise KeyError.",
     "unresolved_fact": "Whether tax_table.json has a 'default' key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18",
     "suspicion": "Rates stored as percentages would be applied as multipliers (21x charge).",
     "unresolved_fact": "The value format in tax_table.json."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "billing/proration.py:17,19",
     "suspicion": "Double rounding (net, then gross) may not match the required rounding rule.",
     "unresolved_fact": "The rounding rule introduced in commit a1b2c3d4e5."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "billing/proration.py:7",
     "suspicion": "Tax table read once at import; updates need a restart and a missing file breaks module import.",
     "unresolved_fact": "How tax_table.json is deployed and updated."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Off-by-one: the upgrade day should be excluded.",
     "evidence": "The request says 'from D to the end of that month', which includes D; the +1 is correct."},
    {"id": "R2", "candidate": "Float imprecision in the tax rate.",
     "evidence": "Decimal(str(rate)) and Decimal arithmetic throughout."}
  ]
}
```