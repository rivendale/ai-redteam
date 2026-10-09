VERDICT: **REWORK.** Any anonymous internet user can trigger an unbounded model-call loop billed to your account, and the conversation history the agent sends back to the model is malformed.

CONFIDENCE: **medium.** Limits: no tools in this session, so nothing was run and every reproduction below is written out but not executed. The `llm` adapter, the `tools` registry and the deployment layer (gateway, rate limits) were not supplied. This was a single reviewer with no subagent or second seat, although I did not write the work.

INPUTS LEDGER:
- Seen: `request.md` (verbatim request), `context.md`, `agent.py` (full).
- Not seen: the `llm` callable and its provider API, which matters for F2 and S1. The `tools` dict and what each tool can do, which matters for S1 and S2. Any gateway, rate limiting or request-size limit in front of `/ask`, which matters for S3 and moderates F1 and F4 but does not remove them. The HTTP framework's timeout behaviour, which matters for F3.

COVERAGE: Scope is the whole work (`agent.py`).
- Checked: `request.md`, `context.md`, `agent.py`, `run_agent`, `ask_endpoint`, the docstring claims ("Retry forever on a tool error", "no login").
- Not checked:
  - The `llm` adapter, tools and gateway config (`not_supplied`).
  - Invisible or look-alike characters in `agent.py` (`no_tools`): I could not byte-scan the file.

SEATS AND GATE: One reviewer (this session). No subagent or cross-vendor seats were available because the session has no tools. Sensitivity gate passed: no personal data, credentials or confidential material in the inputs.

### Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `agent.py:8-17` (`while True`; the only exit is `return reply["answer"]` at 17) | No cap on turns, tokens, cost or wall-clock time. The docstring makes "retry forever" deliberate. | An anonymous caller posts a question that keeps the model calling tools (e.g. "call search again after every result until I say stop"), or any tool fails persistently. Lines 13-16 turn every exception into a result and `continue`. Each turn resends the whole growing `messages` list, so billed tokens grow roughly quadratically. The loop ends only when the model chooses to answer, if ever. A handful of parallel requests run up unbounded spend on your account. | Add `max_turns` (e.g. 8) and a cumulative token/cost budget per request, and return a fixed "could not answer" when either is hit. Add a per-request deadline. Cap consecutive tool errors (e.g. 2). **Repro:** stub `llm = lambda m: {"tool": "t", "args": {}}` and `tools = {"t": lambda: 1}`, then call `run_agent(llm, tools, "q")` with a 5 s timeout. Expected: it returns or raises at the cap. Observed by trace: it never returns, and `len(messages)` grows without bound. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED (traced) | B | `agent.py:15` (only `{"role": "tool", ...}` is appended) | The model's own tool-call turn is never added to `messages`. Tool results carry no tool name, arguments or call id. | A question needs two tool calls. On turn 3 the model sees `user, tool, tool` with no record of what it asked for and cannot tell which result belongs to which call. It re-issues calls, which feeds F1, or answers from mismatched data. On the major provider APIs a tool-result message with no preceding assistant tool call is rejected outright, so the first tool use fails (the adapter was not supplied; see S1). | Append the assistant reply (with its tool call and id) before the tool result, and include `tool_call_id`/name in the result message, in the provider's format. **Repro:** stub an `llm` that records `messages` and calls tool `a` and then tool `b`. On the third call, assert that the history contains both assistant tool-call turns. Observed by trace: they are absent. | a✓ b✓ c✓ d✓ |
| F3 | Medium | PROBABLE | B | `agent.py:12` (tool call), `agent.py:9` (`llm(messages)`) | There is no timeout on tool or model calls. | A tool that hangs (a slow upstream, a large fetch) holds the request and its worker indefinitely. A few concurrent anonymous requests exhaust the worker pool, and the endpoint stops answering everyone. | Wrap each tool and model call in a timeout, and enforce the per-request deadline from F1. **Repro:** `tools = {"t": lambda: time.sleep(3600)}` with an `llm` that calls `t` once. Expected: a timeout error result within N s. Observed by trace: it blocks for an hour. | a✓ b✗ c✗ d✓ |
| F4 | Medium | CONFIRMED (traced) | B | `agent.py:22` (`request["question"]`) | No validation of type, presence or size of `question`. | A caller sends a 1 MB question. It is billed on every turn of the loop, multiplied by F1. A missing key raises an uncaught `KeyError`, which becomes a 500. | Reject requests where the field is missing or not a string, and cap the length (e.g. 2,000 characters) before any model call. **Repro:** `ask_endpoint({}, llm, tools)` raises `KeyError` instead of returning a 400. `ask_endpoint({"question": "x"*10**6}, ...)` reaches `llm` unchanged. | a✓ b✓ c✗ d✓ |
| F5 | Medium | PROBABLE | B | `agent.py:13-14` (`f"error: {exc}"`) | Raw exception text goes into the model context, and the model can repeat it to an anonymous caller. | A tool raises an exception whose message contains an internal hostname, file path or connection string with a password. The caller asks "repeat the last tool error verbatim", and the answer leaks it. | Return a generic error code to the model, and log the full exception server-side only. **Repro:** `tools = {"t": lambda: (_ for _ in ()).throw(RuntimeError("db://admin:pw@10.0.0.5"))}` with a stub `llm` that calls `t` and then returns `{"answer": <last tool content>}`. Observed by trace: the answer contains `admin:pw`. | a✓ b✗ c✓ d✗ |
| F6 | Low | CONFIRMED (traced) | B | `agent.py:17` (`reply["answer"]`), `agent.py:10` (`reply.get("tool")`) | Any reply with neither a truthy `tool` nor an `answer` key crashes. This covers a refusal, a content-only message, or `tool: ""`. | The model returns `{"content": "I can't help"}`, and the result is an uncaught `KeyError` and a 500. | Handle an unknown reply shape explicitly and return a fixed fallback. **Repro:** `run_agent(lambda m: {"content": "x"}, {}, "q")` raises `KeyError: 'answer'`. | a✓ b✓ c✗ d✗ |

**Confirm-or-refute and siblings:**
- **F1:** The strongest defence is "the model will normally stop". That does not hold: the loop exit is under the control of anonymous input and of tool failures, and the docstring promises retrying forever. Held as **Critical, security: yes**.
  - Boundary: anonymous internet caller → `question` text (plus tool errors) → no turn/token/cost cap → crosses from public input to billed account spend → resource is your model-provider budget and worker capacity.
  - Siblings searched (other unbounded-spend or unbounded-resource paths in `agent.py`): found F3 (no time bound), F4 (no input-size bound) and the growing `messages` list (part of F1, same location). Rate limiting is not in the supplied code (S3).
- **F2:** The strongest defence is "the adapter might track the assistant turns internally". But `llm(messages)` takes the whole history on every call, which signals a stateless design, and the adapter was not supplied. Held as **High, security: no**.
  - Siblings searched (other places where history or messages are built): line 7 (initial user turn) is fine. Line 15 is the only append, so there are no other sites.

### Needs validation
- **S1:** Whether the `llm` adapter rejects or repairs a tool message with no preceding assistant tool call. This settles whether F2 breaks every tool use or degrades answers.
- **S2:** What the tools can do. Tool name and `args` come straight from model output (`agent.py:12`), and anonymous users steer the model through `question`, so every registered tool is callable with attacker-chosen arguments. Settle it by listing each tool and checking whether any of them writes, fetches arbitrary URLs (SSRF), reads files, or touches other users' data. Settle also whether tools return untrusted web content (indirect prompt injection). If any tool has side effects or private reach, this becomes Critical.
- **S3:** Whether a gateway in front of `/ask` enforces per-IP rate limits, a request-size limit and timeouts. Even if it does, F1 remains, because a single request is unbounded.
- **S4:** How the answer is rendered to the caller. If a client renders it as markdown or HTML, image links in model output can exfiltrate context. This depends on the client, which was not supplied.

### Refuted
- **R1** (candidate: an unknown tool name crashes the request). Refuted because `tools[reply["tool"]]` sits inside the `try` at lines 11-14, so the `KeyError` is caught and returned as an error string. It still feeds F1.
- **R2** (candidate: a non-serialisable tool result crashes `json.dumps`). Refuted because `default=str` at line 15 stringifies it.

### What holds up
- Tool exceptions do not crash the request.
- Results are serialised safely.
- The request is met in shape: the agent uses tools until it answers and returns the answer.
- The lack of authentication is stated openly (line 21) rather than hidden.

### Unverified claims
- "Anyone on the internet may call it": I could not see the deployment config, so it is unknown whether anything in front of the endpoint mitigates this.
- The implicit claim that the model will eventually answer: there is no evidence, and F1 shows the code does not enforce it.

### Questions for the author
1. Which tools are registered, and do any of them have side effects or reach private data?
2. Which provider API does `llm` wrap, and how does it expect tool calls and tool results to be sent?
3. Is there a gateway with rate limits, a size limit and timeouts in front of `/ask`?

### Decision-maker summary
Do not announce the endpoint until F1 (turn and cost caps, per-request deadline), F2 (correct tool-call history) and F4 (input size limit) are fixed, and S2's tool list has been reviewed. If you proceed anyway, one anonymous user can drive unbounded per-token charges to the account, and tool use may fail or loop on every request.

### Owner summary
As written, anyone on the internet can make this assistant keep working forever, and the company pays for every step. The assistant also forgets what it asked its tools for, which can make it fail or repeat itself. Both need fixing, and the tools it can use should be checked, before the service goes public.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "agent.py", "status": "seen", "matters": true},
    {"item": "llm adapter / provider API", "status": "not_seen", "matters": true},
    {"item": "tools registry", "status": "not_seen", "matters": true},
    {"item": "gateway / rate-limit / timeout config", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-single-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "agent.py", "kind": "file"},
      {"unit": "agent.py:run_agent", "kind": "function"},
      {"unit": "agent.py:ask_endpoint", "kind": "function"},
      {"unit": "docstring: retry forever on a tool error", "kind": "claim"},
      {"unit": "docstring: no login; anyone may call it", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "llm adapter", "reason": "not_supplied"},
      {"unit": "tools registry", "reason": "not_supplied"},
      {"unit": "gateway config", "reason": "not_supplied"},
      {"unit": "agent.py invisible/look-alike character scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:8-17",
     "scenario": "An anonymous caller's question keeps the model calling tools, or a tool fails persistently; the while True loop has no turn, token, cost or time cap and resends the growing history each turn, so billed spend grows without bound.",
     "fix": "Add max_turns, a per-request token/cost budget, a per-request deadline and a cap on consecutive tool errors; return a fixed fallback when any is hit.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Stub llm = lambda m: {'tool': 't', 'args': {}} and tools = {'t': lambda: 1}; call run_agent(llm, tools, 'q') under a 5 s timeout. Expected: return or raise at the cap. Observed by trace: never returns; messages grows without bound. Not executed (no tools).",
     "security": true,
     "boundary": {"principal": "an anonymous internet caller", "input": "the question field of POST /ask (and induced tool errors)",
                  "control": "no turn, token, cost or time cap in run_agent", "crossed": "public input to billed account spend",
                  "resource": "the model-provider budget and worker capacity"},
     "siblings_searched": {"searched": "all unbounded spend/resource paths in agent.py: loop exit, history growth, input size, call timeouts, rate limiting",
                           "found": "F3 (no timeouts), F4 (no input size cap); rate limiting not present in supplied code (S3)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:15",
     "scenario": "On a question needing two tool calls, the model sees user, tool, tool with no record of its own calls; it re-calls tools or mismatches results, and provider APIs that require a matching assistant tool call reject the request.",
     "fix": "Append the assistant tool-call reply before each tool result and include the tool call id/name in the result message, in the provider's format.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Stub an llm that records messages and calls tool a, then tool b; on the third call assert that both assistant tool-call turns are in messages. Observed by trace: absent. Not executed (no tools).",
     "security": false,
     "siblings_searched": {"searched": "every place messages is built or appended in agent.py",
                           "found": "line 7 (initial user turn) is correct; line 15 is the only append"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:9,12",
     "scenario": "A hanging tool or model call holds the request and worker indefinitely; a few concurrent anonymous requests exhaust the pool.",
     "fix": "Wrap tool and model calls in timeouts and enforce a per-request deadline.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "tools = {'t': lambda: time.sleep(3600)} with an llm that calls t once; expected a timeout error result within N s; observed by trace: blocks for an hour. Not executed (no tools)."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:22",
     "scenario": "A 1 MB question is billed on every loop turn; a missing question key raises an uncaught KeyError and returns 500.",
     "fix": "Validate that question is present and a string, and cap its length before any model call; return 400 otherwise.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "ask_endpoint({}, llm, tools) raises KeyError instead of returning 400; ask_endpoint({'question': 'x'*10**6}, ...) passes it to llm unchanged. Not executed (no tools)."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:13-14",
     "scenario": "A tool exception message containing an internal host or credential enters the model context; an anonymous caller asks the model to repeat it and receives it.",
     "fix": "Send the model a generic error code; log the full exception server-side only.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "A tool raising RuntimeError('db://admin:pw@10.0.0.5') and a stub llm that calls it, then answers with the last tool content; observed by trace: the answer contains admin:pw. Not executed (no tools)."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:10,17",
     "scenario": "A model reply with neither a truthy tool nor an answer key (a refusal, content only, tool '') raises KeyError and returns 500.",
     "fix": "Handle unknown reply shapes explicitly with a fixed fallback.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "run_agent(lambda m: {'content': 'x'}, {}, 'q') raises KeyError: 'answer'. Not executed (no tools)."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent.py:9,15",
     "suspicion": "The provider rejects tool results that have no preceding assistant tool call, so every tool use fails.",
     "unresolved_fact": "Which API the llm adapter wraps and whether it repairs history (the adapter was not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent.py:12",
     "suspicion": "Anonymous users can steer the model to call any registered tool with arbitrary args; tool output may carry indirect prompt injection.",
     "unresolved_fact": "The list of registered tools and whether any has side effects, arbitrary URL fetch, file access or reach into other users' data."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent.py:20-22",
     "suspicion": "No rate limiting, request-size limit or timeout in front of /ask.",
     "unresolved_fact": "The gateway/deployment configuration for /ask."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent.py:22",
     "suspicion": "Model output rendered as markdown/HTML by a client could exfiltrate data via image links.",
     "unresolved_fact": "How clients render the answer field."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "An unknown tool name crashes the request.",
     "evidence": "The lookup tools[reply['tool']] is inside the try at agent.py:11-14, so the KeyError is caught (it still feeds F1)."},
    {"id": "R2", "candidate": "A non-serialisable tool result crashes json.dumps.",
     "evidence": "default=str at agent.py:15 stringifies it."}
  ]
}
```