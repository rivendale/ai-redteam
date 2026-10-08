# PR #91 review report

**REVIEWED:** PR #91, "read-only notes and docs servers for the assistant". Head `2b8f4d6`, merge base `8e30c1a`, both as stated in PR.md. I reviewed the provided patch and `work/base/`. I could not check out or verify the SHAs myself because this session has no tools.

**TIER:** High.
- The config is loaded by every developer's coding assistant.
- It decides what the assistant can read and write in the user's notes, which are personal data.
- Its tool descriptions are read by the model as instructions.

The change is small, but it sets access and data handling, so it is High. **This report is round 1 of the 2 that High requires. Round 2 has not run, ideally on a different approved vendor, so the PR is not yet reviewed.**

**REVIEWERS:**
- Reviewer: this instance, Claude Opus 5.5 (`claude-opus-5-5`). It has no memory of writing the change.
- Author: unknown. No commit trailers were provided. Record them from `git log 2b8f4d6` before close-out.
- Data approval (Step 3): the patch carries no note content, only config. Round 2 must still run on an endpoint approved for this repo.

## What checks out

- **`files.js` read-only logic is correct:** `writable = args.includes("--allow-write") && !args.includes("--read-only")` (`base/servers/files.js:4`). The docs entry passes `--read-only` and not `--allow-write`, so `writable` is false.
- **`--root` is parsed correctly.** `--root` is present and followed by `./docs`, so `indexOf` does not return -1 and fall back to `args[0]`.
- **Tool descriptions contain no instructions** beyond describing the tool. This matches the PR's claim and the stakes in context.md.
- **Scope matches the request:** notes search and read, plus docs search, nothing extra in the config.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `agent/mcp.json:5` (`"servers/notes.js"`), `agent/mcp.json:21` (`"servers/files.js", "--root", "./docs"`) | The script paths and the docs root are relative, and there is no `cwd` field, so they resolve against wherever the assistant starts the server. If a developer's assistant starts from a subdirectory or another workspace, one of two things happens. Either both servers fail to start (`Cannot find module servers/notes.js`). Or, if that directory has its own `docs/` and `servers/`, the docs server serves a different folder than intended. That is read access outside the folder the request names, and it would happen on every developer's machine. | Start the assistant with this config from a subdirectory such as `docs/` or `/tmp`. Assert that `search_docs` returns hits only from the repo's `docs/`, or that the config fails loudly. This fails today. Fix: set `cwd` explicitly, or make the paths absolute or resolved by the loader. |
| 2 | P3 | `agent/mcp.json:26-27` (`context_lines`) | The range "0 to 5" appears only in the description prose. The schema is a bare `"integer"`, and `files.js` as shown does no bounds check. A model can pass `context_lines: 10000` or `-1`. A large value returns whole files into context, which is a token cost but stays inside read-only `docs/`. A negative value has undefined slicing behaviour. A limit stated only in model-read prose is not enforced. | Call `search_docs` with `context_lines: 100` and with `-1`. Assert the server either rejects the value or clamps it to 0..5. Also add `minimum: 0, maximum: 5` to the schema, if the loader supports it. |

## FILES NEEDED BUT NOT PROVIDED

- **The loader that reads `agent/mcp.json`.** I need to know whether the `tools` list restricts what is exposed, or only documents it, with the client taking the real list from the server's `tools/list`. If it only documents, any extra tools served by `files.js` or `notes.js` would be exposed even though they are not listed. I also need it to know how relative paths resolve (finding 1).
- **The `notes.js` tool implementation.** The base file only parses `--read-only` into `readOnly`. Nothing shown proves that write, edit or delete tools are withheld or refused when `readOnly` is true. This is the core claim of the PR, and it is unverified.
- **The `files.js` search implementation.** I need to see whether matches stay confined under `root` (symlinks, `..`), and whether `context_lines` is bounded.
- **CI status for head `2b8f4d6`.**

## Close-out

The author adjudicates the findings after the review, and the person who closes the PR writes the close-out. A reviewer never adjudicates its own findings, so this section is left open.

**ADJUDICATION:** pending, for findings 1 and 2.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge (yet).** The following are still open:
- Round 2 of the High tier has not run.
- Findings 1 and 2 have no written decision.
- The `notes.js` read-only enforcement and the loader's tool-exposure semantics are unverified. These are the files listed above.
- Check status for `2b8f4d6` is unknown. A missing check is not a green check.

No P0 or P1 was found in what was provided.

```json
{
  "verdict": "do not merge (yet): High tier, round 2 not run, findings unadjudicated, notes.js read-only enforcement and loader tool-exposure unverified, CI status unknown",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred (loader not provided; relative paths observed in patch)",
      "location": "agent/mcp.json:5, agent/mcp.json:21",
      "scenario": "Script paths and --root ./docs are relative with no cwd set. When a developer's assistant launches from a subdirectory or another workspace, the servers either fail to start or the docs server serves a different docs/ folder than intended.",
      "fix": "Set an explicit cwd, or use loader-resolved or absolute paths. Add a test that launches from a subdirectory and asserts search_docs only returns repo docs/ results or fails loudly."
    },
    {
      "severity": "P3",
      "evidence_level": "observed in patch (bound only in prose); server-side enforcement not shown",
      "location": "agent/mcp.json:26-27",
      "scenario": "context_lines is described as 0 to 5 but typed as a bare integer with no enforced bound. A model passing 10000 gets whole files back; -1 has undefined behaviour.",
      "fix": "Clamp or reject out-of-range values in servers/files.js and add minimum 0 / maximum 5 to the schema. Test with 100 and -1."
    }
  ]
}
```