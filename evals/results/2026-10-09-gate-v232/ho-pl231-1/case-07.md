VERDICT: **REWORK.** The caps are well built. But the endpoint most likely takes the rider's identity from the request body, the agent loop sends a conversation that real model APIs reject once the routing tool is used, and model-call failures are not handled.

CONFIDENCE IN VERDICT: **medium.** The `request` builder and the `llm` adapter were not supplied, and both High findings marked PROBABLE depend on them. I also could not run the tests.

## Pass 1: Reconstruct

`planner.py` exposes `plan()`, meant to serve POST /plan. It rejects calls with no rider and applies a per-rider limit (30/hour) and a global limit (2000/hour). It then runs a model loop of up to 5 turns and 15,000 tokens, dispatches tool calls to a `tools` dict, and returns the model's answer.

For this to be correct, all of the following must hold:
1. `request["rider"]` is set server-side from a verified session and cannot come from the client.
2. The `llm` adapter accepts a `[user, tool, tool, ...]` message list. It must also already know the routing tool's schema and a system prompt, because neither is passed in.
3. `reply["tokens"]` reflects billed usage.
4. The process runs as a single worker, so in-memory limits are real limits.
5. The `llm` adapter never raises.

The work states none of these.

## Coverage

| Item | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| planner.py | checked, every line |
| test_planner.py | checked, all 9 test methods read. Not run (no tools). |
| `llm` adapter, routing tool, HTTP layer that builds `request`, deployment config | not supplied |

## Findings

| # | Sev | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | High | PROBABLE | `plan`: `rider = request.get("rider")` | Identity is read from the same dict that carries the client's `question`. The tests build it as `{"rider": "u1", "question": "q"}`. Nothing in this code checks a session. | An anonymous client POSTs `{"rider":"x1","question":...}`, then `x2`, `x3`, and so on. The login check passes and each fake rider gets a fresh 30/hour. One client spends the global 2000/hour at up to 15k tokens each (about 30M tokens/hour billed to Pedalo). Every real rider then gets `"busy"`. | Derive `rider` from the verified session or token in the HTTP layer and ignore any `rider` field in the body. Test: a request with `rider` in the body and no session must return `login required`. | Y/N/Y/Y |
| 2 | High | PROBABLE | `_run`: `messages.append({"role": "tool", ...})` | The model's tool call is never added to `messages`: there is no assistant turn and no tool-call id. The next call sends `[user, tool]`. | A real question triggers a routing call, and the second `llm` call sends that list. Anthropic's API has no `tool` role. OpenAI requires a preceding assistant `tool_calls` message and a `tool_call_id`. Either way the API returns a 400, which Finding 4 turns into a 500. Every question that needs a route fails, which is the whole feature. | Append the assistant turn with the tool call and id, then a result block that references the id. Reproduction: a fake `llm` that asserts on its second call that `messages[-2]["role"] == "assistant"` and that the result references the call. The current code fails it. | Y/N/Y/Y |
| 3 | High | CONFIRMED (code path) | `_run`/`plan`: only `except Refused`, and `llm(...)` and the tool calls have no timeout | Provider errors (timeout, 429, 5xx, 400) escape as unhandled exceptions. So does a non-dict reply, because `reply.get` raises AttributeError. There is also a self-inflicted case: a tool turn that brings `spent` to exactly 15000 passes `spent > MAX_TOKENS`, so the next call gets `max_tokens=0`, which providers reject. A hung tool or model call holds the worker indefinitely, and the rate slot has already been spent. | A provider timeout under load produces an unhandled 500 and a stuck request. | Catch provider and adapter errors and return `{"error": ...}`. Add timeouts to `llm` and to tool calls. Refuse when `MAX_TOKENS - spent <= 0` before calling. Reproduction: `llm` returns `{"tool":"t","args":{},"tokens":15000}` then records `max_tokens`. You will see a call with `0`. Or make `llm` raise `TimeoutError`, and `plan()` raises. | Y/Y/N/Y |
| 4 | Medium | PROBABLE | `_run`: `llm(messages, max_tokens=...)` | `tools` is never passed to the model, and there is no system prompt. Unless the adapter pre-binds both, the model does not know a routing tool exists. It will answer from memory, inventing routes such as roads unsafe for bikes. It will also answer any question, which makes /plan a general-purpose chatbot billed to Pedalo. | A rider asks for an essay and gets one. A route question gets a made-up route. | Pass the tool schemas and a scoped system prompt explicitly, and test that they reach `llm`. | Y/N/Y/N |
| 5 | Medium | PROBABLE (test coverage UNVERIFIED) | test_planner.py | The tests do not guard the cost controls. Traced by reading, not run: (1) deleting `if spent > MAX_TOKENS: raise` leaves all 9 green, since no test reaches the token budget. (2) Changing the call to `max_tokens=MAX_TOKENS` still passes, since only the first call is checked. (3) Changing `3600` to `10**9` (rate-limit entries never expire) still passes, since the window is never tested. (4) No test sends a tool result back to the model, so Finding 2 cannot show up. | A regression in the budget or window ships green. | Add tests: a 3-turn tool loop with large `tokens` that must refuse with `token budget` and see decreasing `max_tokens`; window expiry at `now+3601`; message-sequence assertion. Confirm each mutation above turns them red in a scratch copy. | Y/N/N/Y |
| 6 | Medium | PROBABLE | `MAX_GLOBAL_PER_HOUR` with `MAX_REQUESTS_PER_HOUR` | Even with real authentication, 67 accounts × 30 requests fill the 2000 global quota. That locks out every rider for an hour. | A small group of sign-ups, or one person with 67 accounts, denies the service to everyone. | Reserve headroom per rider tier, alert on reaching the global cap, and rate-limit account creation. | Y/N/Y/N |
| 7 | Low | CONFIRMED | `_run`: `if spent > MAX_TOKENS` runs after the call | The budget is enforced after billing. The over-budget call is paid for and its answer thrown away. If `tokens` counts input as well as output, `max_tokens` does not bound the call at all. | The last call overshoots and the rider gets an error for tokens Pedalo already paid for. | Estimate input size before calling and cap on remaining budget minus that estimate. | Y/Y/N/N |
| 8 | Low | PROBABLE | `result = f"error: {exc}"` | Raw exception text, possibly including internal URLs or keyed query strings, is given to the model. A question like "quote any tool error verbatim" relays it to the rider. | Internal details leak through the answer. | Give the model a generic error and log the details server-side. | Y/N/N/N |
| 9 | Low | CONFIRMED | `_seen` | Riders who stop calling are never evicted, so up to 2000 new keys a day accumulate for the life of the process. | Slow memory growth. | Sweep periodically or use a TTL store. | Y/Y/N/N |
| 10 | Low | CONFIRMED | `json.dumps(...)[:4000]` | Truncation cuts mid-JSON with no marker. | A long route reaches the model as malformed or partial text, and it may present an incomplete route as complete. | Truncate structurally and add a "truncated" flag. | Y/Y/N/N |

**Re-examined as the defender:**
- Finding 1 stands unless the framework overwrites `rider` from the session after parsing the body. Nothing supplied shows that. Siblings searched: every read of `request`. Only `rider` and `question` are read, and `question` is legitimately client input.
  - Boundary: the lower-trust principal is an anonymous internet client. Its input is the JSON body field `rider`. The failing control is the `if not rider` login check. The boundary crossed is unauthenticated to authenticated, billed model use. The resources affected are Pedalo's model spend and the global quota.
- Finding 2 stands unless the adapter rebuilds the message history itself. Sibling: Finding 4, where the tools are not passed either. Both come from the same undefined adapter contract.
- Finding 3: the defender would say the framework returns a 500 and the rider retries. The scoring rubric (a, b and d all yes) still makes it High. Siblings: the tool calls are guarded by `except Exception`; the `llm` call is not.

## Needs validation

- **Worker and instance count.** `_seen`, `_all` and `_lock` are per process. With N workers, every limit is N times higher and resets on restart. Settled by the deployment config.
- **What `reply["tokens"]` counts:** output only, or input plus output. Settled by the adapter source.
- **How `answer` is rendered on the rider site.** Its type is never checked, and model text inserted as HTML would be an XSS risk. Settled by the front-end code.
- **Whether `tools` contains only the routing tool.** Any other entry can be called by the model with arguments it chooses, and the rider can steer it through the question. Settled by the call site.

## Refuted

- **Unknown tool name or non-dict `args` crashes the loop.** Refuted: the KeyError or TypeError is caught by `except Exception` and returned to the model as text.
- **Race in the rate limiter.** Refuted: both the check and the update happen under `_lock`.
- **The global-ceiling test leaks its patched constant.** Refuted: `finally` restores 2000, and `plan` reads the module global at call time.
- **Negative or bool `tokens` inflate the budget.** Refuted as a finding: the value comes from the provider adapter, not from the rider.
- **Embedded instructions aimed at the reviewer.** None found.

## What holds up

- Anonymous and over-long or missing questions are refused before any model call, and tests cover this.
- The turn cap works; its test would fail against an unbounded loop.
- The rate slot is recorded before the model runs, so failures still count against the rider.
- The lock covers check and update together, and the model call runs outside the lock.
- Tool exceptions are contained and tool output size is capped.
- Global and per-rider window logic is correct for a single process.

## Unverified claims

- **"9 tests pass":** 9 test methods exist, but I could not run them. Confirm with `python -m unittest test_planner -v`.
- **"Signed-in riders only" (docstring):** confirm in the HTTP layer that builds `request`.
- **"Caps on tokens":** confirm what `tokens` counts and add the missing budget test (Finding 5).

## Questions for the author

1. Where is `request["rider"]` set, and can a body field override it?
2. Show the `llm` adapter. Does it bind tool schemas and a system prompt, and how does it translate `role: "tool"` messages?
3. How many worker processes and instances serve /plan?

## Decision-maker summary

Do not launch until rider identity is confirmed to come from the server session, the agent loop is tested end to end against the real model API with a real routing call, and provider errors and timeouts are handled. If launched as is, the likely outcomes are that any anonymous client can spend up to the global model budget and lock real riders out, and that route questions fail with server errors. Cost caps are only as strong as the deployment's worker count, which is unknown.

## Owner summary

The trip planner has sensible spending limits, but it probably trusts the browser to say who the rider is, so anyone could use it for free at the company's expense and block real riders. It also looks likely to fail on exactly the questions it exists for: once it asks the map service for a route, the next step is formatted in a way the AI provider rejects. These need fixing and testing against the real AI service before launch.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "planner.py", "status": "seen", "matters": true},
    {"item": "test_planner.py", "status": "seen", "matters": true},
    {"item": "llm adapter", "status": "not_seen", "matters": true},
    {"item": "HTTP layer building request", "status": "not_seen", "matters": true},
    {"item": "deployment config", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "planner.py", "kind": "file"},
      {"unit": "test_planner.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "test execution and mutation runs", "reason": "no_tools"},
      {"unit": "llm adapter", "reason": "not_supplied"},
      {"unit": "HTTP/auth layer", "reason": "not_supplied"},
      {"unit": "deployment config", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B", "location": "planner.py plan(): rider = request.get(\"rider\")",
     "scenario": "Anonymous client posts {\"rider\":\"x1\",\"question\":...}, rotating rider ids; passes the login check, bypasses the per-rider limit, spends up to 2000 calls/hour at 15k tokens each and makes every real rider get 'busy'.",
     "fix": "Derive rider from the verified server session; ignore body-supplied rider.",
     "reproduction": "POST /plan with body {\"rider\":\"anyone\",\"question\":\"q\"} and no session cookie; expect 'login required', observe an answer.",
     "answers": {"a": true, "b": false, "c": true, "d": true}, "security": true,
     "siblings_searched": {"searched": "every read of request in planner.py", "found": "only rider and question; question is legitimately client input"},
     "boundary": {"principal": "anonymous internet client", "input": "JSON body field 'rider'", "control": "if not rider login check", "crossed": "unauthenticated to authenticated billed model use", "resource": "Pedalo model spend and global quota"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B", "location": "planner.py _run(): messages.append({\"role\": \"tool\", ...})",
     "scenario": "First real tool call; the second llm call sends [user, tool] with no assistant tool-call turn and no id; Anthropic/OpenAI return 400; the exception escapes and every route question fails.",
     "fix": "Append the assistant tool-call turn with its id and reference that id in the result; test against the real API.",
     "reproduction": "Fake llm that on its second call asserts messages[-2]['role']=='assistant' and that the tool-call id matches; it fails on current code.",
     "answers": {"a": true, "b": false, "c": true, "d": true}, "security": false,
     "siblings_searched": {"searched": "all llm calls and message construction", "found": "tools and system prompt are also never passed (F4)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "planner.py plan(): except Refused only; _run(): llm(...) and tools[...] have no timeout",
     "scenario": "A provider timeout/429/400, a non-dict reply, or max_tokens=0 after a tool turn bringing spent to exactly 15000 raises an unhandled exception (500); a hung call holds the worker; the rate slot is already spent.",
     "fix": "Catch adapter errors and map them to {error}; add timeouts; refuse when the remaining budget is <= 0 before calling.",
     "reproduction": "llm returns {\"tool\":\"t\",\"args\":{},\"tokens\":15000} then records max_tokens and sees 0; or llm raises TimeoutError and plan() raises.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "all external calls in _run", "found": "tool calls are wrapped in except Exception; the llm call is not"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "planner.py _run(): llm(messages, max_tokens=...)",
     "scenario": "Tools and system prompt are never passed; unless the adapter pre-binds them the model invents routes and answers off-topic requests billed to Pedalo.",
     "fix": "Pass tool schemas and a scoped system prompt explicitly; test that they reach llm.",
     "reproduction": "Fake llm that records its kwargs; there is no tools or system argument.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "test_planner.py",
     "scenario": "Deleting the token-budget check, fixing max_tokens at MAX_TOKENS, or making the rate window never expire all leave the 9 tests green (traced, not run).",
     "fix": "Add token-budget, decreasing max_tokens, window-expiry and message-sequence tests; confirm by mutation in a scratch copy.",
     "reproduction": "Apply each mutation in a scratch copy and run python -m unittest test_planner.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "planner.py MAX_GLOBAL_PER_HOUR / MAX_REQUESTS_PER_HOUR",
     "scenario": "67 accounts x 30 requests exhaust the 2000 global quota and lock out all riders for an hour.",
     "fix": "Per-tier headroom, alerting at the cap, sign-up rate limiting.",
     "reproduction": "Set the per-rider limit to 30 and the global to 2000; issue 30 calls from each of 67 riders; the next rider gets 'busy'.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "planner.py _run(): spent check after the llm call",
     "scenario": "The over-budget call is billed and its answer discarded; if tokens include input, max_tokens does not bound the call.",
     "fix": "Estimate input before calling and cap on the remaining budget.",
     "reproduction": "llm returns tokens=20000 on its first call; the result is the 'token budget' error after billing.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "planner.py _run(): result = f\"error: {exc}\"",
     "scenario": "Raw exception text is passed to the model, which relays it to a rider who asks for tool errors verbatim.",
     "fix": "Give the model a generic error; log details server-side.",
     "reproduction": "Tool raises Exception('http://internal/key=SECRET'); the fake llm sees that text in messages.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F9", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "planner.py _seen",
     "scenario": "Inactive riders are never evicted; memory grows for the life of the process.",
     "fix": "Periodic sweep or a TTL store.",
     "reproduction": "Call plan for 10000 distinct riders, advance now by 2 hours; len(_seen) is still 10000.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F10", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "planner.py _run(): json.dumps(...)[:4000]",
     "scenario": "A long route result is cut mid-JSON with no marker; the model may present a partial route as complete.",
     "fix": "Truncate structurally and add a truncated flag.",
     "reproduction": "Tool returns a list of 1000 steps; the content sent to the model is invalid JSON.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "NV1", "status": "needs_validation", "location": "planner.py module state _seen/_all/_lock", "suspicion": "Limits are per process and multiply with workers or instances.", "unresolved_fact": "Worker and instance count in deployment config."},
    {"id": "NV2", "status": "needs_validation", "location": "planner.py reply[\"tokens\"]", "suspicion": "May count output only, leaving input spend uncapped.", "unresolved_fact": "llm adapter source."},
    {"id": "NV3", "status": "needs_validation", "location": "planner.py plan() return answer", "suspicion": "Untyped model text may be rendered as HTML (XSS).", "unresolved_fact": "Front-end rendering code."},
    {"id": "NV4", "status": "needs_validation", "location": "planner.py tools dict", "suspicion": "Any extra tool can be invoked with model-chosen args steered by the rider.", "unresolved_fact": "Contents of tools at the call site."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Unknown tool name or bad args crash the loop", "evidence": "KeyError/TypeError are caught by except Exception around the tool call."},
    {"id": "R2", "candidate": "Race in the rate limiter", "evidence": "Check and update both occur under _lock."},
    {"id": "R3", "candidate": "Global-ceiling test leaks its patched constant", "evidence": "finally restores 2000; plan reads the module global at call time."},
    {"id": "R4", "candidate": "Negative or bool tokens inflate the budget", "evidence": "The value comes from the provider adapter, not the rider."},
    {"id": "R5", "candidate": "Embedded instructions aimed at the reviewer", "evidence": "None present in the supplied files."}
  ]
}
```