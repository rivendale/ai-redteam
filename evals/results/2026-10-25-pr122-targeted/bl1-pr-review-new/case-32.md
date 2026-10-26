# PR #91 review: read-only notes and docs servers

**Review report**

**REVIEWED:** PR #91, head `2b8f4d6`, merge base `8e30c1a`. Both SHAs come from PR.md and are short SHAs. I had no tools, so I could not check out the head. I reviewed `change.patch` against `base/` as provided. I have not confirmed that the patch is the exact content of `2b8f4d6`.

**TIER:** High.
- The config sets permissions: it decides which tools every developer's assistant gets and whether they can write.
- It sets data scope: the user's notes, which may hold personal data, and a filesystem root.
- Its tool descriptions are read by the model as instructions.
- Step 2 places "authentication and permissions… (including their configuration)" and "personal data" in High. When unsure, take the higher tier.

**REVIEWERS:**
- Round 1: this instance (Claude Opus 5.5, `claude-opus-5-5`). It is a separate session that did not write or help write the change.
- Round 2: **not run.** Step 2 says "a High-tier PR whose second round has not run is not reviewed". Round 2 should ideally use a second vendor on an endpoint approved for notes data (Step 3).
- Author: unknown. No commit trailers were provided.

**Data handling (Step 3):** No code was sent anywhere. This round ran in-session with no tools.

**Request check:**
- The notes server exposes only search and read, and is started with `--read-only` (`agent/mcp.json:5`).
- The docs server exposes search only, with `--read-only` and `--root ./docs` (`agent/mcp.json:21`).
- Nothing beyond the request was added.
- PR.md claims the "tool descriptions say only what the tool does". I read all three descriptions: none addresses the reviewer or instructs the model beyond describing the tool. The claim holds.

**Read-only verification:**
- **Docs server:** confirmed at the flag level. In `base/servers/files.js:4`, `writable = args.includes("--allow-write") && !args.includes("--read-only")`. The config passes `--read-only` and not `--allow-write`, so `writable` is false.
- **Notes server:** not confirmed. `base/servers/notes.js:2` only parses `readOnly`. I cannot see any code that gates write tools on it. This is listed as a coverage gap below, not a finding.

**Other checks:**
- No dependency, runtime or TLS change, so the supply-chain and TLS lenses do not apply.
- No sources are cited.
- `agent/mcp.json` is a living document, not a dated record.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `agent/mcp.json:5`, `agent/mcp.json:21` | `servers/notes.js`, `servers/files.js` and `--root ./docs` are relative paths. `files.js:3` uses the root string as given, so it resolves against whatever working directory the assistant launches from. A developer whose assistant starts in `agent/` or in another project gets one of two failures: the servers do not start (module not found), or `./docs` resolves to *that* directory's `docs/`, exposing an unintended folder to search. Base as provided also contains no `docs/` directory. (Inferred: the client's cwd behaviour was not provided.) | Launch the config with cwd set to `agent/` and to an unrelated temp directory. Assert that both servers start and that the docs root resolves to `<repo>/docs`. This fails today. |
| 2 | P3 | `agent/mcp.json:25-26` | The "0 to 5" bound on `context_lines` exists only in the description prose. The schema is a bare `"integer"`, and no enforcement is visible in `files.js`. If the model passes `500` or `-1`, the result is unbounded output or undefined behaviour. Impact is low because the whole docs folder is readable anyway. (Inferred: the search implementation was not provided.) | Call `search_docs` with `context_lines: 50` and `-1`. Assert rejection or clamping to 0–5. Fix: add `minimum: 0, maximum: 5` to the schema and clamp server-side. |

**FILES NEEDED BUT NOT PROVIDED:**
- **`servers/notes.js` tool implementation.** Needed to see whether `readOnly` actually removes or blocks every write or delete tool. Without it, "read-only notes" is an unverified claim.
- **`servers/files.js` search implementation.** Needed to confirm:
  - that a `search_docs` tool exists with `phrase`/`context_lines`;
  - that results are contained under `--root`, including symlinks;
  - which tools the server advertises.
- **The assistant/MCP client loader.** Needed to know:
  - whether the `"tools"` arrays in `mcp.json` restrict and override what the server advertises, or are ignored, in which case the server's own tool list and descriptions are what the model sees;
  - which working directory the client uses for `command`/`args`.
- **Whether a `docs/` folder is meant to exist in the repo.** It is absent from `base/`.
- **Commit trailers and CI check results for `2b8f4d6`.**
- **A checkout of `2b8f4d6`** to confirm it matches `change.patch`.

---

**Close-out** (not completed: the reviewer does not adjudicate its own findings)

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (author) | — |
| 2 | Pending (author) | — |

**VERIFIED AFTER FIXES:** None. No fixes have been made yet.

**MERGE RECOMMENDATION: do not merge yet.** The evidence so far shows no P0 or P1. Merge is blocked because the review is incomplete:
- Step 2: "a High-tier PR whose second round has not run is not reviewed." Round 2 has not run.
- Step 8: "every round the tier requires has run, and every finding has a written decision". Neither holds: round 2 is missing and findings 1–2 are unadjudicated.
- Step 8: "every expected check is present and green (a missing check is not green…)". No CI results were provided.

The notes server's read-only enforcement (`notes.js`) and the client's tool-list semantics are open coverage gaps. Round 2 should be given those files.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred",
      "location": "agent/mcp.json:5, agent/mcp.json:21",
      "scenario": "Relative server paths and --root ./docs resolve against the assistant's launch cwd (files.js:3 uses the root string unresolved); from any cwd other than repo root the servers fail to start or ./docs points at another project's docs folder, exposing it to search. base/ contains no docs/ directory.",
      "fix": "Resolve paths relative to the config file or repo root (e.g. resolve --root against __dirname in files.js, or use the client's config-relative path variable); add a launch test from a non-root cwd."
    },
    {
      "severity": "P3",
      "evidence_level": "inferred",
      "location": "agent/mcp.json:25-26",
      "scenario": "context_lines bound 0-5 is stated only in description prose; schema is bare integer and no enforcement is visible, so values like 500 or -1 give unbounded output or undefined behaviour.",
      "fix": "Add minimum 0 / maximum 5 to the arg schema and clamp or reject server-side; test with 50 and -1."
    }
  ]
}
```