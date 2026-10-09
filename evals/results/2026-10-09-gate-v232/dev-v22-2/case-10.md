Same-context review: no subagent or tools in this session, so I reviewed the code by hand and ran nothing. The work was not written in this conversation, which lowers the anchoring risk, but for production billing it is worth re-running in a fresh session with tools.

**VERDICT: REWORK.** The code charges for a fixed 30-day month instead of the actual calendar month. Upgrades on the 31st are billed nothing and late-February upgrades are overcharged up to about 3x, which fails the original request directly.

**CONFIDENCE: medium.** The main defect is certain from the code itself. Confidence is limited because I had no tools, and because the tax table, the referenced commit, the callers and any tests were not supplied.

**INPUTS LEDGER**
- **Seen:** the original request, the context (including the PR description), and `billing/proration.py` as a full file, not as a diff.
- **Not seen:**
  - `billing/tax_table.json`. This **matters**: the rate format (fraction or percent), which regions it covers and whether it has a `"default"` key all decide whether tax is correct.
  - Commit `a1b2c3d4e5`. This **matters**: the PR says it defines the rounding policy, so I cannot check that the rounding here "follows the fix".
  - The PR diff against base. This **matters** a little: I cannot tell which lines are new.
  - Callers of `prorated_cents`. This **matters**: I cannot confirm they pass the *new* plan's price and the customer's actual region.
  - Tests. The context lists only `proration.py` as changed, so the PR appears to include none.

**COVERAGE**
- **Checked:**
  - `proration.py` module load (`TAX_TABLE`)
  - `prorated_cents`: the remaining-days computation, the clamp, the share, net rounding, tax lookup and gross rounding
  - Hand-traced dates: Jan 1, Jan 2, Jan 30, Jan 31, Feb 15, Feb 28 (non-leap) and Feb 29 (leap)
- **Not checked:** the tax table, the rounding commit, callers, the timezone of `upgrade_on`, and tests.

**SEATS AND GATE:** Only the local reviewer ran. The work contains no personal or confidential data, but no subagent or cross-vendor seats were available in this session.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (hand trace) | B | `proration.py:9`, `:14-17` | `DAYS_IN_BILLING_MONTH = 30` is used for every month, but the request is "days from D to the end of **that** month". The `< 0` clamp can never fire, and day 31 silently gives 0. | Assume a 3000¢ plan and 0% tax. **Jan 31:** remaining = 30−31+1 = 0, so the charge is **0¢** instead of about 97¢ (1/31), and the customer gets a free day. **Feb 15 (non-leap):** 16/30 gives **1600¢** instead of 14/28 = 1500¢. **Feb 28:** 3/30 gives **300¢** instead of about 107¢ (1/28), nearly a 3x overcharge. **Jan 2:** 29/30 gives 2900¢ instead of about 2903¢. Every month that is not 30 days long is mispriced. | Use `days_in_month = calendar.monthrange(d.year, d.month)[1]` and `remaining = days_in_month - d.day + 1`, and remove the dead clamp. **Repro:** `prorated_cents(3000, date(2026,1,31))` with tax rate 0: expect 97, observe 0. Add parametrized tests for the 1st, the 31st, Feb 28 and 29 in leap and non-leap years, and a 30-day month. | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED (code) | B/R | `proration.py:12` (`region="default"`), `:19` (`.get(region, TAX_TABLE["default"])`) | An unknown, misspelled or differently cased region, or a caller that omits `region`, silently gets the default rate instead of the rate "for their region". | A customer in a region missing from the table, or one that does not match by case (`"CA"` vs `"ca"`), is taxed at the default rate. Nothing logs or fails. Real harm depends on the table's contents, which I could not see (see S1). | Make `region` required. Raise or alert on an unknown region rather than falling back, or limit the fallback to an explicit allow-list. **Test:** `prorated_cents(1000, d, region="nonexistent")` should raise. Today it returns the default-taxed amount. | a✓ b✓ c✗ d✗ |
| F3 | Medium | CONFIRMED (context) | B | The PR as a whole: only `billing/proration.py` changed | A production billing change ships with no tests. Any test on a 31-day month or on February would have caught F1. | The next edit to the day math regresses with no signal. | Add the F1 table-driven tests. Before trusting them, mutate the code (for example, put the constant 30 back) and confirm the tests go red. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED (code) | B | `proration.py:7` | The tax table is read once at import, so a long-running worker keeps stale rates after the table changes. | The table is updated for a rate change and workers that are not restarted keep billing the old rate. | Document that a restart is required on deploy, or load the table through a versioned config with a reload hook. | a✓ b✓ c✗ d✗ |

### NEEDS VALIDATION
- **S1, tax table contents.** I need to know whether `tax_table.json` stores rates as fractions (`0.0825`) or percents (`8.25`). Percents would multiply the bill by about 9x. I also need to know whether it has a `"default"` key (without one, every call raises `KeyError`) and whether it covers every region customers are billed in.
- **S2, rounding policy.** Net is rounded to the cent, then tax is applied and the gross is rounded again. I need to know whether commit `a1b2c3d4e5` specifies this two-step HALF_UP rounding, or tax calculated on the unrounded net, or tax rounded separately as its own line.
- **S3, callers.** I need to know whether every caller passes the **new** plan's monthly price (as the request requires) in integer cents, and a real region.
- **S4, "day D" timezone.** I need to know whether `upgrade_on` is the date in the customer's or the billing region's timezone, or a UTC date. A UTC date can shift the upgrade day near midnight, and at month boundaries it can shift the month.

### REFUTED
- **Negative charge from the clamp.** `upgrade_on.day` is at most 31, so `remaining_days` is never below 0. The clamp is dead code, not a source of negative charges. The real problem it hides is folded into F1.
- **Float precision in the tax rate.** `Decimal(str(...))` avoids binary-float artifacts for JSON numbers. The arithmetic is done entirely in Decimal.

### WHAT HOLDS UP
- Decimal arithmetic throughout, with explicit `ROUND_HALF_UP`.
- `Decimal(str(rate))` instead of `Decimal(float)`.
- Upgrading on the 1st gives a full-month charge (share 1.0), which is correct in every month.
- The function stays small and pure apart from the table load.

### UNVERIFIED CLAIMS
- **"Tax rates come from billing/tax_table.json (see the update in commit a1b2c3d4e5)."** To confirm, open the commit and the table and check the format, the `default` key and region coverage.
- **"Rounding follows the fix in that commit."** To confirm, read the commit and compare its rounding order to lines 18 and 20.

### QUESTIONS FOR THE AUTHOR
1. What is the rate format in `tax_table.json`, and does it include `"default"` and every billed region?
2. What rounding does commit `a1b2c3d4e5` prescribe: rounding the net first, or computing tax on the unrounded net?
3. Should an unknown region fail, or fall back to a default? If it falls back, who approved that for tax purposes?

### DECISION-MAKER SUMMARY
Do not merge. F1 misbills every upgrade in 28-, 29- and 31-day months, including free days on the 31st and roughly 3x overcharges at the end of February. Fix the day count with the real month length, add boundary tests, and have the tax table and rounding commit reviewed before release. Merging as is creates customer overcharges and refunds on every non-30-day month.

### OWNER SUMMARY
The new upgrade billing assumes every month has 30 days. As a result, some customers would be overcharged (badly at the end of February) and others would get a free day at the end of 31-day months. It also quietly uses a default tax rate when it does not recognize a customer's region, and it ships with no tests. It should be corrected and tested before it goes live, and someone should check the tax rate file and rounding rules it relies on.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "PR #214 diff against base", "status": "not_seen", "matters": true},
    {"item": "callers of prorated_cents", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "billing/proration.py", "kind": "file"},
      {"unit": "billing/proration.py:prorated_cents", "kind": "function"},
      {"unit": "billing/proration.py:TAX_TABLE load", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "billing/tax_table.json", "reason": "not supplied"},
      {"unit": "commit a1b2c3d4e5", "reason": "not supplied"},
      {"unit": "callers of prorated_cents", "reason": "not supplied"},
      {"unit": "timezone of upgrade_on", "reason": "depends on callers, not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:9,14-17",
     "scenario": "Fixed 30-day month: upgrade on Jan 31 is charged 0 (remaining=30-31+1=0); Feb 28 non-leap is charged 3/30 instead of 1/28 (~3x overcharge); Feb 15 charged 16/30 instead of 14/28.",
     "fix": "remaining = calendar.monthrange(d.year, d.month)[1] - d.day + 1; divide by that month length; drop the dead clamp.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "prorated_cents(3000, date(2026,1,31)) with tax rate 0: expect 97, observe 0 (hand-traced; not executed, no tools)."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:12,19",
     "scenario": "A region missing from the table, differently cased, or omitted by the caller is silently taxed at the default rate instead of the customer's region rate.",
     "fix": "Make region required; raise or alert on an unknown region instead of falling back.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "prorated_cents(1000, date(2026,3,10), region='nonexistent'): expect an error, observe a default-taxed amount."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "PR #214 (only billing/proration.py changed)",
     "scenario": "No tests accompany a production billing change; month-length regressions such as F1 ship undetected.",
     "fix": "Add parametrized boundary tests (1st, 31st, Feb 28/29 leap and non-leap, a 30-day month) and confirm they fail against the current code.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Revert the month-length fix after adding the tests; the Jan 31 and Feb 28 cases must go red."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:7",
     "scenario": "The tax table is loaded once at import; long-running workers bill stale rates after a table update until restarted.",
     "fix": "Document a restart-on-deploy requirement, or load the table through versioned config with a reload hook.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Start a worker, change a rate in tax_table.json, call prorated_cents: the old rate is still applied."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "billing/tax_table.json",
     "suspicion": "Rate format or missing keys could make every tax computation wrong or raise.",
     "unresolved_fact": "Whether rates are fractions or percents, whether a 'default' key exists, and whether all billed regions are present."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18,20",
     "suspicion": "Two-step rounding (net, then gross) may not match the policy in commit a1b2c3d4e5.",
     "unresolved_fact": "The rounding rule actually specified in commit a1b2c3d4e5."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "callers of prorated_cents",
     "suspicion": "Callers may pass the old plan's price, non-integer amounts, or no region.",
     "unresolved_fact": "What every call site passes for monthly_price_cents and region."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "billing/proration.py:12 (upgrade_on)",
     "suspicion": "A UTC date can shift the upgrade day or month near midnight relative to the customer.",
     "unresolved_fact": "Which timezone the callers use to compute upgrade_on."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The remaining_days clamp hides negative charges.",
     "evidence": "day is at most 31, so 30-day+1 >= 0; the clamp never fires. The real defect is F1."},
    {"id": "C2", "candidate": "Float imprecision in the tax rate.",
     "evidence": "Decimal(str(rate)) is used, and all arithmetic is in Decimal."}
  ]
}
```

I could not run `tools/validate_findings.py` against this block in this session.