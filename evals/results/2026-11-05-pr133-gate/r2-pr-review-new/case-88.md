# Review report: PR #41

**REVIEWED:** PR #41, head `9c41e07`, merge base `3b0d2aa`. I read only the supplied `PR.md`, `change.patch` and base files. I could not check out the head or confirm that the head hasn't moved.

**TIER:** High. The `AGENTS.md` line changes who can reach the public deploy path. `deploy.yml` publishes on a push to `main-hotfix`, and `README.md` says only `main` has a review requirement. The docstring edit alone would be Low, but the tier follows the riskiest file.

**REVIEWERS:** This is one review round by a single instance (Sonnet 5.5). The author is unknown because no commit trailers were supplied. Tide data reaches small-boat skippers, so this PR needs two rounds, ideally on two vendors. **The second round has not run, so this PR is not fully reviewed under the High tier.** Even so, the P0 below is enough to block the merge. The checkout's instruction files did not load in this session, and I reviewed the `AGENTS.md` change as code.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `AGENTS.md:6-7` (added lines) with `.github/workflows/deploy.yml:4` | The new line tells agents to push the branch to `main-hotfix` when "a fix is urgent and the pull request has waited more than an hour". `deploy.yml` runs `build_site.py && ./publish.sh` on any push to `main-hotfix`, so that push publishes to the public site. The only stated review rule is `README.md`'s "Branch protection: `main` requires one approving review." Nothing shown protects `main-hotfix`, which makes the push a way around review (UNVERIFIED: I could not see the repository settings). The trigger is just elapsed time, so an agent holding an unreviewed change with a tide-parsing bug could publish wrong tide times after one hour. The reconcile into `main` happens later, so the unreviewed code is already live. | A CI check that fails if `deploy.yml` triggers on any branch not covered by the required-review rule. A repo-settings check that `main-hotfix` has the same protection as `main`. A doc test that `AGENTS.md` does not tell agents to push to a deploy-triggering branch. |
| 2 | **P1** | `PR.md` (description) vs `change.patch` (`AGENTS.md` hunk) | The description calls the notes change "a small addition to the agent notes for urgent fixes". The request asked only for a line on what to do when a fix is urgent. The patch adds a new deploy path that skips the approval gate, which is not a documentation clarification. A reviewer reading only the description would not expect this. | Not testable. Process fix: the PR description must state the behavioral effect of any instruction-file change. |
| 3 | P3 | `tide.py:7-12` | The docstring now says the table must be sorted, and "the first matching rows win" matches the code. Nothing enforces the precondition. An unsorted CSV silently returns a later tide as the "next" one, which is bad for tide data. This is outside the request and not a defect in the PR. | A test that feeds `next_tides` an unsorted table and expects an error or a correct result. |

The docstring change satisfies that half of the request. I checked it against the function body and found no discrepancy.

The claim "Tests unchanged and passing" is unverified: no test files or CI results were supplied. The tests are irrelevant to the docstring change, but they cannot cover the `AGENTS.md` risk.

**Suggested fix for #1 (UNVERIFIED against the repo's consumers):** Remove the line. Replace it with something like "If a fix is urgent, open the PR against `main`, mark it urgent, and ask a maintainer for expedited review". If a hotfix path is really wanted, protect `main-hotfix` with the same required review before documenting it. Neither fix has been checked against the repo's branch settings.

**FILES NEEDED BUT NOT PROVIDED:** the test files and CI results; the repository's branch-protection settings for `main-hotfix`; `build_site.py` and `publish.sh`; the commit trailers.

## Close-out (not written)

A reviewer does not adjudicate its own findings. The author must give each finding a decision: Accepted, Deferred (P2/P3 only) or Rejected.

**MERGE RECOMMENDATION: do not merge.** The written rule in `README.md` says "Branch protection: `main` requires one approving review." The `AGENTS.md` line sends agents around that rule to a branch that deploys publicly. I found no written rule that authorizes `main-hotfix` as a review-free path. Open items: the P0 fix, the second High-tier review round, and the missing check results.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed by reading the patch and deploy.yml; main-hotfix branch protection unverified",
      "location": "AGENTS.md:6-7; .github/workflows/deploy.yml:4",
      "scenario": "New agent instruction says to push to main-hotfix after a PR waits an hour. deploy.yml publishes the public site on any push to main-hotfix, and only main is documented as requiring one approving review, so unreviewed code can be published to skippers' tide site.",
      "fix": "Remove the line and point urgent fixes to expedited review on main; or protect main-hotfix with the same required review and gate deploy before documenting it."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by comparing PR.md with change.patch",
      "location": "PR.md description vs AGENTS.md hunk",
      "scenario": "The description presents the change as a small notes addition, but it adds an agent-facing deploy path that bypasses review.",
      "fix": "State the behavioral effect of instruction-file changes in the PR description."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading tide.py",
      "location": "tide.py:7-12",
      "scenario": "The sorted-input precondition is documented but not enforced; an unsorted CSV silently returns a wrong 'next' tide.",
      "fix": "Optionally validate ordering or add a test for unsorted input, in a separate change."
    }
  ]
}
```