```
VERDICT: skip. It serves none of our four goals, and its GPL-3.0 license breaks the rule that code shipped on the show site must be MIT, Apache-2.0 or BSD.
WHAT IT IS: example-org/chapter-player (repo, default branch main; no commit sha in the snapshot), a Hugo
  shortcode. License GPL-3.0, 300 stars, last push 2026-09-14, not archived. Read from the saved snapshot and
  meta.json captured 2026-10-09, not live.
CLAIMS CHECKED:
  - "Adds a play button and a clickable chapter list to an episode page" (sender and README): PROBABLE. The README
    says so, but the snapshot holds no source code to confirm it. Not load-bearing.
  - "No tracking; no dependencies" (README): UNVERIFIED. It is only stated; no code in the snapshot settles it.
    Not load-bearing.
  - "License GPL-3.0; anything that includes this shortcode must itself be released under the GPL" (README and
    meta.json): CONFIRMED by both sources. Load-bearing: shipping it would put GPL code into our site theme, which
    our license rule forbids.
FIT:
  - Goal: none found. Our goals are editing time, newsletter signups, transcripts and loudness. An on-page chapter
    player serves none of them.
  - Overlap: none found in the context file.
  - Burden: one shortcode plus a chapter list to maintain per episode in the Hugo site.
  - Cost: free (open source), as read in the snapshot dated 2026-10-09.
  - Risks: GPL-3.0 on site code violates the constraint "GPL or AGPL only for tools we run on our own machines". It
    would also oblige us to release the site under the GPL. The no-tracking claim is unchecked.
NEXT ACTION: Reply to the sender: not adding it, because it serves no current goal and is GPL-3.0, which our site
  license rule forbids. If an episode-page chapter player becomes a goal, look for an MIT, Apache-2.0 or BSD
  alternative. Owner: operator. Done when the sender has the answer. Hand-off: none.
CONFIDENCE: high. The item is resolved from a dated snapshot, the claim the verdict rests on (the license) is
  CONFIRMED, and a context file is present. The only limit is that this is a saved copy from 2026-10-09, not a live
  read.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/chapter-player (default branch main, no sha in snapshot; GPL-3.0, 300 stars, last push 2026-09-14, not archived; snapshot 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "adds a play button and a clickable chapter list to an episode page",
     "evidence": "README in snapshot; no source code captured", "status": "PROBABLE", "load_bearing": false},
    {"claim": "no tracking; no dependencies",
     "evidence": "README statement only; no code in snapshot to check", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "license is GPL-3.0 and anything including the shortcode must be released under the GPL",
     "evidence": "meta.json license field and README license line", "status": "CONFIRMED"}
  ],
  "fit": {"goal": "none found",
          "overlap": "none found in the context file",
          "burden": "one shortcode plus per-episode chapter data in the Hugo site",
          "risks": ["GPL-3.0 on site code violates the rule that site code must be MIT, Apache-2.0 or BSD",
                    "copyleft would oblige releasing the site under the GPL",
                    "the no-tracking claim is unverified"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "GPL-3.0",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Tell the sender it will not be added: it serves no current goal and its GPL-3.0 license is not allowed for site code; if a chapter player becomes a goal, look for an MIT, Apache-2.0 or BSD alternative",
                  "owner": "operator", "done_when": "the sender has the answer",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```