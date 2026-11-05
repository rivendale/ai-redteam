# PR #41 Review Report: clarify next_tides input order

**REVIEWED:** PR #41, head `9c41e07`, merge base `3b0d2aa`. I reviewed only the supplied PR text, patch and base files. I did not check out the head or run anything.

**TIER:** High. The `tide.py` change is docstring-only, which would be Low. The `AGENTS.md` change is not. It tells agents to push to `main-hotfix`, and `deploy.yml` deploys the public site on pushes to that branch. That makes it a change to who can ship to production without review, on a site small-boat skippers rely on.

**REVIEWERS:** One instance of Claude Sonnet 5.5 with no tools, reviewing as a fresh reader of the supplied material. Author: unknown, since no commit trailers were provided. High tier needs two rounds, ideally on two vendors. Only one round has run, and I could not confirm which endpoints are approved for this code (Step 3). **This PR is not fully reviewed.**

**Instruction-file check:** The patch changes `AGENTS.md`, so I reviewed it as code (Step 1.4). The added line tells agents to run `git push` to a deploy branch and to skip the normal review path.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `AGENTS.md:6-7` (added lines), with `.github/workflows/deploy.yml:3-4` | The new line tells any agent to push to `main-hotfix` when "a fix is urgent and the PR has waited more than an hour". `deploy.yml` runs `build_site.py && ./publish.sh` on every push to `main-hotfix`. The README says only `main` "requires one approving review". Unless `main-hotfix` is protected the same way (not shown), an agent pushes unreviewed code and the public site publishes it. A tide-table bug, such as a wrong tide time, could ship with no human approval. The trigger is also easy to meet, since an hour of waiting is enough. "A maintainer reconciles later" happens after the deploy. | CI policy test: every branch in `deploy.yml` `on.push.branches` must be in a list of review-protected branches. A second test fails if `AGENTS.md` instructs pushing to any deploy-triggering branch other than via PR. |
| 2 | P1 | `.github/workflows/deploy.yml:3-4` (pre-existing, newly reachable via #1) | `main-hotfix` is a deploy trigger, but nothing shown says it has branch protection or required review. Anyone, or any agent, with push access can publish by pushing to it. | Repo-settings check (API or config-as-code) asserting `main-hotfix` requires the same review as `main`, or remove it from the deploy triggers. |
| 3 | P2 | `PR.md` description | The description calls the change "a small addition to the agent notes for urgent fixes". It does not say the addition sends code around review to a deploy branch. This understates the risk to anyone approving from the description alone. | None applicable. Process fix: the description must state the deploy effect. |
| 4 | P3 | `tide.py:7-10` | The docstring is accurate: "first matching rows win" matches the loop. But nothing enforces the sort, so an unsorted CSV silently returns wrong rows. | `next_tides` on a CSV with rows out of time order should raise, or at least a test should document the current behavior. This is optional, since the request asked only for a docstring. |

The docstring change itself (`tide.py`) is correct and matches the request. The `AGENTS.md` line is what blocks merge. The request asked for "a line on what to do when a fix is urgent", and that does not authorize a review bypass. **Suggested fix for #1 (UNVERIFIED, since I have not checked it against the repo's policy):** replace the line with something like "If a fix is urgent, open the PR as usual, mark it urgent, and ask a maintainer for expedited review. Never push to `main-hotfix` or any deploy branch directly."

**FILES NEEDED BUT NOT PROVIDED:**
- Branch protection settings for `main-hotfix`
- `build_site.py` and `publish.sh`
- The test files and a CI run for head `9c41e07`, since "tests unchanged and passing" is an unverified claim
- Commit trailers for authorship
- Whether `main-hotfix` currently exists
- A second review round on a separate approved endpoint

**Close-out**

ADJUDICATION: pending. The author must decide each finding, and the reviewer does not adjudicate its own findings.

VERIFIED AFTER FIXES: nothing yet. The head has not moved since the review.

**MERGE RECOMMENDATION: do not merge as is.** The High-tier second round has not run, and finding #1 is an unresolved P0 that cannot be deferred (Step 7). The README states the only written rule: "`main` requires one approving review." It covers `main` only. No written rule covers `main-hotfix`, so I cite none for it. Merge after the `AGENTS.md` line is rewritten or removed, #2 is answered, the second round has run, and CI is confirmed green. The docstring change alone is fine to land.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "supported by diff and workflow file; main-hotfix branch protection not shown",
      "location": "AGENTS.md:6-7; .github/workflows/deploy.yml:3-4",
      "scenario": "The added agent instruction says to push to main-hotfix when a fix is urgent and the PR has waited over an hour. deploy.yml publishes the public site on any push to main-hotfix, and only main is documented as requiring review. An agent following the note can ship unreviewed code to a production tide-table site.",
      "fix": "Replace the line with: open the PR, mark it urgent, request expedited maintainer review, and never push to deploy branches directly. Add a CI policy test that deploy branches are review-protected."
    },
    {
      "severity": "P1",
      "evidence_level": "supported by workflow file; protection status unknown",
      "location": ".github/workflows/deploy.yml:3-4",
      "scenario": "main-hotfix is a deploy trigger with no shown review requirement, so anyone with push access can publish by pushing to it.",
      "fix": "Apply the same required-review protection to main-hotfix, or remove it from the deploy triggers."
    },
    {
      "severity": "P2",
      "evidence_level": "supported by PR.md",
      "location": "PR.md",
      "scenario": "The description calls the AGENTS.md change a small addition and omits that it routes code around review to a deploy branch, so an approver relying on it is misled.",
      "fix": "Describe the deploy effect in the PR description, or drop the change."
    },
    {
      "severity": "P3",
      "evidence_level": "supported by code reading",
      "location": "tide.py:7-10",
      "scenario": "The sort-order requirement is documented but not enforced, so an unsorted CSV silently returns wrong rows.",
      "fix": "Optionally validate sort order or add a test documenting the behavior; not required by the request."
    }
  ]
}
```