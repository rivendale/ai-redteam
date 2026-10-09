# Adversarial Diagnostic Review: Pedalo `/plan` endpoint

No tools were available in this session, so nothing was run. Every finding below comes from reading the code. "CONFIRMED" means I can point to the exact lines; it does not mean I executed them.

## Pass 1: Reconstruct

The work claims to implement `POST /plan`: an agent loop where a model, given a rider's question and a routing tool, answers "how do I get from A to B by bike". It also claims caps on input length, turns, tokens, per-rider requests and global requests, plus nine passing tests.

For this to be correct, several things must hold:
- The `llm` adapter must accept a message history containing only `user` and `tool` entries and still continue a tool-use conversation.
- `request["rider"]` must be set by the auth layer, not by the client.
- The service must run as a single process, since all rate-limit state is in memory.
- `reply["tokens"]` must reflect the tokens Pedalo is billed for.
- The model must stay on the bike-routing task with no system prompt.

None of these is shown in the work.

## Pass 2: Attack (Track B, with some Track A and R)

**The agent loop drops the model's own turns (core feature).** When the model calls a tool, the code appends only `{"role": "tool", "content": ...}`. It never appends the assistant's reply, the tool name, the args, or a tool-call id.
- On the next turn the model sees `[user question, anonymous tool output]`.
- Both major provider APIs reject a `tool` or `tool_result` message that does not follow an assistant tool call with a matching id. That gives a 400 error, which is uncaught here.
- A permissive adapter would let the model run but lose track of what it asked for. It would likely re-call the tool until `turn limit`, billing 5 calls and returning an error.
- No test exercises the path "tool call, then answer", so the nine green tests cannot see this.

**Auth and rate limits depend on where `rider` comes from.** `rider` and `question` are read from the same `request` dict, which suggests a parsed body or merged params.
- If a client can set `rider`, then "signed-in riders only" is a fiction.
- A client could also rotate `rider` per request and bypass the 30/hour limit.
- A non-hashable `rider`, such as a JSON list, raises `TypeError` in `_seen.get`.

**Rate limiting is per process.** `_seen`, `_all` and `_lock` live in module memory.
- With N gunicorn/uvicorn workers or N instances, the per-rider cap becomes 30·N and the "global" cap becomes 2000·N.
- State also resets on every deploy or restart.

**Nothing scopes the model to bike routing.** There is no system prompt.
- Any signed-in rider can use `/plan` as a general-purpose LLM billed to Pedalo, for example "write my essay".
- The worst-case spend is up to 2000 requests × 15k tokens per hour per process.
- The model can also answer a routing question without ever calling the routing tool, giving an ungrounded, possibly unsafe route on a customer-facing surface.

**Token accounting does not bound billed spend.** `max_tokens` caps output per call, but the full history is re-sent as input every turn.
- If `tokens` is output-only, input cost is untracked.
- If `tokens` is input+output, a call can exceed the remaining budget, because `max_tokens` does not limit input. The overshoot is only detected after it is billed.
- Negative or boolean `tokens` values pass `isinstance(..., int)`, so a negative value would reduce `spent`.
- When `spent == MAX_TOKENS`, the next call is made with `max_tokens=0`, which most APIs reject.

**Failure handling.**
- Exceptions from `llm` (timeouts, 429s, 5xx) are not caught: they surface as a 500 after the rate-limit slot has been consumed.
- Neither `llm` nor the tool call has a timeout.
- Tool exception text (`f"error: {exc}"`) is fed to the model. It may contain internal URLs, keys or hosts, which the model can repeat to the rider.

**Resource growth.** `_seen` keeps a key for every rider who has ever called and only prunes on that rider's next request, so memory grows without bound.

**Global ceiling as a DoS lever.** 67 accounts at 30/hour (or one spoofer, if `rider` is client-set) exhaust the 2000/hour ceiling and lock out every rider with `busy`.

**The tests have gaps that matter.** I count 9 test methods; "9 pass" is unverified. By reading, these mutations would leave all nine tests green:
- Deleting `if spent > MAX_TOKENS: raise Refused("token budget")`. The never-stopping-model test still hits `turn limit` first.
- Replacing `MAX_TOKENS - spent` with `MAX_TOKENS`. `test_the_model_is_asked_for_no_more_than_the_remaining_budget` only checks the first call.
- Removing the `try/except` around the tool call, or never feeding the tool result back to the model.

No test covers a tool call followed by an answer, the tool error path, window expiry, or an `llm` exception.

**Requirement fit.** The routing tool, the LLM adapter and the HTTP route registration are not in the work; only the handler is. Whether `/plan` exists end to end is unverified.

## Pass 3: Self-check

I removed an XSS finding about rendering the model's answer: I could not tie it to a location, because the rendering code is not shown.

I kept the rider-spoofing finding at Critical but UNVERIFIED, because its severity if true is decisive and one fact settles it.

Where the most serious problem could still hide:
- In the unseen `llm` adapter. It decides whether the history bug is a hard failure or a silent loop, and what `tokens` actually counts.
- In the deploy topology, which decides whether the caps mean anything.

---

**VERDICT: REWORK.** The agent loop never records the model's own tool calls, so the core "answer using the routing tool" path is broken or wasteful against any real provider. The tests cannot detect it.

**CONFIDENCE IN VERDICT: medium-high.** The history bug is visible in the code. Its exact runtime symptom depends on the unseen `llm` adapter, and the auth and deployment findings depend on code not supplied.

### Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | UNVERIFIED | `plan`: `rider = request.get("rider")` | Identity is read from the same dict as the client's `question`. Nothing shows it comes from a verified session. | Client posts `{"rider":"x1","question":...}`. Anonymous access succeeds, and rotating `x1, x2, …` bypasses the per-rider cap. | Show where `request` is built. Derive `rider` only from the authenticated session. Add a test that a body-supplied `rider` without a session is refused. |
| 2 | High | CONFIRMED (omission); failure mode PROBABLE | `_run`: `messages.append({"role": "tool", ...})` | The assistant's tool-call turn (name, args, id) is never appended. The tool message has no id linking it to a call. | Any question needing the routing tool. Either the provider returns a 400, uncaught, which becomes a 500 after billing one call. Or the model re-calls the tool until `turn limit`, billing 5 calls and answering nothing. | Append the assistant reply, including its tool-call id, before the tool result, in the provider's required shape. Test: an LLM stub that calls `route` and then answers using the tool's output, asserting that the second call's `messages` contains the call and the result. |
| 3 | High | PROBABLE | Module globals `_seen`, `_all`, `_lock` | Rate limits are per process and reset on restart. | 4 workers × 3 instances gives a real global cap of 24,000/hour and a per-rider cap of 360/hour. A deploy wipes all counters. | Move counters to a shared store (Redis with atomic INCR/EXPIRE, or a sliding window). Confirm the worker count for production. |
| 4 | Medium | PROBABLE | `_run`: `messages = [{"role":"user","content":question}]` | No system prompt scopes the model to bike routing or requires it to use the routing tool. | "Write a 3,000-word essay…" is answered at Pedalo's cost. "A to B?" is answered from memory with an invented route. | Add a system prompt restricting scope and requiring the routing tool. Reject or redirect off-topic requests. Test that an answer with no tool call is either flagged or not returned as a route. |
| 5 | Medium | CONFIRMED | `_run`: `reply = llm(...)` and `tools[...](...)` | Exceptions from `llm` are uncaught. Neither `llm` nor the tool has a timeout. | Provider times out or returns 429: the rider gets a 500, possibly with a stack trace, and the worker hangs on a stalled call. | Wrap the `llm` call and map errors to a clean error. Set timeouts on the client and the tool. Test an `llm` stub that raises. |
| 6 | Medium | PROBABLE | `_run`: `max_tokens=MAX_TOKENS - spent` and `spent += reply["tokens"]` | The cap bounds output per call, not the billed input. The check runs after billing. Negative or bool `tokens` are accepted. At `spent == MAX_TOKENS` the next call gets `max_tokens=0`. | A 5-turn tool loop re-sends a growing history: real billed tokens exceed 15k, or the last call overshoots. An adapter bug returning `-1` lets the loop run longer. | Clarify what `tokens` counts. Account for input+output. Reject `tokens < 0` or `bool`. Stop when the remaining budget is ≤ a minimum. |
| 7 | Medium | CONFIRMED (by reading; mutations not run) | `test_planner.py` | The token-budget check and the per-turn subtraction are untested. No test covers tool → answer, the tool error path, or `llm` raising. | Deleting the `spent > MAX_TOKENS` check, or dropping `- spent`, leaves all 9 tests green. | Add a stub with `tokens=6000` per turn and assert `token budget` on turn 3. Assert the `max_tokens` sequence `[15000, 9000, 3000]`. Add the tool → answer test from #2. |
| 8 | Medium | PROBABLE | `plan`: `MAX_GLOBAL_PER_HOUR` check | The shared ceiling can be exhausted by a few accounts. | 67 riders × 30 requests fill 2000/hour, and every other rider gets `busy` for up to an hour. | Size the global cap against the per-rider cap and the number of active riders. Consider per-account-age or reputation limits. Alert when the ceiling is near. |
| 9 | Low | PROBABLE | `_run`: `result = f"error: {exc}"` | Raw exception text goes to the model and can be echoed to the rider. | The routing client raises with a URL containing an API key, and the model repeats it in the answer. | Return a generic tool-error string to the model and log the detail server-side. |
| 10 | Low | CONFIRMED | `plan`: `_seen[rider] = ...` | The dict is never pruned for inactive riders. | Over months, memory grows with every rider ever seen. | Evict empty or expired keys, or use a TTL store (which also fixes #3). |

### What holds up

- The per-rider and global check-and-record runs under one lock, so it is atomic within a process.
- The question type and length check runs before any model call, and is tested.
- The turn cap is enforced and tested; that test would fail if the loop were unbounded.
- Tool dispatch errors (unknown tool name, bad args) are contained and do not crash the loop.
- Tool output is truncated to 4,000 characters.
- Replies missing `tokens` or `answer` are refused, and that is tested.
- Test state is reset in `setUp`, and the global-cap test restores the constant.

### Unverified claims

- **"9 tests pass"**: run `python -m unittest test_planner -v` and check for 9 `ok` lines.
- **"Signed-in riders only"**: show the framework code that builds `request` and sets `rider`.
- **Caps hold in production**: show the worker and instance count, or the shared-store design.
- **The routing tool exists and is wired in, and the `/plan` route is registered**: neither is in the work. Show the tool, the adapter and the route registration.
- **`tokens` reflects billed usage**: show the adapter mapping from the provider's usage fields.

### Questions for the author

1. Where is `request["rider"]` set, and can a client influence it?
2. What does the `llm` adapter do with a `{"role":"tool"}` message that has no preceding assistant tool call? Is there an end-to-end run against the real provider that produced an answer?
3. How many processes and instances serve `/plan` in production?
4. Does `tokens` include input tokens?

### Decision-maker summary

Do not launch yet. The agent loop does not record the model's own tool calls, so route questions will likely error or burn five billed calls without answering, and the passing tests never exercise that path. Before relying on the spend caps, confirm that rider identity comes from the session and that the limits hold across all production processes. Otherwise anonymous or multiplied usage is billed to Pedalo.

### Owner summary

The route-planning feature is not ready to launch. As written, it will probably fail on the questions that need the map lookup while still costing money for each attempt. The spending limits may also not hold once the site runs on more than one server, so these issues should be fixed and retested first.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "UNVERIFIED", "location": "planner.py plan(): rider = request.get(\"rider\")", "scenario": "If request is the client body, a client sets rider freely: anonymous access, and rotating rider IDs bypasses the per-rider cap; a list-valued rider raises TypeError.", "fix": "Derive rider only from the authenticated session; test that a body-supplied rider without a session is refused."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "planner.py _run(): messages.append({\"role\": \"tool\", ...})", "scenario": "Assistant tool-call turns are never appended and the tool message has no call id; real providers reject the history (uncaught 400, then 500) or the model loops to 'turn limit', billing 5 calls with no answer.", "fix": "Append the assistant reply with its tool-call id before the tool result in the provider's format; add a stub test of tool call then answer that inspects the second call's messages."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "planner.py module globals _seen, _all, _lock", "scenario": "With N workers or instances, the per-rider and global caps multiply by N and reset on restart, so spend caps do not hold.", "fix": "Use a shared atomic store (e.g. Redis) for counters; confirm the production worker count."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "planner.py _run(): messages initialised with user question only", "scenario": "No system prompt: riders use /plan as a general LLM at Pedalo's cost, and the model can answer routes without calling the routing tool.", "fix": "Add a scoping system prompt that requires the routing tool; refuse off-topic requests; test that an answer with no tool call is not returned as a route."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py _run(): llm(...) call and tools[...](...) call", "scenario": "Provider timeout or 429 raises uncaught, giving a 500 after the rate slot is consumed; with no timeouts a stalled call hangs the worker.", "fix": "Catch llm errors and map them to a clean error; set client and tool timeouts; test an llm stub that raises."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "planner.py _run(): max_tokens=MAX_TOKENS - spent; spent += reply[\"tokens\"]", "scenario": "Input tokens grow per turn and are uncapped or only checked after billing; negative or bool tokens pass the isinstance check; spent == MAX_TOKENS triggers a max_tokens=0 call.", "fix": "Account input+output tokens, reject tokens < 0 or bool, stop when the remaining budget falls below a minimum."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "test_planner.py (whole file)", "scenario": "Deleting the token-budget check or the '- spent' subtraction leaves all 9 tests green; there is no tool->answer, tool-error or llm-exception test.", "fix": "Add a tokens=6000 stub asserting 'token budget' and the max_tokens sequence [15000, 9000, 3000]; add a tool->answer test and an llm-raises test."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "planner.py plan(): MAX_GLOBAL_PER_HOUR check", "scenario": "About 67 accounts at 30/hour exhaust the 2000/hour ceiling, and every other rider gets 'busy' for up to an hour.", "fix": "Size the global cap against the per-rider cap and the active rider count; add alerting; consider tiered limits."},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "planner.py _run(): result = f\"error: {exc}\"", "scenario": "Exception text containing internal URLs or keys is passed to the model and echoed to the rider.", "fix": "Send a generic tool-error string to the model; log the details server-side."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "planner.py plan(): _seen[rider] = hits + [now()]", "scenario": "Keys for inactive riders are never evicted; memory grows with every rider ever seen.", "fix": "Evict expired keys or use a TTL store."}
  ]
}
```