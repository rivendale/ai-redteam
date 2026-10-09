VERDICT: **SHIP WITH FIXES.** The server-side checks (ownership, balance, per-order limit, amount validation) hold against hostile model output. However, the concurrency guarantee rests on an API behaviour that was neither supplied nor tested, and the order identifier the model supplies is never validated.

CONFIDENCE: **medium.** I had no tools, so nothing was run, including the "7 tests pass" claim. The refunds API, the `llm` wrapper and the login layer were not supplied. The work was not written in this conversation, so anchoring on the author's reasoning is not a concern, but this is a single, unexecuted read.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `handler.py`, `prompts.py`, `system_prompt.txt`, `test_handler.py`.
- **Not seen, and it matters:**
  - The real `/refunds` API. The race protection depends on it enforcing `expected_refunded`.
  - The `api` client: how it builds URLs, normalises paths, attaches auth and raises errors.
  - The `llm` wrapper: whether it keeps conversation history and how it shapes tool calls.
  - The login layer: the type of `is_staff`.
  - The staff-approval workflow for `/refund_requests`.
- **Not seen, and it matters less:** the test run output. Hand-tracing suggests all 7 tests pass.

COVERAGE:
- **Scope:** the whole work (4 files plus 2 input documents).
- **Checked:**
  - `handler.py`: `refund` and `handle_turn`
  - `prompts.py`
  - `system_prompt.txt`
  - `test_handler.py`: all 7 tests, traced by hand
  - `request.md` and `context.md`
  - The claim in the line 22 comment
  - The claim that `is_staff` is "set by the login layer"
- **Not checked:**
  - The refunds API, api client, llm wrapper and approval workflow (`not_supplied`)
  - Actual test execution and mutation runs (`no_tools`)

SEATS AND GATE:
- **Gate:** no personal data, credentials or client material appears in the work. `"test-only"` is a placeholder key.
- **Seats:** a single local reviewer ran. No subagent or cross-vendor seats were available in this session (no tools).

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | `handler.py:13`, `handler.py:23` | `order_id` comes from the model, so the customer controls it. It is never type- or format-checked. It is interpolated raw into the GET path, and the raw value is then sent as `"order"` to `/refunds`. The order that is checked and the order that is acted on are two separate representations of attacker input. | A customer asks the model to call `refund(10, "VICTIM/../MINE")` or `"MINE?x=VICTIM"`. Suppose the api client normalises or truncates the GET path to `MINE`. The ownership and balance checks then pass on the customer's own order, while `/refunds` receives a different identifier string. Whether money moves on the wrong order depends on how `/refunds` parses `"order"`. | **Fix:** validate `order_id` against a strict pattern (for example `^[A-Za-z0-9_-]{1,64}$`, type `str`). Post `order["id"]` from the fetched record, not the raw argument. **Repro:** call `turn(api, {"id": 9}, {"amount": 1, "order_id": "o1/x"})` with a mock whose `get` normalises paths. The refund posts with `order == "o1/x"`. Expected: `"bad order id"`. | a✓ b✗ c✓ d✗ |
| F2 | Medium | CONFIRMED | B | `test_handler.py:17-22`; `handler.py:22-23` | The mock `Api.post` ignores `expected_refunded`. This is the only control that stops two concurrent turns from both spending the same balance, or both staying under `LIMIT`. No test exercises it, so it could be removed without any test going red. | Two simultaneous turns each request 300 on `o2` (refunded 0). Both pass the limit check, since 300 ≤ 500. If `expected_refunded` is dropped by a refactor, or the API doesn't honour it, 600 is refunded with no staff approval, and every test stays green. | **Fix:** make the mock reject when `orders[o]["refunded"] != body["expected_refunded"]`, and add an interleaved test (GET both, then POST both). **Mutation repro:** delete `"expected_refunded": order["refunded"]` from line 23 and run `python -m unittest test_handler`. Expected: a failure. By reading, all 7 still pass (not run). | a✓ b✓ c✗ d✗ |
| F3 | Medium | PROBABLE | B | `handler.py:20-21` | Every over-limit turn posts a new `/refund_requests` entry. There is no dedupe, rate cap or check for an existing pending request. | A frustrated customer repeats "refund 600 on o2" five times, which creates five approval requests. Suppose the approval workflow posts each approved request without re-checking the balance and limit (not supplied). Two approvals would then pay 1200 on a 900 order, or exceed the intended staff-approved amount. At minimum, the staff queue fills with duplicates. | **Fix:** before posting, query for an existing pending request on the same order. Include `expected_refunded` in the request so that approval re-validates. Cap requests per user per day. **Repro:** call `turn(api, {"id": 5}, {"amount": 600, "order_id": "o2"})` twice. `len(api.requests) == 2`. Expected: 1. | a✓ b✗ c✓ d✗ |
| F4 | Medium | PROBABLE | B | `handler.py:26-33`; `system_prompt.txt:3` | `handle_turn` passes the model only the current message, and never feeds tool results back to it. The prompt's instruction "tell the user what the tool said" is therefore dead: the user receives the raw exception string. On success, the user receives the raw API response object, not a chat reply. As written, this is not a working chat assistant. | Turn 1: "refund my order" → the model asks "which order?". Turn 2: "o1" → the model has no history, so it does not know a refund was requested. A successful refund returns `{"amount":30,"order":"o1","by":9,"expected_refunded":0.0}` to the customer instead of a sentence. | **Fix:** keep the conversation history per session and pass it to `llm`. Return the tool result to the model as a tool message, and let it compose the reply. **Repro:** call `handle_turn` with a stub `llm` that records its arguments. No prior turns are present; the success return value is a `dict`. | a✓ b✗ c✓ d✓ (request fit) → see note* |
| F5 | Low | CONFIRMED | B | `handler.py:31-32` | Catching `KeyError` and returning `str(exc)` leaks internal key names to the customer. | `REFUND_API_KEY` is unset in production, so the customer sees `'REFUND_API_KEY'`. A missing order in a dict-backed client shows `'o9'`. | **Fix:** map exceptions to fixed customer messages and log the details server-side. **Repro:** `del os.environ["REFUND_API_KEY"]`, then `turn(Api(), {"id": 9}, {"amount": 1, "order_id": "o1"})` returns `"'REFUND_API_KEY'"`. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED | B | `handler.py:33` | `reply["text"]` is outside the `try`. A model reply with neither a tool call nor text raises an uncaught `KeyError`. | A malformed model output, for example `{"tool": "other"}`, makes the turn crash instead of producing a reply. | **Fix:** use `reply.get("text") or a fallback`. **Repro:** `handler.handle_turn(lambda s,u,m: {"tool": "x"}, Api(), {"id": 9}, "x")` raises `KeyError: 'text'`. | a✓ b✓ c✗ d✗ |
| F7 | Low | CONFIRMED | B | `prompts.py:1` | The prompt path is relative to the CWD, and the file handle is never closed. | The service starts from another directory, so the import fails with `FileNotFoundError`. | **Fix:** `Path(__file__).with_name("system_prompt.txt").read_text()`. **Repro:** `cd /tmp && python -c "import sys; sys.path.insert(0, '<repo>'); import prompts"` raises `FileNotFoundError`. | a✓ b✓ c✗ d✗ |

\*Note on F4: by the four questions, a, c and d hold, which would place it at High as request drift. I scored it **Medium** because the deciding fact is unverified. The `llm` callable is supplied by the caller and could close over history, so (b) is PROBABLE and the scenario is conditional on that wrapper. If the wrapper does not keep history, raise F4 to **High**.

## NEEDS VALIDATION

- **S1:** Does `/refunds` actually reject when `expected_refunded` doesn't match? Every race guarantee rests on this; the comment at `handler.py:22` is an unverified claimed control. Settle it with the API's contract or a test against staging.
- **S2:** How does a rejected `/refunds` post surface? If it raises an exception type other than the four that are caught (for example an `HTTPError`), the turn crashes. If it returns an error body, that body is passed to the user as if it were a success. Settle it with the api client's error behaviour.
- **S3:** Is `user["is_staff"]` always a real boolean? `bool("false")` is `True`, so a string flag from the login layer would grant staff bypass of both ownership and the limit. Settle it with the login layer's schema.
- **S4:** Does the api client normalise or encode paths, and what auth does `api.get` carry? This decides whether F1 is exploitable and whether a customer-controlled GET path reaches other endpoints under service credentials.
- **S5:** Is a per-order limit (rather than per-customer or per-period) the intended business rule? A customer with ten orders can self-serve 10 × 500. The comment says "on one order", so this looks deliberate, but it needs confirmation.
- **S6:** Do the 7 tests pass? Not run. Hand-traces of all 7 are consistent with passing, including the float edge case `9.99 - (19.99 - 10.0)` rounding to 0.

## REFUTED

- **R1:** "The model can override `user` or `api` via `**reply["args"]`." Refuted: a duplicate keyword raises `TypeError` ("got multiple values"), which is caught. Extra keys also raise `TypeError`.
- **R2:** "Splitting refunds evades `LIMIT`." Refuted: line 19 checks the cumulative `order["refunded"] + amount`, and `test_a_series_of_small_refunds_cannot_pass_the_limit` covers it.
- **R3:** "Float rounding lets a sub-cent or over-balance amount through." Refuted: line 11 rejects non-2-decimal amounts, and line 17 rounds the difference. Float error is about 1e-13, far below the 0.01 granularity.
- **R4:** "The API key is leaked." Refuted for the value: it is read from the environment and sent only in the `/refunds` header. Only the variable name can leak (F5).

## WHAT HOLDS UP

- **"The model proposes; the server enforces" is real.** Ownership, balance and limit checks use `user` from the login layer, never values from the model.
- **Amount validation is thorough.** It rejects bool, non-numeric, NaN and inf values, and amounts that are non-positive or below one cent.
- **The limit logic is cumulative and fails closed.** Over-limit requests queue for staff instead of refunding.
- **Tests assert real behaviour** for ownership, bad amounts, overpayment, limit splitting and the last-cents edge.
- **The prompt doesn't depend on the model for safety.**

## UNVERIFIED CLAIMS

- "`/refunds` rejects the post if … no longer `expected_refunded`" (`handler.py:22`). Confirm it from the API contract, or with a concurrent test against staging.
- "Set by the login layer, never by the chat" (`handler.py:14`). Confirm the source and type of `is_staff`.
- "7 tests pass" (context). Run `python -m unittest test_handler` in an isolated copy.

## QUESTIONS FOR THE AUTHOR

1. Does `/refunds` enforce `expected_refunded`, and what does it raise or return when it rejects a post?
2. Does the `llm` wrapper keep conversation history and feed tool results back to the model?
3. Does staff approval of a `/refund_requests` entry re-check the balance and the limit?
4. What format do real order IDs have, and does the api client normalise paths?

## DECISION-MAKER SUMMARY

The core guards are sound, and hostile model output cannot refund someone else's order or exceed balance or limit on a single uncontended turn. Before customers see it:
- confirm and test the `/refunds` concurrency check (F2, S1);
- validate `order_id` (F1);
- dedupe staff requests (F3);
- wire conversation history and tool results through the model (F4).

If it ships as is, the main risks are concurrent refunds bypassing the limit (if the API doesn't enforce the check) and a chat that can't hold a multi-turn conversation.

## OWNER SUMMARY

The refund assistant's main safety checks work: customers can't refund other people's orders or take back more than they paid. A few gaps need closing before launch. One protection against two refunds happening at the same moment is assumed but never tested. Order numbers typed by customers aren't checked for a valid format. Repeated requests can flood the staff approval queue. As built, the assistant also doesn't remember earlier messages in a conversation, so it will feel broken to customers until that is fixed.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "handler.py", "status": "seen", "matters": true},
    {"item": "prompts.py", "status": "seen", "matters": true},
    {"item": "system_prompt.txt", "status": "seen", "matters": true},
    {"item": "test_handler.py", "status": "seen", "matters": true},
    {"item": "real /refunds API contract (expected_refunded enforcement)", "status": "not_seen", "matters": true},
    {"item": "api client (path handling, auth, error types)", "status": "not_seen", "matters": true},
    {"item": "llm wrapper (history, tool-result handling)", "status": "not_seen", "matters": true},
    {"item": "login layer (is_staff type)", "status": "not_seen", "matters": true},
    {"item": "staff approval workflow for /refund_requests", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "handler.py", "kind": "file"},
      {"unit": "handler.py:refund", "kind": "function"},
      {"unit": "handler.py:handle_turn", "kind": "function"},
      {"unit": "prompts.py", "kind": "file"},
      {"unit": "system_prompt.txt", "kind": "file"},
      {"unit": "test_handler.py", "kind": "file"},
      {"unit": "handler.py:22 expected_refunded concurrency claim", "kind": "claim"},
      {"unit": "handler.py:14 is_staff set by login layer", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "/refunds API implementation", "reason": "not_supplied"},
      {"unit": "api client", "reason": "not_supplied"},
      {"unit": "llm wrapper", "reason": "not_supplied"},
      {"unit": "login layer", "reason": "not_supplied"},
      {"unit": "staff approval workflow", "reason": "not_supplied"},
      {"unit": "test execution and mutation runs", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "handler.py:13, handler.py:23",
     "scenario": "Customer-controlled order_id such as 'VICTIM/../MINE' is interpolated raw into the GET path; if the api client normalises it to MINE, ownership and balance checks pass on the customer's order while /refunds receives the raw, different identifier.",
     "fix": "Validate order_id as a str against a strict pattern and post order['id'] from the fetched record instead of the raw argument.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "With a mock whose get() normalises paths, turn(api, {'id': 9}, {'amount': 1, 'order_id': 'o1/x'}) posts a refund with order='o1/x'; expected 'bad order id'."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_handler.py:17-22; handler.py:22-23",
     "scenario": "The mock ignores expected_refunded, so the only concurrency guard is untested; if it regresses or the API ignores it, two concurrent 300 refunds on o2 both pass the limit check and 600 is refunded without staff approval while all tests stay green.",
     "fix": "Make the mock reject on refunded != expected_refunded and add an interleaved GET/GET/POST/POST test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete the expected_refunded key from handler.py:23 and run python -m unittest test_handler; expected a failure, by reading all 7 still pass (not run)."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "handler.py:20-21",
     "scenario": "Each repeated over-limit request posts a new /refund_requests entry; if approval does not re-check balance, approving duplicates pays out more than intended, and at minimum floods the staff queue.",
     "fix": "Dedupe against pending requests per order, include expected_refunded in the request, and rate-cap per user.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Call turn(api, {'id': 5}, {'amount': 600, 'order_id': 'o2'}) twice on one Api(); len(api.requests) == 2, expected 1."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "handler.py:26-33; system_prompt.txt:3",
     "scenario": "handle_turn passes only the current message and never returns tool results to the model, so multi-turn requests lose context, the prompt's 'tell the user what the tool said' never applies, and a successful refund returns a raw API dict to the customer.",
     "fix": "Keep per-session history, pass tool results back to the model as tool messages, and return model-composed text.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Call handle_turn with a stub llm that records its arguments: no prior turns are passed, and the success return value is a dict, not text."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:31-32",
     "scenario": "A KeyError such as an unset REFUND_API_KEY is returned verbatim to the customer, leaking internal names.",
     "fix": "Map exceptions to fixed customer-facing messages and log the details server-side.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "del os.environ['REFUND_API_KEY']; turn(Api(), {'id': 9}, {'amount': 1, 'order_id': 'o1'}) returns \"'REFUND_API_KEY'\"."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:33",
     "scenario": "A model reply with no tool call and no 'text' raises an uncaught KeyError and the turn crashes.",
     "fix": "Use reply.get('text') with a fallback message.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "handler.handle_turn(lambda s,u,m: {'tool': 'x'}, Api(), {'id': 9}, 'x') raises KeyError: 'text'."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "prompts.py:1",
     "scenario": "The prompt file is opened relative to the CWD, so starting the service from another directory fails at import.",
     "fix": "Path(__file__).with_name('system_prompt.txt').read_text().",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "From /tmp, import prompts with the repo on sys.path; FileNotFoundError is raised."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "handler.py:22-23",
     "suspicion": "The race protection may not exist server-side.",
     "unresolved_fact": "Whether /refunds rejects a post whose expected_refunded no longer matches."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "handler.py:23, handler.py:31",
     "suspicion": "A /refunds rejection may raise an uncaught exception type or be returned to the user as if it were a success.",
     "unresolved_fact": "The api client's error behaviour on a rejected post."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "handler.py:14",
     "suspicion": "A string is_staff such as 'false' would coerce to True and grant staff bypass.",
     "unresolved_fact": "The type the login layer sets for is_staff."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "handler.py:13",
     "suspicion": "A customer-controlled GET path may reach other endpoints under service credentials.",
     "unresolved_fact": "Whether the api client normalises paths and what auth api.get carries."},
    {"id": "S5", "status": "needs_validation", "track": "A", "location": "handler.py:7",
     "suspicion": "A per-order limit lets a customer with many orders self-serve 500 on each.",
     "unresolved_fact": "Whether the business rule is per order, per customer or per period."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "test_handler.py",
     "suspicion": "The claim that 7 tests pass is not run.",
     "unresolved_fact": "The output of python -m unittest test_handler in an isolated copy."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The model can override user or api via **reply['args'].", "evidence": "A duplicate keyword raises TypeError ('got multiple values'), which is caught at handler.py:31."},
    {"id": "R2", "candidate": "Splitting refunds evades LIMIT.", "evidence": "handler.py:19 checks the cumulative refunded + amount; the test_a_series_of_small_refunds test covers it."},
    {"id": "R3", "candidate": "Float rounding admits sub-cent or over-balance amounts.", "evidence": "handler.py:11 rejects non-2-decimal amounts; handler.py:17 rounds the difference to 2 places."},
    {"id": "R4", "candidate": "The API key value leaks.", "evidence": "It is read from the environment and sent only in the /refunds header; only its name can leak (F5)."}
  ]
}
```