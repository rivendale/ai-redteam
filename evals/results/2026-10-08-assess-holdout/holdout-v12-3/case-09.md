VERDICT: needs-decision. Trying it sends usage data to a new party (the unitykit maintainers), because telemetry is on by default, and the operator has to approve that. My lean is **skip**: none of our four goals needs it, and the one-line install pipes a script from a moving branch straight into the shell.

WHAT IT IS: example-org/unitykit, a repo read from a saved snapshot captured 2026-10-08 (work/meta.json and work/snapshot.md), not live. It is MIT licensed, has 860 stars, was last pushed 2026-09-27, is not archived, and its default branch is `main`. No commit SHA was captured, and install.sh and the source were not in the snapshot.

CLAIMS CHECKED:
- **"handy cli for unity projects"** (sender): UNVERIFIED. The README lists three commands but offers no evidence they save time. "Handy" is the sender's opinion.
- **"install is one line"** (sender): CONFIRMED and load-bearing. The line is `curl -sSL https://raw.githubusercontent.com/example-org/unitykit/main/install.sh | sh`. That runs an unpinned script from the moving `main` branch, and nothing in the snapshot shows what install.sh does.
- **"clean caches, bump versions, list unused assets"** (README): PROBABLE. The README states these features, but no source was read. Not load-bearing.
- **"Anonymous usage statistics are collected by default"** (README): CONFIRMED by the item's own text. Load-bearing.
- **"To turn them off set `UNITYKIT_TELEMETRY=0`"** (README): UNVERIFIED. No source was read to show the variable actually stops all reporting. Load-bearing for any trial.
- **License MIT, last release 2026-09-27**: CONFIRMED by meta.json.
- **860 stars**: a true count, but not evidence of quality or safety. Not load-bearing.

FIT:
- **Goal:** none found.
  - Goal 1 (Android build under 10 minutes) is the closest, but "clean caches" and "list unused assets" are not shown to cut build time.
  - It does nothing for crashes, translations or the devlog.
- **Overlap:** version bumps and cache cleaning are routine steps that Jenkins jobs often already handle. The context file does not say whether ours do, so this overlap is not confirmed.
- **Burden:** a new CLI to install and keep updated on the macOS Mac mini and on Windows machines. The README shows only a POSIX `sh` install, so Windows support is unknown.
- **Cost:** free, open source, MIT. No tier limits were found. Checked 2026-10-08 from the snapshot.
- **Risks:**
  - The install path is `curl | sh` from an unpinned `main` branch.
  - Telemetry is on by default and goes to a new party. This is developer usage data, not player data, but it is still data leaving the machine.
  - Whether the opt-out works is unverified.
  - The MIT license is fine for a tool we run and never ship.
  - Project health looks active (pushed 11 days before capture).

NEXT ACTION: The operator decides whether a tool that sends usage data to a new party may be tried at all. Done when the operator records yes or no.
- If **no**: skip, and nothing else to do.
- If **yes**: before any trial, someone reads install.sh and the telemetry code at a pinned commit, without running them, to confirm what the install does and that `UNITYKIT_TELEMETRY=0` disables reporting.
- Hand-off: none.

CONFIDENCE: medium. It is limited by four things:
- I worked from a saved snapshot, not a live read.
- No commit SHA was captured.
- install.sh and the source were not available, so what the installer does and whether the telemetry opt-out works are unverified.
- The context file is present.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "repo",
           "identity": "example-org/unitykit (no sha captured; MIT, 860 stars, last push 2026-09-27, not archived, default branch main; read from snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "handy cli for unity projects (sender)", "evidence": "README lists commands; no evidence of time saved", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "install is one line (sender)", "evidence": "README: curl -sSL .../main/install.sh | sh, an unpinned script from a moving branch piped to the shell", "status": "CONFIRMED"},
    {"claim": "cleans caches, bumps versions, lists unused assets", "evidence": "README feature list; source not read", "status": "PROBABLE", "load_bearing": false},
    {"claim": "anonymous usage statistics are collected by default", "evidence": "README states it", "status": "CONFIRMED"},
    {"claim": "setting UNITYKIT_TELEMETRY=0 turns telemetry off", "evidence": "README states it; no source read to verify", "status": "UNVERIFIED"},
    {"claim": "license is MIT, last release 2026-09-27", "evidence": "meta.json license and last_push; README", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "860 stars", "evidence": "meta.json; a true count, not evidence of quality", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (goal 1, Android build under 10 minutes, is closest, but no build-time benefit is shown)",
          "overlap": "version bumps and cache cleaning may already be Jenkins steps; not confirmed from the context file",
          "burden": "a new CLI on the macOS Mac mini and Windows machines; only a POSIX sh install is shown",
          "risks": ["curl | sh install from the unpinned main branch",
                    "telemetry on by default sends usage data to a new party",
                    "telemetry opt-out unverified",
                    "MIT is acceptable for a tool we run and never ship"],
          "cost": {"price": "free", "tier": "open source", "limits": "none found", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether a tool with default-on telemetry to a new party may be tried; if yes, first read install.sh and the telemetry code at a pinned commit without running them",
                  "owner": "operator",
                  "done_when": "the operator records yes or no; if yes, install.sh and the opt-out are confirmed by reading",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```