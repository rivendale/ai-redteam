# Adversarial Diagnostic Review: `planner.py` (`POST /plan`)

## Pass 1: Reconstruct

The work is a public, unauthenticated `POST /plan` handler. It passes the caller's `question` to a model, runs whatever tool the model names with whatever arguments it supplies, feeds the result back, and loops until the model returns an `answer`. For this to be correct and safe in production:

- The model must eventually stop calling tools.
- The `llm` wrapper must understand a bare `{"role":"tool"}` message with no record of the call that produced it.
- `tools` must contain only safe, routing-related callables.
- Callers must send well-formed, reasonably sized, on-topic questions.
- Something outside this file (gateway, WAF, quota) must limit how much an anonymous caller can spend.

None of these is enforced in the code shown. The last one is unstated and carries the most weight, because the context says every model call is billed to Pedalo and the endpoint is linked from the app's front page.

## Pass 2: Attack (Track B, with Track A on scope)

**Loop and cost.**
- `while True:` (lines 8–17) has no iteration cap, token budget, or wall-clock timeout.
- When the model calls a tool, the code appends only the tool result (line 15). The assistant's own tool-call turn is never appended. On the next call the model sees a user question followed by an unexplained tool result, with no link to any call it made.
- Many chat APIs reject that sequence; others make the model call again. With a validation-error result or a flaky routing backend, the model can keep retrying.
- Each iteration is a billed call, so one request can mean unbounded spend, and many anonymous requests multiply it.

**Missing protections on a public endpoint.**
- There is no auth (by design, per the docstring), no rate limit, no input size limit, and no system prompt restricting scope.
- Anyone can use it as a free general-purpose LLM proxy on Pedalo's bill, for example by asking it to write an essay. Nothing ties it to bike routing.

**Tool dispatch.**
- `tools[reply["tool"]](**reply.get("args", {}))` executes any key in `tools` with model-chosen kwargs.
- The model's choices are steered by attacker-controlled text, so this is prompt-injection to arbitrary tool invocation. The blast radius depends on what `tools` holds, which is not shown.
- `args` is not checked to be a dict. A list or string makes `**` raise a TypeError, which is caught and the loop continues.

**Error handling.**
- `except Exception` sends `str(exc)` to the model (lines 13–14). Exception text from an HTTP client or database typically includes internal URLs, hostnames, sometimes credentials in connection strings. The user can ask the model to repeat it, so it leaks out.
- Errors outside the `try` are not handled:
  - `request["question"]` (line 7) raises KeyError on a missing field.
  - `reply["answer"]` (line 17) raises KeyError if the model returns neither a tool nor an answer.
  - `llm` errors propagate raw.
- Each of these becomes a 500 with possible stack trace exposure, depending on the framework.

**Hostile inputs traced.**

| Input | What happens |
|---|---|
| Empty body or missing `question` | KeyError, 500 |
| `question` is a non-string or dict | Passed straight into `content`; behavior depends on `llm` (UNVERIFIED) |
| 1 MB question | Forwarded in full and billed on every loop iteration, since `messages` is resent each time |
| Unknown tool name | KeyError caught, `"error: 'x'"` fed back, loop continues |

**Tests.** None are present. There is nothing to mutate, so per rule 5 coverage is zero, not "unverified".

**Hallucination check.** `json.dumps(..., default=str)` is real and correct. The message schema (`role: "tool"` without `tool_call_id` or a preceding assistant turn) is only valid if the injected `llm` adapter tolerates it. This is UNVERIFIED and depends on the adapter. It is non-compliant for the OpenAI and Anthropic native formats.

**Requirement fit.** "A model agent with a routing tool" became "any tools dict". No routing tool is defined or constrained here. The core loop does otherwise match the request.

**Operations.**
- There is no logging of iterations, tokens, or cost per request, so a runaway spend would not be visible until the bill arrives.
- There are no timeouts on `llm` or tool calls, so slow upstreams hold workers indefinitely. At 10x front-page traffic this exhausts the worker pool.

## Pass 3: Self-check

- I downgraded "model loops forever" from CONFIRMED to PROBABLE. The unbounded loop is confirmed in the code, but whether a given model actually re-calls depends on the adapter.
- The arbitrary-tool finding is rated by worst plausible contents of `tools`. It is PROBABLE for this design and would become Critical if `tools` holds anything with side effects.
- The most serious thing I might be missing is in the parts not shown: the `llm` adapter and the routing tool's own handling of model-supplied coordinates (SSRF if it fetches URLs, injection if it builds queries). That is where I would look next.

---

**VERDICT: REWORK.** An anonymous, unbounded, billed agent loop linked from the front page is a direct cost-abuse and availability risk, and the message-history bug makes runaway loops likely even for honest users.

**CONFIDENCE IN VERDICT: high.** The core defects are visible in the 17 lines. It is limited by not seeing the `llm` adapter, the `tools` contents, or any gateway-level rate limiting.

### Findings, ordered by severity

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `planner.py:8` `while True:` | No iteration cap, token budget, or timeout on a billed loop | Model keeps calling a failing tool, or a crafted prompt induces repeated calls. One request burns unbounded paid model calls and holds a worker. | Cap iterations (e.g. 5) and total tokens. Add an overall deadline. Return a fixed fallback when exceeded. Test: stub `llm` that always returns a tool call and assert termination within N calls. |
| 2 | Critical | CONFIRMED (code) / UNVERIFIED (gateway) | `planner.py:6` docstring "Anyone may call it; no login" | Public, unauthenticated endpoint that spends Pedalo money per call, with no rate limit or quota shown | Scripted traffic, or front-page traffic spikes, drive model spend and exhaust capacity (cost DoS) | Per-IP and per-device rate limits, a global daily spend cap with a circuit breaker, bot protection or app attestation. Confirm what the gateway actually enforces. |
| 3 | High | CONFIRMED | `planner.py:7` | No system prompt or scope restriction; raw user text is the only message | Endpoint used as a free general-purpose chatbot, or to produce off-brand or harmful content under Pedalo's name | Add a system prompt restricting to bike-route planning, cap question length (e.g. 500 chars), refuse off-topic requests, apply output moderation |
| 4 | High | PROBABLE | `planner.py:12` `tools[reply["tool"]](**reply.get("args", {}))` | Model, steered by untrusted input, can invoke any tool in `tools` with arbitrary kwargs | Prompt injection makes the model call a non-routing or side-effecting tool, or the routing tool with hostile args | Allowlist exactly the routing tool. Validate `args` against a schema (types, coordinate bounds) before calling. |
| 5 | High | PROBABLE (depends on adapter) | `planner.py:15` | Assistant tool-call turn is never appended; tool result has no `tool_call_id` | Provider API rejects the history (500 on every tool use), or the model never sees its call and re-calls, feeding finding 1 | Append the assistant tool-call message, then the tool result linked by ID, in the provider's format. Test with the real adapter on a two-step trace. |
| 6 | Medium | CONFIRMED | `planner.py:13-14` | Raw exception text is sent to the model and can be echoed to the user | Routing backend error containing an internal URL or connection string is relayed to the user ("what was the error?") | Log the full exception server-side. Send the model a generic `"routing unavailable"`. |
| 7 | Medium | CONFIRMED | `planner.py:7`, `:17` | Missing `question` or missing `answer` raise uncaught KeyError | Malformed request or odd model reply produces a 500, possibly with a trace | Validate the request body (400 on bad input). Handle a reply with neither tool nor answer explicitly. |
| 8 | Medium | CONFIRMED | `planner.py:9`, `:12` | No timeouts on `llm` or tool calls | Slow upstream ties up workers; front-page traffic exhausts the pool | Per-call timeouts plus an overall request deadline |
| 9 | Medium | CONFIRMED | whole file | No tests | Every defect above ships undetected; a regression in the loop cap would go unnoticed | Tests: loop-cap termination, unknown tool, bad args, missing fields, error message not leaked, off-topic refusal |
| 10 | Low | CONFIRMED | whole file | No logging of iterations, tokens, or cost per request | Runaway spend only discovered on the bill | Emit per-request iteration count and token usage. Alert on spend rate. |

### What holds up

- The basic agent loop shape (call, dispatch tool, feed result, return answer) is correct in outline.
- `json.dumps(result, default=str)` safely serializes non-JSON tool results.
- Catching tool exceptions instead of crashing the request is the right instinct; only what gets forwarded is wrong.

### Unverified claims

- **Whether the `llm` adapter accepts the message format used.** Run one real tool-call round trip against the production adapter.
- **Whether gateway or WAF rate limiting exists for `/plan`.** Check the deployed config, not docs.
- **What `tools` contains in production.** Inspect the wiring at the call site.
- **How the routing tool handles model-supplied args** (SSRF, injection). Review its code.
- **How the framework renders uncaught exceptions to callers.** Send a malformed body to staging.

### Questions for the author

1. What enforces rate limits and a spend ceiling for `/plan` today, and where is it configured?
2. What exactly is passed as `tools` in production, and does it ever hold more than the routing tool?
3. Has a real tool-call round trip run against the production `llm` adapter, and with what result?

### Decision-maker summary

Do not launch until the loop is capped, the endpoint is rate-limited with a global spend cap, and the tool-call history bug is fixed. Proceeding as is lets anyone on the internet run Pedalo-billed model calls without limit, and some honest requests may loop or fail. Remaining risk after the fixes sits in the unseen routing tool and model adapter, which need their own review.

### Owner summary

The trip-planner page works in principle, but as built anyone can use it without limits and every use costs the company money, with no ceiling on how much a single request can spend. It can also be used for things that have nothing to do with bike routes, and some internal error details could reach the public. It needs usage limits, a spending cap and a few safety fixes before it goes on the app's front page.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "planner.py:8 `while True:`", "scenario": "Model repeatedly calls a failing tool or is prompted to loop; one request triggers unbounded billed model calls and holds a worker indefinitely.", "fix": "Cap iterations and tokens, add an overall deadline, return a fallback; test with a stub llm that always returns a tool call."},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "planner.py:6 docstring 'Anyone may call it; no login'", "scenario": "Anonymous scripted traffic or front-page spikes drive unlimited Pedalo-billed model spend and exhaust capacity.", "fix": "Per-client rate limits, global daily spend cap with circuit breaker, bot protection; verify gateway config."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "planner.py:7 messages built from raw question only", "scenario": "Endpoint used as a free general-purpose LLM or to generate off-brand content under Pedalo's name.", "fix": "System prompt restricting to bike routing, question length cap, off-topic refusal, output moderation."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "planner.py:12 tools[reply['tool']](**reply.get('args', {}))", "scenario": "Prompt injection steers the model to call any tool in the dict with arbitrary kwargs.", "fix": "Allowlist only the routing tool; validate args against a schema before invocation."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "planner.py:15 messages.append tool result only", "scenario": "Assistant tool-call turn is missing and the result has no tool_call_id; the provider rejects the history or the model re-calls, feeding the unbounded loop.", "fix": "Append the assistant tool-call message and an ID-linked tool result in the provider's format; test a real round trip."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py:13-14 result = f'error: {exc}'", "scenario": "Internal URLs or connection details in exception text are relayed to the model and echoed to the public user.", "fix": "Log exceptions server-side; send the model a generic error string."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py:7 request['question'], planner.py:17 reply['answer']", "scenario": "Missing field in the request or model reply raises an uncaught KeyError, returning a 500 that may expose a trace.", "fix": "Validate input (400 on bad body); handle a reply with neither tool nor answer explicitly."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py:9 llm(messages), planner.py:12 tool call", "scenario": "A slow model or routing upstream blocks workers with no timeout; front-page load exhausts the pool.", "fix": "Per-call timeouts and an overall request deadline."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "planner.py (entire file)", "scenario": "No tests exist, so the loop, error-leak and validation defects ship undetected.", "fix": "Add tests for loop cap, unknown tool, bad args, missing fields, error non-leakage, off-topic refusal."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "planner.py (entire file)", "scenario": "No per-request logging of iterations or tokens; runaway spend is discovered only on the bill.", "fix": "Emit iteration and token metrics per request and alert on spend rate."}
  ]
}
```