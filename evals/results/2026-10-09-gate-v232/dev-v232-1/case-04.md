**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools and no subagent. I read the first reviewer's candidates and the author's reply before forming my own view, so I may be anchored on them.

VERDICT: **REWORK.** The script deletes the old key before the new one is deployed and never updates the "current key" pointer. No reordering of lines can deliver the zero-downtime rotation that was asked for, because nothing lets the old and new keys be valid at the same time.

CONFIDENCE: **medium.** Three things limit it: this is a same-context review with no tools; the semantics of the `vault` and `deploy` CLIs are unverified; and nothing was supplied on how customers obtain the "current" key.

INPUTS LEDGER:
- Seen: request.md, context.md, README.md, candidates.md, rotate_key.sh, second_pass.md.
- Not seen, and it matters:
  - How customers get the current key (public key endpoint, shared secret sent by email, or a portal). This settles the customer-impact half of F1, F2 and F4.
  - What the `secret/` mount is. Fields like `generate=true` and `read=true` are not standard Vault KV behaviour.
  - Whether `deploy push --restart rolling` waits until the rollout is complete before returning.
  - Whether running instances keep the key in memory or re-read it from the vault.
- Not seen, does not matter: no prior script versions, no CI.

COVERAGE:
- Scope: the whole of rotate_key.sh, plus the candidates and the author's replies.
- Checked: every line of rotate_key.sh (1–18); C1, C2 and C3 against those lines; second_pass.md; README.md; request.md against the design.
- Not checked: the CLI behaviour and the customer key distribution (`not_supplied`). The script was not executed (README says not to, and I have no tools).

SEATS AND GATE: Only the local same-context reviewer ran. The work contains no secrets or personal data, so the sensitivity gate passed. Cross-vendor seats were not run because there were no tools and the user did not ask for them. README's "not to be executed" is a legitimate operating constraint consistent with the skill, not an injection.

## Confirm-or-refute round on C1–C3

- **C1: survives.** It becomes F1, at High, with evidence PROBABLE rather than CONFIRMED.
  - The ordering is a fact: the `vault delete` at line 14 runs before the `deploy push` at line 17.
  - The claimed mechanism, "running instances still sign with the old key, which no longer exists", is overstated. Instances that already hold the key in memory can keep signing with it.
  - The real damage is elsewhere:
    - any instance that starts or restarts before the rollout reaches it cannot load `signing/$OLD_ID`;
    - any customer or verifier that looks up the old key for in-flight calls or retries finds nothing;
    - there is no rollback if the deploy fails (see F2).
- **C2: refuted, as the author said.**
  - `set -euo pipefail` is at line 2.
  - A failing `$(...)` in a plain assignment (lines 8 and 10) causes an exit under `-e`.
  - The bare `vault write` and `vault delete` at lines 12 and 14 also exit on failure.
  - A failed vault command before line 14 therefore never reaches the delete.
  - What remains of the concern is different and is filed separately: a failure *after* the delete (F2), and a vault command that succeeds but prints empty output (S1).
- **C3: refuted.**
  - Line 12 sends stdout to `/dev/null`.
  - Lines 11, 15 and 18 log only `$NEW_ID` and `$OLD_ID`, which come from `-field=key_id`.
  - Nothing writes the secret value to rotation.log or to the terminal's stdout.
  - What is left is a stderr question (S3), which is not a finding.

## FINDINGS

**F1. High · PROBABLE · Track B · rotate_key.sh:14 versus :17 · a/b/c/d = Y/N/Y/Y**
- **What is wrong:** The old key is deleted before the new key is deployed, and before the rolling restart finishes.
- **Failure scenario:** During the rolling restart, an instance that crashes or scales out still has `signing/$OLD_ID` configured and fails to load it. Webhooks signed with the old key, or retried from earlier calls, cannot be verified against a key that has been removed.
- **Fix:** Order the steps as create, deploy, wait for the rollout to complete, and only then delete. Delete only after a grace period that is longer than the maximum webhook retry window.
- **Reproduction:** In a scratch directory with no network, put stub `vault` and `deploy` scripts on PATH that append their argv to calls.txt. Run `rotate_key.sh svc`. Expected: `deploy push` appears before `vault delete`. Observed by static trace: the delete is at line 14 and the deploy at line 17. Not executed.

**F2. High · PROBABLE · Track B · rotate_key.sh:14–17 (failure path) · a/b/c/d = Y/N/Y/Y**
- **What is wrong:** If `deploy push` fails, `set -e` exits right after the old key has already been deleted. Nothing restores it.
- **Failure scenario:** The deploy CLI times out or rejects the push. The service keeps running with config that points at `signing/$OLD_ID`, which is now deleted, and the new key was never deployed. Any restart then cannot load a signing key, so webhooks stop.
- **Fix:** Delete last. Add a `trap` that logs the state and does not delete on failure.
- **Reproduction:** Make the stub `deploy` `exit 1`. Run the script. Observed by trace: the exit code is non-zero, calls.txt contains `vault delete secret/svc/signing/<old>`, and there is no successful deploy.
- **Sibling:** same root cause as F1 (a destructive step before a confirmed deploy). Logged separately because it has its own location and scenario.

**F3. High · CONFIRMED · Track B · rotate_key.sh:8 (read), with no write anywhere · a/b/c/d = Y/Y/N/Y**
- **What is wrong:** The script reads the current key id from `secret/$SERVICE/signing` but never writes `NEW_ID` back to it.
- **Failure scenario:**
  - After a run, the "current" pointer still names the old key, which has been deleted.
  - On the next run, `OLD_ID` is that same deleted id. Depending on the CLI, deleting it again either does nothing, so the previous key is never retired, or errors out after a new key was already created, so the rotation is wedged.
  - Anything that resolves "the current key" from this path gets a dangling id.
- **Fix:** After the rollout completes, atomically update `secret/$SERVICE/signing key_id=$NEW_ID`. Read it back and assert it before deleting the old key.
- **Reproduction:** Use a stub `vault` backed by a file. Run the script twice. Observed by trace: the second run's `OLD_ID` equals the first run's `OLD_ID`.

**F4. High · PROBABLE · Track A/B (drift) · whole design: lines 10–18 · a/b/c/d = Y/N/Y/Y**
- **What is wrong:** The request is "no downtime" with customers verifying against "the key that is current when they receive the call". With a single active key and a rolling restart, some instances sign with the new key while others still sign with the old one. Nothing publishes the new key to customers, and nothing provides an overlap window: no dual signing, no key id in the signature header, and no period where verifiers accept both keys.
- **Failure scenario:** During any rotation, a share of webhooks equal to the share of not-yet-restarted instances fails customer verification. This happens even after F1 is fixed.
- **Fix:**
  1. Publish the new key to customers (for example JWKS or the portal) before signing with it.
  2. Sign with a `kid` in the header, or sign with both keys during the overlap.
  3. Switch signing to the new key.
  4. Wait out the retry window.
  5. Retire the old key.
- **Reproduction (design-level):** With two stub instances, one restarted and one not, verify each signature against the one "current" key: one of the two fails. Static trace only.
- **Siblings searched:** I looked for any publish, overlap or `kid` step anywhere in the script and found none.

Security assessment for F1–F4: none of them is a security finding, because no lower-trust principal crosses a boundary. They are availability and correctness failures on a production payments path.

**F5. Low · CONFIRMED · Track B · rotate_key.sh:10–14**
- **What is wrong:** If the script fails after line 10, the newly generated key is left orphaned. There is no cleanup and no lock against two concurrent runs.
- **Fix:** Add a `trap` that records orphans, and take a lock (for example `flock`).
- **Reproduction:** Make the stub `vault delete` fail. Observed by trace: a new key exists that was never deployed or recorded as current.

## NEEDS VALIDATION
- **S1 (rotate_key.sh:8, :14):** If `vault read -field=key_id` exits 0 but prints nothing, line 14 becomes `vault delete secret/$SERVICE/signing/`. That could delete the parent path.
  - Settles it: the CLI's behaviour when the field is missing or empty.
  - Regardless of the answer, add a guard `[[ -n "$OLD_ID" && -n "$NEW_ID" ]]`.
- **S2 (lines 10, 12):** `generate=true`, `-field=key_id` on a write, and `read=true` are not standard Vault KV behaviour. Line 12's purpose is unclear: it writes a field to `.../new/value`.
  - Settles it: documentation for the `secret/` engine. If this is plain KV, line 10 fails because the write returns no `key_id`, and the script exits early.
  - Also unclear: the key is created at `signing/new`, while the delete and deploy use `signing/<id>`. Whether those paths refer to the same key is unknown.
- **S3 (line 12):** stdout is discarded but stderr is not. If the CLI echoes the value on stderr, or prints a warning that includes it, the value reaches the terminal.
  - Settles it: the CLI's stderr behaviour for `read=true`.
- **S4 (line 17):** Whether `deploy push --restart rolling` blocks until the rollout is complete.
  - Settles it: the deploy CLI documentation. This matters for any fix to F1.

## REFUTED
- **C2:** `set -euo pipefail` at line 2 stops the script on any failing vault command before line 14. This includes the assignments at lines 8 and 10, because a plain assignment takes the substitution's exit status.
- **C3:** Line 12 discards stdout, and lines 11, 15 and 18 log only ids taken from `-field=key_id`. The secret value is never logged or printed to stdout.
- **C1 as worded:** the claim that running instances fail to sign because the key is gone is not supported. The finding survives as F1, with the mechanism restated.

WHAT HOLDS UP:
- Strict mode is set.
- `$1` is guarded by `-u`.
- Only key ids are logged.
- Line 12's stdout is discarded.
- The author's rebuttals of C2 and C3 are correct.

UNVERIFIED CLAIMS:
- The usage note's claim that "the vault CLI and deploy CLI" support these flags. Confirm with the CLI docs.
- That the rolling restart achieves "no downtime". Confirm from the deploy CLI's semantics and a staging rotation.

QUESTIONS FOR THE AUTHOR:
1. How do customers obtain the current key, and do your signatures carry a key id?
2. What is the `secret/` engine, and what does line 12 do?
3. Does `deploy push` block until the rollout is complete?
4. What is the maximum webhook retry window?

DECISION-MAKER SUMMARY: Do not run this against production payments. Even with the delete moved last, it has no overlap window, never updates the current-key pointer, and leaves the service without a loadable key if the deploy fails. Rework it into a publish, overlap, switch and retire sequence, then test it in staging with a deliberately failing deploy.

OWNER SUMMARY: The key-rotation script is not safe to use yet. It removes the old key too early, never records which key is now current, and gives customers no window in which both the old and new keys work, so payment notifications could fail to verify during or after a rotation. The two specific worries raised about error handling and secret leakage turned out to be unfounded.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "customer key distribution mechanism", "status": "not_seen", "matters": true},
    {"item": "secret/ engine and vault/deploy CLI semantics", "status": "not_seen", "matters": true},
    {"item": "README.md, candidates.md, rotate_key.sh, second_pass.md, request.md, context.md", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "no secrets, personal or client data in the work"},
  "coverage": {
    "checked": [
      {"unit": "rotate_key.sh", "kind": "file"},
      {"unit": "candidates.md", "kind": "document"},
      {"unit": "second_pass.md", "kind": "document"},
      {"unit": "README.md", "kind": "document"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "vault/deploy CLI behaviour", "reason": "not_supplied"},
      {"unit": "execution of rotate_key.sh", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:14 vs :17",
     "scenario": "Old key is deleted before the new key is deployed; during the rolling restart, instances that restart or scale out cannot load signing/$OLD_ID, and in-flight or retried webhooks signed with the old key cannot be verified.",
     "fix": "Create, deploy, wait for rollout completion, then delete the old key after a grace period longer than the webhook retry window.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Put stub vault/deploy on PATH in a no-network scratch dir, logging argv to calls.txt; run rotate_key.sh svc; expected deploy before delete, observed (static trace) vault delete at line 14 precedes deploy push at line 17.",
     "security": false,
     "siblings_searched": {"searched": "every destructive step relative to the deploy, including the failure path", "found": "F2 (deploy failure after delete)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:14-17",
     "scenario": "deploy push fails; set -e exits after the old key was deleted and before the new key was deployed; the next restart cannot load any signing key and webhooks stop.",
     "fix": "Move the delete after a verified rollout; add a trap that never deletes on failure and logs the state.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Stub deploy exits 1; run the script; calls.txt shows vault delete of the old key and the script exits non-zero with no successful deploy.",
     "security": false,
     "siblings_searched": {"searched": "other steps after the delete", "found": "only the deploy push and the log line"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:8 (read; no corresponding write)",
     "scenario": "secret/$SERVICE/signing key_id is never updated to NEW_ID; after a run the current pointer names a deleted key; the next run reads the same stale OLD_ID and either never retires the previous key or fails after creating another.",
     "fix": "After the rollout, write key_id=$NEW_ID to secret/$SERVICE/signing, read it back and assert it before deleting the old key.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Use a file-backed stub vault; run the script twice; the second run's OLD_ID equals the first run's OLD_ID.",
     "security": false,
     "siblings_searched": {"searched": "all vault write calls for a write to secret/$SERVICE/signing", "found": "none; writes go only to .../signing/new and .../signing/new/value"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "rotate_key.sh:10-18 (design)",
     "scenario": "With a single active key and a rolling restart, some instances sign with the new key and others with the old one, while customers verify against one current key; the share of webhooks from not-yet-restarted instances fails verification, even with F1 fixed. This drifts from the no-downtime request.",
     "fix": "Publish the new key to customers first, sign with a kid or dual-sign during an overlap window, switch signing, wait out the retry window, then retire the old key.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Two stub instances, one restarted and one not; verify both signatures against the single current key; one fails (static trace).",
     "security": false,
     "siblings_searched": {"searched": "the script for any publish, overlap or kid step", "found": "none"}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rotate_key.sh:10-14",
     "scenario": "A failure after line 10 leaves a generated key orphaned; there is no lock against concurrent runs.",
     "fix": "Add a trap that records orphaned keys and take a lock with flock.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Stub vault delete exits 1; after the run, a new key exists that is neither deployed nor recorded as current."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:8,14",
     "suspicion": "An empty OLD_ID with exit 0 makes line 14 delete secret/$SERVICE/signing/.",
     "unresolved_fact": "The vault CLI's behaviour for a missing or empty -field value."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:10,12",
     "suspicion": "generate=true, -field on write and read=true are non-standard; the signing/new path may not match signing/$NEW_ID.",
     "unresolved_fact": "Documentation of the secret/ engine."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:12",
     "suspicion": "The secret value may reach the terminal via stderr.",
     "unresolved_fact": "Whether the CLI writes the value to stderr."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "rotate_key.sh:17",
     "suspicion": "deploy push may return before the rolling restart completes.",
     "unresolved_fact": "Whether deploy push --restart rolling blocks until rollout completion."}
  ],
  "refuted": [
    {"id": "C2", "candidate": "A failed vault command does not stop the script and the delete still runs.",
     "evidence": "set -euo pipefail at line 2; failing command substitutions in plain assignments (lines 8, 10) and bare commands (line 12) exit before line 14."},
    {"id": "C3", "candidate": "The new secret value is printed to the terminal and to rotation.log.",
     "evidence": "Line 12 redirects stdout to /dev/null; lines 11, 15 and 18 log only key ids from -field=key_id."}
  ]
}
```