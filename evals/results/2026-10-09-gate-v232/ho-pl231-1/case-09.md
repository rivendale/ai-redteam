# Adversarial Diagnostic Review: `forecast.py`

## Pass 1: Reconstruct

The work is a small module meant to load the demand-forecast model for the dock rebalancing job. It downloads `demand-latest.pkl` over HTTPS and unpickles it. It also adds something nobody asked for: a "weather adapter" loaded from Hugging Face Hub with `trust_remote_code=True`.

For this to be safe and correct on the ops server, these must be true:

- **(A1)** Only fully trusted parties can ever write the bytes at `MODEL_URL`, and nothing on the network path can substitute them.
- **(A2)** Only fully trusted parties can ever push to `pedalo-labs/weather-adapter`, and that namespace is really owned by the organization.
- **(A3)** `models.example.test` resolves on the ops server.
- **(A4)** The model endpoint always responds promptly.
- **(A5)** Whatever "latest" points to at run time is a validated model.
- **(A6)** The process running this has nothing worth stealing. Context says the opposite: it holds the fleet DB credentials and the dock control API key.

## Pass 2: Attack (Track B, with security focus)

Each load path is a remote-code-execution sink:

- **`pickle.loads(raw)`** executes whatever `__reduce__` the payload defines. This is documented Python behavior, not a bug.
- **`AutoModel.from_pretrained(..., trust_remote_code=True)`** imports and runs Python files from the Hub repo. No revision is pinned, so it runs whatever is on the default branch at load time.

Neither path has an integrity check (hash, signature, pinned revision). There is no timeout, no error handling and no version logging. The weather adapter is outside the request.

## Pass 3: Self-check

- **Embedded instructions:** None. The work contains no text addressed to the reviewer.
- **Defending #1:** "The model host is internal and only CI writes to it." Even if true, this turns write access to one storage path into code execution on the most privileged box. Also, `urllib` follows redirects, including HTTPS→HTTP. The finding survives.
- **Defending #2:** "It's our own HF org." Unverified, and unpinned. Any org member's leaked Hub token, or a namespace that was never claimed, gives code execution. The finding survives.

---

**VERDICT: REWORK.** Both loaders run code fetched from the network, without integrity checks, inside a process that holds fleet DB and dock-control credentials. The loading approach has to be replaced, not patched.

**CONFIDENCE IN VERDICT: high.** The two sinks are visible in the code and their behavior is well documented. What limits confidence: I had no tools, so nothing was executed, and I could not see the deployment (process isolation, how credentials are exposed, DNS) or any tests.

**COVERAGE**

| Unit | Status |
|---|---|
| `request.md` | checked |
| `context.md` | checked |
| `forecast.py` (whole file, both functions, module constant) | checked |
| Tests | not checked: none supplied |
| Calling job / rebalancing code | not checked: not supplied |
| Dependency manifest (transformers/torch versions) | not checked: not supplied |
| Model-host and HF repo contents | not checked: no tools |

### FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | `forecast.py` `load_model`: `pickle.loads(raw)` on bytes from `urlopen(MODEL_URL)` | Unpickling network data is arbitrary code execution. There is no hash, signature or pinned version. | Someone with write access to `/pedalo/demand-latest.pkl` (a compromised storage credential, a CI job, or a redirect to HTTP with a MITM) publishes a pickle whose `__reduce__` reads environment variables or files and posts them out. On the next job run, the fleet DB credentials and dock control API key are exfiltrated, and the attacker can drive docks. | Don't use pickle. Ship the model in a non-executable format (ONNX, the framework's native JSON/text format, or `skops` with an explicit trusted-types list). Pin the artifact by SHA-256 (or verify a signature) before parsing, and fail closed on mismatch. Run the loader in a process that doesn't hold the credentials. **Repro (scratch copy only, not run):** serve a pickle with `__reduce__ = (os.system, ("touch /tmp/pwned",))` from a local HTTP server, point `MODEL_URL` at it, call `load_model()`, and observe that `/tmp/pwned` exists. **Regression test:** the loader must raise on an artifact whose digest doesn't match the pinned value. | a Y, b Y, c Y, d N (needs a write-path compromise) |
| 2 | **Critical** | CONFIRMED | `forecast.py` `load_weather_adapter`: `from_pretrained("pedalo-labs/weather-adapter", trust_remote_code=True)` | `trust_remote_code=True` runs Python from a public-hub repo with no `revision=` pin, so any future push runs on the ops server. | An org member's Hub token leaks, or the `pedalo-labs` namespace isn't owned by the company. The attacker pushes a `modeling_*.py` that harvests credentials. The next job run executes it with the same impact as #1. | Remove this function. It wasn't requested (see #3). If a weather adapter is truly needed: vendor and review its code, set `trust_remote_code=False`, pin `revision=<commit sha>`, use `use_safetensors=True`, and load from an internal mirror. **Repro (scratch, not run):** create a throwaway HF repo whose config `auto_map` points to a module that writes a marker file at import, call `from_pretrained(..., trust_remote_code=True)`, and observe the marker. | a Y, b Y, c Y, d N |
| 3 | Medium | CONFIRMED | `load_weather_adapter` and the module docstring ("and the weather adapter") | Scope creep: the request asks only for the demand-forecast loader. The extra function adds the `transformers` dependency, a Hub network dependency, and the #2 attack surface. | A reviewer focused on "the model loader" approves a module that also pulls third-party code onto the ops server. If the Hub is down or rate-limited, the job fails for a component nobody asked for. | Remove the function, or justify it in a separate reviewed change. **Repro:** compare the request text with the function list. | a Y, b Y, c N, d N |
| 4 | Medium | CONFIRMED | `urllib.request.urlopen(MODEL_URL)` with no `timeout=` | The default socket timeout is `None`, so a stalled server blocks the job indefinitely. | The model host accepts the TCP connection but never responds (overload or a half-open proxy). The rebalancing job hangs, no error is raised, and docks are not rebalanced. | Pass `timeout=`, add bounded retries, raise a clear error, and alert. **Repro (scratch, not run):** listen on a local port that accepts and never writes, point `MODEL_URL` at it, and observe that `load_model()` never returns. | a Y, b Y, c N, d N |
| 5 | Medium | CONFIRMED | `MODEL_URL = ".../demand-latest.pkl"` | A mutable "latest" pointer, with no version or digest logged. The model can change between runs without a deploy, and there's no record of which model made a given decision. | An unvalidated model is published to `latest`. Rebalancing behavior silently changes, and the cause can't be traced afterwards. | Reference an immutable versioned artifact plus its digest in config, and log the version and digest at load. Shares a fix with #1. **Repro:** swap the file at the URL between two runs; the code loads the new one with no log or diff. | a Y, b Y, c N, d N |

**Same root cause, siblings searched.** I searched every function in `forecast.py` for deserialization or exec sinks and for integrity checks:

- **Found:** `pickle.loads` (#1) and `trust_remote_code=True` (#2).
- **Possible third sink:** `from_pretrained` may load `.bin` weights via `torch.load`, which is pickle-based unless safetensors is used or torch ≥ 2.6 defaults to `weights_only`. This is moot while #2 stands. Listed under NEEDS VALIDATION.
- **Redirects:** `urlopen` follows redirects, including HTTPS→HTTP, which weakens TLS as the only protection for #1.
- **Integrity checks:** none anywhere in the file.

**Security boundary**

- **#1**
  - Principal: anyone who can write the object at `models.example.test/pedalo/demand-latest.pkl`, or a network attacker after a downgrade redirect.
  - Input: the pickle bytes.
  - Failing control: none. TLS authenticates the host, not the content.
  - Boundary crossed: model-store write access → code execution on the ops server.
  - Resource: fleet DB credentials, the dock control API key, physical dock control.
- **#2**
  - Principal: anyone able to push to `pedalo-labs/weather-adapter` on HF Hub.
  - Input: the Python files and config in that repo.
  - Failing control: `trust_remote_code=True` disables the guard, and there is no revision pin.
  - Boundary crossed: public-hub publisher → ops server execution.
  - Resource: same as #1.

### NEEDS VALIDATION
- **`.test` hostname:** `models.example.test` uses a reserved TLD (RFC 6761). Does it resolve on the ops server's DNS, or is it a placeholder presented as finished? Settled by `getent hosts models.example.test` on the ops server.
- **HF namespace ownership:** Does the organization own `pedalo-labs`, and who has push rights? Settled by the Hub org membership page.
- **Credential exposure:** Are the DB credentials and API key in the environment or memory of the same process that calls these loaders? Settled by the job's deployment config. This decides whether process isolation is a viable mitigation.
- **Dependency versions:** Installed `transformers` and `torch` versions, and whether the adapter repo has only safetensors weights. Settled by the lockfile and repo file list.
- **Model class:** Is `AutoModel` the right class for the adapter (versus a task-specific head)? Settled by the adapter's config.
- **Why pickle:** What framework produced `demand-latest.pkl`? This determines which safe format to migrate to.

### REFUTED
- **"HTTP errors would be unpickled as the model."** Refuted: `urlopen` raises `HTTPError` on 4xx/5xx by default. An error page isn't returned as bytes.
- **"Hardcoded secrets in the module."** Refuted: there are no tokens or credentials in the file.
- **"Prompt injection in the work."** Refuted: the work contains no reviewer-directed text.

### WHAT HOLDS UP
- The model URL uses HTTPS, not HTTP.
- The module is small and does not touch credentials itself.
- Errors propagate rather than being swallowed. There is no broad `except` that would let the job run on a missing model.

### UNVERIFIED CLAIMS
The work claims nothing beyond its docstring, which matches the code. It doesn't say the module was tested, and no tests were supplied. Any test coverage is UNVERIFIED. The mutations that would settle it:
- Replace the pinned digest with a wrong one; the loader must go red.
- Point the URL at a hanging socket; the timeout test must go red.

### QUESTIONS FOR THE AUTHOR
1. Who asked for the weather adapter? If no one, will you remove it?
2. Can the model be exported in a non-pickle format? If not, what produces it and who can write to the model store?
3. Does the loader run in the same process that holds the fleet DB credentials and dock API key?

### DECISION-MAKER SUMMARY
Do not run this on the ops server. Both loaders execute code downloaded at run time, and that process holds the fleet database and dock-control credentials. Replace pickle with a non-executable format verified against a pinned digest, drop the unrequested Hugging Face adapter, and add a timeout. If it runs as is, anyone who can tamper with the model file or the Hugging Face repo can take the credentials and control docks.

### OWNER SUMMARY
The new code that loads the forecasting model downloads files and runs whatever instructions are inside them, on the same server that holds the keys to the fleet database and the docks. Anyone who manages to tamper with those downloaded files could take over those keys, so the code should not run until it loads the model in a safe, checked form. It also loads an extra component nobody asked for, which adds the same risk and should be removed.

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
    {"item": "calling job / deployment config", "status": "not_seen", "matters": true},
    {"item": "dependency lockfile", "status": "not_seen", "matters": false}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "forecast.py", "kind": "file"},
      {"unit": "forecast.py:load_model", "kind": "function"},
      {"unit": "forecast.py:load_weather_adapter", "kind": "function"},
      {"unit": "forecast.py:MODEL_URL", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "rebalancing job caller and deployment", "reason": "not_supplied"},
      {"unit": "model host and HF repo contents", "reason": "no_tools"},
      {"unit": "dependency versions", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py load_model: pickle.loads(urllib.request.urlopen(MODEL_URL).read())",
      "scenario": "A party with write access to demand-latest.pkl (or a network attacker after an HTTPS->HTTP redirect) publishes a pickle whose __reduce__ exfiltrates env/files; next job run leaks fleet DB credentials and dock control API key.",
      "fix": "Replace pickle with a non-executable format (ONNX, native JSON/text, or skops with trusted types); verify a pinned SHA-256 or signature before parsing; fail closed; run loader without credential access.",
      "answers": {"a": true, "b": true, "c": true, "d": false},
      "reproduction": "Scratch copy only, not run: serve a pickle with __reduce__=(os.system,('touch /tmp/pwned',)) locally, point MODEL_URL at it, call load_model(), observe /tmp/pwned.",
      "security": true,
      "siblings_searched": {"searched": "All functions in forecast.py for deserialization/exec sinks and integrity checks", "found": "trust_remote_code=True in load_weather_adapter (F2); possible torch.load path inside from_pretrained (needs validation); urllib redirect following including HTTPS->HTTP; no integrity checks anywhere"},
      "boundary": {"principal": "Anyone able to write the object at models.example.test/pedalo/demand-latest.pkl, or a network attacker via downgrade redirect", "input": "pickle bytes", "control": "none; TLS authenticates host, not content; no hash or signature", "crossed": "model-store write access -> code execution on ops server", "resource": "fleet DB credentials, dock control API key, physical dock control"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py load_weather_adapter: AutoModel.from_pretrained('pedalo-labs/weather-adapter', trust_remote_code=True)",
      "scenario": "Leaked Hub token of an org member, or unowned namespace, lets an attacker push malicious modeling code; unpinned load executes it on the ops server and leaks credentials.",
      "fix": "Remove (unrequested). If needed: vendor and review code, trust_remote_code=False, pin revision to a commit SHA, use_safetensors=True, load from an internal mirror.",
      "answers": {"a": true, "b": true, "c": true, "d": false},
      "reproduction": "Scratch, not run: throwaway HF repo whose auto_map module writes a marker at import; call from_pretrained(..., trust_remote_code=True); observe the marker.",
      "security": true,
      "siblings_searched": {"searched": "All functions in forecast.py for exec sinks and revision/digest pins", "found": "pickle.loads in load_model (F1); no revision or digest pin anywhere"},
      "boundary": {"principal": "Anyone with push access to pedalo-labs/weather-adapter on HF Hub", "input": "repo Python modules and config", "control": "trust_remote_code=True disables the guard; no revision pin", "crossed": "public hub publisher -> ops server code execution", "resource": "fleet DB credentials, dock control API key, physical dock control"}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py load_weather_adapter and module docstring",
      "scenario": "Unrequested component adds a transformers dependency, a Hub network dependency, and the F2 attack surface; job can fail on Hub outage for a feature nobody asked for.",
      "fix": "Remove, or move to a separate justified and reviewed change.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "Compare request.md ('loads the demand-forecast model') with the module's function list."
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py load_model: urlopen(MODEL_URL) without timeout",
      "scenario": "Model host accepts TCP but never responds; default socket timeout is None so the job hangs and docks are not rebalanced.",
      "fix": "Pass timeout=, add bounded retries, raise a clear error, alert.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "Scratch, not run: local listener that accepts and never writes; point MODEL_URL at it; load_model() never returns."
    },
    {
      "id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "forecast.py MODEL_URL '.../demand-latest.pkl'",
      "scenario": "An unvalidated model is published to 'latest'; rebalancing behavior changes without a deploy and the model used cannot be identified afterwards.",
      "fix": "Reference an immutable versioned artifact plus digest in config; log version and digest at load.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "Swap the file at the URL between two runs; the second run loads the new model with no log or error."
    },
    {"id": "NV1", "status": "needs_validation", "location": "MODEL_URL host models.example.test", "suspicion": "Reserved .test TLD may be a placeholder that never resolves", "unresolved_fact": "Output of getent hosts models.example.test on the ops server"},
    {"id": "NV2", "status": "needs_validation", "location": "load_weather_adapter repo id", "suspicion": "pedalo-labs namespace may not be owned by the organization", "unresolved_fact": "HF Hub org ownership and member list"},
    {"id": "NV3", "status": "needs_validation", "location": "deployment of the rebalancing job", "suspicion": "Loader runs in the same process that holds credentials", "unresolved_fact": "Job deployment config showing credential exposure"},
    {"id": "NV4", "status": "needs_validation", "location": "load_weather_adapter from_pretrained weights", "suspicion": "Weights may be loaded through pickle-based torch.load", "unresolved_fact": "Installed transformers/torch versions and whether the repo ships only safetensors"},
    {"id": "NV5", "status": "needs_validation", "location": "load_weather_adapter AutoModel", "suspicion": "AutoModel may be the wrong class for the adapter", "unresolved_fact": "Adapter config architecture"}
  ],
  "refuted": [
    {"id": "R1", "candidate": "HTTP error pages would be unpickled as the model", "evidence": "urllib.request.urlopen raises HTTPError for 4xx/5xx by default"},
    {"id": "R2", "candidate": "Hardcoded secrets in the module", "evidence": "No tokens or credentials appear in forecast.py"},
    {"id": "R3", "candidate": "Reviewer-directed instructions in the work", "evidence": "No such text in forecast.py"}
  ]
}
```