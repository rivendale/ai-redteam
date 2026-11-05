# Review report: PR #17 (test -40 degrees; agent notes)

**REVIEWED:** PR #17, head `4f2b9e1`, merge base `a0c3d55`. Both SHAs come from PR.md. I could not check them against a repository, because only the patch and base files were provided. I reviewed the patch against `work/base/`, not a checkout.

**TIER:** Low. The change is one added unit test plus a wording change in agent notes. It touches no auth, permissions, secrets, network exposure or data handling. The dashboard is internal and the code carries no personal data. One independent read is the whole requirement.

**REVIEWERS:** This is a fresh instance (Claude Sonnet 5.5) with no part in writing the change. The commit trailers were not provided, so who wrote the change is **unknown**. I had no tools, so I did not run anything and the session started outside any checkout. `AGENTS.md` is an instruction file, so I read its change as code. The added text only says the suite uses the standard library and points to `docs/sensors.md`. It tells an agent nothing to run, fetch, trust or skip, and nothing in it addresses a reviewer.

**Checks done**
- **The new test is correct.** `c_to_f(-40)` is `-40*9/5+32`, which is `-360/5 = -72.0`, then `+32 = -40.0`. Every step is exact in floating point, and `assertEqual(-40.0, -40)` passes. This is a hand computation. "Tests pass" in the PR is an unverified claim.
- **The patch applies.** The hunk headers match the base files: `@@ -6,6 +6,9 @@` for the test file and `@@ -1,4 +1,4 @@` for AGENTS.md.
- **The PR description is accurate.** −40 is where °C and °F meet. It is also the lower bound in `docs/sensors.md` ("Air sensors read -40 to 85 C"), so the test covers the sensor floor. That doc is undated living guidance, not a binding spec, and I opened it.
- **"Standard library only" holds.** The tests import only `unittest` and `temp`, and `temp.py` has no imports.
- **Scope matches the request.** The PR contains the −40 test, the "what the suite needs" note and the sensor-docs reference, and nothing extra.
- **File types.** `AGENTS.md`, `docs/sensors.md` and `docs/units.md` are living documents, so editing in place is correct. Nothing in the PR is a dated record.
- **No consent or user-facing wording** changed.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `AGENTS.md:3` (patched) | The request asked the notes to say what the suite *needs*. "Only the standard library" is true but incomplete. `from temp import c_to_f` resolves only because `python3 -m unittest` puts the current directory on `sys.path`, and `temp.py` is in the repo root. An agent that follows the notes from `tests/` or another directory gets `ModuleNotFoundError: temp`. | A doc check, or a CI step that runs the documented command from the repo root. Alternatively, state "run from the repository root" in the notes and run the suite from a subdirectory to confirm the failure. |
| 2 | P3 | `AGENTS.md:4` (patched) | The request said to *link* the sensor docs. The PR adds a bare path (`docs/sensors.md`), not a Markdown link, so it does not render clickable. This matches the existing `docs/units.md` style, so it may be intended. | Optional link check that the target resolves, e.g. `[sensor ranges](docs/sensors.md)`. |

**FILES NEEDED BUT NOT PROVIDED:** commit trailers (authorship) and CI or check results at `4f2b9e1`. The checkout itself was also not provided, only the base files and the patch.

**Close-out:** to be written by the author or the person closing the PR. I do not adjudicate my own findings.

**MERGE RECOMMENDATION (for the closer):** Merge. The change is correct, small and in scope, and neither finding is a blocker. Both P3s can be fixed in this PR or deferred with an issue link. Step 8 requires every expected check to be present and green, and I saw no check results. Confirm CI is green at head `4f2b9e1` before merging. No written rule or pending owner decision applies here.

```json
{
  "verdict": "merge",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "read-and-reasoned (not executed)",
      "location": "AGENTS.md:3 (patched)",
      "scenario": "Notes say the suite needs only the standard library but omit that it must run from the repo root. 'from temp import c_to_f' only resolves via cwd on sys.path under 'python3 -m unittest', so running from tests/ or elsewhere raises ModuleNotFoundError: temp.",
      "fix": "Add 'run from the repository root' to the notes, and/or run the documented command in CI from the repo root."
    },
    {
      "severity": "P3",
      "evidence_level": "read",
      "location": "AGENTS.md:4 (patched)",
      "scenario": "Request asked to 'link' the sensor docs; the PR adds a plain-text path, not a Markdown hyperlink, so it is not clickable. Consistent with the existing docs/units.md style, so possibly intended.",
      "fix": "Use [sensor ranges](docs/sensors.md) if a real link is wanted."
    }
  ]
}
```