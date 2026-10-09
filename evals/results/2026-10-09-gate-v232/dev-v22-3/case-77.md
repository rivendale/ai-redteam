**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session, so nothing was run, downloaded or opened. Every claim about library behaviour below comes from documented API semantics, not from execution.

VERDICT: **SHIP WITH FIXES**. The core trust controls are sound: a commit-pinned model, `trust_remote_code=False`, and a SHA-256-pinned safetensors adapter. But the loader does not force safetensors for the base model, checks the adapter's hash on one read and loads it from a second read of a shared `/tmp` path, and can hang or exhaust disk on download.

CONFIDENCE: **medium**. Limits: no tools; the transformers/torch versions, the adapter file and the files at the pinned model revision were not supplied; single reviewer.

INPUTS LEDGER:
- Seen: the original request (one line), context.md and loader.py (21 lines).
- Not seen, and it matters:
  - Dependency pins (requirements or lockfile). These decide whether a pickle fallback can execute code (F1, S4).
  - The adapter file or its key list. This decides whether `strict=True` can ever succeed (S1).
  - The file listing at `acme-labs/ner-small@5f1c0b2e…` (F1).
  - Where the two pinned hashes came from (S2).
  - The deployment layout: number of workers, users on the host, permissions on the HF cache (F2, S5).

COVERAGE:
- Checked: `loader.py` (whole file), `loader.py:load`, the four constants, and the security assumptions (pinning, remote code, deserialization, integrity check).
- Not checked: dependency versions, adapter contents, model repo contents, deployment config, and callers of `load()`.

SEATS AND GATE: Sensitivity gate passed. The work contains no credentials or personal data; the context only says the servers hold credentials. No subagent or cross-vendor seats ran because none were available in this tool-less session. Reviewer: this instance only.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | loader.py:15 | `from_pretrained` is not called with `use_safetensors=True`. If the pinned revision has no `*.safetensors` file, transformers falls back to `pytorch_model.bin`, which is a pickle. | The pinned commit ships only a `.bin` file, or a `.bin` file that is chosen over safetensors. The installed transformers/torch also loads it without `weights_only=True` (older versions). An external party's pickle then runs code on a server whose environment holds customer credentials. | Pass `use_safetensors=True`, so loading fails instead of falling back to the pickle. Repro in a sandbox: point the loader at a test repo revision containing only a `pytorch_model.bin` whose pickle writes a marker file. Expected: an error. Observed on affected versions: the marker file appears. With the fix, an `OSError` is raised. | a✔ b✘ c✔ d✘ |
| F2 | Medium | CONFIRMED | B | loader.py:16-20 | The hash is checked on one read of `/tmp/intake-v3.safetensors` (line 17), then `load_file` reopens the path (line 20). The path is fixed, predictable and shared in world-writable `/tmp`. | (i) Several workers on one host call `load()` at once. One worker's `urlretrieve` truncates the file while another is hashing or loading it. The result is a spurious "adapter hash mismatch" or a safetensors error, and workers fail to boot. (ii) Another local principal can replace or write the file between line 17 and line 20. Weights that were never verified then load. Safetensors means this is tampered model behaviour, not code execution. (iii) A pre-planted symlink makes the download overwrite its target; `fs.protected_symlinks` mitigates this. | Download into a private `tempfile.TemporaryDirectory()`. Stream-hash with a size cap. Then load from the exact verified bytes: `safetensors.torch.load(data)`, or `load_file` on the private path you just hashed. Repro: in a scratch copy, run two processes calling `load()` in a tight loop and observe intermittent mismatch or safetensors errors. For (ii), pause between lines 17 and 20, swap in a different valid safetensors file with matching keys, and observe that load succeeds with the swapped weights. | a✔ b✔ c✔ d✘ |
| F3 | Medium | CONFIRMED | B | loader.py:16-17 | `urlretrieve` takes no timeout and has no size limit. The whole file is then read into memory to hash it, through a file handle that is never closed. The download is repeated on every `load()`. | `files.example.com` stalls, and `load()` blocks indefinitely at startup with no error. Or the host serves a multi-GB body, which fills `/tmp` and RAM before the hash check can reject it. An outage of the external host also prevents every restart of the intake service. | Use `urllib.request.urlopen(url, timeout=…)` and stream in chunks into `hashlib.sha256().update`. Abort when the size exceeds the expected length. Better: mirror both artifacts internally once they are verified, and load offline (`HF_HUB_OFFLINE=1`, a local adapter path). Repro: serve a socket that accepts the connection and never responds, then call `load()`; it never returns. | a✔ b✔ c✘ d✘ |

## Needs validation

- **S1, loader.py:20.** `strict=True` with an "adapter". An adapter (LoRA, PEFT, head-only) does not contain every key of the base model, so `strict=True` would raise at startup. If the file is a full fine-tuned state dict, it loads, but then it fully overwrites the pinned base weights. Unresolved fact: the key set of `intake-v3.safetensors` compared with `model.state_dict().keys()`. If it is a partial adapter, the loader cannot work at all, and that would be a High requirement-fit finding.
- **S2, loader.py:9,11.** A pin proves integrity, not trust. Unresolved fact: who computed `ADAPTER_SHA256` and from what source, and whether anyone reviewed the files at `MODEL_REVISION` before pinning. A hash taken from the same untrusted URL only proves the file has not changed since then.
- **S3, loader.py:10.** `files.example.com` sits under an RFC 2606 reserved domain. Unresolved fact: whether this is the real host or a value sanitised for the review. If it is real, every load fails, though it fails closed.
- **S4.** Unresolved fact: the pinned transformers and torch versions. They decide whether the F1 fallback would unpickle with `weights_only=False`.
- **S5.** Cached model files in the HF cache are not re-hashed when loaded from cache. Unresolved fact: who can write the service user's HF cache directory on the intake servers.

## Refuted

- **Remote code execution through the model config:** refuted. `trust_remote_code=False` is set explicitly at line 15, so no repo-supplied Python is executed.
- **Floating model version:** refuted. `MODEL_REVISION` is a full 40-hex commit SHA, which is immutable, not a branch or tag.
- **Adapter deserialization giving code execution:** refuted. The adapter is loaded with safetensors, which has no code-execution path, and only after a hash check.
- **Broken hash comparison:** refuted. `hexdigest()` is lowercase, the constant is 64 lowercase hex characters, and the value is public, so timing does not matter.
- **Model left in train mode:** refuted. `from_pretrained` returns the model in eval mode, and `load_state_dict` does not change that.

## What holds up

The trust model is correct: a commit-pinned base model, remote code disabled, an adapter checked against a pinned SHA-256 before use, a safetensors format for the adapter, and failure that stops loading on a mismatch. The scope matches the request: a loader for the model and its adapter, with nothing extra.

## Unverified claims

- The docstring describes the file as a "fine-tuned adapter". Confirm by listing the file's keys (S1).
- The implicit claim is that the pinned artifacts are safe. Confirm their provenance and the review record (S2), and list the repo files at the pinned commit (F1).

## Questions for the author

1. Is `intake-v3.safetensors` a full state dict or a partial adapter? What are its keys?
2. Where did the two pinned hashes come from, and was the content at each pin reviewed?
3. How many processes call `load()` per host, and who else can write to `/tmp` and the HF cache there?
4. Which transformers and torch versions are deployed?

## Summaries

**DECISION-MAKER SUMMARY:** The integrity design is sound. Before production, add `use_safetensors=True`, verify and load the adapter from one private temp copy, and add a timeout and a size cap to the download (F1–F3). Confirm that the adapter's keys fit `strict=True` (S1). If you proceed as is, the main risks are failed or hung startups, and possible execution of external pickle code if the pinned model lacks safetensors weights.

**OWNER SUMMARY:** The loader pins exactly which model and adapter it uses and checks the adapter's fingerprint, which is the right foundation. A few gaps could still let unchecked files in or make the service hang at startup, and each is a small code change. One question about the adapter file needs an answer, because the answer decides whether the loader works at all.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "loader.py", "status": "seen", "matters": true},
    {"item": "dependency pins (transformers, torch, safetensors)", "status": "not_seen", "matters": true},
    {"item": "intake-v3.safetensors (adapter keys)", "status": "not_seen", "matters": true},
    {"item": "acme-labs/ner-small file list at pinned revision", "status": "not_seen", "matters": true},
    {"item": "provenance of ADAPTER_SHA256 and MODEL_REVISION", "status": "not_seen", "matters": true},
    {"item": "deployment layout (workers, host users, HF cache perms)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains no credentials or personal data; context only states the servers hold credentials."},
  "coverage": {
    "checked": [
      {"unit": "loader.py", "kind": "file"},
      {"unit": "loader.py:load", "kind": "function"},
      {"unit": "loader.py:8-11 constants", "kind": "config"},
      {"unit": "pinning, remote code, deserialization and integrity-check assumptions", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "dependency versions", "reason": "not supplied"},
      {"unit": "adapter contents", "reason": "not supplied; no tools"},
      {"unit": "model repo contents at pinned revision", "reason": "no tools"},
      {"unit": "deployment config and callers of load()", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "loader.py:15",
     "scenario": "If the pinned revision provides only pytorch_model.bin and the installed transformers/torch unpickles without weights_only=True, an external pickle executes code on a server holding customer credentials.",
     "fix": "Pass use_safetensors=True to from_pretrained so a missing safetensors file fails instead of falling back to pickle.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "In a sandbox, point the loader at a test repo revision containing only a pytorch_model.bin whose pickle writes a marker file; on affected versions the marker appears; with the fix an OSError is raised."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:16-20",
     "scenario": "The hash is computed on one read of the fixed path /tmp/intake-v3.safetensors and load_file reopens it. Concurrent workers truncate each other's file, causing failed boots, and a local principal able to write the path between lines 17 and 20 gets unverified weights loaded.",
     "fix": "Download into a private tempfile.TemporaryDirectory, stream-hash with a size cap, and load the exact verified bytes with safetensors.torch.load(data).",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "In a scratch copy, run two processes calling load() in a loop and observe intermittent 'adapter hash mismatch' or SafetensorError; or pause between lines 17 and 20, swap in a different valid safetensors file, and observe load succeeds."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:16-17",
     "scenario": "urlretrieve has no timeout or size limit and the file is read whole into memory, so a stalled or hostile adapter host hangs startup forever or fills /tmp and RAM before the hash check rejects the file. An outage of the external host blocks every restart.",
     "fix": "Use urlopen with a timeout, stream into hashlib with a size cap, close the handle, and mirror the verified artifacts internally to load offline.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Serve a socket that accepts the connection and never responds, point ADAPTER_URL at it, call load(); it never returns."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "loader.py:20",
     "suspicion": "strict=True will raise if the adapter is a partial (LoRA/PEFT/head) adapter, so the loader cannot work.",
     "unresolved_fact": "The key set of intake-v3.safetensors compared with model.state_dict().keys()."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "loader.py:9,11",
     "suspicion": "Pins prove integrity, not trustworthiness of the pinned content.",
     "unresolved_fact": "Who computed ADAPTER_SHA256 and from what source, and whether the content at MODEL_REVISION was reviewed."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "loader.py:10",
     "suspicion": "files.example.com is under a reserved domain; if real, every load fails.",
     "unresolved_fact": "Whether the URL is the production host or was sanitised for the review."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "loader.py:5-6",
     "suspicion": "Library versions decide whether the F1 pickle fallback is exploitable.",
     "unresolved_fact": "Deployed transformers and torch versions."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "loader.py:15",
     "suspicion": "Cached HF files are not re-hashed on load from cache.",
     "unresolved_fact": "Who can write the service user's HF cache directory on the intake servers."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Remote code executes via the model config.", "evidence": "trust_remote_code=False is set explicitly at loader.py:15."},
    {"id": "R2", "candidate": "The model version floats.", "evidence": "MODEL_REVISION is a full 40-hex commit SHA, which is immutable."},
    {"id": "R3", "candidate": "Adapter deserialization allows code execution.", "evidence": "The adapter is loaded with safetensors, which has no code path, and only after a SHA-256 check."},
    {"id": "R4", "candidate": "The hash comparison is broken by case or timing.", "evidence": "hexdigest() is lowercase, the constant is 64 lowercase hex characters, and the value is public."},
    {"id": "R5", "candidate": "The model is left in train mode.", "evidence": "from_pretrained returns the model in eval mode and load_state_dict does not change it."}
  ]
}
```

I could not run `python3 tools/validate_findings.py` against this block because this session has no tools.