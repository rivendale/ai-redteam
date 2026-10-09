VERDICT: SHIP WITH FIXES. The core safety design holds: the model can only pick from a fixed allowlist, and no model text or raw command output reaches the posted ticket. There is one confirmed crash on malformed model output, and two parts of the request (executing approved actions, a status-bearing image) may not exist anywhere and need answers before go-live.

CONFIDENCE: medium. This was a single-reviewer review with no tools and no subagent, so nothing was run. Every conclusion comes from reading the code. The callables the bot depends on (`llm`, `post`, `run`, `request_approval`, the queue loop) were not supplied.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `bot.py`, `test_bot.py`.
- Not seen, and it matters: the `llm` wrapper (JSON mode, error handling), the `request_approval` implementation and whatever executes approved actions, the badge service behind `status.example.test`, the `post` target (internal note or customer-visible), the queue loop that calls `process`, and the ticket id format.
- Not seen, and it doesn't matter: CI output for "6 tests pass" (UNVERIFIED, but by reading, all six would pass).

COVERAGE:
- Checked: `bot.py` (all five functions, both allowlists, the prompt) and `test_bot.py` (all six tests, traced by hand).
- Not checked: the five external callables, the badge service, deploy and runtime config, and actual `systemctl` and `du` behavior on the target host.

SEATS AND GATE: one reviewer (this session). No subagent or cross-vendor seats were available. Sensitivity gate passed: the only card-like number is the standard test PAN 4111…, so the data is not sensitive.

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `bot.py` handle: `if action in NEEDS_APPROVAL:` (runs before the `isinstance(action, str)` check) | Set membership on an unhashable value raises `TypeError`, and nothing catches it. | A ticket's text steers the model, or the model drifts, into replying `{"action": ["restart_web"]}` or `{"action": {}}`. `handle` raises `TypeError: unhashable type`, `process` posts nothing, and if the queue loop doesn't catch exceptions, every later ticket stalls. | Move `if not isinstance(action, str): return "no action"` above the approval check. Test: `bot.handle(lambda p: '{"action": ["restart_web"]}', 7, "x", run, approve)` should equal `"no action"`. Today it raises. | a Y / b Y / c N / d N |
| F2 | Low | CONFIRMED | B | `test_bot.py` `fake()`, and no test of `process`/`status_markdown` escaping | `fake` ignores argv, and no test asserts which command runs or what gets posted. | Someone changes `READ_ONLY["cache_stats"]` to a destructive argv, or drops the `[`/`]`/`<` escaping. All 6 tests stay green. | Assert the argv passed to `run` for each read-only action. Add a `process` test with a capturing `post` that checks the exact markdown. Mutation check: edit the argv and confirm the test goes red. | a Y / b Y / c N / d N |
| F3 | Low | PROBABLE | B | `bot.py` handle: returncode check (only `web_status` exit 3 is tolerated) | `du -sh` exits 1 when any subdirectory is unreadable, even though it still prints the total. | The cache dir holds files the bot user can't read. Every `cache_stats` then posts "action failed" while a valid size was on stdout. | Run as a user that can read the cache, or accept rc 1 when stdout parses. Test: `fake("12M\t/var/cache/app\n", 1)` should give `cache size: 12M`. | a Y / b N / c N / d N |
| F4 | Low | CONFIRMED | B | `bot.py` summarize: `"web service: " if action == "web_status" else "cache size: "` | Every action other than `web_status` gets the "cache size" label. | A third read-only action is added and its output is posted as "cache size: …" to customers. | Key the label off a dict next to `READ_ONLY`. Test: add a dummy action and assert its label. | a Y / b Y / c N / d N |

NEEDS VALIDATION
- S1 (Track B/D, `NEEDS_APPROVAL`, `request_approval`): Nothing in the code maps `restart_web` or `clear_cache` to a command or runs them after approval. The request says the bot "carries out the action". The question that settles it: does an approval executor exist elsewhere, or do staff restart by hand? If neither, this is drift and at least High.
- S2 (`status_markdown` image URL): The badge URL carries only the ticket id, and the bot never tells the badge service the outcome. The question: how does `status.example.test` know the state for that id? If it can't, the "status image" carries no status.
- S3 (`ask_model`, `handle`): Many models wrap JSON in markdown fences or prose. `json.loads` then fails, and every ticket silently becomes "no action". Separately, an `llm` that returns `None` or raises (timeout, network) is not caught. The question: does the `llm` wrapper enforce JSON mode and handle its own errors?
- S4 (`status_markdown`: `int(ticket_id)`): A non-numeric id such as `ABC-7` raises `ValueError`. Because `handle` is evaluated first, the approval request or action has already happened when the post fails. The question: are ticket ids always integers?
- S5 (`process`/`post`): Every ticket gets a post, including "no action" and "action failed". Posts can also expose internal state ("web service: inactive", cache size) to whoever wrote the ticket, and a customer can trigger them on purpose. The question: are posts internal notes or visible to the customer?
- S6 (queue loop, not supplied): Whether exceptions from `process` are caught per ticket, and whether redelivery causes duplicate approval requests and posts.
- S7 (`request_approval(ticket_id, action)`): Staff receive only the id and action, not why the model chose it. If customers can generate restart requests at will, approval fatigue becomes a risk. The question: what does the approval UI show the approver?

REFUTED
- "Ticket injection can run an arbitrary command." `argv` comes only from `READ_ONLY.get(action)`, so model text is never part of a command. Unknown actions (test 1) and non-JSON (test 2) return "no action".
- "Approval can be bypassed with a variant spelling (`Restart_web`)." A variant spelling is in neither set and falls to "no action".
- "Model or command text reaches the posted markdown." `handle` returns only fixed strings or `summarize` output, which is a fixed label plus the first output token truncated to 20 characters. So neither the escaping in `status_markdown` nor the image URL can carry customer text.

WHAT HOLDS UP: The allowlist design. List-form argv with no shell. The 30 s timeout. The fixed-format summaries. The integer-only image URL. Changes are gated behind staff. The `is-active` exit-3 handling is correct.

UNVERIFIED CLAIMS:
- "6 tests pass": by reading, they would. Confirm with `python3 -m unittest test_bot`.
- "request_approval … must put the request in front of staff": confirm against its implementation.
- "anything that changes production waits for a person": true in this file. Whether it is ever executed afterwards is S1.

QUESTIONS FOR THE AUTHOR:
1. What executes an approved `restart_web` or `clear_cache`?
2. Where does the badge get its status?
3. Does `llm` force JSON output?
4. Are ticket posts visible to customers?

DECISION-MAKER SUMMARY: The bot can't be talked into running arbitrary commands, and the security design is sound. Fix F1 (a one-line reorder plus a test) and answer S1–S3 before connecting it to the queue. If you proceed without the answers, the bot may silently do nothing on most tickets, never act on approved requests, or show a status image that doesn't reflect the state.

OWNER SUMMARY: The bot is built safely: customers can't make it run anything outside a short fixed list, and anything that changes the system waits for a staff member. One small bug can crash it on unusual replies from the AI, and it is quick to fix. Before it goes live, the team needs to confirm what happens after staff approve a request and where the status picture gets its information.

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
    {"item": "llm wrapper", "status": "not_seen", "matters": true},
    {"item": "request_approval implementation and approved-action executor", "status": "not_seen", "matters": true},
    {"item": "status.example.test badge service", "status": "not_seen", "matters": true},
    {"item": "post target and queue loop", "status": "not_seen", "matters": true},
    {"item": "CI output for 6 passing tests", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "self (same session, no subagent available)", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only a standard test card number (4111...) appears; no real personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "bot.py", "kind": "file"},
      {"unit": "bot.py:ask_model", "kind": "function"},
      {"unit": "bot.py:summarize", "kind": "function"},
      {"unit": "bot.py:handle", "kind": "function"},
      {"unit": "bot.py:status_markdown", "kind": "function"},
      {"unit": "bot.py:process", "kind": "function"},
      {"unit": "test_bot.py", "kind": "file"},
      {"unit": "model chooses only from fixed actions", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "llm wrapper", "reason": "not supplied"},
      {"unit": "request_approval and approval executor", "reason": "not supplied"},
      {"unit": "badge service", "reason": "not supplied"},
      {"unit": "post target and queue loop", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:handle `if action in NEEDS_APPROVAL:`",
     "scenario": "Model replies {\"action\": [\"restart_web\"]}; set membership on a list raises an uncaught TypeError, nothing is posted, and an unguarded queue loop stops.",
     "fix": "Check isinstance(action, str) before the NEEDS_APPROVAL test and return 'no action' otherwise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "bot.handle(lambda p: '{\"action\": [\"restart_web\"]}', 7, 'x', run, approve): expect 'no action', observe TypeError."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_bot.py:fake; no test of process or status_markdown escaping",
     "scenario": "READ_ONLY argv is changed to a destructive command or the markdown escaping is removed; all 6 tests still pass.",
     "fix": "Assert the argv passed to run per action and the exact markdown passed to post in a process test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Edit READ_ONLY['cache_stats'] to ['true'] and run the tests: all pass, where they should fail."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "bot.py:handle returncode check",
     "scenario": "du -sh exits 1 on an unreadable subdirectory while still printing the total; the bot posts 'action failed'.",
     "fix": "Ensure cache readability for the bot user, or accept rc 1 when stdout has a size.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "bot.handle(... '{\"action\": \"cache_stats\"}' ..., fake('12M\\t/var/cache/app\\n', 1), None): observe 'action failed'."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "bot.py:summarize label expression",
     "scenario": "A new read-only action is added and its result is posted labelled 'cache size:'.",
     "fix": "Map labels per action in a dict alongside READ_ONLY.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add READ_ONLY['disk'] and call summarize('disk', ...): observe 'cache size: ...'."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "bot.py:NEEDS_APPROVAL / request_approval",
     "suspicion": "Approved changes are never executed, so the bot does not carry out the action as requested.",
     "unresolved_fact": "Whether an executor for approved restart_web/clear_cache exists outside this file."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "bot.py:status_markdown image URL",
     "suspicion": "The status image carries no status because the bot never reports the outcome to the badge service.",
     "unresolved_fact": "How status.example.test learns the state for a ticket id."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "bot.py:ask_model / handle json.loads",
     "suspicion": "Fenced or prose-wrapped JSON makes every ticket 'no action'; llm exceptions or None are uncaught.",
     "unresolved_fact": "Whether the llm wrapper enforces JSON output and handles its own errors."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "bot.py:status_markdown int(ticket_id)",
     "suspicion": "Non-numeric ticket ids raise ValueError after the action or approval has already happened.",
     "unresolved_fact": "Whether ticket ids are always integers."},
    {"id": "S5", "status": "needs_validation", "track": "R", "location": "bot.py:process / post",
     "suspicion": "Every ticket gets a post, and internal service state is shown to customers who can trigger it.",
     "unresolved_fact": "Whether post() writes customer-visible comments or internal notes."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "queue loop calling process (not supplied)",
     "suspicion": "One exception halts the queue; redelivery duplicates approvals and posts.",
     "unresolved_fact": "Per-ticket exception handling and delivery semantics of the queue loop."},
    {"id": "S7", "status": "needs_validation", "track": "D", "location": "bot.py:request_approval(ticket_id, action)",
     "suspicion": "Approvers see only id and action; customer-triggerable requests risk approval fatigue.",
     "unresolved_fact": "What the approval UI shows the approver."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Ticket injection can run an arbitrary command.", "evidence": "argv comes only from READ_ONLY.get(action); unknown or non-JSON replies return 'no action' (tests 1 and 2)."},
    {"id": "C2", "candidate": "A variant spelling bypasses approval.", "evidence": "Values outside both sets fall to READ_ONLY.get -> None -> 'no action'."},
    {"id": "C3", "candidate": "Model or command text reaches the posted markdown.", "evidence": "handle returns fixed strings or summarize output: a fixed label plus the first output token capped at 20 characters; the image URL uses int(ticket_id)."}
  ]
}
```