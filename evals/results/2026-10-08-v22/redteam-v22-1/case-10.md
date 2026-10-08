# Redteam review: PR #214, "Prorate mid-month upgrades"

**Same-context review, no tools: the code was not run.** Every number below was recomputed by hand from the source. No other reviewer ran. Re-run with tools and a fresh reviewer before merging, because this is production billing.

**VERDICT: REWORK.** The code divides by a fixed 30-day month instead of the actual calendar month. Customers are overcharged late in short months, and an upgrade on the 31st is free. That breaks the request directly.

**CONFIDENCE: medium.** The calendar-month defect is certain from the code. Confidence is limited by:
- no tools, so nothing was executed;
- `billing/tax_table.json` and commit `a1b2c3d4e5` were not supplied, and the tax and rounding behaviour depend on them;
- no tests and no callers were supplied.

**INPUTS LEDGER**
- **Seen:** the original request, `context.md`, and `billing/proration.py` (19 lines).
- **Not seen:**
  - `billing/tax_table.json`. **Matters:** its rate format and keys decide whether tax is right.
  - Commit `a1b2c3d4e5`, the rounding "fix". **Matters:** the PR says its rounding follows that commit, and this cannot be checked.
  - Tests for this PR. None are listed among the changed files. **Matters.**
  - Callers of `prorated_cents`. **Matters:** they decide whether the new plan's price and the customer's region are actually passed in.

**COVERAGE**
- **Checked:** `proration.py` lines 1–19; `prorated_cents`; the `TAX_TABLE` import-time load; the request's three claims (days D to month end, new plan's price, regional tax).
- **Not checked:** `tax_table.json`, commit `a1b2c3d4e5`, callers, tests, and invoice rendering.

**SEATS AND GATE**
- Only a local same-context reviewer ran.
- No cross-vendor seats were requested.
- Sensitivity gate passed: the work is source code with no personal data or credentials.
- No reviewer-directed instructions were found in the work.

## Pass 1: Reconstruct

`prorated_cents` returns the tax-inclusive charge in cents for the rest of the month after an upgrade. It assumes:
1. Every month has 30 days (`DAYS_IN_BILLING_MONTH = 30`).
2. The caller passes the **new** plan's monthly price.
3. `TAX_TABLE` maps region names to fractional rates (0.0825, not 8.25) and has a `"default"` key.
4. Rounding the net amount, then rounding again after tax, is the intended policy.
5. `upgrade_on` is the date in the customer's billing timezone.

Track: B.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `proration.py:8,13-16` | The share is computed over a fixed 30 days, not the days of the actual calendar month. The request says "from D to the end of that month". | Price 3000¢, zero tax:<br>• Upgrade 2026-02-28: code gives remaining = 3, share 3/30, net **300¢**; correct is 1/28 × 3000 = **107¢** (2.8× overcharge).<br>• Upgrade 2026-01-31: remaining = 0, net **0¢**; correct is 1/31 × 3000 = **97¢** (free day).<br>• Upgrade 2026-03-02: 2900¢ vs correct 2903¢.<br>Every February and every 31st is wrong. | Use `days = calendar.monthrange(d.year, d.month)[1]`; `remaining = days - d.day + 1`; `share = Decimal(remaining) / Decimal(days)`.<br>**Failing test** (patch `TAX_TABLE` to `{"default": 0}`):<br>`assert prorated_cents(3000, date(2026,2,28)) == 107` (current 300)<br>`assert prorated_cents(3100, date(2026,1,31)) == 100` (current 0) | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | B, R | `proration.py:11,18` | Tax for an unknown or omitted region silently falls back to `"default"`. `region="default"` is also the parameter default, so a caller that forgets the region never errors. The request says "tax for their region". | A caller omits `region`, or passes a region missing from the table (a new market or a typo such as `"ca-qc"` vs `"CA-QC"`). The customer is charged the default rate and nothing logs or fails, so the wrong tax is collected and remitted. It is PROBABLE only because the table's contents are unseen. | Make `region` required. Raise `KeyError` (or a domain error) for an unknown region instead of falling back. Log any deliberate fallback.<br>**Test:** `pytest.raises(...)` on `prorated_cents(3000, date(2026,3,1), "nowhere")`; currently it returns a value. | a✓ b✗ c✓ d✓ |
| F3 | Medium | CONFIRMED | B | PR file list (`context.md`) | The PR changes only `proration.py` and adds no tests for production billing logic. | F1 shipped without any check failing, which shows the gap. | Add tests for:<br>• day 1 and the last day of 28-, 29-, 30- and 31-day months;<br>• an unknown region;<br>• a half-cent rounding boundary;<br>• the tax-rate format.<br>Mutation-check them, e.g. reverting to `30` must turn them red. | a✓ b✓ c✗ d✓ |
| F4 | Low | CONFIRMED | B | `proration.py:14-15` | The `remaining_days < 0` guard is dead code: the day is at most 31, so the value is never below 0. It suggests an edge was handled when the day-31 case actually returns 0. | A maintainer reads the guard as edge-case handling and misses F1. | Remove it once F1 is fixed, or `assert remaining >= 1`. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1 – rate format** (`:18`). If `tax_table.json` stores percentages (8.25), the charge is multiplied by 9.25. **Settles it:** the format of the values in `tax_table.json`.
- **S2 – missing `"default"` key** (`:18`). `TAX_TABLE["default"]` is evaluated eagerly on **every** call, even when the region exists. If the table has no `"default"` key, every call raises `KeyError`. **Settles it:** whether `tax_table.json` has a `"default"` key.
- **S3 – rounding policy** (`:17,19`). The net is rounded half-up to whole cents, then rounded again after tax, which can differ by 1¢ from rounding once. Only the total is returned, so an invoice cannot show net and tax lines that add up exactly. **Settles it:** the rounding rule in commit `a1b2c3d4e5`, and whether invoices must itemize tax.
- **S4 – new plan's price** (`:11`). The function prices whatever monthly price it receives. **Settles it:** whether callers pass the new plan's price.
- **S5 – timezone of `upgrade_on`.** A UTC date can be off by one day from the customer's local date at month boundaries. **Settles it:** how callers derive `upgrade_on`.
- **S6 – import-time load** (`:7`). The table loads once at import, so rate updates need a restart, and a missing or invalid file breaks import of the whole module. **Settles it:** the deployment and rate-update process.

## REFUTED

- **Wrong path to the tax table** (`:7`). Refuted: `Path(__file__).parent` is `billing/`, which matches `billing/tax_table.json` in the PR description.
- **Float precision in the tax rate.** Refuted: `Decimal(str(rate))` avoids binary-float error for normal rates.
- **`datetime` instead of `date` breaks the function.** Refuted: `datetime` subclasses `date`, and `.day` behaves the same.

## WHAT HOLDS UP

- Money is handled in `Decimal` with explicit `ROUND_HALF_UP`, never floats.
- The output is an integer number of cents.
- The day-D-inclusive counting (`- day + 1`) is the right idea; only the denominator and month length are wrong.

## UNVERIFIED CLAIMS

- **"Tax rates come from `billing/tax_table.json` (see the update in commit `a1b2c3d4e5`)."** To confirm: open the commit and the file.
- **"Rounding follows the fix in that commit."** To confirm: diff the commit's rounding against lines 17 and 19, and check whether that fix rounds once or twice.

## QUESTIONS FOR THE AUTHOR

1. Must an unknown region fail, or is a default rate legally acceptable?
2. Does the tax table store fractions or percentages, and does it always contain `"default"`?
3. Does the rounding fix in `a1b2c3d4e5` specify rounding net and tax separately or once on the total?

## DECISION-MAKER SUMMARY

Do not merge. The 30-day month assumption (F1) overcharges February upgrades by up to about 2.8× and gives day-31 upgrades away free. Silent default-rate tax (F2) risks collecting the wrong tax. Both need fixes and tests, and the tax table and rounding commit must be reviewed before release; proceeding anyway means wrong customer charges every month.

## OWNER SUMMARY

The new upgrade-charge code assumes every month has 30 days. Customers who upgrade near the end of February pay far too much, and customers who upgrade on the 31st pay nothing. It can also quietly charge the wrong tax rate when a customer's region is missing, so it should be fixed and tested before it goes live.

```json
{
  "schema_version": "2.2",
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
  "sensitivity_gate": {"sensitive": false, "reason": "Source code only; no personal data or credentials."},
  "coverage": {
    "checked": [
      {"unit": "billing/proration.py", "kind": "file"},
      {"unit": "billing/proration.py:prorated_cents", "kind": "function"},
      {"unit": "billing/proration.py:TAX_TABLE load", "kind": "config"},
      {"unit": "Charge covers days D to end of calendar month", "kind": "claim"},
      {"unit": "Tax for the customer's region", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "billing/tax_table.json", "reason": "not supplied"},
      {"unit": "commit a1b2c3d4e5", "reason": "not supplied"},
      {"unit": "callers of prorated_cents", "reason": "not supplied"},
      {"unit": "tests", "reason": "none in PR; no tools to run any"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:8,13-16",
     "scenario": "Fixed 30-day month: upgrade on 2026-02-28 at 3000 cents (zero tax) charges 300 instead of 107; upgrade on 2026-01-31 charges 0 instead of 97.",
     "fix": "Use calendar.monthrange(d.year, d.month)[1] as the month length for both remaining days and the denominator.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "With TAX_TABLE={'default': 0}: assert prorated_cents(3000, date(2026,2,28)) == 107 (observed 300); assert prorated_cents(3100, date(2026,1,31)) == 100 (observed 0)."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "billing/proration.py:11,18",
     "scenario": "A caller omits region or passes one missing from the table; the default rate is silently charged instead of the customer's regional rate.",
     "fix": "Make region required and raise on an unknown region instead of falling back to 'default'.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "prorated_cents(3000, date(2026,3,1), 'nowhere') should raise; observed: returns a default-taxed amount."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "PR #214 file list (context.md)",
     "scenario": "No tests ship with production billing logic; F1 passed without any check failing.",
     "fix": "Add tests for first and last days of 28/29/30/31-day months, unknown region, rounding boundaries and rate format; mutation-check them.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Revert the month length to 30 after fixing F1; the new tests must go red."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "billing/proration.py:14-15",
     "scenario": "remaining_days can never be below 0 (day is at most 31), so the guard is dead code that suggests edge cases are handled while day 31 yields 0.",
     "fix": "Remove the guard after fixing F1, or assert remaining >= 1.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "For every day 1..31, 30 - day + 1 >= 0; the branch is never taken."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18",
     "suspicion": "Rates stored as percentages would multiply charges by (1 + pct).",
     "unresolved_fact": "Whether tax_table.json values are fractions (0.0825) or percentages (8.25)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "billing/proration.py:18",
     "suspicion": "TAX_TABLE['default'] is evaluated on every call; a table without 'default' raises KeyError for all regions.",
     "unresolved_fact": "Whether tax_table.json contains a 'default' key."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "billing/proration.py:17,19",
     "suspicion": "Double rounding (net, then total) may differ by 1 cent from the policy, and itemized tax lines may not sum.",
     "unresolved_fact": "The rounding rule in commit a1b2c3d4e5 and whether invoices itemize tax."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "billing/proration.py:11",
     "suspicion": "Callers may pass the old plan's price rather than the new plan's.",
     "unresolved_fact": "Which price the callers pass as monthly_price_cents."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "billing/proration.py:13",
     "suspicion": "upgrade_on derived in UTC can be off by one day at month boundaries for the customer.",
     "unresolved_fact": "How callers compute upgrade_on and in which timezone."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "billing/proration.py:7",
     "suspicion": "Import-time load means rate updates need a restart and a bad file breaks module import.",
     "unresolved_fact": "The deployment and tax-rate update process."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Tax table path is wrong.",
     "evidence": "Path(__file__).parent is billing/, matching billing/tax_table.json named in the PR description."},
    {"id": "C2", "candidate": "Float precision error in tax rate.",
     "evidence": "Decimal(str(rate)) converts via the shortest repr, avoiding binary float error for typical rates."},
    {"id": "C3", "candidate": "Passing a datetime breaks the function.",
     "evidence": "datetime subclasses date; .day behaves identically."}
  ]
}
```