```
VERDICT: try. A 14-line script that appends open `known-issue` GitHub issues to a markdown draft directly serves goal 4 and extends our existing devlog.py rather than replacing it; check in one devlog cycle that it actually removes hand work.
WHAT IT IS: Post "Add a known-issues section to a generated devlog", posted 2026-09-30, at https://posts.example.test/known-issues-in-the-devlog. Read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. No author named in the snapshot. No license stated for the code.
CLAIMS CHECKED:
  - "A 14-line script": CONFIRMED. The listing is 14 lines including one blank line. Not load-bearing.
  - "Reads any markdown draft on stdin": CONFIRMED. `draft = sys.stdin.read()`, and the draft is treated as opaque text. Load-bearing.
  - "Asks `gh` for the open issues with that label and appends them as a Known issues section": CONFIRMED, with a limit. It runs `gh issue list --label known-issue --state open --json number,title --limit 50` and writes "## Known issues" followed by "- title (#n)" for each issue. Anything past 50 issues is silently dropped, and the post does not mention the cap. Load-bearing.
  - "With no labelled issues it appends 'None.'": CONFIRMED by the `else` branch. Not load-bearing.
  - Sender's framing, "goal 4?": CONFIRMED. Goal 4 is "Publish the monthly devlog with less hand work", and this automates one section.
FIT:
  - Goal: goal 4 (monthly devlog with less hand work).
  - Overlap: devlog.py already drafts the devlog from merged PRs. This script complements it by adding a known-issues section, which devlog.py does not cover as far as the context file says. It is a pipe stage, not a replacement. The post's `python make_draft.py | ...` assumes the drafter writes to stdout. Whether devlog.py does is not stated, and checking that is part of the trial.
  - Burden: the `gh` CLI must be installed and authenticated against our existing GitHub account on whatever machine builds the devlog. Someone has to keep applying a `known-issue` label to issues. That label discipline is the real ongoing cost.
  - Cost: free. No product and no tier.
  - Risks:
    - No license is given for the snippet. It is a tool we run and never ship, and it is trivial enough to rewrite.
    - Data stays with GitHub, where our code already lives, so no new third party is involved.
    - `gh` resolves the repo from the current directory, so it must run inside the right checkout (or the call needs `--repo`).
    - The 50-issue cap truncates silently.
    - `check=True` makes the pipeline fail hard if `gh` is not authenticated.
    - Issue titles are published verbatim, so internal or player-identifying wording in a title would land in the public devlog.
    - It runs on macOS and Windows (Python plus gh).
    - Nothing in the snapshot tries to direct the reader.
NEXT ACTION: Whoever maintains devlog.py adds this as a step (or a function inside devlog.py), labels the current open issues `known-issue`, and generates next month's draft with it. Done when the draft contains a correct Known issues section with no hand editing. Stop if labelling issues takes more effort than writing the section by hand, or if titles regularly need rewording before publication. Hand-off: glean (borrow the code idea from the post).
CONFIDENCE: high. The snapshot is complete and every load-bearing claim is checkable from the code shown. Limits: this was read from a 2026-10-08 snapshot, not live, and whether devlog.py writes to stdout is unknown.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "post 'Add a known-issues section to a generated devlog', posted 2026-09-30, https://posts.example.test/known-issues-in-the-devlog (snapshot captured 2026-10-08; no author named; no code license stated)",
           "resolved": true},
  "claims": [
    {"claim": "the script is 14 lines", "evidence": "counted the listing: 14 lines including one blank", "status": "CONFIRMED",
     "load_bearing": false},
    {"claim": "reads any markdown draft on stdin", "evidence": "draft = sys.stdin.read(); draft treated as opaque text",
     "status": "CONFIRMED"},
    {"claim": "asks gh for open issues labelled known-issue and appends them as a Known issues section",
     "evidence": "gh issue list --label known-issue --state open --json number,title --limit 50; appends '## Known issues' and '- title (#n)' lines; silently capped at 50",
     "status": "CONFIRMED"},
    {"claim": "with no labelled issues it appends 'None.'", "evidence": "else branch appends '- None.'", "status": "CONFIRMED",
     "load_bearing": false},
    {"claim": "it serves goal 4 (sender's question)", "evidence": "context goal 4: publish the monthly devlog with less hand work; script automates one section",
     "status": "CONFIRMED"}
  ],
  "fit": {"goal": "Publish the monthly devlog with less hand work (goal 4)",
          "overlap": "devlog.py already drafts the devlog from merged PRs; this adds a known-issues section as a pipe stage and does not replace it",
          "burden": "gh CLI installed and authenticated with the existing GitHub account; ongoing discipline of labelling issues known-issue",
          "risks": ["no license stated for the snippet (tool, never shipped; trivial to rewrite)",
                    "issue titles published verbatim in a public devlog",
                    "silent truncation at 50 issues",
                    "gh must run inside the right repo checkout or be given --repo",
                    "hard failure if gh is not authenticated (check=True)",
                    "devlog.py may not write to stdout as the post's pipe assumes"],
          "cost": {"price": "free", "tier": "none (code in a blog post)", "limits": "gh issue list capped at 50 in the script",
                   "terms": "no license stated", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Add the known-issues step to the devlog pipeline (or into devlog.py), label current open issues known-issue, and generate next month's draft with it",
                  "owner": "devlog.py maintainer",
                  "done_when": "next month's draft has a correct Known issues section with no hand editing",
                  "stop_condition": "stop if labelling issues costs more effort than writing the section by hand, or titles regularly need rewording before publishing",
                  "handoff": "glean"},
  "confidence": "high",
  "context_file": "present"
}
```