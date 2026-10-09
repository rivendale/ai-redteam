VERDICT: SHIP WITH FIXES. The core safety design holds: the model picks from a fixed list, never supplies a command, and its text never reaches the posted reply. However, some malformed model replies and runtime errors crash the bot instead of failing closed, and three points need confirming before it touches the queue.

CONFIDENCE: medium. Three things limit it: this is a same-context review (anchoring risk; re-run in a fresh session for anything high-stakes), I had no tools so nothing was executed, and the approval handler, poster, model client and queue loop were not supplied.

INPUTS LEDGER:
- **Seen:** request.md, context.md, bot.py, test_bot.py.
- **Not seen, and it matters:**
  - The `request_approval` implementation and whatever executes an approved action. Without it, "carries out the action" is unverified for restart_web and clear_cache.
  - The production `run`, `post` and `llm` wiring.
  - The queue consumer loop. It decides whether an exception in `process` kills the bot or retries the ticket.
  - The ticket ID format. It matters because of `int(ticket_id)`.
  - Whether ticket replies are visible to customers.
  - Whether `status.example.test` is a placeholder.
- **Not seen, matters less:** the test run output. The context's "6 tests pass" is taken on assertion.

COVERAGE:
- **Scope:** the whole work (2 files).
- **Checked:**
  - Every function in bot.py: `ask_model`, `summarize`, `handle`, `status_markdown`, `process`.
  - All 6 tests in test_bot.py.
  - request.md and context.md.
  - The bot.py module docstring, read as claims.
- **Not checked:**
  - Approval executor, queue loop, `post`/`llm`/`run` implementations: not supplied.
  - Test execution and mutation checks: no tools.

SEATS AND GATE:
- Local same-context reviewer only. No subagent or cross-vendor seats were available because there are no tools in this session.
- Sensitivity gate passed. The only card number is the standard test PAN 4111 1111 1111 1111, and there is no other personal or confidential data.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | bot.py:29 (guard at :32) | `action in NEEDS_APPROVAL` runs before the `isinstance(action, str)` guard on line 32. A list or dict action raises `TypeError: unhashable type`, which nothing catches. | A customer writes a ticket that steers the model to reply `{"action": ["restart_web"]}`, or the model does so on its own. `handle` raises and `process` posts nothing. Depending on the unseen queue loop, the bot either stops for every later ticket or retries the same poison ticket, paying for a model call each time. | Move the `isinstance(action, str)` check above line 29 and return "no action" otherwise. **Repro:** `bot.handle(lambda p: '{"action": ["restart_web"]}', 7, "x", lambda *a, **k: None, lambda t, a: None)`. Expected "no action"; observed TypeError. Add this as a test. | a✓ b✓ c✗ d✗ |
| F2 | Medium | CONFIRMED (traced) | B | bot.py:35-38 | Only `subprocess.TimeoutExpired` is caught. If `systemctl` or `du` is missing or not permitted (for example in a container without systemd), `FileNotFoundError` or `PermissionError` propagates out of `handle`. | The bot runs in a container. Every `web_status` ticket raises `FileNotFoundError`, no reply is posted, and the same queue-loop consequences as F1 follow. | Catch `OSError` alongside `TimeoutExpired` and return "action failed". **Repro:** pass `run=lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError("systemctl"))` with model reply `{"action":"web_status"}`. Expected "action failed"; observed FileNotFoundError. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED (traced) | B | bot.py:26-27 | Only `ValueError` and `AttributeError` are caught. If `llm` returns `None` or a non-string, `json.loads` raises `TypeError`, which is uncaught. Exceptions raised by `llm` itself (network errors, timeouts) also propagate, and the model call has no timeout. | The model client returns `None` on a refusal or empty completion. `handle` raises instead of returning "no action". | Catch `TypeError`. Wrap the `llm` call with a timeout and a fail-closed return. **Repro:** `bot.handle(lambda p: None, 7, "x", lambda *a, **k: None, None)`. Expected "no action"; observed TypeError. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED (traced) | B | test_bot.py `test_image_url_has_no_model_text`; overall test set | The test checks only the text after `badge.png`. The card number is still posted in the body, because `status_markdown` does not filter summary text. Safety rests entirely on `handle` returning fixed strings, and no test pins that. No test covers `process()` end to end, F1–F3, or `request_approval` failing. | A later change makes `handle` echo model or ticket text into the summary. Every test stays green while customer text is posted back. | Add an end-to-end `process()` test with a hostile ticket and assert the posted markdown contains only the expected fixed strings. Add tests for F1–F3. **Repro of the gap:** `"4111" in bot.status_markdown(7, "card 4111 1111 1111 1111 reset")` returns True. | a✓ b✓ c✗ d✗ |

NEEDS VALIDATION (these have no severity):
- **N1. Does an approved action ever run?** bot.py:29-31 has no execution path for restart_web or clear_cache. The request says "carries out the action". This would be drift unless the approval handler executes the approved action. *Settled by:* the `request_approval` implementation and the approval flow.
- **N2. Does a failed approval request get reported?** bot.py:30-31 ignores the return value of `request_approval`, so a failed submission is still reported as "queued for staff approval". *Settled by:* whether the handler raises on failure or returns a status.
- **N3. Can the bot handle the real ticket ID format?** At bot.py:47, `int(ticket_id)` crashes on non-numeric IDs such as "SUP-1042". *Settled by:* the queue's ticket ID format.
- **N4. Does the status image work and show status?** At bot.py:47, `status.example.test` uses a reserved TLD that never resolves. The URL also carries only the ticket ID, so the image cannot reflect the action's result unless the badge server looks up the ticket. *Settled by:* whether the domain is a placeholder replaced at deploy, and how the badge server determines state.
- **N5. Is internal state exposed to customers?** Service state and cache size are posted to tickets. *Settled by:* whether ticket replies are customer-visible and whether that is acceptable.

REFUTED:
- **Prompt injection can run arbitrary commands.** Refuted. `argv` comes only from the fixed `READ_ONLY` dict (bot.py:5-8, :32), the model never supplies a command, and `run` receives a list, not a shell string.
- **Model or customer text exfiltrated via the image link or markdown.** Refuted. `handle` returns only fixed strings or a first token of system command output, truncated to 20 characters. The image URL uses `int(ticket_id)`.
- **Production changes bypass approval.** Refuted. restart_web and clear_cache have no argv, so line 33 returns early even if line 29 were bypassed.
- **Runaway spend from one ticket.** Refuted. There is one model call per ticket with no retries in this code. The queue loop's retry policy is out of scope (see F1).

WHAT HOLDS UP:
- The fixed action allowlist.
- The approval gate for changes.
- Output summarization that never posts raw command output or model text.
- The 30-second command timeout.
- Correct handling of `is-active` exit code 3.
- The fail-closed path for non-JSON replies and unknown actions.
- Tests that cover the main safety properties at the unit level.

UNVERIFIED CLAIMS:
- **"6 tests pass."** Not run. Confirm by running `python -m unittest test_bot` in an isolated copy.
- **Mutation coverage.** For example, deleting line 29-31 should turn `test_a_change_waits_for_staff_with_the_ticket_id` red. Not tested.
- **"anything that changes production waits for a person."** True in this file. Whether the person's approval actually triggers the change is unknown (N1).

QUESTIONS FOR THE AUTHOR:
1. What executes restart_web or clear_cache after staff approve, and does `request_approval` raise on failure?
2. What does the queue loop do when `process` raises: crash, skip, or retry?
3. What do ticket IDs look like, and is `status.example.test` a placeholder?

DECISION-MAKER SUMMARY: The allowlist-and-approval design is sound, and a hostile ticket cannot make this bot run arbitrary commands or leak text. Before connecting the queue, fix F1–F3 so malformed model replies and missing binaries fail closed, and answer N1, N3 and N4. If you proceed as is, a crafted ticket or a container without systemctl can stall or loop the bot, and approved fixes may never actually run.

OWNER SUMMARY: The bot is designed safely: customers cannot make it run anything beyond a short list of harmless checks, and restarts wait for staff. Some unusual replies from the AI, or a missing system tool, can make it stop instead of politely doing nothing, which is a quick fix. We also need to confirm that staff-approved restarts are actually carried out and that the status picture points at a real address.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "bot.py", "status": "seen", "matters": true},
    {"item": "test_bot.py", "status": "seen", "matters": true},
    {"item": "request_approval implementation and approved-action executor", "status": "not_seen", "matters": true},
    {"item": "queue consumer loop", "status": "not_seen", "matters": true},
    {"item": "production llm/post/run wiring", "status": "not_seen", "matters": true},
    {"item": "ticket id format", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "only a standard test card number; no personal or confidential data"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "bot.py", "kind": "file"},
      {"unit": "test_bot.py", "kind": "file"},
      {"unit": "bot.py:ask_model", "kind": "function"},
      {"unit": "bot.py:summarize", "kind": "function"},
      {"unit": "bot.py:handle", "kind": "function"},
      {"unit": "bot.py:status_markdown", "kind": "function"},
      {"unit": "bot.py:process", "kind": "function"},
      {"unit": "bot.py module docstring claims", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "request_approval implementation", "reason": "not_supplied"},
      {"unit": "queue consumer loop", "reason": "not_supplied"},
      {"unit": "llm/post/run production implementations", "reason": "not_supplied"},
      {"unit": "test execution and mutation checks", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:29",
     "scenario": "A ticket steers the model to reply {\"action\": [\"restart_web\"]}; 'action in NEEDS_APPROVAL' raises TypeError (unhashable list) before the isinstance guard at line 32; no reply is posted and the queue loop may crash or retry the poison ticket.",
     "fix": "Check isinstance(action, str) before line 29 and return 'no action' otherwise; add a test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "bot.handle(lambda p: '{\"action\": [\"restart_web\"]}', 7, 'x', lambda *a, **k: None, lambda t, a: None): expected 'no action', observed TypeError."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:35-38",
     "scenario": "Deployed where systemctl or du is missing or not permitted, run() raises FileNotFoundError/PermissionError, which is not caught; every web_status ticket crashes handle and gets no reply.",
     "fix": "Catch OSError alongside TimeoutExpired and return 'action failed'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "bot.handle(lambda p: '{\"action\": \"web_status\"}', 7, 'x', lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError('systemctl')), None): expected 'action failed', observed FileNotFoundError."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:26-27",
     "scenario": "The model client returns None or raises; json.loads(None) raises TypeError (not caught) and llm exceptions propagate; the model call has no timeout.",
     "fix": "Catch TypeError; wrap the llm call with a timeout and a fail-closed 'no action' return.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "bot.handle(lambda p: None, 7, 'x', lambda *a, **k: None, None): expected 'no action', observed TypeError."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_bot.py:test_image_url_has_no_model_text",
     "scenario": "The test checks only the URL tail, while status_markdown posts arbitrary summary text in the body; no test covers process() end to end or F1-F3, so a change that echoes customer text would pass all tests.",
     "fix": "Add an end-to-end process() test with a hostile ticket asserting only fixed strings are posted; add tests for F1-F3.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "'4111' in bot.status_markdown(7, 'card 4111 1111 1111 1111 reset') returns True, while the test passes."},
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "bot.py:29-31",
     "suspicion": "restart_web and clear_cache are never executed by the bot, even after approval; possible drift from 'carries out the action'.",
     "unresolved_fact": "Whether the approval flow executes the approved action."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "bot.py:30-31",
     "suspicion": "request_approval's result is ignored, so a failed submission is still reported as queued.",
     "unresolved_fact": "Whether request_approval raises on failure."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "bot.py:47",
     "suspicion": "int(ticket_id) crashes on non-numeric ticket ids.",
     "unresolved_fact": "The queue's ticket id format."},
    {"id": "N4", "status": "needs_validation", "track": "B", "location": "bot.py:47",
     "suspicion": "status.example.test is a reserved, non-resolving domain, and the URL carries no status, so the status image may never render or reflect state.",
     "unresolved_fact": "Whether the domain is a deploy-time placeholder and how the badge server derives state."},
    {"id": "N5", "status": "needs_validation", "track": "B", "location": "bot.py:20",
     "suspicion": "Internal service state and cache size are posted to tickets that may be customer-visible.",
     "unresolved_fact": "Whether ticket replies are customer-visible and whether that disclosure is accepted."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Prompt injection can run arbitrary commands.", "evidence": "argv comes only from the fixed READ_ONLY dict (bot.py:5-8, :32) and is passed as a list, never a shell string."},
    {"id": "C2", "candidate": "Model or customer text is exfiltrated via the image URL or markdown.", "evidence": "handle returns only fixed strings or a 20-char first token of system output; the URL uses int(ticket_id)."},
    {"id": "C3", "candidate": "Production-changing actions bypass approval.", "evidence": "restart_web and clear_cache have no argv; line 33 returns 'no action' even if line 29 were bypassed."},
    {"id": "C4", "candidate": "Runaway model spend.", "evidence": "One model call per ticket, no retries in this code."}
  ]
}
```