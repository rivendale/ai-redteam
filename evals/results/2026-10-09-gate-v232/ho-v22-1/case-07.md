**Review note:** single reviewer, no tools, no fresh subagent. Nothing was run. Findings come from tracing the supplied code by hand. Re-run with tools before launch.

---

**VERDICT: SHIP WITH FIXES.** The caps on input, turns, tokens, per-rider requests and global requests are correctly built and serialized. However, there are two open questions about where the code is deployed (where `rider` comes from, and how many processes run it). Either one could turn this into REWORK, and both must be answered before launch.

**CONFIDENCE: medium-low.** There were no tools, so nothing was executed or mutation-tested. The LLM wrapper, routing tool, HTTP binding and deployment topology were not supplied.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, `planner.py`, `test_planner.py`.
- **Not seen:**
  - The `llm` wrapper: what `tokens` counts, whether a system prompt is injected, timeouts. **Matters.**
  - The routing tool implementation. Matters for error leakage.
  - The HTTP handler that builds `request`: is `rider` set from the session or from the body? **Matters, possibly Critical.**
  - Deployment: number of worker processes or hosts. **Matters.**
  - The test run output. "9 tests pass" is asserted, not seen.
  - How the front end renders `answer`. Matters for XSS.

**COVERAGE**
- **Checked:** `planner.py:_run`, `planner.py:plan`, the module-level counters and lock, and all 9 tests in `test_planner.py`.
- **Not checked:** the LLM client, the tools, the HTTP and auth layer, deployment config, front-end rendering.

**SEATS AND GATE:** One local reviewer. No cross-vendor seats; none were requested and no tools were available. Sensitivity gate passed: the work is code and contains no personal data or secrets.

---

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | `planner.py:_run`, `reply = llm(...)` / `reply.get(...)`; `plan` catches only `Refused` | Only `Refused` is caught. Any other exception escapes `plan` and becomes an unhandled 500. That includes a network or timeout error from `llm` and an `AttributeError` when `reply` is not a dict (e.g. `None`). | The provider times out or returns malformed output. The rider gets a 500, possibly with a framework traceback. The rate-limit slot is still consumed. | Wrap the `_run` call: catch `Exception`, log it, return `{"error": "unavailable"}`. Repro: `plan({"rider":"r","question":"q"}, lambda m, max_tokens=None: None, {})` raises `AttributeError` instead of returning an error dict. | a✓ b✓ c✗ d✓ (provider errors are routine) → Medium |
| F2 | Medium | PROBABLE | D/B | `planner.py:_run`, `messages = [{"role": "user", "content": question}]` | No system prompt or scope restriction is set here. The request was an agent that answers "A to B by bike" questions. As written, the endpoint is a general chatbot billed to Pedalo. | A rider sends "write my 900-char essay prompt…" 30×/hour. Each call can spend up to 15k tokens on off-topic work. | Prepend a system message limiting the model to bike route planning, or confirm the `llm` wrapper does this. Test: assert that `messages[0]["role"] == "system"` in the first `llm` call. | a✓ b✗ c✗ d✓ → Medium |
| F3 | Medium | CONFIRMED (traced) | B | `test_planner.py`, all tests; `planner.py` `if spent > MAX_TOKENS` | The token-budget refusal path has no test. The longest test spends 5×10 = 50 tokens. | Delete the `spent > MAX_TOKENS` check and all 9 tests still pass. A future refactor can silently remove the main billing cap. | Add a test where the LLM returns `{"tool":"t","args":{},"tokens":9000}` and assert `{"error":"token budget"}` within 2 calls. Also add tests for: a tool raising an exception, an unknown tool name, and rate-limit window expiry (t+3601 is allowed again). | a✓ b✓ c✗ d✗ → Medium |
| F4 | Low | CONFIRMED (traced) | B | `planner.py:plan`, `_seen[rider] = hits + [now()]` | `_seen` keys are never deleted. A rider's timestamps are pruned only when that rider calls again. | Memory grows with the number of distinct riders over the process lifetime. This is minor if riders are authenticated (see S1). | Periodically prune empty or stale keys, or use a TTL store. | a✓ b✓ c✗ d✗ → Low |
| F5 | Low | CONFIRMED (traced) | B | `planner.py:_run`, `isinstance(reply.get("tokens"), int)` | `True` and negative ints pass the check. A negative count lowers `spent` and raises the next `max_tokens` above `MAX_TOKENS`. | This only happens if the wrapper ever reports a negative or bool count, for example from a provider bug or a mapping error. | Require `type(t) is int and t >= 0`. | a✓ b✓ c✗ d✗ → Low |

### NEEDS VALIDATION
- **S1:** where `request["rider"]` comes from (`planner.py:plan`).
  - If it is read from the POST body, which the tests' `{"rider": ..., "question": ...}` shape hints at, then any anonymous caller can set an arbitrary rider. Both the login check and the per-rider limit are bypassed by rotating IDs, and only the 2000/hour global cap remains.
  - **Settling fact:** the HTTP handler code showing that `rider` is set from the authenticated session and that body keys cannot override it.
- **S2:** whether production runs more than one worker process or host.
  - `_seen`, `_all` and `_lock` are per-process memory. With N workers, the effective caps become 30·N per rider and 2000·N global, and they reset on every restart or deploy.
  - **Settling fact:** the worker count in the deployment config. If it is more than 1, move the counters to a shared store such as Redis.
- **S3:** what `reply["tokens"]` counts.
  - If it counts completion tokens only, re-sent history (input tokens) is billed but never counted. Real spend per request could be several times 15k.
  - **Settling fact:** the `llm` wrapper's source.
- **S4:** whether tool exception text can leak secrets.
  - `result = f"error: {exc}"` is fed to the model and can be echoed to the rider. For example, an HTTP client error whose message includes a URL with an API key would reach the rider.
  - **Settling fact:** the routing tool's error messages.
- **S5:** whether `answer` (model output) is rendered as HTML on the rider site.
  - If so, it is an XSS vector, since a crafted question can steer the model's output.
  - **Settling fact:** the front-end rendering code.
- **S6:** whether `llm` and the tool calls have timeouts.
  - If not, a hung provider ties up a worker indefinitely.
  - **Settling fact:** the client config.

### REFUTED
- **Race on the rate-limit counters.** The read, check and append all happen inside `with _lock`.
- **Turn loop never ends.** `for _ in range(MAX_TURNS)` bounds it, and `test_a_model_that_never_stops_is_cut_off` asserts this.
- **Malformed tool name or args crash the request.** The `KeyError` or `TypeError` is caught and returned to the model as `error: …`.
- **Oversized tool output inflates context.** It is truncated to 4000 chars.
- **Over-long question reaches the model.** It is rejected before any call, and a test covers it.

### WHAT HOLDS UP
- The input length cap and type check run before any model call.
- The turn cap holds.
- `max_tokens` is shrunk to the remaining budget on each call.
- A reply without a token count is refused rather than treated as free.
- The rate-limit slot is consumed even when the run later fails, so failed calls can't be spammed for free.
- The global ceiling is enforced, and the time window is injectable for tests.

### UNVERIFIED CLAIMS
- "9 tests pass": run `python -m unittest test_planner`.
- "Signed-in riders only" (docstring): depends on S1.
- "caps … tokens": real billed tokens depend on S3.

### QUESTIONS FOR THE AUTHOR
1. Is `rider` taken from the authenticated session, and can a body field override it?
2. How many worker processes or hosts serve `/plan`?
3. Does `tokens` include prompt tokens, and does the `llm` wrapper add a scoping system prompt?

### DECISION-MAKER SUMMARY
The limit logic is sound in-process. Launch depends on confirming that the rider identity comes from the login session and that the counters are shared across workers. Otherwise anyone can bypass the per-rider limits and run up model costs. Fix the uncaught provider errors and add the missing budget test before launch.

### OWNER SUMMARY
The trip planner's spending limits are built correctly in principle, but two things about how it will run in production still need checking. Without those checks, people may be able to use far more paid AI time than intended. A few smaller fixes, like handling outages gracefully and adding one missing test, should go in before launch.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "low",
  "inputs_ledger": [
    {"item": "planner.py", "status": "seen", "matters": true},
    {"item": "test_planner.py", "status": "seen", "matters": true},
    {"item": "HTTP handler / auth binding for request['rider']", "status": "not_seen", "matters": true},
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "routing tool implementation", "status": "not_seen", "matters": true},
    {"item": "deployment worker topology", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; no personal data or secrets."},
  "coverage": {
    "checked": [
      {"unit": "planner.py", "kind": "file"},
      {"unit": "planner.py:_run", "kind": "function"},
      {"unit": "planner.py:plan", "kind": "function"},
      {"unit": "test_planner.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "llm wrapper", "reason": "not supplied"},
      {"unit": "routing tool", "reason": "not supplied"},
      {"unit": "HTTP/auth layer", "reason": "not supplied"},
      {"unit": "deployment config", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:_run (reply = llm(...)); plan catches only Refused",
     "scenario": "Provider timeout or a non-dict reply raises a non-Refused exception that escapes plan as an unhandled 500, after the rate-limit slot is consumed.",
     "fix": "Catch Exception around _run, log it, return a generic error dict.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "plan({'rider':'r','question':'q'}, lambda m, max_tokens=None: None, {}) raises AttributeError; expected an error dict."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "planner.py:_run messages initialisation",
     "scenario": "No system prompt scopes the agent to bike routing, so riders can use it as a general chatbot billed to Pedalo, up to 15k tokens x 30/hour each.",
     "fix": "Prepend a scoping system message (or confirm the llm wrapper adds one) and test that it is present.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_planner.py (all tests) vs planner.py 'if spent > MAX_TOKENS'",
     "scenario": "Deleting the token-budget check leaves all 9 tests green, since the max test spend is 50 tokens, so the billing cap can regress silently.",
     "fix": "Add tests for budget exhaustion, tool exceptions, unknown tool, and rate-window expiry.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Remove the spent > MAX_TOKENS check; run unittest; observe 9 passes."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:plan _seen[rider] = hits + [now()]",
     "scenario": "Rider keys are never evicted, so memory grows with distinct riders over the process lifetime.",
     "fix": "Evict stale keys periodically or use a TTL store.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:_run isinstance(reply.get('tokens'), int)",
     "scenario": "A negative or bool token count passes the check; a negative count reduces spent and lifts max_tokens above the cap.",
     "fix": "Require type(t) is int and t >= 0.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "planner.py:plan request.get('rider')",
     "suspicion": "If rider comes from the request body, auth and per-rider limits are bypassable by setting arbitrary rider IDs.",
     "unresolved_fact": "Whether the HTTP handler sets rider from the authenticated session and prevents body override."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "planner.py module globals _seen/_all/_lock",
     "suspicion": "Per-process counters multiply limits by worker count and reset on restart.",
     "unresolved_fact": "Number of worker processes/hosts in production."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "planner.py:_run spent += reply['tokens']",
     "suspicion": "If tokens counts only completion tokens, re-sent input history is billed but uncounted.",
     "unresolved_fact": "What the llm wrapper reports in 'tokens'."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "planner.py:_run result = f'error: {exc}'",
     "suspicion": "Tool exception text (possibly containing secrets or URLs) is fed to the model and may be echoed to riders.",
     "unresolved_fact": "Content of routing tool exception messages."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "planner.py:plan return {'answer': ...}",
     "suspicion": "Model output rendered as HTML would be an XSS vector.",
     "unresolved_fact": "How the rider site renders the answer."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "planner.py:_run llm(...) and tools[...](...)",
     "suspicion": "No timeouts visible; a hung provider or tool blocks a worker indefinitely.",
     "unresolved_fact": "Timeout configuration of the llm client and routing tool."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Race condition on rate-limit counters.", "evidence": "Read, check and append all occur inside 'with _lock'."},
    {"id": "C2", "candidate": "Agent loop can run unbounded.", "evidence": "for _ in range(MAX_TURNS) bounds it; covered by test_a_model_that_never_stops_is_cut_off."},
    {"id": "C3", "candidate": "Bad tool name/args crash the request.", "evidence": "KeyError/TypeError caught by except Exception and returned to the model."},
    {"id": "C4", "candidate": "Over-long question reaches the model.", "evidence": "Length check precedes any llm call; covered by test_a_long_question_is_refused_before_any_model_call."}
  ]
}
```