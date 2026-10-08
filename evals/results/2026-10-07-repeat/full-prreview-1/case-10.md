# PR #214 Review: "Prorate mid-month upgrades"

**Review report**

**REVIEWED:** PR #214 as `billing/proration.py`, supplied as text.
- **Head SHA:** not provided.
- **Merge base SHA:** not provided.
- I could not freeze the target. This review covers only the file content shown in the inputs. It does not cover any particular commit. Anyone using it must confirm that this content matches the PR head they intend to merge.

**TIER:** High.
- The change computes customer charges and applies tax, which is money movement in production billing.
- High tier needs two rounds, ideally from two vendors. This is one round. The PR is not reviewed until a second independent round runs.

**REVIEWERS:**
- **Reviewer:** this session (Claude, `claude-opus-5-5`), one round, reading code only. I had no tools, so nothing was executed.
- **Author:** unknown. No commit trailers were supplied.
- **Independence:** this session did not write the change.
- **Data approval (Step 3):** I was not told which endpoints are approved for this code. The file holds pricing and tax logic and no personal data. The owner should still confirm that this endpoint is approved before this round counts.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `billing/proration.py:8`, `:13`, `:16` | The request says "calendar month", but the code divides by a fixed 30-day month. **(a)** Upgrade on day 31 of a 31-day month: `remaining_days = 30 - 31 + 1 = 0`, so net is 0 and the customer pays nothing for a day on the new plan. **(b)** Upgrade on Feb 28, 2026: 1 day remains, but the code charges 3/30. A 2800¢ plan bills 280¢ instead of 100¢, almost 3× too much. **(c)** Every day-D upgrade in a 31-day month is charged `(31-D)/30` instead of `(32-D)/31`. Examples: day 2 charges 29/30 vs 30/31; day 31 charges 0 vs 1/31. This systematically charges customers the wrong amount. | Use a 0% tax region. `prorated_cents(3100, date(2026,1,31))` should equal 100 (today 0). `prorated_cents(2800, date(2026,2,28))` should equal 100 (today 280). Add a leap-year case: `prorated_cents(2900, date(2028,2,29))` should equal 100. Fix: `calendar.monthrange(y, m)[1]` for both the remaining-days count and the denominator. |
| 2 | P1 | `billing/proration.py:11`, `:18` | Any region missing from the table silently gets the `default` tax rate. This includes a typo, a new region, a case mismatch such as `"DE"` vs `"de"`, and a caller that omits `region` (the parameter defaults to `"default"`). Tax is charged at the wrong rate with no error. The request asks for "tax for their region". | `prorated_cents(1000, date(2026,1,1), region="not-a-region")` should raise. Today it returns `1000 * (1 + default_rate)`. Also test that calling without `region` raises (no default argument). |
| 3 | P2 | `billing/proration.py:7` | The tax table is read once, at import. **(a)** After someone edits `tax_table.json`, long-running workers keep charging the old rate until restarted. **(b)** If the file is missing or malformed in a deploy, importing anything from `billing.proration` fails. That takes down every billing path that imports it, not just proration. **(c)** If the table has no `"default"` key, line 18 raises `KeyError` on every call, because the fallback is evaluated eagerly. | Patch `tax_table.json` after import and assert the new rate is used, or document that a restart is required. Assert that a table without `"default"` fails at load time with a clear error, not per charge. |
| 4 | P3 | `billing/proration.py:14-15` | `remaining_days < 0` can never be true, because `date.day` is at most 31. So `30 - 31 + 1 = 0`. The guard suggests overflow was considered, yet the real day-31 bug (#1) produces 0, not a negative number. Dead code that hides a real case. | This is covered by the #1 tests. After the fix, the guard should be removed or replaced by an assertion that `remaining_days >= 1`. |

**Not raised as findings:** I could not tie these to a concrete failure, so I am recording them as open questions.

- **Double rounding** (`:17`, `:19`). Net is rounded to whole cents, then tax is applied and rounded again. Whether that is correct depends on the rounding rule the PR description cites from commit `a1b2c3d4e5`, which I was not given. I did not judge it.
- **No tests in the PR.** The only changed file listed is `proration.py`. Nothing shows that any of this was tested, and Step 5.3 says to trust nothing on assertion.
- **Tax rate format.** The rate is read as a fraction (`1 + tax_rate`). If the table stores percentages (for example `20`), every charge comes out 21×. I cannot check this without the file.
- **Dependency on another commit.** The PR depends on commit `a1b2c3d4e5`. Nothing shows whether that commit is an ancestor of the PR head or of `main`. If it is not, this PR merges without the tax table and rounding it relies on.

**FILES NEEDED BUT NOT PROVIDED:**
- `billing/tax_table.json`, at the PR head.
- Commit `a1b2c3d4e5`: its diff, and whether it is in the merge base.
- The PR head SHA and the merge base SHA.
- The callers of `prorated_cents`, to see how `region` and `upgrade_on` are supplied and which timezone the date comes from.
- Any tests covering proration.
- CI check status.

---

**Close-out**

The author adjudicates these findings. A reviewer never adjudicates its own findings, so this section stays open.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (P0, so it cannot be deferred) | |
| 2 | Pending (P1, so it cannot be deferred) | |
| 3 | Pending | |
| 4 | Pending | |

**VERIFIED AFTER FIXES:** nothing yet. No fixes have been made.

**MERGE RECOMMENDATION:** Do not merge.
- **Open blockers:**
  - P0 #1: wrong charge amounts in any month that is not 30 days, including a free day-31 upgrade.
  - P1 #2: silent fallback to the default tax rate.
- **Missing High-tier requirements:**
  - The second review round has not run.
  - The head and merge base SHAs are unknown.
  - The tax table and commit `a1b2c3d4e5` have not been reviewed.
  - CI check status is unknown, and a missing check is not green.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code_read",
      "location": "billing/proration.py:8,13,16",
      "scenario": "Fixed 30-day month instead of calendar month: upgrade on day 31 is charged 0; upgrade on Feb 28 is charged 3/30 instead of 1/28 (2800c plan -> 280c instead of 100c); all 31-day-month upgrades are charged (31-D)/30 instead of (32-D)/31.",
      "fix": "Use calendar.monthrange(year, month)[1] for both remaining days (days_in_month - D + 1) and the denominator; add tests for Jan 31, Feb 28 (non-leap), Feb 29 (leap), and day 1."
    },
    {
      "severity": "P1",
      "evidence_level": "code_read",
      "location": "billing/proration.py:11,18",
      "scenario": "Unknown, misspelled, or omitted region silently falls back to the default tax rate, so customers are taxed at the wrong rate with no error.",
      "fix": "Make region a required argument and raise on a region missing from the tax table."
    },
    {
      "severity": "P2",
      "evidence_level": "code_read",
      "location": "billing/proration.py:7",
      "scenario": "Tax table loaded once at import: edited rates are ignored until restart; a missing or malformed file breaks import of the billing module; a table without a 'default' key raises KeyError on every call because the fallback is evaluated eagerly.",
      "fix": "Load and validate the table explicitly (including that 'default' exists, if a default is kept), fail at startup with a clear error, and document or implement reload behaviour."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "billing/proration.py:14-15",
      "scenario": "The remaining_days < 0 guard is unreachable (date.day <= 31 gives a minimum of 0), so it is dead code that masks the real day-31 zero-charge case.",
      "fix": "Remove it once the calendar-month fix lands, or replace it with an assertion that remaining_days >= 1."
    }
  ]
}
```