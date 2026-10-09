> Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. This session has no tools and no subagent, so I traced the code by hand, ran nothing, and opened nothing.

**VERDICT: SHIP WITH FIXES.** The server-side limits in `refund()` hold against every hostile amount and argument I traced. But tool results go straight to the customer as raw dicts and Python error text, `order_id` is never validated, and the only double-spend guard is untested. Several facts that decide whether this is safe for real money were not supplied.

**CONFIDENCE: low.** Reasons: same-context review, no tools, and four unsupplied artifacts that the safety claims depend on: the API client, the `/refunds` service, the LLM wrapper and the refund policy.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, handler.py, prompts.py, system_prompt.txt, test_handler.py.
- **Not seen:**
  - The real `api` client (auth, path handling, whether `post()` accepts `headers=`). **Matters.**
  - The `/refunds` service and its `expected_refunded` check. **Matters:** it is the only concurrency guard.
  - The `llm` wrapper (tool-call parsing, conversation history). **Matters.**
  - Brightwell's refund policy (eligibility, refund window). **Matters.**
  - The login layer that sets `is_staff`. Matters less, since its trust is stated.
  - Output of the 7 tests. "7 pass" is UNVERIFIED; my hand trace says each would pass.

**COVERAGE**
- **Checked:**
  - handler.py: `refund`, `handle_turn`, `LIMIT`
  - prompts.py
  - system_prompt.txt
  - test_handler.py: all 7 tests and the fake `Api`
  - Assumption: "the server enforces"
  - Assumption: the CAS comment at handler.py:22
- **Not checked:** the real API client, the refunds service, the LLM wrapper, the login layer, and deployment config (working directory, how `REFUND_API_KEY` is supplied).

**SEATS AND GATE:** Single same-context reviewer. No subagent or cross-vendor seats were available. Sensitivity gate passed: there is no personal data, and the only credential is the test value `"test-only"`.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | handler.py:30-33, 23; system_prompt.txt:3; test_handler.py:63-64 | Tool results never return to the model. They go straight to the customer. On success the customer gets the raw `/refunds` API response (a dict). On failure they get raw Python exception text. The prompt's "tell the user what the tool said" can never run. | A customer whose LLM call omits `order_id` sees `refund() missing 1 required positional argument: 'order_id'`. If `REFUND_API_KEY` is unset, the caught `KeyError` sends the customer `'REFUND_API_KEY'`. A successful refund shows whatever internal fields the refunds API returns. The test at :63-64 locks in the leak. | Feed the tool result back to the model, or map it to fixed customer-facing strings. Never return `str(exc)` for `TypeError` or `KeyError`. Reproduction: `turn(Api(), {"id": 9}, {"amount": 5})` returns the function signature text. Expect a fixed message instead. | a✓ b✓ c✗ d✓ |
| F2 | Medium | CONFIRMED | B | handler.py:13, 23 | `order_id` comes from the model, so the customer controls it. It can be any JSON value, and it goes unvalidated into a URL path. The refund is then posted against that raw string, not the id of the order that passed the ownership check. | A customer types "my order is `o1/../../internal/x`". The model passes it through, and the handler does `GET /orders/o1/../../internal/x` with the service client's credentials. A non-order response raises `KeyError`, which is caught and echoed back per F1, so internal endpoints can be probed through chat. | Validate `order_id` against a strict pattern (for example `^[A-Za-z0-9_-]{1,64}$`) before use. In the `/refunds` body, send the id from the fetched order. Test: `turn(Api(), {"id": 9}, {"amount": 5, "order_id": "o1/../x"})` should return "bad order" with no `api.get` call. | a✓ b✓ c✗ d✗ |
| F3 | Medium | CONFIRMED | B | test_handler.py:13-19; handler.py:22-23 | The double-spend guard (`expected_refunded`) exists only as a comment. The fake `Api.post` reads only `body["order"]` and `body["amount"]`. It ignores `expected_refunded` and headers, so no test fails if the guard is removed. | A refactor drops `expected_refunded` and all 7 tests stay green. Two concurrent turns on o2 each read `refunded=0`, each pass the 500 check, and 600 is refunded with no staff approval. | Make the fake enforce compare-and-swap: reject when `body["expected_refunded"] != order["refunded"]`. Add a test that interleaves two `refund()` calls between their GET and POST. Mutation check: delete the field and confirm the test goes red. | a✓ b✓ c✗ d✗ |
| F4 | Medium | PROBABLE | A/B | system_prompt.txt:2; handler.py:28-30 | Real money moves on the first tool call, with no confirmation step. The prompt says to call `refund` "when the user asks for a refund", and the model's reading of a question decides it. | A customer asks "could I get my $40 back on o1 if it arrives late?" The model calls `refund(40, "o1")` and $40 is refunded at once. That cannot be undone. | Have the model propose, show amount and order, and require an explicit "yes" on a later turn. Or bind a server-issued confirmation token to the amount and order. | a✓ b✗ c✗ d✓ |
| F5 | Low | CONFIRMED | B | handler.py:19-21 | Each over-limit attempt posts a new `/refund_requests` record. Nothing deduplicates them. | A customer repeats "refund 600 on o2" ten times and the staff queue holds ten requests for the same refund. | Dedupe on (order, amount, user) for open requests, or check for an existing open request first. Test: two over-limit turns should give `len(api.requests) == 1`. | a✓ b✓ c✗ d✓ |
| F6 | Low | CONFIRMED | B | handler.py:33; handler.py:31 | A model reply with neither `tool == "refund"` nor a `"text"` key raises an uncaught `KeyError` at :33. Exceptions from the real API client other than the four caught types also escape `handle_turn`. | The model returns an unknown tool call or a malformed reply. The turn throws and the customer gets a chat-layer error. | Use `reply.get("text")` with a fallback, and catch API client errors explicitly. | a✓ b✓ c✗ d✗ |
| F7 | Low | CONFIRMED | B | prompts.py:1 | The prompt is read from a path relative to the working directory, and the file is never closed. | A deploy whose working directory differs from the code directory fails at import with `FileNotFoundError`. | Resolve the path relative to `__file__`. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1 (refund policy).** Any customer can self-refund each of their orders up to 500, with no check on order status, refund window, returned goods, or an existing chargeback. Fact that settles it: Brightwell's written refund policy. If refunds need eligibility conditions, this is High drift: the server does not enforce "allowed".
- **S2 (CAS guard).** Does `/refunds` actually reject when the refunded total ≠ `expected_refunded`? Fact that settles it: the refunds service code, or a live test.
- **S3 (API auth).** `GET /orders` and `POST /refund_requests` carry no `Authorization` header; only `/refunds` does. Facts that settle it:
  - Does the client add auth itself?
  - Does its `post()` accept `headers=`? If not, every refund turns into a caught `TypeError`, which is echoed back per F1.
- **S4 (cross-order refund).** Could a crafted `order_id` make the GET resolve to the customer's own order while `/refunds` resolves the raw string to another order? Fact that settles it: how the client normalizes paths, and how `/refunds` resolves its `order` field. If it can, this is Critical.
- **S5 (conversation history).** `handle_turn` passes only the current message to the model. Fact that settles it: whether the `llm` wrapper keeps conversation history. Without it, multi-turn refund chats break.
- **S6 (staff use).** Staff bypass ownership and the limit (handler.py:14-19) with no confirmation. Fact that settles it: do staff use this assistant and paste customer text into it? If so, a prompt injected through that text could drive unlimited refunds.

## REFUTED

- **The model overrides `user` or `api` through `**args`.** Refuted: `refund(api, user, **{"user": ...})` raises `TypeError` ("multiple values"), which is caught. The identity comes only from the login layer.
- **Bool, NaN, inf, string or sub-cent amounts get through.** Refuted: handler.py:11 rejects all of them.
- **A series of small refunds passes the 500 limit.** Refuted: :19 adds the amount to `refunded`. That holds for sequential turns; for concurrent turns see F3 and S2.
- **Float error blocks refunding the last cents.** Refuted: `round(..., 2)` at :17 absorbs it. `9.99` against a remaining `9.989999…` passes.
- **A customer escalates to staff through chat.** Refuted: `is_staff` is read from `user`, which the model never sets.

## WHAT HOLDS UP

The enforcement in `refund()` is ordered correctly: validate the amount, check ownership, check the paid balance, then the cumulative limit, then post. It holds against every hostile amount and argument shape I traced. Staff status cannot be reached from chat. The tests cover the main bounds.

## UNVERIFIED CLAIMS

- **"7 tests pass."** To confirm: run `python -m unittest test_handler`.
- **The handler.py:22 claim that `/refunds` rejects a stale `expected_refunded`.** To confirm: the service code or an integration test (S2).
- **"the server decides whether it is allowed."** To confirm: the refund policy (S1).

## QUESTIONS FOR THE AUTHOR

1. What makes a refund eligible beyond amount and ownership? (Settles S1.)
2. Does `/refunds` enforce `expected_refunded`, and does the API client authenticate GET and `/refund_requests`? (Settles S2 and S3.)
3. Does the `llm` wrapper keep history and feed tool results back to the model? (Settles S5 and the shape of F1's fix.)

## DECISION-MAKER SUMMARY

Fix these before exposing the assistant to customers:
- **F1:** raw API and exception output reaches customers.
- **F2:** `order_id` is unvalidated, and the refund is posted against the raw string.
- **F3:** the double-spend guard is untested.
- **F4:** there is no confirmation step.

Get written answers on S1–S4 first. If refunds need eligibility conditions, or `/refunds` does not enforce `expected_refunded`, the assistant will pay out money it should not.

## OWNER SUMMARY

The money limits in the refund code are sound: customers cannot refund other people's orders, refund more than they paid, or go past the approval threshold one request at a time. Before customers use it:
- Customers can see internal system messages.
- The order number they type is never checked.
- A refund goes through without the customer confirming it.
- The protection against two simultaneous refunds has never been tested.

Someone also needs to confirm the refund policy and how the payment system guards against duplicate refunds, because this review could not see either.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "low",
  "inputs_ledger": [
    {"item": "handler.py", "status": "seen", "matters": true},
    {"item": "prompts.py", "status": "seen", "matters": true},
    {"item": "system_prompt.txt", "status": "seen", "matters": true},
    {"item": "test_handler.py", "status": "seen", "matters": true},
    {"item": "real api client (auth, path handling, post signature)", "status": "not_seen", "matters": true},
    {"item": "/refunds service expected_refunded enforcement", "status": "not_seen", "matters": true},
    {"item": "llm wrapper (history, tool-call parsing)", "status": "not_seen", "matters": true},
    {"item": "Brightwell refund policy", "status": "not_seen", "matters": true},
    {"item": "login layer setting is_staff", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data; only a test-only key value."},
  "coverage": {
    "checked": [
      {"unit": "handler.py", "kind": "file"},
      {"unit": "handler.py:refund", "kind": "function"},
      {"unit": "handler.py:handle_turn", "kind": "function"},
      {"unit": "prompts.py", "kind": "file"},
      {"unit": "system_prompt.txt", "kind": "file"},
      {"unit": "test_handler.py", "kind": "file"},
      {"unit": "the server enforces refund policy", "kind": "assumption"},
      {"unit": "handler.py:22 CAS comment", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "api client", "reason": "not supplied"},
      {"unit": "/refunds service", "reason": "not supplied"},
      {"unit": "llm wrapper", "reason": "not supplied"},
      {"unit": "refund policy", "reason": "not supplied"},
      {"unit": "deployment config", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:30-33; system_prompt.txt:3; test_handler.py:63-64",
     "scenario": "Tool results bypass the model: a successful refund returns the raw /refunds response dict to the customer, and failures return raw exception text such as \"refund() missing 1 required positional argument: 'order_id'\" or \"'REFUND_API_KEY'\".",
     "fix": "Feed tool results back to the model or map them to fixed customer-facing messages; never return str(exc) for TypeError/KeyError.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "turn(Api(), {'id': 9}, {'amount': 5}) returns the function-signature text; expect a fixed message."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:13, 23",
     "scenario": "A customer-controlled order_id such as 'o1/../../internal/x' is interpolated unvalidated into the GET path under service credentials, and the resulting KeyError is echoed back, so internal endpoints can be probed; the refund is posted against the raw string, not the fetched order's id.",
     "fix": "Validate order_id against a strict pattern before use; post the refund with the fetched order's id.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "turn(Api(), {'id': 9}, {'amount': 5, 'order_id': 'o1/../x'}) should return 'bad order' without calling api.get."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_handler.py:13-19; handler.py:22-23",
     "scenario": "The fake Api ignores expected_refunded, so removing the double-spend guard leaves all 7 tests green; two concurrent 300 refunds on o2 would then total 600 without staff approval.",
     "fix": "Make the fake reject when expected_refunded != order['refunded'] and add an interleaved-turn test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete expected_refunded from handler.py:23 and run the tests in a scratch copy; all 7 still pass."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "system_prompt.txt:2; handler.py:28-30",
     "scenario": "A customer asking whether a refund is possible is refunded immediately because the model calls refund on the first turn with no confirmation step.",
     "fix": "Require an explicit confirmation turn, or a server-issued token bound to the amount and order, before calling /refunds.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:19-21",
     "scenario": "Repeating an over-limit request queues a duplicate staff approval request each time.",
     "fix": "Deduplicate open refund requests by order, amount and user.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Two over-limit turns on o2 give len(api.requests) == 2; expect 1."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:31, 33",
     "scenario": "A model reply with no 'text' key, or an API client error outside the four caught types, raises out of handle_turn.",
     "fix": "Use reply.get('text') with a fallback and catch API client errors explicitly.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "handle_turn(lambda s, u, m: {}, Api(), {'id': 9}, 'x') raises KeyError."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "prompts.py:1",
     "scenario": "Starting the service from a different working directory fails at import with FileNotFoundError.",
     "fix": "Open the file via a path relative to __file__, using a with block.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "cd / && python -c 'import sys; sys.path.insert(0, \"<repo>\"); import prompts' raises FileNotFoundError."},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "handler.py:10-23",
     "suspicion": "Any customer can self-refund each own order up to 500 with no eligibility, window or chargeback check.",
     "unresolved_fact": "Brightwell's refund policy: what makes a refund eligible."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "handler.py:22-23",
     "suspicion": "The double-spend protection may not exist server-side.",
     "unresolved_fact": "Whether /refunds rejects posts whose expected_refunded is stale."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "handler.py:13, 20, 23",
     "suspicion": "GET /orders and POST /refund_requests send no Authorization header, and the real post() may not accept headers=.",
     "unresolved_fact": "The real api client's auth handling and post() signature."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "handler.py:13, 23",
     "suspicion": "A crafted order_id could pass ownership on the customer's own order via GET normalization while /refunds resolves the raw string to another order.",
     "unresolved_fact": "How the client normalizes paths and how /refunds resolves its 'order' field."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "handler.py:27",
     "suspicion": "Only the current message reaches the model, so multi-turn refund conversations break.",
     "unresolved_fact": "Whether the llm wrapper keeps conversation history."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "handler.py:14-19",
     "suspicion": "Staff bypass ownership and the limit with no confirmation, so injected text pasted by staff could drive unlimited refunds.",
     "unresolved_fact": "Whether staff use this assistant and paste customer-supplied text into it."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The model can override user or api via **args.", "evidence": "Duplicate keyword raises TypeError ('multiple values'), caught at handler.py:31."},
    {"id": "R2", "candidate": "Bool, NaN, inf, string or sub-cent amounts pass validation.", "evidence": "handler.py:11 rejects each."},
    {"id": "R3", "candidate": "A series of small sequential refunds passes the 500 limit.", "evidence": "handler.py:19 adds the amount to the order's refunded total."},
    {"id": "R4", "candidate": "Float error blocks refunding the final cents.", "evidence": "round(..., 2) at handler.py:17 absorbs the representation error (9.99 vs 9.989999...)."},
    {"id": "R5", "candidate": "A customer can escalate to staff through chat.", "evidence": "is_staff is read from user, set by the login layer; the model never sets it."}
  ]
}
```