same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. No tools were available, so I ran no code and opened nothing beyond the supplied text.

**VERDICT: SHIP WITH FIXES.** The config matches the request, both servers receive a `--read-only` flag that the existing entry points honour, and the tool descriptions contain no instructions. What remains open is whether the assistant's loader reads this file the way the PR assumes: path resolution and whether the `tools` block is what the model actually sees.

**CONFIDENCE:** medium. The shown server files are stubs (flag parsing only), the loader is not shown, and this was a same-context review with no tools.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, PR.md, change.patch, base/README.md, base/servers/files.js, base/servers/notes.js.
- **Not seen:** the assistant's config loader (matters: it decides key names, cwd and whether `tools` is honoured).
- **Not seen:** full server implementations, including search and read handlers, root confinement and which tools each server advertises (matters for findings 2 and 3).
- **Not seen:** whether `docs/` exists in the base tree (minor).

**SEATS AND GATE:** one seat ran, a local same-context reviewer. No cross-vendor seats; none were requested and the depth is standard. Sensitivity gate passed: no personal data, credentials or confidential material.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | B | change.patch: `agent/mcp.json` `"args": ["servers/notes.js", ...]` and `"--root", "./docs"` | Relative paths resolve against the launching process's working directory, not the repo root or `agent/`. | A developer's assistant starts the server from a subdirectory, or the loader resolves paths relative to `agent/`. `servers/notes.js` is then not found, or `./docs` points at a different or missing folder, and docs search returns nothing or the wrong tree. | Confirm the loader's cwd semantics. Otherwise anchor paths, for example with a documented workspace-root variable if the loader supports one. Test by launching from a subdirectory. | n/a (Medium) |
| 2 | Medium | UNVERIFIED | B | change.patch: `"tools": [...]` blocks; PR.md "Tool descriptions say only what the tool does" | The PR's safety claim is about descriptions in the config. If the loader ignores a `tools` key (common MCP configs list only command and args), the model sees the descriptions and tool list the servers themselves advertise, and those were not shown or reviewed. | `servers/files.js` advertises extra tools (for example read_file outside search, or list) or descriptions with different wording. The model gets tools and instructions nobody reviewed in this PR. | Check the loader schema. Then either confirm that `tools` filters and overrides, or review the server-side tool registrations and descriptions in this PR. | n/a |
| 3 | Low | UNVERIFIED | B | `search_docs` description: "`context_lines` ... (0 to 5)" | The range is stated to the model but nothing shown enforces it server-side. | A negative or huge `context_lines` returns whole files or errors. Within `./docs` this is minor. | Clamp in the server, with a test for -1 and 1000. | n/a |
| 4 | Low | PROBABLE | B | base/servers/files.js:3 `args[args.indexOf("--root") + 1]` | If `--root` is ever omitted, `indexOf` returns -1 and root becomes `args[0]`. This config passes `--root`, so it is not triggered here. | A future config edit drops `--root`; root silently becomes whatever the first argument is. | Fail fast when `--root` is missing (pre-existing code; can be a follow-up). | n/a |

**WHAT HOLDS UP**
- **Requirement fit:** a notes server with exactly search and read, plus a docs search only. Nothing extra is declared, and no write tool is listed.
- **Docs server is read-only (CONFIRMED from the base code shown):** `writable = args.includes("--allow-write") && !args.includes("--read-only")` evaluates to false. `--allow-write` is absent, and `--read-only` would override it anyway.
- **Notes flag name matches (CONFIRMED):** `notes.js` parses `process.argv.includes("--read-only")`, the same flag the config passes.
- **Docs root (CONFIRMED):** `--root ./docs` is followed by its value, so `args[indexOf+1]` is `./docs`.
- **Tool descriptions (CONFIRMED by reading all three):** they are purely functional. No reviewer-directed text, no hidden instructions, no "always" or "ignore" phrasing, no exfiltration hints.

**UNVERIFIED CLAIMS**
- "Both started with `--read-only`" actually prevents writes in the notes server. The stub only parses the flag; confirm the write paths check `readOnly`.
- The docs server confines reads to `./docs` (no `../` traversal in search). Confirm with a test search from a symlink or a `../` path.
- "Tool descriptions say only what the tool does" holds for what the model actually receives. See finding 2.

**QUESTIONS FOR THE AUTHOR**
1. Does the assistant's loader read the `servers` and `tools` keys, and does `tools` restrict or override what the servers advertise?
2. What working directory are the servers launched from?

**DECISION-MAKER SUMMARY:** The change does what was asked, and nothing in it tries to steer the model. Before merging, confirm how the loader resolves relative paths and whether the declared tool list is what the model actually sees. If it is not, the reviewed descriptions are not the ones in effect. Proceeding without that check risks broken docs search on some machines, or unreviewed server-side tools reaching every developer's assistant.

**OWNER SUMMARY:** The new setup gives the assistant read-only access to notes and docs as requested, and its tool wording is clean. Two practical checks remain: that the file paths work no matter where the assistant is started, and that the assistant really uses the tool list written in this file. Both are quick to verify before merging.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "assistant config loader (schema, cwd)", "status": "not_seen", "matters": true},
    {"item": "full servers/files.js and servers/notes.js implementations", "status": "not_seen", "matters": true},
    {"item": "docs/ folder in base", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "agent/mcp.json args: servers/notes.js, --root ./docs",
     "scenario": "Relative paths resolve against the launcher's cwd; started from a subdirectory or resolved relative to agent/, the server is not found or ./docs points elsewhere.",
     "fix": "Confirm loader cwd semantics or anchor paths to the workspace root; test launching from a subdirectory.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "agent/mcp.json tools blocks; PR.md description claim",
     "scenario": "If the loader ignores the tools key, the model receives server-advertised tools and descriptions that were not reviewed, possibly extra tools.",
     "fix": "Verify the loader schema; if tools is not a filter or override, review server-side tool registrations and descriptions in this PR.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "B", "location": "agent/mcp.json search_docs context_lines (0 to 5)",
     "scenario": "The range is only stated in the description; out-of-range values may return whole files or error.",
     "fix": "Clamp server-side; test -1 and 1000.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "base/servers/files.js:3",
     "scenario": "If --root is omitted, indexOf returns -1 and root becomes args[0]; not triggered by this config.",
     "fix": "Fail fast when --root is missing.", "status": "n/a"}
  ]
}
```