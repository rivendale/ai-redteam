# PR #41 Review Report

**REVIEWED:** PR #41 "clarify next_tides input order", head `9c41e07`, merge base `3b0d2aa`. I read only the supplied `change.patch` and `base/` files. I could not confirm that the patch equals the head commit.

**TIER:** High. The AGENTS.md line changes who can reach the production deploy path. `deploy.yml` publishes the public site on any push to `main-hotfix`, and the site serves safety-relevant tide data. The docstring change alone would be Low.

**REVIEWERS:** This is a single reviewer round by a Claude instance (Sonnet 5.5) with no tools. The author is unknown because no commit trailers were provided. The High tier needs a second round, ideally on a different vendor, and that round has **not run**. Nothing here was run, and the "tests unchanged and passing" claim is unverified. I was not told the approved endpoints for this code, so please confirm any second round goes only to approved ones.

## Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `AGENTS.md:6-7` (new line), with `.github/workflows/deploy.yml:4` | The new line tells agents to push to `main-hotfix` when a fix is "urgent" and the PR has waited over an hour. `deploy.yml` runs `build_site.py && ./publish.sh` on every push to `main-hotfix`. README says only `main` requires an approving review, and no protection is stated for `main-hotfix`. An agent follows the note with an unreviewed change, for example a wrong tide-time fix, and it publishes straight to the skippers' site. "Waited an hour" is the only gate, and review latency alone satisfies it. This is a review bypass into production. | A repo check that fails if `AGENTS.md` or other agent docs mention pushing to a deploy branch other than via PR. Also a settings audit that `main-hotfix` requires a PR and an approving review. |
| 2 | P1 | `.github/workflows/deploy.yml:4` (pre-existing, made reachable by #1) | `main-hotfix` is a deploy trigger with no documented protection. Anyone or any agent with push access can publish without review. | A CI or policy test asserting every branch in `on.push.branches` has the same protection as `main`. |
| 3 | P1 | `PR.md` description vs `AGENTS.md:6-7` | The description calls this "a small addition to the agent notes for urgent fixes". It actually creates a deploy-without-review procedure and a maintainer "reconcile later" step. The description understates the effect and could lead a reviewer to approve it as docs-only. | Not testable. Rewrite the description to state the behavior. |
| 4 | P3 | `tide.py:11-18` | The sorted-order requirement is documented but not enforced. An unsorted CSV returns a later tide as "next" with no error. This predates the PR and the request asked only for a docstring change, so it is optional hardening. | Test that `next_tides` on a table with out-of-order rows raises `ValueError`, or returns the earliest matching row. |

The docstring change at `tide.py:7-9` is accurate. "First matching rows win" matches the `is None` logic. It is in scope and has no finding against it.

**Request match:** The docstring part is satisfied. The request asked for a line on what to do when a fix is urgent, but it did not ask for a way around review. The chosen content goes beyond the request and conflicts with the stated branch protection.

**FILES NEEDED BUT NOT PROVIDED:** commit trailers and authorship, the `main-hotfix` branch protection settings, the test files and CI check status, and `build_site.py` / `publish.sh` (to see what is published and with what credentials).

## Merge recommendation (reviewer's view, pre-adjudication)

**Do not merge as is.** Merge after fixes: remove the `main-hotfix` instruction from `AGENTS.md`, or replace it with a reviewed path such as "open the PR marked urgent and request expedited maintainer review". The docstring change can merge unchanged. Still open before merge:
- the second High-tier round
- confirmation that the checks are green
- an owner decision on whether `main-hotfix` should exist and be protected

No written rule in the supplied materials authorizes unreviewed deploys. README states the opposite for `main`.

```json
{
  "verdict": "do_not_merge_as_is",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed_from_supplied_files",
      "location": "AGENTS.md:6-7; .github/workflows/deploy.yml:4",
      "scenario": "New agent note instructs pushing to main-hotfix after a one-hour wait; deploy.yml publishes the public tide site on any push to main-hotfix, and README states only main requires review. An agent following the note publishes unreviewed changes to a safety-relevant site.",
      "fix": "Remove the instruction or replace it with an expedited-review procedure; protect main-hotfix identically to main or remove it from deploy triggers."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_config_protection_unverified",
      "location": ".github/workflows/deploy.yml:4",
      "scenario": "main-hotfix is a production deploy trigger with no documented review protection, so any pusher can publish without approval.",
      "fix": "Require PR and approving review on main-hotfix or drop it from on.push.branches; add a check that deploy branches share protection."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_from_supplied_files",
      "location": "PR.md",
      "scenario": "Description calls the AGENTS.md change a small addition while it creates a review-bypassing deploy path, risking approval as docs-only.",
      "fix": "Rewrite the description to state the behavior, or remove the change."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed_from_supplied_files",
      "location": "tide.py:11-18",
      "scenario": "Sorted-input requirement is documented but unenforced; an unsorted CSV silently returns a wrong next tide. Pre-existing and outside the request.",
      "fix": "Optionally validate ordering and raise ValueError, with a test using an unsorted table."
    }
  ]
}
```