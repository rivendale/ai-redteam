**Same-session review with no tools. Anchoring risk. Re-run in a fresh session, with the code executed, before the announcement.**

The work was not written in this conversation, but no subagent or second seat was available, and nothing could be run. Every claim about execution comes from reading the code.

---

**VERDICT: SHIP WITH FIXES.** The agent loop meets the request and the input, turn and tool-result caps work. But the token cap only checks after each call, model and provider errors escape the error handling, and nothing caps total spend across users. One unanswered question could change this to REJECT: where `request["user"]` comes from.

**CONFIDENCE: medium.** It is limited by:
- no tools: nothing was run, and "6 tests pass" is checked only by tracing the code by hand;
- the HTTP handler, the `llm` wrapper, the tool set and the deployment config were not supplied;
- a same-session reviewer.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `agent.py`, `test_agent.py`.
- **Not seen, and it matters:**
  - The HTTP handler that builds `request`. It decides whether `user` is authenticated or chosen by the caller.
  - The `llm` wrapper. Does it cap output tokens? Does `tokens` include input tokens? Does it raise on provider errors?
  - The `tools` mapping. What can a model-chosen call reach?
  - The deployment config. Is it really one process, and is it threaded?
- **Not seen, matters little:** CI output. The test claim was traced by hand instead.

**COVERAGE**
- **Checked:**
  - `agent.py`: `run_agent` and `ask_endpoint`, line by line.
  - `test_agent.py`: all 6 tests traced by hand. For each guard, I asked whether deleting it would turn a test red.
  - The docstring's claims about its caps.
- **Not checked:** the handler, the `llm` wrapper, the tools, the deployment, and token accounting at the provider.

**SEATS AND GATE:** one same-session reviewer (this one). No cross-vendor seats. The sensitivity gate passed: the work is plain code with no personal data or secrets.

---

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `agent.py` `run_agent`: `reply = llm(messages)` then `spent += …; if spent > MAX_TOKENS_PER_REQUEST` | The token cap is checked only after a call has been made and billed. No output cap is passed to `llm`, and a missing `tokens` key counts as 0. | Turn 1 spends 19,000 tokens. Turn 2's call is still made and billed, at whatever size the wrapper allows, before the check fires. Separately, if the wrapper ever omits `tokens`, `spent` stays 0 and only the 6-turn limit remains. | Pass the remaining budget as `max_tokens` to `llm(messages, max_tokens=MAX_TOKENS_PER_REQUEST - spent)`. Fail closed if `tokens` is missing: `if "tokens" not in reply: raise BudgetExceeded`. **Repro:** `llm` returns `{"tool":"t","tokens":19000}` then `{"tool":"t","tokens":19000}`. Two calls are made; expected is one. | a✓ b✓ c✗ d✗ (depends on the unseen wrapper cap) |
| F2 | Medium | CONFIRMED | B | `run_agent`: `return reply["answer"]`; `ask_endpoint` catches only `BudgetExceeded` | Several things raise uncaught exceptions: a reply with neither a truthy `tool` nor an `answer` (for example `{"tool": ""}`, or a refusal shape); any exception from `llm()` itself (provider 429 or 5xx, timeout); a non-numeric `tokens`; a body missing `question`. All of these bypass the endpoint's error contract. | The provider returns 529 during a busy period. The exception propagates and the caller gets a framework 500, possibly with a traceback if debug is on. The user's rate slot is consumed. | Catch the provider exception types and `KeyError`/`TypeError` around `run_agent`, and return `{"error": "unavailable"}`. Use `reply.get("answer")` and raise a typed error if it is missing. **Repro:** `ask_endpoint({"user":"u","question":"q"}, lambda m: {"tokens":1}, {})`. Expected `{"error": …}`; observed `KeyError: 'answer'`. | a✓ b✓ c✗ d✗ (how often the wrapper raises is unseen) |
| F3 | Medium | CONFIRMED (absence) | A/B | `agent.py` module constants; `ask_endpoint` | Every cap is per request or per user. Nothing bounds total spend per hour or day on a public, per-token-billed endpoint. | An attacker registers N accounts. Spend grows as N × 20 requests per hour × (6 calls each, with no output cap per F1), and no alarm or ceiling stops it. | Add a global spend counter (tokens per hour or day) that refuses requests above a ceiling, plus a billing alert. **Test:** a fake clock and a global ceiling of K tokens; the (K+1)th token's request is refused across distinct users. | a✓ b✓ c✗ d✗ (depends on how cheap signup is; unseen) |
| F4 | Low | CONFIRMED (static mutation reasoning) | B | `test_agent.py`; `agent.py` token check and 3600 s window | Two guards have no test. **Token budget:** the largest cumulative spend in any test is 60 tokens, so deleting the `spent > MAX_TOKENS_PER_REQUEST` check keeps all 6 tests green. **Rate-limit window:** changing `3600` to `float("inf")`, which would lock users out forever, also keeps them green. Every other guard (type check, length check, truncation, login, limit count) would turn a test red if removed. | A later refactor drops the token check or breaks window expiry, and CI stays green. | Add `test_token_budget`, where `llm` returns `tokens: MAX_TOKENS_PER_REQUEST`, asserting an error and exactly one call. Add `test_window_expires`, using the injected `now` to advance 3601 s. Confirm each goes red when its guard is removed. | a✓ b✓ c✗ d✗ |

### NEEDS VALIDATION

- **S1. Is the user identity supplied by the caller?** `ask_endpoint` reads `request.get("user")` from the same dict as `request["question"]`. This would be Critical if the handler builds `request` from the JSON body. In that case any anonymous caller sets `"user": "<random>"` and bypasses both the login check and the rate limit, giving unlimited billed calls. *Fact that settles it:* the handler code showing where `user` is filled in (it should come from the verified session or token, never from the body).
- **S2. Is the rate limiter correct under the real deployment?** `_seen` is per process, and the check-then-set has no lock. *Fact that settles it:* the worker count and threading model. Multiple workers multiply the limit, restarts reset it, and concurrent requests from one user can all pass the check.
- **S3. What can the tools reach?** A public user's question steers which tools are called and with what arguments, and tool output (for example fetched web pages) can inject instructions. *Fact that settles it:* the tool list and each tool's side effects and reach (network, file system, internal APIs).
- **S4. Do tool errors leak internal details?** `f"error: {exc}"` puts raw exception text into the model's context, and the model may repeat it to the public user. *Fact that settles it:* whether any tool's exceptions contain paths, hostnames or connection strings.
- **S5. Does the wrapper accept this message shape?** The assistant `tool_call` and `role: "tool"` messages carry no call ID, and no tool schemas are passed to `llm`. *Fact that settles it:* the wrapper's translation to the provider API, since real tool-use APIs require matching IDs.
- **S6. What does `tokens` count?** Input tokens are re-sent every turn. *Fact that settles it:* whether `tokens` includes input tokens. If it counts only output, the budget understates the real bill. That said, re-sent context is bounded: roughly 2,000 + 5 × 4,000 characters.

### REFUTED

- **R1. An unknown tool name or malformed `args` crashes the agent.** Refuted: `tools[reply["tool"]](**…)` sits inside the `try`. The `KeyError` or `TypeError` becomes an `error:` tool result.
- **R2. An oversized question uses a model call.** Refuted: the length and type checks run before `llm`. Tests 2 and 3 trace correctly.
- **R3. The test-4 aliasing hides a bug.** `seen[0]` and `seen[1]` are the same list object. But no message is appended after the final call, so `seen[1][-1]` is still the tool message. The test checks what it claims.

---

**WHAT HOLDS UP**
- The loop does what was asked: it calls tools until the model answers, then returns the answer.
- The turn cap is real. The test would go red if it were removed: the loop would end only at about 2,000 calls through the token cap.
- Question type and length checks happen before any spend.
- Tool results are truncated after serialization, which bounds context growth.
- Tool exceptions are contained.
- The rate-limit count logic is correct for a single-threaded, single process.
- The 6 tests, traced by hand, should pass in their alphabetical run order.

**UNVERIFIED CLAIMS**
- **"6 tests pass."** Hand-traced only. Confirm with `python -m unittest test_agent -v`.
- **"One process serves the endpoint."** Confirm against the deploy config.
- **"Signed-in users only."** Confirm in the handler (S1).
- **"Token caps."** The cap is enforced only after each call (F1). Confirm the wrapper's `max_tokens`.

**QUESTIONS FOR THE AUTHOR**
1. Where does `request["user"]` come from? Is it the verified session or the request body?
2. Does the `llm` wrapper set an output-token cap? Does its `tokens` include input tokens?
3. How many workers or threads serve `/ask`, and can anyone create an account for free?

**DECISION-MAKER SUMMARY:** Do not announce until question 1 is answered. If the user identity comes from the request body, anyone can run unlimited billed queries. Otherwise, fix the post-call token check, the uncaught provider errors and the missing global spend ceiling (F1 to F3) before launch. Proceeding as is risks an open-ended model bill from a handful of free accounts.

**OWNER SUMMARY:** The research assistant works, and most of its limits are sound. But it has no overall ceiling on what it can cost us, and one of its spending limits only kicks in after the money is already spent. Before announcing it, we need to confirm that sign-in can't be faked, add a total spending cap, and make sure outages show users a clean error.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "agent.py", "status": "seen", "matters": true},
    {"item": "test_agent.py", "status": "seen", "matters": true},
    {"item": "HTTP handler that builds request", "status": "not_seen", "matters": true},
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "tools mapping", "status": "not_seen", "matters": true},
    {"item": "deployment config", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "code only; no personal data or secrets"},
  "coverage": {
    "checked": [
      {"unit": "agent.py", "kind": "file"},
      {"unit": "agent.py:run_agent", "kind": "function"},
      {"unit": "agent.py:ask_endpoint", "kind": "function"},
      {"unit": "test_agent.py", "kind": "file"},
      {"unit": "docstring caps claims", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "HTTP handler", "reason": "not supplied"},
      {"unit": "llm wrapper", "reason": "not supplied"},
      {"unit": "tools", "reason": "not supplied"},
      {"unit": "deployment config", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:run_agent (reply = llm(messages); spent += reply.get('tokens', 0))",
     "scenario": "Turn 1 spends 19000 tokens; turn 2's call is still made and billed before the check fires; a missing tokens key counts as 0 so the cap never fires.",
     "fix": "Pass remaining budget as max_tokens to llm; fail closed when tokens is missing.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "llm returns {'tool':'t','tokens':19000} twice; observe 2 calls, expect 1."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:run_agent return reply['answer']; ask_endpoint except BudgetExceeded only",
     "scenario": "Provider error, reply without tool or answer, non-numeric tokens or missing question raises uncaught; caller gets a 500 (possible traceback) and loses a rate slot.",
     "fix": "Catch provider and KeyError/TypeError around run_agent and return a structured error; use reply.get('answer').",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "ask_endpoint({'user':'u','question':'q'}, lambda m: {'tokens':1}, {}) raises KeyError: 'answer'; expected {'error': ...}."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "agent.py module constants and ask_endpoint",
     "scenario": "Attacker creates N accounts; spend scales as N x 20 requests/hour with no global ceiling on a per-token-billed public endpoint.",
     "fix": "Add a global hourly/daily token ceiling and a billing alert.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "With fake clock and global ceiling K, requests from distinct users past K tokens should be refused; currently none are."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_agent.py; agent.py token check and 3600s window",
     "scenario": "Deleting the token-budget check or making the window infinite leaves all 6 tests green, so a regression ships unnoticed.",
     "fix": "Add test_token_budget and test_window_expires; confirm each goes red when its guard is removed.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Remove 'if spent > MAX_TOKENS_PER_REQUEST' and run the suite: all pass (static trace)."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent.py:ask_endpoint request.get('user')",
     "suspicion": "If user comes from the request body, anonymous callers bypass login and rate limit by choosing any user string (would be Critical).",
     "unresolved_fact": "Where the HTTP handler populates request['user'] (verified session vs body)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent.py:_seen",
     "suspicion": "Per-process, unlocked rate limiter is multiplied by workers, reset on restart, and racy under threads.",
     "unresolved_fact": "Worker count and threading model of the deployment."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent.py:run_agent tools[reply['tool']](**args)",
     "suspicion": "Public user or injected tool output steers tool calls with side effects.",
     "unresolved_fact": "The tool list and each tool's reach and side effects."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent.py:run_agent f'error: {exc}'",
     "suspicion": "Raw exception text may leak internal details into the public answer.",
     "unresolved_fact": "Whether tool exceptions include paths, hosts or connection strings."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "agent.py:run_agent message construction",
     "suspicion": "Tool messages lack call IDs and no tool schemas are passed to llm.",
     "unresolved_fact": "How the llm wrapper maps these messages to the provider API."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "agent.py:run_agent reply.get('tokens')",
     "suspicion": "Budget may count only output tokens while input is re-sent every turn.",
     "unresolved_fact": "Whether the wrapper's tokens field includes input tokens."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Unknown tool name or malformed args crashes the agent.",
     "evidence": "The tool dispatch is inside try/except Exception; the error becomes a tool result."},
    {"id": "R2", "candidate": "Oversized or non-text question spends a model call.",
     "evidence": "isinstance and length checks precede llm(); tests 2 and 3 trace correctly."},
    {"id": "R3", "candidate": "Test 4's list aliasing hides a bug.",
     "evidence": "No message is appended after the final call, so seen[1][-1] is the tool message."}
  ]
}
```