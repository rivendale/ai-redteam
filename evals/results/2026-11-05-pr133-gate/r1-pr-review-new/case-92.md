# PR #112 review report

**REVIEWED:** PR #112 "test negative zoom; hash-checked installs for agents", head `e61d0b3`, merge base `93ac2f7`. These SHAs come from `PR.md`. I had no repository, so I could not confirm them, and the review covers only `change.patch` applied to the files in `base/`. The head has not been checked for movement.

**TIER:** Standard.
- The change adds one unit test and tightens an agent instruction file.
- It adds no dependency, version bump, code path, privilege or network exposure, and `requirements.lock` is untouched, so the dependency supply-chain lens does not apply.
- The instruction-file edit makes agents more restrictive, not less. I still read it as code (Step 1.4).
- The mapping-service stakes did not push it higher, because nothing touches auth, secrets, data handling or exposure.

**REVIEWERS:**
- Reviewer: a fresh Claude instance (Sonnet 5.5) with no part in writing the change.
- Author: unknown, because commit trailers were not provided.
- Data: the code carries no personal data and was sent nowhere beyond this session.
- Instruction files: I started in an empty directory, so no instruction file from the checkout loaded.
- Round budget: one round, which is this review.

**Checks performed**
- `CLAUDE.md` changes: they tell agents to run only `pip install --require-hashes -r requirements.lock`, to fetch nothing else, and to stop if a package is missing. They also tell offline agents to ask a maintainer for a matching wheel bundle. Nothing is aimed at reviewers, and nothing tells an agent to fetch, trust or skip anything unsafe. No injection found.
- Test `test_negative_zoom`: `parse_key("-1/0/0")` gives `int("-1") = -1`, so `z < 0` at `tiles.py:6` raises `ValueError`. The test isolates that clause. Without it, `x=0 >= 2**-1 = 0.5` is false and `y` behaves the same, so nothing would raise and the test would fail. The test therefore guards the check.
- Scope against the request: both requested items are done. Two additions go beyond "install only pinned, hash-checked packages": the ban on any network fetch, and the offline wheel-bundle path (finding 2).
- "Tests pass" is an unverified claim. I could not run anything, and no CI result was provided.
- Lock file: `six==1.16.0` has one hash, which I did not verify and which is outside this diff. `--require-hashes` fails closed if the artifact differs. `six` has no dependencies, so full pinning holds.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `CLAUDE.md:4-6` (head) | The offline path says to get a wheel bundle but gives no install command. An offline agent running the stated command makes pip try the index, retry and fail, or improvise a different install. The stated command also contacts the network, which sits awkwardly beside "Do not fetch or install anything else from the network". Fix: state `pip install --require-hashes --no-index --find-links <bundle-dir> -r requirements.lock` for offline use. This is UNVERIFIED, because I could not run pip. The consumer check is pip's documented `--require-hashes` and `--no-index` behavior. | Docs-only, so no automated test applies. Dry-run the stated offline command in a sandbox with no network and a bundle directory, and confirm it succeeds and rejects a wheel with a wrong hash. |
| 2 | P3 | `CLAUDE.md:5` (head) | "Do not fetch or install anything else from the network during a task" is broader than the request, which was about package installs. An agent may refuse `git fetch` or documentation lookups, or ignore the rule as unworkable. | Docs-only. Narrow the wording to package installs, or record in the PR that the broader ban is intended. |

**FILES NEEDED BUT NOT PROVIDED:**
- Commit trailers, to identify the author.
- CI and check results for head `e61d0b3`.
- Confirmation that the head tree equals base plus `change.patch`.
- The wheel bundle and any documentation of where maintainers keep it, which are referenced but not in the repo.

---

# Close-out (pending)

A reviewer does not adjudicate its own findings, so the author or whoever closes the PR must complete this.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | not yet decided |
| 2 | pending | not yet decided |

**VERIFIED AFTER FIXES:** nothing yet. The head has not moved, and no fix has been made.

**MERGE RECOMMENDATION:** merge after fixes, or after the author defers both P3s with tracking issues.
- Neither finding is a blocker.
- Step 8 is not yet met: both findings lack written decisions, and no check results were provided. A missing check is not green.
- No written rule governs this decision, so I cite none.

```json
{
  "verdict": "approve_with_comments",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "read-only inspection of patch; pip behavior not run",
      "location": "CLAUDE.md:4-6 (head e61d0b3)",
      "scenario": "Offline guidance says to obtain a wheel bundle but gives no install command. An offline agent running the stated command makes pip contact the index and fail, or improvises a different install. The stated command also contacts the network, which conflicts with the no-network wording.",
      "fix": "Document the offline command: pip install --require-hashes --no-index --find-links <bundle-dir> -r requirements.lock (UNVERIFIED, not run), and dry-run it in a sandbox."
    },
    {
      "severity": "P3",
      "evidence_level": "read-only inspection of patch",
      "location": "CLAUDE.md:5 (head e61d0b3)",
      "scenario": "'Do not fetch or install anything else from the network' goes beyond the requested install policy and could block legitimate fetches such as git fetch or doc lookups, or be ignored as unworkable.",
      "fix": "Limit the wording to package installs, or state in the PR that the broader ban is intended."
    }
  ]
}
```