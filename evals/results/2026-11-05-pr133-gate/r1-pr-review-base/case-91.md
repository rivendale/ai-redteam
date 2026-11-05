# PR #17 review report

**REVIEWED:** PR #17 "test -40 degrees; agent notes". Head `4f2b9e1`, merge base `a0c3d55`. Both SHAs come from `PR.md` only. There is no git repository in this session, so I could not check them against real history. I reviewed `change.patch` against the `base/` files, not a checkout of the head.

**TIER:** Low. The PR changes one test and one docs file, and touches no auth, secrets, network exposure or data handling. No sensitive data is involved, so Step 3 is satisfied by reviewing in this session without sending code elsewhere.

**REVIEWERS:** This session (Claude Sonnet 5.5, `claude-sonnet-5-5`) reviewed it, with no memory of writing the change. The author and commit trailers (e.g. `Co-Authored-By`) were not provided, so the author is unknown. One independent read is enough at this tier. I had no tools, so I did not run anything.

**What I checked**
- **The new test:** `c_to_f(-40)` evaluates as `-40*9 = -360`, then `/5 = -72.0`, then `+32 = -40.0`. `assertEqual(-40.0, -40)` passes, and the float arithmetic is exact here.
- **"Standard library only":** `tests/test_temp.py` imports `unittest` and `temp`, and `temp.py` has no imports. The claim is true.
- **Import path:** `python3 -m unittest discover -s tests` puts the cwd on `sys.path`, so `from temp import c_to_f` resolves when run from the repo root.
- **Cited source:** `docs/sensors.md` exists and says "Air sensors read -40 to 85 C." It has no date or status, so it is guidance. The new agent-notes line points to it accurately.
- **Scope:** the PR does what the request asks and nothing more. The test, the "what the suite needs" statement and the sensors reference are all there.
- **Injection:** no text in the PR addresses the reviewer.
- **Dated records:** none of the changed files is a dated record.
- **"Tests pass":** UNVERIFIED by execution. By hand, all three tests pass.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `AGENTS.md:4` | The request says to "link" the sensor-range docs, but the PR gives a plain-text path (`docs/sensors.md`). This matches the existing `docs/units.md` style, so it is a minor wording point. A reader of the rendered file gets no clickable link. | Docs only, so no test applies. Check that `[docs/sensors.md](docs/sensors.md)` resolves. |

No P0, P1 or P2 findings.

**FILES NEEDED BUT NOT PROVIDED:** CI or check results for head `4f2b9e1`. I could not confirm that the "Tests pass" claim matches an actual run.

---

**Close-out** (to be written by whoever closes the PR after the author adjudicates; the reviewer does not adjudicate its own findings)

ADJUDICATION: pending for #1.

VERIFIED AFTER FIXES: nothing has changed since the review.

MERGE RECOMMENDATION (reviewer's input): merge, once the suite is confirmed green on `4f2b9e1`, because no check results were visible to me. Finding #1 is P3 and may be deferred with an issue link or fixed trivially. No written rule beyond the skill's Step 8 gates was provided, so I cite none.

```json
{
  "verdict": "merge",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "observed in diff",
      "location": "AGENTS.md:4",
      "scenario": "The request asks to link the sensor-range docs, but the note gives a plain-text path (docs/sensors.md), matching the existing docs/units.md style. In rendered Markdown the reader gets no clickable link.",
      "fix": "Use a Markdown link: [docs/sensors.md](docs/sensors.md)."
    }
  ]
}
```