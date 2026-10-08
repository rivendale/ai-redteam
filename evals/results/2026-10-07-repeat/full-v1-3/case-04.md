Note: this is not a same-context review. The work was not produced in this conversation, so I reviewed it directly. I had no tools, so nothing was run; every verdict rests on reading the script text. The `vault` and `deploy` calls do not match stock Vault KV semantics (for example `generate=true` and `read=true`), so their behaviour is UNVERIFIED.

## Pass 1: Reconstruct

The script claims to rotate the payments webhook signing key with no downtime. It reads the current key id, creates a new key, deletes the old key, then rolls the new key out to the service. For that to be correct:

- The old key must stay usable until no instance signs with it and no customer still needs it.
- The new key must become "current" for customers before or as instances start signing with it.
- The vault paths must point at what the script assumes.
- `deploy push --restart rolling` must finish before anything depends on the rollout being complete.

## Confirm-or-refute round

**C1: SURVIVES (CONFIRMED), and it is broader than stated.**
- `vault delete "secret/$SERVICE/signing/$OLD_ID"` runs before `deploy push ... --restart rolling`, so the author's concession is correct.
- Reordering alone does not fix it. During a rolling restart, old and new instances sign at the same time. The request says customers verify with "the key that is current when they receive the call", so one of the two signer groups fails verification whichever key is current.
- If `deploy push` fails after the delete, the old key is gone, the new key is not deployed, and there is no rollback. Under `set -e` the script just stops.

**C2: REFUTED.**
- `set -euo pipefail` is on line 2.
- Plain assignments like `NEW_ID="$(vault write ...)"` take the exit status of the command substitution, so `-e` aborts on failure. The exceptions are `local` and `export` forms, and neither is used here.
- `vault write ... > /dev/null` also aborts on failure. There are no pipes, so `pipefail` is irrelevant but harmless.
- A failed vault command therefore never reaches `vault delete`. The real problem is the missing rollback after the delete, which is covered under C1.

**C3: REFUTED.**
- `rotation.log` only receives `$NEW_ID` and `$OLD_ID`, which are ids, not values.
- The one command that may return the value has its stdout sent to `/dev/null`.
- Nothing is echoed to the terminal.
- `deploy push --secret "signing/$NEW_ID"` passes a reference, not the secret value.

## Report

**VERDICT: REWORK.** The script deletes the old key before the rollout. It has no overlap window for mixed signers or for customers. It never promotes the new key to "current". So it cannot rotate with no downtime as written.

**CONFIDENCE IN VERDICT: medium-high.** The ordering and promotion findings are visible in the text. Confidence is limited because I had no tools and the semantics of the custom `vault`/`deploy` commands are unknown.

### Findings, ordered by severity

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `vault delete .../$OLD_ID` before `deploy push ... --restart rolling` (C1) | The old key is destroyed while instances still sign with it. Nothing can be rolled back if the deploy fails. | Instances not yet restarted sign with a deleted key, so customer verification fails. If `deploy push` errors, the script exits with the old key gone and the new key undeployed. | Use phases: create new key, publish it to customers alongside the old one, deploy and wait for the rollout to complete, switch "current", wait out the retry/grace window, then delete old. Add a trap or rollback for each phase. |
| 2 | High | CONFIRMED | No write to `secret/$SERVICE/signing` anywhere; new key lives at `signing/new` | The new key is never promoted to current. `secret/$SERVICE/signing` still holds `key_id=$OLD_ID`, which is now deleted. | Any consumer of the "current key" pointer (customer key endpoint, verification docs, the next rotation run) gets a deleted id. The next rotation reads the stale `OLD_ID` and fails or deletes the wrong thing. | Atomically update the current pointer as a distinct step. Test: after a run, `vault read -field=key_id secret/$SERVICE/signing` equals `$NEW_ID`. |
| 3 | High | PROBABLE | Whole design vs. request ("key that is current when they receive the call") | There is no overlap period, so mixed signers during the rollout and webhooks still in flight or retried at the switch moment fail verification. | A webhook signed with the old key arrives, or is retried, just after "current" switches. The customer verifies with the new key and rejects it. | Sign with both keys during the overlap (multi-signature header) or have customers accept old and new until a grace deadline. Confirm whether retries re-sign at send time. |
| 4 | Medium | UNVERIFIED | `vault write "secret/$SERVICE/signing/new/value" read=true > /dev/null` | It uses `write` to read a value. On a stock KV engine this would overwrite the path with `{read: "true"}`. It has no visible purpose. | If this is KV, the secret data at `signing/new/value` is replaced. If it was meant as a validation step, it validates nothing. | Confirm the backend's semantics. Replace it with a read-only check that the new key is retrievable, or remove it. |
| 5 | Medium | UNVERIFIED | `deploy push --restart rolling` | It is unknown whether this blocks until every instance runs the new key. | If it returns early, any step that follows it (a reordered delete, a pointer switch) races the rollout. | Wait for or poll rollout completion and health before proceeding. |
| 6 | Medium | UNVERIFIED | `vault delete "secret/$SERVICE/signing/$OLD_ID"` vs. `vault read ... "secret/$SERVICE/signing"` | The old id is read from `signing`, but the old key is assumed to live at `signing/$OLD_ID`. That layout is never established. | The delete targets a nonexistent or wrong path. Either it errors, or it "succeeds" while the real old key remains, so rotation does not actually retire it. | Document and assert the key layout. Read back the path before deleting. |
| 7 | Low | PROBABLE | Whole script | There is no lock against concurrent runs. | Two operators run it at once: two new keys are created and one is orphaned or deleted under the other. | Use a lock (vault CAS, `flock`, or a deploy lock). |

### What holds up
- `set -euo pipefail` correctly stops the script on any failing command before the delete (C2 refuted).
- No secret value reaches the log or the terminal, and the deploy step passes only a reference (C3 refuted).
- A missing `$1` aborts via `set -u` rather than running against an empty service name.

### Unverified claims
- What `vault write ... generate=true` and `read=true` actually do on this backend. Settle it by checking the plugin/engine docs, or by a dry run against a non-production mount.
- Whether `deploy push --restart rolling` is synchronous. Check the deploy CLI docs, or time a rollout.
- Whether webhook retries are re-signed at send time or replay the stored signature. Check the webhook sender code.
- How customers obtain the "current" key, and whether they can hold two keys at once.

### Questions for the author
1. How do customers learn the current key? Can they accept two keys during an overlap window?
2. Is `secret/$SERVICE/signing` the pointer the signing service and the customer key endpoint read? Where is it supposed to be updated?
3. Does `deploy push --restart rolling` block until the rollout is complete?
4. Are retried webhooks re-signed with the key current at send time?

### Decision-maker summary
Do not run this script in production. It deletes the live signing key before rollout, never marks the new key as current, and has no overlap window, so webhook verification will fail for customers during and after rotation. Of the first reviewer's findings, C1 stands (and is worse than stated), while C2 and C3 are refuted by `set -euo pipefail` and the `/dev/null` redirect; the rework needs phased publish → deploy-and-wait → switch → grace → delete steps with rollback.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "rotate_key.sh: `vault delete \"secret/$SERVICE/signing/$OLD_ID\"` runs before `deploy push --service \"$SERVICE\" --secret \"signing/$NEW_ID\" --restart rolling` (candidate C1, survives)",
      "scenario": "During the rolling restart, instances not yet restarted sign with the deleted old key and customer verification fails; if deploy push fails after the delete, set -e exits with the old key gone and the new key undeployed, with no rollback.",
      "fix": "Phase the rotation: create new key, publish it to customers alongside the old one, deploy and wait for rollout completion, switch current, wait out the retry/grace window, then delete the old key; add a trap/rollback per phase."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "rotate_key.sh: no write updates `secret/$SERVICE/signing`; the new key exists only under `secret/$SERVICE/signing/new`",
      "scenario": "After a run, the current pointer still holds key_id=$OLD_ID, which has been deleted; consumers of the current key and the next rotation read a deleted id.",
      "fix": "Atomically promote the new key to current as an explicit step; test that `vault read -field=key_id secret/$SERVICE/signing` returns $NEW_ID after the run."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "rotate_key.sh overall vs. request: 'customers verify ... with the key that is current when they receive the call'",
      "scenario": "With no overlap period, webhooks signed by not-yet-restarted instances, or in flight/retried at the moment current switches, are verified by customers against the other key and rejected.",
      "fix": "Dual-sign during an overlap window, or have customers accept both old and new keys until a grace deadline; confirm whether retries are re-signed at send time."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "rotate_key.sh: `vault write \"secret/$SERVICE/signing/new/value\" read=true > /dev/null`",
      "scenario": "A write is used to read a value; on a stock KV engine this overwrites the path's data with {read: \"true\"}, and as a validation step it checks nothing.",
      "fix": "Confirm the backend semantics; replace with a read-only check that the new key is retrievable, or remove the line."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "rotate_key.sh: `deploy push ... --restart rolling`",
      "scenario": "If the command returns before every instance runs the new key, any following step (a reordered delete or a pointer switch) races the rollout.",
      "fix": "Wait for or poll rollout completion and instance health before proceeding."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "rotate_key.sh: `vault read -field=key_id \"secret/$SERVICE/signing\"` vs. `vault delete \"secret/$SERVICE/signing/$OLD_ID\"`",
      "scenario": "The script assumes the old key lives at signing/$OLD_ID without establishing that layout; the delete either errors or succeeds against the wrong path while the real old key remains.",
      "fix": "Document and assert the key path layout; read back the target path before deleting it."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "rotate_key.sh overall",
      "scenario": "Two concurrent runs each create a new key; one key is orphaned, or one run deletes the key the other just deployed.",
      "fix": "Take a lock (vault check-and-set, flock, or a deploy lock) for the duration of the rotation."
    }
  ]
}
```