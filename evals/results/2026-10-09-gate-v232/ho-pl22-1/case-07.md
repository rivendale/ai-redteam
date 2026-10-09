# Adversarial Diagnostic Review: Pedalo `/plan` endpoint

## Pass 1: Reconstruct

The work claims to deliver a `/plan` endpoint. A model agent answers bike-routing questions and can call tools. Spending is capped by question length, turns, tokens, a per-rider rate limit and a global rate limit. It claims that only signed-in riders get through and that its 9 tests pass.

For it to be correct, these things must hold:

1. `request["rider"]` is an identity set by the server, not something the client sends.
2. The process is the only instance of the service, since the rate-limit state lives in module memory.
3. `reply["tokens"]` measures what Pedalo is billed for.
4. The hidden `llm` adapter knows the routing tool and accepts the message format built here.
5. The tests guard the limits they are named after.

None of these is shown in the material. Assumptions 1, 2 and 4 are unstated.

## Pass 2: Attack (Track B, plus cost and abuse)

Traced paths:

- **Main path:** question → model calls the tool → result appended → model answers.
- **Hostile input, rider rotation:** the caller changes `rider` on every request.
- **Hostile input, endless model:** the model keeps calling tools.
- **Hostile input, exact budget:** `spent` lands exactly on `MAX_TOKENS`.
- **Hostile input, odd rider value:** `rider` is a list or dict.
- **Failure inside calls:** the `llm` call raises an error, or the tool raises one.

I mentally applied a mutation to every limit check to see whether any test would go red.

## VERDICT: REWORK

The cost controls are reasonable in shape, but they rest on an identity and a token count that this file does not establish. The agent loop most likely cannot complete a real tool call. Two of the five limits have tests that would still pass if the limit were deleted.

**CONFIDENCE IN VERDICT: medium.** I cannot see the `llm` adapter or the code that builds `request`. If both turn out to be sound, findings 1 and 3 drop, and the verdict moves to SHIP WITH FIXES.

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | PROBABLE | `plan`: `rider = request.get("rider")`, `if not rider` | "Signed-in riders only" is enforced only by checking that the value is truthy. Nothing in the file verifies identity. The tests pass `rider` in the same dict as `question`, which suggests both come from the request body. | An attacker POSTs `{"rider": "<random>", "question": ...}` with a new value each time. Both the login check and the per-rider limit are bypassed. Only the global cap remains: 2000 requests × 15k tokens ≈ 30M billed tokens/hour per process, on Pedalo's account. | Take `rider` from the authenticated session or token in the handler, never from the body. Add a test that a body-supplied `rider` without a session is refused. |
| 2 | High | CONFIRMED (design) / PROBABLE (impact) | `plan`: `MAX_GLOBAL_PER_HOUR` check | The global cap is shared by everyone, and an over-limit request is refused rather than queued. | One abuser exhausts the 2000/hr ceiling, using rotated IDs (finding 1) or about 67 real accounts × 30 requests. Every legitimate rider then gets `{"error": "busy"}` for up to an hour. | Keep the global cap as a cost circuit-breaker, but alert when it trips. Limit per IP or account age as well. Decide explicitly whether busy-for-everyone is acceptable. |
| 3 | High | CONFIRMED (code) / PROBABLE (impact) | `_run`: `llm(messages, max_tokens=...)` and `messages.append({"role": "tool", ...})` | `tools` is never passed to the model, so the model is never told the routing tool exists or what its schema is. The model's own tool-call turn is never appended to `messages`, so the next turn contains a tool result with no request before it, and no call id. The Anthropic API has no `"tool"` role. OpenAI requires a `tool_call_id` and a preceding assistant `tool_calls` message. | Against a real model, the first tool use either errors out or the model sees an orphaned result. Then it re-requests the tool until it hits the turn limit, paying for 5 calls and answering nothing. The core feature, routing, never works. All tests use lambda fakes, so nothing catches this. | Append the assistant tool-call message, plus the tool result with its id. Pass the tool schemas. Add one test against the real adapter, or a recorded fixture of the provider's message format. |
| 4 | High | PROBABLE | Module globals `_seen`, `_all`, `_lock` | All limits are in-process memory. | Under N workers or replicas the real ceilings become N × 30 per rider and N × 2000 global. A restart or deploy resets every counter. The billing bound claimed in the docstring does not hold. | Move the counters to a shared store such as Redis (INCR with a TTL, or a sliding window). Alternatively, document and enforce single-process deployment. |
| 5 | High | CONFIRMED (by mutation reasoning) | `test_the_model_is_asked_for_no_more_than_the_remaining_budget` | The test makes only one model call, so `max_tokens=MAX_TOKENS` (no subtraction) passes too. | A regression that drops `- spent` ships green. Each turn can then request the full 15k tokens. | Use a tool-calling fake that returns `tokens: 4000` and assert `seen == [15000, 11000, 7000, ...]`. |
| 6 | High | CONFIRMED (by mutation reasoning) | `if spent > MAX_TOKENS: raise Refused("token budget")` | No test exercises this branch. In the never-stops test, 5 × 10 tokens hits the turn limit first, and that test only asserts `"error" in r`. | Deleting the token-budget check leaves all 9 tests green. | Add a test where `tokens` exceeds the budget on the second call and assert `{"error": "token budget"}`. Assert the exact error in the turn-limit test. |
| 7 | Medium | UNVERIFIED | `spent += reply["tokens"]`; `max_tokens=MAX_TOKENS - spent` | `max_tokens` caps only output, but every turn re-sends the growing context: question plus up to 4 × 4000 characters of tool output. Whether `reply["tokens"]` includes input tokens is not stated. Also, the budget check runs after the call, so the overshoot has already been billed. | If `tokens` counts output only, input tokens are never counted against the budget, and real cost per request exceeds `MAX_TOKENS`. | Define `tokens` as input + output from the provider's usage field. Before each call, refuse if estimated input plus remaining output would exceed the budget. |
| 8 | Medium | PROBABLE | `max_tokens=MAX_TOKENS - spent` when `spent == MAX_TOKENS` | `spent == MAX_TOKENS` passes the `>` check, and the next call is then sent with `max_tokens=0`. Providers reject 0. | The provider raises an error that is not caught (see finding 9). The request fails with a 500 after being billed. | Refuse when `spent >= MAX_TOKENS`, or when the remaining budget falls below a useful minimum. |
| 9 | Medium | CONFIRMED | `_run` / `plan`: only `Refused` is caught | Exceptions from `llm()`, such as timeouts, 429s or 5xx errors, propagate out of `plan`. An unhashable `rider` (for example a JSON list) raises a `TypeError` at `_seen.get`. No timeout is set on the call. | Provider hiccups become uncaught 500s, possibly with a stack trace. The rider's rate-limit slot is still consumed. A hung call ties up a worker. | Catch provider errors and return a generic error. Set a timeout. Validate that `rider` is a string. |
| 10 | Medium | CONFIRMED | `messages = [{"role": "user", "content": question}]` | There is no system prompt limiting the agent to bike routing. | Riders, or anyone given finding 1, can use Pedalo's model for unrelated tasks at Pedalo's expense. Prompt injection through tool data (place names) is easier with no instructions in place. | Add a system prompt that scopes the task and tells the model to treat tool output as data. Add a test that the system message is present. |
| 11 | Low | CONFIRMED | `_seen[rider] = ...` | Entries are pruned only when the same rider returns, so the dictionary grows with every distinct rider ID. | With rotated IDs (finding 1) it grows by up to 2000 keys per hour, forever, until restart. | Sweep expired keys periodically, or use a TTL store (finding 4 fixes this). |
| 12 | Low | CONFIRMED | `test_the_per_rider_limit_applies` | Window expiry is never tested. Mutating `< 3600` to `< 10**9` passes. | A rider who hit the limit might never be let back in, and no test would notice. | Assert that a request at `now = 1000 + 3600` succeeds. |
| 13 | Low | CONFIRMED | `result = f"error: {exc}"` | Raw exception text from the tool goes to the model, which may repeat it to the rider. | Internal hostnames, URLs or API keys embedded in a routing-service error message could reach a rider's screen. | Log the exception server-side and send the model a generic "routing unavailable" message. |
| 14 | Low | UNVERIFIED | `return {"answer": reply["answer"]}` | The answer's type and content are not checked. | If the site renders the answer as HTML, text influenced by the model or by tool data is an XSS path. | Ensure the frontend escapes the answer, and check that it is a string. |

## WHAT HOLDS UP

- **Atomic rate-limit updates:** the check-then-record step for both limits is done under one lock, so concurrent requests within a process cannot overshoot.
- **Early refusal:** anonymous and oversized or missing questions are refused before any model call, and tests cover both.
- **Turn cap:** `range(MAX_TURNS)` bounds model calls. The never-stops test would catch an unbounded loop, because `calls` would far exceed 5.
- **Missing token count:** a reply without an integer token count is refused instead of being silently counted as 0.
- **Tool failure handling:** unknown tool names and bad `args` are caught. Tool output is truncated to 4000 characters, which bounds context growth per turn.

## UNVERIFIED CLAIMS

- **"9 tests pass":** I count 9 tests, and tracing them by hand they appear to pass, but I could not run them. Run `python -m unittest test_planner -v`.
- **"Signed-in riders only":** confirming this requires the handler code that builds `request`.
- **The token budget bounds billed cost:** confirming this requires the `llm` adapter's definition of `tokens`.
- **The agent works with a real routing tool:** confirming this requires one integration run against the real provider and the real routing service.

## QUESTIONS FOR THE AUTHOR

1. Where does `request["rider"]` come from: the session, or the request body?
2. What does the `llm` adapter send to the provider? Does it attach the tool schemas, and what message format does it expect for tool results?
3. Does `reply["tokens"]` include input tokens?
4. How many processes or replicas will serve `/plan` in production?

## DECISION-MAKER SUMMARY

Do not launch until rider identity is confirmed to come from the server session, the agent loop has been run end to end against the real model and routing tool, and the rate limits live in shared storage rather than per-process memory. The existing tests would not notice if the token-budget limit were removed. If shipped as is, the likely outcomes are uncapped or poorly capped model spend, a routing feature that fails on its first tool call, and a single abuser able to lock out every rider.

## OWNER SUMMARY

The trip planner has sensible spending limits on paper, but they may be easy to get around, and they reset or multiply when the service runs on more than one server. The part where the assistant looks up a route is probably not wired correctly for the real AI service, and it has only been tested with stand-ins. A few focused fixes and one real end-to-end trial are needed before launch.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "PROBABLE", "location": "planner.py plan(): rider = request.get(\"rider\"); if not rider", "scenario": "Client supplies an arbitrary, rotating rider value in the request body, bypassing login and per-rider limits; only the global cap remains (~30M billed tokens/hour per process).", "fix": "Derive rider from the authenticated session, not the body; add a test that a body-supplied rider without a session is refused."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "planner.py plan(): MAX_GLOBAL_PER_HOUR check", "scenario": "One abuser (rotated IDs or ~67 accounts) exhausts the 2000/hr shared ceiling and every legitimate rider gets 'busy' for up to an hour.", "fix": "Keep the cap as a cost breaker with alerting, add per-IP/account limits, and decide explicitly whether lockout is acceptable."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "planner.py _run(): llm(messages, max_tokens=...) and messages.append({\"role\": \"tool\", ...})", "scenario": "Tools are never passed to the model and the assistant's tool-call turn is never recorded; a real provider rejects the orphaned tool result or the model loops to the turn limit, so routing never works.", "fix": "Append the assistant tool-call message and the tool result with its id, pass tool schemas, and add an integration test or provider-format fixture."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "planner.py module globals _seen, _all, _lock", "scenario": "With N workers or replicas, limits become N x 30 per rider and N x 2000 global; restarts and deploys reset all counters.", "fix": "Move counters to a shared store (e.g. Redis with TTL) or enforce single-process deployment."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "test_planner.py test_the_model_is_asked_for_no_more_than_the_remaining_budget", "scenario": "Only one model call is made, so removing '- spent' from max_tokens still passes.", "fix": "Use a multi-turn fake returning tokens=4000 and assert max_tokens sequence [15000, 11000, 7000, ...]."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "planner.py _run(): if spent > MAX_TOKENS: raise Refused(\"token budget\")", "scenario": "No test reaches this branch; deleting the check leaves all 9 tests green.", "fix": "Add a test where tokens exceed the budget on the second call and assert {'error': 'token budget'}; assert the exact error in the turn-limit test."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "planner.py _run(): spent += reply[\"tokens\"]; max_tokens=MAX_TOKENS - spent", "scenario": "max_tokens caps only output; if tokens excludes input, the re-sent context (up to ~17k chars per turn) is never counted, and overshoot is billed before the post-call check.", "fix": "Count input + output from provider usage and check estimated input plus remaining output before each call."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "planner.py _run(): max_tokens=MAX_TOKENS - spent", "scenario": "When spent == MAX_TOKENS the next call sends max_tokens=0, which providers reject; the uncaught error becomes a 500 after billing.", "fix": "Refuse when spent >= MAX_TOKENS or the remaining budget is below a useful minimum."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py plan()/_run(): only Refused is caught", "scenario": "Provider timeouts, 429s or 5xx errors, or an unhashable rider value, raise uncaught exceptions (500, possible stack trace); no timeout is set on the model call.", "fix": "Catch provider errors and return a generic error, set a timeout, and validate that rider is a string."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py _run(): messages = [{\"role\": \"user\", \"content\": question}]", "scenario": "With no system prompt, riders can use the model for unrelated tasks at Pedalo's cost, and tool-data prompt injection is easier.", "fix": "Add a system prompt scoping the agent to bike routing and treating tool output as data; test that it is present."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "planner.py plan(): _seen[rider] = hits + [now()]", "scenario": "Keys for riders who never return are never pruned; with rotated IDs the dict grows by up to 2000 keys per hour until restart.", "fix": "Sweep expired keys periodically or use a TTL store."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "test_planner.py test_the_per_rider_limit_applies", "scenario": "Window expiry is untested; changing '< 3600' to a huge value still passes, so a limited rider might never be let back in.", "fix": "Assert that a request at now=1000+3600 succeeds."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "planner.py _run(): result = f\"error: {exc}\"", "scenario": "Raw tool exception text (internal hosts, URLs, keys) reaches the model and may be repeated to the rider.", "fix": "Log the exception server-side and give the model a generic 'routing unavailable' message."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "location": "planner.py _run(): return reply[\"answer\"]", "scenario": "The answer is unchecked; if rendered as HTML, text influenced by the model or tool data is an XSS path.", "fix": "Ensure the frontend escapes the answer and check that it is a string."}
  ]
}
```