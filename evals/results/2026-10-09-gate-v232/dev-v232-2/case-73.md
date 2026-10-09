**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools. I did not author the work. I could not run any code, so every finding below comes from reading and tracing the supplied source line by line, and none of the reproductions has been executed.

VERDICT: **SHIP WITH FIXES.** The turn, input and truncation caps work as written, but the token cap fails open and is untested, and nothing caps total spend. Three questions could turn this into REWORK: where `request["user"]` comes from, what the tools can do, and what the LLM adapter reports.

CONFIDENCE: **low-medium.** Limits:
- This is a same-context review with no tools; nothing was run.
- The LLM adapter, the tool implementations, the HTTP layer that builds `request`, and the deployment config were not supplied.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `agent.py`, `test_agent.py`.
- **Not seen:**
  - **LLM adapter** (what `llm` returns, whether it reports tokens under `"tokens"`, any per-call `max_tokens`, any timeout). Matters: yes.
  - **Tool implementations** (side effects, network reach, timeouts). Matters: yes.
  - **Request construction / auth middleware** (whether `user` is set by the server or by the client body). Matters: yes.
  - **Deployment** (whether there is truly one process, or a worker count). Matters: yes.
  - **Test run output.** The "6 pass" claim is UNVERIFIED but plausible on trace. Matters: no.

COVERAGE:
- **Scope:** the whole work (two files).
- **Checked:**
  - `agent.py`: constants, `run_agent`, `ask_endpoint`.
  - `test_agent.py`: all six tests, traced.
  - `request.md`, `context.md`.
  - Claims: the module docstring ("input, turn, token and request caps", "One process") and the `ask_endpoint` docstring ("signed-in users only, rate limited per user").
- **Not checked:**
  - LLM adapter, tools, auth layer, deployment: not_supplied.
  - Actual test execution: no_tools.

SEATS AND GATE:
- Only the local same-context reviewer ran. No subagent was available and no cross-vendor seats were requested.
- Sensitivity gate passed: the work is code with no personal data or credentials.

## Findings

All findings are CONFIRMED by trace and none are security findings with a crossed boundary. The four questions (a/b/c/d) are listed under each.

**F1. Medium, Track B. The token cap fails open** (`agent.py:26`)
- **What is wrong:** `spent += reply.get("tokens", 0)` treats a missing usage field as zero tokens.
- **Failure scenario:** The real adapter reports usage under another key (for example `usage.total_tokens`) or omits it. `spent` then stays 0, and the advertised 20,000-token cap never fires. Every request is bounded only by 6 turns and whatever output length the adapter allows.
- **Fix:** Fail closed. Raise if `"tokens"` is absent or not a non-negative int, and count input plus output tokens.
- **Reproduction:**
  - Run `run_agent(lambda m: {"tool":"t","args":{},"usage":{"total_tokens":50000}}, {"t": lambda: "x"}, "q")`.
  - Expected: `BudgetExceeded("token budget for this request")` after call 1.
  - Observed by trace: 6 calls, then `"turn limit"`.
- **a/b/c/d:** Y / Y / N / N.

**F2. Medium, Track B. The token cap has no test; the "6 tests pass" signal does not cover it** (`test_agent.py`, all tests; `agent.py:27-28`)
- **What is wrong:** No test exercises `MAX_TOKENS_PER_REQUEST`. The only multi-turn test spends 10 × 6 = 60 tokens, so the turn limit fires first.
- **Failure scenario:** Someone deletes or breaks lines 27-28 (or F1 disables them) and every test stays green. The endpoint is announced with an unguarded spend cap.
- **Fix:** Add a test where the LLM returns a tool call with `tokens: 15000` each time. Assert `{"error": "token budget for this request"}` and exactly 2 calls. Also test that a missing `tokens` key is refused, which goes red today.
- **Reproduction:**
  - Mutation: delete `agent.py:27-28` in a scratch copy.
  - Run `python -m unittest test_agent`.
  - Expected: a failure. Observed by trace: all 6 pass.
- **a/b/c/d:** Y / Y / N / N.

**F3. Medium, Track B. No aggregate spend cap on a public, per-token-billed endpoint** (`agent.py:9, 46-49`)
- **What is wrong:** The only limits are per request and per user. Nothing bounds total spend per hour or day.
- **Failure scenario:** The endpoint is announced, and N accounts (sign-ups, scripted or real) each make 20 requests per hour at up to about 20k tokens each. That is about N × 400k tokens per hour with no ceiling and no alert.
- **Fix:** Add a global hourly and daily token or cost budget that refuses new requests when exhausted, plus a spend alert.
- **Reproduction:**
  - Loop `ask_endpoint({"user": f"u{i}", "question": "q"}, lambda m: {"answer": "a", "tokens": 19000}, {})` for i in 0..99, 20 times each.
  - Expected: refusals once a global budget is reached.
  - Observed by trace: all 2,000 calls succeed.
- **a/b/c/d:** Y / Y / N / N. d stays N until sign-up cost is known.

**F4. Low, Track B. The cap is checked only after the call is billed, and no per-call output limit is passed** (`agent.py:25-28`)
- **What is wrong:** `llm(messages)` is called with no `max_tokens`, and the budget check runs only after the call returns.
- **Failure scenario:** A request with `spent` at 19,000 makes one more call that returns a very long output. That whole call is billed, then the request is refused, so the cap overshoots by an unbounded single-call cost.
- **Fix:**
  - Pass `max_tokens = min(per_call_cap, MAX_TOKENS_PER_REQUEST - spent)` to the LLM.
  - Refuse before calling if the remaining budget is under a floor.
- **Reproduction:**
  - Replies `{"tool":"t","tokens":19000}` then `{"tool":"t","tokens":500000}`.
  - Expected: the second call is limited or never made.
  - Observed by trace: both calls are made, then the error is raised.
- **a/b/c/d:** Y / Y / N / N.

**F5. Low, Track B. Non-budget errors escape `ask_endpoint` unhandled** (`agent.py:37`, `agent.py:51-53`)
- **What is wrong:** `reply["answer"]` and `request["question"]` raise `KeyError`, and adapter exceptions propagate. Only `BudgetExceeded` is caught.
- **Failure scenario:** The model returns neither a tool call nor an answer (a refusal, an empty reply, or an API error). The framework returns a 500, possibly with a traceback if debug is on. The rate-limit hit has already been recorded.
- **Fix:** Catch `Exception` in `ask_endpoint`, log it, and return a generic error. Use `reply.get("answer")` with an explicit error when it is missing.
- **Reproduction:**
  - Run `ask_endpoint({"user":"x","question":"q"}, lambda m: {"tokens":1}, {})`.
  - Expected: `{"error": ...}`.
  - Observed by trace: `KeyError: 'answer'` is raised.
- **a/b/c/d:** Y / Y / N / N.

**F6. Low, Track B. `_seen` never evicts users** (`agent.py:10, 49`)
- **What is wrong:** A user's entry is pruned only when that same user calls again.
- **Failure scenario:** Every distinct user that ever calls stays in memory forever. This is slow growth with server-set users, but unbounded growth if `user` is client-controlled (see S1).
- **Fix:** Periodically sweep keys whose newest timestamp is older than 3600 s, or use a TTL store.
- **Reproduction:**
  - Call once each with 100,000 distinct `user` values.
  - Expected: entries expire after 1 h.
  - Observed by trace: `len(_seen) == 100000` indefinitely.
- **a/b/c/d:** Y / Y / N / N.

## NEEDS VALIDATION (no severity)

- **S1 (`agent.py:43`).** Is `request["user"]` set by trusted auth middleware, or is it parsed from the client's request body? If it comes from the client, login and the rate limit are bypassed by sending any string. That is a High or Critical security finding: anonymous internet to billed model, with unlimited spend.
- **S2 (`agent.py:32`).** What do the tools do? Model-chosen tool names and args are driven by a public user's question and by tool-returned content (prompt injection). If any tool has side effects, reaches internal network addresses (SSRF), or reads non-public data, that is a boundary crossing. Settled by the tool list and their implementations.
- **S3 (`agent.py:25, 32`).** Do the LLM and tool calls have timeouts? With "one process serves the endpoint", a hanging tool or model call (for example a fetch of an attacker-chosen slow URL) would block every user. Settled by the adapter and tool code, and by the server's concurrency model.
- **S4 (`agent.py:1`, `_seen`).** Is it actually one process? Under N workers or a restart, the per-user limit becomes N × 20 per hour or resets. Settled by the deployment config.
- **S5 (`agent.py:34`).** Can tool exception text (paths, hostnames, keys in URLs) be echoed by the model to the public user? Settled by what the tools raise.
- **S6 (`agent.py:26`).** Does the adapter's token figure include input tokens? Context is resent each turn, so output-only counting understates spend. Settled by the adapter.
- **S7.** Where is the answer rendered? If a client renders it as markdown or HTML, injected image links or script become a concern. Settled by the client.

## REFUTED

- **Unknown tool name or non-dict args crash the loop.** Refuted: the lookup `tools[reply["tool"]]` and the `**args` call are both inside the `try` at `agent.py:31-34`, so the error is returned to the model.
- **The truncation test reads the wrong message.** Refuted: `seen[1]` is the same mutated list, and by the time of the assertion its last element is the tool result. The test is valid.
- **Race on the rate-limit check-then-set.** Withdrawn as a finding: there is no await or I/O between lines 46 and 49. Any thread race window is tiny and depends on the deployment (folded into S4).

## WHAT HOLDS UP

- Question type and length checks run before any model call, and both are tested.
- The turn cap bounds the loop and is tested.
- Tool results are serialized and truncated before re-entering the context, and this is tested.
- Tool errors are contained.
- The rate limit is recorded before the run, so failed requests still count.
- Anonymous requests are refused, provided S1 resolves well.
- The work does what was asked (tools until answer, return the answer). The extra controls are justified by the stated stakes.

## UNVERIFIED CLAIMS

- **"6 tests pass."** Confirm by running `python -m unittest test_agent` in an isolated copy.
- **"token … caps"** (docstring). Confirm via F1 and F2 plus the adapter.
- **"signed-in users only"**. Confirm via S1.
- **"One process serves the endpoint."** Confirm via S4.

## QUESTIONS FOR THE AUTHOR

1. Who populates `request["user"]`?
2. Which tools are wired in, and can any of them write, reach internal hosts, or read private data?
3. What does the LLM adapter return for usage, and does it set `max_tokens` and a timeout?
4. Is sign-up open, and is there any account-level or global billing limit outside this code?

## DECISION-MAKER SUMMARY

Before announcing, fix the fail-open token cap and add its test (F1, F2), and add a global spend ceiling (F3). Answer S1 and S2 first: if the user identity is client-supplied, or if the tools can act or read beyond public data, this becomes REWORK. Proceeding as-is risks an uncapped model bill driven by anyone on the internet.

## OWNER SUMMARY

The question-answering service mostly limits itself sensibly. However, its per-request spending limit can silently switch off, nothing has ever tested that limit, and there is no overall ceiling on how much the service can spend in an hour. Those should be fixed, and a few questions about how users are identified and what the tools can do should be answered, before the service is announced publicly.

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
    {"item": "LLM adapter (llm callable)", "status": "not_seen", "matters": true},
    {"item": "tool implementations", "status": "not_seen", "matters": true},
    {"item": "request construction / auth middleware", "status": "not_seen", "matters": true},
    {"item": "deployment config (process count)", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
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
      {"unit": "docstring claim: one process serves the endpoint", "kind": "claim"},
      {"unit": "context claim: 6 tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "LLM adapter", "reason": "not_supplied"},
      {"unit": "tool implementations", "reason": "not_supplied"},
      {"unit": "auth middleware / request construction", "reason": "not_supplied"},
      {"unit": "deployment config", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:26",
     "scenario": "If the LLM adapter omits the 'tokens' key or reports usage under another key, spent stays 0 and the 20,000-token per-request cap never fires; only the 6-turn cap remains.",
     "fix": "Fail closed: raise BudgetExceeded when 'tokens' is missing or not a non-negative int; count input plus output tokens.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "run_agent(lambda m: {'tool':'t','args':{},'usage':{'total_tokens':50000}}, {'t': lambda: 'x'}, 'q'): expected BudgetExceeded('token budget for this request') after 1 call; traced: 6 calls then 'turn limit'. Not executed (no tools)."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_agent.py (all tests); agent.py:27-28",
     "scenario": "No test reaches MAX_TOKENS_PER_REQUEST (the multi-turn test spends 60 tokens), so removing or breaking the token check leaves all 6 tests green.",
     "fix": "Add a test with tool replies of tokens=15000 asserting {'error': 'token budget for this request'} after 2 calls, and a test that a reply missing 'tokens' is refused.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy delete agent.py:27-28 and run python -m unittest test_agent: expected a failure; traced: all 6 pass. Not executed (no tools)."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:9, 46-49",
     "scenario": "On the public endpoint, N accounts at 20 requests/hour and up to about 20k tokens each give about N x 400k billed tokens/hour with no global ceiling or alert.",
     "fix": "Add a global hourly/daily token or cost budget that refuses requests when exhausted, plus a spend alert.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "For i in 0..99, call ask_endpoint({'user': f'u{i}', 'question': 'q'}, lambda m: {'answer':'a','tokens':19000}, {}) 20 times each: expected refusals after a global budget; traced: all 2,000 succeed. Not executed (no tools)."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:25-28",
     "scenario": "The budget is checked only after a call is billed and llm() receives no max_tokens, so with spent near the cap one long-output call is billed in full before refusal.",
     "fix": "Pass max_tokens = min(per_call_cap, MAX_TOKENS_PER_REQUEST - spent) to the LLM; refuse before calling if the remaining budget is under a floor.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replies {'tool':'t','tokens':19000} then {'tool':'t','tokens':500000}: expected the second call to be limited or not made; traced: both made, then error. Not executed (no tools)."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:37, 51-53",
     "scenario": "A model reply with neither 'tool' nor 'answer', a request without 'question', or an adapter exception raises out of ask_endpoint as a 500, possibly with a traceback; the rate-limit hit is already recorded.",
     "fix": "Catch Exception in ask_endpoint, log it, return a generic error; treat a missing 'answer' as an explicit error.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "ask_endpoint({'user':'x','question':'q'}, lambda m: {'tokens':1}, {}): expected {'error': ...}; traced: KeyError('answer') raised. Not executed (no tools)."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent.py:10, 49",
     "scenario": "_seen keeps every distinct user forever because entries are pruned only on that user's next call; memory grows without bound, quickly if user values are client-controlled.",
     "fix": "Sweep keys whose newest timestamp is older than 3600 s, or use a TTL store.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call ask_endpoint once each with 100,000 distinct user values: expected entries to expire after 1 h; traced: len(agent._seen) == 100000 indefinitely. Not executed (no tools)."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "agent.py:43",
     "suspicion": "If request['user'] comes from the client body, any string bypasses login and the per-user rate limit, so anonymous callers get unlimited billed model use.",
     "unresolved_fact": "Whether 'user' is set by trusted auth middleware or parsed from client input."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "agent.py:32",
     "suspicion": "Model-chosen tool calls are steerable by public users and by injected tool content; tools with side effects, internal network reach (SSRF) or private data access would cross a trust boundary.",
     "unresolved_fact": "The tool list and what each tool can read, write or reach."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "agent.py:25, 32",
     "suspicion": "With one process and no timeouts in this code, a hanging model or tool call blocks every user.",
     "unresolved_fact": "Whether the adapter and tools enforce timeouts, and the server's concurrency model."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "agent.py:1, 10",
     "suspicion": "The in-memory rate limit multiplies across workers and resets on restart.",
     "unresolved_fact": "The actual worker/process count in deployment."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "agent.py:34",
     "suspicion": "Tool exception text may be echoed by the model to public users and leak internal details.",
     "unresolved_fact": "What exceptions the tools raise and what their messages contain."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "agent.py:26",
     "suspicion": "Output-only token counting understates spend because context is resent each turn.",
     "unresolved_fact": "Whether the adapter's 'tokens' includes input tokens."},
    {"id": "S7", "status": "needs_validation", "track": "B", "location": "agent.py:51",
     "suspicion": "The answer is attacker-influenced; if a client renders it as markdown or HTML, injected image links or script are a risk.",
     "unresolved_fact": "How and where the answer is rendered."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "An unknown tool name or non-dict args crashes the loop.",
     "evidence": "The tool lookup and **args call are inside the try at agent.py:31-34; the error is returned to the model."},
    {"id": "C2", "candidate": "test_a_huge_tool_result_is_truncated inspects the wrong message.",
     "evidence": "seen[1] is the same mutated messages list; its last element at assertion time is the truncated tool result."},
    {"id": "C3", "candidate": "Race on the rate-limit check-then-set at agent.py:46-49.",
     "evidence": "No await or I/O between read and write; any thread race window is tiny and deployment-dependent, folded into S4."}
  ]
}
```