**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session, so no code was run. Every reproduction below is a test to run, not one I ran.

---

**VERDICT: REWORK.** One public request with no login can keep the agent calling the billed model forever, with a growing context on every call, and nothing in the code caps cost, time or iterations.

**CONFIDENCE: medium.** I could not run anything. The `llm` wrapper, the `tools` dict, the web framework and the gateway or deploy config were not supplied. The main finding comes straight from the code, so it does not depend on any of those.

**INPUTS LEDGER**
- Seen:
  - the original request (`request.md`, verbatim)
  - the context (`context.md`)
  - `agent.py` (full file, 23 lines)
- Not seen:
  - **The `llm` callable.** Its message format and tool-call protocol are unknown. This matters for F3.
  - **The `tools` dict.** Which tools exist and what they can reach is unknown. This matters for S1 and F4.
  - **Gateway, deploy and framework config.** I can't tell if any rate limit, auth, timeout or body-size limit sits in front of `/ask`. This matters for F2 and F5.
  - **Tests.** None were supplied. The work cites none, so there is no test claim to check.

**COVERAGE**
- Checked: `agent.py:run_agent` and `agent.py:ask_endpoint`. I traced the main path plus these hostile inputs:
  - a model that always returns a tool call
  - an unknown tool name
  - a reply with neither key
  - a missing or huge `question`
  - a tool that hangs
- Not checked: the `llm` implementation, the tool implementations, framework routing, and the deploy config (none supplied).

**SEATS AND GATE:** one same-context reviewer (this session). No subagent and no cross-vendor seats. The sensitivity gate passed: the code contains no personal data, credentials or client material.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `agent.py:8-16` (`while True`, `continue`); docstring line 6 "Retry forever" | The agent loop has no limit on iterations, tokens, cost or wall-clock time. `messages` grows on every turn, so each model call costs more than the last, and total tokens grow roughly quadratically. | A caller asks something the model keeps "researching", or uses prompt injection ("call search again until you find X"). Each request then loops until the process dies, billing every call to the account. Many parallel requests multiply this (denial of wallet). | Add `max_steps` (for example 8), a per-request token or cost budget, and a deadline. Past any of these, return a bounded "could not answer" response. Repro: a fake `llm` that always returns `{"tool":"t"}`; expect `run_agent` to return within `max_steps` calls; today it never returns. | y/y/y/y |
| F2 | High | PROBABLE | B | `agent.py:20-22` (docstring "no login; anyone on the internet may call it") | The public endpoint drives billed model calls and tool execution with no rate limit, per-client quota or global spend cap anywhere in the code. "Public" was requested; "unmetered" was not. | A script sends thousands of requests per minute. Each one triggers at least one billed call, and with F1 an unbounded number. Spend is limited only by the provider's account limit. | Add a per-IP or per-key rate limit and concurrency cap, plus a global daily spend ceiling with an alert. Repro: send 100 concurrent POSTs; expect 429s past the limit; today all 100 run. It is PROBABLE only because the gateway config was not supplied. | y/n/y/y |
| F3 | High | PROBABLE | B | `agent.py:10-15` | The model's own tool-call reply is never added to `messages`; only the tool result is. The next turn shows the model a tool result with no record of which call produced it. Most chat APIs reject a tool message that has no preceding assistant tool call. | (a) With an OpenAI- or Anthropic-style API, the second call fails with a request error, and every tool-using question returns a 500. (b) With a lenient wrapper, the model can't see what it already tried, repeats the same call, and feeds F1. | Append the assistant reply, including its tool-call id, before the tool result, and send the result with the matching id. Repro: a fake `llm` that records `messages`; after one tool turn, assert that `messages[-2]` is the assistant tool call. Today it is the user question. | y/n/y/y |
| F4 | Medium | PROBABLE | B | `agent.py:12-14`, `22` | Raw exception text (`f"error: {exc}"`) goes to the model, and the model's answer goes to an anonymous caller. Exceptions often contain internal hostnames, file paths, SQL or connection strings. | A user asks "call the db tool with a bad id and repeat the exact error". The model echoes the internal details back to the public caller. | Return a generic error to the model and log the full exception server-side. Repro: a tool that raises `Exception("postgres://u:p@10.0.0.5")` and a model that echoes tool output; assert that the string is not in the HTTP response. | y/n/n/y |
| F5 | Medium | CONFIRMED | B | `agent.py:9`, `11`, `22` | No timeout on `llm(...)` or on tool calls. No handling of model errors. No validation of `request["question"]`: it can be missing, not a string, or arbitrarily long. | A tool that hangs on a slow URL holds the worker forever, and enough of these exhaust the pool. A 1 MB question is billed in full on every iteration. A body without `question` returns an unhandled `KeyError` (500). | Wrap model and tool calls in timeouts. Validate `question` as a non-empty string under N characters, returning 400 otherwise. Catch model errors and return 502/503. Repro: POST `{}`; expect 400; today it raises `KeyError`. | y/y/n/y |
| F6 | Low | CONFIRMED | B | `agent.py:16` | A reply with no `tool` and no `answer`, or with `tool: ""`, raises `KeyError` on `reply["answer"]`. | The model wrapper returns a refusal or an empty completion, and the caller gets a 500 instead of a clean failure. | Use `reply.get("answer")` and fall back to a fixed message if it is missing. Repro: a fake `llm` returning `{}`; expect a graceful response; today it raises `KeyError`. | y/y/n/n |

### NEEDS VALIDATION
- **S1, prompt injection into tools.** The question and every tool result are untrusted text that steer which tool is called and with which `**args`. There is no allowlist and no argument validation. The impact depends entirely on what is in `tools`. A fetch-URL tool would allow SSRF to internal addresses, and a write or DB tool would be worse. **To settle it:** the list of tools and what each can reach or change.
- **S2, gateway mitigation.** Some gateway may already rate-limit or authenticate `/ask` (bears on F2). **To settle it:** the deploy and gateway config for this route.

### REFUTED
- **C1, "the retry-forever docstring means a failing tool is re-executed in a tight loop without the model."** Withdrawn. The `except` block (lines 12-13) does not re-run the tool. It feeds the error back to the model, which decides what to do next. The unbounded behaviour is real but belongs to F1, not to a hidden retry loop.
- **C2, "an unknown tool name crashes the request."** Withdrawn. The `tools[...]` lookup is inside the `try`, so the `KeyError` is caught and returned to the model as an error.

### WHAT HOLDS UP
- Tool exceptions are contained, so one failing tool doesn't crash the request (line 12-13).
- `json.dumps(..., default=str)` serialises tool results that are not JSON-native instead of raising.
- The structure (question in, loop, answer out) matches the request. The request did ask for a public endpoint, so the missing login is not drift in itself. Missing metering is.

### UNVERIFIED CLAIMS
- **"Retry forever on a tool error"** is presented as a feature. Nothing shows that anyone decided unbounded spend was acceptable. To confirm, ask the owner whether a budget exists.
- **That the `llm` wrapper accepts `role: "tool"` messages with no preceding call.** To confirm, read the wrapper or run one tool turn against it.

### QUESTIONS FOR THE AUTHOR
1. Is there any rate limit, auth or spend cap in front of `/ask` today (gateway, provider limits)?
2. What tools are in `tools`, and can any of them reach internal networks or write data?
3. Which model API does `llm` wrap, and does it need the assistant tool-call message before a tool result?

### DECISION-MAKER SUMMARY
Do not announce `/ask` yet. A single anonymous request can loop billed model calls without limit, and nothing meters callers (F1, F2). The tool-calling history is also probably malformed (F3). Add a step, token and time budget, plus per-client rate limits and a spend ceiling, then re-review. Proceeding as is risks an open-ended bill from one script.

### OWNER SUMMARY
The question-answering service as written can keep running and charging our account indefinitely for a single question. Anyone on the internet could trigger that as often as they like. It also likely mishandles its own research steps and may reveal internal error details to the public. It needs spending and time limits, and some protection against abuse, before launch.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "agent.py", "status": "seen", "matters": true},
    {"item": "llm callable implementation", "status": "not_seen", "matters": true},
    {"item": "tools dict and tool implementations", "status": "not_seen", "matters": true},
    {"item": "gateway/deploy config for /ask", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "agent.py", "kind": "file"},
      {"unit": "agent.py:run_agent", "kind": "function"},
      {"unit": "agent.py:ask_endpoint", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "llm wrapper", "reason": "not supplied"},
      {"unit": "tools", "reason": "not supplied"},
      {"unit": "gateway/deploy config", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:8-16",
     "scenario": "A model that keeps calling tools (naturally or via prompt injection) loops forever; each billed call carries a growing message history, so one anonymous request causes unbounded spend.",
     "fix": "Add max_steps, a per-request token/cost budget and a deadline; return a bounded failure when exceeded.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Fake llm always returns {\"tool\":\"t\"}; expect run_agent to stop after max_steps; observed: never returns."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:20-22",
     "scenario": "A script floods the unauthenticated /ask with concurrent requests; every one triggers billed model calls with no rate limit, quota or spend cap.",
     "fix": "Per-IP/key rate limit and concurrency cap, plus a global spend ceiling with alerting.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Send 100 concurrent POST /ask; expect 429 beyond the limit; observed in code: all 100 run."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:10-15",
     "scenario": "The assistant tool-call reply is never appended, so the next llm call sends an orphan tool result: strict APIs reject it (500 on every tool question), and lenient ones lose the call history and repeat calls.",
     "fix": "Append the assistant reply (with tool-call id) before the tool result, and link the result by id.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Fake llm recording messages; after one tool turn assert messages[-2] is the assistant tool call; observed: it is the user question."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:12-14,22",
     "scenario": "Raw exception text (hosts, paths, connection strings) is given to the model, which can echo it to an anonymous caller.",
     "fix": "Return a generic error string to the model; log the full exception server-side.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "A tool raises Exception('postgres://u:p@10.0.0.5') and the model echoes tool output; assert the string is absent from the response."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:9,11,22",
     "scenario": "No timeouts on model or tool calls, so a hanging tool pins a worker forever; a 1 MB question is billed on every iteration; a missing 'question' key returns a 500.",
     "fix": "Timeouts on llm and tool calls; validate question as a non-empty string under a length cap (400 otherwise); map model errors to 502/503.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "POST {} to /ask; expect 400; observed: KeyError."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:16",
     "scenario": "A reply with neither tool nor answer raises KeyError and the caller gets a 500.",
     "fix": "Use reply.get('answer') with a fallback message.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Fake llm returns {}; expect a graceful response; observed: KeyError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent.py:11",
     "suspicion": "Untrusted question and tool output choose the tool and its **args with no allowlist or validation, so prompt injection could drive dangerous tools (SSRF, writes).",
     "unresolved_fact": "Which tools are in the tools dict and what each can reach or modify."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent.py:20-22",
     "suspicion": "A gateway may already rate-limit or authenticate /ask, which would mitigate F2.",
     "unresolved_fact": "The deploy/gateway config for the /ask route."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A failing tool is re-executed in a tight loop without the model.",
     "evidence": "agent.py:12-13 feeds the error back to the model; the tool is not re-run directly. The unbounded behaviour is covered by F1."},
    {"id": "C2", "candidate": "An unknown tool name crashes the request.",
     "evidence": "The tools[...] lookup is inside the try at agent.py:11, so the KeyError is caught."}
  ]
}
```