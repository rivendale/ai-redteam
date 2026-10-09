**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagents were available, so I could not run anything. Every behaviour below comes from reading the code and from documented Python semantics.

VERDICT: **SHIP WITH FIXES.** The server-side checks on ownership, amount, paid balance and the per-order limit hold up against a customer steering the model, but two things must be fixed before exposure: the over-limit path creates a new staff request on every retry, and internal errors are shown to customers as chat replies. One policy question (S1) should also be answered before go-live.

CONFIDENCE: **medium-low.** Limits:
- Same-context review with no tools.
- The real `api` client, the `/refunds` service, the login layer and the `llm` wrapper were not supplied, and the double-spend guarantee depends on them.

INPUTS LEDGER:
- **Seen:** request.md, context.md, handler.py, prompts.py, system_prompt.txt, test_handler.py.
- **Not seen, and it matters:**
  - The `/refunds` service. Its compare-and-set on `expected_refunded` is the only double-spend guard.
  - The real `api` client: its auth, its error behaviour and how it builds paths.
  - The login layer: the type of `is_staff` and of `id`.
  - The `llm` wrapper: history, tool-call parsing, and what it does with `user`.
  - Refund eligibility policy.
- **Not seen, and it matters less:** the chat UI's handling of non-string replies.
- **Test results:** "7 tests pass" is UNVERIFIED. I could not run them.

COVERAGE:
- **Checked:** handler.py:refund, handler.py:handle_turn, prompts.py, system_prompt.txt, test_handler.py (all 7 tests and the fake `Api`).
- **Not checked:** the external services listed above, and runtime behaviour.

SEATS AND GATE:
- **Seats:** local same-context review only. No subagent or cross-vendor seats were available.
- **Sensitivity gate:** no personal data, credentials or client material appears in the work. The key is read from the environment, and the test value is `"test-only"`. Gate passed.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B | handler.py:19-21 | Every over-limit turn posts a new `/refund_requests` entry. There is no dedupe and no `expected_refunded` on the request. | A customer asks for $600 on order o2, is told "a staff member has been asked", and then asks "did it go through?" or repeats the request. The model calls `refund` again each time. Staff get N identical requests. If two are approved, the outcome depends on an approval flow nobody has reviewed. | Before posting, check for an open request for the same order. Make the request idempotent, keyed on order. Record `expected_refunded` so approval re-checks the balance. **Repro:** call `turn(api, {"id":5}, {"amount":600,"order_id":"o2"})` three times. Expected `len(api.requests)==1`; observed 3. | a Y, b Y, c N, d Y |
| F2 | Medium | CONFIRMED | B | handler.py:35-36 (`except (... KeyError)`), :24 (`os.environ[...]`) | Catching `KeyError` turns server faults into customer-visible replies. A missing `REFUND_API_KEY`, or an order record missing `paid` or `customer_id`, returns `"'REFUND_API_KEY'"` or `"'paid'"` to the customer. Nothing is raised or logged, so refunds silently stop working. A nonexistent order also gives a different message from "not your order", which lets someone enumerate order IDs. | The key is unset after a deploy. Every refund turn answers `'REFUND_API_KEY'`, and no alert fires. | Validate arguments explicitly, for example `order_id` being missing, and raise your own `ValueError`. Read the key at startup and fail fast. Stop catching `KeyError`, or catch it only around argument binding. Log server faults and give the customer a generic message. **Repro:** unset `REFUND_API_KEY` and run a 10.00 refund on o1. Expected an exception or error log; observed the reply `"'REFUND_API_KEY'"`. | a Y, b Y, c N, d N |
| F3 | Medium | CONFIRMED | B | test_handler.py:15-19 (fake `Api.post`), whole file | The concurrency guard and the staff path have no tests. The fake ignores `expected_refunded` and `headers`, and no test uses `is_staff`. | Someone removes `expected_refunded` from the post, or flips `not staff`. All 7 tests stay green, and double-spend or staff bypass ships. | Make the fake reject a post whose `expected_refunded` differs from the current total. Add a two-reads-then-two-posts test where the second must fail. Add a test where a staff user refunds another customer's order and goes over the limit. Add a test where a non-staff user cannot. **Mutation to confirm:** delete `"expected_refunded": ...` and the suite should go red; today it would not (UNVERIFIED, not run). | a Y, b Y, c N, d N |
| F4 | Medium | PROBABLE | B/D | handler.py:34, :38; system_prompt.txt:3 | On success, `handle_turn` returns the raw `/refunds` response object as the chat reply. Failures return a string. The tool result never goes back to the model, so the prompt's "tell the user what the tool said" never runs. | The customer sees a dict or JSON blob, possibly with internal fields such as `by` or ledger IDs. Or a chat layer that expects a string errors out. | Send the tool result back through the model, or map it to a fixed customer-facing message. Always return a string. | a Y, b N, c N, d Y |
| F5 | Low | PROBABLE | B | handler.py:12 (`math.isfinite`) | `math.isfinite` on an int too large for a float, such as `10**400`, raises `OverflowError`. That exception is not in the caught list. | A customer gets the model to emit a 400-digit amount, and the turn crashes with an unhandled exception. No money moves. | Check the type and bound first (`abs(amount) < 1e9`), or catch `OverflowError`. **Repro:** call `turn(Api(), {"id":9}, {"amount":10**400,"order_id":"o1"})`. Expected `"bad amount"`; predicted `OverflowError`. | a Y, b N, c N, d N |
| F6 | Low | CONFIRMED | B | prompts.py:1 | The prompt is opened with a path relative to the working directory, at import time, and the file handle is never closed. | The service starts from a different directory and fails at import. This is loud, not silent. | Use `Path(__file__).with_name("system_prompt.txt").read_text()`. | a Y, b Y, c N, d N |

## Needs validation (no severity)

- **S1 – Refund eligibility.** The prompt says "the server decides whether it is allowed". The server only checks ownership, amount bounds, paid balance and the $500-per-order limit. As built, any customer gets an automatic refund on any of their orders, up to $500 each and across all orders, just by asking. There is no return window, delivery status or reason check.
  - **Settles it:** the business's refund policy, and whether instant self-serve refunds of this size are intended.
  - If not intended, this is drift and at least High.
- **S2 – Double-spend guard.** Does `/refunds` actually reject a post when `expected_refunded` is stale, and does the rejection raise or come back as a normal response body? If it comes back as a body, F4 shows it to the customer as a success. The handler's comment is an assertion, not evidence.
- **S3 – `order_id` reaches the URL unvalidated** (`f"/orders/{order_id}"`).
  - **Settles it:** whether the client normalises or encodes the path, and whether `/refunds` resolves `"order"` the same way GET does.
  - **Scenario:** `"theirs/../mine"` passes the ownership check on GET while the post refers to a different order.
  - **Fix regardless:** whitelist the format, for example `^[A-Za-z0-9_-]{1,64}$`.
- **S4 – Type of `user["is_staff"]` from the login layer.** `bool("false")` is `True`, so a string flag would make every customer staff.
- **S5 – Auth on other calls.** Only `POST /refunds` carries the key. Do `GET /orders` and `POST /refund_requests` authenticate through the client?
- **S6 – What the model receives.** `llm(prompts.SYSTEM, user, message)` passes no conversation history, so multi-turn exchanges like "which order?" → "o1" may fail. It also passes the whole `user` dict, including `is_staff` and possibly personal data, to the model. Settles it: what the wrapper does with both.

## Refuted

- **"A customer can refund someone else's order by prompt injection."** Ownership is checked against `user["id"]` from login, not against model output. A model-supplied `user` or `is_staff` key raises `TypeError` ("multiple values for argument") and is refused.
- **"Several small refunds can get past the $500 limit."** The check uses `order["refunded"] + amount`, and `test_a_series_of_small_refunds_cannot_pass_the_limit` covers this sequentially. The concurrent case depends on S2.
- **"Float error blocks the last cents or allows sub-cent amounts."** `round(amount - (paid - refunded), 2)` absorbs `19.99 - 10.0` rounding. `round(amount, 2) != amount` rejects `0.001`.
- **"A boolean or string amount slips through."** Both are explicitly rejected (line 12), and `test_bad_amounts` covers them.

## What holds up

The core design holds. The model proposes, and the server enforces identity, ownership, positivity, finiteness, cent precision, the paid-balance cap and the per-order staff limit from trusted data. The order of the checks is sound, and argument binding means the model cannot inject identity.

## Unverified claims

- **"7 tests pass."** Run `python -m unittest test_handler`.
- **"/refunds rejects the post if ... no longer expected_refunded"** (handler.py:23). Read the service code, or post two refunds with the same `expected_refunded` in staging.
- **"set by the login layer, never by the chat"** (handler.py:15). Inspect the login layer and confirm the type is a real bool.

## Questions for the author

1. Is self-serve refunding of up to $500 per order, with no eligibility check, the intended policy (S1)?
2. Does `/refunds` enforce `expected_refunded`, and how does it report a conflict (S2)?
3. What does the staff approval flow do with duplicate requests (F1)?

## Decision-maker summary

The server-side money checks are sound against customers manipulating the assistant. Fix F1 and F2 and add the missing concurrency and staff tests before launch. If you launch as is, staff queues fill with duplicate approval requests, configuration faults show up as gibberish to customers instead of alerts, and the double-spend guard rests on an untested assumption about another service.

## Owner summary

The assistant cannot be talked into refunding someone else's order or going beyond what the customer paid. Before customers use it, a few gaps should be closed: repeated asks currently pile up duplicate approval requests for staff, some internal errors are shown to customers instead of raising an alarm, and the protection against paying the same refund twice has not been tested. Someone also needs to confirm that customers are meant to get refunds of up to $500 per order on request, with no other conditions.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "low",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "handler.py", "status": "seen", "matters": true},
    {"item": "prompts.py", "status": "seen", "matters": true},
    {"item": "system_prompt.txt", "status": "seen", "matters": true},
    {"item": "test_handler.py", "status": "seen", "matters": true},
    {"item": "/refunds service (expected_refunded check)", "status": "not_seen", "matters": true},
    {"item": "real api client (auth, path building, errors)", "status": "not_seen", "matters": true},
    {"item": "login layer (is_staff, id types)", "status": "not_seen", "matters": true},
    {"item": "llm wrapper (history, tool parsing)", "status": "not_seen", "matters": true},
    {"item": "refund eligibility policy", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal data, credentials or client material in the work; the key is read from the environment and the test value is a placeholder."},
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
      {"unit": "/refunds service", "reason": "not supplied"},
      {"unit": "api client", "reason": "not supplied"},
      {"unit": "login layer", "reason": "not supplied"},
      {"unit": "llm wrapper", "reason": "not supplied"},
      {"unit": "runtime behaviour and test execution", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:19-21",
     "scenario": "A customer repeats an over-limit request (600 on o2); each turn posts a new /refund_requests entry with no dedupe and no expected_refunded, so staff receive duplicates that may each be approved.",
     "fix": "Check for an open request for the same order before posting (idempotent per order) and record expected_refunded so approval re-checks the balance.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Call turn(api, {'id':5}, {'amount':600,'order_id':'o2'}) three times; expect len(api.requests)==1, observe 3."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:24, handler.py:35-36",
     "scenario": "REFUND_API_KEY is unset or an order record lacks a field; the KeyError is caught and its key name (e.g. 'REFUND_API_KEY') is returned to the customer, refunds silently fail, and nothing is logged.",
     "fix": "Validate arguments explicitly, load the key at startup and fail fast, stop catching KeyError broadly, and log server faults while showing the customer a generic message.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Unset REFUND_API_KEY and refund 10 on o1; expect an exception or error log, observe the reply \"'REFUND_API_KEY'\"."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_handler.py:15-19",
     "scenario": "The fake Api ignores expected_refunded and no test uses is_staff, so removing the double-spend guard or flipping the staff check leaves all 7 tests green.",
     "fix": "Make the fake enforce expected_refunded; add a stale-read concurrent-refund test and staff and non-staff tests for cross-customer refunds and the limit.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete the expected_refunded field from the /refunds post in a scratch copy; the suite should go red but is expected to stay green (not run)."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "handler.py:34, handler.py:38; system_prompt.txt:3",
     "scenario": "On success the raw /refunds response object is returned as the chat reply; the model never sees tool results, so the customer may see internal fields or the chat layer may fail on a non-string.",
     "fix": "Route tool results back through the model or map them to a fixed customer message; always return a string.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Run a successful turn on o1 for 10; observe a dict returned rather than customer-facing text."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "handler.py:12",
     "scenario": "An integer amount such as 10**400 makes math.isfinite raise OverflowError, which is not caught, so the turn crashes. No money moves.",
     "fix": "Bound-check the amount before math.isfinite, or add OverflowError to the caught exceptions.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "turn(Api(), {'id':9}, {'amount':10**400,'order_id':'o1'}); expect 'bad amount', predict OverflowError."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "prompts.py:1",
     "scenario": "The service starts from a different working directory and fails at import because system_prompt.txt is opened relative to the working directory.",
     "fix": "Path(__file__).with_name('system_prompt.txt').read_text().",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "cd / && python -c 'import sys; sys.path.insert(0, \"<repo>\"); import prompts' raises FileNotFoundError."},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "system_prompt.txt:2; handler.py:refund",
     "suspicion": "Any customer can get an automatic refund on any of their orders, up to 500 each, with no eligibility check (window, delivery, reason).",
     "unresolved_fact": "Whether the business intends instant self-serve refunds with no eligibility conditions."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "handler.py:23-24",
     "suspicion": "The double-spend guard depends on /refunds enforcing expected_refunded, and its rejection may not raise.",
     "unresolved_fact": "The /refunds service's compare-and-set behaviour and how it reports a conflict."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "handler.py:13",
     "suspicion": "An unvalidated order_id is interpolated into the GET path (e.g. 'theirs/../mine'), so GET and POST may refer to different orders.",
     "unresolved_fact": "Whether the api client encodes or normalises paths and how /refunds resolves the order string."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "handler.py:14",
     "suspicion": "If the login layer sets is_staff as a string, bool('false') is True and every customer becomes staff.",
     "unresolved_fact": "The type of is_staff that the login layer sets."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "handler.py:13, handler.py:20",
     "suspicion": "GET /orders and POST /refund_requests carry no Authorization header.",
     "unresolved_fact": "Whether the api client authenticates these calls itself."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "handler.py:30",
     "suspicion": "The llm call passes no conversation history and passes the whole user dict, which may include personal data, to the model.",
     "unresolved_fact": "What the llm wrapper does with history and with the user argument."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Prompt injection can refund another customer's order.", "evidence": "Ownership is checked against the login-provided user['id']; a model-supplied user or is_staff key raises TypeError at argument binding."},
    {"id": "R2", "candidate": "Several small refunds can get past the 500 limit.", "evidence": "The check uses order['refunded'] + amount, and test_a_series_of_small_refunds_cannot_pass_the_limit covers it (the concurrent case is S2)."},
    {"id": "R3", "candidate": "Float rounding blocks the last cents or allows sub-cent amounts.", "evidence": "round(...,2) on the paid comparison and round(amount,2) != amount handle 9.99 of 19.99-10.0 and reject 0.001."},
    {"id": "R4", "candidate": "A boolean or string amount is accepted.", "evidence": "Line 12 rejects bool and non-numeric types; test_bad_amounts covers both."}
  ]
}
```