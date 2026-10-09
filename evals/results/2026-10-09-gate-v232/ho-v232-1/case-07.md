VERDICT: **SHIP WITH FIXES**. The spend caps (input length, turns, tokens, per-rider and global rate limits) are coherent and bounded, but the tool-use loop drops the model's own tool call from the conversation, so the endpoint's core path (routing tool, then answer) probably does not work, and no test exercises it.

CONFIDENCE: **medium**. Limits:
- Single reviewer with no tools, so nothing was run. Every reproduction below is a trace or a proposed test.
- The `llm` wrapper, the routing tool, the HTTP layer that builds `request`, and the deployment config were not supplied.
- The work was not produced in this conversation, but no fresh subagent was available.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `planner.py`, `test_planner.py`.
- **Not seen, and it matters:**
  - The `llm` wrapper. It decides message format, what `tokens` counts, timeouts and system prompt.
  - The HTTP/auth layer that fills `request["rider"]`. It decides whether `rider` is spoofable.
  - The routing tool. It decides cost and what its error text can leak.
  - Deployment config (worker and process count). It decides whether the in-process limits are real limits.
  - The frontend rendering of `answer`.
- **Not seen, does not matter:** the CI run behind "9 tests pass". My trace agrees they would pass.

COVERAGE:
- **Scope:** the whole work (two files).
- **Checked:**
  - `request.md` and `context.md`.
  - `planner.py`: `_run`, `plan`, the constants and module state.
  - All 9 tests in `test_planner.py`, including whether each would fail under a mutation.
- **Not checked:**
  - `llm` wrapper, routing tool, auth layer, deploy config: `not_supplied`.
  - Runtime behaviour: `no_tools`.

SEATS AND GATE:
- One local reviewer (this session).
- No cross-vendor seats; none were requested and the depth is standard.
- Sensitivity gate passed: no personal or confidential data in the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | PROBABLE | B | `planner.py:32-38` | After a tool call, only `{"role":"tool","content":...}` is appended. The model's own tool-call turn (tool name, args, call id) is never added to `messages`. | **Conditions:** a rider asks a routing question, the model calls the routing tool, then `_run` sends the next turn. **What goes wrong:** both major chat APIs reject a tool result with no preceding assistant tool call (role `tool` without a `tool_call_id`; Anthropic has no `tool` role). The call errors, and per F3 that becomes an unhandled exception. If a wrapper tolerates it, the model sees a result it has no record of requesting and may call the tool again until "turn limit". Either way the core feature fails. | **Fix:** append the assistant turn (tool name, args, id) before the tool result, in whatever format the wrapper expects. Add a test where the model calls the tool once and then answers.<br>**Reproduction:** stub `llm` returning `{"tool":"route","args":{},"tokens":5}` on call 1. On call 2, assert that some message before the `tool` message records the tool call. This fails on the current code. Against a real API, any routing question returns an error. | a✓ b✗ c✓ d✓ |
| F2 | Medium | CONFIRMED | B | `test_planner.py:41-44`; `planner.py:26`, `planner.py:30-31` | The budget test only checks the first call's `max_tokens`. No test drives `spent` past `MAX_TOKENS`, so both token-cap mechanisms are unguarded. | **Conditions:** a later edit changes line 26 to `max_tokens=MAX_TOKENS`, or deletes lines 30-31. **What goes wrong:** all 9 tests still pass. The highest-spending test uses 50 tokens total. Per-request spend silently rises to 5 × 15000 tokens. | **Fix:** add (1) a two-turn test asserting the second `max_tokens == MAX_TOKENS - first_tokens`, and (2) a test whose stub reports 16000 tokens, expecting `{"error":"token budget"}`.<br>**Reproduction:** in a scratch copy, apply either mutation and run `python -m unittest test_planner`. All 9 tests pass. | a✓ b✓ c✗ d✗ |
| F3 | Medium | CONFIRMED | B | `planner.py:26`, `planner.py:59-62` | Only `Refused` is caught. Any exception from `llm` escapes `plan`: provider 429/5xx, timeout, or bad request (including F1's malformed history). | **Conditions:** the provider errors or times out. **What goes wrong:** `plan` raises instead of returning `{"error":...}`, the framework returns a raw 500, and the rider's rate-limit slot is still consumed. Not High: the framework most likely turns this into a 500, and per request it is occasional, not typical. | **Fix:** catch provider exceptions around the `llm` call and map them to `{"error":"planner unavailable"}`. Log them without the question text.<br>**Reproduction:** `plan({"rider":"u","question":"q"}, lambda m, max_tokens=None: (_ for _ in ()).throw(RuntimeError("503")), {})`. Expected an error dict; observed `RuntimeError` raised. | a✓ b✓ c✗ d✗ |
| F4 | Medium | PROBABLE | B | `planner.py:11-13`, `planner.py:50-58` | Rate-limit state is a module-level dict and list behind a `threading.Lock`. It is per-process and lost on restart. | **Conditions:** the app runs under N worker processes or instances, which is typical for production Python. **What goes wrong:** the real ceilings become 30·N per rider per hour and 2000·N globally. Every restart or deploy resets them. The spend ceiling in the docstring and the context does not hold. | **Fix:** keep the counters in a shared store (for example Redis INCR with TTL), or document and enforce a single-process deployment.<br>**Reproduction:** run two processes importing `planner`. Send 30 requests for one rider to each; all 60 are accepted. Expected: 30. | a✓ b✗ c✗ d✓ |
| F5 | Low | CONFIRMED | B | `planner.py:30`, `planner.py:26` | The budget check is `>`, so `spent == MAX_TOKENS` continues to another turn with `max_tokens=0`. Providers reject 0, so this becomes an F3-style exception. | **Conditions:** a tool turn brings `spent` to exactly 15000. **What goes wrong:** the next call is made with `max_tokens=0` and fails. | **Fix:** use `>=`, or refuse when the remaining budget is ≤ 0 before calling.<br>**Reproduction:** stub `llm` returns a tool call with `tokens=15000`, then records `max_tokens`. Observed: second call with `max_tokens=0`. Expected: `{"error":"token budget"}` with no second call. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED | B | `planner.py:21` | An empty string passes validation and triggers a billed model call. Some providers also reject empty content, which leads to F3. | **Conditions:** a rider sends `{"question": ""}` or whitespace. **What goes wrong:** a model call is made (and billed) for nothing. | **Fix:** reject `not question.strip()`.<br>**Reproduction:** `plan({"rider":"u","question":""}, recording_llm, {})`. Observed: one `llm` call. Expected: `{"error":"question not accepted"}` and zero calls. | a✓ b✓ c✗ d✗ |
| F7 | Low | CONFIRMED | B | `planner.py:57` | Rider keys in `_seen` are never deleted. Stale timestamps are pruned only when that rider calls again. | **Conditions:** a long-running process serves many distinct riders. **What goes wrong:** memory grows without bound. The growth rate is capped at about 2000 keys per hour by the global limit. | **Fix:** periodically evict keys whose newest hit is more than 3600 s old, or use a TTL store (see F4).<br>**Reproduction:** call `plan` for riders `r0..r99` at t=0. At t=4000, call for `r100`. Observed: `len(_seen) == 101`. Expected: 1. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

These have no severity and do not set the verdict.

- **S1, rider spoofing** (`planner.py:47`). Is `request["rider"]` set only from a verified session, or can the client's JSON body supply or override it? The tests pass `rider` and `question` in one dict. If the body can set it, auth and per-rider limits are bypassed (Critical): anyone can spend up to the global cap.
- **S2, unscoped agent** (`planner.py:23`). Does the `llm` wrapper add a system prompt that limits the agent to bike routing? The code sends only the raw question. Without a scope, the endpoint is a general-purpose LLM billed to Pedalo, which is drift from the request.
- **S3, what `tokens` counts** (`planner.py:27-29`). Does `reply["tokens"]` include input tokens? History grows by up to 4000 characters per tool turn. If only output is counted, input spend is not covered by `MAX_TOKENS`.
- **S4, tool error leakage** (`planner.py:35-36`). Can the routing tool's exception messages contain upstream URLs, API keys or internal hosts? `f"error: {exc}"` goes to the model, and the model can repeat it to the rider.
- **S5, answer rendering** (`planner.py:60`). Does the rider site render `answer` as HTML or markdown? The answer is shaped by the question and by tool data such as place names, so it needs escaping and no auto-loaded images.
- **S6, timeouts.** Do the `llm` wrapper and the routing tool have timeouts? `_run` has none, so a hang holds a worker.
- **S7, exhausting the global cap.** Is sign-up free or automatable? About 67 accounts at 30 requests each fill the 2000/hour global cap and lock out every legitimate rider with "busy".

## REFUTED

- **Rate-limit race:** the check and the record both happen under `_lock` (`planner.py:50-58`).
- **Unknown tool name or non-dict `args` crashes the request:** the `KeyError` or `TypeError` is raised inside the `try` (`planner.py:33-36`) and returned to the model as text.
- **Rejected requests inflate the counters:** "rate limit" and "busy" return before `_seen` and `_all` are updated (`planner.py:53`, `planner.py:56`).
- **The global-limit test leaks its mutated constant:** the `finally` block restores it (`test_planner.py:38-39`), and `plan` reads the module global at call time.
- **Negative or bool `tokens` bypass the budget:** the value comes from the provider via the wrapper, not from the rider, so there is no lower-trust principal.

## WHAT HOLDS UP

- Login and length checks run before any model call; tests confirm this.
- The turn cap holds: `test_planner.py:10-15` would go red under an unbounded loop.
- Per-rider and global checks are correct within one process, with sliding windows and the lock covering check and record.
- The remaining-budget `max_tokens` design is sound, though under-tested (F2).
- Tool output is truncated to 4000 characters.
- Missing token counts and missing answers are refused.

## UNVERIFIED CLAIMS

- **"9 tests pass":** not run here. My trace agrees they should pass.
- **Docstring "caps on ... tokens":** true per process and per request for whatever `tokens` counts (S3, F4).
- **"Signed-in riders only":** depends on S1.

## QUESTIONS FOR THE AUTHOR

1. Where does `request["rider"]` come from, and can the request body set it? (S1)
2. What message format does `llm` expect for tool calls and results, and does it add a system prompt? (F1, S2)
3. How many worker processes and instances run in production? (F4)

## DECISION-MAKER SUMMARY

Fix F1 and prove it with a tool-then-answer test. Add the token-cap tests (F2). Catch provider errors (F3). Answer S1 before launch, because a spoofable `rider` would make this Critical.

If shipped as is, routing questions will probably fail. The billing caps are also weaker than stated under multiple workers and are unprotected against regression.

## OWNER SUMMARY

The cost controls on the trip planner are well designed. However, the part that calls the routing tool and then answers probably does not work as written, and nothing tests it. A few small fixes are needed, plus confirmation that rider identity cannot be faked, before launch.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "planner.py", "status": "seen", "matters": true},
    {"item": "test_planner.py", "status": "seen", "matters": true},
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "routing tool", "status": "not_seen", "matters": true},
    {"item": "HTTP/auth layer populating request['rider']", "status": "not_seen", "matters": true},
    {"item": "deployment config (worker count)", "status": "not_seen", "matters": true},
    {"item": "frontend rendering of answer", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "planner.py", "kind": "file"},
      {"unit": "planner.py:_run", "kind": "function"},
      {"unit": "planner.py:plan", "kind": "function"},
      {"unit": "test_planner.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "llm wrapper", "reason": "not_supplied"},
      {"unit": "routing tool", "reason": "not_supplied"},
      {"unit": "HTTP/auth layer", "reason": "not_supplied"},
      {"unit": "deployment config", "reason": "not_supplied"},
      {"unit": "runtime execution of tests", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:32-38",
     "scenario": "A rider asks a routing question and the model calls the routing tool; the next turn's history holds a tool result with no preceding assistant tool call, so the provider rejects it or the model loops to the turn limit; the core feature fails.",
     "fix": "Append the assistant tool-call turn (name, args, id) before the tool result in the format the llm wrapper expects; add a tool-then-answer test.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Stub llm: call 1 returns {'tool':'route','args':{},'tokens':5}; on call 2 assert a message before the 'tool' message records the tool call. Fails on current code.",
     "security": false,
     "siblings_searched": {"searched": "every place messages is built or appended in planner.py", "found": "only planner.py:23 (initial user turn) and planner.py:37; no other construction site"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_planner.py:41-44",
     "scenario": "Changing planner.py:26 to max_tokens=MAX_TOKENS or deleting planner.py:30-31 leaves all 9 tests green; per-request spend silently rises to 75000 tokens.",
     "fix": "Add a two-turn test asserting the second max_tokens equals MAX_TOKENS minus the first reply's tokens, and a test where a reply reports 16000 tokens expecting 'token budget'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy apply either mutation, run python -m unittest test_planner; all 9 pass."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:59-62",
     "scenario": "The provider returns 429/5xx or times out; the exception escapes plan, the rider gets a raw 500, and the rate-limit slot is still consumed.",
     "fix": "Catch provider exceptions around the llm call and return {'error': 'planner unavailable'}.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "plan({'rider':'u','question':'q'}, llm that raises RuntimeError, {}); expected an error dict, observed RuntimeError raised."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:11-13",
     "scenario": "Under N worker processes the per-rider and global caps become 30*N and 2000*N per hour, and reset on every restart.",
     "fix": "Move the counters to a shared store (e.g. Redis INCR with TTL) or enforce single-process deployment.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Two processes importing planner each accept 30 requests for the same rider; 60 accepted, expected 30."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:30",
     "scenario": "spent reaches exactly 15000 on a tool turn; the next call is made with max_tokens=0 and the provider rejects it.",
     "fix": "Use >= or refuse when the remaining budget is <= 0 before calling.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Stub returns a tool call with tokens=15000, then records max_tokens; observed a second call with max_tokens=0."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:21",
     "scenario": "An empty or whitespace question passes validation and triggers a billed model call.",
     "fix": "Reject when not question.strip().",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "plan({'rider':'u','question':''}, recording llm, {}); observed one llm call, expected a refusal and zero calls."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:57",
     "scenario": "Rider keys in _seen are never deleted, so memory grows without bound in a long-running process.",
     "fix": "Evict keys whose newest hit is older than 3600 s, or use a TTL store.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call plan for riders r0..r99 at t=0, then for r100 at t=4000; len(_seen)==101, expected 1."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "planner.py:47",
     "suspicion": "request['rider'] may be client-controlled, bypassing login and per-rider limits.",
     "unresolved_fact": "Whether the HTTP layer sets rider only from a verified session and strips it from the body."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "planner.py:23",
     "suspicion": "No system prompt scopes the agent to bike routing, making it a general LLM billed to Pedalo.",
     "unresolved_fact": "Whether the llm wrapper injects a scoping system prompt."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "planner.py:27-29",
     "suspicion": "Input tokens may not be counted toward MAX_TOKENS.",
     "unresolved_fact": "What reply['tokens'] counts in the llm wrapper."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "planner.py:35-36",
     "suspicion": "Tool exception text may carry secrets or internal URLs into the model context and on to the rider.",
     "unresolved_fact": "What the routing tool's exceptions contain."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "planner.py:60",
     "suspicion": "Model answer may be rendered unescaped (HTML/markdown/image links).",
     "unresolved_fact": "How the rider site renders answer."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "planner.py:26",
     "suspicion": "No timeouts on llm or tool calls.",
     "unresolved_fact": "Whether the wrapper and the routing tool set timeouts."},
    {"id": "S7", "status": "needs_validation", "track": "D", "location": "planner.py:55-56",
     "suspicion": "About 67 accounts can exhaust the global cap and lock out all riders.",
     "unresolved_fact": "Whether account sign-up is free or automatable."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Race between the rate-limit check and the record.", "evidence": "Both happen under _lock at planner.py:50-58."},
    {"id": "C2", "candidate": "An unknown tool name or non-dict args crash the request.", "evidence": "KeyError/TypeError are raised inside the try at planner.py:33-36 and returned to the model as text."},
    {"id": "C3", "candidate": "Rejected requests inflate the counters.", "evidence": "Early returns at planner.py:53 and planner.py:56 precede the updates at 57-58."},
    {"id": "C4", "candidate": "The global-limit test leaks its mutated constant.", "evidence": "The finally block at test_planner.py:38-39 restores it."},
    {"id": "C5", "candidate": "Negative or bool tokens bypass the budget.", "evidence": "The value is provider-reported via the wrapper, not rider-controlled; no lower-trust principal."}
  ]
}
```