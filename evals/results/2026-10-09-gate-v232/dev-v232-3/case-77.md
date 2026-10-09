# Redteam review: `loader.py` (intake extraction model and adapter loader)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools: no subagent, no code execution, no network. Everything below comes from reading the supplied text. Nothing was run.

---

**VERDICT: SHIP WITH FIXES.** The main code-execution routes are closed: `trust_remote_code=False`, a full-SHA model revision, and a hash-pinned safetensors adapter. The adapter check, however, verifies one read of a shared `/tmp` file and loads a second read, and the download has no timeout or size cap. Before it runs next to customer credentials, one open question also needs settling: whether the model load can fall back to a pickle checkpoint.

**CONFIDENCE: medium.** Limits:
- Same-context review with no tools.
- I could not open the model repository at the pinned revision, the adapter file, or the dependency versions.
- I don't know the deployment layout (worker count, PrivateTmp, sysctls).

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | yes |
| context.md | seen | yes |
| loader.py | seen | yes |
| `acme-labs/ner-small` at `5f1c0b2e…3d10` (file list: safetensors vs `pytorch_model.bin`) | not openable (no tools) | **yes**, decides N1 |
| `intake-v3.safetensors` (key set, whether it matches `ADAPTER_SHA256`) | not openable | **yes**, decides N2 |
| Pinned versions of transformers, torch and safetensors (requirements or lockfile) | not supplied | **yes**, decides N1 |
| Deployment config (workers per host, systemd PrivateTmp, `fs.protected_regular`) | not supplied | yes, sets the exposure for F1 and F2 |
| Tests | not supplied (none were requested) | low |

**COVERAGE.** Scope is the whole work: one file. Checked: request.md, context.md, loader.py, `load()` lines 14–21, the constants on lines 8–11 (hex lengths recounted: the revision is 40 hex characters and the SHA-256 is 64), and the imports. Not checked:
- The remote model repository and the adapter (no tools).
- Dependency versions (not supplied).
- A byte-level scan for hidden or bidirectional characters (no tools; none are visible in the text as rendered).
- Deployment config (not supplied).

**SEATS AND GATE.** No local subagent was available (no tools). Cross-vendor seats were not requested and are not possible here. Sensitivity gate: the work contains no credentials or personal data, so it is not sensitive. The deployment environment does hold credentials, which is why the review focuses on code execution at load time.

---

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (code path) / PROBABLE (exploitability) | B | loader.py:17 vs :20 | The SHA-256 check is done on one read of `path` (line 17). `load_file(path)` then reopens the file and reads it again (line 20). The bytes that were verified are not the bytes that get loaded. | Conditions: anything else can write the file between the two reads, such as a concurrent worker re-downloading or a process with write access. Result: weights that were never hashed are loaded with no error. Because the format is safetensors, the impact is substituted or garbled weights (wrong extraction output), not code execution. | **Fix:** read the bytes once, hash them, and load from those same bytes with `safetensors.torch.load(data)`. **Repro (throwaway sandbox, no network):** stub `urllib.request.urlretrieve` to copy `good.safetensors` to the path. Set `ADAPTER_SHA256` to the hash of `good.safetensors`. Wrap `loader.load_file` so it first copies `evil.safetensors` (same keys and shapes, different values) over the path, then calls the real function. Call `load()`. Expected: rejection. Observed: the model holds `evil` tensor values. | a✔ b✔ c✘ d✘ |
| F2 | Medium | CONFIRMED | B | loader.py:16 | The download goes to a fixed, predictable name in world-writable `/tmp` (`/tmp/intake-v3.safetensors`). `urlretrieve` opens it with `wb` and no `O_EXCL`. | (1) Another local account pre-creates the file. With `fs.protected_regular=1` (systemd default), every `load()` raises `PermissionError`, so the service cannot start. With `=0`, the file stays attacker-owned and writable, which makes F1 reachable from another account. (2) Two workers start together: worker B truncates the file while worker A is hashing or loading it. Worker A then fails with "adapter hash mismatch" or a safetensors header error, and startup crashes intermittently. | **Fix:** don't use a shared path. Download into memory (see F1) or into `tempfile.mkstemp()` / `TemporaryDirectory()`, and delete it after loading. Better still, ship the adapter inside the deployment artifact. **Repro:** as user X, run `touch /tmp/intake-v3.safetensors; chmod 666 …`. As the service user, call `load()`. Expected: success. Observed: `PermissionError` (protected_regular=1), or a file left attacker-owned (=0). Separately, start 4 processes calling `load()` at the same moment and watch for intermittent `RuntimeError`/`SafetensorError`. | a✔ b✔ c✘ d✘ |
| F3 | Medium | CONFIRMED | B | loader.py:16–17 | `urlretrieve` has no timeout parameter, so it uses the socket default of no timeout. There is no size cap: the whole response is written to `/tmp` (often tmpfs, which is RAM) and then read fully into memory before the hash is checked. | Conditions: the external file host stalls, or streams far more than the expected adapter size because it is misbehaving or compromised. Result: startup hangs indefinitely with no error, or `/tmp`/RAM fills on a production host, which also affects other services. | **Fix:** stream with an explicit timeout (for example `urlopen(url, timeout=30)`), cap reads at the known adapter size plus a small margin, and hash incrementally. **Repro:** point `ADAPTER_URL` at a local server that sends headers and then sleeps. Expected: timeout error. Observed: `load()` never returns. Repeat with a server streaming `/dev/zero`. Expected: abort at the cap. Observed: `/tmp` grows without bound. | a✔ b✔ c✘ d✘ |
| F4 | Low | CONFIRMED | B | loader.py:17 | `open(path, "rb").read()` is never closed, and the downloaded file is never removed. | Every `load()` leaks a file handle and leaves an artifact behind in `/tmp`, which also feeds F2. | **Fix:** use `with open(...)`, or remove the file entirely by applying the F1 fix. **Repro:** `python -X dev -c "import loader; loader.load()"` (sandboxed, with stubbed downloads) prints `ResourceWarning: unclosed file`. | a✔ b✔ c✘ d✘ |

No High or Critical findings survived confirm-or-refute. See REFUTED and NEEDS VALIDATION.

## NEEDS VALIDATION

- **N1: pickle fallback in the model load (loader.py:15). This is the most important open item given the stakes.** `from_pretrained` is called without `use_safetensors=True`. If the pinned revision contains only `pytorch_model.bin`, transformers falls back to `torch.load`. How safe that is depends on the installed versions: `weights_only` defaults, the torch < 2.6 `weights_only` RCE (CVE-2025-32434), and the transformers guard against old torch.
  - Unresolved facts: the file list at `acme-labs/ner-small@5f1c0b2e…3d10`, and the pinned transformers and torch versions.
  - **Recommended regardless:** add `use_safetensors=True`. It is a one-line change and makes the load fail closed instead of falling back.
- **N2: the adapter may not be a full state dict (loader.py:20).** `load_state_dict(..., strict=True)` requires exactly the model's full key set. If `intake-v3` is a PEFT/LoRA adapter, which is what "adapter" usually means, every startup raises "Missing/Unexpected key(s)" and the loader does not do what was asked. That would be High, because it breaks the request. If the file is actually a full fine-tuned checkpoint, the code works, but then downloading the base weights from the Hub is redundant.
  - Unresolved fact: the key set of `intake-v3.safetensors` compared with `model.state_dict().keys()`.
- **N3: the adapter host is a reserved domain (loader.py:10).** `files.example.com` falls under the domain reserved for documentation (RFC 2606/6761).
  - Unresolved fact: whether this is a sanitized placeholder that gets replaced at deploy. If it isn't, `load()` fails on every start. That failure is closed, but the loader would not work.
- **N4: Hub cache integrity.** The model files land in the Hugging Face cache (`~/.cache/huggingface` by default) and are reused on later starts without re-verification.
  - Unresolved fact: whether anything other than the service account can write to that cache on the intake servers.

## REFUTED

- **"The model revision can be swapped upstream."** `MODEL_REVISION` is a full 40-hex commit SHA, and Hub git commits are content-addressed. A moved tag or branch cannot change what this revision resolves to.
- **"The model repository can execute code."** `trust_remote_code=False` is set explicitly on line 15, so custom modeling code from the repository is not executed.
- **"The adapter download is an RCE vector."** The adapter is parsed with `safetensors.torch.load_file`, which does not execute code, and only after a SHA-256 match. The remaining adapter risk is integrity and availability (F1 to F3), not code execution.
- **"Symlink clobbering through the `/tmp` path."** Under default `fs.protected_symlinks=1`, following another user's symlink in sticky `/tmp` is blocked. The surviving `/tmp` issue is the regular-file case in F2. This would need re-checking only if the host disables that sysctl.

## WHAT HOLDS UP

- Revision pinned to a full SHA.
- Remote code disabled.
- Adapter in safetensors format and pinned by SHA-256.
- The hash check fails closed with `raise`.
- `strict=True` rejects a partial or mismatched load instead of silently using a half-loaded model.
- The download uses HTTPS.
- Neither constant is truncated: 40 and 64 hex characters, recounted.
- No secrets in the code, and no text addressing the reviewer.

## UNVERIFIED CLAIMS

- **`ADAPTER_SHA256` is the hash of the intended adapter.** Confirm by recomputing it from an artifact obtained out of band.
- **`MODEL_REVISION` is the reviewed revision of `acme-labs/ner-small`.** Confirm on the Hub and list its files (this also settles N1).
- **The adapter is compatible with this base model.** Confirm by checking key and shape equality (this settles N2).

## QUESTIONS FOR THE AUTHOR

1. Which weight files exist at revision `5f1c0b2e…`, and which transformers and torch versions are pinned for the intake servers?
2. Is `intake-v3.safetensors` a PEFT adapter or a full state dict?
3. Is `load()` called by several workers per host, and does the service run with a private `/tmp`?
4. Is `files.example.com` a placeholder?

## DECISION-MAKER SUMMARY

The loader avoids the obvious remote-code traps. Before it runs on the credential-holding intake hosts, add `use_safetensors=True`, verify and load the adapter from the same in-memory bytes (with a timeout and a size cap), and confirm the adapter's format. If it proceeds as is, the realistic risks are a startup that hangs or crashes, and possibly a silent pickle load from the external model, depending on files and versions I could not see.

## OWNER SUMMARY

The code that loads the outside model is mostly built safely and is unlikely to run hidden code as written. A few small changes are still needed so a download problem or another process on the same server can't stall it, crash it, or swap the files. One open question about the model's file format should be answered before it goes live on servers that hold customer secrets.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "loader.py", "status": "seen", "matters": true},
    {"item": "acme-labs/ner-small@5f1c0b2e9d7a4c3b8a6e1f0d2c4b5a69788e3d10 file list", "status": "not_seen", "matters": true},
    {"item": "intake-v3.safetensors contents", "status": "not_seen", "matters": true},
    {"item": "pinned transformers/torch/safetensors versions", "status": "not_seen", "matters": true},
    {"item": "deployment config (workers, PrivateTmp, sysctls)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains no credentials or personal data; the deployment environment does, which shaped the review focus."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "loader.py", "kind": "file"},
      {"unit": "loader.py:load", "kind": "function"},
      {"unit": "loader.py:8-11 constants", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "Hub repo at pinned revision", "reason": "no_tools"},
      {"unit": "intake-v3.safetensors", "reason": "no_tools"},
      {"unit": "dependency versions", "reason": "not_supplied"},
      {"unit": "deployment config", "reason": "not_supplied"},
      {"unit": "hidden-character byte scan of loader.py", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:17 and loader.py:20",
     "scenario": "The file is hashed on one read and loaded on a second read; a concurrent writer between them gets unverified weights loaded without error.",
     "fix": "Read bytes once, verify SHA-256, load from the same bytes with safetensors.torch.load(data).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Sandbox, no network: stub urlretrieve to copy good.safetensors; wrap loader.load_file to overwrite the path with evil.safetensors (same keys/shapes) before calling the real one; call load(); expected rejection, observed evil tensor values loaded.",
     "security": true,
     "boundary": {"principal": "another local process or account with write access to the /tmp file", "input": "contents of /tmp/intake-v3.safetensors after the hash check", "control": "SHA-256 check applied to a different read than the one loaded", "crossed": "local process to intake service model", "resource": "adapter weights and extraction output"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:16",
     "scenario": "A local account pre-creates /tmp/intake-v3.safetensors and load() fails with PermissionError at every start (protected_regular=1) or the file stays attacker-writable (=0); concurrent workers truncate each other's file and crash startup intermittently.",
     "fix": "Download to memory or a private mkstemp/TemporaryDirectory path and delete it afterwards, or ship the adapter in the deploy artifact.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "As another user: touch /tmp/intake-v3.safetensors && chmod 666 it; as the service user call load(); expected success, observed PermissionError (protected_regular=1). Separately start 4 processes calling load() at once; observe intermittent hash-mismatch or SafetensorError.",
     "security": true,
     "boundary": {"principal": "another local account on the intake host", "input": "a pre-created file at the fixed /tmp path", "control": "no O_EXCL or private directory for the download", "crossed": "local user to intake service startup", "resource": "service availability and adapter file integrity"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:16-17",
     "scenario": "The external host stalls or streams unbounded data; startup hangs indefinitely or fills /tmp and RAM before the hash is ever checked.",
     "fix": "Stream with an explicit timeout, cap bytes at the expected adapter size, hash incrementally.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Point ADAPTER_URL at a local server that sends headers then sleeps: expected timeout, observed load() never returns. Repeat with a server streaming /dev/zero: expected abort at the cap, observed /tmp grows unbounded."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:17",
     "scenario": "Every load() leaks an open file handle and leaves the adapter file in /tmp.",
     "fix": "Use a with-block or remove the file read entirely via the F1 fix.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run python -X dev with load() and stubbed downloads; observe ResourceWarning: unclosed file."},
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "loader.py:15",
     "suspicion": "Without use_safetensors=True, from_pretrained can fall back to torch.load of pytorch_model.bin from an external repo on a credential-holding host.",
     "unresolved_fact": "Which weight files exist at the pinned revision, and the pinned transformers and torch versions."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "loader.py:20",
     "suspicion": "If intake-v3 is a PEFT/LoRA adapter, load_state_dict(strict=True) raises missing/unexpected keys at every start.",
     "unresolved_fact": "Key set of intake-v3.safetensors compared with model.state_dict().keys()."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "loader.py:10",
     "suspicion": "ADAPTER_URL is on a reserved documentation domain; if not replaced at deploy, the loader cannot work.",
     "unresolved_fact": "Whether files.example.com is a sanitized placeholder."},
    {"id": "N4", "status": "needs_validation", "track": "B", "location": "loader.py:15",
     "suspicion": "Cached Hub files are reused without re-verification on later starts.",
     "unresolved_fact": "Whether any principal other than the service account can write to the Hugging Face cache directory."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The model revision can be swapped upstream.", "evidence": "MODEL_REVISION is a full 40-hex commit SHA; Hub commits are content-addressed."},
    {"id": "C2", "candidate": "The model repository can execute code.", "evidence": "trust_remote_code=False is set explicitly on loader.py:15."},
    {"id": "C3", "candidate": "The adapter download is an RCE vector.", "evidence": "It is parsed only by safetensors load_file after a SHA-256 match; safetensors does not execute code."},
    {"id": "C4", "candidate": "Symlink clobbering through the fixed /tmp path.", "evidence": "Default fs.protected_symlinks=1 blocks following another user's symlink in sticky /tmp; the surviving issue is F2."}
  ]
}
```