VERDICT: SHIP WITH FIXES. The caps are mostly sound, but the tool-call history is malformed, so the core "answer with the routing tool" path is probably broken and is never tested. Rider identity also comes from the same dict as the client's question.

CONFIDENCE: medium. I had no tools, so nothing was run; every test result below comes from tracing the code by hand. The HTTP glue that builds `request` and the real `llm` wrapper were not supplied, and both carry weight.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `planner.py`, `test_planner.py`.
- Not seen:
  - The HTTP layer that builds `request`. **This matters for F1**: it decides whether `rider` comes from the session or from the client.
  - The `llm` wrapper and the provider message format. **This matters for F2 and S1**.
  - The routing tool. This matters for S2.
  - The front-end rendering of `answer`. This matters for S3.
  - Deployment topology (worker count). This matters for F3.
  - The test run output. "9 tests pass" is UNVERIFIED, though my trace says each of the 9 would pass.
- Independence: the work was not authored in this conversation. This is a single local review with no subagent.

COVERAGE:
- Scope: the whole work, both files.
- Checked: `request.md`, `context.md`, `planner.py` (`_run`, `plan`, the constants and globals), and `test_planner.py` (all 9 tests).
- Not checked: the HTTP glue, the llm wrapper, the routing tool and the front end. None were supplied.

SEATS AND GATE: local reviewer only. No cross-vendor seats were requested or available. Sensitivity gate passed (no personal or confidential data).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | PROBABLE | B | planner.py:47-49, 57 | `rider` is read from the same `request` dict as the client's `question`, with no session lookup. "Signed-in riders only" holds only if the glue overwrites `rider` from the session. | An anonymous client POSTs `{"rider":"x1","question":...}` and rotates `x1…x67`. This gets past login and the 30/h per-rider cap. It spends the full 2000/h global budget (~30M output tokens/h at 15k each, billed to Pedalo) and locks every real rider out with "busy". | Derive `rider` from the authenticated session in `plan`, or assert the glue does. Never take it from the body. Repro: send POST /plan with a body `rider` and no session cookie; expect 401, but per `plan` you get an answer. | a✓ b✗ c✓ d✓ |
| F2 | High | CONFIRMED (defect) / PROBABLE (impact) | B | planner.py:32-38 | On a tool call, only the tool result is appended. The model's own tool request (name, args, call id) is never added to `messages`. | The model calls the routing tool and the next turn sees a bare `role:"tool"` message. Chat APIs require a preceding assistant tool call with a matching id, so they reject this with a 400, and every routing question becomes a 500. A lenient wrapper avoids the 400, but the model still can't tell what the result answers, re-requests it, and hits "turn limit". The original request's core path fails either way. | Append the assistant turn (tool name, args, call id) before the tool result, and pass the id on the result. Repro test: fake llm returns `{"tool":"route","args":{"a":"A","b":"B"},"tokens":5}`, then on turn 2 asserts `messages[1]` is that assistant call. It fails today. No existing test covers tool-then-answer. | a✓ b✓ c✓ d✓ |
| F3 | Medium | PROBABLE | B | planner.py:11-13, 50-58 | Rate and global counters are per-process in-memory lists. | With N workers or replicas, limits become 30·N per rider and 2000·N global, and they reset on every deploy or restart. The billing cap is not what the constants say. | Move the counters to a shared store (e.g. Redis INCR with TTL). Repro: two processes, 30 requests each for one rider; the 31st in the second process succeeds. | a✓ b✗ c✗ d✓ |
| F4 | Medium | CONFIRMED | B | test_planner.py:38-41; planner.py:26, 30 | The tests never exercise a multi-turn budget or the over-budget branch. | Two mutations each leave all 9 tests green by trace: changing `MAX_TOKENS - spent` to `MAX_TOKENS`, and deleting lines 30-31. The never-stop test spends only 50 tokens. A regression that removes the spend cap ships unnoticed. | Add tests: (1) a tool reply with `tokens=10000`, then assert the second call gets `max_tokens=5000`; (2) a second reply of 6000 tokens must produce "token budget". Repro: apply either mutation and run the suite; it stays green. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED | B | planner.py:26, 30 | If `spent == MAX_TOKENS` exactly, the check `>` passes and the next call is made with `max_tokens=0`. Exceptions from `llm` are not caught anywhere. | A tool turn costs exactly the remaining budget. The next call sends `max_tokens=0`, the provider rejects it, and the exception escapes `plan`: a 500 instead of "token budget". | Use `>=`, or stop when the remaining budget is ≤ 0. Repro: fake llm returns a tool reply with tokens=15000 and records `max_tokens`; it observes 0. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED | B | planner.py:57 | `_seen` keys are never evicted. A rider's list is pruned only when that rider returns. | Over months, every rider ever seen stays in memory (much worse if F1 holds: unbounded keys from the client). | Periodically drop keys with no hits in the last hour. Repro: 100k distinct riders, then check `len(_seen)`. It stays at 100k. | a✓ b✓ c✗ d✗ |

F1 security boundary:
- Principal: an anonymous or any client.
- Input: the body field `rider`.
- Control that fails: the login and per-rider checks trust that field.
- Boundary crossed: anonymous to signed-in.
- Resource: Pedalo's model budget and service availability.

Sibling search, all by reading:
- F1: other identity reads in `plan`. Only line 47.
- F2: other places messages are built. Only lines 23 and 37. The missing call id is the same root cause and is part of F2.

NEEDS VALIDATION:
- S1: Do the reported `tokens` include input tokens? Each turn re-sends the question plus up to 5×4000 chars of tool output. Settled by the llm wrapper's definition of `tokens`.
- S2: `f"error: {exc}"` (line 36) feeds raw tool exception text to the model, and the model can repeat it to the rider. Many HTTP clients put the URL, including `?key=…`, in the message. Settled by the routing tool's error format.
- S3: Is `answer` rendered as HTML or markdown on the rider site? If so, model output is untrusted (XSS, or image-link exfiltration). Settled by the front-end code.

REFUTED:
- "An unknown tool name or bad args crashes the request." `KeyError` and `TypeError` are caught at line 35 and returned to the model.
- "Concurrency race on the counters." All reads and writes are under `_lock`.
- "The global-ceiling test leaks state." The `finally` block restores the constant, and `setUp` clears the lists.

## Assessment

WHAT HOLDS UP:
- The question type and length check runs before any model call.
- The turn cap holds.
- The remaining budget is passed to the first call.
- A reply missing `tokens` or `answer` is refused.
- Tool output is truncated to 4000 chars.
- The per-rider and global checks are atomic under the lock.
- All 9 tests trace as passing.

UNVERIFIED CLAIMS: "9 tests pass". Confirm by running `python -m unittest test_planner` in an isolated copy.

QUESTIONS FOR THE AUTHOR:
1. Where does `request["rider"]` come from: the session or the body?
2. What message format does the `llm` wrapper expect for tool calls and results?
3. How many workers or replicas serve /plan?

DECISION-MAKER SUMMARY: Before launch, fix the tool-call history (F2) and confirm rider identity comes from the session (F1). Both are small changes, and both need a test. If you launch as is, routing answers will likely fail outright, and if `rider` is client-supplied, anyone can burn the hourly model budget and lock out real riders.

OWNER SUMMARY: The trip planner has sensible spending limits, but the part where it asks the routing tool for directions is probably broken and has never been tested. It is also unclear whether the "logged-in riders only" check can be faked, which would let anyone run up the bill and block real riders. Both are quick fixes and should be done before launch.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "planner.py", "status": "seen", "matters": true},
    {"item": "test_planner.py", "status": "seen", "matters": true},
    {"item": "HTTP glue building request", "status": "not_seen", "matters": true},
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "routing tool", "status": "not_seen", "matters": true},
    {"item": "front-end rendering", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"}, {"unit": "context.md", "kind": "document"},
      {"unit": "planner.py", "kind": "file"}, {"unit": "planner.py:_run", "kind": "function"},
      {"unit": "planner.py:plan", "kind": "function"}, {"unit": "test_planner.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "HTTP glue", "reason": "not_supplied"}, {"unit": "llm wrapper", "reason": "not_supplied"},
      {"unit": "routing tool", "reason": "not_supplied"}, {"unit": "front end", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:47-49,57",
     "scenario": "An anonymous client sets rider in the POST body and rotates values. Login and the 30/h per-rider cap are bypassed, the 2000/h global budget (~30M tokens/h) is consumed, and real riders get 'busy'.",
     "fix": "Derive rider from the authenticated session, never from the request body.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "POST /plan with body {\"rider\":\"x1\",\"question\":\"A to B\"} and no session; expect 401, observe an answer.",
     "security": true,
     "boundary": {"principal": "anonymous client", "input": "request body field rider",
                  "control": "login and per-rider limit trust the client-supplied rider",
                  "crossed": "anonymous to signed-in rider", "resource": "Pedalo model budget and service availability"},
     "siblings_searched": {"searched": "all identity reads in plan and _run", "found": "only planner.py:47"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:32-38",
     "scenario": "The model calls the routing tool. Only the tool result is appended, without the assistant tool call or call id, so the provider rejects the next request or the model loops to 'turn limit'. Routing questions fail.",
     "fix": "Append the assistant tool-call turn (name, args, id) before the tool result and reference the id in the result; add a tool-then-answer test.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Fake llm: turn 1 returns {\"tool\":\"route\",\"args\":{},\"tokens\":5}; turn 2 asserts messages[1] is the assistant tool call. It fails: messages[1] is the bare tool result.",
     "security": false,
     "siblings_searched": {"searched": "every place messages is built (lines 23, 37)", "found": "missing call id is the same root cause, included here"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:11-13,50-58",
     "scenario": "With N workers, the per-rider and global caps multiply by N and reset on restart, so billing exceeds the stated cap.",
     "fix": "Keep counters in a shared store such as Redis with TTL.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Run two processes, send 30 requests per process for one rider; the 31st overall succeeds."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_planner.py:38-41; planner.py:26,30",
     "scenario": "Changing MAX_TOKENS - spent to MAX_TOKENS, or deleting the spent > MAX_TOKENS check, leaves all 9 tests green by trace, so the spend cap can regress unnoticed.",
     "fix": "Add multi-turn budget tests: assert the second call gets the remaining budget and that an overspend returns 'token budget'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Apply either mutation to planner.py in a scratch copy and run the suite; all 9 tests still pass."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:26,30",
     "scenario": "When spent equals MAX_TOKENS, the loop calls llm with max_tokens=0; the provider error escapes plan as a 500.",
     "fix": "Use >= or stop when the remaining budget is <= 0.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Fake llm returns a tool reply with tokens=15000 and records max_tokens on the next call; it observes 0."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:57",
     "scenario": "_seen keeps every rider key forever, so memory grows without bound, faster if rider is client-supplied.",
     "fix": "Evict keys with no hits in the last hour.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call plan with 100k distinct riders, then check len(_seen); expect pruning, observe 100k."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "planner.py:26-30",
     "suspicion": "The token cap may not cover input tokens, which are re-sent each turn.",
     "unresolved_fact": "Whether the llm wrapper's tokens field includes input tokens."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "planner.py:36",
     "suspicion": "Raw tool exception text, possibly containing API keys in URLs, reaches the model and can be relayed to the rider.",
     "unresolved_fact": "The routing tool's exception message format."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "planner.py:60",
     "suspicion": "Model answer may be rendered as HTML or markdown, enabling XSS or image-link exfiltration.",
     "unresolved_fact": "How the rider site renders the answer."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "An unknown tool name or bad args crashes the request.", "evidence": "KeyError and TypeError are caught at planner.py:35."},
    {"id": "R2", "candidate": "Race on the rate counters.", "evidence": "All reads and writes happen under _lock (lines 50-58)."},
    {"id": "R3", "candidate": "The global-ceiling test leaks state.", "evidence": "finally restores the constant; setUp clears the lists."}
  ]
}
```