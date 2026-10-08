# Redteam report: `rotate_key.sh` (confirm-or-refute round)

**Review conditions:** This is an independent review, since the work was not produced in this conversation. I had no tools, so nothing was executed, consistent with the README. The vault commands (`generate=true`, `read=true`, a `signing/new` path) do not match the standard Vault KV CLI. They look like a custom secrets engine whose behavior I cannot check, which caps confidence on anything that depends on vault semantics.

## Pass 1: Reconstruct

The script claims to rotate the payments webhook signing key with no downtime. It reads the current key id, generates a new key, deletes the old key, then rolls the new key out to the service.

For this to be correct, all of the following must hold:
- (a) Every signer and every customer verifier agree on which key is "current" at each instant, including during a rolling restart.
- (b) Nothing signed with the old key is still in flight, such as retries or queued deliveries, when the old key is deleted.
- (c) The vault paths written, deleted, and deployed refer to the same key.
- (d) A failure at any step leaves at least one valid key in service.

## Candidate rulings

**C1: ordering, delete before deploy. Survives (CONFIRMED).**
- `vault delete "secret/$SERVICE/signing/$OLD_ID"` runs before `deploy push ... --restart rolling`. The author concedes this.
- The concession understates the problem. Moving the delete after the deploy is not enough for zero downtime (see F2).

**C2: no error handling. Refuted as stated.**
- `set -euo pipefail` is on line 2. Under `set -e`, a plain assignment `VAR="$(cmd)"` takes the exit status of the command substitution, so a failing `vault read` or `vault write` aborts the script before the delete. Unset `$1` also aborts under `-u`.
- The author's rebuttal is correct on its own terms.
- Two real weaknesses sit next to it, and I report them as new findings rather than keep C2 alive:
  - A failure after the delete, in `deploy push`, aborts with the old key already gone and no rollback (F3).
  - A command that exits 0 with empty output is not caught (F5).

**C3: secret value exposed. Refuted as stated.**
- The only value-touching command sends stdout to `/dev/null`.
- `rotation.log` receives only `$NEW_ID` and `$OLD_ID`, which are identifiers, not key material. No line echoes the value.
- A residual question about what that line actually does is F6 (Low).

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| F1 (=C1) | Critical | CONFIRMED | `vault delete ...` precedes `deploy push ...` | Old key is destroyed while every running instance still signs with it. | From the delete until the rolling restart finishes, signatures come from a key that no longer exists as "current". Customer verification fails and production payment webhooks are rejected. | Never delete before the new key is fully live. Delete only after deploy succeeds and after a grace period longer than the maximum webhook retry window. |
| F2 | Critical | PROBABLE | Whole design; `--restart rolling` | No overlap period. Even with the delete reordered, a rolling restart means old and new instances sign with different keys at the same time. Customers verify with a single "current" key, per the request. | Mid-rollout, about half of deliveries are signed with the key customers don't consider current, so verification fails. Retries queued before the rotation and signed with the old key also fail. | Use a two-phase rotation: (1) publish the new key so customers accept old and new, or send a key-id header customers use to select a key; (2) switch signing; (3) wait at least the retry window; (4) retire the old key. Test by sending webhooks continuously during a staging rotation and asserting zero verification failures. |
| F3 | High | CONFIRMED (control flow) | `deploy push` after `vault delete`, no `trap` | `set -e` stops the script but does not roll back. | `deploy push` fails (auth expired, bad secret path, failed health check). The script exits with the old key deleted and the new key not deployed, so no valid key is in service. | Order the steps so every failure point leaves the old key intact. Add a `trap` for reporting and log the state at each step. |
| F4 | High | PROBABLE | `vault write ... "secret/$SERVICE/signing/new"`; `deploy push --secret "signing/$NEW_ID"`; `vault read ... "secret/$SERVICE/signing"` | Path inconsistency. The key is created under `signing/new` but deployed as `signing/$NEW_ID`, and the old key is deleted at `signing/$OLD_ID`. Nothing ever updates the "current" pointer at `secret/$SERVICE/signing`. | Deploy may reference a path that doesn't exist. The current pointer keeps naming the deleted old key, so the next rotation tries to delete it again, and any customer-facing lookup of "current" returns the dead key. | Confirm the engine's path layout. Explicitly promote the new key to current. Add an assertion that `vault read -field=key_id secret/$SERVICE/signing` equals `$NEW_ID` after the rotation. |
| F5 | Medium | PROBABLE | `OLD_ID=...`, `NEW_ID=...` | Ids are never validated as non-empty. | `vault read` exits 0 with an empty field, so the script runs `vault delete "secret/$SERVICE/signing/"`, which targets the parent path. | Add `[[ -n "$OLD_ID" && -n "$NEW_ID" && "$OLD_ID" != "$NEW_ID" ]] \|\| exit 1`. |
| F6 | Low | UNVERIFIED | `vault write "secret/$SERVICE/signing/new/value" read=true > /dev/null` | The author calls this a read, but `vault write path k=v` writes `{read: "true"}` to the path in standard Vault. The line's purpose is unclear, and its result is discarded either way. | On a KV-like engine this could overwrite the stored value at `signing/new/value`. | Find out what the custom engine does with this call. If it is meant as a check, use a read and assert on the result. Otherwise remove the line. |

## What holds up

- `set -euo pipefail` does stop the script on any failing vault or deploy command, so the C2 rebuttal is right.
- No key material is written to the terminal or the log, so the C3 rebuttal is right.
- Logging ids to `rotation.log` gives a usable audit trail. It is a relative path, so it lands in whatever directory the script is run from.

## Unverified claims

- **Semantics of the custom vault commands** (`generate=true`, `-field=key_id` on write, `read=true`). Confirm with the engine documentation or a dry run against a staging vault.
- **How customers learn the "current" key.** This could be a JWKS-style endpoint, a dashboard, or a key-id header. It determines whether F2 is fully Critical.
- **Whether `deploy push --secret signing/$NEW_ID` resolves.** This depends on the actual layout behind F4.
- **Webhook retry window length.** It sets the minimum grace period before the old key can be deleted.

## Questions for the author

1. How do customers obtain the key they verify with, and can they hold two keys at once or select a key by key id?
2. Where does the new key actually live after `vault write .../signing/new`, and what updates `secret/$SERVICE/signing`?
3. How long can a webhook delivery or retry signed with the old key stay in flight?

## Decision-maker summary

Do not run this in production. Deleting the key before deploying it guarantees failed webhook verification. Even reordered, the script has no overlap period, so a rolling restart still breaks verification for part of the traffic. C2 and C3 are refuted, but the rework needs a two-phase rotation (publish, switch, wait, retire), consistent vault paths, and a design where every failure leaves a valid key in service.

```json
{
  "verdict": "REWORK",
  "candidate_rulings": {
    "C1": "survives (CONFIRMED)",
    "C2": "refuted: set -euo pipefail aborts on failed commands, including in VAR=$(cmd) assignments",
    "C3": "refuted: value output goes to /dev/null and rotation.log holds only key ids"
  },
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "rotate_key.sh: `vault delete \"secret/$SERVICE/signing/$OLD_ID\"` before `deploy push ... --restart rolling` (C1)",
      "scenario": "Old key deleted while all instances still sign with it; customer verification fails for the whole window until the rolling restart completes.",
      "fix": "Delete the old key only after the deploy succeeds and a grace period longer than the webhook retry window has elapsed."
    },
    {
      "severity": "Critical",
      "evidence_level": "PROBABLE",
      "location": "Overall design; `--restart rolling`",
      "scenario": "During the rolling restart, old and new instances sign with different keys while customers verify against a single current key, so part of the traffic fails; in-flight retries signed with the old key also fail.",
      "fix": "Two-phase rotation: publish the new key so customers accept both (or use a key-id header), switch signing, wait at least the retry window, then retire the old key. Test with continuous webhook traffic during a staging rotation and assert zero failures."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "`deploy push` after `vault delete`; no trap or rollback",
      "scenario": "deploy push fails after the delete; set -e exits with the old key gone and the new key not live, leaving no valid key in service.",
      "fix": "Order steps so every failure point leaves the old key intact; add a trap and per-step state logging."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "`secret/$SERVICE/signing/new` vs `signing/$NEW_ID` vs `secret/$SERVICE/signing` (key_id)",
      "scenario": "New key is created under signing/new but deployed as signing/$NEW_ID, and the current pointer is never updated; deploy references a missing path, and the next rotation re-reads the deleted old id.",
      "fix": "Verify the engine's path layout, explicitly promote the new key to current, and assert after rotation that the current key_id equals $NEW_ID."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "`OLD_ID=$(vault read ...)`, `NEW_ID=$(vault write ...)`",
      "scenario": "A command exits 0 with empty output, so the script runs `vault delete secret/$SERVICE/signing/` against the parent path.",
      "fix": "Assert both ids are non-empty and different before any destructive step."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "`vault write \"secret/$SERVICE/signing/new/value\" read=true > /dev/null`",
      "scenario": "Described as a read but is a write; on a KV-like engine it could overwrite the stored value with {read: true}.",
      "fix": "Confirm the engine's semantics; replace with an asserted read or remove the line."
    }
  ]
}
```
