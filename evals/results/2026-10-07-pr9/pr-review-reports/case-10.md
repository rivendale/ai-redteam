# pr-review: PR #214, "Prorate mid-month upgrades"

## Review report

**REVIEWED:** PR #214. **Head SHA and merge base SHA were not provided**, so I could not freeze the target (Step 1). This review covers only the text of `billing/proration.py` as supplied in this session. If that text differs from the PR head, this review does not apply to the head. Whoever closes the PR must record both SHAs and confirm the reviewed text matches the head.

**TIER: High.** The change computes customer charges and applies tax, which is money movement in production billing. High tier requires two rounds, ideally on two vendors. **This is round 1 of 2. The PR is not reviewed until round 2 has run.**

**Data protection (Step 3):** No approved-endpoint list was given. The supplied code contains no personal data or secrets, only pricing logic. Before round 2 is sent anywhere, the owner should confirm which endpoint is approved for billing source code.

**REVIEWERS:** Round 1 was this instance (Claude Opus 5.5, `claude-opus-5-5`). I had no tools, so nothing was executed and every result below is a hand trace. This session did not write the change. The author is unknown because no commits or `Co-Authored-By` trailers were supplied; record it from the commit trailers at close-out.

**Scope check against the request:** The request is "days from D to the end of *that calendar month*, at the new plan's price, plus tax for their region." The code uses a fixed 30-day month (finding 1) and silently substitutes a default tax rate for unknown regions (finding 2). So it does not do what was asked. I found nothing extra beyond the request.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `billing/proration.py:8`, `:13`, `:16` | `DAYS_IN_BILLING_MONTH = 30` replaces the calendar month the request specifies. Hand-traced examples with price 3000 cents, tax 0: **(a)** Upgrade on Jan 31 gives `remaining_days = 30-31+1 = 0`, so the charge is **0**. The correct charge is 1/31 × 3000 = **97**, so the upgrade is free. **(b)** Upgrade on Feb 15, 2026 (28 days) gives 16/30, so the code charges **1600**. The correct charge is 14/28 = **1500**, an overcharge of 6.7%. **(c)** Upgrade on Feb 29, 2028 gives 2/30, so the code charges **200**. The correct charge is 1/29 = **103**, nearly double. **(d)** Upgrade on Jan 2 gives 29/30 = **2900** instead of 30/31 = **2903**. Every month that is not 30 days long is mispriced, which means wrong money for most customers. The unused `date` import (`:3`) suggests calendar logic was intended. | Parametrised test: `prorated_cents(3000, date(2026,1,31), region_with_rate_0) == 97`, `(…, date(2026,2,15)) == 1500`, `(…, date(2028,2,29)) == 103`, and `(…, date(2026,1,2)) == 2903`. Use `calendar.monthrange(y, m)[1]` for the expected days. All four fail today. |
| 2 | **P1** | `billing/proration.py:18` | `TAX_TABLE.get(region, TAX_TABLE["default"])` silently applies the default rate to any region missing from the table. Examples include a typo, a new region, case differences such as `"DE"` vs `"de"`, and `None`. The request asks for "tax for their region", and this charges the wrong tax with no error or log. If the table has no `"default"` key, **every** call raises `KeyError`, including calls for valid regions, because the fallback argument is evaluated eagerly. (Not verifiable without the table, see below.) | `prorated_cents(3000, date(2026,1,1), region="unknown-xx")` should raise a clear error, or follow a documented, owner-approved rule. Today it returns the default-taxed amount. Also test that removing `"default"` from a fixture table does not break lookups of known regions. |
| 3 | **P1** (unverified, file not provided) | `billing/proration.py:18–19` | The units of the tax rate are unknown. The code treats the value as a fraction (`1 + tax_rate`). If `tax_table.json` stores percentages (for example `20` for 20%), every charge is multiplied by 21. I cannot rule this out without the file. | Load the real `tax_table.json` and assert every value is in `[0, 1)`. Add a golden test for one known region, for example 1000 net at 20% giving 1200. |
| 4 | **P2** (unverified, commit not provided) | `billing/proration.py:17`, `:19` | The code rounds twice: once to whole cents on the net amount, then again after tax. Depending on jurisdiction and invoicing rules, tax may need to be computed on the unrounded net, or rounded per line with a different mode. Those approaches can differ by 1 cent per invoice. The PR says "rounding follows the fix in commit a1b2c3d4e5", which I cannot check. This is a claim, not evidence. | Pick a case where single and double rounding differ, for example net 1250×(1/30) with a 7.5% rate. Assert the result the fix in a1b2c3d4e5 specifies. |
| 5 | **P2** | `billing/proration.py:7` | The tax table is read once at import time. Updates to `tax_table.json`, such as the one in a1b2c3d4e5, have no effect until every billing process restarts. Until then, old rates are charged. A missing or malformed file also crashes import of the whole billing module, not just proration. | Test that changing the fixture table after import changes the result, or that the loader is injectable. Separately, test that a missing file raises a clear error at call time, not at import time. |
| 6 | **P3** | `billing/proration.py:11`, `:17` | There is no input validation. A float price such as `19.99`, passed in dollars by mistake, yields a 0–20 cent charge with no error. `Decimal(float)` also carries binary noise. Negative prices are accepted. | `prorated_cents(19.99, date(2026,1,1))` and `prorated_cents(-100, …)` should raise `TypeError`/`ValueError`. Today they return small or negative charges. |
| 7 | **P3** | `billing/proration.py:14–15` | The `remaining_days < 0` clamp is dead code because `day ≤ 31` gives a minimum of 0. It hides the real bug in finding 1, where day 31 gives 0 days. Once finding 1 is fixed, `remaining_days` is always at least 1. | Covered by the finding 1 test. Remove the clamp, or assert `remaining_days >= 1`. |

**Owner question (not a finding):** The request says to charge the new plan's price for the remaining days. It says nothing about crediting the unused days of the old plan, and the code gives no credit. The code matches the request as written. The owner should confirm that customers are not meant to pay for both plans over the same days.

**FILES NEEDED BUT NOT PROVIDED:**
- `billing/tax_table.json` (findings 2 and 3)
- commit `a1b2c3d4e5`, its diff and the "rounding fix" it describes (finding 4)
- PR head SHA and merge base SHA
- tests covering `prorated_cents`, if any (none were supplied, so no claim of testing can be credited)
- callers of `prorated_cents`, to check the region values and price units actually passed in
- commit trailers, to identify the author

## Close-out

A reviewer never adjudicates its own findings, so this section is left for the author or whoever closes the PR.

**ADJUDICATION:** pending, one row per finding 1–7 required. Findings 1, 2 and 3 are P0/P1 and cannot be deferred.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge.**
- Finding 1 is an open P0: wrong charges in every month that is not 30 days long, and free upgrades on day 31.
- Finding 2 is an open P1.
- Finding 3 is a possible P1 that cannot be checked without `tax_table.json`.
- The High-tier second round has not run.
- The head and merge-base SHAs are not recorded.
- No CI check status was provided, and a missing check is not green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "hand-traced from supplied code (not executed)",
      "location": "billing/proration.py:8,13,16",
      "scenario": "Fixed 30-day month instead of the calendar month. Upgrade on Jan 31 charges 0 (should be 97 of 3000); Feb 15 2026 charges 1600 (should be 1500); Feb 29 2028 charges 200 (should be 103); Jan 2 charges 2900 (should be 2903).",
      "fix": "Use calendar.monthrange(upgrade_on.year, upgrade_on.month)[1] for days in month; remaining = days_in_month - day + 1; share = remaining / days_in_month."
    },
    {
      "severity": "P1",
      "evidence_level": "read from supplied code",
      "location": "billing/proration.py:18",
      "scenario": "Unknown, typo'd or None region silently gets the default tax rate; if 'default' is missing, every call raises KeyError because the fallback is evaluated eagerly.",
      "fix": "Raise a clear error for unknown regions (or follow an owner-approved, documented fallback with logging); look up 'default' only when actually needed."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified: tax_table.json not provided",
      "location": "billing/proration.py:18-19",
      "scenario": "If tax_table.json stores percentages (e.g. 20) rather than fractions (0.20), every charge is multiplied by 21.",
      "fix": "Validate on load that all rates are in [0, 1); add a golden test for one known region."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified: commit a1b2c3d4e5 not provided",
      "location": "billing/proration.py:17,19",
      "scenario": "Net is rounded to cents before tax and rounded again after; this can differ by 1 cent from single rounding or the rule in a1b2c3d4e5, which cannot be checked.",
      "fix": "Confirm the required rounding rule against a1b2c3d4e5 and jurisdiction rules; add a test case where single and double rounding differ."
    },
    {
      "severity": "P2",
      "evidence_level": "read from supplied code",
      "location": "billing/proration.py:7",
      "scenario": "Tax table read once at import: rate updates are ignored until every process restarts, and a missing or malformed file breaks import of the module.",
      "fix": "Load the table through an injectable, reloadable loader with clear errors at call time."
    },
    {
      "severity": "P3",
      "evidence_level": "read from supplied code",
      "location": "billing/proration.py:11,17",
      "scenario": "Float price in dollars (19.99) yields a charge of a few cents with no error; negative prices are accepted.",
      "fix": "Require int cents >= 0; raise TypeError/ValueError otherwise."
    },
    {
      "severity": "P3",
      "evidence_level": "read from supplied code",
      "location": "billing/proration.py:14-15",
      "scenario": "The remaining_days < 0 clamp can never trigger (day <= 31 gives a minimum of 0) and masks the day-31 zero-charge bug.",
      "fix": "Remove the clamp after the calendar fix, or assert remaining_days >= 1."
    }
  ]
}
```
