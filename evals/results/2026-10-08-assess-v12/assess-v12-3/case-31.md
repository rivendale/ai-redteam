VERDICT: try. The post's idea fits goal 4 and costs nothing, but we already have `changelog.py`, so the useful part is a small borrow into it: group commits by type at build time. Adopting the post's hook-plus-script setup alongside `changelog.py` would add little.

WHAT IT IS: A blog post, "Changelogs from commit trailers, step by step", at posts.example.test, posted 2026-09-17. No author is named. I read it from the saved snapshot captured 2026-10-08 (work/snapshot.md and meta.json), not live. No license is stated for its code.

CLAIMS CHECKED:
- **"A 21-line script reads git log since the last tag."** CONFIRMED. The script in the post is 21 lines, counting blank lines. It runs `git describe --tags --abbrev=0` and then `git log {tag}..HEAD`. Load-bearing.
- **"[It] groups lines by trailer type and writes the markdown."** CONFIRMED, with limits visible in the code:
  - Only `added`, `changed`, `fixed` and `removed` are printed.
  - Any other trailer value, and any commit with no `Change:` trailer, is dropped silently.
  - If the repo has no tags, `git describe` fails because the call uses `check=True`.
  - Load-bearing.
- **"A commit-msg hook adds a `Change:` trailer … so nobody types one."** UNVERIFIED. The hook's code is not in the post. Only one example mapping is given ("Fix the retry" becomes "Change: fixed"), so the full mapping is unknown. The code also suggests a caveat: a local commit-msg hook must be installed on each clone. Commits made in GitHub's web UI, including squash merges, would get no trailer, and the script would then drop them. Not load-bearing, because I recommend skipping the hook (see FIT).
- **"Run on the post's sample repository it prints `## Changes since v0.3.0`, then `### Added` and `### Fixed`."** PROBABLE. The code would print that structure for such commits, but the sample repo is not in the snapshot. Not load-bearing.
- **Sender: "this explains building a changelog from commit trailers."** CONFIRMED. That is what the post covers.

FIT:
- **Goal:** Goal 4, "Ship a weekly changelog without manual work."
- **Overlap:** High. The nightly `changelog.py` already builds a changelog draft from commit messages. What the post adds is grouping by change type, which may cut the manual editing that the word "draft" implies.
- **The hook is not needed:** The trailer is derived only from the subject's first word, so `changelog.py` can make the same classification when it builds the changelog. That avoids per-clone hooks and the web-UI and squash-merge gaps.
- **Weekly vs. tags:** The post works "since the last tag"; our goal is weekly. Use a date range (`--since`) or add weekly tags.
- **Burden:** A small change to an existing script. No new service or account.
- **Cost:** Free. It is a public post with no price or tier, read 2026-10-08.
- **Risks:**
  - The code has no stated license. It is short and generic, so reimplement the idea in our own words rather than pasting it.
  - No data leaves the machine, and there is no telemetry.
  - If our commit subjects don't start with consistent verbs, classification will be poor, and that is the main unknown.

NEXT ACTION: Add first-word classification and Added/Changed/Fixed/Removed grouping to `changelog.py`, with an "Other" section so nothing is dropped. Then run it over the last week of commits.
- **Owner:** the maintainer of `changelog.py`.
- **Done when:** one week's grouped output has been compared with the current draft, and the edits each one needed are noted.
- **Stop condition:** stop if more than about a third of the week's commits land in "Other", or if the grouped draft needs as much hand editing as the current one.
- **Hand-off:** harvest, to borrow the idea from the post.

CONFIDENCE: Medium.
- The item is resolved from a dated snapshot.
- Load-bearing claims are confirmed.
- A context file is present.
- What limits it: I can't see our commit history. Whether our commit subjects classify cleanly by first word decides whether this removes manual work, and only the trial will show that.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Changelogs from commit trailers, step by step\", posts.example.test, posted 2026-09-17, no author named, read from snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "a 21-line script reads git log since the last tag", "evidence": "the full script is in the post: 21 lines; uses git describe --tags and git log tag..HEAD", "status": "CONFIRMED"},
    {"claim": "the script groups lines by trailer type and writes markdown", "evidence": "read the script: groups by Change trailer; prints only added/changed/fixed/removed and silently drops commits without a trailer or with other values", "status": "CONFIRMED"},
    {"claim": "a commit-msg hook adds the Change trailer so nobody types one", "evidence": "hook code not shown; one example mapping only; a local hook does not cover web-UI or squash-merge commits", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "on the sample repository it prints Changes since v0.3.0 with Added and Fixed lists", "evidence": "consistent with the code; sample repository not in the snapshot", "status": "PROBABLE", "load_bearing": false},
    {"claim": "the post explains building a changelog from commit trailers (sender)", "evidence": "the post's text and script", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "Ship a weekly changelog without manual work (goal 4)",
          "overlap": "changelog.py nightly cron already drafts a changelog from commit messages; only grouping by type is new",
          "burden": "small change to the existing changelog.py; no hook needed if classification is done at build time",
          "risks": ["code has no stated license: reimplement rather than copy",
                    "local commit-msg hooks miss web-UI and squash-merge commits",
                    "post works since last tag, not weekly: needs --since or weekly tags",
                    "classification quality depends on consistent first words in our commit subjects"],
          "cost": {"price": "free", "tier": "public post", "limits": "none", "terms": "no license stated for the code",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Add first-word classification and Added/Changed/Fixed/Removed grouping (plus Other) to changelog.py and run it over the last week of commits",
                  "owner": "changelog.py maintainer",
                  "done_when": "one week's grouped output is compared with the current draft and the edits each needed are noted",
                  "stop_condition": "stop if more than about a third of commits land in Other, or the grouped draft needs as much hand editing as the current one",
                  "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```