# Redteam report: refunds chat assistant (handler, prompt, tests)

**Reviewer note:** I am the only reviewer. No subagent or fresh instance was available, and I had no tools. Everything below comes from reading and tracing the code. Nothing was run.

**VERDICT: SHIP WITH FIXES.** The core design holds: the model proposes, the server checks ownership, the amount and the per-order limit, and the model cannot change who the user is. No confirmed finding is High or Critical. The one guarantee that protects against concurrent over-refunds depends on how the `/refunds` service behaves. That service was not supplied, and the tests do not exercise the guarantee. Settle that before customers get access.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so the "7 tests pass" claim is traced, not run.
- The `/refunds` API, the API client, the login layer and the staff-approval tool were not supplied.
- There was no independent reviewer.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, handler.py, prompts.py, system_prompt.txt, test_handler.py.
- **Not seen, and it matters:**
  - The `/refunds` service and whether it enforces `expected_refunded`. This is load-bearing for concurrency.
  - The `api` client: how it builds URLs, its default auth and the errors it raises. This matters for `order_id` handling and auth.
  - The staff-approval tool for `/refund_requests`. This matters for whether duplicate requests can pay out twice.
- **Not seen, matters less:**
  - The `llm` wrapper and how it parses tool calls.
  - The login layer, which sets `user`.
  - The chat renderer.
  - The refund policy, such as eligibility windows or order status.

**COVERAGE**
- **Scope:** the whole work as supplied.
- **Checked:**
  - all six files;
  - `refund()` line by line;
  - `handle_turn()`;
  - all seven tests, each traced against the mock;
  - the claims "the server enforces", "two turns cannot both spend the same balance" and "7 tests pass".
- **Not checked:** the external services above (not supplied), and runtime behaviour (no tools).

**SEATS AND GATE**
- **Seats:** a single same-session reviewer. No cross-vendor seats were requested.
- **Sensitivity gate:** passed. The work contains only synthetic test data and no credentials. The `"test-only"` key is a placeholder.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | handler.py:23 (call), handler.py:22 (comment); test_handler.py:17-22 | The protection against concurrent double spending rests only on `expected_refunded`. The test mock's `post` ignores that field. No test covers concurrency. | Someone later drops or misnames `expected_refunded`, or the real `/refunds` ignores it. Two concurrent turns then each pass the paid and limit checks and over-refund. All 7 tests stay green. | **Fix:** make the mock reject a `/refunds` post when `expected_refunded != orders[order]["refunded"]`. Add a test that reads the order, changes `refunded` underneath, and then posts. **Repro:** delete `"expected_refunded": ...` from handler.py:23 in a scratch copy and run `python -m unittest test_handler`. Expected: a failure. Traced result: 7 pass. | a✓ b✓ c✗ d✗ |
| F2 | Medium | CONFIRMED (traced) | B | handler.py:19-21 | Every over-limit turn files a new `/refund_requests` entry. There is no check for an open request on the same order and no idempotency key. | A customer told "a staff member has been asked to approve it" asks again 20 times, or scripts it. The staff queue gets 20 requests for the same 600 on o2. Whether approving more than one pays twice depends on the approval tool (see S5). | **Fix:** before posting, look for an open request on that order and return its status. Alternatively, send an idempotency key such as `(order, amount, user)`. **Repro:** call `turn(api, {"id":5}, {"amount":600,"order_id":"o2"})` twice on one `Api()`. Expected: `len(api.requests)==1`. Traced result: 2. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED (traced) | B | handler.py:14-15, 19; test_handler.py (no test sets `is_staff`) | The staff branch, which skips the ownership check and the 500 limit, is never tested. | Someone inverts or removes `not staff` at line 15 or 19, so staff lose the bypass or customers gain it. All 7 tests still pass. | **Fix:** add tests where a staff user refunds another customer's order and where a staff user goes over 500 directly. Add one where `{"id":5,"is_staff":False}` still hits the limit. **Repro:** in a scratch copy, change line 19 to `if order["refunded"] + amount > LIMIT:` (dropping `and not staff`). The suite stays green. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED (traced) | B | handler.py:23, 31-32 | If `REFUND_API_KEY` is unset, the resulting `KeyError` is caught as if it were a bad tool argument. The customer is shown `'REFUND_API_KEY'`. | A deploy is missing the env var. Every allowed refund silently fails, each customer sees an internal config name, and nothing alerts. | **Fix:** read the key once at import and fail fast. Catch only the exceptions `refund()` raises on purpose, and log the others. **Repro:** `del os.environ["REFUND_API_KEY"]`, then `turn(Api(), {"id":9}, {"amount":5,"order_id":"o1"})`. Expected: an error is raised or logged. Traced result: the string `"'REFUND_API_KEY'"` is returned. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED (traced) | B | prompts.py:1 | `open('system_prompt.txt')` resolves against the process's working directory, not the module's directory. | The service starts from another directory, for example under systemd or a container `WORKDIR`. The import fails with `FileNotFoundError` and the assistant is down. | **Fix:** `Path(__file__).with_name("system_prompt.txt").read_text()`. **Repro:** `cd /` and then `python -c "import sys; sys.path.insert(0,'<repo>'); import prompts"`. The import raises `FileNotFoundError`. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED (traced) | R/B | system_prompt.txt:3 vs handler.py:30-32 | The prompt tells the model to relay what the tool said. The handler never returns tool results to the model; it sends the raw exception text straight to the customer. | Customers see unexplained, terse text such as `refund() got an unexpected keyword argument 'reason'`. The prompt instruction has no effect. | **Fix:** either map each error to customer-facing wording in the handler, or feed the tool result back to the model, and align the prompt. **Repro:** use args `{"amount":5,"order_id":"o1","reason":"x"}`. Traced result: the `TypeError` text is returned verbatim. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1. Concurrency guarantee.** Does the real `/refunds` atomically reject a post when the order's refunded total is not `expected_refunded`, and does that check cover the per-order limit as well as the paid balance? This is the only protection against concurrent over-refunds. To settle it, read the `/refunds` implementation or run a two-request race against staging.
- **S2. `order_id` reaching a URL path.** `order_id` is fully controlled by the customer through the model. It is placed into `f"/orders/{order_id}"` (handler.py:13), while the POST body uses the raw string rather than the order's canonical id (handler.py:20, 23). To settle it, find out how the `api` client and server handle `/`, `..`, `?` and `#`. For example, does `o2/../o1` GET order o1 while the POST refers to something else? **Recommended regardless:** validate `order_id` against a strict pattern, and post `order["id"]` from the GET response.
- **S3. Auth on the other calls.** `api.get` and the `/refund_requests` post send no `Authorization` header, while `/refunds` does. Does the client add default credentials, or do these calls fail or run unauthenticated in production? The mock accepts anything.
- **S4. Refund policy.** Any customer can self-refund up to 500 per order with no reason, refund window or order-status check. The limit is per order, not per customer, so 10 orders allow 5,000 without staff review. Is that the intended policy? The request does not state one.
- **S5. Double payouts from duplicate requests.** Does approving duplicate queued requests (F2) re-run the paid-balance check, or could it pay twice? To settle it, read the staff-approval tool.
- **S6. Float comparison at the limit.** `order["refunded"] + amount > LIMIT` (handler.py:19) is not rounded. Is there a pair of two-decimal amounts summing to exactly 500.00 that compares as greater than 500? If so, the effect is fail-safe (an unnecessary staff request). To settle it, run a brute-force check.
- **S7. Data sent to the model provider.** The whole `user` dict goes to `llm` (handler.py:27). What fields does it hold, and is that model endpoint approved for customer data?
- **S8. Model reply handling.** A reply with no `tool` and no `text` raises an uncaught `KeyError` (handler.py:33). It is also unknown whether `reply["text"]` is rendered as markdown or HTML. To settle it, check the `llm` wrapper's output contract and the renderer.

## REFUTED

- **"Prompt injection lets the model act as another user or as staff."** `user` is passed positionally. An `args` dict containing `user` or `api` raises `TypeError` (multiple values for the argument), which is caught. `is_staff` comes only from `user` (handler.py:14).
- **"Small or sub-cent amounts dodge the paid check."** `round(amount, 2) != amount` rejects sub-cent amounts. The paid check is rounded to cents (handler.py:11, 17).
- **"A series of small refunds avoids the 500 limit."** The limit uses the cumulative `order["refunded"] + amount`. test_handler.py's `test_a_series_of_small_refunds_cannot_pass_the_limit` traces correctly.
- **"`True` or `"10"` is accepted as an amount."** Both are explicitly rejected, and the test covers them.

## WHAT HOLDS UP

- Ownership, paid-balance and limit checks are all done in code, server-side, and fail closed.
- Amount validation covers bool, non-numeric, NaN and infinity, values ≤ 0, and sub-cent amounts.
- The API key is never placed in the prompt.
- Malformed tool arguments produce a reply rather than a crash.
- All 7 tests trace as passing against the mock. Each one guards a real check, apart from the gaps in F1 and F3.

## UNVERIFIED CLAIMS

- **"/refunds rejects the post if…" (handler.py:22).** Confirm by reading the `/refunds` code or running a race test (S1).
- **"set by the login layer, never by the chat" (handler.py:14).** Confirm in the login layer.
- **"7 tests pass."** Traced, not run. Confirm with `python -m unittest test_handler`.

## QUESTIONS FOR THE AUTHOR

1. Does `/refunds` enforce `expected_refunded` atomically, and where is that code?
2. Is self-service refunding up to 500 per order, with no eligibility check, the intended policy?
3. Does the `api` client add auth to `get` and `/refund_requests`, and does it escape path segments?

## DECISION-MAKER SUMMARY

The handler's enforcement is sound for single requests. Nothing confirmed blocks launch beyond the Medium and Low fixes. Before exposing it to customers, confirm that `/refunds` really rejects stale `expected_refunded` (S1) and sanitise `order_id` (S2). If you proceed without that, concurrent or crafted requests could refund more than was paid, and the tests would not notice.

## OWNER SUMMARY

The assistant checks on the server that customers can only refund their own orders, within what they paid, and that large amounts go to staff. That part looks right. Two things still need confirming before customers use it: that the payment service blocks two refunds racing for the same money, and that unusual order numbers cannot confuse it. A few smaller fixes are also needed, including stopping repeat staff requests and closer testing of staff permissions.

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
    {"item": "/refunds service implementation", "status": "not_seen", "matters": true},
    {"item": "api client (URL building, default auth)", "status": "not_seen", "matters": true},
    {"item": "staff approval tool for /refund_requests", "status": "not_seen", "matters": true},
    {"item": "llm wrapper and chat renderer", "status": "not_seen", "matters": false},
    {"item": "login layer", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "synthetic test data only; placeholder key"},
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
      {"unit": "claim: 7 tests pass (traced, not run)", "kind": "claim"},
      {"unit": "claim: two turns cannot spend the same balance", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "/refunds service", "reason": "not_supplied"},
      {"unit": "api client", "reason": "not_supplied"},
      {"unit": "staff approval tool", "reason": "not_supplied"},
      {"unit": "runtime execution of tests", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:22-23; test_handler.py:17-22",
     "scenario": "If expected_refunded is dropped from the post or ignored by /refunds, two concurrent turns each pass the paid and limit checks and over-refund; all 7 tests stay green because the mock ignores the field.",
     "fix": "Make the mock reject /refunds posts whose expected_refunded does not match, and add a stale-read test.",
     "reproduction": "In a scratch copy remove expected_refunded from handler.py:23 and run python -m unittest test_handler; expected a failure, traced result 7 pass.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:19-21",
     "scenario": "A customer repeating an over-limit request files a new staff request each turn; 20 repeats give 20 queued requests for the same refund.",
     "fix": "Check for an open request on the order before posting, or send an idempotency key.",
     "reproduction": "Call turn(api, {'id':5}, {'amount':600,'order_id':'o2'}) twice on one Api(); expected len(api.requests)==1, traced 2.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:14-15,19; test_handler.py (no is_staff test)",
     "scenario": "Removing or inverting a 'not staff' guard goes undetected because no test exercises a staff user.",
     "fix": "Add staff-on-other-customer, staff-over-limit and explicit is_staff=False tests.",
     "reproduction": "In a scratch copy drop 'and not staff' from handler.py:19 and run the suite; traced result 7 pass.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:23,31-32",
     "scenario": "With REFUND_API_KEY unset, every allowed refund fails silently and the customer sees the string 'REFUND_API_KEY'.",
     "fix": "Load the key at import and fail fast; catch only intended exceptions and log the rest.",
     "reproduction": "Unset REFUND_API_KEY and call turn(Api(), {'id':9}, {'amount':5,'order_id':'o1'}); traced return \"'REFUND_API_KEY'\".",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "prompts.py:1",
     "scenario": "Starting the service from another working directory makes import prompts raise FileNotFoundError.",
     "fix": "Path(__file__).with_name('system_prompt.txt').read_text().",
     "reproduction": "cd / then python -c \"import sys; sys.path.insert(0,'<repo>'); import prompts\"; raises FileNotFoundError.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "system_prompt.txt:3; handler.py:30-32",
     "scenario": "The prompt tells the model to relay tool refusals, but the handler returns raw exception text straight to the customer, e.g. a TypeError signature message.",
     "fix": "Map errors to customer wording in the handler or feed results back to the model; align the prompt.",
     "reproduction": "args {'amount':5,'order_id':'o1','reason':'x'}; traced return is the raw TypeError text.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "handler.py:22-23",
     "suspicion": "Concurrent turns can over-refund if /refunds does not enforce expected_refunded atomically.",
     "unresolved_fact": "Whether the /refunds service performs an atomic compare on the refunded total."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "handler.py:13,20,23",
     "suspicion": "A customer-controlled order_id is interpolated into a URL path while the POST uses the raw string, so the GET and POST may refer to different orders.",
     "unresolved_fact": "How the api client and server handle '/', '..', '?' and '#' in order_id."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "handler.py:13,20",
     "suspicion": "GET /orders and POST /refund_requests carry no Authorization header.",
     "unresolved_fact": "Whether the api client adds default credentials."},
    {"id": "S4", "status": "needs_validation", "track": "A", "location": "handler.py:7,19",
     "suspicion": "Self-service refunds up to 500 per order with no eligibility check and no per-customer cap.",
     "unresolved_fact": "The intended refund policy."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "handler.py:20",
     "suspicion": "Approving duplicate queued requests could pay twice.",
     "unresolved_fact": "Whether the staff approval tool re-checks the paid balance."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "handler.py:19",
     "suspicion": "Unrounded float sum may push an exactly-500.00 total over LIMIT (fail-safe).",
     "unresolved_fact": "Whether any two-decimal pair summing to 500.00 compares greater than 500."},
    {"id": "S7", "status": "needs_validation", "track": "B", "location": "handler.py:27",
     "suspicion": "The full user dict is sent to the model provider.",
     "unresolved_fact": "Which fields the user dict carries and whether the endpoint is approved for them."},
    {"id": "S8", "status": "needs_validation", "track": "B", "location": "handler.py:33",
     "suspicion": "A reply with no tool and no text raises an uncaught KeyError; the rendering of reply text is unknown.",
     "unresolved_fact": "The llm wrapper's output contract and the renderer."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Model args can override user or is_staff.", "evidence": "user is positional; a 'user' key in args raises TypeError (multiple values), which is caught; is_staff is read only from user."},
    {"id": "C2", "candidate": "Sub-cent amounts bypass the paid check.", "evidence": "round(amount,2)!=amount rejects them at handler.py:11."},
    {"id": "C3", "candidate": "A series of small refunds evades LIMIT.", "evidence": "The limit uses cumulative order['refunded']+amount; the test traces correctly."},
    {"id": "C4", "candidate": "True or '10' is accepted as an amount.", "evidence": "Explicit bool and type checks at handler.py:11; covered by test_bad_amounts."}
  ]
}
```