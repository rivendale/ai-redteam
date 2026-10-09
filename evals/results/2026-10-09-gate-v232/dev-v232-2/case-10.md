VERDICT: **REWORK**. The function divides by a fixed 30-day month and counts remaining days against 30. That contradicts the request ("days from D to the end of that month") and mis-charges customers in every month that is not 30 days long, including a free upgrade on the 31st.

CONFIDENCE: **medium**. Limits:
- I reviewed this alone in this session, with no fresh subagent.
- I had no tools, so I traced every figure by hand and ran no code.
- `billing/tax_table.json` and commit `a1b2c3d4e5` were not supplied, and the tax and rounding claims depend on them.

The core date defects do not depend on the missing inputs, so they are high-confidence.

**INPUTS LEDGER**
- **Seen:**
  - The original request (request.md).
  - context.md, which includes a quoted PR description.
  - `billing/proration.py`, the only changed file.
- **Not seen:**
  - `billing/tax_table.json`. **Matters**: the tax rates, the rate format and whether a `"default"` key exists all depend on it.
  - Commit `a1b2c3d4e5`. **Matters**: the PR says rounding "follows the fix in that commit", and I cannot check that.
  - The callers of `prorated_cents`. **Matters**: they decide whether the new plan's price and the customer's region are actually passed in.
  - Any existing tests. **Matters**: the PR changes no test files.

**COVERAGE**
- Scope: the PR diff, which is the whole of `billing/proration.py`.
- Checked:
  - `proration.py` module load (line 7) and the constant (line 8).
  - `prorated_cents` lines 13–19, traced with these inputs: day 1, day 15, day 28 in February, day 30, day 31, an unknown region and an omitted region.
  - The PR description as quoted in context.md.
- Not checked:
  - `tax_table.json` and commit `a1b2c3d4e5` (not supplied).
  - Callers and tests (not supplied).
  - Execution of any code (no tools).

**SEATS AND GATE**
- Seats: one reviewer (this session). There was no subagent tool and no cross-vendor seats.
- Sensitivity gate: passed. The work contains no personal data or credentials, only pricing code.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (hand-traced) | B | `proration.py:8,16` | The share uses a fixed 30-day denominator instead of the actual number of days in the month. The request asks for the days from D to the end of *that* calendar month. | **February 28, 2026, $28.00 plan:** expected net 1/28 of the price, which is 100¢. The code computes (30−28+1)/30 = 3/30, which is 280¢, so the customer pays 2.8× too much. **February 15:** expected 14/28 = 50%; the code charges 16/30 = 53.3%. **January 16, $31.00 plan:** expected 16/31 = 1600¢; the code charges 15/30 = 1550¢. Overcharges in February are a customer-harm and refund exposure. | **Fix:** take `days_in_month = calendar.monthrange(d.year, d.month)[1]` and compute the share as `(days_in_month - d.day + 1) / days_in_month`.<br>**Reproduction (scratch copy):** create `tax_table.json` containing `{"default": 0}`. Then `prorated_cents(2800, date(2026,2,28))` should give 100 and gives 280 (hand-computed). `prorated_cents(3100, date(2026,1,16))` should give 1600 and gives 1550. | y/y/y/y |
| F2 | Critical | CONFIRMED (hand-traced) | B | `proration.py:13-15` | Remaining days are counted against 30. Upgrading on the 31st gives 30−31+1 = 0 days, so the customer is charged nothing. The `< 0` clamp can never trigger, because the day of the month is at most 31. It suggests the boundary was considered, but the actual broken case (the 31st) is not handled. | A customer upgrades on the 31st of January, March, May, July, August, October or December. They get the new plan for one day at a charge of 0¢, tax included. The expected charge is 1/31 of the price plus tax. | **Fix:** the same as F1, with the remaining days counted against the actual month length. Delete the dead clamp, or turn it into an assertion.<br>**Reproduction:** `prorated_cents(3100, date(2026,1,31))` should give 100 at 0% tax and gives 0, whatever the tax rate. | y/y/y/y |
| F3 | Medium | PROBABLE | B | `proration.py:11,18` | Tax lookup fails open. An unknown, misspelled or missing region silently gets the `"default"` rate. The parameter also defaults to `region="default"`, so a caller that forgets to pass the region charges default tax with no error. The request says "tax for their region". | A caller passes `"CA"` where the table key is `"ca"`, or passes a region added after the table was last updated. The customer is charged the wrong tax and nothing is logged. Whether this happens depends on the table and callers, which I did not see. | **Fix:** make `region` a required argument, and raise an error (or alert) on an unknown region instead of falling back.<br>**Reproduction:** with `TAX_TABLE = {"default": "0.10", "ca": "0.0725"}`, `prorated_cents(3000, date(2026,6,1), "CA")` returns 3300 (10% tax). The expected result is an error, or 3218 at the CA rate. | y/n/y/n |
| F4 | Low | CONFIRMED | B | `proration.py:7` | The tax table is read once, when the module is imported. | The tax table update in commit `a1b2c3d4e5` is deployed without restarting the workers. Those workers keep charging the old rates until they restart. | **Fix:** document that a restart is required, or load the table through a cached loader that can be refreshed.<br>**Reproduction:** import the module, edit the JSON file, call the function again, and observe the old rate. | y/y/n/n |

Confirm-or-refute round on F1 and F2:
- **Defense considered:** a "30-day billing month" (30/360 convention) might be deliberate business policy.
- **Rejected:** the original request explicitly asks for the days from D to the end of that calendar month, so a fixed 30-day month is drift from the request. Both findings hold.
- **Sibling search:** I checked every use of `DAYS_IN_BILLING_MONTH` and all other date arithmetic in the file. There are only two uses (lines 13 and 16), and both are listed above. There are no other date calculations.
- **Security:** neither is a security finding, because no trust boundary is crossed.

**NEEDS VALIDATION**
- **Missing `"default"` key:** `TAX_TABLE["default"]` at line 18 is evaluated on every call, because Python evaluates the fallback argument of `.get` before looking up the region. If the table has no `"default"` key, every call raises `KeyError`, even for known regions. To settle: check whether `tax_table.json` contains `"default"`.
- **Rate format:** settle whether rates are stored as fractions (0.0825) or percentages (8.25). With percentages, tax would be multiplied by roughly 100.
- **Rounding:** the code rounds the net amount to whole cents and then rounds the taxed total again. To settle: read whether commit `a1b2c3d4e5` specifies this order, or rounding of the tax line on its own. Also check whether invoices need tax as a separate amount; the function returns only a combined total.
- **New plan's price:** settle whether callers pass the *new* plan's monthly price, as the request requires.
- **Date and time zone:** settle which time zone determines `upgrade_on`. A UTC date can shift the day of the month near midnight, and on the last day of a month that changes F2's outcome.
- **Tests:** settle whether any existing test covers `prorated_cents`. The PR adds none, and the F1 and F2 cases would fail any month-boundary test.

**REFUTED**
- *A negative or zero price breaks rounding.* `Decimal.quantize` with `ROUND_HALF_UP` handles both signs predictably, and nothing in the request involves negative prices.

**WHAT HOLDS UP**
- All money arithmetic uses `Decimal`. The tax rate goes through `str()` first, which avoids binary float artifacts.
- Day 1 correctly charges the full month in any month.
- On days 1–30 of 30-day months (April, June, September, November) the result is correct.
- Rounding is explicit and deterministic.

**UNVERIFIED CLAIMS**
- "Tax rates come from billing/tax_table.json." The path does match line 7, but I could not see the table's contents. To confirm, supply the file.
- "Rounding follows the fix in that commit." To confirm, supply the diff of `a1b2c3d4e5`.

**QUESTIONS FOR THE AUTHOR**
1. Was the fixed 30-day month intended? If so, the request needs to change, and that needs product and legal sign-off.
2. What should happen for an unknown region?
3. What rounding rule does `a1b2c3d4e5` specify, and should tax be returned as its own amount?

**DECISION-MAKER SUMMARY**
Do not merge. F1 overcharges every February upgrade by up to 2.8×, and F2 makes upgrades on the 31st free. If this ships anyway, there will be refunds and complaints in February and lost revenue on the 31st. Fix F1 and F2 by using the actual month length and adding month-boundary tests, and supply the tax table and the referenced commit before re-review.

**OWNER SUMMARY**
The new upgrade-pricing code assumes every month has 30 days. It charges too much in February, slightly too little in 31-day months, and nothing at all for upgrades on the 31st. It should be fixed and tested before release, and the tax rate file it relies on should be checked too.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md (incl. quoted PR description)", "status": "seen", "matters": true},
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "callers of prorated_cents and existing tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-self", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "pricing code only; no personal data or credentials"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "billing/proration.py", "kind": "file"},
      {"unit": "billing/proration.py:prorated_cents", "kind": "function"},
      {"unit": "billing/proration.py:7-8 module load and constant", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "billing/tax_table.json", "reason": "not_supplied"},
      {"unit": "commit a1b2c3d4e5", "reason": "not_supplied"},
      {"unit": "callers and tests", "reason": "not_supplied"},
      {"unit": "execution of any code", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:8,16",
     "scenario": "Share uses a fixed 30-day denominator. Upgrade on 2026-02-28 of a 2800c plan is charged 280c net instead of 100c (2.8x overcharge); 2026-01-16 of a 3100c plan is charged 1550c instead of 1600c.",
     "fix": "Use calendar.monthrange(d.year, d.month)[1] as the month length for both remaining days and the denominator.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Scratch copy with tax_table.json = {\"default\": 0}: prorated_cents(2800, date(2026,2,28)) expected 100, hand-traced 280; prorated_cents(3100, date(2026,1,16)) expected 1600, hand-traced 1550. Not executed (no tools).",
     "security": false,
     "siblings_searched": {"searched": "every use of DAYS_IN_BILLING_MONTH and all date arithmetic in proration.py", "found": "one other use, line 13, reported as F2"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:13-15",
     "scenario": "Upgrade on the 31st of a 31-day month gives remaining_days = 0, so the customer is charged 0c including tax instead of 1/31 of the price plus tax; the < 0 clamp is unreachable.",
     "fix": "Count remaining days against the actual month length (same fix as F1) and remove the dead clamp.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "prorated_cents(3100, date(2026,1,31)) expected 100 at 0% tax, hand-traced 0 at any tax rate. Not executed (no tools).",
     "security": false,
     "siblings_searched": {"searched": "every use of DAYS_IN_BILLING_MONTH and all date arithmetic in proration.py", "found": "line 16, reported as F1"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "billing/proration.py:11,18",
     "scenario": "A region not in the table (case mismatch, new region) or an omitted region argument silently gets the default tax rate, so the customer is charged the wrong tax.",
     "fix": "Make region required and raise or alert on an unknown region instead of falling back.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "With TAX_TABLE = {\"default\": \"0.10\", \"ca\": \"0.0725\"}, prorated_cents(3000, date(2026,6,1), \"CA\") returns 3300; expected an error or 3218."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:7",
     "scenario": "The tax table is read once at import; an updated tax_table.json deployed without a worker restart keeps the old rates in use.",
     "fix": "Document the restart requirement or load the table through a refreshable cached loader.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Import the module, edit tax_table.json, call prorated_cents again, and observe the old rate applied."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18",
     "suspicion": "TAX_TABLE[\"default\"] is evaluated on every call, so a table without a default key raises KeyError for every region.",
     "unresolved_fact": "Whether tax_table.json contains a \"default\" key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18-19",
     "suspicion": "Rates stored as percentages would multiply tax by about 100.",
     "unresolved_fact": "The rate format in tax_table.json."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "billing/proration.py:17-19",
     "suspicion": "Rounding order (net rounded, then total rounded) and a combined total may not match the rule in the referenced commit or invoice requirements.",
     "unresolved_fact": "The rounding rule in commit a1b2c3d4e5 and whether invoices need tax as a separate amount."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "callers of prorated_cents",
     "suspicion": "Callers may pass the old plan's price, or derive upgrade_on in a time zone that shifts the day of the month.",
     "unresolved_fact": "Caller code."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "PR file list",
     "suspicion": "No tests cover the month-boundary cases.",
     "unresolved_fact": "Whether any existing test exercises prorated_cents."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A negative or zero price breaks rounding.",
     "evidence": "Decimal.quantize with ROUND_HALF_UP handles both signs predictably, and the request involves no negative prices."}
  ]
}
```