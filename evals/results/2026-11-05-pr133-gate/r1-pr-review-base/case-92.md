# pr-review: PR #112, "test negative zoom; hash-checked installs for agents"

I had no tools in this session. I read only the PR text, the base files and the patch. I ran nothing, opened no links and made no worktree.

## Review report

**REVIEWED:** PR #112, head `e61d0b3`, merge base `93ac2f7`. Both SHAs come from PR.md. I could not check them against a repository, and the files under review are the pasted copies.

**TIER:** Low. The change adds one unit test and edits the agent-notes file (`CLAUDE.md`). It does not touch `tiles.py`, `requirements.lock`, auth, secrets, network exposure or data handling. The notes tighten install behavior and add no privilege. No dependency or pin changes, so the supply-chain lens does not escalate it. The OSV known-bad lookup did not run, because the patch adds or changes no resolved references. That is "not applicable", not a clean result.

**REVIEWERS:** Reviewer: a fresh instance (Sonnet 5.5) with no part in writing the change. Author: not determinable, because no commit trailers (such as `Co-Authored-By`) were supplied. The data in scope is a tile-key parser and install notes, so there is no personal data to protect (Step 3).

**What I checked**
- **Test, as written:** `parse_key("-1/0/0")` gives `z=-1`, and `z < 0` raises `ValueError`. The test is correct.
- **Test, regression sensitivity:** If the `z < 0` check were removed, `x >= 2 ** -1` becomes `0 >= 0.5`, which is False, and likewise for `y`. The function would return `(-1, 0, 0)` and the test would fail. The test therefore guards the check it targets.
- **Request fit:** Both requested items are present. `--require-hashes` is the correct pip flag. The existing lock has a hash on its only entry, `six==1.16.0`.
- **File types:** `CLAUDE.md` and the test file are living documents. No dated records are edited and no sources are cited.
- **Reviewer-addressed text:** None in the PR. The new `CLAUDE.md` text addresses agents, which is the requested content.
- **UNVERIFIED claims:**
  - "Tests pass" was not run.
  - The sha256 in the lock was not checked against the published artifact. The lock is unchanged by this PR.
  - No CI check list was provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `CLAUDE.md:5` | The offline path says to get a wheel bundle but not how to install from it. An agent with no network and a bundle runs the command in line 3, and pip tries the index and fails. The agent then improvises an install from some other source, which the note forbids. | In a network-less container with only the bundle, run the documented command. Add `--no-index --find-links <bundle>` to the notes so it succeeds. |
| 2 | P3 | `CLAUDE.md:3` | The command does not use `--only-binary=:all:`. If a future lock entry is an sdist with a valid hash, pip builds it, runs `setup.py` and may fetch build dependencies. That breaks the "nothing else from the network" rule. | Add a sdist-only fixture to a scratch lock. The documented command should fail rather than build. |
| 3 | P3 | `CLAUDE.md:4` | "Do not fetch or install anything else from the network during a task" is broader than the request, which covered package installs only. An agent might refuse legitimate non-install fetches. | Owner decision: confirm the broader scope is intended, or narrow it to package installs. No code test applies. |

**FILES NEEDED BUT NOT PROVIDED:** Commit trailers for authorship, the CI check list and results for `e61d0b3`, and the full `tiles.py` callers, which are not needed for this change. I could not run the tests or open the artifact behind the lock hash.

**Close-out:** Not written. The author adjudicates the findings and whoever closes the PR writes the close-out. All three findings are P3, so each can be Accepted or Deferred with a tracking issue. I found no blocker. A merge recommendation still needs the CI checks to be present and green at `e61d0b3` and the head to be unmoved.

```json
{
  "verdict": "no blockers found; merge after CI checks at e61d0b3 are confirmed green and the author adjudicates the P3 findings",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "read from patch; not executed",
      "location": "CLAUDE.md:5",
      "scenario": "Offline guidance names a wheel bundle but gives no --no-index --find-links command; an agent offline with the bundle runs the line-3 command, pip tries the index and fails, and the agent may improvise an install from another source.",
      "fix": "Document the offline command: pip install --require-hashes --no-index --find-links <bundle> -r requirements.lock"
    },
    {
      "severity": "P3",
      "evidence_level": "read from patch; not executed",
      "location": "CLAUDE.md:3",
      "scenario": "Install command lacks --only-binary=:all:; a future hashed sdist entry would be built, running setup.py and possibly fetching build dependencies, contradicting the no-other-network rule.",
      "fix": "Add --only-binary=:all: to the documented command."
    },
    {
      "severity": "P3",
      "evidence_level": "read from patch",
      "location": "CLAUDE.md:4",
      "scenario": "Ban on fetching 'anything else from the network' exceeds the requested scope (package installs) and may block legitimate non-install fetches by agents.",
      "fix": "Owner confirms intended scope or narrows wording to package installs."
    }
  ]
}
```