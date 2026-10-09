**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available. The work was not written in this conversation, so I share none of the author's reasoning. Every finding comes from reading the 22 supplied lines. Nothing was executed.

VERDICT: **REWORK**. A public, unauthenticated endpoint drives a `while True` loop of per-token-billed model calls with no turn, token, cost or time cap. Any caller, or the model itself, can run up unbounded spend on a single request.

CONFIDENCE: **medium**. The code is short and every path was traced by hand. Limits: no tools to run the reproductions, and the `llm` adapter, the `tools` registry and the deployment layer (gateway, rate limits, timeouts) were not supplied.

INPUTS LEDGER:
- Seen: request.md, context.md, agent.py (full).
- Not seen:
  - `llm` callable/adapter. This matters for timeouts, max_tokens and message format.
  - `tools` registry. This matters for whether model-chosen calls can reach SSRF, file or side-effect sinks.
  - Web framework and gateway config. This matters for per-caller rate limiting and request size limits.
  - Tests: none supplied. That matters, because no behavior is verified.

COVERAGE: Scope is the whole work (agent.py).
- Checked: `run_agent` (lines 5–17), `ask_endpoint` (lines 20–22), request.md, context.md.
- Not checked:
  - `llm` adapter, `tools` registry and infra config (not supplied).
  - Runtime behaviour (no tools).

SEATS AND GATE: Only a local same-context review ran. No subagent tool was available, and cross-vendor seats were not requested. Sensitivity gate passed: there is no personal or confidential data in the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | agent.py:8–16 (and docstring line 6, "Retry forever") | `while True` has no turn, token, cost or wall-clock cap. Tool errors are fed back and the loop `continue`s indefinitely, by design. | An anonymous caller asks a question that steers the model to keep calling tools ("keep searching until you find X"). Alternatively, a tool fails permanently and the model keeps retrying. The request never returns, and every turn re-sends the growing history. Billed tokens grow roughly quadratically, and the cost is uncapped on one request. Many parallel requests multiply this. | Add a max-turns cap (e.g. 8), a cumulative token/cost budget, and a deadline. When any limit is hit, return a bounded "could not answer" response. Repro: `llm=lambda m:{"tool":"t","args":{}}`, `tools={"t":lambda:"x"}`, `run_agent(llm,tools,"q")`. Expected: return or raise after N turns. Observed: never returns, and `len(messages)` grows without bound. | y/y/y/y |
| F2 | High | CONFIRMED (traced) | B | agent.py:9–15 | The model's own tool-call turn is never appended to `messages`. Only `{"role":"tool","content":...}` is added, with no tool name or call id. | After the first tool call, the transcript is user, then tool, then tool, and so on. The model cannot see which call produced which result, so it tends to re-issue the same call, which feeds F1. Real chat APIs (e.g. Anthropic `tool_use`/`tool_result`) reject a tool result without its preceding call, so the request may fail outright. Either way the agent cannot reliably "use tools until it can answer". | Append the assistant reply (including the tool name, args and id) before the tool result, and tag the result with the matching id. Repro: stub `llm` that records `messages`. First returns `{"tool":"t","args":{}}`, then `{"answer":"a"}`. On the second call, observed `messages == [user, tool]`. Expected: `[user, assistant(tool_call t), tool(result for t)]`. | y/y/y/y |
| F3 | Medium | CONFIRMED (traced) | B | agent.py:22 | `request["question"]` has no size or type check before it is sent to a billed model, and it is re-sent on every turn. | A caller posts a question near the model's context limit. Each turn bills that full input again, multiplied by F1. | Reject non-strings and cap the length (e.g. 2–4k chars) with a 400 response. Repro: `ask_endpoint({"question":"A"*500_000},llm,tools)` with a recording stub. Expected: 400 before any `llm` call. Observed: `llm` is called with the full 500k string. | y/y/n/n |
| F4 | Medium | CONFIRMED (traced) | B | agent.py:15 | Tool output is appended without truncation. `json.dumps(..., default=str)` of an arbitrary result can be huge. | A search or fetch tool returns a large page. It is re-billed on every later turn and can overflow the context, which makes the call error out. | Truncate or summarise each tool result to a byte cap before appending. Repro: `tools={"t":lambda:"x"*10_000_000}`. Expected: content length ≤ cap. Observed: 10 MB appended. | y/y/n/n |
| F5 | Medium | PROBABLE | B | agent.py:13–14 | Raw exception text (`f"error: {exc}"`) goes into the model context, and the model's answer is returned verbatim to the public. | A tool raises with an internal path, hostname, connection string or upstream response body. The model quotes it, and the internals are disclosed to an anonymous caller. | Log the exception server-side and give the model a generic `"tool_error"` code only. Repro: `tools={"t":lambda: open("/srv/internal/cfg")}` and an `llm` that echoes the last message as its answer. Observed answer contains `"error: [Errno 2] No such file or directory: '/srv/internal/cfg'"`. | y/n/n/y |
| F6 | Medium | CONFIRMED (traced) | B | agent.py:17 | `reply["answer"]` assumes every non-tool reply has an `answer` key. A falsy `tool` (`""`, `None`) also falls through to this line. | The model hits max_tokens, refuses, or returns plain text. The result is an unhandled `KeyError` and a 500 for the user, after the tokens are already billed. | Handle a missing or empty answer explicitly, and return a defined error payload. Repro: `llm=lambda m:{"text":"hi"}`. Observed: `KeyError: 'answer'`. Expected: a defined fallback response. | y/y/y/n |
| F7 | Low | CONFIRMED (traced) | B | agent.py:22 | A missing `question` key raises `KeyError`, so the caller gets a 500 instead of a 400. | A malformed POST produces an unhandled error and noisy 5xx metrics. | Validate the request and return 400. Repro: `ask_endpoint({},llm,tools)`. Observed: `KeyError: 'question'`. | y/y/n/n |

**Siblings (F1, F2):**
- F1: I searched for every place that bounds work per request: loop, input size, tool-output size, time. Found the uncapped input (F3) and the uncapped tool output (F4), each recorded as its own finding. There is no time bound anywhere; see NEEDS VALIDATION.
- F2: I searched for other places that build `messages`. There is only line 7 and line 15, with no other sibling.
- Security boundary for F1: the principal is an anonymous internet caller (line 21, "no login"). They control the question text, which steers model tool use. The failing control is that no turn, token or cost cap exists. The boundary crossed is from the public internet to the billed model account, and the affected resource is the organisation's per-token spend and worker capacity.
- F2 is not a security finding.

## NEEDS VALIDATION
- **Per-caller rate limiting / quota.** None exists in agent.py. To settle: whether the gateway or framework in front of `/ask` enforces per-IP or per-key limits and a global spend ceiling.
- **Timeouts on `llm` and tool calls.** There are none in this file, so one hung call could hold a worker forever. To settle: whether the `llm` adapter and each tool set a network timeout.
- **Model-chosen tool calls reaching dangerous sinks.** `tools[reply["tool"]](**args)` runs any registered tool with model-controlled args, and the model is steered by an anonymous user's question and by tool results (prompt injection). To settle: the `tools` registry. Specifically, whether any tool fetches arbitrary URLs (SSRF to internal or metadata endpoints), reads files, writes, sends messages, or spends money.
- **max_tokens per call.** To settle: whether the `llm` adapter caps output tokens.

## REFUTED
- "An unknown tool name crashes the request." `tools[reply["tool"]]` is inside the `try` at line 12, so the `KeyError` is caught. It then feeds F1's loop instead.
- "Non-dict `args` crash the request." The `TypeError` from `**` is likewise caught at line 13.

## WHAT HOLDS UP
- The basic shape matches the request: tool loop, then answer, then a returned dict.
- Tool exceptions do not crash the process.
- `json.dumps(default=str)` safely serialises arbitrary results.
- Errors from `llm()` itself propagate rather than being swallowed, which fails closed.

## UNVERIFIED CLAIMS
- Docstring line 21, "anyone on the internet may call it." This is presented as intended. Confirm that the deployment really has no auth and whether any gateway limits apply.
- Nothing in the work claims to be tested. No tests were supplied.

## QUESTIONS FOR THE AUTHOR
1. Which tools are registered, and can any of them make network requests or have side effects?
2. Is there a gateway-level rate limit or a spend ceiling on the model account?
3. What message format does the `llm` adapter expect for tool calls and results?

## DECISION-MAKER SUMMARY
Do not announce `/ask` yet. One anonymous request can loop forever on billed model calls (F1), and the tool transcript is malformed (F2), which makes that loop more likely and answers less reliable. Add turn, token and time caps, fix the message history, and confirm the tool list and rate limiting before launch. Proceeding anyway risks an unbounded bill and outages from any caller.

## OWNER SUMMARY
The new question-answering service can be made to run forever by any member of the public, and every step of that run costs us money with no upper limit. It also loses track of its own research steps, which makes the endless runs more likely and the answers worse. It needs hard limits on steps, cost and time, plus a few smaller safety fixes, before it is announced.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "agent.py", "status": "seen", "matters": true},
    {"item": "llm adapter", "status": "not_seen", "matters": true},
    {"item": "tools registry", "status": "not_seen", "matters": true},
    {"item": "gateway / rate-limit config", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "agent.py", "kind": "file"},
      {"unit": "agent.py:run_agent", "kind": "function"},
      {"unit": "agent.py:ask_endpoint", "kind": "function"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "llm adapter", "reason": "not_supplied"},
      {"unit": "tools registry", "reason": "not_supplied"},
      {"unit": "gateway / rate-limit config", "reason": "not_supplied"},
      {"unit": "runtime execution of reproductions", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:8-16",
     "scenario": "An anonymous caller steers the model into repeated tool calls (or a tool fails permanently); while True never exits, every turn re-sends the growing history, and per-token billing grows without bound on one request.",
     "fix": "Add max-turns, cumulative token/cost budget and a deadline; on limit, return a bounded 'could not answer' response.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "llm=lambda m:{'tool':'t','args':{}}; tools={'t':lambda:'x'}; run_agent(llm,tools,'q'). Expected: stops after N turns. Observed: never returns; len(messages) grows unbounded.",
     "security": true,
     "boundary": {"principal": "anonymous internet caller", "input": "question text on POST /ask, steering model tool use",
                  "control": "no turn, token, cost or time cap on the agent loop", "crossed": "public internet to billed model account",
                  "resource": "per-token model spend and worker capacity"},
     "siblings_searched": {"searched": "every per-request bound in agent.py: loop, input size, tool-output size, time",
                           "found": "uncapped question size (F3), uncapped tool output (F4); timeouts left as needs_validation"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:9-15",
     "scenario": "The assistant's tool-call turn is never appended; the model sees tool results with no record of which call produced them, re-issues calls (feeding F1), and real tool-use APIs may reject the transcript.",
     "fix": "Append the assistant reply (tool name, args, id) before the tool result and tag the result with the matching id.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Recording stub llm returns {'tool':'t','args':{}} then {'answer':'a'}. On the second call observed messages == [user, tool]; expected [user, assistant(tool_call t), tool(result for t)].",
     "security": false,
     "siblings_searched": {"searched": "all writes to messages in agent.py (lines 7 and 15)", "found": "none beyond line 15"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:22",
     "scenario": "A caller posts a question near the context limit; it is billed in full on every turn.",
     "fix": "Validate type and cap question length; return 400 on violation.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "ask_endpoint({'question':'A'*500000},llm,tools) with a recording stub. Expected: 400 before any llm call. Observed: llm called with the full string."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:15",
     "scenario": "A tool returns a very large result; it is appended untruncated and re-billed every later turn, or overflows context.",
     "fix": "Truncate or summarise each tool result to a byte cap before appending.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "tools={'t':lambda:'x'*10_000_000}; observed a 10 MB message appended; expected content length <= cap."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:13-14",
     "scenario": "A tool raises with internal paths or hostnames; the raw exception text enters the model context and is echoed in the public answer.",
     "fix": "Log exceptions server-side; give the model only a generic error code.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "tools={'t':lambda: open('/srv/internal/cfg')}; llm echoes last message as answer. Observed answer contains \"error: [Errno 2] No such file or directory: '/srv/internal/cfg'\"."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:17",
     "scenario": "The model returns a reply without an 'answer' key (max_tokens, refusal, plain text) or with a falsy tool; KeyError gives the user a 500 after the tokens are billed.",
     "fix": "Handle a missing or empty answer explicitly and return a defined error payload.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "llm=lambda m:{'text':'hi'}; run_agent(llm,{},'q'). Observed KeyError: 'answer'; expected a defined fallback."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:22",
     "scenario": "A POST without 'question' raises KeyError and returns 500 instead of 400.",
     "fix": "Validate the request body and return 400.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "ask_endpoint({},llm,tools). Observed KeyError: 'question'; expected 400."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent.py:20-22",
     "suspicion": "No per-caller rate limit or global spend ceiling on a public unauthenticated endpoint.",
     "unresolved_fact": "Whether the gateway/framework enforces per-IP or per-key limits and an account spend cap."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent.py:9,12",
     "suspicion": "No timeout on llm or tool calls; a hung call holds a worker indefinitely.",
     "unresolved_fact": "Whether the llm adapter and each tool set network timeouts."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent.py:12",
     "suspicion": "Model-chosen tool and args, steered by an anonymous question or injected tool output, may reach SSRF, file or side-effect sinks.",
     "unresolved_fact": "The contents of the tools registry and whether any tool fetches arbitrary URLs, reads files or has side effects."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent.py:9",
     "suspicion": "No per-call output token cap.",
     "unresolved_fact": "Whether the llm adapter sets max_tokens."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "An unknown tool name crashes the request.",
     "evidence": "tools[reply['tool']] is inside the try at line 12; the KeyError is caught at line 13."},
    {"id": "C2", "candidate": "Non-dict args crash the request.",
     "evidence": "The TypeError from ** unpacking is raised inside the try at line 12 and caught at line 13."}
  ]
}
```