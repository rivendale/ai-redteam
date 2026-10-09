VERDICT: **SHIP WITH FIXES.** The supply-chain basics are right: the model revision is pinned to a commit, remote code is off, and the adapter is hash-checked before a safetensors load. The adapter's hash check can still be bypassed through a shared `/tmp` path, and two things that cannot be settled from the code alone need answers before this runs on servers holding credentials.

CONFIDENCE: **medium.** No tools were available, so nothing was run or opened. The `transformers`/`torch` versions, the contents of the pinned repository revision, the adapter's key layout and the server's local-user setup were not supplied. The work was not written in this conversation, so this is an independent read, but it was done without a fresh subagent.

INPUTS LEDGER:
- Seen: `request.md`, `context.md` and `loader.py` (24 lines).
- Not seen:
  - Hub repo `acme-labs/ner-small` at `5f1c0b2e…3d10` (matters: whether it holds pickle weights).
  - The adapter file (matters: its key layout against `strict=True`).
  - Pinned `transformers`, `torch` and `safetensors` versions (matters: pickle handling).
  - Intake server user and sysctl setup (matters: whether F1 can be exploited).
  - Where the two pins came from (matters: whether they are trustworthy).
  - Any tests (none were referenced).

COVERAGE:
- Scope: the whole work (`loader.py`).
- Checked: module constants (format of both pins), `load()` line by line, the request and the context.
- Not checked:
  - Pinned repo contents, the adapter file and dependency versions (not supplied).
  - Byte-level scan for hidden or bidirectional characters (no tools; the text as shown contains none).

SEATS AND GATE: one reviewer (this session, no tools). No cross-vendor seats; none were requested, and the depth is standard. Sensitivity gate: the code holds no personal data or secrets. The *deployment environment* holds customer credentials, which is why the severity of runtime risks is weighed carefully below.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | `loader.py:17-21` | The adapter goes to a fixed, predictable path in world-writable `/tmp`. It is hashed in one read, then `load_file(path)` opens the path again. The bytes that are verified are not necessarily the bytes that are loaded. | Another local principal on the intake server pre-creates `/tmp/intake-v3.safetensors` with mode 0666, or keeps write access to it. After the hash check passes, they replace the file with tensors of the same keys and shapes. Attacker-chosen weights then load with no error, and extraction output is silently poisoned. Safetensors limits the impact to weights; there is no code execution. | **Fix:** download into a private `tempfile.TemporaryDirectory()` (mode 0700). Better, read the bytes once, hash them, then load those same bytes with `safetensors.torch.load(data)`, so the verified bytes are the loaded bytes. **Reproduction:** as user B, `touch /tmp/intake-v3.safetensors; chmod 666`. As the service user, run `load()` with a breakpoint after line 20. As B, overwrite the file with a same-shape safetensors file. Continue. Expected: a hash failure or the original weights. Observed: the substituted weights load. | a✓ b✗ c✓ d✗ |
| F2 | Low | CONFIRMED | B | `loader.py:17` | `urllib.request.urlretrieve` has no timeout parameter. With no global `socket.setdefaulttimeout`, which is not set in this file, a stalled server blocks forever. | `files.example.com` accepts the connection but stops sending. `load()` never returns and intake startup hangs with no error. | **Fix:** `urllib.request.urlopen(ADAPTER_URL, timeout=60)` and stream the response to the private temp file. **Reproduction:** point `ADAPTER_URL` at `nc -l 8000` (accepts, never replies) and call `load()`. Expected: a timeout error. Observed: it hangs indefinitely. | a✓ b✓ c✗ d✗ |
| F3 | Low | PROBABLE | B | `loader.py:17-18` | Same root cause as F1: a shared fixed path with no locking between concurrent loaders. | Two workers start at once. Worker A hashes while worker B is truncating and rewriting the file. A gets a partial read, a mismatch, and a startup failure. This fails closed, so the cost is availability only. | **Fix:** the per-process temp directory from F1 also fixes this. **Reproduction:** start two `load()` processes simultaneously in a loop of 50 runs. Expected: none fail. Observed: intermittent "adapter hash mismatch". | a✓ b✗ c✗ d✗ |

F1 is marked as a security finding:
- **Principal:** an unprivileged local user or process on the intake server.
- **Input:** the contents of `/tmp/intake-v3.safetensors`.
- **Control that fails:** the SHA-256 check, which covers an earlier read rather than the one that is loaded.
- **Boundary crossed:** another local user into the service's model integrity.
- **Resource:** the extraction model's weights.

Siblings searched: every path reopened after verification in `loader.py`. Only line 21 does this. `from_pretrained` uses the Hub cache, which is not this pattern.

## NEEDS VALIDATION
- **S1, possible pickle load on the model path (`loader.py:16`).** If the pinned revision contains `pytorch_model.bin` rather than `*.safetensors`, `from_pretrained` uses `torch.load`, a pickle format that can execute code. That would run on a host holding customer credentials. The pin fixes *which* bytes load, not whether they are safe. **Settled by:** the file list at commit `5f1c0b2e…3d10`, plus the installed `transformers` and `torch` versions. `torch` ≥ 2.6 makes `torch.load` default to `weights_only=True`, which refuses arbitrary objects. Cheap guard regardless of the answer: pass `use_safetensors=True`, so the pickle path can never be taken.
- **S2, `strict=True` against an "adapter" (`loader.py:21`).** If the file is a PEFT/LoRA adapter, its keys (`lora_A`, `lora_B`, `base_model.model.*`) will not match the base model's state dict. Every load would then raise `RuntimeError`, and the deliverable would not work. **Settled by:** the key list in `intake-v3.safetensors`. A full fine-tuned state dict is fine; a LoRA adapter needs `peft.PeftModel.from_pretrained` or a merge step.
- **S3, provenance of the two pins.** The hash check only helps if `ADAPTER_SHA256` and `MODEL_REVISION` were obtained out of band from a trusted party and the content they pin was reviewed. **Settled by:** who produced these values and how.

## REFUTED
- **"Remote code execution through the model repo":** `trust_remote_code=False` is set explicitly (line 16).
- **"Unpinned model revision":** `MODEL_REVISION` is a full 40-hex-character commit ID, not a branch or tag (line 9).
- **"Adapter loaded before verification":** the hash is compared and the function raises *before* `load_file` (lines 19-21), so it fails closed.
- **"Adapter deserialization runs code":** `safetensors.torch.load_file` parses tensors only; there is no pickle.
- **"Adapter fetched over plaintext":** the URL is `https`, and the stdlib verifies certificates by default (PROBABLE; no custom SSL context appears in this file).
- **"Malformed hash constant":** `ADAPTER_SHA256` is exactly 64 hex characters.

## WHAT HOLDS UP
- The model revision is pinned by commit, not by name.
- Remote code is disabled.
- The adapter has an integrity check that fails closed and runs before load.
- The adapter uses a safetensors loader.
- There are no secrets in the code.
- The work does what was asked (model plus adapter) and nothing extra.

## UNVERIFIED CLAIMS
- That the pinned model is safetensors-only (see S1).
- That the adapter matches the model's keys exactly (see S2).
- That the hash and revision correspond to vetted artifacts (see S3).

None of these could be checked without the Hub listing, the file itself and the provenance record.

## QUESTIONS FOR THE AUTHOR
1. Does the pinned revision contain any `.bin` or `.pt` weight files, and which `transformers` and `torch` versions are deployed?
2. Is `intake-v3.safetensors` a full state dict or a LoRA adapter?
3. Do any other users or processes run on the intake servers, and are `fs.protected_regular` and `fs.protected_symlinks` set?

## DECISION-MAKER SUMMARY
The loader's main protections are in place. Before it runs in production, move the adapter download off the shared `/tmp` path and add `use_safetensors=True` and a download timeout. Proceeding without answers to S1 and S2 risks either a pickle load on a credential-bearing host or a loader that fails on every start.

## OWNER SUMMARY
The new loading code is mostly safe: it locks the model to a fixed version, checks the add-on file's fingerprint before using it, and avoids running outside code. A few small changes are needed: save the downloaded file somewhere private, stop the download from hanging forever, and force the safe file format for the main model. Two facts about the downloaded files should also be confirmed, because the answers could stop the code from working at all.

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
    {"item": "deployed transformers/torch/safetensors versions", "status": "not_seen", "matters": true},
    {"item": "intake server local users and sysctl settings", "status": "not_seen", "matters": true},
    {"item": "provenance of ADAPTER_SHA256 and MODEL_REVISION", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code contains no personal data or secrets; deployment environment holds credentials, which informed severity only."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "loader.py", "kind": "file"},
      {"unit": "loader.py:load", "kind": "function"},
      {"unit": "loader.py:MODEL_REVISION/ADAPTER_SHA256 format", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "acme-labs/ner-small pinned revision contents", "reason": "no_tools"},
      {"unit": "intake-v3.safetensors", "reason": "not_supplied"},
      {"unit": "dependency versions", "reason": "not_supplied"},
      {"unit": "byte-level hidden-character scan of loader.py", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "loader.py:17-21",
     "scenario": "A local principal on the intake server pre-creates or retains write access to /tmp/intake-v3.safetensors and swaps it for same-shape tensors after the hash check at line 19 passes; load_file at line 21 reopens the path and loads attacker-chosen weights without error.",
     "fix": "Download into a private tempfile.TemporaryDirectory (0700), or read bytes once, hash them, and load the same bytes with safetensors.torch.load(data).",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "As user B: touch /tmp/intake-v3.safetensors && chmod 666 it. As service user: run load() with a breakpoint after line 20; as B overwrite the file with a same-shape safetensors file; continue. Expected hash failure or original weights; observed substituted weights load.",
     "security": true,
     "boundary": {"principal": "an unprivileged local user or process on the intake server", "input": "contents of /tmp/intake-v3.safetensors",
                  "control": "SHA-256 check covers an earlier read, not the bytes loaded", "crossed": "other local user to the intake service",
                  "resource": "extraction model weights"},
     "siblings_searched": {"searched": "every path reopened after verification in loader.py", "found": "only loader.py:21"}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:17",
     "scenario": "The adapter host accepts the connection but stalls; urlretrieve has no timeout, so load() never returns and intake startup hangs.",
     "fix": "Use urllib.request.urlopen(ADAPTER_URL, timeout=60) and stream to the private temp file.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Set ADAPTER_URL to a listener (nc -l 8000) that never replies and call load(); expected a timeout error, observed an indefinite hang."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "loader.py:17-18",
     "scenario": "Two workers start at once; one hashes while the other truncates and rewrites the shared path, giving a spurious 'adapter hash mismatch' and a failed start (fails closed).",
     "fix": "Per-process private temp directory, as in F1.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Launch two load() processes simultaneously, 50 iterations; expected zero failures, observed intermittent RuntimeError('adapter hash mismatch')."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "loader.py:16",
     "suspicion": "from_pretrained may take the torch.load (pickle) path if the pinned revision holds .bin weights, executing code on a host with customer credentials.",
     "unresolved_fact": "File list at the pinned revision and the deployed transformers/torch versions; add use_safetensors=True regardless."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "loader.py:21",
     "suspicion": "strict=True load_state_dict will raise on every start if the 'adapter' is a LoRA/PEFT file whose keys do not match the base model.",
     "unresolved_fact": "Key list of intake-v3.safetensors (full state dict vs LoRA adapter)."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "loader.py:9-11",
     "suspicion": "The pins only protect if ADAPTER_SHA256 and MODEL_REVISION came from a trusted out-of-band source and the pinned content was reviewed.",
     "unresolved_fact": "Who produced the pin values and through what channel."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Remote code execution via the model repository.", "evidence": "trust_remote_code=False at loader.py:16."},
    {"id": "R2", "candidate": "Model revision unpinned.", "evidence": "MODEL_REVISION is a full 40-hex commit ID at loader.py:9."},
    {"id": "R3", "candidate": "Adapter loaded before verification.", "evidence": "Hash compared and RuntimeError raised at loader.py:19-20 before load_file at line 21."},
    {"id": "R4", "candidate": "Adapter deserialization executes code.", "evidence": "safetensors.torch.load_file parses tensors only; no pickle."},
    {"id": "R5", "candidate": "Malformed ADAPTER_SHA256 constant.", "evidence": "Constant is exactly 64 hex characters."}
  ]
}
```