VERDICT: REWORK. On a public, no-login endpoint where every model call is billed, the agent loop has no iteration cap, no scope restriction and no input limits, so one anonymous caller can run up unbounded cost.

CONFIDENCE: medium. The work was not written in this conversation, so there is no shared-author anchoring. But I had no tools: nothing was run, and the `llm` wrapper, `tools` dict, routing tool, HTTP layer and any gateway were not supplied.

INPUTS LEDGER:
- **Seen:** the original request (request.md), the context (context.md) and `planner.py` (17 lines).
- **Not seen:**
  - The `llm` callable and its message contract. This matters for F4.
  - The contents of the `tools` dict and the routing tool. This matters for S1.
  - Any gateway rate limit, auth or body-size limit in front of `/plan`. This matters for F3. It does not change F1, because one request alone is unbounded.
  - Any tests. None were supplied, so test coverage is zero as far as I can see.

COVERAGE:
- **Checked:** `planner.py` in full, including `plan()` and every line of the loop, tool dispatch, error handling and return.
- **Not checked:** the llm wrapper, the tools, the routing tool's argument handling, the HTTP framework and the deployment config. None were supplied.

SEATS AND GATE:
- **Sensitivity gate:** passed. The work holds no personal data, credentials or client material.
- **Seats:** only the local reviewer ran. No subagent or cross-vendor seat was available because this session has no tools.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | planner.py:8-16 | `while True` has no iteration cap, token budget or wall-clock limit. Every turn is a billed `llm` call. | Conditions: an anonymous caller asks a question that makes the model keep calling tools ("check every route between all 200 docks, one call each"), or a tool keeps erroring. Then the request loops indefinitely and each turn is billed to Pedalo. A few such requests in parallel give an attacker cost exhaustion (denial-of-wallet) and tie up workers. | Cap turns (e.g. `for _ in range(MAX_STEPS)`), add a per-request token and time budget, and return a fixed fallback when the cap is hit. Repro: `llm=lambda m: {"tool": "route", "args": {}}` with `tools={"route": lambda: "x"}`. Expected: return after N steps. Observed: never returns. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | B/D | planner.py:7 | There is no system prompt or scope restriction. The user's text is the whole conversation. | Conditions: anyone sends a non-bike request ("write my 3,000-word essay", "translate this book"). Then the endpoint acts as a free general-purpose LLM proxy billed to Pedalo, and its answers show up under the Pedalo brand. The request was specifically "how do I get from A to B by bike". | Add a system message that limits the model to bike trip planning and tells it to refuse anything else. Consider a cheap classifier or refusal check before the agent runs. Repro: question="Write a sonnet about cats". Expected: a refusal. Observed: whatever the model produces, billed. | a✓ b✓ c✓ d✓ |
| F3 | High | CONFIRMED | B | planner.py:6-7 | `question` is unvalidated. There is no type check, length cap, rate limit or abuse control, and the docstring says "Anyone may call it; no login". | Conditions: a caller posts a 1 MB `question`, or scripts thousands of requests. Then every token is billed on every loop turn, because the full history is resent each time, compounding F1. If `question` is missing, `KeyError` causes a 500. | Require a string `question` of at most ~500 characters. Add per-IP or per-session rate limiting and a daily spend ceiling with an alert. Repro: POST `{}`, expect 400, observe a 500. POST a 1 MB question, expect 413/400, observe a billed call. | a✓ b✓ c✓ d✓ |
| F4 | Medium | PROBABLE | B | planner.py:9-15 | The assistant's tool-call turn is never appended to `messages`. Only a `{"role":"tool"}` message with no tool-call id is added. | Conditions: `llm` wraps a standard chat API (Anthropic or OpenAI style). Then either the API rejects a tool result that has no preceding tool call (every multi-step plan fails), or the model cannot see which call it made and repeats the same call, which feeds F1. | Append `reply`, the assistant tool-call message, before the tool result, and carry the call id. Repro: a two-step fake llm that asserts the history contains its prior call. Expected: pass. Observed: the call is missing. | a✓ b✗ c✓ d✓ |
| F5 | Medium | CONFIRMED | B | planner.py:12, 17 | The model's reply shape is trusted. If a reply has neither `tool` nor `answer`, `reply["answer"]` raises `KeyError`. `reply["args"]` is splatted with `**`, so a non-dict raises outside the intended path. | Conditions: the model returns malformed output, a refusal, or an empty or filtered response. Then the rider gets an unhandled 500 instead of a message. | Validate the reply shape and return a friendly fallback. Repro: `llm=lambda m: {}`. Expected: a fallback answer. Observed: `KeyError`. | a✓ b✓ c✗ d✓ |
| F6 | Medium | PROBABLE | B | planner.py:13-14 | Raw exception text, `f"error: {exc}"`, goes to the model, which can repeat it in the public answer. | Conditions: the routing tool throws an exception whose message includes an internal URL, host, key-bearing query string or stack detail. Then the model may quote it to an anonymous user. | Log the exception server-side. Give the model a generic "routing unavailable" message. Repro: a tool that raises `Exception("GET https://int-router:8080/?key=SECRET failed")`, then inspect the messages sent to the llm. | a✓ b✗ c✓ d✗ |
| F7 | Medium | CONFIRMED | B | planner.py:9, 12 | There are no timeouts on the `llm` or tool calls, and no logging or metrics (turns, tokens, cost per request). | Conditions: the model provider or router hangs. Then front-page traffic piles up blocked workers, and nobody can see the spend from F1–F3 until the invoice arrives. | Add per-call timeouts. Log the turn count, tokens and latency per request. Alert on spend. | a✓ b✓ c✗ d✓ |

## Needs validation, refuted and verification gaps

NEEDS VALIDATION:
- **S1:** `tools[reply["tool"]](**args)` lets model-chosen names and arguments, which a user can steer through the question, reach any function in `tools`. This is safe only if `tools` holds nothing but the routing tool and that tool validates its arguments (coordinate bounds, no URL or file parameters). The fact that settles it is what `tools` contains in production and how the routing tool handles hostile arguments.
- **S2:** a gateway rate limit or auth layer may exist in front of `/plan`. This would reduce F3 but not F1. The fact that settles it is the deployment config.

REFUTED:
- **"An unknown tool name crashes the request."** `tools[reply["tool"]]` sits inside the `try` at line 11, so the `KeyError` is caught and returned to the model as an error string.
- **"No login is itself a defect."** A public trip planner on a rider site plausibly should be anonymous. The real defect is the missing cost and abuse controls (F1–F3), not the missing login.

WHAT HOLDS UP:
- The basic agent shape (call the model, dispatch a tool, feed the result back, return the answer) matches the request.
- Tool exceptions are caught rather than crashing the request.
- `json.dumps(..., default=str)` will not crash on non-serializable tool results.

UNVERIFIED CLAIMS:
- That the code works end to end against the real `llm` and routing tool. No tests were supplied and nothing was run. To confirm, add fake-llm unit tests for:
  - a single tool step;
  - a multi-step plan;
  - a looping model;
  - malformed replies;
  - a missing `question`.
- Each test must be confirmed to fail on the current code before the fix.

QUESTIONS FOR THE AUTHOR:
1. What message format does `llm` expect for tool calls and results? (Settles F4.)
2. What is in `tools` in production? (Settles S1.)
3. Is there a gateway rate limit or spend cap in front of `/plan`? (Changes F3's severity, not F1's.)

DECISION-MAKER SUMMARY: Do not launch until the loop is capped (F1), the model is limited to bike routing (F2), and input size and request rate are limited (F3). Each of these is small to fix. If you proceed anyway, any anonymous user can drive unbounded, Pedalo-billed model spend from a link on the app's front page.

OWNER SUMMARY: The trip planner works in principle, but nothing stops it from running, and charging us, indefinitely on a single request. Anyone on the internet can also use it as a free general-purpose AI service at our expense. It needs a few small safety limits and some basic tests before it goes on the front page.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "planner.py", "status": "seen", "matters": true},
    {"item": "llm callable / message contract", "status": "not_seen", "matters": true},
    {"item": "tools dict and routing tool", "status": "not_seen", "matters": true},
    {"item": "gateway / rate-limit / deployment config", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "planner.py", "kind": "file"},
      {"unit": "planner.py:plan", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "llm wrapper", "reason": "not supplied"},
      {"unit": "tools / routing tool", "reason": "not supplied"},
      {"unit": "deployment and gateway config", "reason": "not supplied"},
      {"unit": "runtime behaviour", "reason": "no tools in session; nothing executed"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:8-16",
     "scenario": "An anonymous caller induces repeated tool calls; while True has no step, token or time cap, so the request loops indefinitely and every turn is billed to Pedalo (denial-of-wallet).",
     "fix": "Cap turns (MAX_STEPS), add per-request token and time budgets, and return a fixed fallback when exceeded.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "plan({'question':'x'}, llm=lambda m: {'tool':'route','args':{}}, tools={'route': lambda: 'x'}); expected return after N steps, observed no return."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "D",
     "location": "planner.py:7",
     "scenario": "There is no system prompt, so any off-topic request (essays, translation) is answered as a free general LLM proxy billed to Pedalo, outside the bike-routing scope requested.",
     "fix": "Add a system message restricting the model to bike trip planning with refusal of other requests; optionally pre-classify.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "question='Write a sonnet about cats'; expected refusal, observed a billed off-topic answer."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:6-7",
     "scenario": "Unvalidated, unbounded question on an unauthenticated endpoint: a 1 MB question or scripted flood is billed per token per turn; a missing question raises KeyError and returns a 500.",
     "fix": "Require a string question of at most ~500 chars, rate-limit per IP or session, and set a daily spend cap with an alert.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "POST {} expecting 400, observe 500; POST a 1 MB question expecting 413, observe a billed call."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:9-15",
     "scenario": "The assistant tool-call turn is never appended; with a standard chat API the orphan tool result is rejected, or the model re-issues the same call, feeding F1.",
     "fix": "Append the assistant tool-call message (with call id) before the tool result.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Two-step fake llm asserting its prior tool call is present in messages; observed missing."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:12,17",
     "scenario": "The model returns a reply with neither tool nor answer (refusal, filter, malformed); reply['answer'] raises KeyError and the rider gets a 500.",
     "fix": "Validate the reply shape and return a friendly fallback.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "llm=lambda m: {}; expected fallback, observed KeyError."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:13-14",
     "scenario": "Raw exception text containing internal URLs or keys is sent to the model, which may repeat it to an anonymous user.",
     "fix": "Log exceptions server-side; give the model a generic error string.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "A tool raising Exception('GET https://int-router/?key=SECRET'); inspect messages sent to llm."},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:9,12",
     "scenario": "No timeouts and no logging or metrics: a hung provider blocks workers under front-page traffic, and runaway spend is invisible until invoiced.",
     "fix": "Add per-call timeouts; log turns, tokens and latency per request; alert on spend.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "llm that sleeps 600s; expected timeout error, observed blocked request."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "planner.py:12",
     "suspicion": "User-steerable model can call any function in tools with arbitrary args.",
     "unresolved_fact": "Contents of tools in production and whether the routing tool validates its arguments."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "planner.py:6",
     "suspicion": "A gateway rate limit or auth may already mitigate F3.",
     "unresolved_fact": "Deployment and gateway config for /plan."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "An unknown tool name crashes the request.",
     "evidence": "tools[reply['tool']] is inside the try at line 11; the KeyError is caught and returned as an error string."},
    {"id": "C2", "candidate": "No login is itself a defect.",
     "evidence": "A public trip planner is plausibly meant to be anonymous; the defect is the missing cost and abuse controls (F1-F3)."}
  ]
}
```