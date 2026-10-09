VERDICT: try. It serves goal 4 by summarizing the loudness.log that loudness.py already writes, it costs nothing and sends no data anywhere, but nothing in the snapshot shows it can read our log's exact line format, so run it once on our log before relying on it.

WHAT IT IS: example-org/loudness-table, release v0.4.0 at commit `2d7a91c4e08b35f6a1c9d4720e5b83f1a6c0d947`. It is licensed Apache-2.0, has 75 stars, was last pushed 2026-09-23, is not archived and uses `main` as its default branch. These details come from a saved snapshot and meta.json captured on 2026-10-09, not a live read. Only the README-level description was captured. The source file itself was not, so I have not read the code.

CLAIMS CHECKED:
- **Our log is the input it reads** (the sender: "reads the loudness.log that our script writes"). The snapshot expects one line per episode, holding the episode name, the loudness before and the loudness after, in LUFS. Our context file only says that loudness.py "appends the measured loudness before and after." It does not say whether each line carries the episode name, or what separators and order it uses. **UNVERIFIED. The verdict rests on this.**
- **It prints a markdown table across episodes, showing each AFTER value's distance from the target and flagging anything more than 1 LU off.** The evidence is the item's own description, with no example output. **PROBABLE.** The verdict rests on this. The snapshot does not say whether the target can be set to our -16 LUFS or is fixed.
- **No network and no telemetry; it only reads a file and prints to the terminal.** This is the item's own statement, and I could not read the code to check it. **PROBABLE.** The verdict rests on this.
- **It does not change any audio.** This is also the item's own statement. **PROBABLE.** The verdict does not rest on it, since the tool only reads a log anyway.
- **License is Apache-2.0.** meta.json and the snapshot agree. **CONFIRMED.**
- **The project is maintained.** The last push and the v0.4.0 release are both dated 2026-09-23, and it is not archived. **CONFIRMED.** The verdict does not rest on this.

FIT:
- **Goal:** Goal 4 (keep loudness consistent from one episode to the next). It reports drift across episodes. It does not normalize anything.
- **Overlap:** loudness.py already normalizes each episode and records the numbers, so this tool adds only the cross-episode view and the flagging. Nothing we use today does that. A few lines added to loudness.py could do the same job, which is the fallback if the formats don't match.
- **Burden:** One Python file kept on the Mac mini and run by hand. It needs no account, no service and no daily step.
- **Cost:** Free and open source, under Apache-2.0, with no tiers. Read from the snapshot dated 2026-10-09.
- **Risks:** Apache-2.0 would be acceptable even on the site, and this tool runs locally anyway. It is installed by copying one file from a pinned commit, not from a moving branch. The no-network claim is self-reported, so skim the single file before running it. No listener or subscriber data is involved, and there is no lock-in.

NEXT ACTION: The operator copies the one Python file from commit `2d7a91c4e08b35f6a1c9d4720e5b83f1a6c0d947`, reads it quickly to confirm it makes no network calls, and runs it against our current loudness.log.
- **Done when:** it prints a table covering every episode in the log, with AFTER values measured against -16 LUFS.
- **Stop if:** it cannot parse our log lines, or the target cannot be set to -16. In that case, add a summary step to loudness.py instead.
- **Hand-off:** none.

CONFIDENCE: medium. Three things limit it:
- Format compatibility with our log is unverified.
- The code was not captured, so the no-network claim is self-reported.
- The item was read from a saved snapshot, not live.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/loudness-table@2d7a91c4e08b35f6a1c9d4720e5b83f1a6c0d947 (v0.4.0, Apache-2.0, 75 stars, last push 2026-09-23, not archived, default branch main; snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "it reads the loudness.log that our loudness.py writes",
     "evidence": "item expects one line per episode: name, before, after in LUFS; our context file says only that before and after are appended, not whether the episode name or the same layout is present",
     "status": "UNVERIFIED"},
    {"claim": "prints a markdown table of every episode with AFTER's difference from the target, flagging any more than 1 LU off",
     "evidence": "item's own description, no sample output; whether the target is configurable to -16 LUFS is not stated",
     "status": "PROBABLE"},
    {"claim": "no network, no telemetry; reads a file and prints to the terminal",
     "evidence": "item's own statement; source file not in the snapshot",
     "status": "PROBABLE"},
    {"claim": "does not change any audio",
     "evidence": "item's own statement",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "license is Apache-2.0",
     "evidence": "meta.json and snapshot agree",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "project is maintained",
     "evidence": "meta.json: last push 2026-09-23, not archived; release v0.4.0 dated 2026-09-23",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "keep loudness consistent from one episode to the next (goal 4)",
          "overlap": "loudness.py normalizes and logs each episode but gives no cross-episode view; this only reads its log, so it adds to it rather than duplicating it",
          "burden": "one Python file run by hand on the Mac mini; no account or service",
          "risks": ["Apache-2.0, allowed under our license rules", "no-network claim is self-reported; read the single file before running", "may not parse our log format", "install is a copy from a pinned release commit, not a moving branch"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "Apache-2.0",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Copy the one file from commit 2d7a91c4e08b35f6a1c9d4720e5b83f1a6c0d947, read it for network calls, and run it on our current loudness.log",
                  "owner": "operator",
                  "done_when": "it prints a table of every episode in our log with AFTER values compared to -16 LUFS",
                  "stop_condition": "stop if it cannot parse our log lines or cannot use a -16 LUFS target; add a summary step to loudness.py instead",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```