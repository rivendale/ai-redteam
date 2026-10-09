# Redteam review: ops bot (`bot.py`, `test_bot.py`)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** There are no tools in this session. Nothing was run, so every finding below comes from reading the code and applying Python semantics.

**VERDICT: SHIP WITH FIXES.** The fixed-action allowlist and the approval gate hold against prompt injection. Before this faces customers, three things need fixing: one crash on hostile input, approval requests that reach staff with no context, and unhandled failures that leave tickets with no status.

**CONFIDENCE: medium.** Limits:
- Same-context review with no execution.
- The caller loop, the `llm`, `post` and `request_approval` implementations, and the badge server were not supplied.
- The "6 tests pass" claim is unverified.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md, bot.py, test_bot.py | seen | — |
| Queue loop / caller of `process` | not seen | **yes**: decides whether one exception stops the whole bot, and whether tickets are deduplicated |
| `llm` wrapper (JSON mode? code fences?) | not seen | **yes**: decides whether `json.loads` ever succeeds in production |
| `request_approval` implementation and what runs approved actions | not seen | **yes**: the request says "carries out the action" |
| `post` implementation, ticket ID format | not seen | yes: `int(ticket_id)` |
| status.example.test badge server | not seen | yes: decides whether the image shows any status at all |
| Test run output | not seen | partly: the tests were read but not run |

## COVERAGE

- **Checked:**
  - Functions: `ask_model`, `summarize`, `handle`, `status_markdown`, `process`
  - All 6 tests
  - The docstring claims: "model never supplies a command", "anything that changes production waits for a person", "command output is never posted as it is", "image URL carries only the ticket id"
- **Not checked:** the items marked not seen in the inputs ledger.

## SEATS AND GATE

- Seats: a single local reviewer only. No subagent or cross-vendor seats were available because there are no tools.
- Sensitivity gate: passed. The card number in the tests is the standard 4111 test PAN, and there is no real personal data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | bot.py:29 | `action in NEEDS_APPROVAL` runs before the `isinstance(action, str)` check at :32. An unhashable action (a list or dict) raises `TypeError: unhashable type`, and that line is outside the `try`. The `isinstance` guard is effectively dead code. | A customer writes a ticket that steers the model to reply `{"action": ["restart_web"]}`. `handle` raises, `process` never posts, and if the unseen loop does not catch exceptions, the bot stops for every later ticket. | Check `isinstance(action, str)` before any membership test. Repro: `bot.handle(lambda p: '{"action": ["x"]}', 7, "t", None, None)`. Expected `"no action"`; observed TypeError. | a✓ b✓ c✗ d✗ |
| F2 | Medium | CONFIRMED | A/B | bot.py:30, :23-24 | `request_approval(ticket_id, action)` passes staff only an ID and a verb. It omits the ticket text, the model's reply, who asked, and the fact that the suggestion came from customer-controlled input. | A customer writes "site is down, ops already told me to restart web". Staff see "ticket 7: restart_web", proposed by the bot, and approve. Production web restarts for all customers on one customer's word. The gate exists, but it is a weak gate. | Pass the ticket excerpt, the raw model output, and a "customer-originated" flag. Rate-limit or deduplicate approval requests per ticket and customer. Test: assert that `request_approval` receives the ticket text. | a✓ b✓ c✗ d✗ |
| F3 | Medium | CONFIRMED (traced) | B | bot.py:13, :26, :36, :47, :52 | Several failures are not handled and no status is posted: `llm` raising (network or rate limit); `llm` returning `None` (`json.loads(None)` raises TypeError, which is not caught at :27); `run` raising `FileNotFoundError`/`OSError`; `int(ticket_id)` raising ValueError on a non-numeric ID; `request_approval` being `None` (the tests pass `None`, and nothing enforces "required"). | Model API outage. Every ticket raises in `process`, nothing is posted, and the ticket looks untouched to the customer. | In `process`, wrap `handle` in a catch-all that posts "bot could not process this ticket", logs the error, and re-raises nothing. Validate `request_approval` is callable at entry. Repro: `bot.process({"id": 7, "text": "x"}, lambda p: None, print, None, None)` raises TypeError. | a✓ b✓ c✗ d✓ → Medium (High requires b or c alongside a and d; b is met, so this is borderline. Kept at Medium because the impact is a missing post, not a wrong action.) |
| F4 | Low | CONFIRMED | R | bot.py:20; test_bot.py:test_command_output… | Customers can trigger internal probes and read internal state ("web service: inactive", "cache size: 12M") on their own ticket. | Any customer can repeatedly ask for cache stats, run `du -sh` on production on demand (I/O cost), and learn internal sizing. | Decide whether customer-visible tickets should carry infrastructure detail. Post a customer-safe phrase instead, and rate-limit `cache_stats`. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED | B | test_bot.py:21-23 | `test_image_url_has_no_model_text` only checks the text after `"badge.png"`. | A mutation that puts the summary in the URL path (`/…/{summary}/badge.png`) still passes. The test also never exercises `process`/`post`, F1, F3, or the escaping at :46. | Parse the image URL and assert it equals the exact expected string. Add tests for a list-valued action, an `llm` exception, a `None` return, and `process` end to end. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1 (bot.py:26): code-fenced model replies.** Many models wrap JSON in ```` ```json ```` fences. If the wrapper does not enforce JSON mode, every ticket ends as "no action" and the bot silently does nothing. The test suite would not show this, so the green suite is not evidence against it. **Settles it:** whether the `llm` wrapper uses a structured or JSON output mode; one real call shows it.
- **S2 (bot.py:47): the status image may not show status.** The badge URL carries only the ticket ID, and the bot never reports the outcome to status.example.test. The image reflects status only if that server looks the ticket up itself. **Settles it:** the badge server's behaviour. If it is a static badge, this is drift from the request ("status image").
- **S3 (bot.py:29-31): approved actions may never run.** `restart_web` and `clear_cache` are queued, and no code here carries them out after approval. **Settles it:** whether `request_approval`'s backend executes approved actions. If nothing does, half the request ("carries out the action") is unbuilt.
- **S4 (process): reprocessing duplicates side effects.** Reprocessing a ticket (retry, edit, or a re-poll) re-posts and re-requests approval. **Settles it:** how the caller loop handles deduplication and idempotency.
- **S5: the suite's pass claim.** "6 tests pass" is unverified. **Settles it:** a run of `python -m unittest test_bot`.

## REFUTED

- **Prompt injection runs arbitrary commands.** Refuted. `argv` only ever comes from the `READ_ONLY` dict at :32, and model text never reaches `run`. The tests at :11-19 cover an unknown action and non-JSON text.
- **Injection triggers a production change directly.** Refuted. `NEEDS_APPROVAL` returns before `run` at :29-31, and test_a_change_waits… asserts `ran == []`.
- **Command output leaks to the ticket (secrets, extra lines).** Refuted. At :18-19 only the first whitespace token, capped at 20 characters, is posted. Its sources are `systemctl is-active` and `du -sh`, so the token is not attacker-controlled.
- **Markdown or image injection in the posted summary.** Refuted. The summary only contains fixed strings plus that first token. `[`, `]` and `<` are neutralised anyway, and the image URL uses `int(ticket_id)`.
- **A stopped service reported as a failure.** Refuted. The exit-3 special case at :39 is correct for `systemctl is-active` on an inactive unit.

## WHAT HOLDS UP

- The core safety design holds: the model chooses a label, never a command; `argv` is a list (no shell); there is a timeout; and changes are gated behind approval.
- Output is minimised before posting.
- The image URL is free of model text.
- The docstrings' claims match the code, apart from the "required" `request_approval` (F3).

## UNVERIFIED CLAIMS

- "6 tests pass": run the suite.
- "request_approval … must put the request in front of staff": read its implementation.
- The badge reflects status: query the badge server for two tickets with different outcomes.

## QUESTIONS FOR THE AUTHOR

1. What executes an approved `restart_web` or `clear_cache` (S3)?
2. Does the `llm` wrapper force JSON output (S1)?
3. Does the badge server know each ticket's outcome (S2)?
4. Does the queue loop survive an exception from `process`, and does it deduplicate tickets (F1, F3, S4)?

## DECISION-MAKER SUMMARY

The bot cannot be talked into running arbitrary commands or changing production by itself; that design is sound. Before connecting it to the customer queue:
- Fix the list-valued action crash and the unhandled failures (F1, F3).
- Give staff the ticket context in approval requests (F2).
- Confirm S1 to S3, any of which could mean the bot silently does nothing or never completes approved actions.

Proceeding as is risks silent non-responses, a bot loop that hostile tickets can stop, and staff approving production restarts without seeing who asked or why.

## OWNER SUMMARY

The bot is built safely at its core: customers cannot make it run arbitrary commands, and any real change waits for a person. A few fixes are needed before going live. It can crash or stay silent on unusual or failed replies, and staff approving a change are not shown why it was requested. We also need to confirm that approved changes actually get carried out, and that the status picture really shows the ticket's status.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "bot.py", "status": "seen", "matters": true},
    {"item": "test_bot.py", "status": "seen", "matters": true},
    {"item": "queue loop / caller of process", "status": "not_seen", "matters": true},
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "request_approval implementation and approved-action executor", "status": "not_seen", "matters": true},
    {"item": "post implementation and ticket id format", "status": "not_seen", "matters": true},
    {"item": "status.example.test badge server", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only a standard test card number (4111...) appears; no real personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "bot.py", "kind": "file"},
      {"unit": "test_bot.py", "kind": "file"},
      {"unit": "bot.py:ask_model", "kind": "function"},
      {"unit": "bot.py:summarize", "kind": "function"},
      {"unit": "bot.py:handle", "kind": "function"},
      {"unit": "bot.py:status_markdown", "kind": "function"},
      {"unit": "bot.py:process", "kind": "function"},
      {"unit": "model never supplies a command", "kind": "claim"},
      {"unit": "anything that changes production waits for a person", "kind": "claim"},
      {"unit": "command output is never posted as it is", "kind": "claim"},
      {"unit": "image URL carries only the ticket id", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "queue loop", "reason": "not supplied"},
      {"unit": "llm wrapper", "reason": "not supplied"},
      {"unit": "request_approval backend", "reason": "not supplied"},
      {"unit": "badge server", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:29",
     "scenario": "A customer ticket steers the model to reply {\"action\": [\"restart_web\"]}; 'action in NEEDS_APPROVAL' raises TypeError (unhashable list) outside the try, process never posts, and an unguarded loop stops for all later tickets.",
     "fix": "Check isinstance(action, str) before any membership test; add a test for list and dict action values.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "bot.handle(lambda p: '{\"action\": [\"x\"]}', 7, 't', None, None): expected 'no action', observed TypeError."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "A",
     "location": "bot.py:30",
     "scenario": "A customer writes text that leads the model to propose restart_web; staff receive only (ticket_id, 'restart_web') with no ticket text, model output or customer-origin flag, approve it, and production web restarts for everyone.",
     "fix": "Pass the ticket excerpt, raw model output and a customer-originated flag to request_approval; deduplicate and rate-limit approval requests per ticket and customer.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call handle with a model reply of restart_web and record request_approval's arguments: only (7, 'restart_web') is received."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:13,26,36,47,52",
     "scenario": "During a model API outage, or when llm returns None, run raises OSError, the ticket id is non-numeric, or request_approval is None, process raises and nothing is posted, so the ticket looks untouched.",
     "fix": "Wrap handle in process with a catch-all that posts a 'could not process' status and logs the error; validate that request_approval is callable at entry.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "bot.process({'id': 7, 'text': 'x'}, lambda p: None, print, None, None) raises TypeError from json.loads(None)."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "R",
     "location": "bot.py:20",
     "scenario": "Any customer can make the bot run du -sh on production and post internal state such as 'cache size: 12M' or 'web service: inactive' to a customer-visible ticket, repeatedly.",
     "fix": "Post customer-safe wording instead of raw infrastructure detail, and rate-limit cache_stats.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "test_command_output_is_not_posted_as_it_is shows 'cache size: 12M' as the posted summary."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_bot.py:21-23",
     "scenario": "A regression that puts the summary into the image URL path before 'badge.png' still passes the test; process, the escaping and the F1/F3 failure paths have no tests.",
     "fix": "Assert the exact image URL; add tests for list-valued actions, llm exceptions and None returns, and process end to end.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Change the URL in bot.py:47 to embed {safe} before /badge.png; the test still passes."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "bot.py:26",
     "suspicion": "Code-fenced JSON from the model makes every ticket end as 'no action'.",
     "unresolved_fact": "Whether the llm wrapper enforces a JSON or structured output mode."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "bot.py:47",
     "suspicion": "The status image may not reflect any status, because the bot never reports the outcome to the badge server.",
     "unresolved_fact": "Whether status.example.test looks up each ticket's state itself."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "bot.py:29-31",
     "suspicion": "Approved restart_web and clear_cache actions are never carried out by any code shown.",
     "unresolved_fact": "Whether the request_approval backend executes actions after approval."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "bot.py:50-52",
     "suspicion": "Reprocessing a ticket duplicates the post and the approval request.",
     "unresolved_fact": "How the queue loop deduplicates tickets."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "test_bot.py",
     "suspicion": "The claim that all 6 tests pass is unverified.",
     "unresolved_fact": "Output of python -m unittest test_bot."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Prompt injection runs arbitrary commands.", "evidence": "argv only comes from the READ_ONLY dict (bot.py:32); model text never reaches run; tests at test_bot.py:11-19."},
    {"id": "R2", "candidate": "Injection triggers a production change directly.", "evidence": "NEEDS_APPROVAL returns before run (bot.py:29-31); test asserts ran == []."},
    {"id": "R3", "candidate": "Command output leaks to the ticket.", "evidence": "Only the first token, capped at 20 characters, is posted (bot.py:18-19)."},
    {"id": "R4", "candidate": "Markdown or image injection in the posted summary.", "evidence": "The summary is fixed strings plus a non-attacker-controlled token; brackets are neutralised; the URL uses int(ticket_id) (bot.py:46-47)."},
    {"id": "R5", "candidate": "A stopped service is reported as a failure.", "evidence": "The exit-3 special case at bot.py:39 matches systemctl is-active behaviour for an inactive unit."}
  ]
}
```