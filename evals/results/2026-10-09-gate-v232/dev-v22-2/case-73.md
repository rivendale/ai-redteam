VERDICT: **SHIP WITH FIXES**. The agent loop and per-request caps are sound as written, but the confirmed defects (crash paths, no timeouts, a token cap that fails open and is untested, no global spend ceiling) should be fixed before announcement. The verdict assumes the unseen auth layer supplies `request["user"]`; if a client can set that field, the verdict becomes REJECT (see S1).

CONFIDENCE: **low**. I had no tools in this session, so nothing was run; all evidence comes from reading and tracing the code. The largest risks sit in inputs I was not given: the HTTP/auth layer, the LLM adapter and the tool set. This is an independent review (I did not author the work), but it is not execution-verified.

INPUTS LEDGER:
- Seen: the original request (verbatim), context.md, `agent.py`, `test_agent.py`.
- Not seen:
  - **The HTTP layer that builds `request`.** It matters: login and the rate limit both trust `request["user"]`.
  - **The `llm` adapter.** It matters: the token cap depends on what `"tokens"` reports.
  - **The `tools` dict.** It matters: a public user effectively chooses tool calls and arguments.
  - **The server concurrency model.** It matters for the rate-limit race and for hangs.
  - **Test run output.** The "6 tests pass" claim could not be re-run.

COVERAGE:
- Checked: `agent.py` (`run_agent`, `ask_endpoint`, the constants, the `_seen` state) and all 6 tests in `test_agent.py`, traced against the code.
- Not checked: the auth/HTTP layer, the LLM adapter, the tool implementations and the deployment/concurrency config, none of which were supplied.

SEATS AND GATE:
- One reviewer seat ran: this instance (Claude), local only.
- No cross-vendor seats; none were requested and depth is standard.
- Sensitivity gate: the inputs are source code with no personal data, credentials or client material, so the gate passed.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `agent.py:37`, `:51`, `:25` | Only `BudgetExceeded` is caught. A missing `answer`, a missing `question` or an LLM/network error escapes as an unhandled exception. | The model returns `{"tokens": 5}` (no tool, no answer), or a client POSTs `{}` without `question`. `KeyError` escapes `ask_endpoint`. The framework returns a 500, possibly with a traceback, after tokens were already paid and the user's quota slot consumed. | Validate the reply shape. Catch `Exception` in `ask_endpoint`, log it server-side and return a generic error. Repro: `ask_endpoint({"user":"u9","question":"q"}, lambda m: {"tokens":1}, {})` should return `{"error":…}` but raises `KeyError: 'answer'`. Likewise `ask_endpoint({"user":"u9"}, …)` raises `KeyError: 'question'`. | a✓ b✓ c✗ d✗ (legitimate clients send `question`; whether the adapter emits answer-less replies is unknown) |
| F2 | Medium | PROBABLE | B | `agent.py:25`, `:32` | There is no timeout on `llm(...)` or on tool calls, and no wall-clock cap per request. The module docstring says one process serves the endpoint. | A question steers a fetch-style tool at a slow or never-closing URL, or the LLM API stalls. The request never finishes. If the process has few workers, the endpoint stalls for every user. | Add per-call timeouts and an overall deadline checked in the loop, raised as `BudgetExceeded`. Repro: a tool `lambda: time.sleep(10**6)` makes `ask_endpoint` hang; expected: an error within N seconds. | a✓ b✗ c✗ d? |
| F3 | Medium | CONFIRMED | B | `agent.py:26-28` | The token cap fails open and is enforced only after billing. `reply.get("tokens", 0)` treats a missing count as 0. The check runs after the call is paid for, and no output cap is passed to `llm`. | If the adapter omits `"tokens"`, or counts only output tokens while each turn resends the growing history, the 20k cap never fires (only the 6-turn cap bounds spend). A single 1M-token reply is accepted, billed, and only then rejected. | Make a missing `tokens` an error. Count input plus output. Pass the remaining budget as max output tokens. Repro: an llm returning `{"tool":"t","args":{}}` with no `tokens` six times shows `spent` stays 0. `{"answer":"a","tokens":10**6}` returns the error only after the call. | a✓ b✓ c✗ d? |
| F4 | Medium | CONFIRMED (traced) | B | `test_agent.py` (all tests) | The per-request token cap and the rate-limit window expiry are never exercised. `test_a_model_that_never_stops_is_cut_off` spends 60 tokens, far below 20,000. Its two assertions would also pass vacuously if the request were refused before any call (error present, 0 calls). | Mutation: delete `agent.py:27-28`. All 6 tests still pass, so "6 tests pass" says nothing about the token cap. | Add a test with `tokens = MAX_TOKENS_PER_REQUEST + 1` asserting an error and exactly 1 call. Add a window test using the `now` parameter. In test 1, assert `calls == MAX_TURNS`. | a✓ b✓ c✗ d✓ → Medium (c✗ and it guards rather than breaks) |
| F5 | Medium | PROBABLE | A | `agent.py:9`, `:46-49` | Spend is capped per user only, with no global ceiling. Worst-case hourly exposure is (number of accounts) × 20 × (cost per request). | If sign-up is self-serve, a script creates 500 accounts and burns about 10,000 capped requests per hour against the billed account, with nothing tripping. | Add an account-wide hourly or daily token budget that fails closed, plus a spend alert. Settle whether sign-up is open (see questions). | a✓ b✗ c✗ d? |
| F6 | Low | CONFIRMED | B | `agent.py:10`, `:49` | `_seen` is in-process memory. It never evicts users who don't return, it resets on restart, and it is not shared across workers. | A restart (deploy or crash) resets every quota. Adding a second worker silently doubles the effective limit. Memory grows with user count. | Move to a shared store (for example Redis with TTL) or periodically prune empty entries. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1 (`agent.py:43-49`):** Is `request["user"]` set by authenticated session middleware, or is it client-supplied, for example from the JSON body as the tests model it?
  - If client-supplied: `{"user": "<random>"}` bypasses both the login check and the rate limit, giving unlimited billed calls.
  - A non-hashable `user` would also raise `TypeError` at `_seen.get`.
  - Settled by reading the route and auth handler that build `request`.
- **S2 (`agent.py:29-32`):** What is in `tools`?
  - The agent calls any tool the model names with any arguments it emits. On a public endpoint, the asker and any text in tool results (prompt injection) steer those calls.
  - Any tool with side effects, internal network reach (SSRF) or private data access is exposed.
  - Settled by the tool list, with each tool's network and permission scope.
- **S3 (`agent.py:46-49`):** Does the server run concurrent requests (threads or async workers)?
  - If so, the check-then-set on `_seen` lets a burst of simultaneous requests from one user pass and lose updates, exceeding 20 per hour. This also decides how bad F2 is.
  - Settled by the server and worker config.
- **S4 (`agent.py:26`):** What does the adapter's `"tokens"` field contain: input plus output, output only, or nothing?
- **S5 (`agent.py:34`):** Raw tool exception text is fed to the model and may be echoed to the public asker.
  - That text can include internal hostnames, file paths or URLs carrying keys.
  - Settled by the tools' exception messages.
- **S6:** "6 tests pass" could not be re-run here. Tracing suggests they do pass; confirm with the CI log or a local run.

## REFUTED

- *Unknown tool name crashes the request.* `tools[reply["tool"]]` sits inside the `try` at `:31-34`, so the `KeyError` becomes `"error: ..."`.
- *Non-dict `args` crashes `**` unpacking.* The resulting `TypeError` is raised inside the same `try` and caught.
- *Non-JSON-serializable tool result crashes the request.* `json.dumps(..., default=str)` at `:35` handles it.
- *A model that keeps calling tools loops forever.* `for _ in range(MAX_TURNS)` bounds it, and `:38` raises.
- *A non-string question crashes `len()`.* The `isinstance` check at `:18` runs first.
- *Refused requests dodge the rate limit.* The slot is recorded at `:49` before validation, so oversize or invalid requests still count.

## WHAT HOLDS UP

- The turn cap, the question length and type checks before any model call, and tool-result truncation are all correctly placed and covered by tests.
- Tool errors are contained inside the loop.
- The rate limiter's sliding-window logic is correct for a single-threaded, single-process server.
- No drift: the code does what was asked (loop on tools until it can answer, return the answer).

## UNVERIFIED CLAIMS

- "6 tests pass": run `python -m unittest test_agent`.
- "signed-in users only" (`:42`): read the auth layer (S1).
- "One process serves the endpoint" (`:1`): check the deploy config (S3, F6).
- The token cap being meaningful: depends on the adapter (S4).

## QUESTIONS FOR THE AUTHOR

1. Where does `request["user"]` come from, and can a client set it?
2. Which tools are registered, and can any of them write, send or reach internal hosts?
3. Is sign-up self-serve, and is there a billing-side hard cap on the model account?
4. Does the adapter return `tokens` as input plus output on every reply?

## DECISION-MAKER SUMMARY

Before announcing, confirm that the user identity comes from real authentication and list the tools the agent can call. If a client can set `user`, both the login check and the rate limit can be bypassed (S1). Then add a global spend ceiling and timeouts, make the token cap fail closed, and add the missing tests. Proceeding as-is risks runaway bills from scripted accounts and hung requests, and possibly unauthenticated, unlimited use.

## OWNER SUMMARY

The question-answering feature is mostly well built, but several safety limits are weaker than they look. Spending is limited per person but not overall, some limits are never actually tested, and slow or broken responses can hang or crash a request. Before going public, someone should confirm how users are identified and which actions the assistant is allowed to take, then add an overall spending cap.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "low",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "agent.py", "status": "seen", "matters": true},
    {"item": "test_agent.py", "status": "seen", "matters": true},
    {"item": "HTTP/auth layer that builds request", "status": "not_seen", "matters": true},
    {"item": "llm adapter", "status": "not_seen", "matters": true},
    {"item": "tools implementations", "status": "not_seen", "matters": true},
    {"item": "server concurrency/deploy config", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Source code only; no personal data, credentials or client material."},
  "coverage": {
    "checked": [
      {"unit": "agent.py", "kind": "file"},
      {"unit": "agent.py:run_agent", "kind": "function"},
      {"unit": "agent.py:ask_endpoint", "kind": "function"},
      {"unit": "test_agent.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "HTTP/auth layer", "reason": "not supplied"},
      {"unit": "llm adapter", "reason": "not supplied"},
      {"unit": "tools", "reason": "not supplied"},
      {"unit": "deploy/concurrency config", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:37, agent.py:51, agent.py:25",
     "scenario": "A model reply with neither tool nor answer, a request without 'question', or an LLM network error raises an uncaught exception from ask_endpoint, producing a 500 after tokens are billed and quota is consumed.",
     "fix": "Validate the reply shape; catch Exception in ask_endpoint, log server-side, return a generic error.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "ask_endpoint({'user':'u9','question':'q'}, lambda m: {'tokens':1}, {}) raises KeyError 'answer'; expected {'error': ...}."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:25, agent.py:32",
     "scenario": "A tool or LLM call that never returns hangs the request indefinitely; with one process serving the endpoint and few workers, all users stall.",
     "fix": "Add per-call timeouts and an overall request deadline that raises BudgetExceeded.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Register tool lambda: time.sleep(10**6); ask_endpoint hangs instead of returning an error within N seconds."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:26-28",
     "scenario": "If the adapter omits 'tokens' or counts only output tokens, the 20k cap never fires; a single oversized reply is billed before the cap rejects it.",
     "fix": "Treat a missing token count as an error, count input+output, pass the remaining budget as max output tokens.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "llm returning {'tool':'t','args':{}} with no 'tokens' for 6 turns leaves spent at 0; {'answer':'a','tokens':10**6} errors only after the call."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_agent.py (test_a_model_that_never_stops_is_cut_off and suite)",
     "scenario": "Deleting agent.py:27-28 leaves all 6 tests green, so the token cap and the rate-limit window expiry are unguarded; test 1 also passes vacuously if the request is refused before any call.",
     "fix": "Add a test with tokens=MAX_TOKENS_PER_REQUEST+1 asserting error and exactly 1 call; add a window-expiry test using now; assert calls == MAX_TURNS in test 1.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Remove agent.py:27-28 and run python -m unittest test_agent; expected a failure, observed (by trace) all pass."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "agent.py:9, agent.py:46-49",
     "scenario": "With self-serve sign-up, a script creates many accounts; each gets 20 capped requests per hour and total spend has no ceiling.",
     "fix": "Add an account-wide token budget that fails closed, plus a spend alert.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:10, agent.py:49",
     "scenario": "_seen is in-process: a restart resets every quota, a second worker doubles the effective limit, and entries for users who never return are never evicted.",
     "fix": "Use a shared store with TTL, or prune empty entries.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent.py:43-49",
     "suspicion": "If request['user'] is client-supplied, login and the rate limit are both bypassed by sending a random user value.",
     "unresolved_fact": "Whether the route sets request['user'] from an authenticated session or from the request body."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent.py:29-32",
     "suspicion": "Public askers and prompt-injected tool results steer arbitrary tool calls and arguments, exposing any side-effecting or internal-network tool.",
     "unresolved_fact": "The registered tool list and each tool's permissions and network reach."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent.py:46-49",
     "suspicion": "Under a threaded or async server, check-then-set on _seen lets concurrent bursts exceed the hourly limit.",
     "unresolved_fact": "The server's concurrency model."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent.py:26",
     "suspicion": "The token count may exclude resent input history, undercounting spend.",
     "unresolved_fact": "What the adapter's 'tokens' field contains."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "agent.py:34",
     "suspicion": "Raw tool exception text reaches the model and may be echoed to the public asker, leaking internal details.",
     "unresolved_fact": "What the tools' exceptions contain."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "An unknown tool name crashes the request.", "evidence": "The tools[...] lookup is inside the try at agent.py:31-34; the KeyError is caught."},
    {"id": "R2", "candidate": "Non-dict args crash ** unpacking.", "evidence": "The TypeError is raised inside the same try and caught."},
    {"id": "R3", "candidate": "A non-serializable tool result crashes the request.", "evidence": "json.dumps(..., default=str) at agent.py:35."},
    {"id": "R4", "candidate": "A model that keeps calling tools loops forever.", "evidence": "for _ in range(MAX_TURNS) at agent.py:24, then the raise at :38."},
    {"id": "R5", "candidate": "A non-string question crashes len().", "evidence": "The isinstance check at agent.py:18 runs first."},
    {"id": "R6", "candidate": "Refused requests bypass the rate limit.", "evidence": "The slot is recorded at agent.py:49 before validation."}
  ]
}
```