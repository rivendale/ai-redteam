# PR #214 review: "Prorate mid-month upgrades"

## Review report

**REVIEWED:** PR #214, `billing/proration.py`.
- **Head SHA and merge base: not provided.** I was given the file contents, not a checkout, so this review is pinned to the text supplied above and not to a commit. Whoever closes the PR must confirm that text matches the head SHA they intend to merge.
- I could not use a throwaway worktree, and I could not run anything.

**TIER: High.** This is production billing: money movement, and tax is regulated text.
- **High requires two rounds, ideally on two vendors. This is round 1 only.** The PR is not reviewed until a second round runs on an approved endpoint.
- Data protection (Step 3): the diff carries no personal data, only prices, dates and region codes. A second-vendor round is acceptable if that endpoint is approved for proprietary billing code.

**REVIEWERS:**
- Round 1: a separate Claude instance (Opus 5.5) with no part in writing the change.
- Author: unknown. No commit or `Co-Authored-By` trailers were supplied, so record the author from the commit before closing out.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `proration.py:9`, `:14`, `:17` (`DAYS_IN_BILLING_MONTH = 30`) | The request says "days from D to the end of **that calendar month**", but the code assumes every month has 30 days. **(a)** Upgrade on Jan 31: `remaining_days = 30-31+1 = 0`, so the customer pays **0** for a day on the new plan. This happens every 31-day month. **(b)** Upgrade on Feb 15, 2026 (28 days): the spec share is 14/28 = 0.5, but the code uses 16/30 ≈ 0.533. On a 2800¢ plan that charges 1493¢ instead of 1400¢, an overcharge. **(c)** Upgrade on day 1 of a 31-day month: the share is 30/30, so the customer pays for 31 days at the 30-day price. That one is consistent, but every mid-month day of a 31-day month is mispriced by the 30 vs 31 denominator. | With a zero-tax region: `prorated_cents(3100, date(2026,1,31)) == 100` (returns 0 today). `prorated_cents(2800, date(2026,2,15)) == 1400` (returns 1493 today). Parametrize over all days of Jan, Feb 2026, Feb 2028 and Apr, asserting `share == (days_in_month - D + 1)/days_in_month` using `calendar.monthrange`. |
| 2 | **P1** | `proration.py:19` (`TAX_TABLE.get(region, TAX_TABLE["default"])`) and `:12` (`region="default"`) | The request says "plus tax **for their region**". **(a)** A region code missing from the table, or written in a different form (`"US-CA"` vs `"us-ca"`, or a new region not yet added), silently gets the default rate. The customer is charged the wrong tax with no error or log. **(b)** Any caller that omits `region` gets the default rate, because the parameter has a default. **(c)** A region present with a `null` value makes `Decimal("None")` raise `InvalidOperation` at charge time. | `prorated_cents(1000, date(2026,4,1), region="NOT_A_REGION")` should raise, not return a default-taxed amount. Also test that calling without `region` is a `TypeError` once the default is removed. |
| 3 | **P2** | `proration.py:18` and `:20` (double `quantize`) | The net is rounded to whole cents, then tax is applied and the result rounded again. Example: price 1000¢, upgrade on Apr 30 (share 1/30), tax 0.10. Net 33.33 rounds to 33, ×1.10 = 36.3, rounds to **36**. Rounding once on the unrounded amount gives 36.67, which rounds to **37**. Whether 36 or 37 is correct depends on the rounding rule the PR says comes from commit `a1b2c3d4e5`, which I was not given. Per-line vs per-total tax rounding is often set by jurisdiction. | A fixture taken from the rule in `a1b2c3d4e5`: `prorated_cents(1000, date(2026,4,30), region=<10% region>) == <expected per rule>`. |
| 4 | **P3** | `proration.py:7` (module-level `TAX_TABLE` load) | The tax table is read once at import. **(a)** A tax-rate update (like the one the PR description cites) does not take effect in running processes until a restart, so customers are charged the stale rate in between. **(b)** A missing or malformed `tax_table.json` breaks `import billing.proration` for every importer, not just the proration path. | After changing the table file in a test, a newly loaded rate is used. Alternatively, document and test that a deploy or restart is required. |

The clamp at `proration.py:15-16` (`if remaining_days < 0`) is dead code: `date.day` is at most 31, so `remaining_days` is never below 0. It is not a finding on its own, but it shows the author expected a negative case and missed the zero case in Finding 1.

### FILES NEEDED BUT NOT PROVIDED

- **`billing/tax_table.json`.** I need it to confirm that rates are fractions (`0.0825`) and not percentages (`8.25`). Percentages would overcharge tax roughly 100×. I also need to check that `"default"` exists, that no value is `null`, and how region keys are spelled.
- **Commit `a1b2c3d4e5`.** The PR says it defines the rounding rule, and Finding 3 cannot be settled without it.
- **Callers of `prorated_cents`.** I need these to see whether `region` is always passed (Finding 2b) and which timezone determines `upgrade_on`. A UTC-vs-local mismatch on the last day of a month changes D, and with it the month.
- **Tests for this PR.** None were supplied, so any "tested" claim is unverified.
- **Head SHA, merge base and commit trailers** (see above).

**Owner decision pending:** the request does not say whether the customer is credited for the unused part of the old plan. The code charges only the new plan for the rest of the month. That may be intended, but the owner should confirm it explicitly. It is not a finding.

## Close-out

Not written by me: a reviewer does not adjudicate its own findings. Template for the author and closer:

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *pending* (P0, cannot be deferred) | |
| 2 | *pending* (P1, cannot be deferred) | |
| 3 | *pending* | |
| 4 | *pending* | |

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION: do not merge.**
- **Finding 1 is a P0.** It produces wrong charges every month and zero charges on the 31st.
- **Finding 2 is a P1** on regional tax.
- The second High-tier round has not run.
- The head SHA is not pinned.
- CI check status was not provided, and a missing check is not green.
- The tax table and rounding commit the PR depends on have not been reviewed.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed by reading the code against the request",
      "location": "proration.py:9,14,17",
      "scenario": "Fixed 30-day month: upgrade on Jan 31 gives remaining_days=0 and a charge of 0; Feb 15 2026 charges 16/30 instead of 14/28 (1493 vs 1400 cents on a 2800-cent plan). The request specifies the actual calendar month.",
      "fix": "Use calendar.monthrange(upgrade_on.year, upgrade_on.month)[1] as days_in_month; remaining = days_in_month - day + 1; share = remaining / days_in_month. Remove the dead negative clamp. Add parametrized tests over 28/29/30/31-day months."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by reading the code; table contents not seen",
      "location": "proration.py:12,19",
      "scenario": "Unknown or misspelled region, or an omitted region argument, silently gets the default tax rate instead of the customer's regional rate; a null rate raises InvalidOperation at charge time.",
      "fix": "Make region a required argument; raise on a region missing from the table (or with a non-numeric rate) instead of falling back to the default; normalize region keys explicitly."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred; depends on rounding rule in unseen commit a1b2c3d4e5",
      "location": "proration.py:18,20",
      "scenario": "Double rounding: 1000 cents, Apr 30, 10% tax returns 36; rounding once on the unrounded amount returns 37. Which is correct depends on the cited rule.",
      "fix": "Apply the rounding rule from a1b2c3d4e5 (or the jurisdiction's rule) explicitly and pin it with a fixture test."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading the code",
      "location": "proration.py:7",
      "scenario": "Tax table loaded once at import: rate updates are not applied until restart; a missing or malformed file breaks import of the whole module.",
      "fix": "Load through a function with explicit reload/versioning, or document and test that a restart is required on table changes."
    }
  ]
}
```