# Assess: cleanvoice-cli

```
VERDICT: try: it serves goal 1 (cut editing time) and nothing in use automates filler cuts, but run it only after
  reading the install script, with usage statistics turned off, on a copy of one episode.
WHAT IT IS: example-org/cleanvoice-cli (repo; sha not captured), MIT, 530 stars, last push 2026-09-12, not archived,
  default branch main. Read from a saved snapshot and meta.json captured 2026-10-09, not live.
CLAIMS CHECKED:
  - Sender: "removes filler words": the README says it removes "um" and "uh" from an audio file. That is PROBABLE as
    stated in the README, untested, and narrower than "filler words" (no "like", "you know", false starts).
    The verdict rests on this.
  - Sender: "in one command": the snapshot shows no usage command at all. UNVERIFIED.
  - Sender: "install is one line": CONFIRMED, but the line is `curl -fsSL https://cleanvoice.example.test/get | bash`.
    That pipes an unread, unpinned script from the vendor's site straight into a shell.
  - Implied by "on our mac": that it runs on macOS. The snapshot names no platforms. UNVERIFIED, and the verdict rests on it.
  - Item: "Anonymous usage statistics, including audio file names and lengths, are sent by default", and
    `CLEANVOICE_NO_STATS=1` turns them off. The default sending is CONFIRMED by the item's own text. That the opt-out
    actually stops all sending is PROBABLE, because it is documented but not checked against code. The verdict rests
    on the opt-out.
  - Item: "License: MIT. Last release 2026-09-12". CONFIRMED, and it matches meta.json.
FIT:
  - Goal: goal 1, cutting editing time to under 2 hours per episode. Today every filler and silence is cut by hand in
    Reaper. It does not touch goals 2, 3 or 4.
  - Overlap: none. Nothing automates cutting, and ffmpeg is used only by loudness.py. It would run before or alongside
    Reaper, not replace it, so it fits the decision that "we edit in Reaper".
  - Burden: one CLI install on the Mac mini, and one extra step per episode before editing.
  - Cost: free, MIT, no account named. Checked 2026-10-09 from the snapshot.
  - Risks:
    - The install path is curl | bash from a vendor domain. It is unpinned and unread.
    - Telemetry is on by default and sends episode file names and lengths to the vendor, which is a new party. This is
      not listener data, but it must be off for the trial.
    - The edits are automatic and could clip words.
    - macOS support is unknown.
    - The project is young-ish but active (pushed 4 weeks ago).
    - MIT is fine, and the tool runs locally anyway.
NEXT ACTION: The operator downloads the install script without running it, reads it, and installs only if it does
  nothing beyond fetching the binary. Then export CLEANVOICE_NO_STATS=1 and run the tool on a copy of last week's
  episode on the Mac mini. Compare the result in Reaper against the hand edit.
  - Done when: the operator has a count of the fillers it removed and missed, any words it clipped, and an estimate
    of the minutes saved per episode.
  - Stop if any of these happens:
    - the script fetches from a moving branch or does anything else, such as editing the shell profile or starting a
      daemon;
    - it does not run on macOS;
    - it makes network calls with stats off;
    - it clips real words;
    - it saves less than about 15 minutes per episode.
  - Hand-off: none.
CONFIDENCE: medium. The item is read from a snapshot. macOS support and the "one command" usage are not shown. The
  install script and the code behind the stats opt-out were not read.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/cleanvoice-cli (sha not captured; MIT, 530 stars, last push 2026-09-12, not archived, default branch main; snapshot 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "removes filler words (sender)", "evidence": "README: removes \"um\" and \"uh\" from an audio file; narrower than all filler words, untested",
     "status": "PROBABLE"},
    {"claim": "works in one command (sender)", "evidence": "snapshot shows no usage command", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "install is one line (sender)", "evidence": "README: curl -fsSL https://cleanvoice.example.test/get | bash (unpinned, unread script piped to a shell)",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "runs on our Mac (implied by sender)", "evidence": "snapshot names no supported platforms", "status": "UNVERIFIED"},
    {"claim": "usage statistics including audio file names and lengths are sent by default", "evidence": "README states it",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "CLEANVOICE_NO_STATS=1 turns the statistics off", "evidence": "README states it; code not read",
     "status": "PROBABLE"},
    {"claim": "MIT license, last release 2026-09-12", "evidence": "README and meta.json agree", "status": "CONFIRMED",
     "load_bearing": false}
  ],
  "fit": {"goal": "cut editing time to under 2 hours per episode (goal 1)",
          "overlap": "none: every filler and silence is cut by hand in Reaper; nothing automates cutting",
          "burden": "one CLI install on the Mac mini and one pre-edit step per episode",
          "risks": ["install is curl | bash from a vendor domain, unpinned and unread",
                    "telemetry on by default sends episode file names and lengths to the vendor; must set CLEANVOICE_NO_STATS=1",
                    "automatic cuts may clip real words",
                    "macOS support not stated",
                    "MIT; runs locally"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Download and read the install script without running it; if it only fetches the binary, install, export CLEANVOICE_NO_STATS=1, and run it on a copy of last week's episode on the Mac mini, then compare the result in Reaper with the hand edit",
                  "owner": "operator",
                  "done_when": "fillers removed and missed, any clipped words, and estimated minutes saved per episode are recorded",
                  "stop_condition": "stop if the script fetches from a moving branch or does anything beyond installing the binary, if it does not run on macOS, if it makes network calls with stats off, if it clips real words, or if it saves less than about 15 minutes per episode",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```