# PR Review Report: PR #17

**REVIEWED:** PR #17 "test -40 degrees; agent notes". Head `4f2b9e1`, merge base `a0c3d55`. Both SHAs come from PR.md. I could not check them against a checkout, because I only have the patch and the base files.

**TIER:** Low. The change is one unit test plus a two-line edit to `AGENTS.md`, with no code, auth, secrets, network or data handling. `AGENTS.md` is an instruction file, so I read its change as code for anything aimed at an agent or reviewer (Step 1.4). The new text only says the suite uses the standard library and names `docs/sensors.md`. It tells no one to run, fetch, trust or skip anything, and nothing in it addresses reviewers.

**REVIEWERS:** A fresh Claude instance (Sonnet 5.5) with no part in writing the change, working from the diff and base files only. The author is unknown, since no commit trailers were supplied. I had no tools, so I ran nothing and opened no links.

**What I checked**
- **The test is correct.** `c_to_f(-40)` computes `-40*9/5 + 32`, which is `-360/5 + 32 = -72.0 + 32 = -40.0`. Every intermediate value is exactly representable, so `assertEqual(-40.0, -40)` holds with no float tolerance needed.
- **The patch is consistent with the base.** The hunk headers match the base files (`-6,6` in the tests, `-1,4` in `AGENTS.md`), so it should apply cleanly. The new test sits between the existing two and doesn't disturb them.
- **The "standard library only" claim holds.** The suite imports only `unittest` and the local `temp` module.
- **The cited source exists.** `docs/sensors.md` is in the base and says "Air sensors read -40 to 85 C", so -40 is the sensor's lower bound and a sensible boundary to test. I can't see its date. Its status is guidance (a reference doc, not a spec).
- **The request is covered, with nothing extra.** The test is added, the notes say what the suite needs, and the sensor docs are referenced. The edit leaves the run command and `docs/units.md` reference as they were.
- **The test command works only from the repo root.** `python3 -m unittest discover -s tests` finds `temp` because `-m` puts the current directory on `sys.path`. This is background, not a defect.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `AGENTS.md:4` | The request asked to "link" the sensor docs, but the line gives a plain path (`docs/sensors.md`), not a Markdown link. This matches the existing `docs/units.md` line, so it is consistent, but a renderer won't make it clickable. | Docs-only, so no test applies. Check by rendering the file, or change it to `[docs/sensors.md](docs/sensors.md)`. |
| 2 | P3 (UNVERIFIED claim) | `PR.md` ("Tests pass.") | I can't see the run, and no CI result was provided. By my arithmetic the new test passes, but that isn't an observed result. | Run `python3 -m unittest discover -s tests` from the repo root at `4f2b9e1` and attach the output. |

No P0, P1 or P2 findings.

**FILES NEEDED BUT NOT PROVIDED:** The head checkout at `4f2b9e1` (only the patch and base were given), the CI check status, and the commit trailers.

---

**Close-out** (to be written by the author or whoever closes the PR, not by this reviewer)

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending | |
| 2 | Pending | |

**VERIFIED AFTER FIXES:** None yet. The head has not moved since the review as far as I can tell.

**MERGE RECOMMENDATION:** Merge after confirming a green test run on `4f2b9e1`. The Low-tier round (one independent read) is done, and I found no blocking issue. A missing check is not a green check, so finding 2 should be settled first. No written rule covers this case, so I cite none. Finding 1 is optional polish and shouldn't block.

```json
{
  "verdict": "merge_after_fixes",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "read-only inspection of patch and base",
      "location": "AGENTS.md:4",
      "scenario": "The request asked to link the sensor docs; the line gives a plain path (docs/sensors.md), not a Markdown link, so it won't be clickable when rendered. It matches the existing docs/units.md line, so this is a consistency choice, not a defect.",
      "fix": "Optionally use [docs/sensors.md](docs/sensors.md). Docs-only, so no test applies."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified claim; no execution or CI output available",
      "location": "PR.md (\"Tests pass.\")",
      "scenario": "No test run or CI result was provided. Hand arithmetic shows c_to_f(-40) == -40.0 and assertEqual passes, but the claim is not observed.",
      "fix": "Run python3 -m unittest discover -s tests from the repo root at 4f2b9e1 and attach the output or confirm CI is green."
    }
  ]
}
```