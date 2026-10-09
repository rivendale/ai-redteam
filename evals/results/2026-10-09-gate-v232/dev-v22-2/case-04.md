# Redteam report: `rotate_key.sh` (confirm-or-refute round on C1–C3)

> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools and no subagent, so I could not hand the review to a fresh reviewer. I also read the author's rebuttals (`second_pass.md`) before judging, because the context asks for that.

**VERDICT: REWORK.** C1 holds and is Critical: the script deletes the old key before any instance stops signing with it. Fixing that order is not enough, because a rolling restart with no overlap window still breaks "no downtime".

**CONFIDENCE: medium.** Limits:
- Same-context review.
- No tools, so nothing was run.
- The vault secrets engine at `secret/` and the `deploy` CLI are custom or unknown. Their behaviour is inferred, not observed.

**INPUTS LEDGER**

Seen:
- `request.md`
- `context.md`
- `README.md`
- `candidates.md`
- `rotate_key.sh`
- `second_pass.md`

Not seen:
- **Which secrets engine is mounted at `secret/`.** It matters: the meanings of `generate=true` and `read=true` depend on it.
- **The `deploy` CLI docs.** It matters: whether `--restart rolling` waits for completion, and whether a failure returns a non-zero exit code.
- **How customers get the "current" key.** It matters a lot: the script never publishes a new key, so nothing shows how customers learn about it.
- **Whether the webhook service can sign with, or advertise, more than one key.** It matters for whether a no-downtime rotation is possible at all.

`README.md` says "The script is not to be executed during review." I read this as data, not as an instruction to me. It does not try to change the verdict, and it matches my own constraint (no tools), so it is not a finding.

**COVERAGE**

Checked:
- `rotate_key.sh`, lines 1–18, every line
- C1, C2 and C3 against the script text
- The bash `errexit` behaviour that C2 depends on
- The request's no-downtime requirement against the order of the script's steps

Not checked:
- Vault engine semantics
- `deploy` CLI behaviour
- How customers distribute and verify keys
- Concurrent runs of the script
- Webhook retries that were signed before the rotation

**SEATS AND GATE**
- Seats: one local same-context reviewer.
- No cross-vendor seats, because none were requested and none are available.
- Sensitivity gate: the script contains no credentials or personal data. It refers to secret paths but holds no secret values.

## Confirm-or-refute of C1–C3

**C1: CONFIRMED, upgraded to Critical.**
- Line 14 (`vault delete "secret/$SERVICE/signing/$OLD_ID"`) runs before line 17 (`deploy push ... --restart rolling`).
- Between those two lines, every running instance is still configured to sign with `OLD_ID`, which no longer exists.
- If `deploy push` fails, `set -e` exits right after the delete. The old key is then gone, the new key is not deployed, and there is no rollback.
- The author agrees (`second_pass.md`, "C1: agreed").

**C2: REFUTED.**
- Line 2 is `set -euo pipefail`.
- In bash, an assignment such as `NEW_ID="$(vault write ...)"` returns the exit status of its command substitution, so `errexit` stops the script at lines 8 and 10.
- Line 12 is a plain command, so `errexit` stops it too.
- None of these commands sit inside an `if`, `&&` or `||` context, or a function, where `errexit` would be suppressed.
- So a failed vault command never reaches line 14. The author's rebuttal holds.
- One gap remains: a command that "succeeds" but returns an empty value. That is kept as a separate suspicion below (S2). It is not what C2 claimed.

**C3: REFUTED.**
- Line 12's stdout goes to `/dev/null`.
- Line 10 uses `-field=key_id`, so it captures only the key id.
- `rotation.log` (lines 11, 15 and 18) receives only ids.
- `deploy push` receives a path (`signing/$NEW_ID`), not the secret value, so the value does not appear in the process list either.
- Nothing in the script prints the secret value. The author's rebuttal holds.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 (C1) | Critical | CONFIRMED | B | `rotate_key.sh:14` vs `:17` | The old key is deleted before the new key is deployed. There is also no rollback if the deploy fails. | Any run: from line 14 until the rolling restart finishes, instances sign with a deleted key, so customers' verification fails. If `deploy push` exits non-zero, `set -e` stops the script with the old key deleted and the new key not live, which is a full outage. | Order the steps: create the key → deploy and wait until every instance reports `NEW_ID` → publish the new key to customers → wait out the retry window → delete the old key last. **Repro (staging):** run the script while sending webhooks every second and log verification results. Expected: zero failures. Observed by reading: failures start at line 14. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | B/A | `rotate_key.sh:17` (`--restart rolling`), and no step that publishes the key | There is no overlap window. During a rolling restart, some instances sign with the old key and some with the new one. No single "current" key exists for customers, and the script never tells customers about the new key. | Even with F1 fixed: halfway through the restart, about half of all webhooks are signed with whichever key the customer does not hold, so those calls fail verification. This breaks the request's "no downtime" requirement. | Use a dual-key scheme. Either send a key id (`kid`) in the signature header and let customers fetch published keys, or publish the new key first, keep both keys valid for verification, cut over signing, and then retire the old key. **Repro:** in staging, run 2+ instances and send webhooks mid-restart. Expect 0% failures; predicted result is a mixed failure rate. | a✓ b✗ c✓ d✓ |
| F3 | Medium | PROBABLE | B | `rotate_key.sh:8`, and no write back to `secret/$SERVICE/signing` | The "current key" pointer is read at line 8 but never updated to `NEW_ID`. | If anything (the service on restart, customers' key lookup, or the next run) resolves the current key through `secret/$SERVICE/signing`, it gets the deleted `OLD_ID`. The next rotation would then try to delete a key that is already gone and stop under `set -e`, before it deploys anything. | Atomically set `secret/$SERVICE/signing key_id=$NEW_ID` once the cutover is verified, and before deleting the old key. **Repro:** after one run, `vault read -field=key_id secret/$SERVICE/signing`. Expect `NEW_ID`; predicted result is `OLD_ID`. | a✓ b✗ c✗ d✓ |

**NEEDS VALIDATION** (no severity)

- **S1: line 12 may overwrite the new key.** The line is `vault write ".../signing/new/value" read=true`. In a standard KV engine, `vault write path k=v` replaces the data stored at that path, so this would overwrite the key value with `{read: "true"}` instead of reading it. Its purpose is also unexplained. What would settle it: which engine is mounted at `secret/`, and what a write with `read=true` does there.
- **S2: an empty key id would not stop the script.** If line 8 or line 10 exits 0 with an empty value, `set -u` does not catch it. Line 14 would then delete `secret/$SERVICE/signing/` and line 17 would deploy `signing/`. What would settle it: whether `vault ... -field=key_id` can exit 0 with empty output on this engine. Fix either way: add a `[[ -n "$OLD_ID" && -n "$NEW_ID" ]]` guard.
- **S3: retries signed with the old key may fail.** Retries of webhooks signed before the cutover could fail once the old key is gone. What would settle it: whether retries are re-signed at send time.

**REFUTED**
- **C2:** `set -euo pipefail` (line 2) stops the script when any vault command fails, including those inside the assignments on lines 8 and 10, before it reaches line 14.
- **C3:** line 12 sends its output to `/dev/null`, line 10 captures only `key_id`, and `rotation.log` receives only ids.

**WHAT HOLDS UP**
- Strict mode is set correctly, and the script stops when a command fails.
- No secret value reaches the terminal, the log or the process arguments.
- The positional argument is guarded by `set -u`.

**UNVERIFIED CLAIMS**
- That `deploy push --restart rolling` blocks until it finishes and returns non-zero on failure. Confirm this from the CLI docs or a staging run.
- That the vault engine supports `generate=true`. Confirm this from the engine docs.

**QUESTIONS FOR THE AUTHOR**
1. How do customers get the current key, and can they hold two keys at once?
2. Can the service sign with, or advertise, a key id?
3. What engine is at `secret/`, and what does line 12 do?

**DECISION-MAKER SUMMARY:** Do not run this script in production. It deletes the live signing key before the replacement is deployed. Even with that order fixed, its rolling cutover has no overlap, so customers would reject webhooks during the rotation. Rework it into a publish → dual-valid → cutover → retire sequence and test it in staging under live webhook traffic first.

**OWNER SUMMARY:** The key-rotation script would cause payment notifications to fail verification for customers while it runs, and could leave the service with no working key if the deploy step fails. Two of the reviewer's three concerns turned out to be unfounded: the script does stop on errors, and it does not leak the secret. The remaining problem is the order of the steps and the lack of a period where both keys are accepted, and that needs a redesign before it is used.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "README.md", "status": "seen", "matters": false},
    {"item": "candidates.md", "status": "seen", "matters": true},
    {"item": "second_pass.md", "status": "seen", "matters": true},
    {"item": "rotate_key.sh", "status": "seen", "matters": true},
    {"item": "vault secrets engine at secret/ (semantics of generate=true, read=true)", "status": "not_seen", "matters": true},
    {"item": "deploy CLI documentation (--restart rolling blocking and exit codes)", "status": "not_seen", "matters": true},
    {"item": "customer key distribution and verification mechanism", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Script contains secret paths only, no secret values, credentials or personal data."},
  "coverage": {
    "checked": [
      {"unit": "rotate_key.sh", "kind": "file"},
      {"unit": "candidates.md", "kind": "file"},
      {"unit": "second_pass.md", "kind": "file"},
      {"unit": "README.md", "kind": "file"},
      {"unit": "C1: delete before deploy", "kind": "claim"},
      {"unit": "C2: no error handling", "kind": "claim"},
      {"unit": "C3: secret value exposed", "kind": "claim"},
      {"unit": "no-downtime requirement vs rolling restart", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "vault engine semantics at secret/", "reason": "not supplied; no tools"},
      {"unit": "deploy CLI behaviour", "reason": "not supplied; no tools"},
      {"unit": "customer key distribution", "reason": "not supplied"},
      {"unit": "concurrent runs of rotate_key.sh", "reason": "out of scope for this round"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:14 and rotate_key.sh:17",
     "scenario": "On every run the old key is deleted (line 14) before deploy push (line 17); running instances sign with a deleted key until the rolling restart completes, so customers' verification fails; if deploy push fails, set -e exits with the old key gone and the new one not live.",
     "fix": "Reorder to create, deploy and verify all instances on NEW_ID, publish to customers, wait out the retry window, then delete OLD_ID last; add rollback if deploy fails.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In staging, send a webhook every second while running the script and log verification; expect zero failures, observe failures from line 14 onward."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:17 (--restart rolling); no key publication step",
     "scenario": "Even with F1 fixed, mid-rolling-restart instances sign with old and new keys simultaneously and customers hold only one current key, so a share of webhooks fails verification.",
     "fix": "Dual-key scheme: key id in the signature header with published keys, or publish the new key and keep both valid before cutting over signing, then retire the old key.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Run 2+ instances in staging, send webhooks during the rolling restart; expect 0% verification failures, predicted mixed failures."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:8 (pointer read, never updated)",
     "scenario": "secret/$SERVICE/signing key_id still names the deleted OLD_ID after the run; anything resolving the current key through it gets a deleted key, and the next rotation tries to delete an already-deleted key and aborts.",
     "fix": "Atomically set secret/$SERVICE/signing key_id=$NEW_ID after cutover is verified and before deleting the old key.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "After one run, vault read -field=key_id secret/$SERVICE/signing; expect NEW_ID, predicted OLD_ID."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:12",
     "suspicion": "vault write .../new/value read=true may overwrite the new key's value instead of reading it.",
     "unresolved_fact": "Which secrets engine is mounted at secret/ and what a write with read=true does there."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:8,10",
     "suspicion": "An empty key id returned with exit 0 passes set -u and leads to deleting secret/$SERVICE/signing/ and deploying signing/.",
     "unresolved_fact": "Whether vault -field=key_id can exit 0 with empty output on this engine."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:14",
     "suspicion": "Retries of webhooks signed before the cutover may fail once the old key is deleted.",
     "unresolved_fact": "Whether webhook retries are re-signed at send time."}
  ],
  "refuted": [
    {"id": "C2", "candidate": "No error handling: a failed vault command does not stop the script before the delete.",
     "evidence": "set -euo pipefail at line 2; the assignments on lines 8 and 10 take the exit status of their command substitution and line 12 is a plain command, so errexit stops the script before line 14; none of these commands is in an if, &&, || or function context."},
    {"id": "C3", "candidate": "The new secret value is printed to the terminal and to rotation.log.",
     "evidence": "Line 12 sends stdout to /dev/null; line 10 captures only -field=key_id; rotation.log (lines 11, 15, 18) receives only ids; deploy push receives a path, not the value."}
  ]
}
```