```
VERDICT: needs-decision (data_to_new_party). Installed the way the sender proposes, unitykit sends usage statistics to its maintainers by default. My lean is skip: none of our four goals needs cache cleaning, version bumps or an unused-asset list, and the install pipes a script from a moving branch into the shell.
WHAT IT IS: example-org/unitykit, a repo on default branch main (no sha recorded at capture). MIT license, 860 stars, last push 2026-09-27, not archived. I read it from the saved snapshot and meta.json captured 2026-10-08, not live.
CLAIMS CHECKED:
  - "a handy cli for unity projects" (sender). The README lists three commands: clean caches, bump versions, list unused assets. That they exist: PROBABLE, because only the README was read, not the code. That it is "handy": UNVERIFIED, since that is an opinion with no evidence offered. Not load-bearing.
  - "install is one line" (sender). CONFIRMED: `curl -sSL https://raw.githubusercontent.com/example-org/unitykit/main/install.sh | sh`. That one line runs an unread script from the moving `main` branch, unpinned and with no checksum. Load-bearing.
  - "Anonymous usage statistics are collected by default" (README). That collection is on by default: CONFIRMED by the item's own text. Load-bearing. That the data is "anonymous": UNVERIFIED, because the README does not say what is collected or where it goes. Not load-bearing.
  - "set UNITYKIT_TELEMETRY=0 to turn them off" (README). UNVERIFIED: install.sh and the source were not read, and install.sh itself could report usage before the variable is checked. Not load-bearing.
  - "License: MIT. Last release 2026-09-27." CONFIRMED by meta.json (MIT, last push 2026-09-27). Not load-bearing.
FIT:
  - Goal: none found. Cleaning caches, bumping versions and listing unused assets do not serve goal 1 (Android build under 10 minutes), goal 2 (crash noise), goal 3 (five languages) or goal 4 (devlog).
  - Overlap: version bumps can already be scripted in Jenkins. No listed tool lists unused assets, but no goal asks for that either.
  - Burden: a new CLI on every dev machine and possibly on the Jenkins Mac mini, plus an env var to keep telemetry off everywhere.
  - Cost: free and MIT (checked 2026-10-08). It is a tool we run and never ship, so the license is fine either way.
  - Risks: `curl | sh` from a moving branch. Telemetry is on by default, which sends dev/CI usage data to a new party. That is not player data, but it is a new party. Windows support is not stated, and a `| sh` installer suggests it is macOS/Linux first, while our builds run on macOS and Windows. Health is fine (recent push, not archived).
NEXT ACTION: The operator decides whether a tool that sends usage data to its maintainers by default may be installed at all. My lean is no, since it serves no current goal. Owner: operator. Done-when: the decision is recorded in the context file under "Already decided". If the answer is yes, the trial should pin install.sh to a commit, set UNITYKIT_TELEMETRY=0 before the first run, and read install.sh first. Hand-off: none.
CONFIDENCE: medium. The item was read from a saved snapshot rather than live. install.sh and the source were not read, so the opt-out and the actual data collected are unverified. Windows support is unknown.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "data_to_new_party",
  "item": {"type": "repo",
           "identity": "example-org/unitykit@main (no sha in snapshot; MIT, 860 stars, last push 2026-09-27, not archived; snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "provides commands to clean caches, bump versions and list unused assets", "evidence": "README only; source not read", "status": "PROBABLE", "load_bearing": false},
    {"claim": "it is a handy cli (sender)", "evidence": "none offered", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "install is one line (sender)", "evidence": "README: curl -sSL .../main/install.sh | sh, unpinned moving branch", "status": "CONFIRMED"},
    {"claim": "usage statistics are collected by default", "evidence": "README states it", "status": "CONFIRMED"},
    {"claim": "the usage statistics are anonymous", "evidence": "README asserts it; does not say what is collected", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "UNITYKIT_TELEMETRY=0 turns telemetry off", "evidence": "README; install.sh and source not read", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "MIT license, last release 2026-09-27", "evidence": "meta.json license MIT, last_push 2026-09-27", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found",
          "overlap": "version bumps can already be scripted in Jenkins; no goal needs cache cleaning or unused-asset listing",
          "burden": "new CLI on dev machines and possibly the Jenkins Mac mini; telemetry env var to maintain everywhere",
          "risks": ["curl | sh from the moving main branch, unpinned, script unread",
                    "telemetry on by default sends usage data to a new party",
                    "Windows support not stated; our builds run on macOS and Windows",
                    "MIT, tool we run not ship: license fine"],
          "cost": {"price": "free", "tier": "open source", "limits": "none stated", "terms": "MIT",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether a tool with default-on telemetry to its maintainers may be installed; lean is skip because it serves no current goal",
                  "owner": "operator",
                  "done_when": "decision recorded under Already decided in the context file",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```