# Assess: loudness-table

```
VERDICT: try — it fills a real gap under goal 4 (loudness.py normalizes and logs, but nothing shows the episodes side by side), it is free, local and Apache-2.0, and the one open question is whether it reads our loudness.log as written.
WHAT IT IS: example-org/loudness-table, release v0.4.0 at 2d7a91c4e08b35f6a1c9d4720e5b83f1a6c0d947, Apache-2.0, 75 stars, last push 2026-09-23, not archived, default branch main. Read from a saved snapshot captured 2026-10-09 (snapshot.md and meta.json), not live. The source file itself is not in the snapshot.
CLAIMS CHECKED:
  - "Reads a log with one line per episode (name, loudness before, loudness after, in LUFS) and prints a markdown table, flagging any episode more than 1 LU from the target." The only evidence is the README description; no code is shown. PROBABLE. The verdict rests on this.
  - "No network, no telemetry; reads a file and prints to the terminal." This is the project's own statement, and the source is not in the snapshot. PROBABLE. The verdict rests on this.
  - "It does not change any audio." The README says so. PROBABLE. Not load-bearing, since the table is all we want from it.
  - "License: Apache-2.0." meta.json (read live at capture) agrees. CONFIRMED.
  - Sender: "reads the loudness.log that our script writes." The context file only says loudness.py appends the loudness measured before and after. It does not give the line format or say whether the episode name is on each line. The README also does not say whether the target can be set (ours is -16 LUFS). Nothing here settles it either way. UNVERIFIED. The verdict rests on this, and the trial exists to check it.
FIT:
  - Goal: goal 4 (keep loudness consistent from one episode to the next). It turns the per-episode log into a cross-episode view and flags outliers.
  - Overlap: loudness.py already does the normalizing and the measuring. This tool does neither. It only reports on the log, which nothing in use does today. There is no overlap with Reaper, ffmpeg or Buzzsprout.
  - Burden: copy one Python file and run it by hand on the Mac mini when wanted. No account and no service.
  - Cost: free, open source, Apache-2.0, as read 2026-10-09.
  - Risks: The license is fine under any rule here, and it runs on our own machine anyway. The install is a single file pinned to a release commit, not `curl | bash` from a moving branch. The "no network" claim should be confirmed by reading that file before running it. The only data it touches is loudness numbers and episode names, with no listener or subscriber data. Project health looks fine for a one-file tool (a recent release, not archived). Lock-in: none.
NEXT ACTION: The operator reads the one Python file at commit 2d7a91c, checking that it has no network or subprocess calls and that it does not write to the input. Then they run it on our loudness.log with the target at -16 LUFS. Owner: operator. Done when a table prints with every episode in the log and its AFTER-vs-target difference. Stop condition: stop if it cannot parse our log without changing loudness.py's output format, if the target cannot be set to -16, or if the file makes any network call. Hand-off: none, because this is using a tool, not borrowing ideas.
CONFIDENCE: medium. It is limited by three things: the claim the verdict most depends on (that it reads our log format) is unverified, the tool's source is not in the snapshot, and the item was read from a 2026-10-09 snapshot, not live. A context file is present.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/loudness-table@2d7a91c4e08b35f6a1c9d4720e5b83f1a6c0d947 (v0.4.0, Apache-2.0, 75 stars, last push 2026-09-23, not archived; from snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "reads a one-line-per-episode loudness log and prints a markdown table, flagging episodes more than 1 LU from the target",
     "evidence": "README description only; source not in the snapshot", "status": "PROBABLE"},
    {"claim": "no network, no telemetry; reads a file and prints to the terminal",
     "evidence": "project's own statement; source not in the snapshot", "status": "PROBABLE"},
    {"claim": "does not change any audio", "evidence": "README statement", "status": "PROBABLE",
     "load_bearing": false},
    {"claim": "license is Apache-2.0", "evidence": "README and meta.json (read live at capture) agree",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "it reads the loudness.log that our loudness.py writes (sender)",
     "evidence": "context file gives no line format for loudness.log; README does not say whether the target is configurable",
     "status": "UNVERIFIED"}
  ],
  "fit": {"goal": "goal 4: keep loudness consistent from one episode to the next",
          "overlap": "none: loudness.py normalizes and logs, but nothing in use reports across episodes",
          "burden": "copy one Python file and run it by hand on the Mac mini",
          "risks": ["Apache-2.0, fine under every license rule", "single file pinned to a release commit, not curl|bash",
                    "no-network claim unread in source; read the file before running",
                    "touches only loudness numbers and episode names, no listener data"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "Apache-2.0",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Read the one Python file at commit 2d7a91c (no network/subprocess calls, no writes to the input), then run it on our loudness.log with the target at -16 LUFS",
                  "owner": "operator",
                  "done_when": "a table prints listing every episode in loudness.log with its AFTER-vs-target difference",
                  "stop_condition": "stop if it cannot parse our log without changing loudness.py's output, cannot use a -16 LUFS target, or makes any network call",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```