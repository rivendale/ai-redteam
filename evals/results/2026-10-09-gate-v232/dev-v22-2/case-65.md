**Single reviewer, same session, no tools:** anchoring risk applies. Re-run in a fresh session for anything high-stakes. No code was executed; every CONFIRMED item below comes from tracing the code by hand.

**VERDICT: SHIP WITH FIXES.** The safety design holds: the model only picks from a fixed list, nothing runs through a shell, changes wait for staff, and the posted text and image cannot carry model or customer text. But a malformed model reply or a missing binary crashes the handler, and the ticket then gets no status.

**CONFIDENCE: medium.** It is limited by:
- no tools, so the "6 tests pass" claim was not re-run;
- the callables that are passed in (`llm`, `post`, `run`, `request_approval`) and the badge service were not supplied.

**INPUTS LEDGER**
- **Seen:** the original request (verbatim), context.md, bot.py and test_bot.py.
- **Not seen, and matters:** the production wiring of `request_approval`. The safety claim depends on it.
- **Not seen, and matters:** the badge service at `status.example.test`. The "status image" requirement depends on it.
- **Not seen, and matters:** the ticket-queue consumer. Crash containment and retries depend on it.
- **Not seen, matters less:** the `llm` and `post` clients.
- **Not seen, matters less:** a test run log.

**COVERAGE**
- **Checked:** bot.py, every function (`ask_model`, `summarize`, `handle`, `status_markdown`, `process`), and test_bot.py, all 6 tests.
- **Not checked:** the injected callables, the badge service, the queue consumer, and actual test execution.

**SEATS AND GATE**
- Local reviewer only.
- Sensitivity gate: the work is not sensitive. The card number in the tests is the standard fake test card 4111…. Production tickets will hold customer data, which is a deploy concern, not a property of this work.
- No cross-vendor seats were requested.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | bot.py `handle`: `if action in NEEDS_APPROVAL:` runs before `isinstance(action, str)` | Testing membership in a set hashes the value. A list or dict `action` raises `TypeError: unhashable type`, which the `except (ValueError, AttributeError)` does not catch, because the type guard comes one line too late. | A customer ticket nudges the model to reply `{"action": ["restart_web"]}`. Or the model emits that shape on its own. `handle` raises, `process` never calls `post`, and the ticket gets no status. If the consumer retries, the same ticket fails every time (a poison message). | Put `if not isinstance(action, str): return "no action"` straight after the parse, before the approval check. **Repro:** `bot.handle(lambda p: '{"action": ["restart_web"]}', 7, "x", lambda *a, **k: None, lambda t, a: None)`. Expected `"no action"`; you get `TypeError`. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (traced) | B | bot.py `handle`: `except subprocess.TimeoutExpired` | Only a timeout is caught. `FileNotFoundError` (no `systemctl` in a container without systemd, or no `du`) and `PermissionError` propagate. | The bot is deployed to a container without `systemctl`. Every `web_status` ticket raises, and nothing is posted. | Also catch `OSError` and return `"action failed"`. **Repro:** pass `run` that raises `FileNotFoundError`. Expected `"action failed"`; you get an exception. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED | B | bot.py `status_markdown`: `https://status.example.test/badge.png` | The image host is hard-coded, and `.test` is a reserved top-level domain that never resolves (RFC 6761). | Deployed as written, every posted status image is broken. | Move the badge base URL into config, and fail at startup if it is unset or a reserved domain. | a✓ b✓ c✗ d✗ |

No Critical or High findings. The safety-relevant candidates were each re-examined and refuted (see REFUTED below).

### NEEDS VALIDATION

- **S1. Approval wiring and execution.** The bot cannot carry out an approved change: there is no command for `restart_web` or `clear_cache`.
  - To settle: whether production `request_approval` really puts the request in front of staff, and what executes the action once approved.
  - The request says "carries out the action". The only path for changes is "queued", so the request is met only if another system finishes the job.
- **S2. Status image content.** The URL carries only the ticket id, and the bot never reports the outcome anywhere.
  - To settle: whether the badge service gets per-ticket status from another source. If not, the image cannot reflect the status.
- **S3. `llm` return type.** If the client returns `None`, `json.loads(None)` raises an uncaught `TypeError`.
  - To settle: whether the client is guaranteed to return `str` or `bytes`.
- **S4. Ticket id format.** `int(ticket_id)` raises `ValueError` on ids like `"TCK-123"`, after the action has already run.
  - To settle: what the id format in the queue is.
- **S5. Approval flooding.** Any customer can phrase a ticket so that it files a restart request. That trains staff to rubber-stamp.
  - To settle: whether the approval queue de-duplicates, rate-limits, or shows the ticket text next to the request.
- **S6. "6 tests pass".** Not re-run here (see UNVERIFIED CLAIMS).

### REFUTED

- **Prompt injection leads to command execution.** The model's text only selects a key. `READ_ONLY` maps keys to fixed argv lists, and no shell is involved (`test_text_that_is_not_json_does_nothing`, `test_unknown_action_does_nothing`).
- **A change runs without approval.** The `NEEDS_APPROVAL` branch returns before `run` is ever called, and the test asserts `ran == []`.
- **Markdown or image injection through the summary.**
  - The summary is either a fixed string or a fixed prefix plus the first token (at most 20 characters) of output from fixed local commands. The model and the customer control neither.
  - The image URL uses `int(ticket_id)`.
- **Raw command output is posted.** Only `words[0]` is used, and `test_command_output_is_not_posted_as_it_is` covers this.
- **A stopped service is reported as a failure.** Exit code 3 is special-cased, and a test covers it.

### WHAT HOLDS UP

- The fixed action allow-list.
- Commands run as argv with no shell, with a 30-second timeout.
- The approval gate for anything that changes production.
- A posted summary that cannot carry injected text, and an image URL that carries only an integer id.
- **The tests guard real behavior, by reasoning:**
  - Removing the exit-code-3 exception would turn the stopped-service test red.
  - Putting the summary into the URL would turn the image test red.
  - Running approval actions would turn the approval test red.
  - None of this mutation testing was actually run.

### UNVERIFIED CLAIMS

- **"6 tests pass":** run `python3 -m unittest test_bot` in a scratch copy.
- **"request_approval must put the request in front of staff":** read the production wiring.

**Test gap:** no test covers a non-string `action`, an `OSError` from `run`, or `process` end to end.

### QUESTIONS FOR THE AUTHOR

1. What executes `restart_web` or `clear_cache` after staff approve?
2. Where does the badge service get each ticket's status, and what is the real host?
3. Does the queue consumer catch exceptions from `process`, or retry them?

### DECISION-MAKER SUMMARY

The safety design is sound: customers cannot make the bot run arbitrary commands or change production without staff. Fix F1 and F2 (a one-line type guard and a broader exception catch) and replace the placeholder image host before connecting the queue. If you proceed as is, odd model replies and environment gaps will leave tickets silently without a status, and the status image will be broken.

### OWNER SUMMARY

The bot is safe in the ways that matter most: customers cannot use it to run their own commands, and any change to the live system waits for a person. A few unusual situations will make it stop without posting anything to the ticket, and the status picture points at a placeholder address that will not load. These are small fixes to make before it goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request_approval production wiring", "status": "not_seen", "matters": true},
    {"item": "badge service status.example.test", "status": "not_seen", "matters": true},
    {"item": "ticket queue consumer", "status": "not_seen", "matters": true},
    {"item": "llm and post clients", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; 4111... is a standard test card number."},
  "coverage": {
    "checked": [
      {"unit": "bot.py", "kind": "file"},
      {"unit": "bot.py:ask_model", "kind": "function"},
      {"unit": "bot.py:summarize", "kind": "function"},
      {"unit": "bot.py:handle", "kind": "function"},
      {"unit": "bot.py:status_markdown", "kind": "function"},
      {"unit": "bot.py:process", "kind": "function"},
      {"unit": "test_bot.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "test execution", "reason": "no tools in this session"},
      {"unit": "request_approval, llm, post, run implementations", "reason": "not supplied"},
      {"unit": "badge service", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:handle, `if action in NEEDS_APPROVAL` before the isinstance check",
     "scenario": "Model replies {\"action\": [\"restart_web\"]} (customer-induced or a malformed reply); set membership raises an uncaught TypeError (unhashable type); nothing is posted to the ticket, and a retrying consumer fails on it every time.",
     "fix": "Return \"no action\" when action is not a str, immediately after parsing and before the approval check.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "bot.handle(lambda p: '{\"action\": [\"restart_web\"]}', 7, 'x', lambda *a, **k: None, lambda t, a: None): expected 'no action', observe TypeError."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:handle, `except subprocess.TimeoutExpired`",
     "scenario": "On a host without systemctl or du, run raises FileNotFoundError, which is not caught; the ticket gets no status.",
     "fix": "Also catch OSError and return \"action failed\".",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Pass a run that raises FileNotFoundError: expected 'action failed', observe the exception propagating."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:status_markdown, https://status.example.test/badge.png",
     "scenario": "Deployed as written, the status image points at a reserved .test domain that never resolves, so every posted image is broken.",
     "fix": "Make the badge base URL configuration, validated at startup.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Render status_markdown(7, 'x') and resolve status.example.test: NXDOMAIN by RFC 6761."},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "bot.py:handle NEEDS_APPROVAL branch",
     "suspicion": "Approved changes are never carried out by the bot; the requirement 'carries out the action' depends on an unseen system.",
     "unresolved_fact": "What real request_approval does and what executes an action after approval."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "bot.py:status_markdown image URL",
     "suspicion": "The image carries only the ticket id and the bot never reports the outcome, so the image may not show the status.",
     "unresolved_fact": "Whether the badge service obtains per-ticket status from another source."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "bot.py:handle json.loads(ask_model(...))",
     "suspicion": "An llm client returning None raises an uncaught TypeError.",
     "unresolved_fact": "The return-type contract of the llm client."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "bot.py:status_markdown int(ticket_id)",
     "suspicion": "Non-numeric ticket ids raise ValueError after the action has already run.",
     "unresolved_fact": "The ticket id format in the production queue."},
    {"id": "S5", "status": "needs_validation", "track": "D", "location": "bot.py:handle NEEDS_APPROVAL branch",
     "suspicion": "Customers can make every ticket file a restart request, inducing approval fatigue.",
     "unresolved_fact": "Whether the approval queue de-duplicates, rate-limits, or shows ticket context."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Prompt injection leads to command execution.", "evidence": "The model output only selects a key in READ_ONLY's fixed argv lists; no shell is used."},
    {"id": "C2", "candidate": "A change runs without approval.", "evidence": "The NEEDS_APPROVAL branch returns before run is called; the test asserts ran == []."},
    {"id": "C3", "candidate": "Markdown or URL injection through the posted status.", "evidence": "The summary is a fixed prefix plus the first token (at most 20 chars) of output from fixed commands; the URL uses int(ticket_id)."},
    {"id": "C4", "candidate": "Raw command output is posted to the customer.", "evidence": "summarize uses only words[0]; test_command_output_is_not_posted_as_it_is covers it."}
  ]
}
```