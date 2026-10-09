> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so nothing was executed. Every figure below was recomputed by hand from the code.

**VERDICT: REWORK.** The function prorates over a fixed 30-day month instead of the actual calendar month the request specifies. Every customer who upgrades in a month that is not 30 days long is charged the wrong amount, and anyone upgrading on the 31st is charged nothing.

**CONFIDENCE: medium.** The core defect is pure arithmetic and certain. The tax and rounding behaviour depends on `billing/tax_table.json` and commit `a1b2c3d4e5`, and I was given neither. Nothing was run.

**INPUTS LEDGER**
- Seen: `request.md`, `context.md` (including the quoted PR description), `billing/proration.py` (supplied as `proration.py`).
- Not seen: `billing/tax_table.json`. **Matters**, because tax correctness, units and region keys all depend on it.
- Not seen: commit `a1b2c3d4e5`. **Matters**, because the PR claims its rounding "follows the fix in that commit", and that cannot be checked.
- Not seen: callers of `prorated_cents` and any tests. **Matters** for whether `region` and the *new* plan price are actually passed.

**COVERAGE**
- Scope: the PR's one changed file.
- Checked: `proration.py` (all lines, `prorated_cents`), `request.md`, `context.md` and the PR description's claims.
- Not checked: `tax_table.json` (not_supplied), commit `a1b2c3d4e5` (not_supplied), callers and tests (not_supplied). Nothing was run (no_tools).

**SEATS AND GATE:** Local same-context review only. No subagent or cross-vendor seats were available. Sensitivity gate: no personal data, credentials or client material in the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (recomputed) | B | `proration.py:8,13,16` | `DAYS_IN_BILLING_MONTH = 30` is used both for remaining days and as the denominator. The request says "from D to the end of that **calendar** month". | Feb 15 2026, price 2800¢: the code uses 16/30 for a net of 1493¢. The correct share is 14/28, a net of 1400¢, so the customer is **overcharged**. Jan 16 2026, price 3100¢: the code uses 15/30 for 1550¢. The correct share is 16/31, 1600¢, so the customer is **undercharged**. Jan 31: the code gives 30−31+1 = 0 days and **charges 0**, where the correct share is 1/31 (100¢ net). Upgrades on Feb 29–30 are impossible dates, but Feb 28 bills 3/30 instead of 1/28. | Use `calendar.monthrange(upgrade_on.year, upgrade_on.month)[1]` as `days_in_month`, with `remaining = days_in_month - upgrade_on.day + 1` and `share = remaining / days_in_month`. Test: for a region with rate 0 (or by asserting the pre-tax net), check `prorated_cents(3100, date(2026,1,16)) == 1600` (observed 1550), `prorated_cents(2800, date(2026,2,15)) == 1400` (observed 1493) and `prorated_cents(3100, date(2026,1,31)) == 100` (observed 0). Add a leap-year case: Feb 15 2028 gives 15/29. | y/y/y/y |
| F2 | Medium | PROBABLE | B | `proration.py:11,18` | Tax lookup fails open. The `region="default"` parameter and `TAX_TABLE.get(region, TAX_TABLE["default"])` silently apply the default rate to any region missing from the table, or to any caller that omits `region`. | A new region, or a key-format mismatch (for example `"CA"` against `"US-CA"`), is taxed at the default rate with no error or log. The request asks for "tax for their region", so tax is under- or over-collected. Whether any real region is missing is unverified. | Make `region` required and raise on an unknown region, or at least log and alert. Test: `prorated_cents(3000, date(2026,1,1), region="ZZ-not-a-region")` should raise; observed behaviour is that it returns the default-taxed amount. | y/n/y/n |
| F3 | Low | CONFIRMED | B | `proration.py:14-15` | The `< 0` clamp is dead code. With `day` ≤ 31 the minimum is 0, so the branch can never run. It suggests the author considered end-of-month edge cases but missed that day 31 yields zero (F1). | No runtime harm on its own, but it gives a false impression that the edge case is handled. | Remove it with the F1 fix, or replace it with an assertion that `remaining >= 1`. Reproduction: no `day` in 1–31 makes line 13 negative (30−31+1 = 0 is the minimum). | n/y/n/n |

F1 sibling search: both uses of `DAYS_IN_BILLING_MONTH` are in this file (lines 13 and 16), and both carry the same defect (numerator and denominator). The rest of the repository was not supplied, so other users of a 30-day constant are unknown. **Not a security finding.**

**NEEDS VALIDATION** (no severity)
- **Tax rate units.** If `tax_table.json` stores percentages (`8.25`) rather than fractions (`0.0825`), line 19 multiplies the charge by 9.25. Settled by: the table contents.
- **Rounding.** The code rounds the net to whole cents, then rounds the tax-inclusive total again. Whether this is the rounding "fix in commit a1b2c3d4e5", and whether tax should be rounded separately per jurisdiction rules, is unknown. Settled by: the commit diff and the tax-rounding policy.
- **New plan price.** The function charges whatever `monthly_price_cents` it receives. Whether callers pass the *new* plan's price is unknown. Settled by: the call sites.
- **Upgrade date timezone.** `upgrade_on` is a naive date, so a late-day upgrade may fall on a different D in UTC than in the customer's local time. Settled by: how callers derive `upgrade_on`.
- **Missing `"default"` key.** If the table has no `"default"` key, every call raises `KeyError` (it fails closed, which is safer). Settled by: the table contents.

**REFUTED**
- *"remaining_days can go negative."* Refuted: 30 − 31 + 1 = 0 is the floor for valid dates.
- *"`Decimal(str(float))` introduces binary float error."* Refuted: `str()` of a JSON float yields its shortest repr (for example `'0.0825'`), so the `Decimal` is exact for typical rates.

**WHAT HOLDS UP**
- Decimal arithmetic with explicit `ROUND_HALF_UP`, with no float math on money.
- An integer-cents return value.
- The table path (`Path(__file__).parent / "tax_table.json"`) matches `billing/tax_table.json` as described.
- A missing table file fails loudly at import.

**UNVERIFIED CLAIMS**
- "Tax rates come from billing/tax_table.json (see the update in commit a1b2c3d4e5)". To confirm, check the commit diff and the table.
- "Rounding follows the fix in that commit". To confirm, compare the commit's rounding with lines 17 and 19.
- No tests were supplied, so any claim of tested behaviour is unverified. A test should be confirmed red against the current code using the F1 cases.

**QUESTIONS FOR THE AUTHOR**
1. Was the 30-day month intentional? The request says calendar month.
2. Are tax rates in the table fractions or percentages, and does it key every billable region?
3. What exactly did commit `a1b2c3d4e5` change about rounding: per-line, per-invoice, or tax rounded separately?

**DECISION-MAKER SUMMARY:** Do not merge. Proration uses a fixed 30-day month, so most upgrades are mis-billed: February upgrades are overcharged, 31-day-month upgrades are undercharged, and day-31 upgrades are free. If it ships anyway, expect systematic billing errors on every upgrade in a non-30-day month, plus unverified tax behaviour.

**OWNER SUMMARY:** This change bills upgrade customers the wrong amount whenever the month isn't exactly 30 days long. February customers pay too much, customers in longer months pay too little, and anyone upgrading on the 31st pays nothing. It needs to be corrected and the tax setup confirmed before it goes live.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "billing/proration.py", "status": "seen", "matters": true},
    {"item": "billing/tax_table.json", "status": "not_seen", "matters": true},
    {"item": "commit a1b2c3d4e5", "status": "not_seen", "matters": true},
    {"item": "callers and tests of prorated_cents", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "billing/proration.py", "kind": "file"},
      {"unit": "billing/proration.py:prorated_cents", "kind": "function"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md (incl. PR description)", "kind": "document"}
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
     "location": "proration.py:8,13,16",
     "scenario": "Fixed 30-day month instead of the calendar month: Feb 15 2026 at 2800c bills net 1493 instead of 1400; Jan 16 2026 at 3100c bills 1550 instead of 1600; Jan 31 bills 0 instead of 100.",
     "fix": "Use calendar.monthrange(year, month)[1] for both remaining days and the denominator.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "With a zero-tax region (or asserting pre-tax net): prorated_cents(3100, date(2026,1,16)) expect 1600, observe 1550; prorated_cents(2800, date(2026,2,15)) expect 1400, observe 1493; prorated_cents(3100, date(2026,1,31)) expect 100, observe 0.",
     "security": false,
     "siblings_searched": {"searched": "all uses of DAYS_IN_BILLING_MONTH in the supplied file", "found": "lines 13 and 16, both affected; rest of repository not supplied"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "proration.py:11,18",
     "scenario": "A caller omitting region, or a region absent from tax_table.json, is silently taxed at the default rate instead of its own.",
     "fix": "Make region required and raise (or alert) on an unknown region.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "prorated_cents(3000, date(2026,1,1), region='ZZ-not-a-region') expected to raise; observed to return the default-taxed amount."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "proration.py:14-15",
     "scenario": "Dead clamp: remaining_days cannot be below 0 for day 1-31, so the branch never runs and gives a false sense the end-of-month edge is handled.",
     "fix": "Remove it with the F1 fix, or assert remaining >= 1.",
     "answers": {"a": false, "b": true, "c": false, "d": false},
     "reproduction": "Evaluate 30 - day + 1 for day in 1..31; the minimum is 0 at day 31, never negative."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "proration.py:18-19",
     "suspicion": "Tax rates may be stored as percentages, making line 19 multiply by (1 + 8.25).",
     "unresolved_fact": "The value format in billing/tax_table.json."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "proration.py:17,19",
     "suspicion": "Double rounding (net, then total) may not match the rounding fix the PR cites.",
     "unresolved_fact": "The diff of commit a1b2c3d4e5 and the tax-rounding policy."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "proration.py:11",
     "suspicion": "Callers may pass the old plan price rather than the new plan's price.",
     "unresolved_fact": "The call sites of prorated_cents."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "proration.py:11",
     "suspicion": "upgrade_on may be derived in UTC rather than the customer's local date, shifting D.",
     "unresolved_fact": "How callers compute upgrade_on."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "remaining_days can go negative.", "evidence": "30 - 31 + 1 = 0 is the minimum for any valid day."},
    {"id": "C2", "candidate": "Decimal(str(float)) introduces float error in the tax rate.", "evidence": "str() of a JSON float yields its shortest repr, so the Decimal is exact for typical rates."}
  ]
}
```

I could not run `tools/validate_findings.py` against this block because no tools were available.