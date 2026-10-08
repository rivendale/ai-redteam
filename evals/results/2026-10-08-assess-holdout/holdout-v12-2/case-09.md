```
VERDICT: needs-decision — installing it as shipped sends usage data from our dev and build machines to a new party (example-org's telemetry is on by default), and the operator has to approve that. My lean is skip: none of its listed commands serves one of our four goals, and the "one line" install is `curl | sh` from the moving `main` branch.

WHAT IT IS: example-org/unitykit (repo), read from a saved snapshot captured 2026-10-08 (work/snapshot.md and
  work/meta.json), not live. Facts at capture: license MIT; 860 stars; last push 2026-09-27; not archived; default
  branch main. No commit SHA was recorded. The snapshot is the README only. install.sh and the source were not
  captured, so I have not read either.

CLAIMS CHECKED:
  1. "install is one line" (sender). CONFIRMED as stated. The README gives
     `curl -sSL https://raw.githubusercontent.com/example-org/unitykit/main/install.sh | sh`.
     The one line pipes an unread script from a moving branch straight into a shell. Load-bearing.
  2. "Anonymous usage statistics are collected by default". CONFIRMED by the item's own README: telemetry is on unless
     the user opts out. Load-bearing.
  3. The statistics are "anonymous". UNVERIFIED. The snapshot does not say what is collected, where it is sent, or how
     long it is kept. The telemetry code was not captured.
  4. Setting `UNITYKIT_TELEMETRY=0` turns telemetry off. UNVERIFIED. This is the README's word only, with no code to
     check it against. It also does not cover anything install.sh itself might send.
  5. "Handy commands for Unity projects (clean caches, bump versions, list unused assets)" / "handy cli" (sender).
     UNVERIFIED. These are the features listed. Whether they work, or work on Unity 6, is not shown anywhere: there is
     no source, no tests and no examples.
  6. License MIT. CONFIRMED (meta.json and README agree).
  7. Last release 2026-09-27. CONFIRMED, matches last_push in meta.json. 860 stars is a true count, but it is not
     evidence that the tool is useful or safe.
  8. Implied: it works for us on macOS and Windows. UNVERIFIED. A `sh` installer suggests Unix only. Windows support
     is not stated.

FIT:
  Goal: none found. Cache cleaning, version bumps and listing unused assets do not directly address any of our goals:
    Android build under 10 minutes, crash noise, five languages by Q1, or the devlog. "List unused assets" might trim
    build size a little, but nothing in the item shows it would affect build time.
  Overlap: version bumping and cache cleaning are usually a few lines in the existing Jenkins job or a Unity editor
    script. I found no specific tool in our list that does the same job, so overlap is partial at most.
  Burden: a new CLI on each dev machine and possibly the Jenkins Mac mini. Every install also needs the opt-out
    env var set, and the tool has to be kept updated.
  Cost: free (MIT, open source), as read in the 2026-10-08 snapshot. No paid tier is mentioned.
  Risks:
    - The install path is `curl | sh` from the `main` branch, with no pinned version and no checksum. We would run
      whatever is on main at install time, and that script is unread.
    - Telemetry is on by default and sends data to a new party (example-org) from our machines. The README does not
      say what is sent.
    - On Windows, a `sh` installer may not work.
    - License: MIT. That is fine, both as a tool we run and if any of it were ever shipped.
    - Project health looks active (push on 2026-09-27, not archived).

NEXT ACTION: The operator decides whether usage telemetry from our machines may go to example-org. My
  recommendation is no, and then skip. Owner: operator. Done when the decision is recorded. If approved anyway,
  install from a pinned tag after reading install.sh, never by piping main into a shell, and set
  UNITYKIT_TELEMETRY=0 first. Hand-off: none.

CONFIDENCE: medium. The context file is present and the load-bearing claims (telemetry on by default, the install
  path) are CONFIRMED from the item's own text. What limits it: I worked from a README-only saved snapshot. install.sh,
  the telemetry code and the commands themselves were not captured, so I could not check what data is sent or whether
  the opt-out works.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "repo",
           "identity": "example-org/unitykit@main (no SHA captured; MIT, 860 stars, last push 2026-09-27, not archived; saved snapshot 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "install is one line (sender)", "evidence": "README: curl -sSL .../main/install.sh | sh, a pipe-to-shell from the moving main branch", "status": "CONFIRMED"},
    {"claim": "anonymous usage statistics are collected by default", "evidence": "README states telemetry is on unless UNITYKIT_TELEMETRY=0", "status": "CONFIRMED"},
    {"claim": "the usage statistics are anonymous", "evidence": "README wording only; telemetry code and data fields not in snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "UNITYKIT_TELEMETRY=0 turns telemetry off", "evidence": "README wording only; code not captured", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "handy commands for Unity projects: clean caches, bump versions, list unused assets", "evidence": "feature list in README; no source, tests or examples captured", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "license is MIT", "evidence": "meta.json license MIT and README agree", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "last release 2026-09-27", "evidence": "matches meta.json last_push 2026-09-27", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "works on our macOS and Windows machines", "evidence": "only a sh installer is given; Windows not mentioned", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (no listed command addresses build time, crash noise, localization or the devlog)",
          "overlap": "version bumps and cache cleaning are typically covered by the existing Jenkins job or editor scripts; no direct tool overlap found",
          "burden": "new CLI on each dev machine and possibly the Jenkins Mac mini, plus a telemetry opt-out env var on each",
          "risks": ["curl | sh install from moving main branch, unpinned and unread",
                    "telemetry on by default sends usage data to a new party (example-org); contents not documented",
                    "sh installer, Windows support unstated",
                    "MIT license, acceptable for tools and shipped code"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether usage telemetry from our machines may go to example-org; recommendation is no, then skip; if approved, install from a pinned tag after reading install.sh with UNITYKIT_TELEMETRY=0 set",
                  "owner": "operator", "done_when": "the decision is recorded",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```