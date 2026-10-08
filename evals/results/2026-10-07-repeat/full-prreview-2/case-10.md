# PR #214 review: "Prorate mid-month upgrades"

## Review report

**REVIEWED:** PR #214, `billing/proration.py` only.
- **Head SHA:** not provided. **Merge base SHA:** not provided.
- Step 1 could not be completed. This review covers the text of `proration.py` as supplied, not a pinned commit. Treat it as unanchored until someone records the head SHA it applies to.

**TIER:** High. This is production billing (money movement) with tax calculation. The tier requires two rounds, ideally from two vendors. This is round 1 of 2. **The PR is not reviewed until round 2 runs.**

**DATA (Step 3):** Billing logic only, no personal data in the supplied file. I have not been told which endpoints are approved for round 2. The owner should name one before it runs.

**REVIEWERS:** Claude (Opus 5.5, `claude-opus-5-5`), a separate instance with no part in writing the change.
- **Author:** unknown. Commit trailers were not supplied.

**Method:** I read the code only. I had no tools, so nothing was run. Every finding below is a code-reading result, and each comes with a concrete test that would confirm it.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `proration.py:8`, `proration.py:13`, `proration.py:16` | The request says to charge from day D to the end of *that calendar month*. The code assumes every month has 30 days, so the share is wrong in every month that is not 30 days long:<br>• **Day 31 is free.** Upgrade on 2026‑01‑31: `30 - 31 + 1 = 0`, so the charge is **0**. Correct is 1/31 of the price (3100 → 100).<br>• **February overcharges.** 2800¢, upgrade 2026‑02‑15: the code gives 16/30 → **1493**. Correct is 14/28 → **1400**.<br>• **31‑day months undercharge.** 3100¢, upgrade 2026‑03‑02: the code gives 29/30 → **2997**. Correct is 30/31 → **3000**.<br>The `remaining_days < 0` guard at lines 14–15 is dead code, because `day` is at most 31 and so the value is at least 0. It hides nothing but suggests the edge was considered. | Use a zero-tax region and parametrize:<br>• `(3100, 2026‑01‑31) → 100`<br>• `(2800, 2026‑02‑15) → 1400`<br>• `(2900, 2028‑02‑15) → 1500` (leap year)<br>• `(3100, 2026‑03‑02) → 3000`<br>• `(3000, 2026‑04‑01) → 3000`<br>All except the last fail today. Fix: `calendar.monthrange(y, m)[1]` for both the remaining days and the denominator. |
| 2 | **P1** | `proration.py:11`, `proration.py:18` | "Tax for their region" becomes a silent fallback in two ways:<br>• A caller that omits `region` gets `"default"` tax.<br>• A region missing from the table gets the default rate with no error. Causes include a case mismatch (`"de"` vs `"DE"`) or a region that was never added.<br>Either way the customer is charged the wrong tax, and nothing is logged. | `prorated_cents(1000, date(2026,4,1), region="NOT_A_REGION")` should raise (for example `KeyError` or `UnknownTaxRegion`). Today it returns a default-taxed amount. Also make `region` a required argument. |
| 3 | **P2** (conditional on table contents) | `proration.py:18` | `TAX_TABLE.get(region, TAX_TABLE["default"])` evaluates `TAX_TABLE["default"]` **on every call**, even when `region` is present. If `tax_table.json` has no `"default"` key, every call raises `KeyError`, including calls for valid regions. I cannot confirm this, because the table was not supplied. | Monkeypatch `TAX_TABLE = {"DE": 0.19}` and call with `region="DE"`. Expect 19% tax. Today it raises `KeyError: 'default'`. |
| 4 | **P3** | `proration.py:7` | The tax table is read once at import time:<br>• A missing or malformed `tax_table.json` crashes import of the whole billing module, not just tax lookups.<br>• A tax-rate update has no effect until the process restarts. | Load the module with `tax_table.json` absent. Assert that the failure is a clear, specific error at call or config-validation time. Separately, assert a rate change is picked up per the agreed reload policy. |

### Open questions (not findings: no confirmed failure without the missing files)

- **Rounding.** The net is rounded to whole cents, then tax is applied and rounded again (lines 17 and 19). Whether this is correct depends on the "rounding fix in commit a1b2c3d4e5", which I have not seen. I cannot say it matches or breaks that fix.
- **Rate format.** `Decimal(str(...))` is correct if the table stores fractions such as `0.19`. If it stores percentages such as `19`, the tax is 20× too high. This is unknown without the table.
- **Inclusive day D.** The code charges for day D itself (`+1`). The request says "from D to the end", which reads as inclusive, so this looks consistent. The owner should confirm.
- **Callers.** I did not see the callers. I cannot check that they pass `region`, pass integer cents (a float would make `Decimal(float)` carry binary error), or avoid also charging the old plan for the same days.

### FILES NEEDED BUT NOT PROVIDED

- `billing/tax_table.json`
- Commit `a1b2c3d4e5` (the tax-table update and the rounding fix the PR description relies on)
- Tests for `proration.py`. None were supplied, so any claim of "tested" is unverified.
- Callers of `prorated_cents`
- PR head SHA, merge base SHA, and commit trailers

## Close-out

**ADJUDICATION:** Pending. The author adjudicates. The reviewer does not decide on its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — | — (P0: cannot be deferred) |
| 2 | — | — (P1: cannot be deferred) |
| 3 | — | — |
| 4 | — | — |

**VERIFIED AFTER FIXES:** None yet.

**MERGE RECOMMENDATION: Do not merge.**
- **P0 open (#1).** Customers are charged the wrong amount in every month that does not have exactly 30 days. That is 7 of 12 months, and upgrades on the 31st are charged nothing.
- **P1 open (#2).** Wrong tax is applied silently for unknown or omitted regions.
- **High tier.** Round 2 has not run.
- **Missing evidence.** No head or merge-base SHA was recorded. The tax table, the referenced commit and the tests are missing, so the rounding and rate-format claims in the PR description are unverified. No CI check results were supplied, and a missing check is not green.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code_reading_with_worked_examples_not_executed",
      "location": "billing/proration.py:8,13,16",
      "scenario": "Fixed 30-day month instead of the actual calendar month. Upgrade on the 31st charges 0 (3100 -> 0, correct 100). February 15 charges 16/30 (2800 -> 1493, correct 1400). March 2 charges 29/30 (3100 -> 2997, correct 3000). The remaining_days < 0 guard is dead code.",
      "fix": "Use calendar.monthrange(upgrade_on.year, upgrade_on.month)[1] as days_in_month; remaining = days_in_month - day + 1; share = remaining / days_in_month. Add parametrized tests covering 28-, 29-, 30- and 31-day months and the last day of each."
    },
    {
      "severity": "P1",
      "evidence_level": "code_reading",
      "location": "billing/proration.py:11,18",
      "scenario": "An omitted region parameter, or a region missing from tax_table.json (typo, case mismatch, new region), silently gets the default tax rate, so the customer is charged the wrong tax with no error.",
      "fix": "Make region required; raise on unknown region instead of falling back; add a test that an unknown region raises."
    },
    {
      "severity": "P2",
      "evidence_level": "code_reading_conditional_on_unseen_tax_table",
      "location": "billing/proration.py:18",
      "scenario": "TAX_TABLE['default'] is evaluated eagerly as the .get() default, so if the table lacks a 'default' key every call raises KeyError, even for valid regions.",
      "fix": "Look up the region explicitly (and per finding 2, raise on a miss) instead of computing TAX_TABLE['default'] on every call; add a test with a table lacking 'default'."
    },
    {
      "severity": "P3",
      "evidence_level": "code_reading",
      "location": "billing/proration.py:7",
      "scenario": "The tax table is loaded at import: a missing or malformed file breaks import of the billing module, and rate updates need a process restart.",
      "fix": "Load and validate the table via an explicit loader with a clear error; document or implement the reload policy; add a test for a missing or malformed table."
    }
  ]
}
```