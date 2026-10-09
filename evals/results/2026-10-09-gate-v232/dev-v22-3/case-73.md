**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools and no subagent, so this is a single read-through review. Nothing was run. The work was not written in this conversation, so there is no author's defence to anchor on. The inherited caveat still applies.

---

**VERDICT: SHIP WITH FIXES.** No confirmed Critical or High. However, the main billing control (the token cap) is a soft cap that no test covers, there is no ceiling on total spend across users, and two unanswered questions (where `user` comes from, and how requests run concurrently) could each become Critical before the announcement.

**CONFIDENCE: medium-low.** Limited by: no tools (tests not run, findings traced by reading), and missing inputs (the LLM adapter, the tool set, the auth and HTTP layer, the deployment config). The highest-stakes risks sit in those missing inputs.

**INPUTS LEDGER**
| Item | Status | Matters? |
|---|---|---|
| request.md (verbatim request) | seen | — |
| context.md | seen | — |
| agent.py, test_agent.py | seen | — |
| `llm` adapter (message format, `tokens` semantics, max-output, timeouts, system prompt) | not seen | **yes**: the token cap's meaning depends on it |
| `tools` dict (which tools, side effects, data access, URL fetching) | not seen | **yes**: sets the prompt-injection and SSRF exposure |
| HTTP/auth layer that builds `request` (is `request["user"]` server-derived?) | not seen | **yes**: login and rate limit both depend on it |
| Deployment config (workers, threads, restarts) | not seen | **yes**: the in-memory rate limiter depends on "one process" |
| Test run output for "6 tests pass" | not seen | partly; traced by reading instead |

**COVERAGE**
- Checked: agent.py (constants, `run_agent`, `ask_endpoint`); test_agent.py (all 6 tests, each read against a deliberate mutation of the code); claims "token cap", "request cap", "signed-in users only", "One process serves the endpoint", "6 tests pass".
- Not checked: the adapter, the tools, the auth middleware, the deployment (none supplied); actual test execution (no tools).

**SEATS AND GATE:** No sensitive data found (no PII, credentials or client material), so the gate passed. One local same-context reviewer ran. No subagent and no cross-vendor seats were available in this session.

---

### Pass 1: Reconstruct

The work claims to be the /ask research agent with caps on input size, turns, tokens per request and requests per user per hour. It loops `llm → tool → llm` until the model returns an answer and returns it, or returns `{"error": ...}` when a cap trips.

For it to be correct on the public internet with per-token billing, all of these must hold:
- `request["user"]` comes from verified authentication.
- `reply["tokens"]` reports the billed tokens (input and output) for every call.
- The rate limiter's single in-process dict is the only one and is never accessed concurrently.
- The tools are safe to expose to anonymous-quality prompts.

Tracks: **B** (primary) and **A** (are the caps sufficient as a cost control).

---

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | agent.py:27-28; test_agent.py:6-11 | The per-request token cap, the main billing control, has no test. The only multi-turn test spends 10 tokens × 6 turns = 60, far below 20,000. | Someone deletes or breaks lines 27-28 during a refactor. All 6 tests stay green. Requests then run 6 full turns regardless of spend. | Add a test: replies of `{"tool":"t","tokens":15000}` twice. Assert `{"error":"token budget for this request"}` and exactly 2 calls. **Mutation check:** delete lines 27-28; today all 6 tests still pass (traced); the new test must go red. | a✓ b✓ c✗ d✗ |
| F2 | Medium | CONFIRMED (traced) | B | agent.py:25-28 | The cap is checked *after* each billed call, and no remaining budget is passed to `llm`. A single call can therefore overshoot by up to one full call. A reply without `"tokens"` counts as 0, so an adapter that omits the key disables the cap silently. | (i) After 5 calls `spent` = 19,000; the 6th call returns 30,000 tokens. 49,000 are billed, then the user gets an error and no answer for tokens already paid. (ii) The adapter omits `tokens`, so only the turn limit applies. | Pass the remaining budget as max output (`llm(messages, max_tokens=MAX_TOKENS_PER_REQUEST - spent)`, or the adapter's equivalent). Treat a missing `tokens` key as an error, not 0. **Repro:** `replies=iter([{"tool":"t","tokens":19000},{"answer":"a","tokens":30000}])`; observe 2 calls and 49,000 counted before the error. `lambda m: {"tool":"t"}` never trips the token cap. | a✓ b✓ c✗ d✗ |
| F3 | Medium | CONFIRMED (absence, read) | A | agent.py:5-10, 46-49 | All caps are per request or per user. There is no global spend or request ceiling and no circuit breaker. Worst-case spend therefore scales with the number of accounts. | Public announcement. One actor holds 50 accounts × 20 req/h × ≥20k tokens, about 20M+ tokens/hour billed to the company with no stop. (How easy accounts are to get is S1/S8.) | Add a global hourly token/request budget enforced before `llm()`, plus a provider-side spend limit and billing alerts. **Test:** set a global cap of N; issue N+1 requests from distinct users; assert the last is refused before any model call. | a✓ b✓ c✗ d✗ |
| F4 | Medium | CONFIRMED (traced) | B | agent.py:25, 37, 51-53 | Only `BudgetExceeded` is caught. Other failures propagate: `llm()` exceptions (provider 429/5xx/timeout), a reply with neither `tool` nor `answer` (`KeyError` at line 37), and a request without `question` (`KeyError` at line 51, raised *after* the rate-limit slot is consumed at line 49). Neither `llm` nor the tools have a timeout. | The provider returns 529, or the adapter maps a refusal to `{"text": ...}`. The endpoint raises; depending on the framework, the user gets a 500 or a traceback. A tool that hangs holds the request indefinitely. | Catch exceptions at the endpoint boundary and return a generic error (log the detail server-side). Use `.get("answer")` and treat its absence as an error. Set timeouts on `llm` and tools. **Repro:** `agent.ask_endpoint({"user":"u","question":"q"}, lambda m: {"tokens":1}, {})` raises `KeyError: 'answer'`; expected `{"error": ...}`. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED (read) | B | agent.py:10, 49 | `_seen` never evicts users, so it grows by one key per distinct user forever. A process restart resets every user's limit. | Over months, memory grows with the user base. A deploy or crash gives everyone a fresh quota of 20. | Evict keys whose newest hit is older than 3600 s, or move to a shared store with TTL (e.g. Redis `INCR` + `EXPIRE`), which also addresses S2. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED (traced) | B | test_agent.py:33-37 | The rate-limit test asserts only that request 21 fails. It never checks that requests 1-20 succeed, and never uses the injected `now` to check that the window expires. | Change line 47 to `>= 1`. Only the first request per hour then succeeds, yet the test still passes because `res[-1]` is an error. An off-by-one or a window that never expires also passes. | Assert `all("answer" in r for r in res[:-1])`. Add a test with a fake clock advancing 3601 s and assert the request succeeds. **Mutation:** `>= 1` at line 47 must go red. | a✓ b✓ c✗ d✗ |

### NEEDS VALIDATION (no severity)

- **S1: Is `request["user"]` set by verified auth?** If the HTTP layer copies it from the client body or header, then `{"user":"anything"}` bypasses login (lines 43-45), and rotating names bypasses the rate limit. That would make the endpoint unauthenticated with only per-request caps, which would be Critical. *Settles it:* the middleware code that populates `request`.
- **S2: Concurrency model, and is it really one process?** Lines 46-49 are read-check-write with no lock. Under a threaded server, N simultaneous requests from one user all see fewer than 20 hits and all pass. If the server is single-threaded, F4's missing timeouts mean one slow request blocks every user. Multiple workers or processes multiply the limit by the worker count. *Settles it:* the server and worker config.
- **S3: What do the tools do?** The question is attacker-controlled and tool results (if web or document fetch) are untrusted text fed back to the model. If any tool has side effects, reads private data, or fetches arbitrary URLs (SSRF to internal endpoints or metadata), a public user can drive it. *Settles it:* the `tools` dict and each tool's permissions.
- **S4: Does `reply["tokens"]` include input tokens?** Each turn resends the whole history (line 25), so input cost grows every turn. If the adapter reports only output tokens, the 20,000 cap understates billed spend several-fold. *Settles it:* the adapter source.
- **S5: Tool error text is relayed to the model.** `f"error: {exc}"` (line 34) can carry internal hostnames, paths or URLs with keys, and the model may repeat them in a public answer. *Settles it:* what exceptions the tools raise.
- **S6: Is there a system prompt or scope limit?** `run_agent` sends only the user's question (line 22). Unless the adapter adds one, /ask is a general-purpose LLM on the company's bill, not a research agent. *Settles it:* the adapter.
- **S7: Is the message format accepted by the provider?** The assistant `tool_call` has no id, and the tool message has no reference to it (lines 30, 35). Real tool-use APIs usually require ids. *Settles it:* the adapter's translation layer.
- **S8: How easy are accounts to get?** This determines whether F3 is likely. *Settles it:* the sign-up flow (email verification, CAPTCHA, payment).
- **S9: "6 tests pass."** Not run here. Tracing suggests all 6 would pass. *Settles it:* `python -m unittest test_agent -v` output.

### REFUTED

- *An unknown tool name crashes the request.* Refuted: the `tools[reply["tool"]]` lookup is inside the `try` (line 32), so the `KeyError` becomes an error string returned to the model.
- *Non-dict `args` crash the request.* Refuted: the `TypeError` from `**args` is caught by the same `try`.
- *A huge tool result blows the context.* Refuted: truncated to 4,000 chars (line 35). `json.dumps` defaults to `ensure_ascii=True`, which escapes non-ASCII, so 4,000 chars stays token-bounded. Covered by test_agent.py:23-28.
- *A non-string question bypasses the length check.* Refuted: the `isinstance` check (line 18) runs first. Tested at line 18-21.
- *An off-by-one lets 21 requests through.* Refuted: the `>= 20` check before appending allows exactly 20.

### WHAT HOLDS UP
- The input caps work: type and length are checked before any model call, and both paths are tested.
- The turn loop is bounded at 6 and tested.
- Tool-result truncation is applied and tested.
- Tool failures stay inside the loop instead of killing the request.
- The anonymous check exists, assuming S1 holds.
- The scope matches the request: an agent loop that returns an answer. The caps are justified additions for a public, billed endpoint, not drift.

### UNVERIFIED CLAIMS
- "6 tests pass": run the suite.
- "One process serves the endpoint": check the deployment config.
- "signed-in users only": check the auth middleware (S1).
- "token cap": its meaning depends on what `tokens` measures (S4) and on the overshoot (F2).

### QUESTIONS FOR THE AUTHOR
1. Where does `request["user"]` come from, and can a client set it?
2. Which server, how many workers, and are there threads per worker?
3. What tools ship in production, and can any fetch URLs or touch internal data?
4. Does the adapter's `tokens` include input tokens, and does it set a system prompt and max output?

### DECISION-MAKER SUMMARY
Before announcing, fix F2 (pass the remaining budget as max output), add a global spend ceiling (F3), and add the missing token-cap test (F1). Get written answers to S1-S3. If you proceed now, the realistic risk is spend that grows with the number of accounts and only roughly bounded per request. If S1 or S3 resolve badly, it becomes an unauthenticated or tool-abusable public endpoint, which would be a Critical issue.

### OWNER SUMMARY
The assistant code is mostly sound and has sensible limits, but its spending limit can be overshot, nothing caps the total bill across all users, and the spending limit itself is never tested. A few things outside this code still need checking before launch: how users are identified, how many requests the server handles at once, and what the assistant's tools are allowed to do. Fix the spending limits and get those answers before the public announcement.

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
    {"item": "llm adapter", "status": "not_seen", "matters": true},
    {"item": "tools implementations", "status": "not_seen", "matters": true},
    {"item": "HTTP/auth layer populating request", "status": "not_seen", "matters": true},
    {"item": "deployment/server config", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "agent.py", "kind": "file"},
      {"unit": "agent.py:run_agent", "kind": "function"},
      {"unit": "agent.py:ask_endpoint", "kind": "function"},
      {"unit": "test_agent.py", "kind": "file"},
      {"unit": "One process serves the endpoint", "kind": "assumption"},
      {"unit": "6 tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "llm adapter", "reason": "not supplied"},
      {"unit": "tools", "reason": "not supplied"},
      {"unit": "auth middleware", "reason": "not supplied"},
      {"unit": "deployment config", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:27-28; test_agent.py:6-11",
     "scenario": "The token-cap check is deleted or broken in a refactor; all 6 tests still pass because the only multi-turn test spends 60 tokens, and requests then run 6 full turns regardless of spend.",
     "fix": "Add a test with two replies of 15000 tokens each asserting the token-budget error after exactly 2 calls.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete agent.py lines 27-28 and run test_agent.py: all tests pass (traced); the new test must fail."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:25-28",
     "scenario": "With 19000 tokens spent, the next call returns 30000 tokens; 49000 are billed before BudgetExceeded and the user gets no answer. A reply without a tokens key counts 0, so the cap never trips.",
     "fix": "Pass the remaining budget as max output to llm before each call; treat a missing tokens key as an error.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "replies=[{tool:t,tokens:19000},{answer:a,tokens:30000}] -> 2 calls, 49000 counted, then error; lambda m: {'tool':'t'} never trips the token cap."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "agent.py:5-10,46-49",
     "scenario": "One actor with 50 accounts makes 20 requests/hour each at 20000+ tokens: about 20M+ tokens/hour billed with no global stop.",
     "fix": "Add a global hourly token/request budget checked before llm(), plus a provider spend limit and billing alerts.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "With a global cap N, issue N+1 requests from distinct users; expect the last refused before any model call; today all succeed."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:25,37,51-53",
     "scenario": "A provider error, a reply without answer/tool, or a request without question raises an uncaught exception (500 or traceback). The rate-limit slot is already consumed, and tools/llm have no timeout, so a hang holds the request.",
     "fix": "Catch exceptions at the endpoint boundary and return a generic error; use reply.get('answer') and treat its absence as an error; set timeouts on llm and tools.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "agent.ask_endpoint({'user':'u','question':'q'}, lambda m: {'tokens':1}, {}) raises KeyError('answer'); expected {'error': ...}."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:10,49",
     "scenario": "_seen keeps one key per distinct user forever, so memory grows; any restart resets every user's limit.",
     "fix": "Evict stale keys or use a shared store with TTL (e.g. Redis INCR+EXPIRE).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call ask_endpoint for 100000 distinct users; len(agent._seen) == 100000 and never shrinks."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_agent.py:33-37",
     "scenario": "Changing agent.py:47 to '>= 1' lets only one request per hour through, yet test_rate_limit still passes because it checks only res[-1]; window expiry is never tested.",
     "fix": "Assert requests 1-20 return answers; add a fake-clock test that advances 3601s and expects success.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Mutate line 47 to '>= 1'; test_rate_limit passes (traced); the strengthened test must fail."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent.py:43",
     "suspicion": "request['user'] may be client-supplied, bypassing login and the per-user rate limit.",
     "unresolved_fact": "Whether the auth middleware sets request['user'] from a verified session."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent.py:46-49",
     "suspicion": "Unlocked read-check-write races under threads; multiple workers multiply the limit; a single-threaded server lets one slow request block all users.",
     "unresolved_fact": "Server, worker and thread configuration in production."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent.py:32",
     "suspicion": "Public users can steer tools via prompt injection (side effects, private data, SSRF).",
     "unresolved_fact": "Which tools are registered and what each can access."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent.py:26",
     "suspicion": "tokens may count only output tokens, understating spend as the history is resent each turn.",
     "unresolved_fact": "What the adapter puts in reply['tokens']."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "agent.py:34",
     "suspicion": "Exception text from tools may leak internal details into public answers.",
     "unresolved_fact": "What exceptions and messages the tools raise."},
    {"id": "S6", "status": "needs_validation", "track": "A", "location": "agent.py:22",
     "suspicion": "Without a system prompt, /ask is a general-purpose LLM on the company bill.",
     "unresolved_fact": "Whether the adapter injects a system prompt or scope limit."},
    {"id": "S7", "status": "needs_validation", "track": "B", "location": "agent.py:30,35",
     "suspicion": "Tool call and result messages lack ids that provider tool-use APIs usually require.",
     "unresolved_fact": "How the adapter translates these messages."},
    {"id": "S8", "status": "needs_validation", "track": "A", "location": "agent.py:43-49",
     "suspicion": "Cheap sign-up makes multi-account cost abuse (F3) likely.",
     "unresolved_fact": "Sign-up friction: verification, CAPTCHA, payment."},
    {"id": "S9", "status": "needs_validation", "track": "B", "location": "test_agent.py",
     "suspicion": "The claim that 6 tests pass was not executed here.",
     "unresolved_fact": "Output of python -m unittest test_agent -v."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "An unknown tool name crashes the request.", "evidence": "The tools[...] lookup is inside the try at agent.py:31-34; the KeyError becomes an error string."},
    {"id": "R2", "candidate": "Non-dict args crash the request.", "evidence": "The TypeError from ** unpacking is caught by the same try."},
    {"id": "R3", "candidate": "A huge tool result exhausts the context.", "evidence": "Truncated to 4000 chars at agent.py:35 with ensure_ascii escaping; tested at test_agent.py:23-28."},
    {"id": "R4", "candidate": "A non-string question bypasses the length check.", "evidence": "isinstance check at agent.py:18 runs first; tested at test_agent.py:18-21."},
    {"id": "R5", "candidate": "An off-by-one admits 21 requests per hour.", "evidence": "The >= 20 check at line 47 runs before the append at line 49, allowing exactly 20."}
  ]
}
```