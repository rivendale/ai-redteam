# Redteam report: Pedalo `/plan` endpoint

**VERDICT: SHIP WITH FIXES.** The caps and the locking hold up. But the agent loop drops the model's own tool calls from the conversation history, and model or adapter failures escape the endpoint's error contract. The core "use the routing tool, then answer" path is untested, and it is the path most likely to fail against a real model API.

**CONFIDENCE: medium.** I had no tools, so I ran no code and could not reproduce "9 tests pass". The `llm` adapter, the `tools` registry, the auth layer that sets `rider`, and the deployment topology were not supplied. Several conclusions depend on them.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `planner.py`, `test_planner.py`.
- **Not seen, and it matters:**
  - The `llm` adapter. Message format, whether `tokens` counts input, timeouts, whether it adds a system prompt. This decides F1, F3 and S3.
  - The auth middleware that populates `request["rider"]`. This decides S1.
  - The deployment process/worker count. This decides S2.
- **Not seen, matters less:** the routing tool implementation.
- **Test run output:** not seen. "9 tests pass" is UNVERIFIED.

**COVERAGE**
- **Checked:**
  - `planner.py`: `_run`, `plan`, module state and lock.
  - `test_planner.py`: all 9 tests, each traced against a mutation.
  - Assumptions: rider identity, process model, token accounting.
- **Not checked:** the adapter, the tools, the auth layer, the web framework's handling of uncaught exceptions.

**SEATS AND GATE**
- One reviewer: this session, no subagent, no tools.
- The work was not authored in this conversation, so there is no authorship anchoring. It is still a single unverified read.
- No sensitive data is present. No cross-vendor seats were requested; none ran.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | PROBABLE (the code fact is CONFIRMED; the API impact depends on the adapter) | B | `planner.py:32-38` | When the model calls a tool, only the tool result is appended (`{"role": "tool", ...}`). The model's own call (tool name, args, call id) is never added to `messages`. | A rider asks for a route and the model calls the routing tool. On turn 2 the history is `user, tool`, with no assistant turn. Anthropic requires `tool_result` to reference a prior assistant `tool_use` id; OpenAI requires `tool_call_id`. Neither can be rebuilt from these messages, so the API rejects the call, or the model sees an orphan result and repeats the call until "turn limit". Either way the main feature fails on every tool-using question. | Append the assistant reply (tool name, args, id) before the tool result, and carry the id on the result. **Test:** an `llm` stub that on its second call asserts `messages[1]` is the assistant tool call and `messages[2]` references it, then answers. On current code the assertion fails. | a Y, b N, c Y, d Y |
| F2 | High | CONFIRMED | B | `planner.py:59-62` (also 26-27) | Only `Refused` is caught. A provider timeout, 429 or 5xx, or a non-dict reply (`reply.get` at line 27 raises `AttributeError`), escapes `plan()`. | The provider returns 429 at peak. `plan()` raises, and the rider gets the framework's 500 instead of `{"error": ...}`. Depending on framework config, that may include a traceback. The rate-limit slot is still consumed. | Catch adapter exceptions around `llm(...)` and around reply parsing; return `{"error": "planner unavailable"}` and log. **Test:** an `llm` stub that raises `TimeoutError`; expect `{"error": ...}`. Current code raises. | a Y, b Y, c N, d Y |
| F3 | Medium | PROBABLE | B/D | `planner.py:23` | There is no system prompt or scope restriction: `messages` is just the rider's text. Unless the adapter adds one, the endpoint answers anything. | A signed-in rider uses `/plan` as a free general-purpose LLM (essays, code), up to 30 × 15k tokens per hour, billed to Pedalo. This drifts from "answers how do I get from A to B by bike". | Add a scoped system prompt here, not hidden in the adapter. Optionally refuse off-topic answers. **Test:** assert the first message sent to `llm` is the system prompt. | a Y, b N, c N, d Y |
| F4 | Medium | CONFIRMED (traced; not run) | B | `test_planner.py` | The suite would stay green under several breaking mutations. | (1) Delete lines 30-31, the token-budget check: all 9 tests still pass, because `test_a_model_that_never_stops` ends at the turn limit. (2) Change line 26 to `max_tokens=MAX_TOKENS`: `test_the_model_is_asked_for_no_more_than_the_remaining_budget` still passes, because it makes only one call. (3) There is no test of tool call → answer (see F1), of window expiry after 3600 s, or of the tool-error path. | Add tests for: replies of 10,000 tokens each → expect `"token budget"`; a multi-turn stub asserting `max_tokens` goes 15000, 14990, …; a tool-then-answer conversation; a rider allowed again at t+3601. | a Y, b Y, c N, d N |
| F5 | Medium | PROBABLE | B | `planner.py:36` | `f"error: {exc}"` sends raw exception text to the model, which can repeat it to the rider. | The routing tool's HTTP client raises with a message containing the upstream URL, including an API-key query parameter. The model includes it in its answer. | Pass a generic `"routing failed"` to the model and log the exception server-side. | a Y, b N, c N, d N |
| F6 | Low | CONFIRMED | B | `planner.py:11, 57` | `_seen` is never pruned. A rider's key stays forever; it is only filtered when that same rider returns. | Memory grows with every distinct rider for the life of the process. It is far worse if rider ids can be forged (S1). | Periodically drop keys whose newest hit is older than 3600 s, or use a TTL cache. | a Y, b Y, c N, d N |
| F7 | Low | CONFIRMED | B | `planner.py:26, 30` | The check is `spent > MAX_TOKENS`, so `spent == MAX_TOKENS` passes, and a tool reply then triggers a call with `max_tokens=0`. | Most APIs reject `max_tokens < 1`, so the request falls into F2 instead of `"token budget"`. | Use `>=`, or stop when the remaining budget is under a minimum. **Test:** tool replies totalling exactly 15000 tokens; expect `{"error": "token budget"}`. | a Y, b Y, c N, d N |

## NEEDS VALIDATION

- **S1. Source of `request["rider"]`.** If it comes from the POST body rather than verified auth middleware, then:
  - anyone can call `/plan` while "signed out";
  - rotating rider strings bypasses the per-rider limit, so one client exhausts the 2000/h global budget for everyone;
  - a JSON object as `rider` raises `TypeError` (unhashable) at line 51.

  That would be Critical. **Settle it:** read the auth layer.
- **S2. Process model.** `_seen`, `_all` and `_lock` are per-process. With N workers or instances, every limit becomes N×, including the global billing ceiling. A restart resets all limits. **Settle it:** check the deployment config for worker and replica count.
- **S3. Token accounting.** Does `reply["tokens"]` include input tokens? Each turn re-sends the full history (up to ~4.5k tokens with truncated tool results). If `tokens` counts output only, input spend is outside the 15k cap. **Settle it:** read the adapter.
- **S4. Timeout.** Does the adapter set a timeout on the model call? If not, a hung call holds a worker indefinitely.
- **S5. "9 tests pass."** Not run here.

## REFUTED

- **Unknown tool name crashes the endpoint.** Refuted: `tools[reply["tool"]]` is inside the `try` at line 34, so the `KeyError` becomes an error string.
- **Race on rate-limit counters.** Refuted: the whole read-check-append is under `_lock` (lines 50-58), and the lock is not held during the model call.
- **A "busy" refusal burns the rider's quota.** Refuted: line 56 returns before line 57 appends.
- **The global-limit test leaks its modified constant.** Refuted: `finally` restores `MAX_GLOBAL_PER_HOUR`.

## WHAT HOLDS UP

- Anonymous requests and over-length questions are refused before any model call, and this is tested.
- Turns are hard-bounded at 5.
- Tool output is truncated to 4000 characters.
- A missing token count fails closed.
- Per-rider and global sliding windows are correct within one process.
- Lock scope is tight.
- Malformed tool args are contained by the `try`.

## UNVERIFIED CLAIMS

- **"Signed-in riders only"** (docstring). Depends on S1.
- **"Caps on ... tokens."** Only output-capped per call and checked after billing; see S3 and F4.
- **"9 tests pass."** Confirm by running `python -m unittest test_planner`.

## QUESTIONS FOR THE AUTHOR

1. Where is `rider` set, and can a client influence it?
2. How many processes or instances serve `/plan`?
3. What message format does the `llm` adapter send to the provider, and does `tokens` include input?

## DECISION-MAKER SUMMARY

Fix F1 and F2 and add the missing tool-path and budget tests before launch. The routing-tool path is very likely broken against a real model API, and provider errors surface as raw 500s. Before launch, also confirm that rider identity comes from verified auth and that limits survive multiple workers; otherwise the per-user and global spend caps may not hold.

## OWNER SUMMARY

The trip planner has sensible spending limits, but the part where the AI looks up a route probably does not work with a real AI service yet, and the tests never try it. When the AI service has a hiccup, riders will see a crash page instead of a friendly message. Two questions need answers before launch: how riders are identified, and whether the limits still apply when the site runs on several servers.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "planner.py", "status": "seen", "matters": true},
    {"item": "test_planner.py", "status": "seen", "matters": true},
    {"item": "llm adapter", "status": "not_seen", "matters": true},
    {"item": "auth middleware setting request['rider']", "status": "not_seen", "matters": true},
    {"item": "deployment worker/instance config", "status": "not_seen", "matters": true},
    {"item": "routing tool implementation", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "planner.py", "kind": "file"},
      {"unit": "planner.py:_run", "kind": "function"},
      {"unit": "planner.py:plan", "kind": "function"},
      {"unit": "test_planner.py", "kind": "file"},
      {"unit": "rider identity is authenticated", "kind": "assumption"},
      {"unit": "single-process deployment", "kind": "assumption"},
      {"unit": "tokens field includes input", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "llm adapter", "reason": "not supplied"},
      {"unit": "auth middleware", "reason": "not supplied"},
      {"unit": "deployment config", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:32-38",
     "scenario": "Model calls the routing tool; only the tool result is appended, never the assistant tool call, so turn 2 sends user+tool with no tool_use/tool_call_id; real provider APIs reject it or the model loops to 'turn limit', breaking every tool-using question.",
     "fix": "Append the assistant tool-call message (name, args, id) before the tool result and reference its id in the result.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "llm stub that on call 2 asserts messages[1] is the assistant tool call; current code fails the assertion."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:59-62",
     "scenario": "Provider timeout/429 or a non-dict reply raises out of plan(); rider gets an unhandled 500 (possibly a traceback) instead of {'error': ...}.",
     "fix": "Catch adapter/parse exceptions around the llm call, return a generic error, and log.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "plan({'rider':'u','question':'q'}, llm that raises TimeoutError, {}); expect {'error': ...}, observe exception."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "planner.py:23",
     "scenario": "With no system prompt, a rider uses /plan as a general-purpose LLM billed to Pedalo.",
     "fix": "Add a bike-routing-scoped system prompt in planner.py and test that it is sent.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_planner.py",
     "scenario": "Deleting planner.py:30-31 or hardcoding max_tokens=MAX_TOKENS leaves all 9 tests green; the tool-then-answer path and window expiry are untested.",
     "fix": "Add tests for token-budget refusal, decreasing max_tokens across turns, tool-then-answer, and rider allowed after 3600s.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Remove lines 30-31 in a scratch copy and run the suite; it stays green."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "planner.py:36",
     "scenario": "A tool exception message containing an upstream URL with an API key is passed to the model and echoed to the rider.",
     "fix": "Send a generic 'routing failed' to the model; log the exception server-side.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:11,57",
     "scenario": "_seen keeps every rider key forever; memory grows for the process lifetime.",
     "fix": "Evict keys whose newest hit is older than 3600s, or use a TTL cache.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "planner.py:26,30",
     "scenario": "spent == MAX_TOKENS passes the check; the next call sends max_tokens=0, which providers reject, falling into F2.",
     "fix": "Use >= or stop when the remaining budget is below a minimum.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Tool replies totalling exactly 15000 tokens; expect {'error':'token budget'}, observe llm called with max_tokens=0."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "planner.py:47-48",
     "suspicion": "If rider comes from the request body, login and per-rider limits are bypassable and an unhashable rider crashes line 51.",
     "unresolved_fact": "Whether request['rider'] is set only by verified auth middleware."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "planner.py:11-13",
     "suspicion": "In-memory limits multiply by worker/instance count and reset on restart.",
     "unresolved_fact": "Number of processes/instances serving /plan."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "planner.py:26-31",
     "suspicion": "Input tokens from re-sent history may be outside the 15k cap.",
     "unresolved_fact": "Whether the adapter's reply['tokens'] includes input tokens."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "planner.py:26",
     "suspicion": "A hung model call holds a worker indefinitely.",
     "unresolved_fact": "Whether the llm adapter sets a request timeout."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Unknown tool name crashes the endpoint.", "evidence": "The lookup at planner.py:34 is inside the try; KeyError becomes an error string."},
    {"id": "C2", "candidate": "Race on rate-limit counters.", "evidence": "Read-check-append is entirely under _lock at planner.py:50-58."},
    {"id": "C3", "candidate": "A 'busy' refusal consumes the rider's quota.", "evidence": "planner.py:56 returns before the append at line 57."},
    {"id": "C4", "candidate": "The global-limit test leaks its modified constant.", "evidence": "A finally block restores MAX_GLOBAL_PER_HOUR."}
  ]
}
```