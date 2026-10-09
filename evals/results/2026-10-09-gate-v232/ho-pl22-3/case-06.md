# Adversarial Diagnostic Review: `planner.py` (/plan endpoint)

## Pass 1: Reconstruct

The work is a public, unauthenticated `POST /plan` handler. It passes a rider's free-text question to an LLM, runs any tool the model names, feeds each result back, and returns the model's final `answer`. The request asks for a model agent with a routing tool that answers "how do I get from A to B by bike."

For this to be safe in production, the following must hold, and none is stated in the work:
- The model eventually stops calling tools.
- Anonymous callers cannot drive unbounded billed model calls.
- The `llm` wrapper accepts this message format.
- `tools` contains only the routing tool.
- The model actually calls the router instead of inventing a route.
- Upstream code validates and limits the request.

## Pass 2: Attack (Track B, plus cost and abuse exposure)

**Main path traced (CONFIRMED by reading):**
1. `messages = [user question]`.
2. Loop: call `llm`. If the reply has `"tool"`, run it, append only a `role: "tool"` message, and loop again.
3. Otherwise return `reply["answer"]`.

There is no iteration cap, no system prompt, no timeout and no input limit. The assistant's own tool-call turn is never appended to `messages`.

**Hostile inputs:**
- **Question crafted to make the model keep calling tools** ("call the router for every pair of these 500 stations"): the loop never exits and each iteration is a billed call.
- **Missing `question` key:** raises `KeyError`, which surfaces as a 500.
- **Non-string `question`** (list or dict): it is passed raw as message content, so behaviour depends on the wrapper.
- **10 MB question:** it is sent to the model in full, and the cost is billed to Pedalo.
- **Model reply with neither `tool` nor `answer`** (refusal, truncation, wrapper error shape): `reply["answer"]` raises `KeyError` and the endpoint returns a 500.
- **Off-topic use** ("write my essay"): with no system prompt or scope check, the endpoint is a free general-purpose LLM proxy on Pedalo's bill.

**What holds:** an unknown tool name raises `KeyError` inside the `try` and becomes an error string, so the request does not crash. Bad `args` (wrong type or extra keys) raise `TypeError`, which is caught the same way. `json.dumps(..., default=str)` will not crash on non-JSON-serializable results.

**Tests:** none were supplied. Rule 5 cannot be applied, so test coverage is UNVERIFIED (zero).

## Pass 3: Self-check

- Findings about message format (F3) and tool scope (F5) depend on the `llm` wrapper and the `tools` dict, which are not shown. I kept them at PROBABLE or UNVERIFIED and did not assume the worst.
- The output-rendering risk (XSS) depends on the frontend. I list it as a question rather than a finding.
- **Most serious thing I might still be missing:** what the routing tool does with model-controlled `args`. If it builds URLs or queries from them, user-steered arguments could reach an internal service (server-side request forgery or injection). That would hide in the tool implementation, which is not under review.

---

**VERDICT: REWORK.** An unbounded, unauthenticated agent loop on a billed, front-page endpoint lets any anonymous caller generate unlimited model spend, and the conversation it builds is likely malformed.

**CONFIDENCE IN VERDICT: high.** The loop and cost findings are visible in the code. What limits confidence: the `llm` wrapper, the `tools` dict, the HTTP wiring and the frontend were not provided.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `while True:` loop; `continue` after the tool call | No iteration cap and no budget per request. | The model keeps emitting tool calls, either prompted by an attacker or by re-asking because it cannot see its own calls (F3). One request runs billed `llm` calls until the process or the HTTP timeout kills it. The handler may keep running server-side even after the client disconnects. | Cap iterations (for example 5) and set a token or cost budget per request; return a fixed error when either is hit. Test: a fake `llm` that always returns a tool call must terminate within N calls. |
| 2 | Critical | CONFIRMED (code) / PROBABLE (exposure) | Docstring "Anyone may call it; no login"; `plan()` has no limits | No authentication, rate limit, or input-length cap on a billed endpoint linked from the front page. | A script sends 100 requests per second with long prompts, which is effectively a denial-of-wallet attack. | Limit per IP and per session, cap question length (for example 500 characters), set a global spend circuit breaker, add a CAPTCHA or app token. Rate limits upstream count only if verified in the deployed configuration. |
| 3 | High | CONFIRMED (code) / PROBABLE (impact) | `messages.append({"role": "tool", ...})` | The assistant's tool-call turn is never appended, and the tool message has no `tool_call_id`. OpenAI-style APIs reject an orphan `tool` message, and Anthropic's API has no `tool` role at all. | Either every tool-using request fails with an API error, or the wrapper tolerates it and the model, unable to see its own call, calls the tool again and again. That feeds F1. | Append the assistant turn with its tool call, and pair each result with the call id in the provider's format. Test against the real `llm` wrapper with a 2-step tool conversation. |
| 4 | High | CONFIRMED | `messages = [{"role": "user", ...}]`; no system prompt | The agent is not scoped to bike routing. | A user asks for unrelated content, gets a free LLM at Pedalo's cost, and Pedalo's brand appears on whatever the model says. | Add a system prompt restricting scope and a refusal path; consider a cheap topic classifier before the agent runs. Test: an off-topic prompt returns a refusal. |
| 5 | High | UNVERIFIED | `tools[reply["tool"]](**reply.get("args", {}))` | The code dispatches any tool name the model emits, with arguments controlled by the model (and so by the user). | If `tools` contains more than the router, or the router fetches URLs or queries from `args`, prompt injection can reach those sinks. | Allow-list only the routing tool and validate its args against a schema (coordinates or place names, length limits). Settle this by showing how `tools` is built and the router's code. |
| 6 | Medium | CONFIRMED | `result = f"error: {exc}"` | Raw exception text goes into the model context, and the model may repeat it to the anonymous user. | The routing API fails with a message containing an internal URL or API key query string, and the model echoes it. | Log the exception server-side and give the model a generic "routing unavailable" message. |
| 7 | Medium | CONFIRMED | `request["question"]`, `reply["answer"]` | No input validation or response-shape handling. | A missing or non-string question, or a model reply without `answer`, raises a 500. | Validate input (type, non-empty, length) and return 400 on failure. Handle unexpected reply shapes with a fallback message. |
| 8 | Medium | CONFIRMED | Whole function | No timeouts on `llm` or tool calls. | A hung routing API pins a worker per request, and under load the site stalls. | Set timeouts per call and an overall deadline for the request. |
| 9 | Medium | PROBABLE | `return {"answer": reply["answer"]}` | Nothing makes the model call the router before answering. | The model invents a route with plausible street names and no tool call, and a rider follows bad directions. | Require at least one successful routing call before returning a route, or return structured router output alongside the text. Test: a fake `llm` that answers directly is rejected. |
| 10 | Medium | CONFIRMED | None supplied | No tests. | Regressions in F1, F3 and F7 ship unnoticed. | Add tests for termination, malformed input, unknown tool and message format; check each by mutation (remove the cap and confirm the test goes red). |
| 11 | Low | CONFIRMED | `json.dumps(result, default=str)` | Tool output size is unbounded. | A large router payload inflates the tokens of every later call. | Truncate or summarize tool output before appending it. |
| 12 | Low | CONFIRMED | Whole function | No logging of request id, iteration count, tokens or cost. | Spend spikes cannot be attributed or alerted on. | Log usage per request and alert on a spend threshold. |

## What holds up

- An unknown tool name or bad `args` is caught inside the `try` and does not crash the request.
- `default=str` prevents serialization crashes.
- The function is small and easy to harden.

## Unverified claims

- **"POST /plan":** the HTTP wiring, request parsing and any upstream middleware (auth, rate limit, size limit) are not shown. Confirm with the router or framework config and the deployed gateway settings.
- **"Routing tool":** the contents of `tools` and the router implementation are not shown. Confirm with the code that builds `tools`.
- **`llm` contract:** whether it returns `{"tool","args"}` or `{"answer"}` and accepts `role: "tool"` without an assistant turn. Confirm with the wrapper code and a live 2-step call.

## Questions for the author

1. What does `tools` contain in production, and what does the routing tool do with its args?
2. What `llm` wrapper and provider is this, and has a tool-using conversation run end to end against it?
3. Is there any rate limiting, auth or spend cap in front of this endpoint today, verified in the deployed config?
4. How is `answer` rendered on the rider site: as escaped text or as HTML or Markdown?

## Decision-maker summary

Do not launch as is. The endpoint lets anyone trigger an unlimited number of billed model calls per request, with no login or rate limit, and the agent is not restricted to bike routing. Adding an iteration cap, a spend cap, rate limiting, a scoped system prompt and a corrected tool-message format makes it launchable; without them, the risks are runaway spend and the route-planning feature being used as a free general chatbot.

## Owner summary

The new trip-planning feature works in principle, but as built anyone on the internet can make it run up an unlimited bill for us, and it will answer any question, not just bike routes. It can also give directions without actually checking a map. A few targeted fixes are needed before it goes live, mainly limits on usage and cost and keeping it on topic.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "planner.py: while True loop / continue after tool call", "scenario": "Model keeps emitting tool calls (attacker-prompted or because it cannot see its own calls); a single request runs unbounded billed llm calls.", "fix": "Cap iterations and set a token/cost budget per request; test with a fake llm that always returns a tool call."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "planner.py: plan() docstring 'Anyone may call it; no login'", "scenario": "Anonymous scripted traffic with long prompts drives unlimited model spend (denial of wallet).", "fix": "Rate limit per IP/session, cap question length, add a global spend circuit breaker, add app token or CAPTCHA; verify in deployed config."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "planner.py: messages.append({'role': 'tool', ...})", "scenario": "Assistant tool-call turn and tool_call_id are missing; provider rejects the conversation, or the model repeats calls it cannot see, feeding the unbounded loop.", "fix": "Append the assistant turn with its tool call and pair results by call id in the provider format; integration-test a 2-step tool conversation."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "planner.py: messages initialised with user content only, no system prompt", "scenario": "Users use the endpoint as a free general-purpose LLM for off-topic content billed to and branded as Pedalo.", "fix": "Add a scoped system prompt and refusal path, optionally a topic classifier; test that an off-topic prompt is refused."},
    {"severity": "High", "evidence_level": "UNVERIFIED", "location": "planner.py: tools[reply['tool']](**reply.get('args', {}))", "scenario": "Model-chosen tool name and user-influenced args reach any tool in the dict or the router's backend (injection, SSRF).", "fix": "Allow-list the routing tool only and validate args against a schema; review how tools is built and the router code."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py: result = f'error: {exc}'", "scenario": "Exception text with internal URLs or keys enters model context and is echoed to an anonymous user.", "fix": "Log exceptions server-side; give the model a generic error message."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py: request['question'], reply['answer']", "scenario": "Missing or non-string question, or a model reply without 'answer', raises KeyError and returns a 500.", "fix": "Validate input (type, non-empty, length) and return 400; handle unexpected reply shapes with a fallback."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py: llm(...) and tool calls", "scenario": "A hung model or routing API holds a worker per request; under load the site stalls.", "fix": "Set timeouts per call and an overall request deadline."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "planner.py: return {'answer': reply['answer']}", "scenario": "Model answers without calling the router and invents a route that a rider follows.", "fix": "Require a successful routing call before returning a route; test with a fake llm that answers directly."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "work as submitted: no tests", "scenario": "Regressions in loop termination, message format and input handling ship unnoticed.", "fix": "Add tests for termination, malformed input, unknown tool and message format; verify each by mutation."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "planner.py: json.dumps(result, default=str)", "scenario": "A large router payload inflates tokens on every later call.", "fix": "Truncate or summarize tool output before appending."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "planner.py: plan() (no logging)", "scenario": "Spend spikes cannot be attributed or alerted on.", "fix": "Log request id, iterations, tokens and cost; alert on a spend threshold."}
  ]
}
```