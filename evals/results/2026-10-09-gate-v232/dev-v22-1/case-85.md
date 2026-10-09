same-context review; anchoring risk; re-run in a fresh session for anything high-stakes. (No subagent and no tools: nothing was run, and every test result below comes from tracing the code by hand.)

**VERDICT: SHIP WITH FIXES.** The core money controls hold: ownership comes from the login layer, the amount is validated, refunds are capped at what was paid, and there is a per-order limit before staff review. But duplicate staff requests, raw exception and API text reaching customers, and several unseen API guarantees need fixing or answering before customers use it.

**CONFIDENCE: medium.** It is limited by the same-context review, no tools, and missing inputs. The double-spend protection depends entirely on how the `/refunds` API behaves, and that API was not supplied.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, handler.py, prompts.py, system_prompt.txt, test_handler.py.
- **Not seen, and it matters:**
  - The real `api` client and the `/refunds` server. The race safety (`expected_refunded`) and auth depend on them.
  - The `llm` wrapper: tool schema, conversation history, output parsing.
  - The staff approval path for `/refund_requests`.
  - The refund eligibility policy.
  - The chat frontend that renders `handle_turn`'s return value.
- **Not seen, matters less:** CI output for the "7 tests pass" claim. I traced all 7 by hand and expect them to pass.

**COVERAGE**
- **Checked:**
  - `handler.py:refund`, every branch.
  - `handler.py:handle_turn`.
  - `prompts.py`.
  - `system_prompt.txt`, all 3 lines.
  - `test_handler.py`, all 7 tests traced, with mutations reasoned through.
- **Not checked:** the API server, the LLM wrapper, the approval workflow and the frontend (none supplied).

**SEATS AND GATE:**
- **Seats:** only the local same-context reviewer ran. No cross-vendor seats were requested, and no subagent was available.
- **Sensitivity gate:** not sensitive. The work holds only synthetic test data and a test-only key.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B | handler.py:19-21 | An over-limit ask posts a new `/refund_requests` entry every time. There is no dedupe and no check for an already-pending request. | A customer with order o2 (900 paid) asks for 600, is told staff will approve, then asks again twice ("any update? refund the 600"). Three 600 requests sit in the staff queue, and each passed the paid check against the same `refunded=0`. If approval does not re-check, approving two of them refunds 1200 on a 900 order. At minimum the queue fills with duplicates. | Before posting, look up pending requests for the order. Reply "already waiting for approval" instead of posting again. Reproduction: call `turn(api,{"id":5},{"amount":600,"order_id":"o2"})` twice. Expect `len(api.requests)==1`; observe 2. | a✓ b✓ c✗ d✓ |
| F2 | Medium | PROBABLE | B | handler.py:31-32; system_prompt.txt:3 | On success, `handle_turn` returns the raw `api.post` response (a dict), not chat text. Tool results never go back to the model, so the prompt line "If a tool is refused, tell the user what the tool said" can never run. The handler returns `str(exc)` directly. | A customer gets a refund, and the chat receives a dict such as `{"amount":30,"order":"o1","by":9,"expected_refunded":0.0}` (the test at line 37 asserts exactly that). Depending on the frontend, the customer sees internal fields or a broken reply. | Either feed the tool result back to the model for a final text turn, or format a fixed customer message on success. Reproduction: `test_repeated_refunds…` already shows that `handle_turn` returns a dict. | a✓ b✗ c✗ d✓ |
| F3 | Medium | CONFIRMED | B | handler.py:33-34, 24 | The broad `except (…KeyError…)` sends raw exception text to the customer and logs nothing. | Deployed without `REFUND_API_KEY`: every eligible refund replies `'REFUND_API_KEY'` to the customer, nobody is alerted, and no refund happens. An unknown order id gives `'o9'`. Missing arguments give `refund() missing 1 required positional argument: 'order_id'`. | Map known errors to fixed customer messages. Log the exception, and fail loudly on missing configuration at startup. Reproduction: unset `REFUND_API_KEY` and call a valid 10.00 refund on o1. Observe the reply `"'REFUND_API_KEY'"`. | a✓ b✓ c✗ d✗ |
| F4 | Medium | PROBABLE | A/D | system_prompt.txt:2; handler.py:31 | Money moves on a single model turn with no confirmation of the amount and order. The prompt says to call refund "when the user asks" and that "the server decides". | A customer asks "if I return this, how much would I get back?" The model reads that as a request and refunds the full amount immediately. The refund cannot be undone from the chat. | Have the tool return a pending summary first and execute only after an explicit "yes", or add a confirmation step in the prompt and the handler. Reproduction: run an LLM eval with hypothetical-phrasing prompts and count refund calls. | a✓ b✗ c✗ d✗ |
| F5 | Low | CONFIRMED | B | handler.py:11, 35 | `math.isfinite` raises `OverflowError` on a huge int, and that error is not caught. A reply with no `text` key raises `KeyError` outside the `try`. | A customer gets the model to emit `"amount": 1` followed by 400 zeros. The JSON parses to an int, `math.isfinite` raises `OverflowError`, and the turn crashes. | Reject amounts above a sane ceiling before calling `isfinite`. Catch or guard `reply.get("text")`. Reproduction: `turn(Api(),{"id":9},{"amount":10**400,"order_id":"o1"})` → `OverflowError`. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED | B | test_handler.py (whole file) | The tests never exercise the staff path, `expected_refunded`, the auth header, or concurrent turns. The fake `Api.post` ignores `expected_refunded`. | Remove `and not staff` from handler.py:16, or remove `"expected_refunded"` from line 24. By trace, all 7 tests stay green, so those guards are unprotected. | Add tests: staff refunds another customer's order; the staff limit bypass; the fake API rejects a stale `expected_refunded`; two interleaved turns where the second is rejected. Confirm each goes red under the mutation above. | a✓ b✓ c✗ d✗ |
| F7 | Low | CONFIRMED | B | prompts.py:1 | `open('system_prompt.txt')` resolves relative to the working directory, with no encoding set. | The service starts from another directory, and the import fails with `FileNotFoundError`. It fails loudly, so no data is at risk. | Resolve the path relative to `__file__`, use `encoding="utf-8"`, and use a `with` block. | a✓ b✓ c✗ d✗ |

## Confirm or refute (F1, the only High)

The strongest defence is that the approval workflow probably re-checks paid and refunded before paying. That defence addresses only the overpay part, and the approval workflow was not supplied, so overpay stays under S5. The duplicate queue entries are confirmed from lines 19-21 regardless, and repeating a request after "staff has been asked" is realistic customer behaviour. **Held** as High, scoped to the duplicates.

## NEEDS VALIDATION
- **S1:** Does `/refunds` actually reject a post when the stored `refunded` ≠ `expected_refunded`, atomically? This is the only thing stopping two concurrent turns from both passing the paid and limit checks at handler.py:17-19. *Settled by:* the API source or a contract test.
- **S2:** `api.get` (line 13) and `POST /refund_requests` (line 20) send no `Authorization` header, while `/refunds` does. *Settled by:* whether the `api` client adds auth itself, and whether `/orders/{id}` requires it.
- **S3:** `order_id` comes from the model and goes unvalidated into the URL path (line 13) and the POST body (line 24). For example, `"theirs/../mine"` could make the GET return the customer's own order (passing the ownership check) while `/refunds` acts on a different id. *Settled by:* how the client and server normalise paths and how `/refunds` resolves `order`.
- **S4:** Is the intended policy really "any paid order, any reason, any age, up to 500 per order, with no total cap across orders"? A customer can ask the chat to refund every past order under 500. *Settled by:* the written refund policy.
- **S5:** Does staff approval re-check paid and refunded and use `expected_refunded`? *Settled by:* the approval workflow code.
- **S6:** `llm` receives only the current message (line 29). Does the wrapper keep conversation history? If not, a multi-turn chat ("my order is o1" followed by "refund 30") cannot work. *Settled by:* the `llm` wrapper.
- **S7:** There is no check of order status (cancelled, charged back, unpaid). *Settled by:* whether `/refunds` enforces status itself.
- **S8:** Is LIMIT = 500 in a single currency? *Settled by:* whether orders can be multi-currency.

## REFUTED
- **R1:** "The model can escalate to staff or impersonate another user through the tool arguments." Refuted: `user` and `api` are positional, so passing `user` in `args` raises `TypeError` (caught). `is_staff` comes only from the login-layer `user` (line 15).
- **R2:** "Float error lets the last cents fail or allows sub-cent overpay." Refuted: line 17 rounds the difference (19.99−10.0 = 9.989999… still passes 9.99), and line 11 rejects amounts with more than 2 decimal places.
- **R3:** "Splitting a large refund into small ones bypasses the limit." Refuted: line 19 checks `refunded + amount`, which the series test covers.

## WHAT HOLDS UP
- The "model proposes, server enforces" design holds for identity: ownership and the staff flag never come from the chat.
- Amount validation rejects bool, str, NaN, inf, ≤0 and sub-cent values.
- The paid cap and the cumulative per-order limit are correct and tested.
- The check-and-set intent (`expected_refunded`) is the right pattern, pending S1.
- Prompt injection can at most make the model request refunds the server would allow anyway.

## UNVERIFIED CLAIMS
- **"7 tests pass":** I traced them to pass but did not run them. Confirm with `python3 -m unittest test_handler`.
- **The line-23 comment that `/refunds` rejects stale totals:** confirm with S1.
- **"set by the login layer, never by the chat" (line 15):** confirm by reading the login middleware.

## QUESTIONS FOR THE AUTHOR
1. Does `/refunds` enforce `expected_refunded` atomically?
2. What is the refund eligibility policy beyond the 500 per-order limit?
3. Does staff approval re-check balances?
4. Does the `api` client attach auth to every call?
5. How does the frontend render a dict reply?

## DECISION-MAKER SUMMARY
Fix F1 through F3 (dedupe staff requests, return customer-safe text, log and stop leaking exceptions) and answer S1, S4 and S5 before exposure. The identity and amount controls are sound. The double-spend and overpay safety rests on API behaviour nobody has shown. If you proceed anyway, the risk is duplicate or overpaid approvals and confusing customer replies, and an unanswered S1 could allow concurrent double refunds.

## OWNER SUMMARY
The assistant's basic safeguards are good: customers can only refund their own orders, never more than they paid, and large refunds go to staff. Before customers use it, it needs to stop filing the same staff request repeatedly, stop showing customers raw technical messages, and we need confirmation that the payment system blocks two refunds racing each other. We also need the written refund rules, because right now anyone can get any order under 500 refunded just by asking.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "api client and /refunds server (expected_refunded enforcement, auth)", "status": "not_seen", "matters": true},
    {"item": "llm wrapper (tool schema, history)", "status": "not_seen", "matters": true},
    {"item": "staff approval workflow for /refund_requests", "status": "not_seen", "matters": true},
    {"item": "refund eligibility policy", "status": "not_seen", "matters": true},
    {"item": "chat frontend rendering of handle_turn output", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "synthetic test data and a test-only key only"},
  "coverage": {
    "checked": [
      {"unit": "handler.py", "kind": "file"},
      {"unit": "handler.py:refund", "kind": "function"},
      {"unit": "handler.py:handle_turn", "kind": "function"},
      {"unit": "prompts.py", "kind": "file"},
      {"unit": "system_prompt.txt", "kind": "file"},
      {"unit": "test_handler.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "/refunds API server", "reason": "not supplied"},
      {"unit": "llm wrapper", "reason": "not supplied"},
      {"unit": "staff approval workflow", "reason": "not supplied"},
      {"unit": "chat frontend", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:19-21",
     "scenario": "A customer repeats an over-limit request (600 on order o2) three times; three duplicate refund_requests are queued, each valid against refunded=0, risking overpay if approval does not re-check.",
     "fix": "Check for a pending request on the order before posting; reply that it is already awaiting approval.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Call turn(api,{'id':5},{'amount':600,'order_id':'o2'}) twice; expect len(api.requests)==1, observe 2."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "handler.py:31-32; system_prompt.txt:3",
     "scenario": "On a successful refund the chat receives the raw API response dict (including internal fields such as expected_refunded) instead of a message; tool results never reach the model.",
     "fix": "Feed the tool result back to the model for a text reply, or return a fixed customer message on success.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "test_repeated_refunds_cannot_exceed_what_was_paid already asserts handle_turn returns a dict."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:24, 33-34",
     "scenario": "With REFUND_API_KEY unset, every eligible refund replies \"'REFUND_API_KEY'\" to the customer with no log or alert; unknown orders and missing arguments leak Python error text.",
     "fix": "Map errors to fixed customer messages, log exceptions, and validate config at startup.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Unset REFUND_API_KEY and request a 10.00 refund on o1; observe the reply \"'REFUND_API_KEY'\"."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "A",
     "location": "system_prompt.txt:2; handler.py:31",
     "scenario": "A customer asks hypothetically how much they would get back; the model calls refund and money moves with no confirmation step.",
     "fix": "Require an explicit confirmation turn before executing a refund.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Run an LLM eval with hypothetical-phrasing prompts and count refund tool calls."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:11, 35",
     "scenario": "amount=10**400 makes math.isfinite raise an uncaught OverflowError; a reply without 'text' raises an uncaught KeyError; the turn crashes.",
     "fix": "Bound the amount before isfinite; guard reply.get('text').",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "turn(Api(),{'id':9},{'amount':10**400,'order_id':'o1'}) raises OverflowError."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_handler.py",
     "scenario": "Removing 'and not staff' at handler.py:16, or expected_refunded at line 24, leaves all 7 tests green (by trace); the staff and concurrency guards are unprotected.",
     "fix": "Add staff-path tests and a fake API that rejects a stale expected_refunded; confirm each goes red under the mutation.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete 'and not staff' from handler.py:16 and run the tests; expect a failure, observe all 7 pass."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "prompts.py:1",
     "scenario": "The service starts from a different working directory and the import fails with FileNotFoundError.",
     "fix": "Open the prompt relative to __file__ with encoding='utf-8' in a with block.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "cd / && python3 -c 'import sys; sys.path.insert(0,\"<repo>\"); import prompts' raises FileNotFoundError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "handler.py:23-24",
     "suspicion": "Concurrent turns could both pass the paid and limit checks if /refunds does not enforce expected_refunded.",
     "unresolved_fact": "Whether /refunds rejects atomically when stored refunded != expected_refunded."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "handler.py:13, 20",
     "suspicion": "GET /orders and POST /refund_requests carry no Authorization header.",
     "unresolved_fact": "Whether the api client adds auth itself and whether those endpoints require it."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "handler.py:13, 24",
     "suspicion": "An unvalidated model-supplied order_id in the URL path could make the GET resolve to the customer's own order while /refunds acts on another.",
     "unresolved_fact": "How the client and server normalise paths and resolve the 'order' field."},
    {"id": "S4", "status": "needs_validation", "track": "A", "location": "system_prompt.txt:2; handler.py:7",
     "suspicion": "Any paid order under 500 is refunded on request with no eligibility rules and no cap across orders.",
     "unresolved_fact": "The written refund policy."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "handler.py:20",
     "suspicion": "Approving queued requests may not re-check balances.",
     "unresolved_fact": "The approval workflow code."},
    {"id": "S6", "status": "needs_validation", "track": "D", "location": "handler.py:29",
     "suspicion": "Only the current message reaches the model; multi-turn chat may not work.",
     "unresolved_fact": "Whether the llm wrapper keeps per-user history."},
    {"id": "S7", "status": "needs_validation", "track": "B", "location": "handler.py:13-19",
     "suspicion": "No order status check (cancelled, charged back, unpaid).",
     "unresolved_fact": "Whether /refunds enforces order status."},
    {"id": "S8", "status": "needs_validation", "track": "A", "location": "handler.py:7",
     "suspicion": "LIMIT is a bare number with no currency.",
     "unresolved_fact": "Whether orders can be in multiple currencies."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The model can override user or api through tool args to escalate privileges.",
     "evidence": "Passing user or api in args raises TypeError (multiple values), which is caught; is_staff comes only from the login-layer user."},
    {"id": "R2", "candidate": "Float error blocks refunding the last cents or allows sub-cent overpay.",
     "evidence": "Line 17 rounds the difference to 2 places; line 11 rejects amounts with more than 2 decimals."},
    {"id": "R3", "candidate": "A series of small refunds bypasses the limit.",
     "evidence": "Line 19 checks refunded + amount; test_a_series_of_small_refunds covers it."}
  ]
}
```