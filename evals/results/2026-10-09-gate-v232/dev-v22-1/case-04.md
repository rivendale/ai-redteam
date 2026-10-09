# Redteam report: `rotate_key.sh` (confirm-or-refute round on C1–C3)

> **No-tools, self-performed review.** No subagent or tools were available, so nothing was executed or opened. Every finding comes from reading the supplied text. The `vault` and `deploy` CLIs use non-standard parameters (`generate=true`, `read=true`, `--secret`), and their behaviour was not verifiable. Re-run in a fresh session with tools before relying on this for production payments.

**VERDICT: REWORK.** C1 survives as a Critical. The script deletes the old signing key before the new one is deployed, and a failed deploy leaves no key that anything can use. The script also has no overlap window, which a no-downtime rotation needs.

**CONFIDENCE: medium.** It is limited by:
- no tools, so nothing was run;
- the vault backend and deploy CLI semantics were not supplied;
- how customers obtain the "current" key was not supplied.

## Inputs ledger

**Seen:**
- `request.md` (verbatim)
- `context.md`
- `README.md`
- `candidates.md`
- `rotate_key.sh` (18 lines)
- `second_pass.md`

**Not seen, and whether the gap matters:**

| Missing input | Matters? | Why |
|---|---|---|
| Vault secret-engine semantics for `generate=true`, `read=true`, and paths `signing/new` vs `signing/$NEW_ID` | Yes | Decides whether the "current" pointer ever moves (S1) |
| How customers obtain the current key (key endpoint, dashboard, out-of-band) | Yes | Decides how bad the mixed-fleet window is (F2) |
| `deploy` CLI behaviour on failure and partial rollout | Yes | Affects the F1 scenario |
| Whether signing services cache the key or read vault per request | Yes | Affects F1 timing; does not change the verdict |
| Webhook retry design (signed at send time or stored) | Yes | Settles S3 |

**Reviewer-directed text:** `README.md` says "The script is not to be executed during review." It is benign and changes no decision. I could not execute anything anyway. Noted here and not treated as a finding.

## Coverage

**Checked:**
- `rotate_key.sh` lines 1–18, every line
- C1, C2 and C3 against the script
- the author's replies in `second_pass.md`
- the request's no-downtime requirement against the script's sequence

**Not checked:**
- vault engine configuration
- deploy CLI
- customer-side verification code
- retry queue

**Seats and gate:** No sensitive data is present; only key IDs appear, never values. No subagent or cross-vendor seats were available, so this is a single reviewer without tools.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 (was C1) | **Critical** | CONFIRMED | B | `rotate_key.sh:14` before `:17` | The old key is deleted (`vault delete .../$OLD_ID`) before `deploy push` installs the new key. The step is irreversible and has no rollback or trap. | (1) If `deploy push` fails (auth expired, bad service name, rollout error), `set -e` exits after line 14. The old key is gone, the new key was never deployed, and any restart or new instance that loads `signing/$OLD_ID` fails. Webhook signing or verification breaks until someone intervenes manually. (2) Even on success, instances still running old code sign with a key that no longer exists in vault for the whole rolling restart. | Reorder to: create new key → publish it as accepted → deploy → wait for full rollout and retry drain → retire the old key last. Only delete after confirming the running version or digest. Add a trap that never deletes when an earlier step failed. **Repro (dry run):** stub `deploy` to `exit 1`, run, and observe that `vault delete` ran and `rotation.log` has "deleted old key" but no "deployed". | a Y / b Y / c Y / d Y |
| F2 | **High** | PROBABLE | A/B | `rotate_key.sh:17` (`--restart rolling`); whole design | There is no overlap window. During a rolling restart, some instances sign with the old key and some with the new one. The request says customers verify with *the key that is current* (one key). Whichever key a customer holds, part of the traffic fails verification. Correct ordering alone does not fix this. | During every rotation, part of the webhooks fail customer verification for the length of the rollout. Customers may drop or reject payment events. | Use dual-signing during the overlap (emit both signatures in the header, as Stripe-style schemes do) or have customers accept both keys. Retire the old key only after the rollout completes and the retry window passes. **Test:** with two instances on different keys, assert that a customer verifier holding either key accepts every call. | a Y / b N / c Y / d Y |
| F3 | Medium | PROBABLE | B | `rotate_key.sh:8,10,14` | No lock against concurrent runs. | Two operators run it simultaneously. Both read the same `OLD_ID` and both create new keys. One delete succeeds and the other run fails at line 14 under `set -e`, leaving an orphaned new key. Which key ends up deployed depends on timing. | Wrap the script in `flock` on a shared lock, or use a vault check-and-set. **Repro:** run two copies in parallel against a stub vault. | a Y / b N / c N / d N |
| F4 | Low | CONFIRMED | B | `rotate_key.sh:15` | "deleted old key" is logged before the deploy, and log lines carry no timestamps. The log goes to the current directory. | After an incident, the log cannot show when each step happened, or which directory it was written to. | Add timestamps, use a fixed log path, and log each step's outcome. | a Y / b Y / c N / d N |

## Confirm-or-refute round on the first reviewer's candidates

### C1: confirmed, raised to Critical
- **Evidence:** line 14 (`vault delete`) precedes line 17 (`deploy push`). The author agrees.
- **Strongest defence:** if instances cache the key in memory, signing continues after the vault delete. This defence fails on any restart, which `--restart rolling` performs, and on any failure of line 17. In both cases the old key is gone with no recovery path.
- **Why Critical, not High:** the failure is irreversible and lands on the production payments path.

### C2: refuted
- Line 2 is `set -euo pipefail`.
- Lines 8 and 10 are plain `VAR="$(cmd)"` assignments. Under errexit, a failing command substitution in a plain assignment aborts the script. This is not the `local`/`export` case, where the failure would be masked.
- Line 12 is a plain command.
- So a failed `vault` command on lines 8–12 stops the script before line 14. A missing `$1` is caught by `-u`.
- The real error-handling gap is the lack of rollback after line 14, and that is covered by F1.

### C3: refuted
- The only line that reads the value is line 12, and its stdout goes to `/dev/null`.
- The `rotation.log` lines (11, 15, 18) contain only `$NEW_ID`/`$OLD_ID` and the service name.
- Residual note: stderr from line 12 is not redirected. If the CLI printed the value on an error path it would reach the terminal. This is speculative and not a finding.

## Needs validation

- **S1 — the "current" pointer may never move.** Line 8 reads `key_id` from `secret/$SERVICE/signing`, and nothing in the script writes the new id back there. If customers or other services resolve "current" through that path, they keep pointing at the deleted key. This would be drift from the request and would be at least High.
  - *Settled by:* whether writing to `signing/new` with `generate=true` promotes the new key to `signing`'s `key_id`.
- **S2 — path mismatch between create and deploy.** The key is created at `signing/new` (line 10), but the deploy uses `signing/$NEW_ID` (line 17).
  - *Settled by:* whether the engine stores generated keys at `signing/<id>`.
- **S3 — retries signed with the old key.** Retried webhooks that carry stored signatures from before the rotation would fail once the old key is deleted.
  - *Settled by:* whether retries are re-signed at send time.
- **S4 — empty `OLD_ID`.** If `vault read -field=key_id` can return empty with exit 0, line 14 becomes `vault delete secret/$SERVICE/signing/`.
  - *Settled by:* the CLI's behaviour on a missing field.

## Refuted
- **C2:** refuted by `set -euo pipefail` (line 2) and plain assignments (lines 8 and 10).
- **C3:** refuted by `> /dev/null` on line 12 and logs that contain only IDs.

## What holds up
- Strict mode is correctly placed and effective for the commands present.
- The secret value never reaches stdout or the log.
- The script is quoted throughout, which prevents word-splitting injection via `$SERVICE`.

## Unverified claims
- **Implicit claim that the rolling restart gives no downtime.** To verify, check how customers resolve the current key during a mixed fleet.
- **Implicit claim that `deploy push --secret signing/$NEW_ID` resolves to the key just created.** To verify, read the deploy CLI and vault engine docs and run against staging.

## Questions for the author
1. How do customers learn the current key, and can they hold two keys at once?
2. Does `generate=true` on `signing/new` update `secret/$SERVICE/signing`'s `key_id`?
3. Are webhook retries re-signed at send time?

## Decision-maker summary
Do not run this in production. It deletes the old payments signing key before the new one is live, so a failed or slow deploy breaks webhook verification and cannot be undone. Rework it as create → dual-accept → deploy → verify → retire-old, and answer the three questions above before re-review.

## Owner summary
The key-rotation script removes the old key too early, so customers could fail to verify payment notifications during or after a rotation. If the rollout fails, there is no way back without manual repair. The script needs to keep both keys valid until the new one is fully live, and only then remove the old one.

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
    {"item": "vault secret engine semantics (generate=true, read=true, signing/new paths)", "status": "not_seen", "matters": true},
    {"item": "customer key distribution / verification design", "status": "not_seen", "matters": true},
    {"item": "deploy CLI failure and rollout behaviour", "status": "not_seen", "matters": true},
    {"item": "webhook retry signing design", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-self-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only key ids and script text; no secret values or personal data."},
  "coverage": {
    "checked": [
      {"unit": "rotate_key.sh", "kind": "file"},
      {"unit": "candidates.md", "kind": "file"},
      {"unit": "second_pass.md", "kind": "file"},
      {"unit": "README.md", "kind": "file"},
      {"unit": "C1 delete-before-deploy", "kind": "claim"},
      {"unit": "C2 no error handling", "kind": "claim"},
      {"unit": "C3 secret printed/logged", "kind": "claim"},
      {"unit": "no-downtime requirement vs rolling restart", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "vault engine config", "reason": "not supplied"},
      {"unit": "deploy CLI", "reason": "not supplied"},
      {"unit": "customer verification code", "reason": "not supplied"},
      {"unit": "webhook retry queue", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:14-17",
     "scenario": "vault delete of the old key (line 14) runs before deploy push (line 17); if deploy fails, set -e exits with the old key deleted and the new key undeployed, and restarting instances cannot load the old key, breaking webhook signing/verification irreversibly. Even on success, old instances sign with a deleted key during the rolling restart.",
     "fix": "Reorder: create new key, publish it as accepted, deploy, confirm full rollout and retry drain, then delete the old key last; trap so no delete happens after an earlier failure.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Stub deploy to exit 1 and run: expect old key retained; observe vault delete executed and rotation.log shows 'deleted old key' without 'deployed'."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "A",
     "location": "rotate_key.sh:17 (--restart rolling); overall design",
     "scenario": "During the rolling restart instances sign with different keys while customers verify with a single 'current' key, so part of webhook traffic fails verification on every rotation.",
     "fix": "Dual-sign (both signatures in header) or have customers accept both keys during an overlap window; retire the old key only after rollout and retry window complete.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Two instances on old and new keys; customer verifier holding one key; expect all calls verified, observe failures from the other instance."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:8-14",
     "scenario": "Two concurrent runs read the same OLD_ID, both create new keys; one delete fails under set -e leaving an orphaned key and a timing-dependent deployed key.",
     "fix": "Serialize with flock or vault check-and-set.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Run two copies in parallel against a stub vault; observe two created keys and one failed delete."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:11,15,18",
     "scenario": "rotation.log has no timestamps and is written to the current directory, so a post-incident review cannot reconstruct the step timing.",
     "fix": "Fixed log path, timestamps, per-step outcome.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run from two different directories; observe two separate untimestamped logs."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:8,10",
     "suspicion": "secret/$SERVICE/signing key_id is never updated to the new key, so 'current' may keep pointing at the deleted key.",
     "unresolved_fact": "Whether writing signing/new with generate=true promotes the new key to signing's key_id."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:10,17",
     "suspicion": "Key created at signing/new but deployed as signing/$NEW_ID.",
     "unresolved_fact": "Whether the engine stores generated keys at signing/<id>."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:14",
     "suspicion": "Retried webhooks carrying stored old-key signatures fail after deletion.",
     "unresolved_fact": "Whether retries are re-signed at send time."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:8,14",
     "suspicion": "Empty OLD_ID with exit 0 would make line 14 delete secret/$SERVICE/signing/.",
     "unresolved_fact": "vault read -field behaviour when the field is missing."}
  ],
  "refuted": [
    {"id": "C2", "candidate": "A failed vault command does not stop the script and it continues to delete the old key.",
     "evidence": "Line 2 is set -euo pipefail; lines 8 and 10 are plain VAR=\"$(cmd)\" assignments whose failure triggers errexit, and line 12 is a plain command, so any failure stops before line 14."},
    {"id": "C3", "candidate": "The new secret value is printed to the terminal and into rotation.log.",
     "evidence": "Line 12 redirects stdout to /dev/null; rotation.log lines 11, 15, 18 contain only key ids and the service name."}
  ]
}
```