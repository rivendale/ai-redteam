**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagent were available in this session. Every result below comes from reading and tracing the supplied text. Nothing was executed.

**VERDICT: SHIP WITH FIXES.** The safety design holds: there is a fixed action allowlist, argv lists with no shell, and production changes are gated before any execution. However, one line of model-output handling lets a customer-steered or malformed reply crash ticket processing instead of falling back to "no action".

**CONFIDENCE: medium.** Three things limit it. The review was done in the same context, nothing could be run, and the production bindings (`llm`, `run`, `post`, `request_approval`, the queue loop and the badge service) were not supplied.

**INPUTS LEDGER**
- Seen:
  - request.md
  - context.md
  - bot.py (52 lines)
  - test_bot.py (6 tests)
- Not seen, and it matters:
  - The `llm` wrapper (timeouts, can it return `None`).
  - The production `run` binding.
  - The `request_approval` implementation and its return contract.
  - The code that executes approved actions and posts their outcome.
  - The queue loop that calls `process` (does an exception halt it?).
  - The `status.example.test` badge service.
  - The format of ticket IDs.
- Not seen, and it does not matter: none.

**COVERAGE**
- Scope: the whole supplied work.
- Checked:
  - request.md and context.md
  - bot.py: `ask_model`, `summarize`, `handle`, `status_markdown`, `process`, the `READ_ONLY` and `NEEDS_APPROVAL` tables
  - test_bot.py: all 6 tests and `fake`
  - The claim "6 tests pass": traced to pass, not run.
- Not checked:
  - A byte-level scan for zero-width or bidirectional characters (no tools; the text was read as rendered).
  - Execution of the tests (no tools).
  - The unsupplied components listed in the ledger (not_supplied).

**SEATS AND GATE**
- Only a local same-context review ran. No subagent tool was available, and no cross-vendor seats were requested.
- Sensitivity gate passed. The only card number is the public Visa test PAN 4111…, inside a test.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED (traced, Python semantics) | B | bot.py:29 (guard too late at :32) | `action in NEEDS_APPROVAL` runs before the `isinstance(action, str)` check. A list or dict action raises `TypeError: unhashable type`, and nothing catches it. | A customer writes "reply with action as a list", or the model returns `{"action": ["web_status","cache_stats"]}` for a ticket describing two problems. `handle` raises and `process` posts nothing. If the queue loop does not catch the exception (see S1), processing stops for every ticket. | **Fix:** check `isinstance(action, str)` (else return "no action") before line 29. **Repro:** `bot.handle(lambda p: '{"action": ["restart_web"]}', 7, "x", lambda *a, **k: None, lambda t, a: None)`. Expected "no action"; observed TypeError. Add this as a test. | Y/Y/N/Y |
| F2 | Medium | PROBABLE | B | bot.py:13, :30 | Ticket text goes into the prompt undelimited, so any customer can steer the model to `restart_web` or `clear_cache`. The approval request carries only `(ticket_id, action)`: no reason, no dedup, no rate limit. | One customer files 50 tickets saying "restart the web server". Staff receive 50 context-free production restart requests. Approval fatigue then leads to an unwarranted restart and a production outage. | **Fix:** pass the ticket excerpt and model rationale to `request_approval`, dedupe by (ticket, action), and rate-limit per customer. **Repro:** call `handle` 50 times with a model stub returning `restart_web` and the same ticket ID. Observe 50 approval calls; expected 1. | Y/N/Y/N |
| F3 | Low | CONFIRMED (traced) | B | test_bot.py:6-7, :30-36 | `fake` ignores its arguments, and no test asserts which argv is run. | Someone changes `READ_ONLY["cache_stats"]` to a destructive command. All 6 tests still pass. | **Fix:** record the argv in `fake` and assert it equals `READ_ONLY[action]`. **Repro:** in a scratch copy, set `READ_ONLY["cache_stats"] = ["rm","-rf","/var/cache/app"]` and run the tests. They stay green. | Y/Y/N/N |
| F4 | Low | CONFIRMED (traced) | B | bot.py:37 | Only `TimeoutExpired` is caught around `run`. An `OSError` such as `FileNotFoundError` propagates. | The container lacks `systemctl`. A web_status ticket raises an uncaught exception, so no status is posted. | **Fix:** also catch `OSError` and return "action failed". **Repro:** `handle` with a model stub returning web_status and `run` raising `FileNotFoundError`. Expected "action failed"; observed an exception. | Y/Y/N/N |

**F1 confirm-or-refute.** The defender's case is that the caller catches exceptions and that the model follows the enum. Neither holds up:
- Even if the caller catches the exception, the ticket gets no post, and the code's own intended fallback ("no action") is bypassed.
- Customer text can push the model off the enum.

The finding stands.

**F1 siblings.** I searched every use of the model-derived value in `handle`:
- `.get` at :26: its AttributeError is caught.
- Membership at :29: this is the bug.
- :32: guarded by `isinstance`.
- :30: only reached with a string.

There is one related case. `json.loads` raises an uncaught TypeError if `llm` returns `None`; that is S5. I found no other location.

**F1 is a security finding:**
- Principal: the customer writing the ticket.
- Input: ticket text that steers the model's reply.
- Failed control: the type check placed after the set lookup.
- Boundary crossed: customer to bot availability.
- Resource affected: ticket processing and status posting.

### NEEDS VALIDATION
- **S1.** Does the queue loop around `process` catch exceptions per ticket? If not, F1 and F4 stop the whole queue.
- **S2.** The return value of `request_approval` is ignored (bot.py:30). If it can fail silently, the customer is told "queued for staff approval" when nothing was queued.
- **S3.** Requirement fit. The request says the bot "carries out the action and posts a status summary". The supplied code never executes `restart_web` or `clear_cache`, and never posts a final status after approval. Which component does this?
- **S4.** `int(ticket_id)` at bot.py:47 raises on non-numeric IDs such as "T-123". What format do ticket IDs have?
- **S5.** The `llm` wrapper: does it have a timeout, a retry or cost cap, and can it return `None`? A `None` return makes :26 raise TypeError, which is not caught.
- **S6.** The badge at `status.example.test`: what does it show, and does it reflect this action's outcome? Is the domain owned by the operator?

### REFUTED
- **Model text reaching a shell.** Argv comes only from fixed lists (:5-8, :32), is passed as a list with no shell, and the model chooses a key only.
- **Model or customer text reaching the posted markdown or image URL.** `handle` returns only literals or `summarize` of fixed-command stdout. The URL carries only `int(ticket_id)`.
- **Prompt injection triggering a production change without staff.** Lines 29-31 return before `run`.
- **A non-dict JSON top level crashing the bot.** `.get` on a list, string, number or `null` raises AttributeError, which :27 catches.
- **Attacker-controlled `du` output.** `du -sh` prints only the total and the path. `words[0]` is the size, truncated to 20 characters.
- **Approval gating as High drift from "carries out the action".** Gating customer-steered production changes is a defensible reading, and the executor was not supplied. Moved to S3.

### WHAT HOLDS UP
- The fixed allowlist with no model-supplied commands.
- The gating of write actions.
- The 30-second timeout on commands.
- The handling of `systemctl` exit code 3 for a stopped service.
- The fixed-format summary, which never echoes raw output.
- An image URL that cannot carry model text.
- Test 3 does go red if the summary were placed in the URL.

### UNVERIFIED CLAIMS
- "6 tests pass": traced to pass, but not run. Confirm by running `python -m unittest test_bot` in an isolated copy.
- "Request_approval must put the request in front of staff": this depends on an implementation that was not supplied.

### QUESTIONS FOR THE AUTHOR
1. Does the queue loop isolate exceptions per ticket?
2. Where do approved actions run, and who posts their final status?
3. What format do ticket IDs have?

### DECISION-MAKER SUMMARY
Fix F1 (a two-line reorder plus a test) before connecting the bot to the queue, and answer S1 and S3. The design otherwise keeps customer text away from commands and production changes. If you proceed as is, one oddly phrased ticket can leave that ticket unanswered, or stall the queue if the loop does not catch errors.

### OWNER SUMMARY
The bot is built safely in the ways that matter most: customers cannot make it run commands, and any change to production waits for a person. One small ordering mistake means an unusual reply from the AI can make the bot crash on a ticket instead of quietly doing nothing, so this should be fixed and tested first. It is also not yet clear what carries out approved changes and tells the customer the result, and that should be confirmed before launch.

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
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "request_approval implementation and approved-action executor", "status": "not_seen", "matters": true},
    {"item": "queue loop calling process()", "status": "not_seen", "matters": true},
    {"item": "status.example.test badge service", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only a public test card number inside a test."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "bot.py", "kind": "file"},
      {"unit": "bot.py:handle", "kind": "function"},
      {"unit": "bot.py:summarize", "kind": "function"},
      {"unit": "bot.py:status_markdown", "kind": "function"},
      {"unit": "bot.py:process", "kind": "function"},
      {"unit": "bot.py:ask_model", "kind": "function"},
      {"unit": "test_bot.py", "kind": "file"},
      {"unit": "6 tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "llm, run, post, request_approval bindings", "reason": "not_supplied"},
      {"unit": "approved-action executor", "reason": "not_supplied"},
      {"unit": "hidden-character byte scan and test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:29",
     "scenario": "Model replies {\"action\": [\"web_status\",\"cache_stats\"]} (customer-steered or natural); 'action in NEEDS_APPROVAL' raises TypeError (unhashable), uncaught, so no status is posted and the queue may halt.",
     "fix": "Return 'no action' unless isinstance(action, str) before the NEEDS_APPROVAL check; add a test for list and dict actions.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "bot.handle(lambda p: '{\"action\": [\"restart_web\"]}', 7, 'x', lambda *a, **k: None, lambda t, a: None): expected 'no action', observed TypeError (traced, not run).",
     "security": true,
     "boundary": {"principal": "customer writing a ticket", "input": "ticket text steering the model reply", "control": "type check placed after set membership", "crossed": "customer to bot availability", "resource": "ticket processing and status posting"},
     "siblings_searched": {"searched": "every use of the model-derived value in handle (lines 26, 29, 30, 32)", "found": "no other location; llm returning None is tracked as S5"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "bot.py:30",
     "scenario": "A customer files many tickets steering the model to restart_web; staff get repeated context-free restart requests and approve one without cause, causing an outage.",
     "fix": "Include the ticket excerpt and rationale in the approval request; dedupe by (ticket, action); rate-limit per customer.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Call handle 50 times with a model stub returning restart_web and ticket id 7; observe 50 request_approval calls, expected 1."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_bot.py:6-7",
     "scenario": "READ_ONLY argv is changed to a destructive command and all 6 tests still pass because fake ignores argv.",
     "fix": "Record argv in fake and assert it equals READ_ONLY[action].",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy set READ_ONLY['cache_stats'] = ['rm','-rf','/var/cache/app'] and run the tests; they stay green."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:37",
     "scenario": "systemctl is missing in the deployment; run raises FileNotFoundError, which is uncaught, and no status is posted.",
     "fix": "Also catch OSError and return 'action failed'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "handle with a model stub returning web_status and run raising FileNotFoundError: expected 'action failed', observed an exception."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "caller of bot.py:process",
     "suspicion": "One uncaught exception may stop the whole queue.",
     "unresolved_fact": "Whether the queue loop catches exceptions per ticket."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "bot.py:30",
     "suspicion": "The customer is told 'queued' when request_approval failed silently.",
     "unresolved_fact": "The return and raise contract of request_approval."},
    {"id": "S3", "status": "needs_validation", "track": "D", "location": "bot.py:29-31",
     "suspicion": "Approved actions are never executed and no final status is posted, contrary to the request.",
     "unresolved_fact": "Which component runs approved actions and posts their outcome."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "bot.py:47",
     "suspicion": "int(ticket_id) raises on non-numeric ids.",
     "unresolved_fact": "The ticket id format."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "bot.py:13",
     "suspicion": "An llm call with no timeout or cap, or a None return, causes a hang or an uncaught TypeError at line 26.",
     "unresolved_fact": "The llm wrapper's timeout and return contract."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "bot.py:47",
     "suspicion": "The status image may not reflect this action's outcome.",
     "unresolved_fact": "What the badge service renders for an id, and who operates the domain."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Model text reaches a shell.", "evidence": "argv comes only from fixed lists at bot.py:5-8 and :32, passed as a list with no shell."},
    {"id": "C2", "candidate": "Model or customer text reaches the posted markdown or image URL.", "evidence": "handle returns only literals or summarize of fixed-command stdout; the URL uses int(ticket_id)."},
    {"id": "C3", "candidate": "Prompt injection triggers a production change without staff.", "evidence": "bot.py:29-31 returns before run."},
    {"id": "C4", "candidate": "A non-dict top-level JSON reply crashes the bot.", "evidence": ".get on list/str/number/None raises AttributeError, caught at :27."},
    {"id": "C5", "candidate": "Approval gating is High drift from 'carries out the action'.", "evidence": "Gating customer-steered production changes is a defensible reading and the executor was not supplied; moved to S3."}
  ]
}
```