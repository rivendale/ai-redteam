**Review conditions:** I had no tools in this session, so I ran no code and opened no links. Every result below comes from reading the files. I did not write this work, but I am the only reviewer and no fresh subagent or external seat ran. Re-run with tools before customer exposure.

---

**VERDICT: SHIP WITH FIXES.** The server-side checks hold up against hostile model output: ownership, amount validation, paid-balance and the cumulative per-order limit all survive attack. However, the one control that stops two turns spending the same balance lives in a service I was not given and the tests never check. Several customer-facing failure paths also need fixing before exposure.

**CONFIDENCE: medium.** Limited by:
- no tools, so every reproduction is traced by hand, not run;
- the refunds API, API client, login layer, LLM wrapper, chat caller and staff-approval flow were not supplied.

**INPUTS LEDGER**

| Input | Status | Does the gap matter? |
|---|---|---|
| request.md | seen | – |
| context.md | seen | – |
| handler.py | seen | – |
| prompts.py | seen | – |
| system_prompt.txt | seen | – |
| test_handler.py | seen | – |
| `/refunds` service (`expected_refunded` enforcement) | not seen | **Yes.** It is the only concurrency guard. |
| API client (`api.get` / `api.post`: auth, path handling, error behavior) | not seen | **Yes** |
| `llm` wrapper (how `user` is serialized, reply format) | not seen | Yes |
| Chat caller (what it does with a `dict` return) | not seen | Yes |
| Staff approval flow for `/refund_requests` | not seen | Yes |
| Login layer (`is_staff`, `id`) | not seen | Partly. I took the comment at face value. |

**COVERAGE**
- **Scope:** the whole work: all four files plus the request and context.
- **Checked:** `refund`, `handle_turn`, `prompts.SYSTEM` loading, the system prompt text, all 7 tests and the `Api` mock.
- **Not checked:** everything in the "not seen" rows above (`not_supplied`). The claim that the 7 tests pass was not run (`no_tools`); my hand trace says all 7 pass.

**SEATS AND GATE**
- **Gate:** passed. The work contains code only, with no personal data or credentials (`"test-only"` is a dummy).
- **Seats:** a single same-session reviewer. No subagent or cross-vendor seats (no tools).

---

### FINDINGS

**F1. Medium · PROBABLE · Track B: no idempotency, so a retried turn refunds twice**
- **Location:** `handler.py:23`
- **What is wrong:** Each turn reads `refunded` fresh and posts a refund. There is no idempotency key tied to the turn or message.
  - `expected_refunded` only stops *concurrent* turns.
  - A *sequential* replay sees the updated total and passes.
- **Failure scenario:** The chat transport or client retries a message after a timeout, or the customer double-submits "refund 10 on o2". Two refunds of 10 are posted, and money moves twice.
- **Fix:** Pass an idempotency key derived from the conversation turn or message id, and have `/refunds` dedupe on it.
- **Reproduction:** `api=Api()`, then call `turn(api,{"id":5},{"amount":10,"order_id":"o2"})` twice.
  - Observed: both return `{"amount":10,...}` and `api.orders["o2"]["refunded"]==20`.
  - Expected: the replayed turn is rejected or returns the first result.
- **a/b/c/d:** a=yes, b=no, c=yes, d=no

**F2. Medium · CONFIRMED · Track B: the tests never exercise the double-spend guard or the API key**
- **Location:** `test_handler.py:17-22` (mock `post`)
- **What is wrong:** The mock ignores `body["expected_refunded"]` and `headers`. Deleting `"expected_refunded"` from `handler.py:23`, or the `Authorization` header, still passes all 7 tests.
- **Failure scenario:** A later edit drops the guard. CI stays green, and concurrent turns can both spend one balance.
- **Fix:** Make the mock reject a `/refunds` post whose `expected_refunded` does not equal the current `refunded`. Then add these tests:
  - two turns that both read before either posts;
  - one that asserts the Bearer header is sent.
- **Reproduction (mutation):** Remove `"expected_refunded": order["refunded"]` from `handler.py:23` and run `python -m unittest test_handler`.
  - Observed (by trace): 7 pass.
  - Expected: a test goes red.
- **a/b/c/d:** a=yes, b=yes, c=no, d=no

**F3. Medium · PROBABLE · Track B/D: the system prompt describes a loop the handler does not implement**
- **Location:** `system_prompt.txt:3` and `handler.py:28-32`
- **What is wrong:** The prompt says "If a tool is refused, tell the user what the tool said". But `handle_turn` never sends the tool result back to the model:
  - an error returns the raw exception text straight to the customer;
  - a success returns the raw `/refunds` response `dict`.
  So `handle_turn` returns either `str` or `dict`.
- **Failure scenario:** After a successful refund, the customer sees a raw API body. That may include internal fields such as `by` and `expected_refunded`, or it may break the chat renderer. After a refusal, the customer sees bare strings like `"more than was paid"` with no explanation from the assistant.
- **Fix:** Feed the tool result back to the model for a customer-facing reply, or map each outcome to fixed customer text. Always return `str`. Never echo the API body.
- **Reproduction:** Call `turn(Api(),{"id":9},{"amount":5,"order_id":"o1"})`.
  - Observed: a `dict` containing `by`, `expected_refunded` and `order`.
  - Expected: customer-facing text.
- **a/b/c/d:** a=yes, b=no, c=no, d=yes

**F4. Medium · PROBABLE · Track D: money moves on the model's reading of intent, with no confirmation step**
- **Location:** `system_prompt.txt:2` and `handler.py:28-30`
- **What is wrong:** One model reply with `tool=="refund"` executes an irreversible refund immediately. The customer never confirms the amount or the order.
- **Failure scenario:** A customer asks "what would I get back if I refunded o1?" or "refund half, maybe?". The model calls `refund`, and money moves on the customer's own order without them meaning it.
- **Fix:** Use two steps:
  1. The tool returns a quote (order, amount) together with a server-held confirmation token.
  2. The refund executes only when the UI sends an explicit "confirm" for that token.
- **Reproduction:** Set the `llm` stub to return `{"tool":"refund","args":{...}}` for any message. `handle_turn` posts `/refunds` with no confirmation input in the path.
- **a/b/c/d:** a=yes, b=no, c=yes, d=no

**F5. Low · CONFIRMED · Track B: a huge integer amount raises an uncaught error**
- **Location:** `handler.py:11`
- **What is wrong:** `math.isfinite(10**400)` raises `OverflowError` (an int too large to convert to float). That error is not in the caught tuple at `handler.py:31`.
- **Failure scenario:** The customer gets the model to emit `amount: 1e400` as a JSON integer. The turn raises instead of answering "bad amount".
- **Fix:** Add `OverflowError` to the `except` tuple, or check `abs(amount) < 1e12` before calling `isfinite`.
- **Reproduction:** Call `turn(Api(),{"id":9},{"amount":10**400,"order_id":"o1"})`.
  - Observed: `OverflowError`.
  - Expected: `"bad amount"`.
- **a/b/c/d:** a=yes, b=yes, c=no, d=no

**F6. Low · CONFIRMED · Track B: catching every `KeyError` and echoing it leaks internal names**
- **Location:** `handler.py:23`, `handler.py:31-32`
- **What is wrong:** If `REFUND_API_KEY` is unset, `os.environ[...]` raises `KeyError`, which is caught. The customer then sees `'REFUND_API_KEY'`. Any missing field such as `'customer_id'` is echoed the same way.
- **Failure scenario:** A misconfigured deploy fails every refund with a confusing message that reveals an internal configuration name.
  - Meanwhile, over-limit turns still file staff requests, because `/refund_requests` does not need the key.
- **Fix:** Read the key at startup and fail fast if it is missing. Return a generic message for `KeyError`/`TypeError` and log the details server-side.
- **Reproduction:** Unset `REFUND_API_KEY`, then call `turn(Api(),{"id":9},{"amount":5,"order_id":"o1"})`.
  - Observed: `"'REFUND_API_KEY'"`.
  - Expected: a generic error, with the misconfiguration caught at startup.
- **a/b/c/d:** a=yes, b=yes, c=no, d=no

**F7. Low · CONFIRMED · Track B: a non-tool reply without `text` crashes the turn**
- **Location:** `handler.py:33`
- **What is wrong:** `reply["text"]` sits outside the `try`.
- **Failure scenario:** The model returns a malformed reply. The turn raises `KeyError` instead of answering.
- **Fix:** Use `reply.get("text")` with a fallback message.
- **Reproduction:** Call `handler.handle_turn(lambda s,u,m:{}, Api(), {"id":9}, "x")`.
  - Observed: `KeyError: 'text'`.
  - Expected: a fallback reply.
- **a/b/c/d:** a=yes, b=yes, c=no, d=no

**F8. Low · CONFIRMED · Track B: the prompt file is loaded relative to the current directory**
- **Location:** `prompts.py:1`
- **What is wrong:** `open('system_prompt.txt')` resolves against the current working directory, not the module's location.
- **Failure scenario:** The service is started from another directory, as process managers and containers often do. `import handler` fails with `FileNotFoundError`.
- **Fix:** Open `Path(__file__).with_name("system_prompt.txt")` inside a `with` block.
- **Reproduction:** From `/tmp`, run `python -c "import sys; sys.path.insert(0,'<repo>'); import handler"`.
  - Observed: `FileNotFoundError`.
  - Expected: the import succeeds.
- **a/b/c/d:** a=yes, b=yes, c=no, d=no

No finding met High or Critical. F1 and F4 carry money risk, but each depends on a condition I could not confirm: transport retries for F1, ambiguous-intent tool calls for F4.

---

### NEEDS VALIDATION

- **S1. Is the concurrency guard real?** (`handler.py:22-23`) Does `/refunds` compare `expected_refunded` to the current total atomically, as a compare-and-set in one transaction? And what does `api.post` do when it rejects? Specifically, which exception it raises, or what body it returns.
  - If it raises something outside the caught tuple, the turn crashes.
  - If it returns an error body, `handle_turn` hands that body to the customer as if the refund succeeded.
- **S2. Can `order_id` point the check and the action at different orders?** (`handler.py:13`, `handler.py:23`) `order_id` comes from the model and is unvalidated. It is interpolated into the GET path, while the raw string goes into the POST body.
  - Unsettled fact: whether the API client or server normalizes `../`, `?` or `#` so that the GET resolves to a different order than `/refunds` resolves from the body.
  - The fix is cheap either way: validate the format against a strict pattern, and post `order["id"]` from the fetched record.
- **S3. How are the other API calls authenticated?** (`handler.py:13`, `handler.py:20`) `api.get` and the `/refund_requests` post send no `Authorization` header. Unsettled fact: whether the API client carries its own credentials, and whether `/refund_requests` accepts unauthenticated posts.
- **S4. Are duplicate staff requests safe?** (`handler.py:19-21`) Every over-limit turn files a new `/refund_requests` entry, with no dedupe. Unsettled fact: whether approving one request re-checks the balance and limit, so approving two duplicates cannot pay twice.
- **S5. What does the model see about the user?** (`handler.py:27`) The whole `user` dict, including `is_staff` and possibly personal data, is passed to `llm`. Unsettled fact: which fields the login layer puts in `user`, and whether the wrapper sends them to the model.
- **S6. Do unknown orders crash the turn?** (`handler.py:13`) Unsettled fact: what the real `api.get` raises for a nonexistent order (for example an HTTP 404 error). The mock raises `KeyError`, which is caught; the real client may raise an exception that is not.
- **S7. Is the refund policy intended?** (`handler.py:10-23`) The server has no eligibility rule: no order status, refund window or returned-goods check. Any customer can self-refund any of their orders up to 500 per order just by asking. Unsettled fact: whether this matches Brightwell's refund policy.

### REFUTED

- **"The model can impersonate another user or staff through extra args."** A `user` key in `args` raises `TypeError` (multiple values for the argument), which is caught. `staff` comes from the server-side `user` dict (`handler.py:14`), not from the model.
- **"`True`, `NaN`, `inf`, strings or sub-cent amounts slip through."** `handler.py:11` rejects `bool`, non-numbers, non-finite values, values ≤ 0, and anything not equal to its 2-decimal rounding. This is tested at `test_handler.py` in `test_bad_amounts` and the sub-cent test.
- **"A series of small refunds can bypass the 500 limit."** The check is cumulative (`order["refunded"] + amount`). Covered by `test_a_series_of_small_refunds_cannot_pass_the_limit`.
- **"Float error blocks or permits the last cents."** The paid check rounds the difference to 2 places. Traced: 9.99 against 19.99 − 10.0 = 9.989999999999998 gives a difference of about 1.8e-15, which rounds to 0.0, so it is allowed.

---

### WHAT HOLDS UP
- **"The model proposes; the server enforces" is real for ownership and amount bounds.** `is_staff` and `id` come from the login layer, never from model output.
- **Validation order is sound:** amount checks, then ownership, then paid balance, then the cumulative limit. The over-limit path records a request and refuses rather than paying.
- **Malformed tool arguments return a message instead of crashing**, except in F5 and F7.

### UNVERIFIED CLAIMS
- **"/refunds rejects the post if the order's refunded total is no longer expected_refunded"** (`handler.py:22`). To confirm, read the `/refunds` handler, or run two concurrent posts against staging.
- **"7 tests in test_handler.py pass"** (context). My trace agrees, but I did not run them. Confirm with `python -m unittest test_handler`.
- **"set by the login layer, never by the chat"** (`handler.py:14`). Confirm in the login middleware.

### QUESTIONS FOR THE AUTHOR
1. Does `/refunds` enforce `expected_refunded` atomically, and what does the client do on rejection?
2. Can the chat transport retry a message, and is there a per-message id that could serve as an idempotency key?
3. Is "any own order, up to 500, on request, no eligibility check" the intended refund policy?

### DECISION-MAKER SUMMARY
- **What holds:** the refund handler's core checks hold against a manipulated model.
- **What is unproven:** the only protection against double spending lives in an API that neither the tests nor this review could see, and retries and ambiguous requests can move money.
- **What to do:** before exposure, confirm S1, then add the idempotency key (F1), a confirmation step (F4) and the guard test (F2), and clean up the customer-facing error paths (F3, F5–F8).
- **Risk if you proceed anyway:** duplicate or unintended refunds of up to 500 per order.

### OWNER SUMMARY
The assistant correctly stops customers from refunding other people's orders, refunding more than they paid, or going over the approval limit. It can still pay the same refund twice if a message is sent twice, and it can act on a vague question as though it were a request. Before customers use it, confirm the payment service blocks double spending, add a "confirm this refund" step, and tidy up the error messages customers would see.

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
    {"item": "/refunds service (expected_refunded enforcement)", "status": "not_seen", "matters": true},
    {"item": "API client implementation", "status": "not_seen", "matters": true},
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "chat caller / transport", "status": "not_seen", "matters": true},
    {"item": "staff approval flow", "status": "not_seen", "matters": true},
    {"item": "login layer", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-session-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "code only; no personal data or real credentials"},
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
      {"unit": "claim: /refunds enforces expected_refunded", "kind": "claim"},
      {"unit": "claim: 7 tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "/refunds service", "reason": "not_supplied"},
      {"unit": "API client", "reason": "not_supplied"},
      {"unit": "llm wrapper", "reason": "not_supplied"},
      {"unit": "chat caller", "reason": "not_supplied"},
      {"unit": "staff approval flow", "reason": "not_supplied"},
      {"unit": "running the tests", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "handler.py:23",
     "scenario": "A retried or double-submitted turn ('refund 10 on o2') posts two refunds; expected_refunded only stops concurrent turns, not a sequential replay.",
     "fix": "Send an idempotency key derived from the message/turn id and dedupe on it in /refunds.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "api=Api(); call turn(api,{'id':5},{'amount':10,'order_id':'o2'}) twice; observe both succeed and refunded==20; expected the replay to be rejected."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_handler.py:17-22",
     "scenario": "The mock ignores expected_refunded and headers, so a change that drops the concurrency guard or the API key still passes all tests and ships.",
     "fix": "Make the mock reject posts whose expected_refunded is stale and assert the Bearer header; add an interleaved two-turn test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete the expected_refunded key at handler.py:23 and run python -m unittest test_handler; by trace all 7 still pass; expected a failure."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "system_prompt.txt:3; handler.py:28-32",
     "scenario": "Tool results never return to the model; on success the customer receives the raw /refunds dict (by, expected_refunded), on refusal a bare exception string.",
     "fix": "Feed tool results back to the model or map outcomes to fixed customer text; always return a str and never echo the API body.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "turn(Api(),{'id':9},{'amount':5,'order_id':'o1'}) returns a dict with by/expected_refunded; expected customer-facing text."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "D",
     "location": "system_prompt.txt:2; handler.py:28-30",
     "scenario": "An ambiguous message ('what would I get back if I refunded o1?') leads the model to call refund, and money moves with no customer confirmation.",
     "fix": "Two-step flow: the tool returns a quote and a server-held token; the refund executes only on an explicit UI confirm of that token.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:11",
     "scenario": "amount=10**400 makes math.isfinite raise OverflowError, which is not caught at handler.py:31, so the turn crashes.",
     "fix": "Catch OverflowError or bound abs(amount) before isfinite.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "turn(Api(),{'id':9},{'amount':10**400,'order_id':'o1'}) raises OverflowError; expected 'bad amount'."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:23; handler.py:31-32",
     "scenario": "With REFUND_API_KEY unset, the KeyError is caught and the customer sees 'REFUND_API_KEY'; any missing field name is echoed the same way.",
     "fix": "Load the key at startup and fail fast; return a generic message for KeyError/TypeError and log details server-side.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Unset REFUND_API_KEY; turn(Api(),{'id':9},{'amount':5,'order_id':'o1'}) returns \"'REFUND_API_KEY'\"; expected a generic error."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "handler.py:33",
     "scenario": "A non-tool reply without 'text' raises KeyError outside the try, so the turn crashes.",
     "fix": "Use reply.get('text') with a fallback message.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "handler.handle_turn(lambda s,u,m:{}, Api(), {'id':9}, 'x') raises KeyError: 'text'; expected a fallback reply."},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "prompts.py:1",
     "scenario": "Started from a working directory other than the source directory, import handler fails with FileNotFoundError.",
     "fix": "open(Path(__file__).with_name('system_prompt.txt')) inside a with block.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "From /tmp: python -c \"import sys; sys.path.insert(0,'<repo>'); import handler\" raises FileNotFoundError; expected a successful import."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "handler.py:22-23",
     "suspicion": "The only concurrency guard may not be enforced atomically, and a rejection may surface as an uncaught exception or as an error body shown as success.",
     "unresolved_fact": "Whether /refunds does an atomic compare-and-set on expected_refunded, and what api.post raises or returns on rejection."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "handler.py:13; handler.py:23",
     "suspicion": "An unvalidated model-supplied order_id in the URL path could make the ownership check and the refund refer to different orders.",
     "unresolved_fact": "Whether the API client or server normalizes ../, ? or # in /orders/{id} differently from how /refunds resolves body.order."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "handler.py:13; handler.py:20",
     "suspicion": "GET /orders and POST /refund_requests send no Authorization header.",
     "unresolved_fact": "Whether the API client carries default credentials and whether /refund_requests accepts unauthenticated posts."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "handler.py:19-21",
     "suspicion": "Each over-limit turn files a duplicate staff request; approving duplicates might pay twice.",
     "unresolved_fact": "Whether the approval flow re-checks balance and limit at approval time."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "handler.py:27",
     "suspicion": "The full user dict, possibly including personal data, is sent to the model.",
     "unresolved_fact": "Which fields the login layer puts in user and what the llm wrapper serializes."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "handler.py:13",
     "suspicion": "A nonexistent order may raise an uncaught HTTP error from the real client.",
     "unresolved_fact": "The exception type the real api.get raises on 404."},
    {"id": "S7", "status": "needs_validation", "track": "A", "location": "handler.py:10-23",
     "suspicion": "There is no eligibility check (order status, refund window); any own order can be self-refunded up to 500 on request.",
     "unresolved_fact": "Whether this matches Brightwell's refund policy."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The model can override user or staff via extra tool args.", "evidence": "A duplicate 'user' kwarg raises TypeError, which is caught; staff is read from the server-side user dict (handler.py:14)."},
    {"id": "C2", "candidate": "bool, NaN, inf, string or sub-cent amounts pass validation.", "evidence": "handler.py:11 rejects all of them; tested in test_bad_amounts and the sub-cent test."},
    {"id": "C3", "candidate": "Repeated small refunds bypass the 500 limit.", "evidence": "The limit uses the cumulative order['refunded'] + amount; covered by test_a_series_of_small_refunds_cannot_pass_the_limit."},
    {"id": "C4", "candidate": "Float error blocks or permits the last cents incorrectly.", "evidence": "The paid check rounds the difference to 2 places; 9.99 against 9.989999999999998 rounds to 0.0 and is allowed."}
  ]
}
```