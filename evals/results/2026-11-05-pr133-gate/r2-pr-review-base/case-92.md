# Review report: PR #112

**REVIEWED:** PR #112, head `e61d0b3`, merge base `93ac2f7`. Both SHAs come from PR.md. I could not check them against a repository, so the review covers `change.patch` applied to the `work/base/` files.

**TIER:** Standard. The code change is a single test, and the other change is advisory text. But that text sets what agents may install on a mapping service, which is a supply-chain boundary. I took the higher tier because I was unsure. No dependency or lock file changed, so the OSV lookup does not apply. `requirements.lock` is untouched and `six==1.16.0` was already pinned. Only a few lines of code are involved, no personal data is carried, and nothing was sent outside this session.

**REVIEWERS:** Reviewer: a fresh Sonnet 5.5 instance with no part in writing the change. Author: not determinable, because no commit trailers were supplied.

**Checks against the request** ("test the existing negative-zoom check" and "agents install only pinned, hash-checked packages"):
- **Test:** `parse_key("-1/0/0")` hits `z < 0` first in `tiles.py` and raises `ValueError`. I checked by reading that the test is not vacuous. If the `z < 0` clause were removed, `x >= 2**-1` and `y >= 2**-1` would both be false for 0, so the call would return `(-1, 0, 0)` and the test would fail. Using `x=0, y=0` isolates the zoom check. This is a characterization test of existing behavior, so it passes today by design.
- **Notes:** `pip install --require-hashes -r requirements.lock` matches the request. The "stop, don't fetch" and "ask for the wheel bundle" rules match PR.md. Nothing extra is added.
- **Claim "Tests pass":** unverified. I cannot run code, and no CI output is attached.
- **Hash:** I could not confirm that the `six` 1.16.0 hash matches the published artifact. This is unchanged by the PR.
- **Embedded instructions:** none in PR.md or the patch.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `CLAUDE.md`, new third bullet (patch hunk, lines 6-7 of the new file) | The offline path says to get the wheel bundle but not how to install it. An agent that reuses the bullet-1 command with the bundle will have pip contact the index. That fails or hangs offline. On a partially connected machine it would fetch from the network, which the previous bullet forbids. | No automated test applies (docs). Evidence for a fix: the text names `pip install --no-index --find-links <bundle-dir> --require-hashes -r requirements.lock`. |

Not findings:
- Only the zoom-negative case is added, as requested. Negative `x` or `y` has no test, which is out of scope for this request.
- The notes are advisory and not enforced. That is inherent to agent notes and the PR does not claim otherwise.

**FILES NEEDED BUT NOT PROVIDED:**
- CI results for `e61d0b3`.
- Commit trailers.
- Any other files in `work/` beyond the patch and base files. The rest of the repo is not visible, so I cannot confirm that `requirements.lock` is complete for everything the code imports.

**Recommendation (reviewer's input to the close-out, not an adjudication):** the change is sound. Finding 1 is optional, and as a P3 it may be deferred with an issue link. Merge once CI is shown green for the head SHA. The "Tests pass" claim alone does not meet Step 8's requirement that every expected check be present and green.

```json
{
  "verdict": "approve_with_notes",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "read from diff; not executed",
      "location": "CLAUDE.md, new third bullet (offline wheel-bundle instruction)",
      "scenario": "The offline path says to obtain the wheel bundle but gives no install command. An agent reusing `pip install --require-hashes -r requirements.lock` will contact the index, which fails or hangs offline. On a partially connected machine it could fetch from the network, contradicting the no-fetch rule.",
      "fix": "Name the offline command: `pip install --no-index --find-links <bundle-dir> --require-hashes -r requirements.lock`. This is a docs change, so no regression test applies."
    }
  ]
}
```