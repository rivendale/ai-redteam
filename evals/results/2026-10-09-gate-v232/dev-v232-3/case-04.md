VERDICT: **REWORK.** The script does not deliver a no-downtime rotation. It deletes the old key before the new one is live. It never marks the new key as current. It gives no overlap during the rolling restart in which customers can verify both keys.

CONFIDENCE: **medium.** Limits:
- No tools in this session. Nothing was run or opened, so every finding comes from reading the 18-line script.
- The behaviour of the `vault` backend (`generate=true`, `-field=key_id` on a write) and the `deploy` CLI was not supplied.
- How customers obtain the verification key was not supplied.
- Single reviewer with no fresh instance. There is anchoring risk from reading C1–C3 and the author's replies first. Re-run in a fresh session before production use.

INPUTS LEDGER:
- **Seen:** request.md, context.md, README.md, candidates.md, rotate_key.sh, second_pass.md.
- **Not seen:** the vault secrets-engine type and its write semantics. This matters for lines 10 and 12.
- **Not seen:** the `deploy push` documentation, specifically whether it returns before the rollout completes and what "rolling" means. This matters for F2 and N2.
- **Not seen:** how customers receive or fetch the verification key, and what reads `secret/$SERVICE/signing`. This matters for F1 and F2.
- **Not seen:** the webhook retry policy, meaning how long a call signed with the old key can still be delivered. This matters for the fix to F3.

COVERAGE:
- **Scope:** the whole work. That means rotate_key.sh lines 1–18, plus C1–C3 and the author's replies.
- **Checked:** all six supplied files; every command in rotate_key.sh; the `set -euo pipefail` semantics behind C2; the output redirections behind C3.
- **Not checked:** runtime behaviour, because there are no tools and README.md says the script is not to be executed. That instruction is a legitimate safety note, not an injection.

SEATS AND GATE:
- One local reviewer only. No subagent or cross-vendor seat was available.
- Sensitivity gate passed. The work contains no secrets, personal data or client material.

## Confirm-or-refute round on C1–C3

**C1 (delete before deploy): CONFIRMED, kept as High (F3), with a corrected mechanism.**
- Line 14 (`vault delete …$OLD_ID`) runs before line 17 (`deploy push … signing/$NEW_ID`).
- The candidate's stated mechanism is weaker than it reads. Running instances most likely hold the old key in memory, so deleting it from vault alone may not stop them signing.
- The real failure is this. From line 14 on, the old key cannot be recovered and the new key is not live. If `deploy push` fails, `set -e` exits right after the delete. Any instance that starts or restarts in that window (autoscaling, a crash) has no valid current key, because the pointer still names the deleted OLD_ID (see F1). There is also no rollback.
- The author agreed. Moving the delete below line 17 is necessary but not sufficient (see F2).

**C2 (no error handling): REFUTED as stated.**
- Line 2 is `set -euo pipefail`. For a plain assignment such as `OLD_ID="$(vault read …)"` with no `local` or `export`, the assignment's exit status is the command substitution's status, so `-e` aborts.
- A failing `vault write` on line 10 or 12 therefore never reaches line 14, and `-u` aborts on a missing `$1`.
- The narrower residual concerns (a "successful" write that returns an empty `key_id`, and no rollback after a mid-run failure) are under N1 and F4.

**C3 (secret printed or logged): REFUTED.**
- Line 12 sends stdout to `/dev/null`.
- Lines 11, 15 and 18 log only `$NEW_ID` and `$OLD_ID`, which are identifiers, not key material.
- No secret appears in command arguments.
- Stderr is not redirected, but it would carry the value only if the backend echoed the secret on error, and nothing indicates that.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B | rotate_key.sh:8, whole script | Line 8 reads the current-key pointer `secret/$SERVICE/signing` (`key_id`), but no line ever updates it to NEW_ID. After rotation it still names OLD_ID, which line 14 deleted. | After a successful run, anything that resolves "the current key" from that path (customer key distribution, new instances, the next rotation) gets a deleted key ID. The next run re-reads the stale OLD_ID and tries to delete it again, while NEW_ID is never retired. | **Fix:** after the deploy is confirmed complete, write NEW_ID to `secret/$SERVICE/signing`; only then retire OLD_ID. **Repro (not executed, no tools):** in an isolated copy, stub `vault` to keep a key→value map, run the script, then `vault read -field=key_id secret/svc/signing`. Expected NEW_ID; the script as written yields OLD_ID. | a✓ b✓ c✗ d✓ |
| F2 | High | PROBABLE | B/A | rotate_key.sh:17; whole design | Drift from the request. During `--restart rolling`, old and new instances sign with different keys at the same time. Customers verify with one "current" key. The script has no overlap window: no step publishes the new key to customers before signing with it, and nothing keeps the old key verifiable afterward. Moving the delete after the deploy (the author's C1 fix) does not fix this. | Midway through the rollout, part of the fleet signs with NEW_ID and part with OLD_ID. Calls from whichever group does not match the customer's current key fail verification. Retried webhooks signed with the old key also fail after it is retired. That is exactly the downtime the request forbids. | **Fix:** run in phases. (1) Create the new key. (2) Publish it so customers accept both keys, or put a key ID in the signature header. (3) Deploy and wait for the rollout to complete. (4) Switch the pointer. (5) Retire the old key only after the maximum retry window. **Repro (not executed):** with stub CLIs, record which key each simulated instance signs with across the rolling steps, and verify each signature with the single published key. Expect 0 failures; mixed steps fail. | a✓ b✗ c✓ d✓ |
| F3 | High | CONFIRMED | B | rotate_key.sh:14 before :17 | The old key is irreversibly deleted before the new key is deployed, and before any deploy success is known (C1). | `deploy push` fails (network, auth, bad secret path). `set -e` exits after line 14. The old key is gone, the new key is not deployed, the pointer names a deleted key, and restarting instances cannot get a valid key. | **Fix:** delete last, after the rollout is verified and the retry window has passed. Add a `trap` that reports the partial state. **Repro (not executed):** stub `deploy` to `exit 1`; run in an isolated copy; observe the delete logged in rotation.log and `secret/svc/signing/$OLD_ID` absent, with no deploy line. | a✓ b✓ c✓ d✓ |
| F4 | Low | CONFIRMED | B | rotate_key.sh:11-18 | There is no rollback or cleanup. An abort leaves an orphaned new key, and rotation.log (relative to the current directory) records only successes, not where the run stopped. | An abort at line 12 or 17 leaves an untracked new key. An operator running from another directory loses the log. | **Fix:** add a `trap … ERR` that logs the failed step and the IDs; use an absolute log path. **Repro (not executed):** stub line 12's `vault write` to fail; observe the "created new key" entry with no completion or error entry. | a✓ b✓ c✗ d✗ |

Siblings for F1–F3:
- **Root cause searched:** destructive or state-changing steps that are not gated on the success of the steps before them, and state that is never updated.
- **Found:** `deploy push` success is taken as rollout completion (N2), and line 12's purpose is unclear (N3). There are no other deletes or writes.
- **Security:** none of F1–F3 is a security finding. The operator is the only principal, and no trust boundary is crossed. They are availability and correctness defects in a production payments path.

NEEDS VALIDATION:
- **N1 (line 10):** whether `vault write -field=key_id … generate=true` can succeed and print nothing. If so, `NEW_ID` is empty, the run continues, and it deploys `signing/`. This is settled by the backend's write response schema. Guard with `[[ -n "$NEW_ID" ]]`.
- **N2 (line 17):** whether `deploy push --restart rolling` returns when the rollout completes or when it starts. This is settled by the deploy CLI documentation.
- **N3 (line 12):** whether `vault write …/new/value read=true` overwrites data at that path. On a KV engine, `write` replaces the secret's data with `{read: true}`. It is also unclear why a "read" is a write. This is settled by the engine type and the line's intent.
- **N4:** paths are inconsistent. The key is created at `…/signing/new`, deleted at `…/signing/$OLD_ID` and deployed as `signing/$NEW_ID`. Whether the new key is actually stored at `signing/$NEW_ID` is settled by the backend's path layout.

REFUTED:
- **C2:** `set -euo pipefail` (line 2) aborts on any failing command, including the command substitutions in the assignments on lines 8 and 10, before line 14 runs.
- **C3:** line 12's stdout goes to `/dev/null`, and lines 11, 15 and 18 log key IDs only.
- **Partial correction to C1:** the vault delete alone does not stop running instances signing, since they likely hold the key in memory. The confirmed harm is the irreversible window and the failure path (F3).

WHAT HOLDS UP:
- Strict shell mode stops the script at the first failing command.
- No secret material reaches the terminal, the log or the command arguments.
- Variables are quoted, and a missing argument is caught by `-u`.

UNVERIFIED CLAIMS:
- **"No downtime"** (implied by the request): unsupported. Confirming it needs the customer key-distribution mechanism and a staged test against a mixed fleet.
- **Author's C2 and C3 refutations:** they are correct by shell semantics, but were not executed. Confirm by running with stub CLIs in an isolated sandbox.

QUESTIONS FOR THE AUTHOR:
1. How do customers obtain the verification key? Fetched from an endpoint, shared out of band, or something else? Can they accept two keys at once, or a key ID in the header?
2. What reads `secret/$SERVICE/signing`, and who is meant to update it?
3. Does `deploy push` block until the rollout completes?
4. What is the webhook retry window?

DECISION-MAKER SUMMARY: Do not run this in production. Of the three first-pass findings, the delete-before-deploy ordering is real, and the other two do not hold. The review also found that the script never makes the new key current and gives customers no window in which both keys verify. Running it as is risks failed webhook verification for customers during and after rotation, and leaves no way to restore the old key if the deploy fails.

OWNER SUMMARY: The key-rotation script removes the old key before the new one is in place and never records which key is current. Customers could therefore reject our payment notifications while it runs, or afterwards. It needs a step-by-step rework, where the old key is kept until everyone has switched over, before it is safe to use.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "README.md", "status": "seen", "matters": false},
    {"item": "candidates.md", "status": "seen", "matters": true},
    {"item": "rotate_key.sh", "status": "seen", "matters": true},
    {"item": "second_pass.md", "status": "seen", "matters": true},
    {"item": "vault secrets-engine semantics", "status": "not_seen", "matters": true},
    {"item": "deploy CLI documentation", "status": "not_seen", "matters": true},
    {"item": "customer key-distribution mechanism", "status": "not_seen", "matters": true},
    {"item": "webhook retry policy", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "README.md", "kind": "document"},
      {"unit": "candidates.md", "kind": "document"},
      {"unit": "second_pass.md", "kind": "document"},
      {"unit": "rotate_key.sh", "kind": "file"},
      {"unit": "rotate_key.sh:2 set -euo pipefail semantics", "kind": "assumption"},
      {"unit": "rotate_key.sh:11-18 output and log redirection", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "runtime execution of rotate_key.sh", "reason": "no_tools"},
      {"unit": "vault backend and deploy CLI behaviour", "reason": "not_supplied"},
      {"unit": "customer key-distribution mechanism", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:8 (pointer read, never written)",
     "scenario": "After a successful run, secret/$SERVICE/signing still names the deleted OLD_ID; consumers of the current key and the next rotation get a deleted key while instances sign with NEW_ID.",
     "fix": "After the rollout is verified, write NEW_ID to secret/$SERVICE/signing; retire OLD_ID only afterwards.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed (no tools). In an isolated copy with stub vault/deploy CLIs, run rotate_key.sh svc, then vault read -field=key_id secret/svc/signing: expected NEW_ID, observed OLD_ID.",
     "security": false,
     "siblings_searched": {"searched": "every vault write/delete and deploy step in rotate_key.sh for state left un-updated or ungated", "found": "N2 (deploy success assumed), N3 (line 12 write semantics); no other pointer writes"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:17 (--restart rolling); no publish or overlap step anywhere",
     "scenario": "During the rolling restart, old and new instances sign with different keys while customers verify with one current key; one group's webhooks fail verification, and retries signed with the old key fail after it is retired.",
     "fix": "Phase the rotation: create the key, publish it so customers accept both (or carry a key id in the header), deploy and wait for completion, switch the pointer, retire the old key after the maximum retry window.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Not executed (no tools). With stub CLIs, simulate N instances restarted one by one; at each step verify every instance's signature with the single published key; expect 0 failures, observe failures at every mixed step.",
     "security": false,
     "siblings_searched": {"searched": "all steps that change which key signs or verifies", "found": "F1 (pointer never switched), F3 (old key retired too early)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:14 runs before rotate_key.sh:17",
     "scenario": "deploy push fails; set -e exits after the delete; the old key is gone, the new key is not deployed, the pointer names a deleted key, and restarting instances have no valid key, with no rollback.",
     "fix": "Move the delete to the end, gated on a verified rollout and the retry window; add a trap reporting partial state.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Not executed (no tools). Stub deploy to exit 1; run in an isolated copy; observe the 'deleted old key' log line and secret/svc/signing/$OLD_ID absent, with no 'deployed' line.",
     "security": false,
     "siblings_searched": {"searched": "other irreversible steps preceding a success check in rotate_key.sh", "found": "none besides line 14; deploy completion itself unverified (N2)"}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:11-18",
     "scenario": "An abort at line 12 or 17 leaves an orphaned new key, and the relative rotation.log records only successes, not the failed step.",
     "fix": "Add trap ERR that logs the failed step and the IDs; use an absolute log path.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed (no tools). Stub line 12's vault write to fail; observe the 'created new key' entry with no completion or error entry."},
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:10",
     "suspicion": "A successful write could print an empty key_id, so the run continues with an empty NEW_ID.",
     "unresolved_fact": "Whether the backend always returns key_id from a write with generate=true."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:17",
     "suspicion": "deploy push may return before the rolling restart completes.",
     "unresolved_fact": "The deploy CLI's completion semantics."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:12",
     "suspicion": "A 'read' implemented as vault write may overwrite data at .../new/value with {read: true}.",
     "unresolved_fact": "The secrets-engine type and the intent of line 12."},
    {"id": "N4", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:10,14,17",
     "suspicion": "Create, delete and deploy use inconsistent paths (signing/new vs signing/$ID).",
     "unresolved_fact": "Whether the backend stores the generated key at signing/$NEW_ID."}
  ],
  "refuted": [
    {"id": "C2", "candidate": "A failed vault command does not stop the script, which goes on to delete the old key.",
     "evidence": "set -euo pipefail at line 2 aborts on any failing command, including the command substitutions in the plain assignments on lines 8 and 10, before line 14."},
    {"id": "C3", "candidate": "The new secret value is printed to the terminal and logged.",
     "evidence": "Line 12 sends stdout to /dev/null; lines 11, 15 and 18 log key IDs only; no secret appears in arguments."}
  ]
}
```