**Review report**

**REVIEWED:** PR #214, "Prorate mid-month upgrades". Head SHA and merge base SHA were **not supplied**, and I have no tools to read them. I reviewed only the text of `billing/proration.py` as pasted. This review is not bound to a commit. Before anyone acts on it, record the SHA of the file that was reviewed.

**TIER:** High. The change computes customer charges (money movement) and applies regional tax rates (regulated). This report is **one round**. High tier requires two rounds, ideally on different vendors, so the PR is not reviewed until a second round runs.

**DATA (Step 3):** The file contains billing logic and no personal data or secrets. I can't confirm that this endpoint is approved for the repository's code. The owner should confirm that before the second round goes to a different vendor.

**REVIEWERS:** Claude (Opus 5.5, `claude-opus-5-5`), a separate instance with no part in writing the change. The author is unknown because commit trailers were not supplied.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `billing/proration.py:8`, `:13` | The request says to charge for the days from D to the end of the **calendar** month. The code instead uses a fixed 30-day month. Every month that isn't 30 days long is billed wrong. Examples at a $100.00 (10000¢) plan with tax ignored:<br>- Upgrade on **Jan 31**: `30 - 31 + 1 = 0` remaining days, so the charge is **0¢**. The customer gets the new plan free for a day; correct is 1/31 × 10000 = 323¢.<br>- Upgrade on **Feb 15**: 16/30 gives 5333¢; correct is 14/28, which is 5000¢. That is a **6.7% overcharge**.<br>- Upgrade on **Jan 15**: 16/30 gives 5333¢; correct is 17/31, which is 5484¢. That is an undercharge.<br>The `remaining_days < 0` clamp on line 14 can never trigger, because day ≤ 31 gives a minimum of 0. It hides nothing and tests nothing. | Parametrised test of the net charge (tax rate 0):<br>- `(10000, date(2026,1,31))` gives 323<br>- `(10000, date(2026,2,15))` gives 5000<br>- `(10000, date(2024,2,29))` gives 345 (1/29)<br>- `(10000, date(2026,1,15))` gives 5484<br>- `(10000, date(2026,4,1))` gives 10000<br>All except the first-of-a-30-day-month case fail today. The fix derives the month length from `calendar.monthrange(upgrade_on.year, upgrade_on.month)[1]`. |
| 2 | P1 | `billing/proration.py:11`, `:17` | The request says to charge "tax for their region". The code silently falls back to the `"default"` rate in two cases: a region missing from the table (for example a new region, or a casing mismatch like `"de"` vs `"DE"`), and a caller that omits `region` (the parameter defaults to `"default"`). Either way the customer is charged the wrong tax and nothing errors or logs, so the wrong tax is collected and remitted. | Calling `prorated_cents(10000, date(2026,4,1), region="XX")` with `"XX"` absent from the table should raise, for example `KeyError` or a domain `UnknownTaxRegion`. Today it returns the default-tax total. A second test checks that `region` is a required argument (no default). |

**Checked and not raised:**
- `Decimal(str(float))` for the tax rate gives the exact decimal literal from the JSON.
- Charging at the full new-plan price matches the request as written, which says nothing about crediting the old plan.

**Unverified claims from the PR description:**
- The PR says rounding "follows the fix in a1b2c3d4e5". I could not check this. The code rounds net to the cent, then rounds net-plus-tax again, and returns no separate tax amount. Whether that matches the rule in that commit, or the invoicing and tax requirements for each region, is **unverified**. It is not a finding because I have no spec to show it wrong.
- No tests for this file were shown. "Tested" should not be assumed.

**FILES NEEDED BUT NOT PROVIDED:**
- PR head SHA and merge base SHA.
- `billing/tax_table.json` at the PR head: does it contain `"default"`, which rates, and is the region key format the same as what callers pass?
- Commit `a1b2c3d4e5` (the rounding rule and the tax table update).
- Callers of `prorated_cents`: do they pass `region`, and is `upgrade_on` in the customer's timezone or UTC?
- Tests covering `billing/proration.py`.
- CI check results for the head.

**Close-out**

Not written. A reviewer does not adjudicate its own findings. The author must give each finding a decision (Accepted with fix commit and regression test, Deferred for P2/P3 only, or Rejected with evidence), and whoever closes the PR writes the close-out.

**ADJUDICATION:** pending, for #1 (P0) and #2 (P1). Neither can be deferred.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge.** Open items:
- P0 #1 (wrong charge in every month that isn't 30 days long, and a 0¢ charge on the 31st) is unresolved.
- P1 #2 (silent default tax rate) is unresolved.
- The second High-tier round has not run.
- The head SHA was not recorded.
- The rounding rule and tax table were not reviewed.
- CI checks were not seen.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code_read",
      "location": "billing/proration.py:8,13",
      "scenario": "Fixed 30-day month instead of the calendar month the request specifies. An upgrade on Jan 31 gives remaining_days=0 and charges 0 cents. An upgrade on Feb 15 charges 16/30 (5333 of 10000) instead of 14/28 (5000), a 6.7% overcharge. An upgrade on Jan 15 charges 16/30 instead of 17/31. The remaining_days<0 clamp is dead code.",
      "fix": "Use days_in_month = calendar.monthrange(upgrade_on.year, upgrade_on.month)[1]; remaining = days_in_month - upgrade_on.day + 1; share = remaining/days_in_month. Add parametrised tests for Jan 31, Feb 15, leap-year Feb 29, Jan 15, and the 1st of the month."
    },
    {
      "severity": "P1",
      "evidence_level": "code_read",
      "location": "billing/proration.py:11,17",
      "scenario": "A region missing from tax_table.json, a key format mismatch, or a caller that omits region silently gets the 'default' tax rate, so the wrong tax is charged and remitted with no error.",
      "fix": "Make region a required argument and raise on an unknown region instead of falling back to 'default'. Add a test where an unknown region raises."
    }
  ]
}
```