VERDICT: try. It could serve goal 1, since nothing automates cutting today, but run a bounded trial on a copy of one episode with telemetry switched off and the installer read before it runs; stop if it sends anything off the Mac.

WHAT IT IS: example-org/cleanvoice-cli, a repo read from a saved snapshot captured 2026-10-09 (no commit sha recorded). License MIT, 530 stars, last push and last release 2026-09-12, not archived, default branch `main`. The README says only that it removes "um" and "uh" from an audio file.

CLAIMS CHECKED:
- **"Removes filler words" (sender).** The README claims only "um" and "uh". Other fillers ("like", "you know") and silences are not claimed. The README gives no evidence of accuracy: no examples, method or test results. PROBABLE for um/uh as a stated feature. Its quality is unknown, and the verdict rests on it.
- **"In one command" (sender).** The snapshot shows no usage example, flags or output format. UNVERIFIED, and the verdict rests on it.
- **"Install is one line" (sender).** CONFIRMED: `curl -fsSL https://cleanvoice.example.test/get | bash`. That one line pipes a script from a third-party domain straight into a shell. The script's contents are not in the snapshot, so what it installs is unknown.
- **Works on our Mac (implied by "try it on our mac").** No platforms are listed anywhere in the snapshot. UNVERIFIED, and the verdict rests on it.
- **Processes audio locally.** The snapshot does not say. UNVERIFIED, and the verdict rests on it. If audio is uploaded, episode audio goes to a new party.
- **Telemetry (from the item's own text).** CONFIRMED: "Anonymous usage statistics, including audio file names and lengths, are sent by default." `CLEANVOICE_NO_STATS=1` turns them off.
- **Health.** 530 stars is popularity, not evidence that it works. A push on 2026-09-12 shows it is active.

FIT:
- **Goal:** goal 1, cutting editing time to under 2 hours per episode. Every filler cut is now made by hand in Reaper.
- **Overlap:** none. Nothing automates cutting, and ffmpeg is used only by loudness.py. Editing stays in Reaper, as already decided. This tool would only pre-process the audio, so it does not replace Reaper.
- **Burden:** a new CLI on the Mac mini, one extra step per episode, and checking its cuts by ear.
- **Cost:** free, MIT, no account mentioned (read 2026-10-09).
- **Risks:**
  - The install path is `curl | bash` from an unseen script.
  - Telemetry is on by default and sends file names and lengths to the vendor. That is not listener data, so the context's approval rule does not strictly apply, but it is still data going to a new party.
  - It is unknown whether the audio is processed locally.
  - macOS support is unstated.
  - Cut quality is unknown, and bad cuts would cost editing time rather than save it.

NEXT ACTION: The operator downloads the install script to a file and reads it instead of piping it to bash. They then install with `CLEANVOICE_NO_STATS=1` set in the environment, run the tool on a copy of last week's episode, and time the remaining hand edits in Reaper against that episode's usual edit time.
- **Owner:** operator (whoever edits).
- **Done when:** the edit time with and without the tool is compared for one episode, and the cuts have been checked by ear.
- **Stop condition:** stop if any of these happens:
  - the script or the tool makes network calls with stats off, or uploads audio (that would make it a needs-decision on data to a new party);
  - it does not run on macOS;
  - its cuts clip words;
  - it saves under about 15 minutes on the episode.
- **Hand-off:** none.

CONFIDENCE: medium. The item is resolved and the context file is present. The claims the verdict rests on (one-command use, Mac support, local processing, cut quality) are unverified in the snapshot, and the snapshot was a saved copy, not a live read.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo", "identity": "example-org/cleanvoice-cli (no sha in snapshot; MIT, 530 stars, last push 2026-09-12, not archived, default branch main; snapshot 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "removes filler words", "evidence": "README claims only 'um' and 'uh'; no examples, method or accuracy evidence", "status": "PROBABLE"},
    {"claim": "works in one command", "evidence": "snapshot shows no usage example or flags", "status": "UNVERIFIED"},
    {"claim": "install is one line", "evidence": "README: curl -fsSL https://cleanvoice.example.test/get | bash (script contents not in snapshot)", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "runs on our Mac", "evidence": "no platforms listed in snapshot", "status": "UNVERIFIED"},
    {"claim": "processes audio locally", "evidence": "snapshot does not say; only telemetry of file names and lengths is mentioned", "status": "UNVERIFIED"},
    {"claim": "sends usage statistics by default, can be disabled", "evidence": "README: file names and lengths sent by default; CLEANVOICE_NO_STATS=1 turns off", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "popular and maintained", "evidence": "meta.json: 530 stars, last push 2026-09-12, not archived; popularity is not evidence it works", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "cut editing time to under 2 hours per episode (goal 1): filler cuts are all made by hand now",
          "overlap": "none: nothing automates cutting; Reaper stays the editor, ffmpeg only runs loudness.py",
          "burden": "a new CLI on the Mac mini, one pre-processing step per episode, checking cuts by ear",
          "risks": ["curl | bash install from an unseen third-party script",
                    "telemetry on by default sends audio file names and lengths to the vendor",
                    "unknown whether audio is processed locally or uploaded",
                    "macOS support not stated",
                    "cut quality unknown; bad cuts add editing time"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT; no account mentioned",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Download and read the install script instead of piping it, install with CLEANVOICE_NO_STATS=1 set, run it on a copy of last week's episode, and time the remaining hand edits in Reaper against that episode's usual edit time",
                  "owner": "operator",
                  "done_when": "edit time with and without the tool is compared for one episode and the cuts are checked by ear",
                  "stop_condition": "stop if the script or tool makes network calls with stats off or uploads audio, does not run on macOS, clips words, or saves under about 15 minutes",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```