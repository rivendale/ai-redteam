# pr-review report: PR #112

**REVIEWED:** PR #112, head `e61d0b3`, merge base `93ac2f7`. I had only `PR.md`, `change.patch` and the base files. I reconstructed the head by applying the patch to the base by hand, and I could not confirm that this matches `e61d0b3` or that the head has not moved. I did not review in a checkout, so no instruction files from the PR loaded into this session.

**TIER:** Standard. The test is Low risk. The change to `CLAUDE.md` governs what agents run and install, but it only narrows agent behavior. It touches no auth, secrets, data handling or deployed network exposure, and `requirements.lock` is unchanged. This is a judgment call: a reviewer who reads agent instruction files as security-relevant could reasonably choose High. If so, a second round on a different vendor is still owed.

**REVIEWERS:** Reviewer is a single instance of Sonnet 5.5 with no tools, so nothing was run. Author is unknown because no commit trailers were provided. Nothing indicates this session wrote the change. Data sent is a tile-key parser and agent notes, with no personal data, so no endpoint restriction applied.

**Summary of what I checked**
- **Request match:** The test and the install-policy change match the request. The wording goes slightly beyond it (finding 2).
- **New test:** `parse_key("-1/0/0")` isolates the `z < 0` check. If that check were deleted, `2 ** -1` is `0.5`, and `x=0` and `y=0` both pass the range comparison, so no error is raised and the test would fail. That is a read of the code, not a run.
- **"Tests pass" in `PR.md`:** This is an unverified claim. Statically, `test_ok`, `test_out_of_range` and the new test should all pass.
- **Dependency lens:** No dependency, lock entry, hook or payload changed, so the OSV lookup had nothing to compare and was not run. This says nothing about `six==1.16.0` itself.
- **Instruction-file review of `CLAUDE.md`:**
  - It tells agents to run `pip install --require-hashes -r requirements.lock`.
  - It forbids other network fetches and installs, and says to stop if a package is missing.
  - It says to ask a maintainer for a wheel bundle when offline.
  - Nothing in it is aimed at reviewers.
- **Document type:** `CLAUDE.md` is a living document. The change cites no external sources and contains no consent wording.

**FINDINGS**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `CLAUDE.md:5` | On an offline machine, an agent gets a "matching" wheel bundle. The note gives no install command for it. The agent runs `pip install bundle/*.whl` or `--no-index --find-links` without `--require-hashes`, so a swapped or tampered wheel installs unchecked. The hash policy applies only on the networked path. | A doc check that fails unless every install instruction in `CLAUDE.md` includes `--require-hashes`, and that the offline path names the full command. |
| 2 | P3 | `CLAUDE.md:4` | "Do not fetch or install anything else from the network" is broader than the request ("install only pinned, hash-checked packages"). An agent could read it as banning `git fetch`, docs lookups or API calls, or find it contradicted by the network install in the line above. | Not testable by code. Reword to "install packages only from `requirements.lock` with hashes" and confirm the scope in review. |
| 3 | P3 | `CLAUDE.md:3-5` | The policy is advisory. A plain `pip install foo` is unaffected, and nothing in the repo enforces `--require-hashes`. | A CI check that fails if any `requirements.lock` entry lacks `--hash`, or sets `PIP_REQUIRE_HASHES=1` in the agent environment. |

**FILES NEEDED BUT NOT PROVIDED:**
- Commit trailers (authorship).
- CI check status for `e61d0b3`.
- Confirmation that the head SHA is current.
- The definition and location of the "wheel bundle".
- The real head tree, as opposed to the hand-applied patch.

**Close-out:** Not written. It must come after the author adjudicates findings 1-3. Standard tier needs one round, which this is, but CI status is unknown and no finding has a decision yet.

**Provisional recommendation (not an adjudication):** merge after fixes. Finding 1 is a one-line doc fix. Findings 2 and 3 can be deferred with tracking issues.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "static-read of change.patch; not run",
      "location": "CLAUDE.md:5",
      "scenario": "Offline path says to ask a maintainer for the matching wheel bundle but gives no install command. An agent installing the wheels directly or via --no-index --find-links without --require-hashes bypasses hash verification, so a tampered bundle installs unchecked.",
      "fix": "Specify the exact command: pip install --no-index --find-links <bundle-dir> --require-hashes -r requirements.lock, and say never to install the wheels without it."
    },
    {
      "severity": "P3",
      "evidence_level": "static-read; wording ambiguity",
      "location": "CLAUDE.md:4",
      "scenario": "'Do not fetch or install anything else from the network' exceeds the requested scope (package installs) and can be read as banning git, docs or API access, while the install in the preceding line itself uses the network.",
      "fix": "Reword to restrict package installation to requirements.lock with hashes, e.g. 'Do not install packages from any other source.'"
    },
    {
      "severity": "P3",
      "evidence_level": "static-read; not run",
      "location": "CLAUDE.md:3-5",
      "scenario": "The policy is advisory only; a plain 'pip install foo' is not blocked by anything in the repo.",
      "fix": "Add a CI check that every requirements.lock entry has --hash, and/or set PIP_REQUIRE_HASHES=1 in the agent environment."
    }
  ]
}
```