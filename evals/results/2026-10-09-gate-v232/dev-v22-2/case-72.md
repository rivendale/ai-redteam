**Review conditions:** I reviewed this with no tools in this session. I could not run the code, and no fresh subagent or second reviewer ran. I did not write this code earlier in the conversation, so anchoring risk is lower, but nothing below was executed. Each CONFIRMED label means I traced the quoted lines by hand.

VERDICT: **REWORK**. Anyone on the internet can make one request run model calls forever, each billed per token with growing context, and nothing in the code limits it.
CONFIDENCE: **medium**. I checked the code by hand only. The `llm` wrapper, the `tools` registry, the HTTP framework or gateway, and the tests were not supplied.

INPUTS LEDGER:
- Seen: the original request (request.md), the context (context.md), and agent.py.
- Not seen: the `llm` callable's contract, which **matters** for F3 and F4. The `tools` dict contents, which **matters** for side effects and data exposure (S1). Any gateway, rate limiter or WAF in front of `/ask`, which **matters** for F2. Tests, which matter because nothing is shown to be tested.

COVERAGE:
- Checked: `agent.py:run_agent` and `agent.py:ask_endpoint`. Assumptions checked: the loop terminates, the endpoint is protected upstream, and the model sees its own tool calls.
- Not checked: tool implementations, the llm wrapper, deployment config and tests (none supplied).

SEATS AND GATE: one same-session reviewer, no tools. No cross-vendor seats ran because none were requested and none were available. Sensitivity gate passed: the work is code only, with no personal data or secrets.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | agent.py:8-17 (`while True`, `continue`; docstring "Retry forever on a tool error") | The loop has no step cap, no token or cost budget, and no wall-clock timeout. The only exit is a reply with no tool. `messages` grows on every turn, so each call costs more than the last. Tool output is appended untruncated. | An anonymous caller asks "call search repeatedly until you find X" for something that does not exist. Or the model keeps calling a tool that keeps erroring. Each iteration is a billed model call over an ever-longer context. A few parallel requests run up an unbounded bill (denial of wallet) and tie up workers. | Add `max_steps` (e.g. 8), a per-request token or cost budget, and an overall deadline. When any limit is hit, return a fixed "could not answer" response. Truncate each tool result (e.g. 4–8 KB). Repro: stub `llm` to always return `{"tool": "t", "args": {}}`. Expect termination after N steps; today it never returns. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | B | agent.py:21-23 (`no login; anyone on the internet may call it`) | No rate limit, per-caller quota or input-size limit exists in the code, and none was shown upstream. Leaving out login fits the request ("public"). Leaving out abuse limits is the gap. | A script sends thousands of requests with 100 KB questions. Each request costs input tokens times the step count (worse with F1), and the bill accrues to the account. | Add per-IP or per-key rate limiting, a global spend ceiling or circuit breaker, and a max `question` length. Reject an empty or missing `question` with a 400. Repro: send 50 concurrent requests with a 200 KB question. Expect 429/413; today all are accepted. | a✓ b✗ c✓ d✓ |
| F3 | High | PROBABLE | B | agent.py:10-15 (only `{"role": "tool", ...}` is appended) | The model's own tool-call turn is never added to `messages`. The model sees tool results with no record of what it called or with what args. Many chat APIs also reject a tool message that has no preceding assistant tool call. | After one tool call, the model cannot tell which call produced the result. It re-issues the same call repeatedly, which feeds F1. Or, with a strict API, the second `llm()` call raises, and every tool-using question returns a 500, which breaks "uses tools until it can answer". | Append the assistant turn (`{"role": "assistant", "tool": ..., "args": ...}`, or the API's native tool_call shape with an id) before the tool result, and link the result to the call id. Repro: stub `llm` to assert that the message before a tool result is the matching assistant call. Today the assertion fails. | a✓ b✗ c✓ d✓ |
| F4 | Medium | CONFIRMED | B | agent.py:17 (`return reply["answer"]`) | A reply with neither `tool` nor `answer` raises an uncaught KeyError. This includes a refusal, a text reply under a different key, or `"tool": ""`. | The model returns `{"content": "I can't help with that"}`. The endpoint returns an unhandled 500, possibly with a traceback, depending on the framework. | Handle the third case explicitly, for example `reply.get("answer")`, falling back to a safe message and logging the malformed reply. Repro: stub `llm` to return `{}`. Expect a graceful answer; observe KeyError. | a✓ b✓ c✗ d✓ |
| F5 | Medium | PROBABLE | B | agent.py:13-14 (`result = f"error: {exc}"`) | Raw exception text goes into the model context, and the model can repeat it in the public answer. Driver and HTTP exceptions often include internal hostnames, paths, query text or credentials in URLs. | A caller asks "run the lookup tool with an invalid id and quote the exact error". The answer contains an internal DSN or path. | Return a generic error string to the model (e.g. `error: tool_failed`) and log the full exception server-side. Repro: make a tool raise `Exception("postgres://user:pw@db.internal")`. Observe the string in `messages`. | a✓ b✗ c✓ d✗ |
| F6 | Medium | PROBABLE | B | agent.py:12 | Tool calls have no per-call timeout. | A tool that fetches a URL hangs on a slow host. The request and its worker are held indefinitely, and a few such requests exhaust the pool. | Wrap each tool call in a timeout, and treat a timeout as a counted step toward the F1 limit. | a✓ b✗ c✗ d✓ |
| F7 | Low | CONFIRMED | B | agent.py:23 (`request["question"]`) | A body with no `question` raises a KeyError, giving a 500 instead of a 400. A non-string value is passed to the model unvalidated. | A malformed client body returns a 500. | Validate that `question` is a non-empty string within the length limit, and return a 400 otherwise. | a✓ b✓ c✗ d✗ |

NEEDS VALIDATION:
- **S1:** The model chooses which tool to call and with what args, and an anonymous caller controls the prompt. So any tool in `tools` is effectively callable by the public. It is unresolved whether any tool has side effects (writes, emails, payments, fetching internal URLs, which would be SSRF) or reads non-public data. If so, this becomes Critical. The fix would be an allowlist of read-only tools for `/ask` and argument validation per tool.
- **S2:** Whether a gateway in front of `/ask` already enforces rate limits and body-size limits. If it does, F2 drops in severity.
- **S3:** Whether any tests exist, and whether they would fail on F1 (no termination) and F3 (missing assistant turn).

REFUTED:
- *"An unknown or hallucinated tool name crashes the request."* The `tools[...]` lookup is inside the `try` at line 11, so the KeyError is caught and returned as `error: ...`. The real effect is another loop iteration, which is covered by F1.
- *"No authentication is drift from the request."* The request specifies a public endpoint, so leaving out login matches it. The risk that remains is abuse control (F2), not missing auth.

WHAT HOLDS UP: The control flow is simple and readable. Tool exceptions do not crash the request. `json.dumps(..., default=str)` will not fail on non-serializable results. The basic answer-or-tool contract matches the request.

UNVERIFIED CLAIMS: The docstring at line 21 says "no login" by design; I could not confirm whether any upstream protection compensates. That `llm` returns `{"tool", "args"}` or `{"answer"}` is assumed and not shown; confirm it from the wrapper.

QUESTIONS FOR THE AUTHOR:
1. Which tools are in `tools` for `/ask`, and do any write data, send messages or fetch arbitrary URLs?
2. Is anything (gateway, WAF, quota) in front of `/ask` today?
3. What chat API shape does `llm` wrap, and does it require the assistant tool-call turn?

DECISION-MAKER SUMMARY: Do not announce `/ask` yet. One anonymous request can loop model calls indefinitely (F1), with no rate limit (F2), and the agent likely re-calls tools blindly because it never records its own calls (F3). Add step, token and time limits, rate limiting, and the assistant-turn fix first. If you proceed anyway, expect an uncapped bill from the first hostile user.

OWNER SUMMARY: The new question-answering feature can be made to run, and charge us, without any limit, by anyone on the internet. It also likely forgets what it already looked up, which makes runaway runs more likely. It needs hard limits and abuse protection before it is announced.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "agent.py", "status": "seen", "matters": true},
    {"item": "llm wrapper contract", "status": "not_seen", "matters": true},
    {"item": "tools registry and implementations", "status": "not_seen", "matters": true},
    {"item": "gateway / rate-limit config", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "agent.py", "kind": "file"},
      {"unit": "agent.py:run_agent", "kind": "function"},
      {"unit": "agent.py:ask_endpoint", "kind": "function"},
      {"unit": "loop terminates", "kind": "assumption"},
      {"unit": "endpoint protected upstream", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "tools implementations", "reason": "not supplied"},
      {"unit": "llm wrapper", "reason": "not supplied"},
      {"unit": "gateway config", "reason": "not supplied"},
      {"unit": "tests", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:8-17",
     "scenario": "An anonymous caller induces repeated tool calls or a persistently failing tool; while True has no step, token or time limit, so billed model calls over a growing context continue indefinitely.",
     "fix": "Add max_steps, a per-request token/cost budget and an overall deadline; truncate tool results; return a fixed fallback when a limit is hit.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Stub llm to always return {\"tool\": \"t\", \"args\": {}}; expect termination after N steps; observe it never returns."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:21-23",
     "scenario": "A script sends thousands of large-question requests to the unauthenticated endpoint; with no rate limit, quota or size cap, token spend is unbounded.",
     "fix": "Per-caller rate limiting, a global spend circuit breaker, and a max question length with 413/429 responses.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Send 50 concurrent POST /ask with a 200 KB question; expect 429/413; observe all accepted."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:10-15",
     "scenario": "The assistant's tool-call turn is never appended, so the model sees orphan tool results and re-issues calls, or a strict chat API rejects the second call and every tool-using question fails.",
     "fix": "Append the assistant tool-call message (with call id) before each tool result and link the result to it.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Stub llm to assert that the message preceding a tool result is the matching assistant call; observe the assertion fail."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:17",
     "scenario": "The model returns a reply with neither tool nor answer (refusal, other key, empty tool); reply['answer'] raises KeyError and the endpoint returns 500.",
     "fix": "Handle the third case with a safe fallback answer and log the malformed reply.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Stub llm to return {}; expect a graceful answer; observe KeyError."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:13-14",
     "scenario": "A tool raises an exception containing an internal DSN or path; the text enters the model context and the caller asks the model to quote it in the public answer.",
     "fix": "Send a generic error string to the model; log full exceptions server-side only.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Make a tool raise Exception('postgres://user:pw@db.internal'); observe the string in messages and potentially in the answer."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:12",
     "scenario": "A tool fetching a slow host hangs; with no per-call timeout the request and worker are held indefinitely and a few such requests exhaust the pool.",
     "fix": "Wrap each tool call in a timeout and count timeouts toward the step limit.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Register a tool that sleeps 600 s; call /ask so the model invokes it; observe the request does not return."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:23",
     "scenario": "A request body without 'question' raises KeyError, returning 500 instead of 400.",
     "fix": "Validate question is a non-empty bounded string; return 400 otherwise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "POST /ask with {}; expect 400; observe KeyError/500."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent.py:12",
     "suspicion": "Anonymous callers can steer the model into invoking any registered tool with arbitrary args, including side-effecting or SSRF-capable tools.",
     "unresolved_fact": "Which tools are registered for /ask and whether any write data, send messages, fetch arbitrary URLs or read non-public data."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent.py:21-23",
     "suspicion": "Upstream protection may or may not exist.",
     "unresolved_fact": "Whether a gateway or WAF enforces rate and body-size limits on /ask."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "tests (not supplied)",
     "suspicion": "No evidence the agent loop is tested.",
     "unresolved_fact": "Whether tests exist and would fail on non-termination (F1) and the missing assistant turn (F3)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "An unknown tool name crashes the request.",
     "evidence": "The tools[...] lookup is inside the try at agent.py:11-14; KeyError is caught and returned as 'error: ...' (effect folded into F1)."},
    {"id": "C2", "candidate": "Missing login is drift from the request.",
     "evidence": "The request specifies a public endpoint; the remaining risk is abuse control, covered by F2."}
  ]
}
```