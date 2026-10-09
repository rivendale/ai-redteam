```
VERDICT: skip. It is GPL-3.0, our site code must be MIT, Apache-2.0 or BSD, and it serves none of our four goals.
WHAT IT IS: example-org/chapter-player, default branch main (no commit sha in the snapshot). GPL-3.0, 300 stars, last push 2026-09-14, not archived. Read from the saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live.
CLAIMS CHECKED:
  - Sender: "adds a play button with the chapter list to episode pages". PROBABLE. The README says this, but the snapshot has no code to confirm it. Not load-bearing.
  - Item: GPL-3.0, and "anything that includes this shortcode must itself be released under the GPL". CONFIRMED by meta.json and the README's own license line. LOAD-BEARING.
  - Item: "no tracking". UNVERIFIED, because the snapshot has no script source to read. Not load-bearing.
  - Item: "no dependencies". UNVERIFIED for the same reason. Not load-bearing.
  - Item: "plain HTML and a small script". UNVERIFIED. Not load-bearing.
FIT:
  - Goal: none found. Our goals are editing time under 2 hours, newsletter signups, a transcript per episode and consistent loudness. A chapter player on episode pages serves none of them.
  - Overlap: none named in the context file. I did not check whether the Buzzsprout player already shows chapters.
  - Burden: small. It is one shortcode added to the Hugo site.
  - Cost: free (open source), as read 2026-10-09.
  - Risks: the license breaks the standing rule that shipped site code (theme and shortcodes) must be MIT, Apache-2.0 or BSD. GPL is allowed only for tools run on our own machines. Its terms would also require the site code that includes it to be released under the GPL. Project health looks fine (pushed last month).
NEXT ACTION: Tell the sender it is declined because GPL-3.0 code cannot ship on the show site and it serves no current goal. Owner: whoever answers the sender (operator). Done when the reply is sent. Hand-off: none.
CONFIDENCE: high. The item is resolved from a dated snapshot, the claim the verdict rests on (the license) is CONFIRMED, and the context file is present. The unverified claims about tracking and dependencies do not affect the verdict.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/chapter-player@main (sha not captured; GPL-3.0, 300 stars, last push 2026-09-14, not archived; snapshot 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "adds a play button with the chapter list to episode pages (sender)",
     "evidence": "README description; no code in snapshot", "status": "PROBABLE", "load_bearing": false},
    {"claim": "licensed GPL-3.0; anything including the shortcode must be released under the GPL",
     "evidence": "meta.json license field and the README license line", "status": "CONFIRMED"},
    {"claim": "no tracking", "evidence": "README assertion only; script source not in snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "no dependencies", "evidence": "README assertion only; source not in snapshot",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "plain HTML and a small script", "evidence": "README assertion only; source not in snapshot",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found",
          "overlap": "none named in the context file (not checked: whether the Buzzsprout player already shows chapters)",
          "burden": "one shortcode added to the Hugo site",
          "risks": ["GPL-3.0 breaks the standing rule that site code must be MIT, Apache-2.0 or BSD",
                    "GPL terms would require the including site code to be released under the GPL"],
          "cost": {"price": "free", "tier": "open source", "limits": "none",
                   "terms": "GPL-3.0 (copyleft applies to anything that includes it)", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Reply to the sender declining: GPL-3.0 cannot ship on the show site and it serves no current goal",
                  "owner": "operator", "done_when": "the reply is sent", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```