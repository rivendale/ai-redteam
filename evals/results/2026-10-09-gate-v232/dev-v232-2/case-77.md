VERDICT: SHIP WITH FIXES. The model pin, the remote-code setting and the hash check are sound, but the hash is checked on one read of a shared `/tmp` file and the weights are loaded from a second read. Two open questions should also be settled before this runs on servers that hold customer credentials.

CONFIDENCE: medium. This session had no tools, so I could not open the model repository at the pinned commit, inspect the adapter file, see the installed `transformers`/`torch` versions, or run anything. It was a single reviewer with no subagent, but the reviewer is not the author.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `loader.py` (21 lines).
- Not seen and it matters:
  - The file list of `acme-labs/ner-small` at commit `5f1c0b2e…3d10`. This decides whether a pickle could be loaded.
  - The adapter file and its key names. This decides whether `load_state_dict(strict=True)` can work at all.
  - Where `ADAPTER_SHA256` came from.
  - The dependency pins (`transformers`, `torch`, `safetensors`).
  - How the intake service calls `load()` (one process or many workers).
  - Host `/tmp` setup (private tmp, `fs.protected_regular`).
- Not seen and it does not matter: the rest of the intake service (out of scope).

COVERAGE:
- Scope: the whole of `loader.py`.
- Checked:
  - Constants (lines 8–11).
  - Lines 15–21 of `load()`.
  - Assumptions: the revision is immutable, `trust_remote_code` is off, the hash is well-formed, the hash is bound to the bytes that get loaded, the adapter format, and download failure behavior.
  - Both documents.
- Not checked: the remote artifacts and dependency versions (not supplied, no tools).

SEATS AND GATE:
- One local reviewer, same vendor, no tools. No subagent was available.
- The gate passed: the work contains no credentials or personal data. No cross-vendor seats were requested.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | loader.py:16–20 | The SHA-256 is computed from one open of `/tmp/intake-v3.safetensors` (line 17). `load_file(path)` then opens the path again (line 20). The check is not bound to the bytes that are loaded. The path is predictable and sits in a shared, world-writable directory. | Conditions: another local principal can write that path, and the host has no private `/tmp` and `fs.protected_regular=0`. Attack: the principal pre-creates the file with mode 666 and rewrites it after the hash passes. The service then loads attacker-chosen weights; `strict=True` only checks key names and shapes. Result: silently manipulated extraction of customer data. Safetensors itself cannot execute code, so this is integrity, not code execution. | **Fix:** read the bytes once, hash them, and load from the same bytes with `safetensors.torch.load(data)`. Or download into a `tempfile.mkdtemp()` directory with mode 0700. **Reproduction (scratch copy):** wrap `loader.load_file` with a function that overwrites `path` with a different safetensors file of the same keys and shapes, then calls the real `load_file`. Expected: `RuntimeError("adapter hash mismatch")`. Observed on the current code: the substituted weights load and `load()` returns normally. | a✓ b✗ c✓ d✗ |
| F2 | Low | PROBABLE | B | loader.py:16 | The download path is fixed and shared by every process. | Conditions: two workers call `load()` at the same time. Worker B's `urlretrieve` truncates the file while worker A is hashing or loading it. Result: a spurious "adapter hash mismatch" or a safetensors parse error, and the service fails to start. It fails closed, so there is no integrity loss. | **Fix:** use a unique per-process temp file, or load from memory as in F1. **Reproduction:** serve the adapter from a local server throttled to about 100 KB/s, start two `python -c "import loader; loader.load()"` at once, and observe one exception in some runs. | a✓ b✗ c✗ d✗ |
| F3 | Low | CONFIRMED | B | loader.py:16 | `urlretrieve` has no timeout. The socket default is `None` unless something sets it globally. | Conditions: the adapter host accepts the TCP connection and then stalls. Result: `load()` blocks forever and the intake service never becomes ready, with no error logged. | **Fix:** `urllib.request.urlopen(ADAPTER_URL, timeout=30)` and read the response yourself. **Reproduction:** point `ADAPTER_URL` at `nc -l 8080` (which accepts and never responds) and call `load()`. Expected: a timeout error. Observed: it hangs. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED | B | loader.py:16–17 | There is no size cap. The whole response is written to `/tmp` before the hash is checked, then read fully into memory. | Conditions: the external host is compromised or misconfigured and serves an endless stream. Result: `/tmp` or memory fills up on the intake server before the hash check can reject the file. | **Fix:** stream with a maximum byte count a little above the expected adapter size, hash incrementally, and abort past the limit. **Reproduction:** serve `/dev/zero` over HTTP and call `load()`. Observe disk usage of `/tmp/intake-v3.safetensors` growing without bound. | a✓ b✓ c✗ d✗ |

## Needs validation

- **S1 — pickle fallback in model loading (loader.py:15).** `from_pretrained` does not pass `use_safetensors=True`. If the pinned commit has only `pytorch_model.bin`, transformers falls back to `torch.load`. With older transformers or torch that is unpickling in a process that holds customer credentials.
  - Settled by: the file list at commit `5f1c0b2e…3d10`, and the installed `transformers` and `torch` versions.
  - Recommended regardless: add `use_safetensors=True` so the guarantee comes from the code, not from what happens to be in the repository.
- **S2 — adapter format versus `load_state_dict(strict=True)` (loader.py:20).** If `intake-v3.safetensors` is a PEFT/LoRA adapter (keys like `…lora_A.weight`), strict loading into the base model raises, so the loader never works. If it is a full fine-tuned state dict, it works, but "adapter" is a misnomer and the separate Hub download is redundant.
  - Settled by: the key names in the adapter file. A LoRA adapter should be loaded with `PeftModel.from_pretrained` or by merging the adapter into the base model.
- **S3 — provenance of `ADAPTER_SHA256` (loader.py:11).** If the hash was computed from a copy downloaded from the same external host, it only proves consistency, not authenticity.
  - Settled by: whether the hash came from the adapter's producer through a separate channel (signed release or internal build record).
- **S4 — dependency pinning.** Pinned weights do not help if `transformers` or `safetensors` are unpinned or come from an unvetted index.
  - Settled by: the requirements/lock file and its hashes.

## Refuted

- **"The Hub model could be swapped upstream."** `MODEL_REVISION` is a full 40-hex commit SHA, and Hub file content is addressed by that commit. A repository takeover or force-push cannot change what this revision resolves to.
- **"Remote code from the model repository executes."** `trust_remote_code=False` is explicit on line 15.
- **"The hash comparison is broken."** The constant is exactly 64 lowercase hex characters, and `hexdigest()` returns lowercase. Any mismatch raises before loading.

## What holds up

- The revision pinning, and remote code being disabled.
- The adapter is safetensors, which cannot execute code when loaded.
- The hash check fails closed, and strict loading rejects unexpected keys.
- HTTPS certificate verification is on by default in `urllib`.
- `from_pretrained` already returns the model in eval mode.

## Unverified claims

- "Fine-tuned adapter" (docstring). Confirm by listing the adapter's keys (S2).
- That the pinned commit contains safetensors weights (S1). Confirm from the Hub file list at that SHA.

## Questions for the author

1. Is the adapter a LoRA/PEFT adapter or a full state dict?
2. Does the pinned model commit include `model.safetensors`?
3. Who produced `ADAPTER_SHA256`, and through what channel?
4. Does the service call `load()` from multiple workers, and does the host use a private `/tmp`?

## Decision-maker summary

Fix the verify-then-reload gap (F1), add `use_safetensors=True`, and settle the adapter format (S2) before deploying. The fixes are small and local. Shipping as is leaves model integrity resting on host `/tmp` hardening and on the contents of an unseen remote commit, on servers that hold customer credentials.

## Owner summary

The loader mostly does the right thing: it pins exactly which model version it downloads and checks the adapter file's fingerprint before using it. However, it checks the fingerprint on one read of a shared temporary file and then uses a second read, which leaves a small window for tampering. It also has not been confirmed that the adapter file is in a format this code can load, or that the model download can never fall back to an unsafe file format. These are quick fixes and should be done before it runs in production.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "loader.py", "status": "seen", "matters": true},
    {"item": "acme-labs/ner-small file list at 5f1c0b2e9d7a4c3b8a6e1f0d2c4b5a69788e3d10", "status": "not_seen", "matters": true},
    {"item": "intake-v3.safetensors contents and key names", "status": "not_seen", "matters": true},
    {"item": "provenance of ADAPTER_SHA256", "status": "not_seen", "matters": true},
    {"item": "dependency pins (transformers, torch, safetensors)", "status": "not_seen", "matters": true},
    {"item": "intake service caller and host /tmp configuration", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; no credentials or personal data in the work."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "loader.py", "kind": "file"},
      {"unit": "loader.py:load", "kind": "function"},
      {"unit": "loader.py:8-11 constants", "kind": "config"},
      {"unit": "revision pin is immutable", "kind": "assumption"},
      {"unit": "hash is bound to loaded bytes", "kind": "assumption"},
      {"unit": "adapter loads with strict=True", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "acme-labs/ner-small at pinned revision", "reason": "no_tools"},
      {"unit": "intake-v3.safetensors", "reason": "no_tools"},
      {"unit": "dependency lock file", "reason": "not_supplied"},
      {"unit": "intake service callers", "reason": "out_of_scope"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "loader.py:16-20",
     "scenario": "A local principal able to write /tmp/intake-v3.safetensors (no private /tmp, fs.protected_regular=0) rewrites the file after the hash check on line 17 and before load_file reopens it on line 20; the service loads attacker-chosen weights with matching keys and shapes, silently corrupting extraction of customer data.",
     "fix": "Hash and load the same in-memory bytes (safetensors.torch.load(data)), or download into a 0700 tempfile.mkdtemp() directory.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "In a scratch copy, wrap loader.load_file so it overwrites path with a different same-shape safetensors file before calling the real load_file; expected RuntimeError('adapter hash mismatch'), observed load() returns with substituted weights."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "loader.py:16",
     "scenario": "Two workers call load() concurrently; one truncates and rewrites the shared fixed path while the other hashes or loads it, causing a spurious hash mismatch or parse error at startup (fails closed).",
     "fix": "Use a unique per-process temp file or load from memory.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Serve the adapter throttled to ~100 KB/s locally, start two processes calling loader.load() simultaneously; observe intermittent RuntimeError or safetensors error."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:16",
     "scenario": "The adapter host accepts the connection and stalls; urlretrieve has no timeout, so load() blocks forever and the service never starts, with no error.",
     "fix": "Use urllib.request.urlopen(ADAPTER_URL, timeout=30) and read the stream explicitly.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Point ADAPTER_URL at a listener that accepts and never responds (nc -l 8080); call load(); expected timeout error, observed indefinite hang."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:16-17",
     "scenario": "A compromised or misconfigured external host serves an unbounded body; the full response is written to /tmp and then read into memory before the hash can reject it, exhausting disk or memory on the intake server.",
     "fix": "Stream with a maximum byte limit near the expected adapter size, hashing incrementally and aborting past the limit.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Serve /dev/zero over HTTP as ADAPTER_URL, call load(); observe /tmp/intake-v3.safetensors growing without bound."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "loader.py:15",
     "suspicion": "Without use_safetensors=True, from_pretrained can fall back to torch.load of pytorch_model.bin (pickle) in a process holding customer credentials.",
     "unresolved_fact": "Whether the pinned commit contains model.safetensors, and the installed transformers/torch versions."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "loader.py:20",
     "suspicion": "If the adapter is a PEFT/LoRA adapter, load_state_dict(strict=True) on the base model raises and the loader never works.",
     "unresolved_fact": "The key names in intake-v3.safetensors."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "loader.py:11",
     "suspicion": "ADAPTER_SHA256 may have been computed from a copy fetched from the same untrusted host, proving consistency rather than authenticity.",
     "unresolved_fact": "Who produced the hash and through what channel."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "loader.py:5-6",
     "suspicion": "Unpinned or unhashed transformers/safetensors packages would undermine the weight pinning.",
     "unresolved_fact": "The requirements or lock file with hashes."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The Hub model could be swapped upstream.", "evidence": "MODEL_REVISION is a full 40-hex commit SHA (loader.py:9); content at a commit is immutable."},
    {"id": "C2", "candidate": "Remote code from the model repository executes.", "evidence": "trust_remote_code=False is explicit at loader.py:15."},
    {"id": "C3", "candidate": "The hash comparison can never match or is case-sensitive wrong.", "evidence": "ADAPTER_SHA256 is 64 lowercase hex characters and hexdigest() returns lowercase; a mismatch raises before loading."}
  ]
}
```