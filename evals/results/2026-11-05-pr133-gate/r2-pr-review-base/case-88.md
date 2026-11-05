# PR #41 review report

**REVIEWED:** PR #41 "clarify next_tides input order", head `9c41e07`, merge base `3b0d2aa`. I read only the patch and the base files provided, with no checkout, so SHAs are as stated in PR.md.

**TIER:** High. The `tide.py` docstring change is Low on its own. The `AGENTS.md` line tells agents how to reach a deploy path. `deploy.yml` publishes the public site on any push to `main-hotfix`, and README documents the required review only for `main`. That touches permissions and exposure, and the site feeds tide data to small-boat skippers.

**REVIEWERS:** One independent instance (Sonnet 5.5, `claude-sonnet-5-5`) with no part in writing the change. The author is unknown because no commit trailers were provided. The code carries no personal data, so Step 3 raises no approved-endpoint concern. **High requires two rounds, and only this one has run, so the High-tier review is incomplete.** I could not run anything, so "tests unchanged and passing" is an unverified claim.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `AGENTS.md:6-7` (new); trigger in `.github/workflows/deploy.yml:3-4` | The line tells agents to push a branch to `main-hotfix` once a PR has waited an hour. `deploy.yml` runs `build_site.py && ./publish.sh` on any push to `main-hotfix`, so unreviewed code goes live. The only documented control, one approving review on `main`, never applies. The agent judges "urgent", and the one-hour wait is the only condition. A bad change, such as a wrong tide time from a parsing bug, reaches skippers immediately. The "maintainer reconciles later" step can then carry unreviewed code into `main`. The request asked for a line on what to do when a fix is urgent, not an instruction to bypass review, and the description calls this a "small addition". | A repo-policy check (CI or settings audit) that fails if any branch in `deploy.yml`'s `on.push.branches` lacks required review. It fails today for `main-hotfix` unless protection exists, which I could not see. A second check fails if `AGENTS.md` tells agents to push to a deploy branch. |
| 2 | P3 | `tide.py:7-16` (docstring plus the loop it documents) | The docstring now states the sorted-order requirement, which matches the first-match-wins loop and is accurate. Nothing enforces it. A CSV with a later high tide listed before an earlier one silently returns the later tide as "next", which is wrong data for a skipper. The comparison `row["time"] <= after` is also lexicographic, so mixed timezone offsets in the ISO text would misorder rows. This is out of scope for the PR, so I list it as a follow-up only. | A unit test with an unsorted CSV that expects a `ValueError`, or the true earliest row. It fails today because the function returns the first-listed row. |

**FILES NEEDED BUT NOT PROVIDED:**
- Branch protection settings for `main-hotfix`. Finding 1's severity depends on whether it requires review.
- `build_site.py` and `publish.sh`, to confirm what a push publishes.
- The existing tests, to check the "passing" claim.
- Commit trailers, to record the author.

**Recommendation (reviewer's view, not an adjudication):** do not merge as written. The docstring change is fine on its own. For finding 1, drop the `AGENTS.md` line or reword it. For example: "If a fix is urgent, mark the PR urgent and ask a maintainer for expedited review. Never push to a deploy branch directly." Also protect `main-hotfix` or remove it from the deploy triggers. The close-out and the second High-tier round remain open.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "supported by provided files; main-hotfix branch protection not visible",
      "location": "AGENTS.md:6-7 (new); .github/workflows/deploy.yml:3-4",
      "scenario": "New agent note tells agents to push to main-hotfix when a PR has waited over an hour. deploy.yml publishes the public site on any push to main-hotfix, bypassing the documented one-review requirement on main. Unreviewed incorrect tide data can reach skippers, and later reconciliation can carry it into main.",
      "fix": "Remove or reword the line to request expedited maintainer review and forbid direct pushes to deploy branches; protect main-hotfix or drop it from deploy triggers. Add a policy check that every deploy-triggering branch requires review."
    },
    {
      "severity": "P3",
      "evidence_level": "read from code",
      "location": "tide.py:7-16",
      "scenario": "Sorted-order requirement is documented but not enforced. An unsorted CSV silently returns a later tide as the next one; lexicographic ISO comparison also misorders mixed timezone offsets. Out of scope for this PR.",
      "fix": "Validate ordering or sort rows, and add a unit test with an unsorted table expecting an error or the earliest row."
    }
  ]
}
```