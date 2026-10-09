VERDICT: skip. levelcheck does serve goal 4, but it does the same job as loudness.py, which already normalizes every finished episode to -16 LUFS with ffmpeg's loudnorm and records before/after loudness.

WHAT IT IS: example-org/levelcheck, a repo read from a saved snapshot captured 2026-10-09, not live; no commit sha recorded. MIT license, 640 stars, last push 2026-09-20, not archived, default branch `main`. It is a single Python file that wraps ffmpeg loudnorm, with a default target of -16 LUFS.

CLAIMS CHECKED:
- **Normalizes an audio file to a target loudness, default -16 LUFS, using ffmpeg's loudnorm.**
  - Evidence: the README text in the snapshot. Only the README was captured; the source was not read.
  - Status: PROBABLE. The verdict rests on this, because it is what makes it a duplicate of loudness.py.
- **Prints loudness before and after.**
  - Evidence: README.
  - Status: PROBABLE. The verdict rests on this. loudness.py already does the same and also appends to loudness.log.
- **Free (sender's words).**
  - Evidence: MIT license in both meta.json and the README.
  - Status: CONFIRMED.
- **No account, no network.**
  - Evidence: README only; the source was not in the snapshot.
  - Status: PROBABLE. Not load-bearing.
- **Serves goal 4 (sender's words).**
  - Evidence: goal 4 is "Keep loudness consistent from one episode to the next," and this tool does that.
  - Status: CONFIRMED. Load-bearing, but goal 4 is already covered by loudness.py.

FIT:
- **Goal:** goal 4, loudness consistency.
- **Overlap:** full overlap. loudness.py already uses the same filter, the same -16 LUFS target and the same before/after report, and adds a log. Nothing in the snapshot shows levelcheck doing anything loudness.py does not.
- **Burden:** switching would add a second script to maintain or replace a working one, for no gain.
- **Cost:** free, open source, no limits stated, MIT terms (read 2026-10-09 from the snapshot).
- **Risks:**
  - MIT is fine under our license rules.
  - The tool runs locally on the Macs.
  - The project looks active (pushed 2026-09-20).
  - No install-path or telemetry concerns are stated, but the source was not read.

NEXT ACTION: The operator closes this item as "already covered by loudness.py." It is done when the item is marked skipped. Hand-off: none.

CONFIDENCE: high. The item is resolved from the dated snapshot, every load-bearing claim is CONFIRMED or PROBABLE, and the context file is present. One limit: the snapshot holds only the README, not the source.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "repo",
           "identity": "example-org/levelcheck (MIT, 640 stars, last push 2026-09-20, not archived, default branch main; snapshot 2026-10-09, no sha recorded)",
           "resolved": true},
  "claims": [
    {"claim": "normalizes an audio file to a target loudness (default -16 LUFS) using ffmpeg's loudnorm",
     "evidence": "README in the snapshot; source not captured", "status": "PROBABLE"},
    {"claim": "prints loudness before and after",
     "evidence": "README in the snapshot", "status": "PROBABLE"},
    {"claim": "free (sender's words)",
     "evidence": "MIT license in meta.json and README", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "no account, no network",
     "evidence": "README only; source not read", "status": "PROBABLE", "load_bearing": false},
    {"claim": "serves goal 4 (sender's words)",
     "evidence": "goal 4 is consistent loudness across episodes; the tool normalizes loudness", "status": "CONFIRMED"}
  ],
  "fit": {"goal": "keep loudness consistent from one episode to the next (goal 4)",
          "overlap": "loudness.py already normalizes each episode to -16 LUFS with ffmpeg loudnorm and logs before/after loudness",
          "burden": "a second script doing the same job, or replacing a working one for no gain",
          "risks": ["MIT, allowed", "local only per README; source not read", "project active (push 2026-09-20)"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Close the item as already covered by loudness.py",
                  "owner": "operator", "done_when": "the item is marked skipped",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```