# pr-review report: PR #17 (test -40 degrees; agent notes)

**REVIEWED:** PR #17, head `4f2b9e1`, merge base `a0c3d55`. Both SHAs come from PR.md. I could not verify them against a repository, and no git history was provided. I reviewed the supplied `change.patch` against the files in `base/`.

**TIER:** Low. The change is one test and two lines of agent-notes docs. It touches no auth, permissions, secrets, network exposure or data handling, and no dependency, runtime or TLS changes. The supply-chain and runtime lenses do not apply.

**REVIEWERS:** I am a fresh instance (Sonnet 5.5) with no memory of writing the change. I have no tools, so I could not run the tests or open links. The author is unknown because no commit trailers were provided. Step 3 (data protection) is not at issue: the code carries no personal data, and I am the only reviewer.

**Checks done by reading:**
- **Arithmetic:** `c_to_f(-40)` is `-40*9/5 + 32`, which is `-360/5 + 32`, which is `-72.0 + 32 = -40.0`. Every step is exact in binary floating point, and `assertEqual(-40.0, -40)` passes. The test is correct and not flaky.
- **Request coverage:** the -40 test is present and the notes link the sensor docs. The patch has no extra changes.
- **Standard-library claim (AGENTS.md:3):** the suite imports only `unittest` and `temp`, so the claim holds. The command works from the repo root because `python3 -m` puts the current directory on `sys.path`, which is how `from temp import c_to_f` resolves.
- **Cited source:** `docs/sensors.md` exists and says "Air sensors read -40 to 85 C." It is guidance and has no date. -40 is the documented lower bound, so the test targets the right edge.
- **Document types:** all changed files are living documents, so editing in place is correct.
- **Injection:** no text in the PR addresses the reviewer.
- **Patch integrity:** the hunk headers match their line counts.
- **"Tests pass" (PR.md):** this is an unverified claim. I traced the new test by hand but did not run it, and no CI results were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `AGENTS.md:4` | The request asked to "link" the sensor docs. The note gives a bare path, `docs/sensors.md`, not a Markdown link. In a rendered view the reader cannot click it. The existing `docs/units.md` reference is also a bare path, so this matches local style, but it only partly meets the request. | A docs check that `AGENTS.md` contains `](docs/sensors.md)` and that the target file exists. |
| 2 | P3 | `AGENTS.md:3` | The request asked the notes to say what the suite needs. The note says only "standard library". The suite also needs `python3` and must be run from the repo root. Run with `-s tests` from another directory, `import temp` fails with `ModuleNotFoundError`. An agent following the notes from a subdirectory would see a failure the notes don't explain. | Run the documented command from the repo root and from `tests/`. Only the root run should be documented as supported. |

**FILES NEEDED BUT NOT PROVIDED:** commit trailers or authorship, CI or check results for `4f2b9e1`, and repository access to confirm the SHAs. The base files that the patch touches were all supplied.

## Close-out

Not yet written. The author must adjudicate findings 1 and 2, and a reviewer does not adjudicate its own findings. Both are P3, so each can be fixed or deferred with a tracking issue. Neither blocks merge.

**MERGE RECOMMENDATION (preliminary):** I found no blocker. The change is correct and in scope. Per Step 8, I cannot yet recommend merge outright, for three reasons:
- the two findings have no written decision;
- no expected checks were shown (a missing check is not green), and "Tests pass" is unverified;
- the head SHA is unconfirmed.

Once the author adjudicates both findings and CI is shown green on `4f2b9e1`, this should be mergeable.

```json
{
  "verdict": "no blockers found; merge pending author adjudication of P3 findings and evidence of green CI on 4f2b9e1",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "static-read",
      "location": "AGENTS.md:4",
      "scenario": "Request asked to link the sensor docs; the note gives a bare path docs/sensors.md rather than a Markdown link, so it is not clickable when rendered.",
      "fix": "Use [docs/sensors.md](docs/sensors.md) and add a docs check that the link target exists."
    },
    {
      "severity": "P3",
      "evidence_level": "static-read",
      "location": "AGENTS.md:3",
      "scenario": "Notes say only 'standard library'; the suite also needs python3 and must be run from the repo root. Run with -s tests from another directory, import temp fails with ModuleNotFoundError.",
      "fix": "State 'python3, standard library only, run from the repo root' and verify the command from root and from tests/."
    }
  ]
}
```