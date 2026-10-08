**Review report**

**REVIEWED:** PR #214, "Prorate mid-month upgrades". The head SHA and merge base SHA were not supplied. I reviewed only the `billing/proration.py` text given in the inputs, so this report cannot be tied to a commit. Whoever posts it must record the head SHA the file came from. Any later commit is unreviewed.

**TIER:** High. The change computes customer charges and applies regional tax, which is money movement in production billing. High tier requires two rounds, ideally on two vendors. **This is round 1 only. The PR is not reviewed until round 2 runs.**

**DATA (Step 3):** The file contains no personal data or secrets. Whether this endpoint is approved for the billing codebase was not stated. The owner should confirm it before round 2 is sent anywhere.

**REVIEWERS:** Round 1 by a separate instance (Claude Opus 5.5, claude-opus-5-5) with no part in writing the change. No commit trailers were supplied, so the author is unknown.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `billing/proration.py:8`, `:13` | The request says "from D to the end of that month", which means calendar days. The code always divides by 30 and computes remaining days as `30 - D + 1`. Examples: **Jan 31**, price 3100¢: `remaining_days = 0`, so the charge is **0** (correct net is 100¢). **Jan 30**, 3100¢: 1/30 gives 103¢ (correct is 2/31, 200¢). **Feb 15, 2026**, 2800¢: 16/30 gives 1493¢ (correct is 14/28, 1400¢), an overcharge of 93¢ before tax. Every 28-, 29- and 31-day month bills wrong amounts. Day-31 upgrades are free. | `prorated_cents(3100, date(2026,1,31), <0%-tax region>) == 100`. `prorated_cents(2800, date(2026,2,15), …) == 1400`. Also a leap-year case: `date(2028,2,29)`, 2900¢ gives 100. Use `calendar.monthrange(y, m)[1]` as the oracle. |
| 2 | P1 | `billing/proration.py:11`, `:18` | The request asks for "tax for their region", but region problems fail silently. A caller that omits `region` gets the `"default"` rate. A region code missing from the table, or spelled in a different case or format (`"DE"` vs `"de"`, `"US-CA"` vs `"us_ca"`), also silently gets the default rate. The customer is charged the wrong tax and nothing logs or raises. | Call with a region that is not in the table and assert it raises (e.g. `KeyError`/`ValueError`) rather than returning a total taxed at the default rate. Remove the `region="default"` default and assert that a call without `region` raises `TypeError`. |
| 3 | P1 (unverified: depends on a missing file) | `billing/proration.py:18-19` | The code assumes `tax_table.json` stores rates as fractions (`0.19`). If the a1b2c3d4e5 update stores percentages (`19`), every total is multiplied by 20. If a value is a string or null, the call raises or produces wrong output. I cannot check this without the table. | Load the real `tax_table.json` and assert every value satisfies `0 <= Decimal(str(v)) < 1`, and that a `"default"` key exists. Add a golden test: one known region, 1000¢, mid-month upgrade, expected total stated in cents. |
| 4 | P2 (unverified: depends on a missing commit) | `billing/proration.py:17`, `:19` | The code rounds twice: the net is rounded to whole cents, then tax is applied to the rounded net and the result is rounded again. The PR says rounding "follows the fix in a1b2c3d4e5", which I was not given. If that fix or the regional tax rules require tax computed on the unrounded amount, or a separate tax line rounded on its own, totals will be off by 1¢ on some inputs. The function also returns only a combined total, so an invoice cannot show the tax amount it charged. | Find an input where single and double rounding differ, e.g. price 1001¢, share 1/30, rate 0.075, and assert the result matches the rule in a1b2c3d4e5. Write the expected value from that commit's spec, not from this code. |
| 5 | P3 | `billing/proration.py:8` | The tax table is read once at import time. A missing or malformed `tax_table.json` breaks import of every module that imports `proration`, not only the proration path. Rate updates also take effect only after a process restart, so running workers keep charging old rates after a table deploy. Floats from `json.loads` pass through `str(float)`; using `parse_float=Decimal` would avoid that conversion. | With `tax_table.json` changed on disk, assert the documented behaviour, whether that is reload or required restart. Test that an import with the file absent fails with a clear error. |
| 6 | P3 | `billing/proration.py:14-15` | The `remaining_days < 0` guard is dead code. `date.day` is at most 31, so the expression is never below 0. The clamp also hides finding 1's day-31 zero charge rather than exposing it. Once finding 1 is fixed with real month lengths, remove the guard or turn it into an assertion. | Covered by finding 1's day-31 test. |

**Checked and not a finding:** the code charges the full new-plan price for the remaining days with no credit for the old plan. That matches the request as written ("at the new plan's price"). If the owner intended a difference-based upgrade charge, that is a spec question for the owner, not a code defect.

**FILES NEEDED BUT NOT PROVIDED:**
- `billing/tax_table.json` (needed for findings 2–3)
- commit `a1b2c3d4e5`, i.e. the tax table update and the "rounding fix" (needed for finding 4)
- the tests for `prorated_cents`; none were supplied, so any claim that it is "tested" is unverified
- the callers of `prorated_cents`, to see whether they pass `region` and how they treat the return value
- the PR head and merge base SHAs

---

**Close-out**

The author has not adjudicated, and a reviewer does not adjudicate its own findings, so this is pending.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–6 | Pending: author to decide | — |

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION: do not merge.**
- Finding 1 is a P0: wrong money on every month that is not 30 days long, and a zero charge on day 31.
- Finding 2 is a P1 and cannot be deferred.
- Finding 3 is a P1 that cannot be cleared until the tax table is reviewed.
- The High-tier second round has not run.
- No head SHA was recorded, and no CI check status was supplied, so checks count as missing, not green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "verified by reading supplied code",
      "location": "billing/proration.py:8,13",
      "scenario": "Fixed 30-day month: upgrade on Jan 31 charges 0 instead of 1/31 of price; Feb 15 2026 at 2800c charges 1493c net instead of 1400c; every non-30-day month misbills.",
      "fix": "Use calendar.monthrange(upgrade_on.year, upgrade_on.month)[1] as days in month; remaining = days_in_month - day + 1; share = remaining / days_in_month."
    },
    {
      "severity": "P1",
      "evidence_level": "verified by reading supplied code",
      "location": "billing/proration.py:11,18",
      "scenario": "Missing, misspelled or omitted region silently falls back to the default tax rate, charging the wrong tax with no error.",
      "fix": "Make region required; raise on a region not in the tax table instead of falling back to default."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified: tax_table.json not provided",
      "location": "billing/proration.py:18-19",
      "scenario": "If tax_table.json stores percentages (19) rather than fractions (0.19), totals are multiplied by 20; non-numeric values raise or misbill.",
      "fix": "Validate the table at load (0 <= rate < 1, 'default' present); add a golden test against the real table."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified: commit a1b2c3d4e5 not provided",
      "location": "billing/proration.py:17,19",
      "scenario": "Double rounding (net rounded, then tax applied to rounded net and rounded again) may differ by 1c from the rounding rule in a1b2c3d4e5; tax amount is not returned for invoicing.",
      "fix": "Apply the rounding rule specified in a1b2c3d4e5 explicitly; return net and tax separately if invoices need a tax line."
    },
    {
      "severity": "P3",
      "evidence_level": "verified by reading supplied code",
      "location": "billing/proration.py:8",
      "scenario": "Tax table loaded at import: a missing or bad file breaks importing the module; rate updates need a restart; floats parsed via str(float).",
      "fix": "Load lazily or via an explicit loader with json.loads(..., parse_float=Decimal) and clear errors; document the reload behaviour."
    },
    {
      "severity": "P3",
      "evidence_level": "verified by reading supplied code",
      "location": "billing/proration.py:14-15",
      "scenario": "remaining_days < 0 guard is unreachable (day <= 31) and masks the day-31 zero charge of finding 1.",
      "fix": "Remove the guard or replace it with an assertion after fixing month length."
    }
  ]
}
```