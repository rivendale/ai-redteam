**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools in this session, so nothing was executed. The script was not run, as `README.md` requires.

**VERDICT: REWORK.** C1 is confirmed. The script also has no overlap window in which customers can verify with both keys, so it cannot deliver "no downtime" as requested. C2 and C3 are refuted as stated.

**CONFIDENCE: medium.** Three things limit it: this is a same-context review, I had no tools, and the semantics of the `vault` and `deploy` CLIs (custom paths, `generate=true`, `read=true`) are unverified.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `README.md`, `candidates.md`, `rotate_key.sh`, `second_pass.md`.
- **Not seen:**
  - The vault secret layout and backend (KV or a custom plugin). This matters because the path findings and the `read=true` finding depend on it.
  - The `deploy` CLI documentation. This matters for what `--secret` resolves to.
  - How customers obtain the verification key (a shared HMAC secret or a published public key). This matters for whether the request is met at all.
  - How running instances load the key (at startup or on each request). This matters for how severe C1 is.

**SEATS AND GATE:** Only the local same-context reviewer ran. No subagent or cross-vendor seats were available. The sensitivity gate passed: the work contains no secrets or personal data, only a script.

## Confirm-or-refute of C1 to C3

**C1: confirmed.** In `rotate_key.sh`, `vault delete "secret/$SERVICE/signing/$OLD_ID"` comes before `deploy push ... --restart rolling`. For the whole rolling restart, old instances sign with a key that has been deleted from the vault. Any old instance that restarts or re-reads the key fails to start or fails to sign. Customers who switch to the new key reject signatures from old instances. If `deploy push` fails, `set -e` stops the script after the delete, which leaves no deployed key in the vault. The author agrees with this finding.

**C2: refuted as stated.** Line 2 is `set -euo pipefail`. Under `set -e`, a failing simple command exits the script. An assignment whose command substitution fails, such as `OLD_ID="$(vault read ...)"`, also exits, because the assignment takes the substitution's exit status. A failed vault command therefore never reaches `vault delete`. Residual weaknesses remain, and they are listed as F4 and F5 below.

**C3: refuted as stated.**
- `vault write ... read=true > /dev/null` discards stdout.
- `rotation.log` receives only `$NEW_ID` and `$OLD_ID`, which are key IDs, never values.
- stderr is not redirected, but stderr normally carries errors, not the secret.

The same line has a different problem, listed as F3 below.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | B | `rotate_key.sh`: `vault delete` line before the `deploy push` line | The old key is deleted before the new key is deployed (C1). | During a rolling restart, old instances sign with a deleted key. If the deploy fails, the old key is gone and the new key is not live. | Reorder the steps: create the key, deploy it, verify all instances, wait out a grace period, then delete the old key. | confirmed |
| 2 | High | CONFIRMED (absence in script); PROBABLE (impact) | B, drift | Whole script | No step gives customers the new verification key. There is no dual-key window: no publishing of both keys, no key ID in the signature header, and no period where customers accept both. The request's "no downtime" requirement is not met. | During and after the rollout, customers still hold the old key and reject every webhook signed with the new key. Mid-rollout, a mix of old and new signers causes intermittent failures. | Add a publish phase: distribute the new key (JWKS or customer portal) and include a key ID in signatures. Have customers accept both keys, then switch signing, and retire the old key only after every in-flight call and retry has finished. | confirmed: nothing in the script touches customer-facing key distribution. |
| 3 | Medium | PROBABLE | B | `vault write "secret/$SERVICE/signing/new/value" read=true` | The comment and the author describe this as a read, but `vault write` with `key=value` writes data. On a KV backend it stores `{read: "true"}` at `.../new/value` and may overwrite the new key material. | The deployed secret is wrong or empty, so every signature fails after the rollout. | Confirm the backend's semantics. To read a value, use `vault read -field=...`; to keep the value off the terminal, do not read it at all. | not High: depends on the unseen backend |
| 4 | Medium | PROBABLE | B | `OLD_ID=...`, `NEW_ID=...`, `vault delete ".../signing/$OLD_ID"` | IDs are never checked for being non-empty. `vault read -field` can exit 0 with empty output. | An empty `OLD_ID` deletes `secret/$SERVICE/signing/`, which could be the parent path or the current key. An empty `NEW_ID` deploys `signing/`. | Add `[[ -n "$OLD_ID" && -n "$NEW_ID" && "$OLD_ID" != "$NEW_ID" ]] \|\| exit 1`. | n/a |
| 5 | Medium | PROBABLE | B | Paths: the read from `secret/$SERVICE/signing`, the create at `.../signing/new`, the delete at `.../signing/$OLD_ID`, the deploy of `signing/$NEW_ID` | The paths are inconsistent. The key is created at a fixed `new` path, but the deploy references `signing/$NEW_ID`. The current-key pointer `secret/$SERVICE/signing` is never updated to `NEW_ID`. | The deploy references a path that may not exist. The next rotation reads the already-deleted old ID again. Concurrent or repeated runs collide on `signing/new`. | Define one layout. Write the new key at `signing/$NEW_ID`, then update the pointer atomically. Add a lock against concurrent runs. | n/a |
| 6 | Low | CONFIRMED | B | `>> rotation.log` | The log uses a relative path with no timestamp, and there is no rollback or cleanup of the orphan key left by a mid-run failure. | The audit trail ends up in whatever directory the script was run from. A partial run leaves an unused key behind. | Use an absolute log path with timestamps, and add a `trap` that reports the partial state. | n/a |

## WHAT HOLDS UP
- `set -euo pipefail` does stop the script on a failed command, so C2 is correctly refuted.
- No secret value is written to the log or to stdout, so C3 is correctly refuted.
- `set -u` catches a missing `$1`.

## UNVERIFIED CLAIMS
- The vault paths and flags (`generate=true`, `read=true`, `-field=key_id` on a write) behave as the author assumes. This would be settled by the backend's documentation or a dry run against a dev vault.
- `deploy push --secret` resolves `signing/$NEW_ID`. This would be settled by the deploy CLI documentation.

## QUESTIONS FOR THE AUTHOR
1. How do customers get the verification key, and can they hold two keys at once?
2. What does `vault write .../new/value read=true` do on your backend?
3. Do instances read the key from the vault only at startup or on every signature?

## DECISION-MAKER SUMMARY
Do not run this against production. It deletes the old key before the new one is live, and it never gives customers the new key, so webhook verification breaks during rotation and may stay broken afterwards. Rework it into a phased rotation: publish the new key, accept both keys, switch signing, wait out a grace period, then retire the old key.

## OWNER SUMMARY
The key rotation script would cause customers to reject our payment notifications while it runs, and possibly after it finishes. It removes the old key too early and never tells customers about the new one. It needs to be redone as a staged changeover before anyone uses it.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "vault backend/path layout", "status": "not_seen", "matters": true},
    {"item": "deploy CLI semantics", "status": "not_seen", "matters": true},
    {"item": "customer key distribution mechanism", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "script only; no secrets or personal data"},
  "findings": [
    {"id": "C1", "severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh: vault delete line precedes deploy push line", "scenario": "Old key deleted while old instances still sign with it during rolling restart; a failed deploy leaves no live key", "fix": "Order the steps create, deploy, verify, grace period, delete old", "status": "confirmed"},
    {"id": "C2", "severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh line 2: set -euo pipefail", "scenario": "Claimed failed vault command continues to delete; set -e exits on failure including failed command substitution in assignment", "fix": "None needed for the claim as stated; see empty-ID validation finding", "status": "refuted"},
    {"id": "C3", "severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh: vault write ... read=true > /dev/null; echo lines log only ids", "scenario": "Claimed secret printed or logged; stdout is discarded and the log holds only key ids", "fix": "None needed for the claim as stated", "status": "refuted"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh (whole script)", "scenario": "No dual-key window or customer key distribution; customers reject webhooks signed with the new key, and mixed signers mid-rollout cause intermittent failures; the request's no-downtime requirement is not met", "fix": "Publish the new key, include a key id in signatures, have customers accept both keys, switch signing, retire the old key after a grace period", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rotate_key.sh: vault write \"secret/$SERVICE/signing/new/value\" read=true", "scenario": "vault write stores {read: true}, possibly clobbering new key material; the deployed secret is wrong", "fix": "Verify backend semantics; use vault read or remove the line", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rotate_key.sh: OLD_ID/NEW_ID assignments and vault delete", "scenario": "Empty id with exit 0 makes the delete target secret/$SERVICE/signing/ and the deploy reference signing/", "fix": "Check that both ids are non-empty and distinct before any delete or deploy", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rotate_key.sh: paths signing, signing/new, signing/$OLD_ID, signing/$NEW_ID", "scenario": "Inconsistent paths and a current-key pointer that is never updated; the deploy may reference a nonexistent path and the next rotation reuses the deleted id", "fix": "Use one path layout, update the pointer atomically, add a lock", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "rotate_key.sh: >> rotation.log", "scenario": "Relative log path without timestamps; no cleanup after a partial run", "fix": "Use an absolute timestamped log and a trap that reports partial state", "status": "n/a"}
  ]
}
```