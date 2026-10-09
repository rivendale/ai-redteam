VERDICT: try. It serves goal 3, where nothing is in use yet, and runs locally with no account, no cost and no data leaving the machine. What we don't know yet is how much proofreading its output needs, so a one-episode trial should settle that before it becomes a weekly step.

WHAT IT IS: example-org/localscribe on GitHub, read from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json). There is no commit SHA in the snapshot, so the identity is the last release, v1.3.0 (2026-09-29). License MIT, 2,300 stars, last push 2026-09-29, not archived, default branch `main`. It is a command-line transcriber, and its speech model (Apache-2.0, 480 MB) is downloaded once from the project's release page.

CLAIMS CHECKED:
- **"Transcribes an audio file on your own machine"** (sender) / "entirely on your own computer… after that it needs no network" (README): **PROBABLE**, load-bearing. The README states it plainly, but the source was not read, so nothing in the snapshot confirms there are no network calls.
- **"We have nothing for transcripts yet"** (sender): **CONFIRMED**, load-bearing. No tool in context_file.md produces transcripts, and goal 3 is "Publish a transcript with every episode."
- **"No account, no telemetry"**: **PROBABLE**, load-bearing. This is also stated only in the README, without source evidence.
- **"Works on macOS (Apple silicon and Intel); signed and notarized"**: **PROBABLE**, load-bearing because our machines are Macs. It is a README statement and the signature was not checked.
- **"Writes plain text with timestamps and an .srt file"**: **PROBABLE**, not load-bearing.
- **"Model is Apache-2.0, 480 MB, SHA-256 published"; "Install: release binary with a published SHA-256"**: **PROBABLE**, not load-bearing. It is a README statement.
- **License MIT**: **CONFIRMED**. It was read live into meta.json and agrees with the README.
- **Maintained (v1.3.0 on 2026-09-29)**: **CONFIRMED**. The meta.json last_push matches, and the repo is not archived. The 2,300 stars show popularity, not quality.
- The README makes **no claim about accuracy**, and nothing in the item says how good its transcripts are. That is the open question the trial has to answer.

FIT:
- **Goal:** goal 3 (a transcript with every episode).
- **Overlap:** none. Reaper, ffmpeg, Buzzsprout, Mailchimp, Google Docs, Hugo and loudness.py do not transcribe. Nothing in "Already decided" covers transcripts.
- **Burden:**
  - a one-time download of the binary and the 480 MB model;
  - each week, one command per episode plus proofreading the text;
  - a publishing step, still to be chosen (for example a page on the Hugo site).
  - Proofreading time pulls against goal 1 (editing under 2 hours per episode) and should be measured.
- **Cost:** free; MIT tool and Apache-2.0 model; no tier and no account. Read from the snapshot dated 2026-10-09. This fits the $0 budget.
- **Risks:**
  - The MIT license is fine, and the tool runs on our own machine and does not ship on the site anyway.
  - The install path is a signed, notarized binary with a published SHA-256, not `curl | bash`.
  - The local, no-telemetry claims are README-only. The audio is our own episode, not listener or subscriber data, so the data constraint is not triggered.
  - Lock-in is low, because the output is plain .txt and .srt.

NEXT ACTION: The operator installs the v1.3.0 release on the Mac mini and checks the SHA-256 of the binary and the model against the published values. They then transcribe one finished 45-minute episode and record how long the run takes and how long proofreading the transcript takes.
- **Done when:** one corrected transcript exists, and both times are written down.
- **Stop condition:** stop if proofreading takes more than 30 minutes per episode, if a checksum does not match, or if the tool asks for an account or tries to reach the network after the model download.
- **Hand-off:** none.

CONFIDENCE: high. The item is resolved from a dated snapshot, a context file is present, and each claim the verdict rests on is CONFIRMED or PROBABLE. The limits are that this was read from a saved copy rather than live, and that the "no network, no telemetry" claims rest on the README alone. Transcript accuracy is unknown, which is why the verdict is a trial and not adopt.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo", "identity": "example-org/localscribe v1.3.0 (MIT, 2,300 stars, last push 2026-09-29, not archived, default branch main; no commit SHA in the snapshot)",
           "resolved": true},
  "claims": [
    {"claim": "transcribes an audio file entirely on your own machine, no network after the one-time model download", "evidence": "README statement; source not read", "status": "PROBABLE"},
    {"claim": "we have nothing for transcripts yet (sender)", "evidence": "context_file.md: no tool in use produces transcripts; goal 3 is a transcript with every episode", "status": "CONFIRMED"},
    {"claim": "no account, no telemetry", "evidence": "README statement; source not read", "status": "PROBABLE"},
    {"claim": "works on macOS (Apple silicon and Intel), signed and notarized", "evidence": "README statement; signature not checked", "status": "PROBABLE"},
    {"claim": "writes plain text with timestamps and an .srt file", "evidence": "README statement", "status": "PROBABLE", "load_bearing": false},
    {"claim": "model is Apache-2.0, 480 MB, with a published SHA-256; release binary has a published SHA-256", "evidence": "README statement", "status": "PROBABLE", "load_bearing": false},
    {"claim": "license is MIT", "evidence": "meta.json license field read live at capture, matches README", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "actively maintained (v1.3.0 released 2026-09-29)", "evidence": "meta.json last_push 2026-09-29, archived false", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "publish a transcript with every episode (goal 3)", "overlap": "none: nothing in use transcribes",
          "burden": "one-time install and 480 MB model download; weekly run plus proofreading, which competes with goal 1; a publishing step still to choose",
          "risks": ["MIT, runs on our own machine only", "signed and notarized binary with SHA-256, not curl | bash", "local-only and no-telemetry claims are README-only", "accuracy not stated anywhere in the item", "low lock-in: plain .txt and .srt output"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT tool, Apache-2.0 model",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Install v1.3.0 on the Mac mini, verify the binary and model SHA-256, transcribe one finished episode, and record the run time and proofreading time",
                  "owner": "operator", "done_when": "one corrected transcript exists and both times are recorded",
                  "stop_condition": "stop if proofreading takes more than 30 minutes per episode, a checksum does not match, or it asks for an account or reaches the network after the model download",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```