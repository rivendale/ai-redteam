VERDICT: try. The post serves goal 4, but our nightly `changelog.py` already builds a changelog draft from commit messages, so the only thing it might add is grouping entries by change type; check whether we lack that before borrowing anything.

WHAT IT IS: Post "Changelogs from commit trailers, step by step", posted 2026-09-17, at https://posts.example.test/changelog-from-trailers. Read from a saved snapshot captured 2026-10-08, not live. No author or code license is stated. The post contains no text that tries to direct the reader.

CLAIMS CHECKED:
- **Sender: "this explains building a changelog from commit trailers".** CONFIRMED. The post gives the full approach and the script.
- **"A commit-msg hook adds a `Change:` trailer from the first word of the subject".** UNVERIFIED. The hook's code is not in the post. Only one example mapping is given (`Fix` → `fixed`), and nothing says how words like "Update" or "Refactor" are mapped. The verdict rests on this claim.
- **"…so nobody types one" (inference from the hook).** PROBABLE, with limits.
  - A commit-msg hook is client-side and has to be installed in every clone.
  - It does not run for commits made on GitHub, such as web edits or squash-merge messages.
  - The script skips commits that have no trailer (`continue`), so those commits drop out silently.
  - The verdict rests on this claim.
- **"A 21-line script".** CONFIRMED. The script shown is 21 lines, counting blank lines.
- **"Reads `git log` since the last tag, groups by trailer type, writes markdown".** CONFIRMED by reading the code: `git describe --tags --abbrev=0`, then `tag..HEAD`, then a `defaultdict` keyed by the trailer value. Two caveats from the code:
  - Only `added`, `changed`, `fixed` and `removed` are written. Any other trailer value is dropped.
  - The script raises an error if the repo has no tag (`check=True` on `git describe`).
  - Its window is "since the last tag", not "this week". A weekly changelog would need weekly tags or a `--since` change.
- **"On the sample repo it prints `## Changes since v0.3.0` with Added and Fixed lists".** PROBABLE. The format matches the code, but the sample repo is not in the snapshot. Not load-bearing.

FIT:
- **Goal:** goal 4, "Ship a weekly changelog without manual work".
- **Overlap:** strong. `changelog.py` (nightly cron) already builds a changelog draft from commit messages. The post's genuinely new part is the Added/Changed/Fixed/Removed grouping. That grouping could be done when the log is read, by classifying each subject's first word inside `changelog.py`. That would need no hook and no trailers, and would cover commits made on GitHub.
- **Burden:**
  - With the hook: a hook to install in every clone, plus a classification table to maintain.
  - Without it: a few lines in an existing script.
- **Cost:** free, read 2026-10-08. No license is stated for the code, so do not vendor it verbatim. A rewrite is trivial.
- **Risks:**
  - Silent omissions from commits that have no trailer.
  - The script fails on a repo with no tags.
  - No data leaves the machine, and nothing new is installed.

NEXT ACTION:
- **Action:** The operator reads `changelog.py` and last week's draft to see whether entries are already grouped by type, and what manual step remains before shipping.
- **Done when:** we know whether grouping is missing and whether it is the manual step.
- **Stop condition:** stop if `changelog.py` already groups entries, or if the manual work is something else (for example, editing wording or publishing). In either case, skip the post.
- **Hand-off:** if grouping is missing, `harvest` the first-word classification idea from the post into `changelog.py`, done at read time rather than through a hook.

CONFIDENCE: medium. Three things limit it:
- I worked from a saved snapshot, not a live read.
- The hook's code is not shown.
- The context file does not say what `changelog.py` already does, or what manual step goal 4 is still waiting on.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Changelogs from commit trailers, step by step\", posted 2026-09-17, https://posts.example.test/changelog-from-trailers (snapshot captured 2026-10-08; no author or code license stated)",
           "resolved": true},
  "claims": [
    {"claim": "the post explains building a changelog from commit trailers (sender's words)",
     "evidence": "snapshot gives the approach and the full script", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "a commit-msg hook adds a Change: trailer from the first word of the subject",
     "evidence": "described with one example (Fix -> fixed); the hook code and the full word mapping are not in the post",
     "status": "UNVERIFIED"},
    {"claim": "so nobody types a trailer",
     "evidence": "follows only where the client-side hook is installed; it does not run on commits made on GitHub, and the script drops trailerless commits",
     "status": "PROBABLE"},
    {"claim": "the script is 21 lines", "evidence": "counted the script in the snapshot: 21 lines including blanks",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "the script reads git log since the last tag, groups by trailer type and writes markdown",
     "evidence": "read the code: git describe --tags then tag..HEAD, defaultdict grouping; only added/changed/fixed/removed are written; it errors with no tags",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "on the sample repo it prints '## Changes since v0.3.0' with Added and Fixed lists",
     "evidence": "the output format matches the code; the sample repo is not in the snapshot",
     "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "ship a weekly changelog without manual work (goal 4)",
          "overlap": "changelog.py (nightly cron) already builds a changelog draft from commit messages; only by-type grouping may be new",
          "burden": "hook in every clone plus a word-mapping table, or a few lines added to changelog.py if the subject is classified at read time",
          "risks": ["commits without a trailer (e.g. GitHub web or squash commits) silently dropped",
                    "script errors on a repo with no tags; its window is since-last-tag, not weekly",
                    "no license stated for the code: do not vendor it verbatim"],
          "cost": {"price": "free", "tier": "blog post", "limits": "none",
                   "terms": "no license stated for the code", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Read changelog.py and last week's draft to see whether entries are grouped by type and what manual step remains",
                  "owner": "operator",
                  "done_when": "we know whether grouping is missing and whether it is the manual step",
                  "stop_condition": "stop and skip the post if changelog.py already groups entries or the manual work is something else",
                  "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```