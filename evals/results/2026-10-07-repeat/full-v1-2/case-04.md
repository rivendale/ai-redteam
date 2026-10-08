# Redteam Report: Confirm-or-Refute Round on `rotate_key.sh`

**Review conditions:** I had no tools in this session, so I did not run the script, call `vault` or `deploy`, or check the vault path layout. I did not write this work, so there is no author-context anchoring. There is some anchoring risk from the first reviewer's framing, which I tried to counter by attacking the script directly.

**VERDICT: REWORK.** C1 survives, and the author's agreed fix (moving the delete after the deploy) still breaks verification during the rolling restart. The script also never makes the new key "current", and a stray `vault write` may overwrite the new secret.

**CONFIDENCE IN VERDICT: medium.** The script order and bash `set -e` behavior are certain. What the custom vault paths do (`generate=true`, `read=true`, `signing` vs `signing/<id>`), what `deploy push` does, and how customers obtain the key are unknown and were not checkable.

---

## Pass 1: Reconstruct

The script claims to rotate the payments webhook signing key without downtime. Its steps are:
1. Read the current key id.
2. Generate a new key.
3. Delete the old key.
4. Roll the new key out with a rolling restart.

For this to be correct, these must all be true:
- At every moment, every signature a customer receives verifies against the key that is "current" for that customer.
- The new key becomes the recorded current key.
- Nothing destroys key material that is still in use.
- No secret value leaks.

Unstated assumptions:
- Customers learn about the new key at the right time.
- A rolling restart has no window where old and new signers coexist.
- The vault paths behave as the script assumes.

---

## Confirm-or-Refute Decisions

### C1: SURVIVES. CONFIRMED, raised to Critical.

The script order is `vault delete "secret/$SERVICE/signing/$OLD_ID"` followed by `deploy push ... --restart rolling`. Two failure modes follow:

- **Instances re-read the key from vault.** They fail as soon as the delete runs.
- **Instances cached the key in memory.** They keep signing with a key that no longer exists anywhere customers or support could reference.

If `deploy push` fails, `set -e` stops the script *after* the delete. The old key is gone, the new key is not deployed, and there is no rollback.

The author's agreement covers only the ordering. The deeper problem remains even after reordering (see F2).

### C2: REFUTED as stated. CONFIRMED.

Under `set -e`, a plain assignment like `NEW_ID="$(vault write ...)"` takes the exit status of the command substitution, so a failing `vault` call exits the script. This would not hold for `local`, `export`, or `declare`, but none of those are used. The bare `vault write ... > /dev/null` also exits on failure.

`set -u` makes a missing `$1` fatal, and `pipefail` is irrelevant because there are no pipes. The author is right.

Two residual gaps remain, filed below as F5 and F6:
- A command can exit 0 while producing empty output.
- There is no cleanup on partial failure.

### C3: REFUTED. CONFIRMED.

- The only `echo` lines write `$NEW_ID` and `$OLD_ID`, which are ids, not values.
- `vault write -field=key_id` captures only the id.
- The `read=true` call sends stdout to `/dev/null`.
- `deploy push` receives a path (`signing/$NEW_ID`), not a value.

Nothing in the script prints the secret. stderr from vault is not redirected, but an error message is very unlikely to contain the value. The author is right. That same `read=true` line has a different problem, filed as F3.

---

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| F1 (C1) | Critical | CONFIRMED | `vault delete ...` before `deploy push ... --restart rolling` | The old key is destroyed while it is still the active signer. | During the rolling restart, or if `deploy push` fails, webhooks are signed with a deleted key or nothing can sign. Customer verification fails and the outage cannot be rolled back. | Delete the old key only in a separate later step, after the deploy has fully succeeded and a grace period has passed. Run `deploy push` before any destructive action. |
| F2 | Critical | PROBABLE (depends on how customers get the key) | Whole design; `--restart rolling` | A rolling restart guarantees a window where some instances sign with OLD and others with NEW. The request says customers verify "with the key that is current when they receive the call." No single "current" key makes both sets of signatures valid. Reordering the delete does not fix this. | Mid-rollout, about half of webhooks fail verification at customers who already switched to NEW (or who are still on OLD). Payment events get rejected or retried. | Use an overlap protocol: publish NEW to customers as accepted, dual-sign (send both signatures with key ids in a header, Stripe-style), roll out, switch the primary, then retire OLD after the retry window. Test by verifying with each customer-side key during a staged rollout. |
| F3 | High | PROBABLE (custom vault path) | `vault write "secret/$SERVICE/signing/new/value" read=true > /dev/null` | `vault write` writes data. On KV-style backends, `read=true` stores `{read: "true"}` at that path and can overwrite the freshly generated value. Reading is `vault read`. The line's purpose is undocumented, and its output is discarded either way. | The new key value is replaced with `read=true`. Instances deploy a corrupt or attacker-guessable "key", and signatures fail or become forgeable. | Remove the line, or replace it with an explicit `vault read` that checks the value exists without printing it. Confirm the backend semantics against a test vault. |
| F4 | High | PROBABLE | `OLD_ID` read from `secret/$SERVICE/signing`; NEW written to `.../signing/new`; nothing updates `.../signing` | The script never repoints the "current" record to `NEW_ID`. | The vault still says OLD is current, but OLD is deleted. The next rotation reads the stale OLD_ID again, and the delete fails or hits the wrong key. Any customer-facing key publication derived from this record shows the wrong key. | Write `key_id=$NEW_ID` to `secret/$SERVICE/signing` after the deploy succeeds. Assert by re-reading it. |
| F5 | Medium | CONFIRMED (bash semantics) | `NEW_ID="$(vault write -field=key_id ...)"` | An exit status of 0 with empty output passes `set -e` and `set -u`. | `NEW_ID=""`. The script deletes OLD and then runs `deploy push --secret "signing/"`, which is a full outage. | Add `[[ -n "$NEW_ID" && "$NEW_ID" != "$OLD_ID" ]] \|\| exit 1`. Apply the same check to `OLD_ID`. |
| F6 | Medium | CONFIRMED | Whole script; no `trap` | Partial failure has no cleanup or rollback. | If `echo >> rotation.log` fails (read-only cwd) after the key is created, an orphan NEW key is left behind. If the deploy fails after the delete, see F1. | Order steps so that every destructive step comes last. Add `trap` reporting of the state reached. Write the log to an absolute, verified-writable path. |
| F7 | Medium | PROBABLE | Whole script | There is no lock against concurrent runs. | Two operators run the script at once. Two NEW keys are created, and the deploys race. One deployed key has no current record, or the second run tries to delete an OLD that is already gone. | Take a vault lock or CAS on the `signing` record, or use `flock`. |
| F8 | Low | CONFIRMED | `rotation.log` (relative path), log lines | The log location depends on cwd, and entries have no timestamps or operator. | The audit trail for a payments key rotation is scattered or unusable. | Use an absolute path, `date -u` timestamps, and `$USER`. |

---

## WHAT HOLDS UP

- `set -euo pipefail` does stop the script on any failing command. C2 is refuted.
- No secret value is echoed or logged. C3 is refuted.
- A missing `$1` is fatal under `set -u`.

---

## UNVERIFIED CLAIMS

| Claim or assumption | How to confirm |
|---|---|
| `generate=true` creates a key and `-field=key_id` returns its id. | Run against a test vault mount. |
| What `read=true` does at `.../new/value`. | Same. Read the path before and after the call. |
| Whether instances re-read the key from vault or cache it. | Check the service code. |
| What `deploy push --secret signing/<id>` resolves (`signing/<id>` vs `signing/new`, given the new key was written to `signing/new`). | Read the deploy CLI documentation or do a dry run. |
| How customers learn the current key (JWKS endpoint, dashboard, email). | Read the customer integration docs. This determines whether F2 is fatal. |

---

## QUESTIONS FOR THE AUTHOR

1. How do customers obtain the verification key, and do they accept more than one at a time? This answers F2.
2. What does `vault write .../new/value read=true` do in your backend, and why is it there? This answers F3.
3. What is supposed to update `secret/$SERVICE/signing` to the new id? This answers F4.

---

## DECISION-MAKER SUMMARY

Do not run this script against production payments. C1 is real, and the agreed fix only reorders the delete. A rolling restart still mixes signers unless customers can accept both keys during an overlap window. Before reuse, the script needs:
- a dual-key or dual-signature rotation,
- an explicit update of the current-key record,
- removal or verification of the `read=true` write,
- non-empty id checks.

```json
{
  "verdict": "REWORK",
  "candidate_decisions": {
    "C1": "survives (CONFIRMED, raised to Critical)",
    "C2": "refuted (set -e exits on failed command substitution in plain assignment); residual gaps filed as F5/F6",
    "C3": "refuted (only key ids are logged; value output goes to /dev/null)"
  },
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "rotate_key.sh: `vault delete secret/$SERVICE/signing/$OLD_ID` precedes `deploy push ... --restart rolling`",
      "scenario": "During the rolling restart, or if deploy push fails after the delete, webhooks are signed with a deleted key or cannot be signed; customer verification fails with no rollback.",
      "fix": "Deploy first; delete the old key only in a later separate step after full rollout plus a grace period covering webhook retries."
    },
    {
      "severity": "Critical",
      "evidence_level": "PROBABLE",
      "location": "rotate_key.sh: overall design, `--restart rolling`",
      "scenario": "A rolling restart means old and new instances sign concurrently; with a single 'current' key on the customer side, part of the traffic fails verification mid-rollout even after reordering the delete.",
      "fix": "Overlap protocol: publish the new key as accepted, dual-sign with key ids, roll out, switch primary, retire the old key after the retry window; test verification with each customer-side key during a staged rollout."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "rotate_key.sh: `vault write \"secret/$SERVICE/signing/new/value\" read=true > /dev/null`",
      "scenario": "vault write stores data; on a KV-style backend this writes {read: true} over the newly generated value, so instances deploy a corrupt or trivial key.",
      "fix": "Remove the line or replace it with a `vault read` existence check that does not print the value; confirm semantics against a test vault."
    },
    {
      "severity": "High",
      "evidence_level": "PROBABLE",
      "location": "rotate_key.sh: OLD_ID read from `secret/$SERVICE/signing`, never updated to NEW_ID",
      "scenario": "The current-key record still points at the deleted OLD key; the next rotation reuses a stale id and any customer-facing key publication shows the wrong key.",
      "fix": "After a successful deploy, write key_id=$NEW_ID to secret/$SERVICE/signing and assert by re-reading it."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "rotate_key.sh: `NEW_ID=\"$(vault write -field=key_id ...)\"`",
      "scenario": "vault exits 0 with empty output; set -e/-u do not catch it; the old key is deleted and `deploy push --secret signing/` deploys nothing usable.",
      "fix": "Validate `[[ -n $NEW_ID && $NEW_ID != $OLD_ID ]]` (and non-empty OLD_ID) before any further step."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "rotate_key.sh: no trap or rollback anywhere",
      "scenario": "A failure mid-script (for example, unwritable rotation.log after key creation, or deploy failure after delete) leaves orphaned or destroyed keys with no record of the state reached.",
      "fix": "Put destructive steps last, add a trap that reports the state reached, and use an absolute, verified-writable log path."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "rotate_key.sh: whole script, no locking",
      "scenario": "Two concurrent runs create two new keys, race their deploys, and attempt a double delete of the old key.",
      "fix": "Use flock or a vault CAS/lock on the signing record."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "rotate_key.sh: `>> rotation.log`",
      "scenario": "The log is written to whatever the cwd is, without timestamps or operator, so the audit trail for a payments key rotation is unreliable.",
      "fix": "Use an absolute log path with `date -u` timestamps and $USER."
    }
  ]
}
```