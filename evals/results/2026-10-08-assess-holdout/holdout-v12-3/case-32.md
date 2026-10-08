VERDICT: try. It serves goal 4 (less hand work on the monthly devlog), costs nothing, and uses GitHub, where our code already lives. A one-month trial will show whether labelling issues is less work than writing the section by hand.

WHAT IT IS: Post "Add a known-issues section to a generated devlog", posted 2026-09-30, read from the saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json). I could not open the live URL. The snapshot names no author and states no license for the script.

CLAIMS CHECKED:
- **"A 14-line script."** The snippet has 14 lines, counting the blank line and the wrapped `subprocess.run` call. CONFIRMED. Not load-bearing.
- **"Reads any markdown draft on stdin."** The code calls `sys.stdin.read()` and does not parse the markdown, so any text works. CONFIRMED. Load-bearing.
- **"Appends open issues labelled `known-issue` as a Known issues section."** The code calls `gh issue list --label known-issue --state open --json number,title` and writes `- title (#n)` under `## Known issues`. CONFIRMED. Load-bearing.
  - Caveat: `--limit 50` silently drops any issues past 50.
- **"With no labelled issues it appends 'None.'"** The `else` branch does this. CONFIRMED. Not load-bearing.
- **Sender: "adds a known-issues section to a markdown draft."** Same as the claims above. CONFIRMED. Load-bearing.

FIT:
- **Goal:** goal 4, "Publish the monthly devlog with less hand work."
- **Overlap:** devlog.py already drafts the devlog from merged pull requests. This script adds to it rather than duplicating it.
  - The post's `make_draft.py` stands in for our devlog.py. The pipe works only if devlog.py writes its draft to stdout, and the context file does not say whether it does.
- **Burden:**
  - Someone has to keep the `known-issue` label up to date on GitHub, which is a new routine step.
  - The `gh` CLI must be installed and logged in wherever the devlog is built. That is a token for our existing GitHub account, not a new account.
  - There is no new service.
- **Cost:** free, and $0 against the budget (checked 2026-10-08).
- **Risks:**
  - No license is stated. The constraints allow GPL/AGPL only for tools we run, and this snippet has no license at all. It is 14 trivial lines, so rewriting it inside devlog.py avoids the question.
  - Issue titles get published in a public devlog. If the repo is private, someone should review the titles before publishing.
  - The 50-issue cap truncates silently.
  - Nothing goes to a new third party.
  - Nothing ships in the game.

NEXT ACTION:
- **Action:** For the next monthly devlog, label the current known issues and pipe the devlog.py draft through the script (`python devlog.py | python known_issues.py > devlog.md`).
- **Owner:** operator.
- **Done when:** the published devlog's Known issues section matches `gh issue list --label known-issue` with no hand edits.
- **Stop condition:** stop if keeping labels current takes as much time as writing the section by hand, or if issue titles need rewording before they can go public.
- **Hand-off:** none.

CONFIDENCE: medium. The item is resolved from the snapshot and every load-bearing claim is CONFIRMED by reading the code, with the context file present. Confidence is held back because I don't know whether devlog.py writes to stdout, and the snippet has no stated license.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post", "identity": "posts.example.test/known-issues-in-the-devlog, posted 2026-09-30, author not named, no license stated; read from snapshot captured 2026-10-08", "resolved": true},
  "claims": [
    {"claim": "a 14-line script", "evidence": "snippet in the post counts 14 lines including one blank and the wrapped subprocess call", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "reads any markdown draft on stdin", "evidence": "code: draft = sys.stdin.read(), no parsing", "status": "CONFIRMED"},
    {"claim": "appends open issues labelled known-issue as a Known issues section", "evidence": "code: gh issue list --label known-issue --state open --json number,title --limit 50, appended under ## Known issues (silently capped at 50)", "status": "CONFIRMED"},
    {"claim": "with no labelled issues it appends None.", "evidence": "code: else branch appends '- None.'", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "sender: adds a known-issues section to a markdown draft", "evidence": "same code as above", "status": "CONFIRMED"}
  ],
  "fit": {"goal": "publish the monthly devlog with less hand work (goal 4)",
          "overlap": "devlog.py already drafts the devlog from merged PRs; this adds a section rather than replacing it, assuming devlog.py writes to stdout",
          "burden": "keep a known-issue label current on GitHub; gh CLI installed and logged in with the existing GitHub account",
          "risks": ["no license stated for the snippet; rewrite it inside devlog.py to avoid the question", "issue titles become public in the devlog", "--limit 50 truncates silently", "no new third party; nothing shipped in the game"],
          "cost": {"price": "free", "tier": "none", "limits": "50 issues per run as written", "terms": "no license stated", "checked_at": "2026-10-08"}},
  "next_action": {"action": "For the next monthly devlog, label known issues and run python devlog.py | python known_issues.py > devlog.md",
                  "owner": "operator",
                  "done_when": "the published devlog's Known issues section matches gh issue list --label known-issue with no hand edits",
                  "stop_condition": "stop if keeping labels current costs as much time as writing the section by hand, or if titles need rewording before publishing",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```