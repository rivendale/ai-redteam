VERDICT: **REWORK**. The loader runs code from outside the network on servers that hold customer credentials, with no pinning, integrity check or sandbox.

CONFIDENCE: **medium**. No tools were available, so I ran nothing, opened no links and could not inspect the model repo or the adapter file. No fresh subagent or seat was available, so this is a single-reviewer pass. The work was supplied, not written in this conversation, which lowers the anchoring risk. Re-run with tools before relying on it. The two security findings are tied to exact lines and documented library behavior, so they do not depend on the gaps.

INPUTS LEDGER:
- Seen: the request (`request.md`), the context (`context.md`) and `loader.py` in full.
- Not seen: the Hub repo `acme-labs/ner-small` and whether it ships custom code. This matters only for how soon F1 fires, not whether the defect exists.
- Not seen: the adapter file and its format (full state dict or PEFT/LoRA). This matters for F4 and S1.
- Not seen: the torch and transformers versions pinned on the intake servers. This matters for F2.
- Not seen: the intake servers' hardware, egress rules and who else runs on them. This matters for F3 and S3.
- Not seen: who controls `files.example.com`. This matters for F2 and F5.

COVERAGE:
- Checked: `loader.py` (file) and `loader.py:load` (function), line by line.
- Checked assumptions: that the model source is trusted, that the adapter is a state dict for this base model, and that `/tmp` is private.
- Not checked: the remote repo contents, the adapter bytes, the dependency versions and the deployment environment. None were supplied, and there were no tools.

SEATS AND GATE: The local reviewer ran. No subagent or cross-vendor seats were available in this session. The gate passed: the work contains no credentials or personal data. The context *describes* credentials on the target servers but does not include any.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `loader.py:12` `from_pretrained(MODEL, trust_remote_code=True)` | `trust_remote_code=True` tells transformers to import and run Python from the repo when its config declares `auto_map`. `MODEL` has no `revision=` pin, so each load pulls whatever the external owner (or anyone who compromises their account) last pushed. | The owner pushes a `modeling_*.py` plus an `auto_map` entry. On the next service start, that code runs as the intake process and reads `os.environ`, which holds the customer credentials, then sends it out. | Use `trust_remote_code=False`. If the architecture truly needs custom code, vendor that code into this repo and review it. Pin `revision="<commit sha>"`. Better still, mirror the weights internally and load from a local path with `local_files_only=True`. **Repro:** in a scratch HF repo with `auto_map` pointing to a module that writes a marker file on import, call `load()` against it. Expected: no marker file. Observed: the marker file is written. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | B | `loader.py:14` `torch.load("/tmp/intake-v3.bin")` | The file is a pickle from outside the network, loaded with no explicit `weights_only=True`. On torch < 2.6 the default is `weights_only=False`, and unpickling can run arbitrary code. This is PROBABLE, not CONFIRMED, because the torch version was not supplied. | On torch 2.5, a tampered `intake-v3.bin` uses a `__reduce__` payload. It executes at load and can read the credential environment. | Ship the adapter as `.safetensors` and load it with `safetensors.torch.load_file`. At minimum pass `weights_only=True` explicitly, and add a hash check (F5). **Repro:** pickle an object whose `__reduce__` returns `(os.system, ("touch /tmp/pwned",))`, then call `torch.load` on it under the pinned torch version. Expected: refused. On < 2.6, observed: `/tmp/pwned` exists. | a✓ b✗ c✓ d✓ |
| F3 | High | CONFIRMED | B | `loader.py:13-14` (fixed path `/tmp/intake-v3.bin`) | A predictable filename in shared `/tmp` is written, then read in a separate step. There is no private temp directory, no atomic rename and no lock. | (1) Two workers call `load()` at once. One reads a half-written file and crashes or loads a truncated state. (2) A local user pre-plants a symlink, so `urlretrieve` follows it and overwrites another file. Or they swap the file between download and `torch.load`, which re-opens the F2 code path with a file they control. | Download into `tempfile.mkdtemp()` (or a service-owned directory with mode 0700). Verify the hash, then load from that same handle or path. Better, bake the verified adapter into the image and never download at runtime. **Repro:** run two `load()` processes in parallel against a throttled server. Observed: an intermittent `UnpicklingError` or `EOFError`. | a✓ b✓ c✓ d✗ |
| F4 | High | CONFIRMED | B | `loader.py:15` `load_state_dict(state, strict=False)` (return value discarded) | `strict=False` returns `missing_keys` and `unexpected_keys` instead of raising, and the code throws that result away. If the adapter keys don't match the base model, no adapter weights are applied and nothing reports it. Mismatch is plausible because the base model is unpinned and can change shape or names upstream. A PEFT-format adapter would also mismatch (see S1). | Upstream renames layers, or the adapter is LoRA-format. `load()` succeeds, and the service runs the generic base model in production with degraded extraction and no error. | Capture the result. Raise if `unexpected_keys` is non-empty, or if `missing_keys` is not exactly the expected frozen-base set. Use PEFT's loader if the adapter is a PEFT adapter. **Repro:** pass `{"bogus.weight": torch.zeros(1)}` to `load_state_dict(..., strict=False)`. Observed: no exception and the model is unchanged. | a✓ b✓ c✗ d✓ |
| F5 | Medium | CONFIRMED | B | `loader.py:9,13` | The adapter is fetched with no pinned SHA-256 or signature check. TLS authenticates only the host, not the file. Even with safe loading, swapped weights can silently change what the model extracts (poisoning). | `files.example.com` is compromised or the file is replaced. Intake runs a model that misses or mislabels entities in customer data. | Pin the expected SHA-256 in code or config and fail closed on mismatch. **Repro:** serve a different file at the URL. Expected: refusal. Observed: it loads. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED | B | `loader.py:13` | `urlretrieve` has no timeout, no retry policy and no error context. Every `load()` re-downloads the adapter, so startup depends on an external host. | The external host hangs, and service startup blocks indefinitely on every restart. | Remove runtime fetching by baking the verified artifact into the image. Otherwise use `urlopen(..., timeout=...)` with bounded retries. | a✓ b✓ c✗ d✗ |

Severity notes:
- **F1** is Critical even if the repo has no custom code today. The flag combined with an unpinned revision is what gives the outside party code execution, and the confirmed defect is that the loader grants it.
- **F2** stays High because its exploitability depends on the unverified torch version.
- **F3** is rated High through c (security exposure). Its likelihood (d) depends on who shares the host.

## Needs validation
- **S1:** Is `intake-v3.bin` a full or partial state dict for `AutoModelForTokenClassification`, or a PEFT/LoRA adapter (keys like `base_model.model.*.lora_A`)? If it is PEFT, `load_state_dict` is the wrong API and F4 fires on every load. Settle it by listing the file's keys.
- **S2:** Does `acme-labs/ner-small` declare `auto_map` or ship `.py` files at the current revision? This settles whether F1 can fire today or only after an upstream change.
- **S3:** Is the adapter saved with CUDA tensors? If so, `torch.load` without `map_location` fails on CPU-only intake servers. Settle it with the server hardware and the adapter's tensor devices.
- **S4:** Can the intake servers reach the HF Hub and `files.example.com` at all, and does their environment hold an `HF_TOKEN` that the Hub client would send?

## Refuted
- **"The model is left in training mode, so dropout is active."** `from_pretrained` returns the model in `eval()` mode, and `load_state_dict` does not change the mode.
- **"The adapter download is plaintext and open to MITM."** The URL is `https://`, and Python's `urllib` verifies certificates by default. The real gap is missing content integrity, which is F5.

## What holds up
- The structure is minimal and matches the request: it loads the base model, then applies the adapter.
- The transport is HTTPS.
- It uses the correct Auto class for an NER token-classification model.

## Unverified claims
- The work makes no explicit claims. Its implicit claim that "this adapter fits this model" is S1, and "the source is safe to execute" is F1/S2.

## Questions for the author
1. Does the model really need custom code? If not, F1's fix is simply deleting the flag.
2. What format is the adapter, and can it be shipped as safetensors with a pinned hash?
3. Which torch version runs on the intake servers?

## Summaries

**Decision-maker summary:** Do not deploy this loader. It lets an outside party run code on servers holding customer credentials (F1, and likely F2), and it can silently skip the adapter (F4). Fix F1–F4 by pinning, removing remote code, using safetensors with a hash check and checking the load result, then re-review. The risk of proceeding anyway is credential theft through a supply-chain change you would not see.

**Owner summary:** The new loading code downloads and runs files from outside the company on servers that hold customer passwords and keys, with nothing checking that those files are what we expect. Anyone who controls or tampers with those outside files could take over the servers or quietly change how customer data is processed. The code needs to be reworked to use locked, verified copies before it goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "loader.py", "status": "seen", "matters": true},
    {"item": "acme-labs/ner-small repository contents", "status": "not_seen", "matters": true},
    {"item": "intake-v3.bin adapter file", "status": "not_seen", "matters": true},
    {"item": "torch/transformers versions on intake servers", "status": "not_seen", "matters": true},
    {"item": "intake server hardware, egress and tenancy", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains no credentials or personal data; context only describes credentials on target servers."},
  "coverage": {
    "checked": [
      {"unit": "loader.py", "kind": "file"},
      {"unit": "loader.py:load", "kind": "function"},
      {"unit": "model source is trusted", "kind": "assumption"},
      {"unit": "adapter is a matching state dict", "kind": "assumption"},
      {"unit": "/tmp is private to the service", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "acme-labs/ner-small repository", "reason": "no tools; not supplied"},
      {"unit": "intake-v3.bin", "reason": "no tools; not supplied"},
      {"unit": "dependency versions", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:12",
     "scenario": "The external repo owner (or an attacker with their account) adds custom modeling code with auto_map; because trust_remote_code=True and the revision is unpinned, it executes on the next load and can exfiltrate the customer credentials in os.environ.",
     "fix": "Set trust_remote_code=False (vendor and review any required code), pin revision to a commit SHA, and preferably load from an internal mirror with local_files_only=True.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Point load() at a scratch repo whose auto_map module writes a marker file on import; expected no marker, observed marker created."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "loader.py:14",
     "scenario": "On torch < 2.6 (default weights_only=False), a tampered intake-v3.bin with a __reduce__ payload executes arbitrary code at torch.load on servers holding credentials.",
     "fix": "Ship the adapter as safetensors and load with safetensors.torch.load_file; at minimum pass weights_only=True and verify a pinned SHA-256 first.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "torch.load a pickle whose __reduce__ returns (os.system, ('touch /tmp/pwned',)) under the deployed torch version; expected refusal, observed /tmp/pwned on < 2.6."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:13-14",
     "scenario": "Concurrent workers read a half-written /tmp/intake-v3.bin and crash, or a local user pre-plants a symlink or swaps the file between download and torch.load, feeding a controlled file into the deserializer.",
     "fix": "Download into a private tempfile.mkdtemp() or 0700 service directory, verify the hash, and load the verified file; better, bake the artifact into the image.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "Run two load() processes in parallel against a throttled server; observe intermittent UnpicklingError or EOFError."},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:15",
     "scenario": "If adapter keys do not match the (unpinned) base model or the adapter is PEFT-format, load_state_dict(strict=False) applies nothing, the discarded result hides it, and production runs the untuned base model.",
     "fix": "Check the returned missing_keys/unexpected_keys and raise on any unexpected key or unexpected missing set; use PEFT's loader if it is a PEFT adapter.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "model.load_state_dict({'bogus.weight': torch.zeros(1)}, strict=False) raises nothing and leaves the weights unchanged."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:9,13",
     "scenario": "A replaced file on files.example.com is loaded without any content check, silently changing extraction behavior on customer data.",
     "fix": "Pin the expected SHA-256 and fail closed on mismatch.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Serve a different file at ADAPTER_URL; expected refusal, observed it loads."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "loader.py:13",
     "scenario": "If the external host hangs, urlretrieve has no timeout and service startup blocks indefinitely on every restart.",
     "fix": "Bake the verified artifact into the image, or use urlopen with a timeout and bounded retries.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Point ADAPTER_URL at a server that accepts the connection and never responds; load() never returns."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "loader.py:15",
     "suspicion": "The adapter may be PEFT/LoRA format, which load_state_dict cannot apply.",
     "unresolved_fact": "The key names inside intake-v3.bin."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "loader.py:12",
     "suspicion": "The repo may already ship custom code, so F1 fires today.",
     "unresolved_fact": "Whether acme-labs/ner-small's config declares auto_map at the current revision."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "loader.py:14",
     "suspicion": "torch.load without map_location fails on CPU-only servers if the adapter holds CUDA tensors.",
     "unresolved_fact": "Server hardware and the devices of the adapter's saved tensors."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "loader.py:12-13",
     "suspicion": "The servers may lack egress to the Hub or the adapter host, or may send an HF_TOKEN from their environment.",
     "unresolved_fact": "The intake servers' egress rules and whether HF_TOKEN is set in their environment."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The model is left in training mode.",
     "evidence": "from_pretrained returns the model in eval() mode, and load_state_dict does not change the mode."},
    {"id": "R2", "candidate": "The adapter download is plaintext and open to MITM.",
     "evidence": "ADAPTER_URL is https and urllib verifies certificates by default; the remaining gap is content integrity (F5)."}
  ]
}
```