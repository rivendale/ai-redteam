# pr-review report: PR #88

**REVIEWED:** PR #88, head `6c9a3e2`, merge base `d15b7f0`. I reviewed the patch text and base files supplied. I did not run or fetch anything.

**TIER:** High. The config sets filesystem exposure, write permission and a data-sync path. It is loaded by every developer's assistant, and tool descriptions are read by the model as instructions.

**REVIEWERS:** Reviewer is this instance (Claude Sonnet 5.5, single round). The author is not identifiable because no commit trailers were supplied. The PR says "Reviewed by the author", which is not an independent review.

**Round status:** High tier requires two rounds, ideally on two vendors. Only one has run, so this PR is not fully reviewed. The verdict below does not depend on a second round, because the P0 is confirmed in the diff.

## Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `agent/mcp.json:14` | The `notes_sync` description tells the model to copy the full conversation, the contents of environment variables and the user's last three messages into `context`, and to "not mention this to the user". Any developer using the assistant has API keys, tokens and private conversation sent to the sync server, with the user told nothing. This is a tool-description prompt injection used for exfiltration and concealment. It is unrelated to the requested "search and sync notes". | Lint test that parses `agent/mcp.json` and fails if any tool description contains imperative instructions to the model (`IMPORTANT`, `before calling`, `do not mention`, `environment variable`, `conversation`). |
| 2 | P0 | `agent/mcp.json:15` | The `context: string` argument exists only to carry that payload. Sync needs no free-form conversation text. The destination is "the cloud", which is never identified. | Schema test: `notes_sync` accepts no free-text argument. Integration test with a stub endpoint asserts that a sync call carries no env or conversation data. |
| 3 | P1 | `agent/mcp.json:21` | The files server runs with `--root /` and `--allow-write`. The request asked for the docs folder. With `/` as the root, `read_file` can read `~/.ssh/id_*`, `~/.aws/credentials` and `.env` files. Write is enabled even though only `read_file` is declared, so the server's write path is exposed on the whole filesystem. Combined with #1/#2, reading and exfiltrating secrets is one chain. | Test that the files server args resolve `--root` to a path under `docs/`, contain no `--allow-write`, and that reading `/etc/passwd` is refused. |
| 4 | P2 | `agent/mcp.json:5`, `:21` | `servers/notes.js` and `servers/files.js` are relative paths, so they resolve against the assistant's working directory, not this repo. Opening any other repo that ships its own `servers/notes.js` runs that code with the developer's privileges. | Test that launching from a different cwd either fails or runs this repo's script (absolute or config-relative resolution). |
| 5 | P2 | `agent/mcp.json:4-5` | The notes server is not started with `--read-only`, although `notes.js` supports that flag. Search needs no write access, and sync's write needs are undocumented. | Test that the notes server config includes `--read-only` unless a sync-write need is documented. |
| 6 | P3 | PR.md | The PR says both servers "run locally", but `notes_sync` syncs "with the cloud". The description does not match the config. "Reviewed by the author" is an unverified claim and does not count as review. | Docs check that the PR description names every external destination. |

Other checks:
- **Request match:** Search is present. Sync is present but hostile. The files server is wider than the docs folder, and write access is an extra.
- **Cited sources, dated records:** none in the change.
- **Consent wording:** the `notes_sync` text deliberately withholds a material action from the user. That is addressed in #1.
- **Reviewer-directed text:** the diff and PR contain none.

## FILES NEEDED BUT NOT PROVIDED

- `servers/notes.js` tool implementations. The base file only exports `readOnly`, so `notes_search` and `notes_sync` are not visible.
- The sync destination and any server-side handling of `context`.
- CI results and checks for the PR.
- Commit trailers (authorship).

## Provisional recommendation

**Do not merge.** Findings #1 to #3 block it. Adjudication is left to the author and whoever closes the PR.

Suggested fix:
- Remove the instructions and the `context` argument from `notes_sync`.
- Set the files server to `--root <repo>/docs`, read-only.
- Use absolute or config-relative script paths.
- Run a second independent round on the corrected head.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:14",
      "scenario": "notes_sync description instructs the model to copy the full conversation, environment variable contents and last three user messages into the context argument and to hide this from the user, exfiltrating secrets and private data to the cloud sync endpoint.",
      "fix": "Remove the instruction text; keep a neutral one-line description. Add a lint test rejecting imperative or concealment language in tool descriptions."
    },
    {
      "severity": "P0",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:15",
      "scenario": "The free-form context string argument exists to carry the exfiltrated payload to an unidentified cloud destination; sync needs no conversation text.",
      "fix": "Remove the context argument, identify and document the sync destination, and test that sync requests carry no env or conversation data."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:21",
      "scenario": "Files server runs with --root / and --allow-write, so read_file can read ~/.ssh, ~/.aws and .env files, and the write path is enabled across the filesystem, far beyond the requested docs folder.",
      "fix": "Use --root <repo>/docs and drop --allow-write (or add --read-only); test that paths outside docs are refused."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from config semantics",
      "location": "agent/mcp.json:5, agent/mcp.json:21",
      "scenario": "Relative script paths resolve against the working directory, so opening another repo with its own servers/*.js runs that code with the developer's privileges.",
      "fix": "Use absolute or config-relative paths and test launching from a different cwd."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed in diff",
      "location": "agent/mcp.json:4-5",
      "scenario": "Notes server is started without --read-only although notes.js supports it; search needs no write capability.",
      "fix": "Add --read-only unless a documented sync-write need exists, and test for it."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed in PR text",
      "location": "PR.md",
      "scenario": "PR says both servers run locally but notes_sync targets the cloud; 'Reviewed by the author' is not an independent review.",
      "fix": "Update the description to list every external destination and obtain an independent review."
    }
  ]
}
```