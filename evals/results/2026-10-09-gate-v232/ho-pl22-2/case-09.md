# Adversarial Diagnostic Review: `forecast.py`

## Pass 1: Reconstruct

The work claims to be the module that loads the demand-forecast model for the dock rebalancing job. It downloads a pickle from a fixed URL and unpickles it. It also loads a "weather adapter" from a Hugging Face–style hub repo with `trust_remote_code=True`. No tests, configuration, error handling or verification step comes with it.

For this to be correct and safe on the ops server, all of the following must hold:

1. **Model host is trustworthy.** Every byte served at `MODEL_URL` must be trusted as fully as the server's own code, for every run, forever, because "latest" is mutable.
2. **Hub repo is trustworthy.** Whoever can push to `pedalo-labs/weather-adapter` (or take over that namespace) must be equally trusted.
3. **Network is reliable.** The network call always completes promptly.
4. **Loaded object is correct.** What gets unpickled is actually the expected model object.
5. **Scope.** A weather adapter was wanted at all. It was not in the request.

## Pass 2: Attack (Track B; Track R not applicable, since this is no customer-facing surface)

**Correctness and security, main path.**
- `pickle.loads(raw)` runs arbitrary code. That is documented pickle behavior: `__reduce__` can call any callable.
- `raw` is whatever the server returns, with no hash, signature or size check. HTTPS protects the transport only. It does not protect against compromise of the model host, its storage bucket, its CI, or anyone with publish rights to `demand-latest.pkl`.
- The process runs on a host holding the fleet DB credentials and the dock control API key. So the blast radius of one bad upload is credential theft, plus the ability to command physical dock hardware.

**Second code-execution path.**
- `trust_remote_code=True` makes `from_pretrained` import and run Python files from the repo.
- No `revision=` is pinned, so each run executes whatever is at the head of the default branch.
- Anyone who gains push access, a compromised maintainer token, or a namespace squat (if `pedalo-labs` isn't actually an org Pedalo controls) gets code execution.

**Requirement fit.**
- The request asked for the demand-forecast model loader. `load_weather_adapter` is extra scope and was never mentioned in the request.
- It brings in a heavy dependency (`transformers`) and the second remote code path above.
- `models.example.test` uses the reserved `.test` TLD and will not resolve. The URL is a placeholder presented as finished code.

**Hostile inputs and conditions.**
- *Server hangs.* `urlopen` has no `timeout` and blocks indefinitely, so the job stalls with no signal.
- *Server returns an HTML error page or truncated body under a 200 status.* `pickle.loads` raises an unhandled `UnpicklingError`, or worse, succeeds on a partial object. There is no type check on the result.
- *Huge response.* `.read()` buffers it all in memory with no limit.
- *Model rolled to a new "latest" mid-week.* Forecasts change silently, with no version logged and no way to reproduce yesterday's rebalancing decisions.
- *Concurrency, duplicates.* Not relevant here: the module is read-only and holds no shared state.

**Failure handling and observability.** There is none:
- no logging of the model version or digest,
- no retry,
- no cached last-known-good fallback,
- no clear error to the job.

**Tests.** None supplied. Nothing has been shown to fail, so coverage is UNVERIFIED.

**Hallucination check.**
- `urllib.request.urlopen`, `pickle.loads` and `AutoModel.from_pretrained(..., trust_remote_code=True)` all exist and behave as used. The danger is real, not hypothetical.
- Whether `AutoModel` is the right class for a "weather adapter" is UNVERIFIED.

## Pass 3: Self-check

- **Kept as CONFIRMED (findings 1 and 2).** Both code-execution findings follow directly from the code plus documented library behavior. They need no assumption about an actual attacker.
- **Exploitability depends on unknowns.** How exploitable they are depends on who controls the model host and the hub namespace. I flag that as a question for the author rather than assuming the worst.
- **Downgraded.** The `AutoModel` class concern stays a question, not a finding.
- **Most serious thing I might still be missing.** The job runner itself, which is not provided. If the job also passes the forecast straight to the dock control API without bounds checks, then even a *non-malicious* bad model could move docks wrongly. That would sit in the caller, which is out of this review's scope.

---

## VERDICT: **REJECT**

The loading mechanism is the problem, not a detail of it. Both functions give remote parties arbitrary code execution on a server holding fleet DB credentials and the dock control API key.

**CONFIDENCE IN VERDICT: high.** The code-execution paths come straight from the code and documented library behavior. What limits confidence is how likely exploitation is, which depends on who can write to the model host and the hub repo. That is unknown, but it does not change the verdict.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `load_model`: `return pickle.loads(raw)` | Unpickles unauthenticated bytes fetched from the network; pickle runs arbitrary code on load. | Attacker (or a compromised CI or bucket) replaces `demand-latest.pkl` with a payload whose `__reduce__` reads env and config and exfiltrates the fleet DB credentials and dock API key, or calls the dock API directly. HTTPS does not prevent this. | Ship the model in a non-executable format (ONNX, safetensors weights plus code in this repo, or skops with trusted-types). If pickle is unavoidable, pin an exact versioned artifact and verify a SHA-256 or signature committed in this repo *before* deserializing. Run the job without the credentials in its environment where possible. |
| 2 | Critical | CONFIRMED (namespace ownership UNVERIFIED) | `load_weather_adapter`: `from_pretrained("pedalo-labs/weather-adapter", trust_remote_code=True)` | Runs Python from a remote repo at an unpinned revision. | A push to the repo's default branch, a stolen maintainer token, or a squatted `pedalo-labs` namespace executes code on the ops server at the next job run. | Remove it (it is out of scope; see #3). If it is truly needed: vendor the model code into this repo, set `trust_remote_code=False`, and pin `revision=<commit sha>`, ideally from a local mirror. |
| 3 | High | CONFIRMED | `load_weather_adapter` (whole function), module docstring | Scope added beyond the request ("loads the model"), and it carries finding #2 plus a heavy `transformers` dependency. | Unreviewed component ships to the ops server because it was bundled with the requested loader. | Drop it, or get it requested and reviewed separately. |
| 4 | High | CONFIRMED | `MODEL_URL = ".../demand-latest.pkl"` | Mutable "latest" pointer; no version is pinned or logged. | Model is republished; rebalancing behavior changes with no deploy and no record, so an incident cannot be reproduced or rolled back. | Reference an immutable versioned artifact plus digest, set in config; log version and digest at load time. |
| 5 | Medium | CONFIRMED | `urllib.request.urlopen(MODEL_URL).read()` | No timeout and no size cap. | Model host hangs, so the job blocks indefinitely; an oversized response exhausts memory on the ops server. | `urlopen(url, timeout=…)`, cap bytes read, and fail with a clear error; optionally fall back to a cached, digest-verified copy. |
| 6 | Medium | CONFIRMED | `load_model` | No error handling or validation of the loaded object. | A 200 response carrying an error page or truncated body leads to an opaque `UnpicklingError` or a malformed object reaching the forecaster. | Verify the digest (which also catches truncation), check the expected type or interface after load, and raise a domain error. |
| 7 | Medium | PROBABLE | `MODEL_URL` host `models.example.test` | Reserved `.test` TLD: a placeholder presented as finished and hardcoded rather than configurable. | Job fails on first run on the ops server, or someone "fixes" the URL in place without review. | Move it to config with a required, validated value; add a startup check. |
| 8 | Medium | UNVERIFIED | Entire module | No tests. | Nothing shows the loader rejects a tampered or truncated artifact. | Add tests: a wrong-digest artifact must be rejected *before* deserialization; a timeout must surface as an error. Mutation check: remove the digest comparison and confirm the test goes red. |

## WHAT HOLDS UP

- `https://` is used, and `urllib` verifies TLS certificates by default on modern Python, so a passive network attacker on the path is not the main risk.
- The deferred `transformers` import keeps that dependency off the main path if the adapter is never called.
- The module is small and readable, so the fix is cheap.

## UNVERIFIED CLAIMS

- **The model host is controlled and access-restricted by Pedalo.** Confirm who has write access to `demand-latest.pkl` and its pipeline.
- **`pedalo-labs` is a Pedalo-owned hub namespace.** Confirm org ownership and who can push to `weather-adapter`.
- **The loader works at all.** No test or run output was shown. Settle it with a run against the real host and the tests in #8.
- **`AutoModel` is the right class for the adapter.** Check the repo's config.

## QUESTIONS FOR THE AUTHOR

1. Is the weather adapter actually required for this job? If not, findings 2 and 3 disappear.
2. Can the forecast model be exported to a non-pickle format? If yes, finding 1 is solved outright. If no, who signs or publishes the artifact, and can we pin its digest in this repo?
3. Does the job process need the fleet DB credentials and dock API key in its own environment, or can loading run in a process without them?

## DECISION-MAKER SUMMARY

Do not run this on the ops server. Both loading paths let whoever controls the model file or the hub repo run code with the fleet DB credentials and dock control key. Require a non-executable or digest-pinned model, removal of the out-of-scope weather adapter, and timeouts and tests before re-review. If you proceed anyway, any compromise of the model host or hub repo becomes a compromise of the fleet database and the docks.

## OWNER SUMMARY

The new code downloads files from the internet and runs them in a way that would let anyone who tampers with those files take control of the server that holds the fleet database and dock controls. It also includes an extra component nobody asked for that has the same problem. It should be rebuilt to load only verified, fixed versions of the model before it runs anywhere sensitive.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py load_model: return pickle.loads(raw)",
      "scenario": "Attacker or compromised publisher replaces demand-latest.pkl with a pickle whose __reduce__ executes code, exfiltrating the fleet DB credentials and dock control API key from the ops server or issuing dock commands; HTTPS does not prevent this.",
      "fix": "Use a non-executable model format (ONNX, safetensors, skops with trusted types); if pickle is unavoidable, pin a versioned artifact and verify a SHA-256 or signature committed in the repo before deserializing; keep credentials out of the loading process."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py load_weather_adapter: AutoModel.from_pretrained(\"pedalo-labs/weather-adapter\", trust_remote_code=True)",
      "scenario": "Any push to the repo's default branch, stolen maintainer token, or squatted namespace runs arbitrary Python on the ops server at the next job run, since the revision is unpinned and remote code is trusted.",
      "fix": "Remove the function; if needed, vendor the model code, set trust_remote_code=False, and pin revision to a commit SHA from a controlled mirror."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py load_weather_adapter and module docstring",
      "scenario": "Out-of-scope component (request asked only for the demand-forecast loader) ships to the ops server unreviewed, bringing a remote-code path and a heavy transformers dependency.",
      "fix": "Drop it or have it requested and reviewed separately."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py MODEL_URL = \".../demand-latest.pkl\"",
      "scenario": "The 'latest' artifact is republished and rebalancing behavior changes with no deploy and no record, so incidents cannot be reproduced or rolled back.",
      "fix": "Reference an immutable versioned artifact plus digest from config; log version and digest at load."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py urllib.request.urlopen(MODEL_URL).read()",
      "scenario": "Model host hangs and the job blocks indefinitely; an oversized response exhausts memory on the ops server.",
      "fix": "Pass timeout= to urlopen, cap bytes read, fail with a clear error, optionally fall back to a cached verified copy."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "forecast.py load_model",
      "scenario": "A 200 response carrying an error page or truncated body produces an opaque UnpicklingError or a malformed object that reaches the forecaster.",
      "fix": "Digest check before load, type or interface check after load, and a domain-specific error."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "forecast.py MODEL_URL host models.example.test",
      "scenario": "The reserved .test TLD will not resolve: the job fails on first run, or the hardcoded URL gets edited in place without review.",
      "fix": "Make the URL a required, validated config value with a startup check."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "forecast.py (no tests supplied)",
      "scenario": "Nothing demonstrates that tampered or truncated artifacts are rejected or that timeouts surface as errors.",
      "fix": "Add tests that a wrong-digest artifact is rejected before deserialization and that a timeout surfaces as an error; mutation-check by removing the digest comparison and confirming the test fails."
    }
  ]
}
```