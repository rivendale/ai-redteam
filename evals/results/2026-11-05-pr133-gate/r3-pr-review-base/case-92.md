# pr-review report: PR #112

**REVIEWED:** PR #112, head `e61d0b3` (full SHA not provided), merge base `93ac2f7`. I reviewed the supplied `change.patch` against the `base/` files. I could not check that the patch matches that head.

**TIER:** Standard. The change is a test plus install-policy notes for agents. It touches no auth, secrets, network exposure or data handling, and it adds or bumps no dependency. `requirements.lock` is unchanged, so the dependency lens and the OSV lookup do not apply. The notes do steer how agents install executable code, so I did not take Low. No personal data is involved, so any approved endpoint will do for one round.

**REVIEWERS:** Reviewer: a fresh Sonnet 5.5 instance (`claude-sonnet-5-5`) with no part in writing the change. Author: not determinable, because no commit trailers were supplied.

**Coverage and checks**
- **Request match:** the PR does both things asked for, a test for the negative-zoom check and hash-checked-only installs in the agent notes. It adds nothing extra.
- **New test:** `parse_key("-1/0/0")` gives z=-1, x=0, y=0. Without the `z < 0` check, `2 ** -1` is 0.5 and `0 >= 0.5` is false, so no error would be raised. The test would therefore fail if the check were removed, and with the check in place it passes (`tests/test_tiles.py:9-11`).
- **Install command:** `--require-hashes` needs every requirement pinned and hashed. `six==1.16.0` is pinned with a hash and has no dependencies, so the command is consistent with the lock file.
- **"Tests pass":** this is an unverified claim. I could not run anything, and no CI result was supplied.
- **Injected instructions:** none found in the PR text or diff.
- **Document types:** `CLAUDE.md` is a living document, so editing it in place is correct.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `CLAUDE.md:5-6` | The notes tell offline agents to get a wheel bundle but give no install command. An agent might run the plain `pip install --require-hashes -r requirements.lock`, which tries the network and fails or stalls. It might also improvise a command without `--require-hashes`, which skips the hash check on the bundle. The two bullets also differ slightly: "stop and say so" versus "ask a maintainer". | No test applies to a doc. Evidence of a correct fix: the notes show `pip install --no-index --find-links <bundle_dir> --require-hashes -r requirements.lock` and say what to do first (ask the maintainer). |

I raised no finding on the hash in `requirements.lock`. It looks like the pure-Python wheel hash for six 1.16.0, but I could not confirm that against PyPI, so it is **UNVERIFIED**. The file is unchanged by this PR, so this does not block merge.

**FILES NEEDED BUT NOT PROVIDED:**
- The CI configuration and check results for the head.
- Commit trailers and the full head SHA.
- The wheel bundle (not part of this PR).

**Close-out (to be completed by the author or closer, not by me)**

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending | The author must decide: Accepted with the fix commit named, Deferred with a tracking issue (allowed for P3), or Rejected with evidence. |

VERIFIED AFTER FIXES: nothing yet. If fixes move the head, a targeted read of the `CLAUDE.md` diff is enough.

MERGE RECOMMENDATION: **merge after fixes or adjudication.** The code and test are sound and match the request. Before merging:
1. Finding 1 needs a written decision.
2. The expected checks must be shown present and green. I could not see them, and "Tests pass" is not evidence.
3. Confirm the head is still `e61d0b3`.

No written rule was supplied that settles anything beyond these Step 8 gates, so I cite none.

```json
{
  "verdict": "merge_after_fixes",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "reasoned from the diff; not executed",
      "location": "CLAUDE.md:5-6",
      "scenario": "Offline agents are told to ask for a matching wheel bundle but are given no install command. An agent may run the networked pip install, which fails or stalls, or may improvise an install without --require-hashes, so the bundle is not hash-checked. The wording 'stop and say so' versus 'ask a maintainer' also differs slightly.",
      "fix": "Add the explicit offline command: pip install --no-index --find-links <bundle_dir> --require-hashes -r requirements.lock, and align the wording to 'stop, then ask a maintainer for the bundle'. No test applies to a doc; the evidence is the command text itself."
    }
  ]
}
```