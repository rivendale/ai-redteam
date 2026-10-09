# Adversarial Diagnostic Review: `/plan` endpoint (planner.py)

**VERDICT: REWORK.** This is a public, login-free endpoint where every model call is billed to Pedalo, yet it has no cap on loop iterations, input size, request rate, or topic, so any anonymous caller can run up cost without limit.

**CONFIDENCE IN VERDICT: high.** The core defects are visible in 17 lines of code. Confidence is lower on the tool-surface and message-format findings because the `llm` wrapper and the `tools` dict were not supplied.

---

## Pass 1: Reconstruct

The work implements `POST /plan`. It puts the user's question into a message list and calls the model in a loop. Whenever the model asks for a tool, it runs that tool and appends the result, until the model returns an answer. For it to be correct and safe in production, several things must be true:

- The model always reaches a final answer within a reasonable number of turns.
- The `llm` wrapper accepts this message shape: user and tool messages only, with no assistant turn and no tool-call id.
- Every reply contains either `tool` or `answer`.
- `tools` holds only safe, routing-related callables.
- Callers send short, on-topic questions at a modest rate.

Unstated assumptions:

- Someone else adds rate limiting, auth, timeouts and size limits upstream.
- An unscoped model will stay on the topic of bike routes.

None of these is enforced or documented in the work.

---

## Pass 2 / Pass 3: Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | `planner.py` `while True:` loop | Nothing limits model calls per request: no iteration cap, timeout or token budget. | A model that keeps calling tools never exits. This can be prompt-induced ("check the route again for every street in the city") or caused by #3, where the model never sees its own prior call. Each turn is a billed call, the worker stays pinned, and the request never returns. A script repeating it from the public front page turns into a denial-of-wallet attack and exhausts workers. | Cap iterations (for example 5–8) and return a fixed fallback when the cap is hit. Add a per-request wall-clock deadline and a token budget. **Repro:** give `plan()` a stub `llm` that always returns `{"tool": "route", "args": {}}`; it never returns. After the fix it should stop at N calls. | a Y / b Y / c Y (financial harm, outage) / d Y |
| 2 | **High** | CONFIRMED | `plan()` docstring "Anyone may call it; no login"; `request["question"]` | No rate limit, no length limit on `question`, and no per-client quota on a billed public endpoint. | An anonymous client posts a 200k-character question in a loop, and Pedalo pays for every input token. The full history is re-sent on every turn and grows with each tool result, so token cost per request grows roughly quadratically with turn count. | Reject `question` above a small limit (for example 500 characters) and require it to be a non-empty `str`. Add per-IP or per-session rate limits and a global spend circuit breaker. Truncate tool results before appending them. **Repro:** post a 100k-character question and observe it forwarded unmodified to `llm`. | a Y / b Y / c Y / d Y |
| 3 | **High** | PROBABLE | `messages.append({"role": "tool", ...})` | The model's own tool-call turn is never appended. Tool results are added with no tool name or call id, so the conversation is user, then tool, then tool, with no assistant turns. | With mainstream chat APIs, a tool result without a preceding assistant tool call is rejected (error on the second call), or the model cannot link the result to its request. It then calls the tool again and feeds #1. Either the endpoint fails on every tool-using question (the main use case) or it loops. | Append the assistant reply, including tool name, args and id, before the tool result, and include the id or name in the tool message per the wrapper's schema. **Repro:** run one real question that triggers the routing tool against the production `llm` wrapper and inspect the second request payload. Settles once the wrapper is seen. | a Y / b N / c Y (breaks the core request) / d Y |
| 4 | **High** | CONFIRMED (code) / PROBABLE (abuse) | `messages = [{"role": "user", ...}]`, with no system message | The agent has no system prompt and no scoping. The request was a bike trip planner; the work ships a general-purpose chatbot. | A user asks it to write essays, code or homework. It answers, Pedalo pays, and the front-page link becomes a free LLM proxy. Off-brand or harmful output also appears under Pedalo's name. | Add a system prompt restricting the agent to cycling-route planning, with a refusal path. Consider a cheap classifier or pre-check before the agent loop. Cap output tokens. **Repro:** call with "write a 2000-word essay on Napoleon" and observe a full answer. | a Y / b Y / c Y (cost, brand) / d Y |
| 5 | **Medium** | CONFIRMED | `tools[reply["tool"]](**reply.get("args", {}))` | The model, steered by an anonymous user, picks any key in `tools` with arbitrary kwargs, with no allowlist or argument validation. | If `tools` holds anything beyond a read-only route lookup (geocoder with a paid quota, a booking or account tool, an internal HTTP fetch), a user can prompt the model into calling it with attacker-chosen arguments. Severity depends on contents (see NV-1). | Use an explicit allowlist of the routing tool(s) for this endpoint. Validate args against a schema (types, coordinate ranges, string lengths). Do not pass the app's global tool registry. **Repro:** stub `tools` with a second sensitive function and an `llm` stub that requests it; it executes. | a Y / b Y / c N (until contents known) / d N |
| 6 | **Medium** | PROBABLE | `result = f"error: {exc}"` | Raw exception text is fed to the model, which may repeat it to the anonymous user. | An upstream routing API fails with a message containing an internal URL, query string with API key, or stack detail. The model says "the service returned error: …" and leaks it. | Log the exception server-side and give the model a generic message ("routing unavailable, try again"). **Repro:** a tool stub raising `Exception("https://internal/route?key=SECRET")`; the string reaches `messages`, and from there the user. | a Y / b N / c Y / d N |
| 7 | **Medium** | CONFIRMED | `return {"answer": reply["answer"]}`, `request["question"]` | KeyError on any reply that has neither a tool nor an answer, or on a request missing `question`. The resulting 500s are uncontrolled. | The model returns an empty or refusal-shaped reply, or a content-filter result, or a client omits `question`. The endpoint errors with an unhandled exception, after already paying for the calls. | Validate the request and return a 400. Handle a missing `answer` with a fallback message. **Repro:** an `llm` stub returning `{}` raises KeyError. | a Y / b Y / c N / d Y |
| 8 | **Low** | CONFIRMED | whole file | No timeouts around `llm(...)` or tool calls, and no logging or metrics of turns, tokens or cost per request. | A slow upstream hangs a worker indefinitely, and a cost spike from #1, #2 or #4 is invisible until the invoice. | Add timeouts and log per-request turns, tokens and tool calls, with alerting on spend. | a Y / b Y / c N / d N |

**Strongest-defender re-examination**

- **#1:** "The model will stop on its own." Nothing in the code enforces that, and #3 makes repeated calls likely. Survives.
- **#2:** "Rate limiting lives at the gateway." No evidence of that was supplied, and the work's own docstring declares the endpoint open. Survives; downgrade if NV-2 shows a gateway limit.
- **#3:** "The `llm` wrapper may handle history itself." That is possible, which is why it is PROBABLE; it stays High because the wrapper as called is stateless (it receives `messages`).
- **#4:** "Scope is a prompt detail." The request was a bike planner and the context says Pedalo pays per call. An unscoped agent is drift. Survives.

**Sibling search (root cause: unbounded consumption on a billed public path).** I searched every input and growth point in the file:

- `question` size: unbounded (#2).
- Loop count: unbounded (#1).
- Tool result size appended to history: unbounded (`json.dumps(result)` with no truncation, folded into #2).
- Output length: no cap (#4).
- Request rate: none (#2).

No other growth points exist in the file.

**Security boundary (#1, #2, #4).**

- **Principal:** an anonymous internet user.
- **Input:** the `question` body of `POST /plan`, plus request frequency.
- **Failing control:** none present (no auth, quota, iteration cap, size limit or scoping).
- **Boundary crossed:** the public internet reaching Pedalo's billed model API account.
- **Resource:** Pedalo's model spend and server workers.

**Most serious thing I might still miss:** what is in `tools` and what the `llm` wrapper does with the messages. If `tools` is a shared registry with write or account actions, #5 becomes Critical. That risk would hide in the caller that wires `plan()` into the web framework, which was not supplied.

---

## COVERAGE

- `request.md`: checked
- `context.md`: checked
- `planner.py`: checked (every line)
- Route wiring, `llm` wrapper, `tools` registry, tests, deployment and gateway config: not checked, not supplied

## NEEDS VALIDATION

- **NV-1:** What callables are in `tools` when `/plan` is served? Settles #5's severity.
- **NV-2:** Is there an upstream gateway enforcing rate limits, body size limits or auth on `/plan`? Settles #2's severity.
- **NV-3:** What message schema does the `llm` wrapper expect for tool calls and results? Settles #3.
- **NV-4:** The request requires a "routing tool". No routing tool is in the work, so it cannot be confirmed that one exists or works.

## REFUTED

- **Unknown tool name crashes the endpoint.** It does not: the `KeyError` from `tools[...]` is raised inside the `try` and becomes an `error:` result.
- **Non-dict `args` crashes the endpoint.** It does not: the `TypeError` is also caught inside the `try`.
- **`json.dumps` fails on non-serialisable tool results.** It does not: `default=str` handles them.

## WHAT HOLDS UP

- Tool exceptions are contained and do not crash the request.
- Results are serialised safely.
- The control flow is simple and easy to harden.

## UNVERIFIED CLAIMS

- "Anyone may call it; no login." This is a stated design choice. Confirm it is intended given billing, and that compensating controls exist (NV-2).
- No tests were supplied, so there is no claim of testing to verify. Coverage of all paths is UNVERIFIED.

## QUESTIONS FOR THE AUTHOR

1. What exactly is passed as `tools` in production?
2. Is there gateway-level rate limiting, auth or a body size limit in front of `/plan`?
3. Does the `llm` wrapper require assistant tool-call turns and ids in `messages`?

## DECISION-MAKER SUMMARY

Do not launch: an anonymous user can make a single request loop on billed model calls without limit, and the endpoint works as a free general-purpose chatbot on Pedalo's account. Add an iteration cap, input and output size limits, rate limiting, a system prompt scoping it to bike routes, and a tool allowlist, then run one real routing question end to end. Launching as is risks an uncapped model bill and outage from a single script.

## OWNER SUMMARY

The new trip-planner page lets anyone on the internet use the AI as much as they want, about anything, and the company pays for every use with no ceiling. In some cases a single question could make it keep working forever, running up cost and tying up the server. It needs limits and a narrow focus on bike routes before it goes live on the app's front page.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "planner.py", "status": "seen", "matters": true},
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "tools registry", "status": "not_seen", "matters": true},
    {"item": "gateway/deploy config", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "planner.py:plan", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "llm wrapper", "reason": "not_supplied"},
      {"unit": "tools registry / routing tool", "reason": "not_supplied"},
      {"unit": "gateway, rate limit, deploy config", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py plan(): while True loop",
     "scenario": "Model keeps requesting tools (prompt-induced or via F3); loop never exits; unbounded billed llm calls and a pinned worker; repeatable by any anonymous caller.",
     "fix": "Cap iterations (e.g. 5-8) with fallback answer; per-request deadline and token budget.",
     "reproduction": "Stub llm always returning {'tool':'route','args':{}}; plan() never returns.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": true,
     "siblings_searched": {"searched": "all growth points in planner.py: loop count, question size, tool result size, output length, request rate", "found": "question size, tool result size, request rate unbounded (F2); output/topic unbounded (F4)"},
     "boundary": {"principal": "anonymous internet user", "input": "POST /plan question body and request frequency", "control": "none: no iteration cap, auth, quota", "crossed": "public internet to Pedalo's billed model API", "resource": "model spend and server workers"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py plan(): request['question'], docstring 'Anyone may call it; no login'",
     "scenario": "Anonymous client posts very large questions repeatedly; every token billed; history resent each turn so cost grows with turns.",
     "fix": "Validate question as non-empty str under a small length limit; per-client rate limits; spend circuit breaker; truncate tool results.",
     "reproduction": "POST a 100k-char question; it is forwarded unmodified to llm.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": true,
     "siblings_searched": {"searched": "same as F1", "found": "same root cause as F1 and F4"},
     "boundary": {"principal": "anonymous internet user", "input": "question body size and request rate", "control": "none: no size limit or rate limit", "crossed": "public internet to billed model API", "resource": "model spend"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py plan(): messages.append({'role':'tool',...})",
     "scenario": "Assistant tool-call turn and call id never appended; real chat APIs reject an orphan tool result or the model cannot see its own prior call and re-calls the tool, so routing questions fail or loop.",
     "fix": "Append the assistant reply (tool, args, id) before the tool result; include id/name per the wrapper schema.",
     "reproduction": "Run one routing question against the production llm wrapper and inspect the second request payload.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all message construction in planner.py", "found": "only the initial user message and tool results are ever appended; no assistant turn anywhere"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "A",
     "location": "planner.py plan(): messages initialised with user message only, no system prompt",
     "scenario": "Users get essays, code and other off-topic output on Pedalo's bill and under its brand; requested scope was bike routing.",
     "fix": "System prompt limiting the agent to cycling-route planning with a refusal path; optional pre-classifier; max output tokens.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": true,
     "siblings_searched": {"searched": "same as F1", "found": "same root cause as F1 and F2"},
     "boundary": {"principal": "anonymous internet user", "input": "off-topic question text", "control": "none: no scoping or system prompt", "crossed": "public internet to billed general-purpose model use", "resource": "model spend and brand"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py plan(): tools[reply['tool']](**reply.get('args', {}))",
     "scenario": "Prompted model invokes any callable in tools with attacker-chosen args; impact depends on tools contents.",
     "fix": "Explicit allowlist of routing tools; schema-validate args.",
     "reproduction": "Stub tools with a second sensitive function and an llm stub requesting it; it executes.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py plan(): result = f'error: {exc}'",
     "scenario": "Exception text with internal URLs or keys is fed to the model and echoed to the anonymous user.",
     "fix": "Log the exception server-side; pass a generic error to the model.",
     "reproduction": "Tool stub raising Exception('https://internal/route?key=SECRET'); the string appears in messages.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py plan(): reply['answer'], request['question']",
     "scenario": "A reply with no tool and no answer, or a request with no question, raises KeyError and returns 500 after billed calls.",
     "fix": "Validate the request and return 400; fall back when answer is missing.",
     "reproduction": "llm stub returning {} raises KeyError.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py: whole file",
     "scenario": "No timeouts on llm or tool calls, and no per-request cost logging; hangs and spend spikes go unnoticed.",
     "fix": "Add timeouts; log turns, tokens and tool calls; alert on spend.",
     "reproduction": "Tool stub that sleeps indefinitely; plan() hangs with no log output.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "NV-1", "status": "needs_validation", "location": "tools argument", "suspicion": "tools may contain non-routing or side-effecting callables", "unresolved_fact": "Exact contents of tools when /plan is served"},
    {"id": "NV-2", "status": "needs_validation", "location": "deployment", "suspicion": "no upstream rate limit, auth or body size limit", "unresolved_fact": "Gateway config for /plan"},
    {"id": "NV-3", "status": "needs_validation", "location": "llm wrapper", "suspicion": "message shape incompatible with the tool-call protocol", "unresolved_fact": "Schema the wrapper expects for tool calls and results"},
    {"id": "NV-4", "status": "needs_validation", "location": "routing tool", "suspicion": "required routing tool not shown", "unresolved_fact": "Existence and behaviour of the routing tool"}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Unknown tool name crashes the endpoint", "evidence": "KeyError from tools[...] is raised inside the try block and becomes an error result"},
    {"id": "R2", "candidate": "Non-dict args crash the endpoint", "evidence": "TypeError is raised inside the try block"},
    {"id": "R3", "candidate": "json.dumps fails on non-serialisable tool results", "evidence": "default=str is set"}
  ]
}
```