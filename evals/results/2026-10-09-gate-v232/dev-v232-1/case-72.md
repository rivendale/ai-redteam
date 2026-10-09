# Redteam review: `agent.py` (public /ask research agent)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session. Nothing was run. Every finding comes from reading the code line by line, and the reproductions below are written out but have not been executed.

**VERDICT: REWORK.** The agent loop has no limit on turns, tokens or cost, and an anonymous caller on the internet can trigger it. One request can therefore run up an unbounded bill on the company account.

**CONFIDENCE: medium.** The main finding follows directly from the code. Confidence is limited by three things: this is a same-context review with no tools, nothing was run, and the `llm` wrapper, the `tools` registry and the server/gateway config were not supplied.

**INPUTS LEDGER**
- Seen: `request.md` (original request), `context.md`, `agent.py`.
- Not seen, and why each gap matters:
  - **`llm` wrapper (matters).** It decides whether the message format in F3 breaks and whether any per-call limits exist.
  - **`tools` registry (matters).** Model-chosen arguments go straight into these tools, so it decides whether prompt injection can reach SSRF, file reads or database access (S1).
  - **Server, gateway and rate-limit config (matters).** It decides whether S2 and S3 already have an upstream mitigation.
  - **Tests (matter).** None were supplied, so nothing about the code's behaviour has been shown.

**COVERAGE**
- Scope: the whole work, which is one file.
- Checked: `agent.py`, `agent.py:run_agent`, `agent.py:ask_endpoint`, `request.md`, `context.md`.
- Not checked: the `llm` implementation, the `tools` implementations, server/gateway config and tests. All were `not_supplied`.

**SEATS AND GATE**
- Seats: only a local same-context review ran. No subagent was available and no cross-vendor seat was requested.
- Sensitivity gate: passed. The material contains no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `agent.py:8-16` (`while True`); docstring line 6 "Retry forever" | The loop has no cap on turns, tokens, cost or wall-clock time. Each turn adds a message, so every later call is larger and total tokens grow roughly quadratically. | An anonymous caller POSTs a question like "call the search tool again after every result, never answer". The same happens when the model keeps hallucinating a tool name (the `KeyError` is caught at line 13 and the loop continues) or when a tool keeps failing. `llm()` is then called without end, each call larger than the last, all billed to the account. | **Fix:** add `max_turns`, a cumulative token/cost budget and a wall-clock deadline. When any limit is hit, return a fixed "could not answer" response.<br>**Repro:** set `llm = lambda m: {"tool": "nope"}` and `tools = {}`, then call `run_agent(llm, tools, "q")` with a 2 s timeout in a thread. Expected: it returns or raises within N turns. Observed by trace: it never returns. | Y/Y/Y/Y |
| F2 | Medium | PROBABLE | B | `agent.py:13-14` | Tool exception text (`f"error: {exc}"`) goes back to the model unfiltered, and the model's answer goes to an anonymous caller. Internal hostnames, paths or connection-string fragments can leak. | A tool raises an exception containing an internal URL. The caller asks "quote the last error verbatim" and receives it. | **Fix:** return a generic error string to the model and log the full exception server-side.<br>**Repro:** use a tool that raises `RuntimeError("db at 10.0.0.5:5432 refused")` and an `llm` stub that echoes the last tool message as its answer. Expected: no internal address. Observed by trace: the address is returned. | Y/N/Y/N |
| F3 | Medium | CONFIRMED | B | `agent.py:15` | Only the tool result is appended. The model's own tool-call turn is never added, and the result carries no tool name or call id. The model cannot match results to calls. Chat APIs that require a tool result to follow a tool-use turn may reject the history outright (depends on the unsupplied wrapper). | After two different tool calls, the model sees two unlabelled results and calls again. This feeds F1. Alternatively, the provider returns 400 on the second turn and every tool-using request fails. | **Fix:** append the assistant reply (tool name, args, id) before the result, and include the tool name or id in the result message.<br>**Repro:** use an `llm` stub that records `messages`. After one tool call, assert that `messages[-2]` is the assistant tool call. Observed by trace: it is the user question. | Y/Y/N/Y |
| F4 | Low | CONFIRMED | B | `agent.py:17` | `reply["answer"]` assumes the key exists. A reply with neither `tool` nor `answer`, or with `tool: ""`, raises an unhandled `KeyError`. | The model returns a malformed reply and the caller gets a 500 with a possible stack trace, depending on the server. | **Fix:** use `reply.get("answer")`. If it is missing, count the reply as a failed turn under the F1 cap, or return the fallback response.<br>**Repro:** call `run_agent(lambda m: {}, {}, "q")`. Expected: a graceful response. Observed by trace: `KeyError`. | Y/Y/N/N |

**F1 sibling and boundary check**
- Security finding: yes.
- Boundary:
  - Principal: an anonymous internet caller (`agent.py:21`, "no login").
  - Input they control: `question`.
  - Failing control: there is no turn, token or cost cap.
  - Boundary crossed: from the public internet to billed model spend on the company account.
  - Resource affected: the company's model budget and service availability.
- Siblings searched: every loop and retry path in `agent.py`. `run_agent` has the only loop, and `ask_endpoint` adds no limit. The F1 root cause has no other location in the supplied code. Rate limits and body-size limits (S2, S3) may exist upstream, which I could not see.

## Needs validation (no severity)

- **S1:** The question is attacker-controlled and the model chooses tool names and arguments (`agent.py:12`), so prompt injection reaches every tool. *Unresolved fact:* which tools are in `tools`, and whether any can fetch URLs, read files, query internal data or write anything.
- **S2:** `ask_endpoint` (`agent.py:20-22`) shows no per-IP or global rate limit or quota. Even with F1 fixed, many parallel requests multiply spend. *Unresolved fact:* whether the gateway or infrastructure enforces a rate limit and a spend ceiling.
- **S3:** `request["question"]` is passed through with no length check. A very large question is billed on every turn. *Unresolved fact:* the upstream request-body size limit.
- **S4:** No timeouts on `llm()` or the tool calls, so a hung call holds the request open. *Unresolved fact:* whether the wrapper and tools set timeouts.
- **S5:** The model's answer is returned raw. If the client renders it as HTML or markdown, it enables XSS or image-link data exfiltration. *Unresolved fact:* how the /ask response is rendered.

## Refuted

- **"An unknown tool name or non-dict `args` crashes the request."** Refuted: `tools[...]` and `**args` both sit inside the `try` (lines 11-14), so the error is caught. The real effect is that the loop continues, which is covered by F1.
- **"Missing authentication is a defect."** Refuted: the request asks for a *public* endpoint, so having no login is within scope. The cost exposure that follows from it is covered by F1 and S2.

## What holds up

- The basic structure matches the request: the agent uses tools until the model answers, then returns the answer.
- `json.dumps(..., default=str)` will not crash on non-serialisable tool results.
- A failing tool does not crash the request by itself.

## Unverified claims

- **"Retry forever on a tool error"** (docstring) is presented as intended behaviour. It is unsafe for this context and is not a guarantee that the agent works correctly.
- No test evidence was supplied. To confirm, run the four reproductions above in an isolated copy.

## Questions for the author

1. Which tools are registered, and can any of them reach a network, the filesystem or internal data?
2. Is there a gateway rate limit, a body-size limit and a provider-side spend cap?
3. What does the `llm` wrapper expect for tool-call history?

## Decision-maker summary

Do not announce the endpoint until F1 is fixed with turn, token, cost and time caps, and until a rate limit and spend ceiling are confirmed (S2). If it ships as is, any anonymous user can make a single request run model calls indefinitely on the company bill. The remaining findings are smaller and can be fixed in the same change.

## Owner summary

The new question-answering service can be made to keep calling the paid AI model with no stopping point, and anyone on the internet can trigger this. That could run up a large, open-ended bill. Add hard limits on how long and how much each question may cost, plus a cap on how many questions a caller can send, before making it public.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "agent.py", "status": "seen", "matters": true},
    {"item": "llm wrapper implementation", "status": "not_seen", "matters": true},
    {"item": "tools registry and implementations", "status": "not_seen", "matters": true},
    {"item": "server/gateway config (rate limit, body size, spend cap)", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-local", "status": "ran", "cross_vendor": false}],
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
      {"unit": "llm wrapper", "reason": "not_supplied"},
      {"unit": "tools implementations", "reason": "not_supplied"},
      {"unit": "server/gateway config", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:8-16",
     "scenario": "An anonymous caller sends a question that makes the model keep calling tools (or a hallucinated tool name / failing tool keeps the loop going); while True has no turn, token, cost or time cap, so llm() is called without end with a growing context, billed per token to the account.",
     "fix": "Add max_turns, a cumulative token/cost budget and a wall-clock deadline; on hitting any limit, return a fixed 'could not answer' response.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Not executed (no tools). llm = lambda m: {'tool': 'nope'}; tools = {}; run run_agent(llm, tools, 'q') in a thread with a 2s timeout. Expected: returns or raises within N turns. Observed by code trace: never returns.",
     "security": true,
     "boundary": {"principal": "anonymous internet caller (no login, agent.py:21)", "input": "the question field of POST /ask",
                  "control": "no turn, token, cost or time cap in run_agent", "crossed": "public internet to billed model spend",
                  "resource": "the company's model budget and service availability"},
     "siblings_searched": {"searched": "all loops and retry paths in agent.py (run_agent, ask_endpoint)",
                           "found": "run_agent holds the only loop; ask_endpoint adds no cap; no other location in supplied code"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:13-14",
     "scenario": "A tool raises an exception containing an internal host or path; the text goes to the model, and a caller asking to quote the error receives it.",
     "fix": "Return a generic error string to the model; log the full exception server-side.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Not executed. Tool raises RuntimeError('db at 10.0.0.5:5432 refused'); llm stub answers with the last tool message. Expected: no internal address in the answer. Observed by trace: the address is returned."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:15",
     "scenario": "The model's tool-call turn is never appended and results carry no tool name or id; after several calls the model cannot match results and calls again, or a provider that requires a tool-use turn before a tool result rejects the history.",
     "fix": "Append the assistant reply (tool, args, id) before the tool result, and include the tool name or id in the result message.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed. An llm stub records messages; after one tool call assert messages[-2] is the assistant tool call. Observed by trace: messages[-2] is the user question."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:17",
     "scenario": "The model returns a reply with neither 'tool' nor 'answer' (or tool == ''); reply['answer'] raises KeyError and the caller gets a 500.",
     "fix": "Use reply.get('answer'); if missing, count it as a failed turn under the F1 cap or return the fallback response.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed. run_agent(lambda m: {}, {}, 'q'). Expected: graceful response. Observed by trace: KeyError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent.py:12",
     "suspicion": "Attacker-controlled question drives model-chosen tool names and args; prompt injection reaches every registered tool (SSRF, file read, data access, writes).",
     "unresolved_fact": "Which tools are registered in `tools` and what each can reach."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent.py:20-22",
     "suspicion": "No per-caller or global rate limit or quota; parallel requests multiply spend even after F1 is fixed.",
     "unresolved_fact": "Whether the gateway or infrastructure enforces a rate limit and a provider spend ceiling."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent.py:22",
     "suspicion": "Unbounded question length is billed on every turn.",
     "unresolved_fact": "The upstream request-body size limit."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent.py:9,12",
     "suspicion": "No timeouts on llm() or tool calls; a hung call holds the request open.",
     "unresolved_fact": "Whether the llm wrapper and tools set timeouts."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "agent.py:17,22",
     "suspicion": "Raw model output returned to the client could enable XSS or image-link exfiltration if rendered.",
     "unresolved_fact": "How the /ask response is rendered by clients."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "An unknown tool name or non-dict args crashes the request.",
     "evidence": "tools[...] and **args are inside the try at agent.py:11-14; the error is caught and the loop continues (covered by F1)."},
    {"id": "C2", "candidate": "Missing authentication is a defect.",
     "evidence": "The original request asks for a public endpoint; the cost exposure is covered by F1 and S2."}
  ]
}
```