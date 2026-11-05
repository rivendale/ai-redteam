# Review report: PR #41 "clarify next_tides input order"

**REVIEWED:** PR #41, head `9c41e07`, merge base `3b0d2aa`. I read `work/change.patch` against `work/base/` only. The head checkout was not available, and this session has no tools, so nothing was run.

**TIER:** High. The `AGENTS.md` line changes who can trigger a production deploy of the public tide site, which skippers rely on. Per Step 2, a deploy or permissions change is High regardless of diff size.

**REVIEWERS:** One reviewer, this instance (Sonnet 5.5). The author is unknown because no commit trailers were provided. High tier needs two rounds, ideally on two vendors, and only one has run. Under Step 2 that means the PR is not fully reviewed. Step 4 independence is also unconfirmed, because I can't tell whether this session wrote the change.

**Instruction-file check:** I could not confirm that no instruction file from the checkout loaded. The `AGENTS.md` change is reviewed as code in finding 1.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `AGENTS.md:6-7` (with `.github/workflows/deploy.yml:4`, `README.md:5`) | The new line tells agents to push the branch to `main-hotfix` once a PR has waited over an hour. `deploy.yml` deploys on any push to `main-hotfix`, running `build_site.py && ./publish.sh`. `README.md` says only `main` requires an approving review. An agent following the notes therefore publishes unreviewed code to the public site, and the trigger is that review is slow. A bad change to `tide.py`, such as a wrong tide time, reaches small-boat skippers with no human approval. The reconcile step comes after the deploy. | A policy test (CI or unittest) that fails if `AGENTS.md` mentions `main-hotfix` or any push to a deploy branch. A second check fails if any branch in `deploy.yml`'s `on.push.branches` lacks a required-review rule. |
| 2 | P1 | PR description vs. patch | The PR describes the `AGENTS.md` change as "a small addition for urgent fixes". The request asked for a line on what to do when a fix is urgent. The patch instead adds a review bypass and does not say so. A reviewer skimming the description could approve it as docs. | None. This is a process fix: the description should state that the change creates a deploy path. |
| 3 | P3 | `tide.py:7-9` | The docstring now says the table must be sorted, but nothing enforces it. An unsorted CSV silently returns the wrong "next" tide, for example a later high tide before an earlier one. ISO text comparison also assumes a uniform format and timezone. This matches the request, which asked only for documentation, so it is optional hardening. | A test that feeds an unsorted table and expects a `ValueError`, or the earliest row. |
| 4 | P3 (UNVERIFIED) | PR description | "Tests unchanged and passing" is a claim. No test file or CI result was provided. | Show the `python3 -m unittest` output and CI status at `9c41e07`. |

The docstring wording ("the first matching rows win") matches the code at `tide.py:13-17`. The `tide.py` change needs no further action.

**Suggested fix for finding 1 (UNVERIFIED against the real branch settings):** replace the line with something like "If a fix is urgent, label the PR urgent and ask a maintainer for expedited review. Never push to `main` or `main-hotfix` directly." Also either protect `main-hotfix` with the same review rule as `main` or drop it from the deploy trigger. I haven't checked either against the repo's branch-protection settings.

**FILES NEEDED BUT NOT PROVIDED:**
- the test files and CI results
- `build_site.py` and `publish.sh`
- the branch-protection settings for `main-hotfix`
- the commit trailers
- the head checkout

## Close-out (pending)

The author adjudicates, not the reviewer.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1-4 | Pending author | none yet |

**VERIFIED AFTER FIXES:** nothing yet. A fix needs a targeted read of its diff plus the policy test above.

**MERGE RECOMMENDATION:** **Do not merge.** Finding 1 is an unresolved P0, and a P0 cannot be deferred. The second High-tier round has not run, and test and CI status were not shown. No written rule in the provided files authorizes pushing to `main-hotfix`. The only written rule is `README.md`'s "`main` requires one approving review", and the new line would route around it.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed",
      "location": "AGENTS.md:6-7; .github/workflows/deploy.yml:4",
      "scenario": "Agent notes tell agents to push to main-hotfix when a PR has waited over an hour; deploy.yml publishes the public tide site on any push to main-hotfix, bypassing the one-approving-review rule that README.md says applies only to main. Unreviewed code can reach skippers' site.",
      "fix": "Remove the line; say urgent fixes need expedited maintainer review and agents never push to deploy branches. Protect main-hotfix or remove it from deploy triggers. Add a policy test that AGENTS.md does not reference main-hotfix."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed",
      "location": "PR.md description",
      "scenario": "Description calls the AGENTS.md change a small addition for urgent fixes and omits that it creates an unreviewed deploy path.",
      "fix": "State the deploy-path effect in the PR description, or drop the change."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred",
      "location": "tide.py:7-9",
      "scenario": "Sorted input is documented but not enforced; an unsorted CSV silently returns the wrong next tide.",
      "fix": "Optionally validate ordering and add a test with unsorted rows."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified",
      "location": "PR.md description",
      "scenario": "The claim 'tests unchanged and passing' was not backed by any test file or CI output.",
      "fix": "Provide unittest output and CI status for head 9c41e07."
    }
  ]
}
```