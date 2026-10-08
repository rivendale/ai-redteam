# pr-review: PR #214, "Prorate mid-month upgrades"

## Review report

**REVIEWED:** PR #214. The head SHA and merge base SHA were **not provided**, so this review is pinned only to the `proration.py` text supplied in this session. It does not cover any particular commit. Anything outside that text, including commit `a1b2c3d4e5`, was not reviewed.

**TIER:** **High.** The change computes customer charges and tax, which is money movement in production billing. The High tier needs two rounds, ideally from two vendors. **This is round 1 of 2.** The PR is not reviewed until a second round has run.

**REVIEWERS:** Round 1 was done by Claude Opus 5.5 (`claude-opus-5-5`), in a fresh session with no part in writing the change. I had no tools, so I ran no code. The traces below are worked by hand from the code. The author is **unknown**, because no commit trailers were provided. Data handling: the code was supplied in this session and was not sent anywhere else.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `billing/proration.py:8`, `:13`, `:16` | The request asks for "days from D to the end of that **calendar** month". The code uses a fixed 30-day month instead. Hand traces with a 3000-cent plan: **Jan 31** gives `30 − 31 + 1 = 0` remaining days, so the charge is **0** for a day of service. The correct charge is 1/31 × 3000 ≈ 97. **Feb 28, 2026** gives 3/30 = **300**. The correct charge is 1/28 ≈ 107. **Feb 15, 2026** gives 16/30 = 1600. The correct charge is 14/28 = 1500. **Jul 15** gives 16/30 = 1600. The correct charge is 17/31 ≈ 1645. The net effect is that 31-day months are undercharged (day 31 is free) and February is overcharged by up to about 3×. | Use the default region at 0% tax. `prorated_cents(3000, date(2026,1,31)) == 97`, `prorated_cents(3000, date(2026,2,28)) == 107`, `prorated_cents(3000, date(2026,2,15)) == 1500`, `prorated_cents(3000, date(2024,2,29)) == 103` (leap year). All of these fail today. Fix: derive the days in the month from `calendar.monthrange(d.year, d.month)[1]`. |
| 2 | **P1** | `billing/proration.py:11`, `:18` | An unknown or misspelled region (for example `"DE "`, `"de"`, or a newly launched region missing from the table) silently gets the `default` tax rate. A caller that omits `region` also gets `default` because of the parameter default. Either way the customer is charged the wrong tax for their region, and nothing signals it. | `prorated_cents(3000, date(2026,1,10), region="no-such-region")` should raise (for example `KeyError` or `UnknownRegion`). Today it returns a default-taxed amount. Also add a test that `region` is required, with no default. |
| 3 | P3 | `billing/proration.py:14–15` | The guard `remaining_days < 0` can never fire. With the 30-day constant, the minimum is 0 on day 31. The dead branch hides the real defect in #1, which is the zero result on day 31. | Covered by the #1 tests. Remove the guard once the month length is computed correctly. |

**Not findings (no evidence available), but they must be checked in round 2 against the missing files:**
- **Rate format.** Line 18 assumes the table stores fractions such as `0.2`. If `tax_table.json` stores percentages such as `20`, every charge is multiplied by 21. I cannot tell from the code.
- **Rounding policy.** The code rounds the net amount to cents, then applies tax and rounds again (`:17`, `:19`). The PR says rounding "follows the fix in a1b2c3d4e5". That claim cannot be verified without the commit.
- **Missing `default` key.** If `tax_table.json` has no `default` key, every call raises `KeyError` (`:18`). That depends on the table contents.
- **Tests.** No tests were supplied. Any claim that this change is tested is unverified.

**FILES NEEDED BUT NOT PROVIDED:** `billing/tax_table.json`; commit `a1b2c3d4e5` (its diff and message); the PR head SHA and merge base; the tests for `billing/proration.py`; the callers of `prorated_cents`, to see how `region` and `upgrade_on` are passed; the commit trailers that identify the author.

## Close-out

**ADJUDICATION:** Pending. The author has not adjudicated these findings, and a reviewer cannot adjudicate its own findings.

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION:** **Do not merge.**
- P0 #1 produces wrong charges on most upgrade dates. It cannot be deferred.
- P1 #2 is open.
- The High tier's second round has not run.
- The head SHA was not identified, the tax table and rounding commit were not reviewed, and no CI checks were shown. A missing check is not green.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed_by_code_trace",
      "location": "billing/proration.py:8,13,16",
      "scenario": "Fixed 30-day month instead of calendar month. Upgrade on Jan 31 yields 0 remaining days and a charge of 0 (should be ~1/31). Feb 28, 2026 charges 3/30 (300 of 3000) instead of 1/28 (~107). Feb 15 charges 1600 instead of 1500. Jul 15 charges 1600 instead of ~1645. 31-day months are undercharged and February is overcharged.",
      "fix": "Compute days_in_month = calendar.monthrange(d.year, d.month)[1]; remaining = days_in_month - d.day + 1; share = remaining / days_in_month. Add tests for Jan 31, Feb 28 (non-leap), Feb 29 (leap), Feb 15, Jul 15."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_by_code_reading",
      "location": "billing/proration.py:11,18",
      "scenario": "An unknown, misspelled or missing region silently falls back to the 'default' tax rate (TAX_TABLE.get(region, TAX_TABLE['default']) and region='default' parameter default), so customers are charged the wrong tax for their region with no error.",
      "fix": "Make region a required argument and raise on regions absent from the tax table. Add a test that an unknown region raises."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed_by_code_trace",
      "location": "billing/proration.py:14-15",
      "scenario": "The remaining_days < 0 guard can never trigger (minimum is 0 on day 31). Dead code that masks the day-31 zero-charge defect.",
      "fix": "Remove the guard after computing the real month length; covered by the P0 tests."
    }
  ]
}
```