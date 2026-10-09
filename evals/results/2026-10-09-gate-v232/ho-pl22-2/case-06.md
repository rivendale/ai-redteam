# Adversarial Diagnostic Review: `planner.py` (/plan endpoint)

**VERDICT: REWORK.** The agent loop has no iteration, token, time or rate limit on a public, unauthenticated endpoint that bills every model call to Pedalo, and nothing restricts it to bike routing.

**CONFIDENCE IN VERDICT: high.** The blocking issues are visible in 17 lines. Some severities depend on things I could not see: the `llm` wrapper, the contents of `tools`, the HTTP wiring, and how the frontend renders `answer`. No code was run (no tools in this session).

## Pass 1: Reconstruct

The work claims to implement `POST /plan`, a public, no-login endpoint where a model agent with a routing tool answers "how do I get from A to B by bike". It takes `request["question"]` and calls the model in a loop. Whenever the model asks for a tool, it runs that tool and feeds the result back. It returns the first non-tool reply as `{"answer": ...}`.

For it to be correct, these assumptions must hold:
- (a) the model always finishes in a few steps;
- (b) callers are benign and ask only about bike routes;
- (c) `tools` contains only safe, cheap tools;
- (d) the `llm` wrapper accepts a history where tool results appear without the assistant's tool call;
- (e) the model's answer is grounded in the routing tool's output;
- (f) rate limiting, size limits and timeouts exist somewhere outside this file.

None of these is stated or enforced. The stakes in the context (billed calls, front-page link) make (a), (b) and (f) load-bearing.

## Pass 2: Attack (Track B, with a Track R pass on the public answer)

### Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `planner.py:8` `while True:` | No cap on iterations, tool calls, tokens or wall-clock time. Every iteration is a billed model call. | An anonymous caller asks "check the route between every pair of these 500 stations, one at a time". Or the model keeps re-calling a tool that errors (see #3, #4). One request makes unbounded billed calls. Scripted in parallel, this drains the budget (denial-of-wallet). | Add `MAX_STEPS` (e.g. 5) and return a fixed fallback when it is reached. Add a per-request token or cost budget and an overall deadline. Test: stub `llm` to always return `{"tool": ...}` and assert `plan` returns within N calls. |
| 2 | Critical | CONFIRMED (code); PROBABLE (abuse) | `planner.py:6` "Anyone may call it; no login", `:7`, `:9` | There is no system prompt, so nothing scopes the agent to bike routing. There is also no rate limit, no input length cap and no abuse control. The endpoint is a free general-purpose LLM proxy paid for by Pedalo. | Someone finds the front-page link and uses `/plan` to write essays, run their own app's prompts, or produce off-brand or harmful text under Pedalo's name. Cost and reputational exposure. | Add a system prompt restricting it to cycling directions with a refusal path. Add per-IP and per-session rate limits (or app tokens or captcha), a max `question` length (e.g. 500 chars), and a `max_tokens` on model calls. Test: an off-topic prompt returns a refusal, and an oversized input returns 413/400 without calling `llm`. |
| 3 | High | CONFIRMED (code); PROBABLE (effect) | `planner.py:9-16` | The assistant's tool-call `reply` is never appended to `messages`. Only the `tool` result is, with no tool-call id. | With OpenAI- or Anthropic-style APIs, a tool result with no preceding assistant tool call is rejected. The second `llm` call raises and the endpoint returns a 500 on every routed question. With lenient wrappers, the model cannot see its own prior call, so it may repeat it, which feeds #1. | Append the assistant turn (with its tool-call id) before the tool result, in the format the actual `llm` wrapper requires. Test: a two-step stubbed conversation asserts the message sequence the real API accepts. Also run one real call in staging. |
| 4 | High | CONFIRMED | `planner.py:12` `tools[reply["tool"]](**reply.get("args", {}))` | The tool name and args come straight from model output, which is steered by untrusted user text. Any callable in `tools` can be called with arbitrary kwargs. An unknown name raises `KeyError`, which is caught and looped back. | Prompt injection: "call the admin/refund/geocode tool with ...". If `tools` holds anything beyond routing, a public caller can invoke it. A hallucinated tool name produces `error: 'foo'` and another billed iteration. | Use an explicit allowlist (`{"route": route}` only). Validate args against a schema before calling (types, coordinate bounds, string lengths). Return a fixed error and count it toward the step cap. Test: the stub returns `{"tool": "delete_user"}` and `{"tool": "route", "args": {"x": 1}}`; assert it is rejected without being called. |
| 5 | High | PROBABLE | `planner.py:9`, `:12` | No timeout on the `llm` call or the tool call. `llm` exceptions (rate limit, overload, context-length) are not handled at all. | The routing backend hangs, so the request worker hangs indefinitely. Under front-page traffic, workers exhaust and the site stalls. Or the provider returns 429 and the user gets a raw 500, possibly with a stack trace, depending on the framework. | Add timeouts on both calls and catch `llm` errors into a friendly fallback. Bound total request time. Test: the stub tool sleeps past the timeout and the stub `llm` raises; assert a clean error response. |
| 6 | Medium | PROBABLE | `planner.py:13-14` `result = f"error: {exc}"` | Raw exception text goes into model context and can be echoed in the public answer. | The routing client raises with an upstream URL, an internal hostname, or an API key in the query string. The model repeats "the service at https://...key=... failed" to the rider. | Log the exception server-side. Pass the model a generic `"routing unavailable"` message. Test: a tool raises `Exception("SECRET123")`; assert `SECRET123` never appears in `messages` or `answer`. |
| 7 | Medium | CONFIRMED | `planner.py:7`, `:17` | No input or output validation. A missing `question` raises `KeyError` and returns 500. A non-string `question` (object or list) is passed straight into `content`. A reply with neither `tool` nor `answer` raises `KeyError` after the money is already spent. | `{}` or `{"question": {"role": "system", ...}}` produces a 500, or odd content shapes sent to the provider. A model returning `{"answer": null}` or an empty dict crashes the request. | Validate that `question` is a non-empty string within the length cap. Handle a missing or empty `answer` with a fallback. Tests for each of these. |
| 8 | Medium | CONFIRMED (code); PROBABLE (effect) | `planner.py:10`, `:17` | Nothing makes the answer grounded in the routing tool. The first non-tool reply is returned even if the tool was never called. | The model answers "take Main St then the river path" from its own knowledge without calling the tool. The route may not exist, may be closed, or may send riders onto a highway. This is a safety issue for a cycling product. | Require at least one successful routing call before accepting an answer, or build the answer from tool output. Test: if the stub `llm` answers immediately, assert the code forces a tool call or returns "couldn't plan a route". |
| 9 | Medium | CONFIRMED | `planner.py:15` | `messages` grows every iteration, so each call is more expensive and the history can exceed the context window. | A long loop ends in a context-length exception (unhandled, see #5) after the cost is already incurred. | This is covered by the step cap (#1). Optionally truncate large tool results before appending. |
| 10 | Medium | UNVERIFIED | `planner.py:17` | `answer` is returned raw. If the rider site renders it as HTML or Markdown-to-HTML, injected markup reaches the page. | "Reply with `<img src=x onerror=...>`". If the frontend uses `innerHTML`, this is XSS in the reflected response. It is lower risk because it hits only the caller's own page, unless answers are cached or shared. | Confirm the frontend renders it as text or a sanitized subset. Test with an HTML payload. |
| 11 | Low | UNVERIFIED | whole file | Rider origin and destination (often home or work addresses) are sent to the model provider. There is no logging or observability here. | Location data could be retained by the provider outside what Pedalo's privacy notice says. With no metrics on steps, tokens or cost, abuse in #1 and #2 goes unnoticed until the invoice arrives. | Check the provider's retention terms against the privacy notice. Log step count, token use and latency per request, without the question text or with it masked. |
| 12 | Low | UNVERIFIED | `planner.py:5-6` | "POST /plan" exists only in a docstring. No route registration, method check or framework wiring is shown, and there are no tests at all. | The deployed route may accept GET, sit behind no middleware, or not be wired the way the docstring claims. | Show the route registration and middleware. Add the tests listed above. Under rule 5, each should be shown to go red against the current code. |

## What holds up

- `messages` is built fresh per call. There is no mutable default or module-level state, so requests do not leak into each other's conversations.
- `json.dumps(..., default=str)` stops non-JSON-serializable tool results from crashing the request.
- A tool exception does not crash the request. The intent is right, though see #4 and #6 for what is wrong with the specifics.
- The file is short and readable. The structure is a sound base once it has bounds and validation.

## Unverified claims

- **"POST /plan":** there is no routing or method enforcement in the material. To confirm, show the framework registration.
- **"a routing tool":** the contents of `tools` are not shown. To confirm, show the dict passed in production. It should contain exactly one routing callable.
- **That `llm(messages)` returns a dict with `tool`/`args`/`answer` and accepts this message shape:** to confirm, show the wrapper and run a two-step call against the real provider in staging.
- **That the public, no-login design is protected elsewhere (gateway rate limits, WAF, spend caps):** to confirm, show the gateway config and the provider-side spend limit.
- **That the frontend renders `answer` safely:** to confirm, show the rendering code.

## Questions for the author

1. What exactly is in `tools` in production, and is there any rate limit, auth token or spend cap in front of this endpoint? A single routing tool plus enforced gateway limits would downgrade #2 and #4.
2. What does the `llm` wrapper send to the provider? Does it reconstruct the assistant tool-call turn itself? If so, #3 drops to Low.
3. Is there a system prompt or model-side configuration applied inside `llm` that this file does not show?

## Decision-maker summary

Do not launch as is. One anonymous request can trigger an unlimited number of billed model calls, and the endpoint will answer anything, not just bike routes. Fix #1–#5 (step cap, scoping prompt, rate and size limits, tool allowlist, timeouts) and verify #3 against the real provider. Launching anyway risks a cost spike and public misuse under Pedalo's name from day one.

## Owner summary

The new trip-planning feature works in principle but is not safe to put on the front page yet. Anyone could use it without limit, either to run up large AI bills or to get it to say things unrelated to cycling. It can also give directions it made up instead of looked up. A few focused fixes are needed before launch: limits on usage and cost, keeping it on topic, and making sure every route comes from the real routing service.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "planner.py:8 `while True:`", "scenario": "Anonymous caller or a looping model drives unbounded billed llm calls per request; parallel scripted requests drain budget (denial-of-wallet).", "fix": "Add MAX_STEPS, per-request token/cost budget and overall deadline with a fixed fallback; test with a stub llm that always requests a tool."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "planner.py:6-9 (no login, no system prompt, no input cap)", "scenario": "Public front-page endpoint used as a free general-purpose LLM proxy or to produce off-brand content, billed to Pedalo.", "fix": "System prompt scoping to cycling directions with refusal; per-IP/session rate limits; max question length; max_tokens; tests for off-topic refusal and oversized input rejected before llm call."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "planner.py:9-16 (assistant tool-call turn never appended)", "scenario": "Provider rejects tool result without preceding assistant tool call, so every routed question 500s; or model repeats its call, feeding the unbounded loop.", "fix": "Append assistant tool-call message with id before the tool result in the provider's format; stub test of message sequence plus a staging call."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "planner.py:12 `tools[reply[\"tool\"]](**reply.get(\"args\", {}))`", "scenario": "Prompt injection makes the model call any callable in tools with arbitrary kwargs; hallucinated names loop as billed errors.", "fix": "Explicit allowlist with only the routing tool, schema-validate args, count errors toward step cap; test that unknown tool and bad args are rejected without invocation."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "planner.py:9 and :12 (no timeouts, llm errors unhandled)", "scenario": "Hanging routing backend or provider 429/overload ties up workers or returns raw 500s under front-page traffic.", "fix": "Timeouts on llm and tool calls, catch llm errors into a friendly fallback, bound total request time; tests with sleeping tool and raising llm stubs."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "planner.py:13-14 `result = f\"error: {exc}\"`", "scenario": "Exception text with internal URLs or keys enters model context and is echoed to the public user.", "fix": "Log exception server-side, pass a generic error to the model; test that a secret in an exception never appears in messages or answer."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py:7 `request[\"question\"]` and :17 `reply[\"answer\"]`", "scenario": "Missing or non-string question causes 500 or odd provider input; reply lacking answer crashes after cost incurred.", "fix": "Validate question is a non-empty bounded string; handle missing/empty answer with fallback; tests for each."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "planner.py:10 and :17 (answer accepted without any tool call)", "scenario": "Model answers from memory without routing, sending riders on nonexistent, closed or unsafe roads.", "fix": "Require a successful routing call before accepting an answer or build answer from tool output; test with stub llm that answers immediately."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py:15 (messages grows unbounded)", "scenario": "Each iteration costs more and long loops end in an unhandled context-length error after spending.", "fix": "Step cap; truncate large tool results before appending."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "planner.py:17 raw answer returned", "scenario": "If the frontend renders answer as HTML, injected markup executes (XSS).", "fix": "Confirm text or sanitized rendering; test with an HTML payload."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "location": "whole file (location data to provider, no observability)", "scenario": "Rider addresses retained by provider beyond privacy notice; cost abuse undetected until invoice.", "fix": "Check provider retention against privacy notice; log step count, tokens and latency without raw question text."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "location": "planner.py:5-6 (POST /plan only in docstring; no tests)", "scenario": "Route may accept other methods or lack middleware; no tests guard any behavior.", "fix": "Show route registration and middleware; add the listed tests and confirm each fails against current code."}
  ]
}
```