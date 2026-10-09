VERDICT: **REWORK.** The caps are mostly coded correctly. But the agent loop as written cannot drive a real tool-calling model. The rider identity and rate limits are probably not trustworthy in production. The tests skip the paths that control cost.

CONFIDENCE IN VERDICT: **medium.** Three things I could not see limit it: the `llm` wrapper (does it add a system prompt and tool schemas, and what does `tokens` count?), the HTTP layer (where does `request["rider"]` come from?), and the deployment (how many worker processes). I had no tools, so nothing was run.

## Pass 1: Reconstruct

The work claims a `/plan` endpoint where a model with a routing tool answers bike-route questions. It says signed-in riders only, with caps on question length (1000 chars), turns (5), tokens (15k per request), per-rider requests (30/h) and global requests (2000/h).

For it to be correct, these must all hold:

- `request["rider"]` is a server-verified identity.
- The `llm` callable knows the available tools and accepts this message format.
- `reply["tokens"]` reflects what Pedalo is billed.
- The process-local `_seen`/`_all` state is the only rate-limit state, meaning a single process that never restarts.
- Something constrains the model to bike routing.

None of these is shown in the material.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | PROBABLE | `plan`: `rider = request.get("rider")`; `if not rider` | "Signed-in riders only" is enforced only by a truthy check on a field of the same dict that carries `question`. The tests build both from one literal. Nothing verifies a session. | If `request` is the parsed POST body, an anonymous caller sends `{"rider":"x1","question":...}`. They then rotate `x2`, `x3`, … to bypass login and the 30/h limit, billing Pedalo up to the global cap. Each new ID also grows `_seen` forever. | Take the rider ID from the verified session or auth middleware as a separate argument, never from the body. Add a test that a body-supplied `rider` without a session is refused. |
| 2 | High | CONFIRMED (code), PROBABLE (effect) | `_run`: `llm(messages, max_tokens=...)`; `messages.append({"role":"tool",...})` | (a) `tools` is never passed to `llm`, so the model gets no tool names or schemas. (b) The model's own tool-call turn is never appended; only the tool result is. (c) The tool message has no tool-call ID. Real tool-use APIs (Anthropic `tool_use`/`tool_result`; OpenAI `tool_call_id`) reject or misread this sequence. | A rider asks for a route. The model can't call the router, or calls it and the next request errors. Or the model never sees its own call, re-calls the tool, and hits "turn limit" after 5 billed calls. The core feature fails while costing money. | Append the assistant reply, including tool-call IDs, before each tool result. Pass tool schemas to the model. Add a test where a fake LLM requires the prior assistant turn and returns an answer after one tool call. |
| 3 | High | PROBABLE | Module globals `_seen`, `_all`, `threading.Lock` | Limits live in one process's memory. With N workers or instances, the limits become 30·N per rider and 2000·N globally. Every deploy or restart resets them. | Under gunicorn with 8 workers, the "2000/h" cost ceiling is really 16,000/h, and the per-rider cap is 240/h. | Move the counters to a shared store (Redis or the DB) with atomic increments. Also add a hard spend cap at the model-provider account level. |
| 4 | High | PROBABLE | `_run`: `messages = [{"role":"user","content":question}]` | There is no system prompt or scope restriction, unless the unseen wrapper adds one. The endpoint is a general-purpose LLM billed to Pedalo, with up to 15k tokens per request. | A rider (or anyone, per #1) uses `/plan` to write essays or code. Pedalo pays, and the output appears on Pedalo's site. | Add a system prompt limiting scope to bike routing, and possibly an output check. Test that an off-topic question is declined. |
| 5 | Medium | CONFIRMED | `plan`: `except Refused` only; `tools[...]` call | Exceptions from `llm` (timeout, 429, 5xx, a malformed reply, `max_tokens=0` once `spent == MAX_TOKENS`) are not caught and escape as a 500. Neither the LLM call nor the tool call has a timeout. | The provider has an outage and riders get 500s, possibly with stack traces. A hung routing service holds a worker indefinitely. The quota slot is already used either way. | Catch provider errors and map them to a clean error. Set timeouts on both calls. Stop when `MAX_TOKENS - spent < 1`. Test with an `llm` that raises. |
| 6 | Medium | PROBABLE | `_run`: `max_tokens=MAX_TOKENS - spent` / `if spent > MAX_TOKENS` | The budget is checked only after billing. `max_tokens` caps output, but each turn re-sends the whole history as input (question plus up to 5×4000-char tool results). If `tokens` counts output only, input is not counted at all. If it counts both, the last call can still overshoot by its full input. | A 5-turn request bills well over 15k tokens, while the code reports it as within budget. | Define `tokens` as input plus output in the wrapper contract. Estimate the next call's input before sending it, and refuse if the estimate plus `max_tokens` exceeds the remaining budget. |
| 7 | Medium | CONFIRMED | `plan`: global `_all` check | One shared ceiling with no per-rider share means a few accounts can exhaust it for everyone for up to an hour. | About 67 accounts at 30/h (or one spoofer, per #1) fill 2000/h, and every legitimate rider gets "busy". | Keep the ceiling as a cost backstop, but add sign-up friction or per-account trust. Alert when the ceiling is near. |
| 8 | Medium | CONFIRMED (by reading; mutations not run) | `test_planner.py` | The tests miss the cost-critical paths. No test exceeds 15k tokens, so deleting `if spent > MAX_TOKENS` leaves all 9 tests green. `test_the_model_is_asked_for_no_more_than_the_remaining_budget` checks only the first call, so replacing `MAX_TOKENS - spent` with `MAX_TOKENS` passes. There is no test for window expiry, so changing `< 3600` to `< 10**9` passes. There are no tests for tool→answer, a tool exception, or an `llm` exception. | A regression removes a cost cap and CI stays green. | Add tests for each mutation above, then confirm each goes red against the mutated code. |
| 9 | Low | PROBABLE | `_run`: `result = f"error: {exc}"` | Tool exception text, which can include internal URLs or keys in HTTP client errors, is fed to the model and can surface in the answer. | The routing API fails and the model repeats the internal endpoint URL to the rider. | Log the exception and return a generic error to the model. |
| 10 | Low | UNVERIFIED | `plan` return `{"answer": ...}` | The model output is returned raw. If the site renders it as HTML, a prompt-injected answer is XSS. | A crafted question makes the model emit `<script>`. | Confirm the frontend escapes the answer, or sanitize it server-side. |

## What holds up

- The turn cap bounds the loop.
- Question length and type are checked before any model call or tool call (verified by tests).
- The rate-limit check and update happen together under one lock, so there is no race within a process.
- The tool-name lookup and bad args (`KeyError`/`TypeError`) are caught.
- Tool output is truncated to 4000 chars.
- A missing token count or missing answer is refused.
- There are 9 test methods, matching the claim.

## Unverified claims

- **"9 tests pass":** I could not run them. Run `python -m unittest test_planner` in a scratch copy.
- **"Signed-in riders only":** this depends on the caller. Show the route handler that builds `request`.
- **Token caps limit spend:** this depends on what `reply["tokens"]` counts. Show the wrapper and compare against the provider's usage report for a multi-turn request.
- **Rate limits hold in production:** this depends on the process and instance count. Show the deploy config.

## Questions for the author

1. Where does `request["rider"]` come from: the session or the body?
2. Does the `llm` wrapper add a system prompt and tool schemas? Does it rebuild the assistant turns?
3. Does `tokens` include input tokens?
4. How many processes or instances serve `/plan`?

## Decision-maker summary

Do not launch yet. Fix the agent loop so it actually works with the model provider. Confirm rider identity comes from the login session. Move the rate limits to shared storage and add a provider-side spend cap. If shipped as is, routing will likely fail on real traffic, and Pedalo's model bill may be exposed to anonymous or off-topic use well beyond the intended limits.

## Owner summary

The trip planner is not ready to launch. As written it likely cannot use its route-finding step correctly, and its protections against misuse and runaway costs may be weaker than they look. A few targeted fixes and better tests are needed before it handles real riders.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "PROBABLE", "location": "planner.py plan(): rider = request.get(\"rider\")", "scenario": "If rider comes from the POST body, an anonymous caller sets arbitrary rider IDs, bypassing login and the per-rider limit and billing Pedalo up to the global cap; _seen grows without bound", "fix": "Derive rider from the verified session/auth layer, not the body; test that a body-supplied rider without a session is refused"},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "planner.py _run(): llm(messages, max_tokens=...) and messages.append({\"role\":\"tool\",...})", "scenario": "Tools are never passed to llm, the assistant tool-call turn is never appended, and there is no tool-call ID; real tool-use APIs reject or misread this, so routing fails or loops to the turn limit after 5 billed calls", "fix": "Append the assistant reply with tool-call IDs before each tool result and pass tool schemas; add a tool-call-then-answer test with a strict fake LLM"},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "planner.py module globals _seen, _all, _lock", "scenario": "With N workers or instances, limits multiply by N and reset on every restart, so the 2000/h cost ceiling is not real", "fix": "Use a shared atomic store (Redis/DB) for counters; add a provider-level spend cap"},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "planner.py _run(): messages = [{\"role\":\"user\",...}]", "scenario": "No system prompt restricts scope, so the endpoint works as a general LLM billed to Pedalo, with output shown on Pedalo's site", "fix": "Add a routing-only system prompt and test that off-topic questions are declined"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py plan(): except Refused only; llm and tool calls", "scenario": "Provider timeouts, errors, or max_tokens=0 escape as 500s; no timeouts, so a hung routing service holds a worker", "fix": "Catch provider errors, set timeouts, stop when the remaining budget is below 1; test with a raising llm"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "planner.py _run(): max_tokens=MAX_TOKENS - spent; if spent > MAX_TOKENS", "scenario": "The budget is checked after billing and input is re-sent each turn, so actual billed tokens exceed 15k (fully, if tokens counts output only)", "fix": "Count input plus output and pre-check estimated input plus max_tokens against the remaining budget"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py plan(): global _all ceiling", "scenario": "About 67 accounts at 30/h exhaust 2000/h and every rider gets 'busy' for up to an hour", "fix": "Add per-account trust or sign-up friction and alerting near the ceiling"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "test_planner.py", "scenario": "Deleting the spent > MAX_TOKENS check, replacing MAX_TOKENS - spent with MAX_TOKENS, or widening the 3600s window all leave the 9 tests green; tool-to-answer and exception paths are untested", "fix": "Add tests for each mutation and confirm each goes red"},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "planner.py _run(): result = f\"error: {exc}\"", "scenario": "Internal URLs or keys in tool exception text reach the model and the rider", "fix": "Log the exception; send a generic error to the model"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "location": "planner.py plan(): return {\"answer\": ...}", "scenario": "If the frontend renders the answer as HTML, a prompt-injected answer is XSS", "fix": "Confirm frontend escaping or sanitize server-side"}
  ]
}
```