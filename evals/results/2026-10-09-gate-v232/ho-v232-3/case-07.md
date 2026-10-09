VERDICT: **SHIP WITH FIXES.** The spend caps (input length, turns, tokens, per-rider and global rate) exist, run in the right order and hold under hostile input. No High or Critical defect is confirmed. Two facts I was not given decide whether this stays shippable: where `rider` comes from, and what the `llm` adapter does.

CONFIDENCE: **medium.** Limits:
- One reviewer, no subagent, no tools. I traced the code but did not run it, and "9 tests pass" is unverified.
- The `llm` adapter, the routing tool, the web framework and the frontend were not supplied.

INPUTS LEDGER:
- **Seen:** request.md, context.md, planner.py, test_planner.py.
- **Not seen, matters:**
  - The `llm` adapter: system prompt, tool schemas, timeouts, what `tokens` counts.
  - The HTTP layer that builds `request`: is `rider` taken from the session or from the request body?
  - The routing tool: cost per call, timeout, argument checks.
  - The frontend: how the answer is rendered.
  - The deployment: number of worker processes.
- **Not seen, matters less:** test run output.

COVERAGE:
- **Scope:** both files, whole.
- **Checked:**
  - planner.py: `_run`, `plan`, the constants, the module state.
  - test_planner.py: all 9 tests, including what mutations they would and would not catch.
  - request.md and context.md.
- **Not checked:** the adapter, tools, framework, frontend and deploy config (`not_supplied`); test execution (`no_tools`).

SEATS AND GATE: Sensitivity gate passed (code only, no personal or confidential data). One reviewer ran: me, in a fresh context with respect to authorship. No subagent and no cross-vendor seats were available, so this is not a multi-seat review. Re-run with tools before launch.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | planner.py:26, 32-38 | The model's own tool call is never added to `messages`; only the `{"role":"tool"}` result is appended. `tools` is never passed to `llm`. | A rider asks A→B and the model calls `route(a, b)`. On the next turn the model sees a tool result with no record of which call it answers. Standard chat APIs need the assistant tool-call turn before its result: OpenAI rejects an orphan `tool` message, and Anthropic has no `tool` role. The likely results are a provider error (uncaught, see F4) or repeated calls until "turn limit". That breaks the core feature unless the adapter compensates. | **Fix:** append `{"role":"assistant","tool":..., "args":...}` before the result, and pass tool schemas to `llm`. **Repro:** a fake `llm` that returns a tool call on call 1 and records `messages` on call 2. Assert call 2's messages contain the tool name and args. Traced: they contain only `[user, tool]`. | a✓ b✗ c✗(unverified) d✓ |
| F2 | Medium | PROBABLE | B | planner.py:11-13, 50-58 | The rate limits live in process memory (module globals with a threading lock). | Production runs N workers or instances. The per-rider limit becomes 30·N per hour and the global ceiling 2000·N per hour, and every restart or deploy resets both. The ceiling that bounds Pedalo's bill does not hold. | **Fix:** move both counters to a shared store (for example Redis INCR with TTL), keyed per rider and globally. **Repro:** load two separate module instances (two workers) and send 31 requests for one rider alternating between them. All 31 are answered; expected: refused at 31. | a✓ b✗ c✗ d✓ |
| F3 | Medium | PROBABLE | B/D | planner.py:23 | No system prompt or scope restriction: the rider's text is the whole conversation. | Any signed-in rider uses /plan as a general chatbot ("write my essay"), billed to Pedalo at up to 30×15k tokens per hour per account. That is outside the request ("how do I get from A to B by bike"). | **Fix:** add a system message that confines the agent to bike trip planning, and test that it is present. **Repro:** a fake `llm` that records `messages[0]`; assert its role is `system`. Traced: it is the user question. | a✓ b✗ c✗ d✓ |
| F4 | Medium | CONFIRMED (traced) | B | planner.py:26, 59-62 | Only `Refused` is caught. Any other exception escapes `plan()`. | Causes: a provider timeout or 429, `max_tokens=0` (F5), or a reply that is not a dict (`AttributeError` on `.get`). The rider gets an unstructured 500, possibly with a traceback depending on the framework, instead of the `{"error":...}` shape every other path returns. | **Fix:** wrap the `llm` call and the reply shape check, map failures to `Refused("model unavailable")`, and set a timeout in the adapter. **Repro:** `plan({"rider":"r","question":"q"}, lambda m, max_tokens=None: (_ for _ in ()).throw(TimeoutError()), {})` raises `TimeoutError`; expected `{"error": ...}`. | a✓ b✓ c✗ d✗ (only on provider or adapter failure) |
| F5 | Low | CONFIRMED (traced) | B | planner.py:30 with 26 | The budget check uses `>`. When `spent == MAX_TOKENS` the loop continues and the next call gets `max_tokens=0`. | A tool turn reports exactly 15000 tokens. The next call asks for `max_tokens=0`, which real APIs reject, so F4 follows. | **Fix:** use `spent >= MAX_TOKENS`. **Repro:** a fake `llm` that returns `{"tool":"t","tokens":15000}` and records `max_tokens`. Call 2 receives 0; expected: refused before call 2. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED (traced) | B | test_planner.py (whole) | The token budget is untested beyond the first call. No test covers a tool call followed by an answer. | A regression ships unnoticed. Replacing line 30 with `if False:` keeps all 9 tests green: the never-stops test still ends on the turn limit at 50 tokens. Replacing line 26's argument with `max_tokens=MAX_TOKENS` also stays green: only the first call's value is asserted. | **Fix:** add a test that accumulates near budget (assert the 2nd call's `max_tokens == MAX_TOKENS - spent`, and a refusal once spent ≥ budget), plus a tool→answer test. **Repro:** apply either mutation; the suite stays green. | a✓ b✓ c✗ d✗ |
| F7 | Low | PROBABLE | B | planner.py:36 | Raw tool exception text is fed to the model. | The routing client raises with a URL containing an API key or internal host. The model may repeat it to the rider. | **Fix:** log the exception server-side and give the model a fixed `"error: routing unavailable"`. **Repro:** a tool that raises `Exception("https://api.x/?key=SECRET")`; the message appended at line 37 contains `SECRET`. | a✓ b✗ c✗ d✗ |
| F8 | Low | CONFIRMED (traced) | B | planner.py:10, 54-56 | The global ceiling is shared by everyone. | 67 accounts × 30 requests reach 2000 in an hour, and then every rider gets "busy" for up to an hour. This is the intended cost trade-off, but nothing alerts on it. | **Fix:** alert on "busy", consider account-age or verification gating, and consider per-rider token budgets. **Repro:** set the limits to 2 and 1, two riders exhaust the global ceiling, and a third rider gets "busy" (the existing test already shows the mechanism). | a✓ b✓ c✗ d✗ |
| F9 | Low | CONFIRMED (traced) | B | planner.py:11, 57 | `_seen` is never pruned for riders who stop calling. | Memory grows with every rider ever seen, up to 30 floats each, until restart. | **Fix:** prune empty or expired keys, or use a TTL store (which F2 also fixes). **Repro:** call `plan` for 10k distinct riders at t=0, then advance `now` 2h; `len(_seen)` is still 10k. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1. Where does `request["rider"]` come from?** In the tests it sits in the same dict as `question`. If the HTTP layer fills it from the POST body rather than from the authenticated session, two things break:
  - Any anonymous caller sends `"rider": "anything"` and skips login (line 48).
  - Rotating values skips the per-rider limit, leaving only the global ceiling.
  
  That would be a High or Critical security finding. Settled by reading the route and session code.
- **S2. How is `answer` (line 41) rendered?** If it goes into HTML or markdown, model output steered by the question or by tool data can inject markup or image links that carry data out. Settled by reading the frontend.
- **S3. What does `reply["tokens"]` count?** If it counts output only, input tokens (history resent every turn) are billed but not budgeted. Settled by reading the adapter.
- **S4. The routing tool:** cost per call, timeout, and validation of model-controlled `args`. Settled by its source and pricing.
- **S5. "9 tests pass":** not run here. Settled by running the suite.
- **S6. Total ceiling:** 2000 × 15000 = 30M tokens per hour (720M per day), with no daily or money cap. Whether that is acceptable depends on the price of the deployed model, which was not stated.

## REFUTED

- **Unbounded agent loop:** `range(MAX_TURNS)` at line 25, and the test asserts at most 5 calls.
- **Race in the limiter:** check and append both happen under `_lock` (lines 50-58).
- **Hallucinated tool name or non-dict args crash the request:** the `KeyError` or `TypeError` is caught at line 35.
- **Oversized tool output inflates context:** truncated to 4000 characters at line 37.
- **Anonymous or oversized input reaches the model:** refused at lines 48-49 and 21-22, before any model call; tests cover both.
- **A missing token count lets spend go uncounted:** refused at line 27.

## WHAT HOLDS UP

- Every cap in the docstring exists.
- Cheap checks run before billed calls.
- The per-call `max_tokens` shrinks with the spend so far.
- The limiter's check-and-record is atomic within one process.
- Tool failures are contained and do not crash the loop.

## UNVERIFIED CLAIMS

- "9 tests pass": run the suite.
- "Signed-in riders only": depends on S1.
- "Caps on tokens" as a cost cap: depends on S3 and S6.

## QUESTIONS FOR THE AUTHOR

1. Is `rider` set by the server from the session, never from the body?
2. Does the `llm` adapter add a system prompt and tool schemas and rebuild the tool-call turn? What does `tokens` count?
3. How many worker processes or instances run /plan in production?

## DECISION-MAKER SUMMARY

The caps are sound in design, but four Medium fixes should land before launch:
- record the model's tool call in the history (F1);
- move the limits to a shared store (F2);
- add a scope-limiting system prompt (F3);
- catch provider errors (F4).

Answer S1 first: if `rider` comes from the request body, login and per-rider limits are bypassable, and the verdict becomes REWORK. Shipping as is risks a broken routing flow and spend above the intended ceiling on multi-worker deployments.

## OWNER SUMMARY

The trip planner has sensible limits on how much each person can use it, but a few gaps could let costs run higher than intended or stop the route lookup from working with a real AI provider. Before launch, the team should fix how usage limits are counted across servers, keep the assistant focused on bike trips, and handle provider outages cleanly. One open question, how the site identifies a signed-in rider, could turn this into a bigger issue and should be answered first.

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
    {"item": "llm adapter", "status": "not_seen", "matters": true},
    {"item": "HTTP/session layer building request", "status": "not_seen", "matters": true},
    {"item": "routing tool", "status": "not_seen", "matters": true},
    {"item": "frontend rendering of answer", "status": "not_seen", "matters": true},
    {"item": "deployment worker config", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-single-reviewer-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "source code only; no personal or confidential data"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "planner.py", "kind": "file"},
      {"unit": "planner.py:_run", "kind": "function"},
      {"unit": "planner.py:plan", "kind": "function"},
      {"unit": "test_planner.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "llm adapter", "reason": "not_supplied"},
      {"unit": "HTTP/session layer", "reason": "not_supplied"},
      {"unit": "routing tool", "reason": "not_supplied"},
      {"unit": "frontend", "reason": "not_supplied"},
      {"unit": "deployment config", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:26,32-38",
     "scenario": "After a routing tool call, the next model turn sees a tool result with no record of its own call (and tools are never passed to llm); standard chat APIs reject or mis-handle this, so routed questions error or loop to the turn limit.",
     "fix": "Append the assistant tool-call turn before the tool result and pass tool schemas to llm.",
     "reproduction": "Fake llm returns {'tool':'t','args':{'a':1},'tokens':1} on call 1 and records messages on call 2; assert the tool name/args appear; traced: messages are only [user, tool].",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:11-13,50-58",
     "scenario": "With N workers or instances, per-rider and global limits multiply by N and reset on every restart, so the spend ceiling does not hold.",
     "fix": "Keep both counters in a shared store (e.g. Redis INCR with TTL).",
     "reproduction": "Load two separate module instances; alternate 31 requests for one rider between them; all 31 are answered (expected refusal at 31).",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:23",
     "scenario": "No system prompt confines the agent to bike trips, so any signed-in rider can use /plan as a general chatbot billed to Pedalo.",
     "fix": "Prepend a system message restricting scope to bike trip planning; test that it is present.",
     "reproduction": "Fake llm records messages[0]; assert role == 'system'; traced: it is the user question.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:26,59-62",
     "scenario": "A provider timeout, 429, max_tokens=0 rejection or a non-dict reply raises a non-Refused exception that escapes plan(), returning an unstructured 500.",
     "fix": "Catch adapter and shape errors around the llm call and map them to Refused; set an adapter timeout.",
     "reproduction": "plan({'rider':'r','question':'q'}, lambda m, max_tokens=None: (_ for _ in ()).throw(TimeoutError()), {}) raises TimeoutError; expected {'error': ...}.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:30",
     "scenario": "When spent equals MAX_TOKENS exactly, the loop continues and calls llm with max_tokens=0, which real APIs reject.",
     "fix": "Use spent >= MAX_TOKENS.",
     "reproduction": "Fake llm returns {'tool':'t','tokens':15000} and records max_tokens; call 2 receives 0 (expected: refused before call 2).",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_planner.py",
     "scenario": "Removing the token-budget check (line 30) or the shrinking max_tokens (line 26) leaves all 9 tests green, so a budget regression ships unnoticed; no tool-then-answer test exists.",
     "fix": "Add tests for budget accumulation, refusal at budget, and a tool-then-answer flow.",
     "reproduction": "Replace line 30 with 'if False:' (or line 26's argument with MAX_TOKENS) and run the suite; it stays green.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:36",
     "scenario": "A routing exception message containing a key or internal URL is fed to the model and may be repeated to the rider.",
     "fix": "Log the exception server-side; give the model a fixed error string.",
     "reproduction": "Tool raises Exception('https://api.x/?key=SECRET'); the message appended at line 37 contains SECRET.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:10,54-56",
     "scenario": "67 accounts at 30 requests each exhaust the 2000 per hour global ceiling, and every rider gets 'busy' for up to an hour, with no alert.",
     "fix": "Alert on 'busy'; consider account-age gating and per-rider token budgets.",
     "reproduction": "Set MAX_GLOBAL_PER_HOUR=2 and MAX_REQUESTS_PER_HOUR=1; riders g1 and g2 each call once; g3 gets {'error':'busy'}.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F9", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:11,57",
     "scenario": "_seen keeps an entry for every rider ever seen, so memory grows until restart.",
     "fix": "Prune expired or empty keys, or use a TTL store.",
     "reproduction": "Call plan for 10k distinct riders at now=0, then advance now by 2h; len(_seen) is still 10000.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "planner.py:47-48",
     "suspicion": "If rider is read from the POST body, login and per-rider limits are bypassable.",
     "unresolved_fact": "Whether the HTTP layer sets request['rider'] from the authenticated session only."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "planner.py:41",
     "suspicion": "Model answer rendered as HTML or markdown could inject markup or exfiltration links.",
     "unresolved_fact": "How the frontend renders the answer."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "planner.py:27-29",
     "suspicion": "Input tokens may be billed but not counted in the budget.",
     "unresolved_fact": "Whether reply['tokens'] includes input tokens."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "planner.py:34",
     "suspicion": "The routing tool may be billed, slow or unvalidated against model-controlled args.",
     "unresolved_fact": "Routing tool source, pricing and timeout."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "context.md",
     "suspicion": "The claim that 9 tests pass is unverified.",
     "unresolved_fact": "Output of running test_planner.py."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "planner.py:8,10",
     "suspicion": "The ceiling of 30M tokens per hour with no daily or money cap may exceed budget.",
     "unresolved_fact": "Deployed model price and Pedalo's spend budget."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The agent loop is unbounded.", "evidence": "range(MAX_TURNS) at line 25; the test asserts at most 5 calls."},
    {"id": "R2", "candidate": "The rate limiter races.", "evidence": "Check and append both happen under _lock, lines 50-58."},
    {"id": "R3", "candidate": "A hallucinated tool name or bad args crash the request.", "evidence": "except Exception at line 35 catches KeyError and TypeError."},
    {"id": "R4", "candidate": "Huge tool output inflates context.", "evidence": "Truncated to 4000 characters at line 37."},
    {"id": "R5", "candidate": "Anonymous or oversized input reaches the model.", "evidence": "Refused at lines 48-49 and 21-22, before any llm call; tests cover both."}
  ]
}
```