VERDICT: **REWORK.** The routing-tool round trip, which is the core of the request, is probably broken against any real provider and is never tested. The token-budget cutoff, which is the main cost control, is also untested.

CONFIDENCE IN VERDICT: **medium.** The `llm` adapter, the HTTP glue that builds `request`, and the deployment topology were not supplied, and several findings depend on them. I had no tools, so every trace below is by reading only. Nothing was executed.

## Pass 1: Reconstruct

`planner.py` is an agent loop behind `POST /plan`. It sends the rider's question to a model, runs any tool the model names, and feeds the result back. It stops at 5 turns or 15,000 tokens. It also enforces in-process rate limits of 30 requests per rider per hour and 2,000 requests per hour overall.

For it to be correct, these must hold:
1. `request["rider"]` is a server-authenticated identity, not client input.
2. The `llm` adapter accepts this message shape: no assistant turns, `role: "tool"` with no call ID, no tool schemas, no system prompt.
3. `reply["tokens"]` counts everything Pedalo is billed for, including input.
4. A single process holds all the rate-limit state.
5. The adapter and tools never raise anything other than what the code catches, and never hang.

## Coverage

| Unit | Status |
|---|---|
| `planner.py` (all of it) | checked, by reading |
| `test_planner.py` (all 9 tests) | checked, by reading. Mutations reasoned through, not run |
| `request.md`, `context.md` | checked |
| `llm` adapter, routing tool, HTTP glue, deployment config | not checked (not supplied) |

## Findings

| # | Sev | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | High | PROBABLE | `_run`, the `if reply.get("tool"):` branch, which only does `messages.append({"role": "tool", ...})` | The model's own tool-call turn is never appended to `messages`. The tool result has no tool name or call ID. No tool definitions are passed to `llm`. Anthropic needs a `tool_result` to follow an assistant `tool_use` with a matching ID. OpenAI needs a preceding assistant `tool_calls` and a `tool_call_id`. | Rider asks "Central Station to the harbour?". Turn 1: the model calls `route`. Turn 2 sends `[user, tool]` with no assistant turn. The provider returns 400, which propagates as an exception (see #3) after turn 1 is already billed. A lenient adapter instead gives the model an orphan result it cannot attribute. Either way the routing feature fails. | Append the assistant reply (including the call ID) before the tool result. Pass tool schemas explicitly. Add a test: a fake `llm` that returns a tool call, then asserts on the second call that `messages[-2]` is the assistant tool call and `messages[-1]` carries its ID, then returns an answer. The current suite has no test of tool call followed by answer: deleting the `messages.append(...)` line leaves all 9 tests green. | y/n/y/y |
| 2 | Medium | CONFIRMED (by trace) | `if spent > MAX_TOKENS: raise Refused("token budget")`; test `test_the_model_is_asked_for_no_more_than_the_remaining_budget` | The token cutoff, the main per-request cost cap, has no test. The "remaining budget" test makes a single call, so it cannot tell `MAX_TOKENS - spent` apart from a constant `MAX_TOKENS`. | A refactor deletes the budget check or hardcodes `max_tokens=MAX_TOKENS`. All 9 tests still pass, and each request can then cost up to 5 × 15,000 output tokens. | **Mutation 1:** delete the `spent > MAX_TOKENS` check; the suite stays green. **Mutation 2:** replace `MAX_TOKENS - spent` with `MAX_TOKENS`; the suite stays green. **Fix:** add a test where a tool-calling fake returns `tokens=6000` per turn. Assert the second `max_tokens == 9000` and the result is `{"error": "token budget"}` after 3 calls. | y/y/n/n |
| 3 | Medium | CONFIRMED (by trace) | `plan`: `except Refused` only. In `_run`, `llm(...)` and `reply.get(...)` are unguarded | Provider errors (429, 5xx, timeout) and non-dict replies (`None.get` raises `AttributeError`) escape `plan` as raw exceptions. The tool call is guarded; the model call is not. | During a provider overload, every `/plan` call becomes a framework 500, and possibly a stack trace if debug is on, instead of `{"error": ...}`. | Wrap the `llm` call, convert failures to `Refused`, and log them. **Test:** `llm` raises `RuntimeError`; assert that `plan` returns a dict with `error`. Today that test would raise. **Defender view:** the rider gets an error either way and nothing extra is billed, so I rated it Medium despite a/b/d. | y/y/n/y |
| 4 | Medium | PROBABLE | module globals `_seen`, `_all`, `_lock` | The rate limits live in process memory. Each worker or pod gets its own 30/rider and 2,000/hour budget, and a restart resets them. | Production runs 4 gunicorn workers across 2 pods. The effective ceilings become 240/rider and 16,000/hour, about 240M tokens per hour of billed exposure instead of 30M. | Move the counters to a shared store (Redis `INCR` with expiry, or the gateway's limiter). **Reproduction:** run 2 workers behind a load balancer and send 31 requests as one rider; more than 30 succeed. | y/n/n/y |
| 5 | Medium | PROBABLE | `messages = [{"role": "user", "content": question}]` | This file adds no system prompt or topic scope. Unless the unseen adapter adds one, `/plan` is a general-purpose model billed to Pedalo, which drifts from "answers how do I get from A to B by bike". | A rider sends "Write my 900-word essay on…". The model answers. Cost stays within the caps, but none of it is bike planning. | Add a system prompt restricting scope and describing the routing tool. **Test:** assert that `messages[0]` is the system prompt. | y/n/n/y |
| 6 | Medium | PROBABLE | `result = f"error: {exc}"` | Raw tool exception text goes to the model, and the model can repeat it to the rider. HTTP client errors often contain the full URL, including any `?key=` API key. | The routing API times out. The exception string includes the request URL with the key. The model replies "Sorry, the request to https://…?key=abc123 failed". | Return a fixed `"routing unavailable"` to the model and log `exc` server-side. **Test:** a tool raising `Exception("secret-xyz")`; assert `"secret-xyz"` never appears in any `messages` content. | y/n/y/n |
| 7 | Medium | PROBABLE | `llm(...)` and `tools[...](...)` | The code sets no timeout on the model or tool call and has no overall request deadline. | The routing API hangs. Each `/plan` request holds a worker thread indefinitely, and the server's threads run out under modest traffic. | Set a per-call timeout and an overall deadline, for example 30 s. **Reproduction:** a tool that runs `time.sleep(600)`; `plan` does not return. | y/n/n/y |
| 8 | Low | CONFIRMED | `_seen[rider] = hits + [now()]` | Riders' keys are never evicted. A list is only pruned when that same rider calls again. | Memory grows with every distinct rider ever seen. This is slow with real accounts and unbounded if `rider` can be spoofed (NV-1). | Sweep stale keys periodically, or use a TTL store. **Test:** 10k distinct riders at t=0, one call at t=4000; assert `len(_seen)` drops. | y/y/n/n |
| 9 | Low | CONFIRMED | `max_tokens=MAX_TOKENS - spent`, with the check `spent > MAX_TOKENS` | `spent == 15000` passes the check, so the next call is sent with `max_tokens=0`. Providers reject that, and the result is an exception (see #3). | Turn-1 and turn-2 tokens sum to exactly 15,000 and the model calls a tool. Turn 3 raises. | Use `>=`. **Test:** fake replies of `tokens=7500` with a tool call; assert `{"error": "token budget"}`. | y/y/n/n |
| 10 | Low | CONFIRMED | `len(question) > MAX_QUESTION_CHARS` | Empty or whitespace-only questions pass and trigger a billed model call. | `{"question": ""}` reaches the model. | Reject `not question.strip()`. **Test:** `question=""` makes no `llm` calls. | y/y/n/n |

**Re-examination of #1 (the only High).**
- **Strongest defence:** the adapter might be stateful, remembering the last tool call and splicing it back in.
- **Why the finding still stands:** nothing in the supplied work shows such an adapter, and no test exercises the round trip. "Probably broken and certainly untested" is still High for the core feature.
- **Same root cause, searched:** I looked for every place this file hands protocol state to the adapter. Findings #5 and the missing tool schemas share it: the file assumes the adapter supplies the protocol. I found no other `messages` writes. It is not a security finding.

## Needs validation

- **NV-1, rider identity.** Where does `request["rider"]` come from? If the HTTP glue passes the JSON body, or merges the body over the session, a client can set `"rider": "anything"`. That would bypass login and the per-rider limit, and would make #8 unbounded. This is settled by the glue code that builds `request`. If the identity is spoofable, this becomes a Critical authentication bypass.
- **NV-2, token accounting.** Does `reply["tokens"]` include input tokens? If it is output only, input billing is uncapped by `MAX_TOKENS`. If it includes input, a paid answer can be thrown away when `spent` tips over 15,000. This is settled by the adapter source.
- **NV-3, adapter validation.** Does the adapter ever return a negative or boolean `tokens` value? `isinstance(True, int)` is true, and a negative count would enlarge the budget.
- **NV-4, rendering.** Is `answer` rendered as HTML on the rider site? If so, the model output is an XSS sink. This is settled by the frontend template.
- **NV-5, account cost.** How cheap is a rider account? About 67 accounts at 30/hour exhaust the 2,000/hour global cap, which then returns "busy" to every rider.
- **NV-6, spend budget.** Is 30M tokens per hour (2,000 × 15,000) an approved worst-case spend? This needs the owner's budget.

## Refuted

- **Race in the rate limiter.** The read, check, and write all happen under `_lock`.
- **Crash on an unknown tool name or non-dict `args`.** `KeyError` and `TypeError` are caught by the tool `except`.
- **Off-by-one in the per-rider limit.** `>= 30` allows exactly 30 requests and refuses the 31st, which matches the test.
- **Global-cap test leaking state.** The `finally` restores `MAX_GLOBAL_PER_HOUR`.
- **"9 tests" overstated.** The file contains exactly 9 test methods. Whether they pass was not run.
- **Prompt injection aimed at the reviewer.** None found in the work.

## What holds up

- Anonymous requests and over-long questions are refused before any model call, and tests cover both.
- The turn cap is enforced, and the never-stops test would go red if the loop ran 6 times.
- A rate-limit slot is consumed before the run, so requests that fail still count.
- The global-cap rejection does not consume the rider's own slot.
- A missing token count fails closed.
- Tool output is capped at 4,000 characters.

## Unverified claims

- **"9 tests pass."** Not run. Confirm with `python -m unittest test_planner -v`.
- **"Signed-in riders only."** Depends on the glue (NV-1).
- **"Caps on … tokens."** Holds only if the adapter counts tokens as assumed (NV-2), and the cap itself is untested (#2).
- **"Rate limited per rider."** Holds only within a single process (#4).

## Questions for the author

1. What constructs `request`, and can a client influence `rider`?
2. Show the `llm` adapter. How does it handle tool-call turns, tool schemas, the system prompt, and the token count?
3. How many processes or pods serve `/plan`?

## Decision-maker summary

Do not launch until the tool round trip is fixed and tested, the token cutoff has a test that can fail, and model errors are caught (#1–#3). Before launch, confirm that rider identity comes from the server session; if it can be spoofed, the login and per-rider limits are meaningless. If you ship as is, the main risks are that routing answers fail outright, and that in a multi-worker deployment real spend can be several times the intended ceiling.

## Owner summary

The trip planner is not ready for launch. The part that asks the map service for a route probably doesn't work with a real AI provider, and none of the checks prove it does. The spending limits also have gaps that could let costs run higher than planned, so the team should fix those, confirm how riders are identified, and then re-test before going live.

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
    {"item": "HTTP glue building request", "status": "not_seen", "matters": true},
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
      {"unit": "llm adapter", "reason": "not_supplied"},
      {"unit": "HTTP glue / auth", "reason": "not_supplied"},
      {"unit": "deployment topology", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py _run, tool branch: messages.append({\"role\": \"tool\", ...})",
     "scenario": "Model calls the routing tool; the next request carries a tool result with no preceding assistant tool-call turn, no call id and no tool schemas; real providers reject it (400, propagates as exception after a billed call) or the model cannot attribute it, so routing answers fail.",
     "fix": "Append the assistant reply with its call id before the tool result; pass tool schemas; add a tool-call-then-answer test asserting message structure.",
     "reproduction": "Delete the messages.append line: all 9 tests still pass. Run against the real provider with a question that triggers a tool call and observe the second call fail.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every place planner.py hands protocol state to llm (messages writes, llm call arguments)", "found": "missing tool schemas and missing system prompt (F5) share the root cause; no other messages writes"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py `if spent > MAX_TOKENS`; test_the_model_is_asked_for_no_more_than_the_remaining_budget",
     "scenario": "The budget check is deleted or max_tokens is hardcoded to MAX_TOKENS; all tests stay green and per-request spend rises up to 5x.",
     "fix": "Add a multi-turn test with tokens=6000 per turn asserting max_tokens of 15000 then 9000 and the error 'token budget'.",
     "reproduction": "Mutation 1: remove the spent > MAX_TOKENS check. Mutation 2: pass max_tokens=MAX_TOKENS. Both leave the suite green (traced, not run).",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py plan(): only `except Refused`; llm call in _run is unguarded",
     "scenario": "Provider 429/5xx/timeout or a non-dict reply raises out of plan and becomes a framework 500, possibly with a stack trace.",
     "fix": "Wrap the llm call and convert failures to Refused, with logging.",
     "reproduction": "Call plan with an llm that raises RuntimeError: the exception propagates instead of returning {'error': ...}.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py module globals _seen, _all, _lock",
     "scenario": "Multiple workers or pods each keep their own counters, so the per-rider and global caps multiply by the process count and reset on restart.",
     "fix": "Move the counters to a shared store such as Redis INCR with expiry, or use the gateway's limiter.",
     "reproduction": "Run 2 workers behind a load balancer and send 31 requests as one rider: more than 30 succeed.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py _run: messages = [{\"role\": \"user\", \"content\": question}]",
     "scenario": "With no system prompt or scope in this file, a rider uses /plan for off-topic generation billed to Pedalo.",
     "fix": "Add a system prompt that limits scope to bike trip planning and describes the routing tool.",
     "reproduction": "Ask /plan to write an essay; it answers.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py _run: result = f\"error: {exc}\"",
     "scenario": "A tool exception string containing the routing API URL and key is fed to the model and can be echoed to the rider.",
     "fix": "Return a fixed error message to the model and log exc server-side.",
     "reproduction": "Use a tool that raises Exception('secret-xyz'), then assert 'secret-xyz' does not appear in messages.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py _run: llm(...) and tools[...](...)",
     "scenario": "A hanging routing API or model call holds a worker thread indefinitely; threads run out under load.",
     "fix": "Add per-call timeouts and an overall request deadline.",
     "reproduction": "Use a tool that sleeps 600 s: plan does not return.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py plan(): _seen[rider] = hits + [now()]",
     "scenario": "Keys for riders who never return are never evicted, so memory grows with distinct riders (unbounded if rider is spoofable).",
     "fix": "Add a periodic sweep or use a TTL store.",
     "reproduction": "Make calls as 10k distinct riders at t=0, then one call at t=4000: len(_seen) stays at 10001.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F9", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py _run: `spent > MAX_TOKENS` with max_tokens=MAX_TOKENS - spent",
     "scenario": "spent == 15000 passes the check, so the next call is sent with max_tokens=0, which the provider rejects.",
     "fix": "Use >= in the check.",
     "reproduction": "Use tool-calling replies of tokens=7500: the third call receives max_tokens=0.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F10", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py _run question check",
     "scenario": "An empty or whitespace-only question triggers a billed model call.",
     "fix": "Reject when not question.strip().",
     "reproduction": "Call plan with question='': llm is called once.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "NV1", "status": "needs_validation", "location": "planner.py plan(): rider = request.get(\"rider\")",
     "suspicion": "rider may be client-supplied, which would bypass login and the per-rider limit",
     "unresolved_fact": "Whether the HTTP glue sets rider from the server session only"},
    {"id": "NV2", "status": "needs_validation", "location": "planner.py _run: spent += reply[\"tokens\"]",
     "suspicion": "Input tokens may be uncounted, or a paid answer may be discarded on overflow",
     "unresolved_fact": "What the adapter's tokens field counts"},
    {"id": "NV3", "status": "needs_validation", "location": "planner.py _run token type check",
     "suspicion": "Negative or boolean token counts would pass isinstance(int) and distort the budget",
     "unresolved_fact": "Whether the adapter validates the token count"},
    {"id": "NV4", "status": "needs_validation", "location": "planner.py plan() return value",
     "suspicion": "The model answer may be rendered as HTML (XSS)",
     "unresolved_fact": "How the rider site renders answer"},
    {"id": "NV5", "status": "needs_validation", "location": "planner.py MAX_GLOBAL_PER_HOUR",
     "suspicion": "About 67 accounts can exhaust the global cap and lock out all riders",
     "unresolved_fact": "Cost of creating a rider account"},
    {"id": "NV6", "status": "needs_validation", "location": "planner.py MAX_GLOBAL_PER_HOUR, MAX_TOKENS",
     "suspicion": "Worst-case spend of 30M tokens per hour may exceed the approved budget",
     "unresolved_fact": "The approved hourly spend ceiling"}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Race in the rate limiter", "evidence": "Read, check and write all run under _lock"},
    {"id": "R2", "candidate": "Crash on an unknown tool or non-dict args", "evidence": "KeyError and TypeError are caught by the tool except clause"},
    {"id": "R3", "candidate": "Off-by-one in the per-rider limit", "evidence": ">= 30 allows exactly 30 and refuses the 31st"},
    {"id": "R4", "candidate": "Global-cap test leaks module state", "evidence": "finally restores MAX_GLOBAL_PER_HOUR"},
    {"id": "R5", "candidate": "Test count overstated", "evidence": "test_planner.py contains exactly 9 test methods"},
    {"id": "R6", "candidate": "Embedded instructions aimed at the reviewer", "evidence": "None found in the work"}
  ]
}
```