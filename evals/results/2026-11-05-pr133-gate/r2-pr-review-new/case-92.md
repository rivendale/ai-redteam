# pr-review report: PR #112

**REVIEWED:** PR #112, head `e61d0b3`, merge base `93ac2f7`. I received only `PR.md`, the patch and the base files. I did not have a checkout of the head, so everything below is a static read of the patch against the base files.

**TIER:** Standard. The change adds a test and edits `CLAUDE.md`, which is an agent instruction file. It does not touch auth, secrets, network exposure or data handling, and it adds or bumps no dependency. `requirements.lock` is unchanged. The mapping-service stakes do not move it up: `parse_key` itself is untouched.

**REVIEWERS:** This is a fresh, independent instance (Sonnet 5.5) with no part in writing the change. The author is unknown because no commit trailers were provided. Data protection (Step 3): the code carries no personal data, and nothing was sent outside this session.

**Instruction-file check:** The patch changes `CLAUDE.md`, so I read it as code. It tells agents to:
- run `pip install --require-hashes -r requirements.lock`;
- fetch nothing else from the network;
- stop and say so if a package is missing;
- ask a maintainer for a matching wheel bundle when offline.

It contains no line aimed at reviewers and no instruction to skip checks. The tests step is kept. `PR.md`'s "Tests pass" is an unverified claim, not an instruction.

**Request fit:** Both parts are met, and nothing extra is added.

**Test check (by reading, not running):** `parse_key("-1/0/0")` hits `z < 0` first and raises `ValueError`. If the `z < 0` clause were removed, `x >= 2 ** -1` becomes `0 >= 0.5`, which is false, and likewise for `y`. No `ValueError` would be raised and the new test would fail. So the test is discriminating, and the short-circuit avoids any float oddity.

**Install command check:** `six==1.16.0` is pinned and hashed. `six` has no dependencies, so `--require-hashes` will not hit an unhashed transitive requirement. I did not verify the hash against PyPI, but the PR does not change it.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `CLAUDE.md:5` (patched) | The offline instruction says to get a wheel bundle but not how to install it. An agent that gets the bundle may run `pip install bundle/*.whl`, or `pip install --no-index --find-links bundle six`. Either bypasses `requirements.lock` and its hashes, which defeats the PR's stated goal. The plain command on line 3 fails offline, so the gap is likely to be hit. | Docs check: the note contains an offline command that keeps hashes, such as `pip install --no-index --find-links <bundle_dir> --require-hashes -r requirements.lock`. Alternatively, a CI grep that fails if `CLAUDE.md` mentions the bundle without `--require-hashes`. |
| 2 | P3 (coverage note) | `PR.md` | "Tests pass" is an assertion. No CI result or run output was provided, so I could not confirm that the new test passes or that the expected checks are green. | Attach the output of `python3 -m unittest discover -s tests` and the CI status for `e61d0b3`. |

**FILES NEEDED BUT NOT PROVIDED:** commit trailers (authorship); CI check list and status for `e61d0b3`; the head checkout. Only the patch was reviewed, so the head state beyond the patch is unconfirmed.

## Close-out (pending)

The author or whoever closes the PR must adjudicate, and I do not adjudicate my own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | Accepted needs a doc fix, with the fix diff read. No test applies to docs, so the evidence is the corrected line. |
| 2 | pending | Needs the CI output. |

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION:** Provisionally merge after fixes. I found no P0 or P1. Merge once finding 1 has a written decision and the expected checks are shown green for the final head. No written rule was provided that covers this decision, so I cite none.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "static reading of patch; not executed",
      "location": "CLAUDE.md:5",
      "scenario": "Offline guidance says to ask for a wheel bundle but gives no hash-preserving install command. An agent holding the bundle may install wheels directly or with --find-links without --require-hashes -r requirements.lock, bypassing the hash check the PR is meant to enforce.",
      "fix": "State the offline command: pip install --no-index --find-links <bundle_dir> --require-hashes -r requirements.lock, and say the bundle must not be installed any other way."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified claim; no CI output provided",
      "location": "PR.md",
      "scenario": "'Tests pass' is asserted without run output or CI status for head e61d0b3, so the green-check merge gate cannot be confirmed.",
      "fix": "Provide the unittest output and CI status for the final head before merging."
    }
  ]
}
```