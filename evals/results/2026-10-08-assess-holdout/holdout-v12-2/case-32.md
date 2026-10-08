VERDICT: try. The post's script directly serves goal 4 by adding a Known issues section that devlog.py does not produce today, and it costs nothing, so run it on one devlog before keeping it.

WHAT IT IS: Post "Add a known-issues section to a generated devlog", posted 2026-09-30, at https://posts.example.test/known-issues-in-the-devlog. I worked from a saved snapshot captured 2026-10-08 (work/snapshot.md and meta.json), not a live read. No author is named in the snapshot, and no license is stated for the code. The post contains no text that tries to direct the reader.

CLAIMS CHECKED:
- **"Reads any markdown draft on stdin, asks `gh` for open issues labelled `known-issue` and appends them as a Known issues section."** CONFIRMED by reading the quoted code. It reads stdin, runs `gh issue list --label known-issue --state open --json number,title`, and writes the draft followed by `## Known issues` and one bullet per issue. *The verdict rests on this claim.*
- **"With no labelled issues it appends 'None.'"** CONFIRMED. The `else` branch appends `- None.`. Not load-bearing.
- **"A 14-line script."** CONFIRMED. The block is 14 physical lines, counting the blank line and the wrapped `subprocess.run` call. Not load-bearing.
- **Unstated limit:** the script uses `--limit 50`, so beyond 50 labelled issues the list is silently cut off. This is a fact read from the code, not a claim the post makes.

FIT:
- **Goal:** goal 4, "Publish the monthly devlog with less hand work". It replaces hand-writing a known-issues list.
- **Overlap:** devlog.py already drafts the devlog from merged PRs. Merged PRs are closed work, and nothing in the context says devlog.py lists open issues, so the script adds to devlog.py rather than duplicating it. It assumes the drafting script writes to stdout (`make_draft.py | known_issues.py`). Whether devlog.py does that is not known from here.
- **Burden:**
  - A `known-issue` labelling habit on GitHub issues.
  - The `gh` CLI installed and authenticated on the machine that builds the devlog.
  - One extra pipe step.
  - There is no new account, because our code is already on GitHub.
- **Cost:** Free, checked 2026-10-08. The post states no license.
- **Risks:**
  - The issue titles get published in a public devlog. If the repo is private, the titles must be fit for the public.
  - Titles copied from player reports could carry player details, so check before publishing.
  - No license is stated. That is minor for a tool we run and never ship, and the 14 lines are easy to rewrite in devlog.py instead.
  - The silent cap at 50 issues.
  - No network calls other than `gh`, and no telemetry in the code.

NEXT ACTION: Whoever maintains devlog.py does three things:
1. Label the current open issues that players should know about with `known-issue`.
2. Add the step to the pipeline, either as a pipe after devlog.py or folded into devlog.py.
3. Generate the next monthly devlog with it.

- **Done when:** that devlog is published with a generated Known issues section that needed no hand edits.
- **Stop if** devlog.py cannot produce its draft on stdout without more than a trivial change, or if the labelled titles need rewriting by hand before they can be published.
- **Hand-off:** `glean` (borrowing a code snippet).

CONFIDENCE: High. The snapshot is readable, every load-bearing claim is CONFIRMED by the code itself, and the context file is present. Two limits: it is a saved copy, not a live read, and devlog.py's output interface is unknown. That second point affects the effort, not the verdict.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post", "identity": "post 'Add a known-issues section to a generated devlog', posted 2026-09-30, https://posts.example.test/known-issues-in-the-devlog (saved snapshot captured 2026-10-08; no author or code license stated)",
           "resolved": true},
  "claims": [
    {"claim": "reads any markdown draft on stdin, asks gh for open issues labelled known-issue and appends them as a Known issues section",
     "evidence": "read the quoted script: stdin read, gh issue list --label known-issue --state open, appends '## Known issues' with one bullet per issue",
     "status": "CONFIRMED"},
    {"claim": "with no labelled issues it appends 'None.'", "evidence": "else branch appends '- None.'",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "a 14-line script", "evidence": "counted the code block: 14 physical lines",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "publish the monthly devlog with less hand work (goal 4)",
          "overlap": "devlog.py drafts the devlog from merged PRs; nothing stated about it listing open issues, so this extends it rather than duplicating it",
          "burden": "a known-issue labelling habit, gh CLI installed and authenticated on the devlog machine, one pipe step; no new account (code already on GitHub)",
          "risks": ["issue titles become public in the devlog; check private-repo titles and any player details before publishing",
                    "no license stated for the snippet; acceptable for an internal tool, or rewrite the 14 lines in devlog.py",
                    "--limit 50 silently truncates longer lists",
                    "assumes the draft script writes to stdout; devlog.py's interface unknown"],
          "cost": {"price": "free", "tier": "none (code in a blog post)", "limits": "none", "terms": "no license stated",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Label current player-facing open issues known-issue, add the step after devlog.py (pipe or fold in), and generate the next monthly devlog with it",
                  "owner": "devlog.py maintainer", "done_when": "one monthly devlog is published with a generated Known issues section needing no hand edits",
                  "stop_condition": "stop if devlog.py needs more than a trivial change to emit its draft on stdout, or if the labelled titles must be hand-rewritten before publishing",
                  "handoff": "glean"},
  "confidence": "high",
  "context_file": "present"
}
```