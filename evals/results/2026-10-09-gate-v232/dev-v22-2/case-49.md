# Redteam review: multi-agent plan run

> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools and no subagent in this session, so I could not fetch the file versions or open the tool implementations.

**VERDICT: REWORK.** The API section is missing from `shared/plan.md`: agent B overwrote agent A's write. The orchestrator's summary nonetheless reports both sections as present, so the request's "confirm" step was falsely passed.

**CONFIDENCE: medium.** The core finding rests on the final file and both logs, which agree. It is limited by:
- a same-context review with no tools;
- the content of versions `a1` and `b2` not being supplied;
- the `write_file` and `claim` tool implementations not being supplied.

## INPUTS LEDGER

**Seen:**
- `request.md`
- `context.md`
- `agent_a.jsonl`
- `agent_b.jsonl`
- `coordination.md`
- `shared/claims.json`
- `shared/plan.md` (current)
- `summary.md`

**Not seen, and whether each gap matters:**

| Item | Matters? | Why |
|---|---|---|
| Contents of `plan.md` at sha `a1` | No | Not needed for the main finding. |
| Contents of `plan.md` at sha `b2` | Yes, for recovery | It shows whether A's API text can be restored rather than rewritten. |
| SHA of the current `plan.md` | Low | The content matches B's note, so it is almost certainly `c3`. |
| `write_file` / `claim` tool code | Yes, for the fix | It shows whether `base_sha` is checked at all. |
| The orchestrator's own log | Yes | It would show whether the orchestrator read `plan.md` before writing the summary. |

## COVERAGE

- **Checked:** every event in both logs, ordered into one timeline; all three protocol rules against each agent's actions; `claims.json`; the final `plan.md`; every claim in `summary.md`.
- **Not checked:** tool implementations, file version history, the orchestrator's process.

## SEATS AND GATE

- **Seats:** local same-context review only. No subagent was available. No cross-vendor seats were requested.
- **Sensitivity gate:** passed. The material is a non-sensitive planning document.

## Merged timeline

| ts | Agent | Event |
|---|---|---|
| 10:00:01 | A | Reads `plan.md` at `a1` |
| 10:00:02 | B | Reads `plan.md` at `a1` |
| 10:00:09 | A | Claims `api` |
| 10:00:20 | A | Writes `a1` → `b2` (API section added) |
| 10:00:30 | B | Writes with `base_sha` `a1` → `c3`. This replaces the whole file and discards `b2`. B never claimed and never re-read. |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `shared/plan.md` (whole file); `agent_b.jsonl` line 2 (`"base_sha": "a1"`, ts 10:00:30) | A's API section is lost. B wrote a whole-file replacement built on `a1`, the version from before A's write at 10:00:20 (`b2`). The final file has Overview and Database only. B broke protocol rule 1 (no `claim` event; `claims.json` is `{"api": "A"}` only) and rule 2 (its only read was at 10:00:02, 28 s before writing). | The next sprint is planned from a document with no API section, even though A reported it "added". | Recover A's API text from the `b2` version if the store keeps history. Otherwise re-run A against the current file. Then re-read `plan.md` and check that both headings exist. **Reproduction:** order both logs by ts. The write at 10:00:30 has `base_sha` `a1` while the current sha is `b2`. `grep '^## API' shared/plan.md` returns nothing, and `grep '^## Database'` hits as a positive control. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | C/A | `summary.md` line 3: "shared/plan.md now contains the API section and the Database section." | The orchestrator's confirmation is false. It restates the agents' `final` messages instead of reading the file. The request explicitly required confirming the plan contains both sections. | A reader trusts the summary, skips the check, and the sprint starts on an incomplete plan. Every future run with a lost write also reports success. | The orchestrator must read `shared/plan.md` after all agents finish and assert each required heading. If one is missing, report failure. **Reproduction:** compare `summary.md` line 3 against the current `plan.md`. | a✓ b✓ c✓ d✓ |
| F3 | High | PROBABLE | B | `coordination.md` rules 1–3; `write_file` tool | The protocol cannot prevent lost writes. Claims are per section, but writes are whole-file, so a claim never protects another agent's section. Rule 2 still leaves a race between re-read and write. Most importantly, `write_file` appears to accept a stale `base_sha`: B's write on `a1` succeeded after `b2` existed, and no error is logged. | Two compliant agents re-read at nearly the same moment, and the later write erases the earlier one, as happened here. | Make `write_file` a compare-and-swap: reject the write when `base_sha` ≠ current sha, and have the agent re-read and retry. Alternatively, give each agent its own section file and merge them. **Test:** write with a stale `base_sha` and expect a rejection. | a✓ b✗ c✓ d✓ |
| F4 | Low | CONFIRMED | B | `agent_a.jsonl` lines 1–3 | A also broke rule 2. It read at 10:00:01 and wrote at 10:00:20 without re-reading. This was harmless here only because nothing was written in between. | If B had written first, A would have erased B's Database section. | Same fix as F3. Also log a re-read event before every write so compliance can be audited. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1:** Whether A's API text can be recovered. This is settled by whether the store retains version `b2`.
- **S2:** Whether the orchestrator ever read `plan.md`. This is settled by the orchestrator's own log, which was not supplied.

## REFUTED

- **R1: "A violated the claim rule."** Refuted. `agent_a.jsonl` line 2 shows a successful claim before the write, and `claims.json` records it.
- **R2: "B's Database content is also missing or corrupted."** Refuted. The current `plan.md` contains `## Database` with the described content.

## WHAT HOLDS UP

- A followed rule 1.
- B's Database section is present and coherent.
- The Overview from `a1` survived.
- Both logs are internally consistent and timestamped, which is what made this failure traceable.

## UNVERIFIED CLAIMS

- **A's `final` message ("API section added").** True at 10:00:20 but false now. Confirming the original content requires `b2`.
- **"Both agents finished without errors."** Possibly true at the tool level, but meaningless as evidence of success. Confirm it with the tool's return values.

## QUESTIONS FOR THE AUTHOR

1. Is version `b2` retrievable?
2. Does `write_file` check `base_sha` at all?

## DECISION-MAKER SUMMARY

The run did not deliver the request. The plan has no API section, and the orchestrator's summary wrongly says it does. Restore or rewrite the API section and verify the file directly before the sprint uses it. Make writes reject stale versions, or the same silent loss will recur.

## OWNER SUMMARY

The shared plan is missing its API section because the second agent saved over the first agent's work. The run summary wrongly says both sections are there. The API part needs to be restored or rewritten and checked before the plan is used, and the tooling should be fixed so a save on top of an outdated copy is refused.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "shared/plan.md at sha b2", "status": "not_seen", "matters": true},
    {"item": "shared/plan.md at sha a1", "status": "not_seen", "matters": false},
    {"item": "write_file and claim tool implementations", "status": "not_seen", "matters": true},
    {"item": "orchestrator log", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "agent_a.jsonl", "kind": "file"},
      {"unit": "agent_b.jsonl", "kind": "file"},
      {"unit": "coordination.md", "kind": "file"},
      {"unit": "shared/claims.json", "kind": "file"},
      {"unit": "shared/plan.md", "kind": "file"},
      {"unit": "summary.md", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "write_file/claim tool code", "reason": "not supplied"},
      {"unit": "plan.md version history", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shared/plan.md; agent_b.jsonl line 2 (base_sha a1, ts 10:00:30)",
     "scenario": "B, without claiming or re-reading, replaced the whole file from stale base a1 after A wrote b2; the API section is gone and the sprint is planned without it.",
     "fix": "Restore A's API text from b2 or re-run A on the current file, then verify both headings exist.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Order both logs by ts: B's write at 10:00:30 has base_sha a1 while current is b2. grep '^## API' shared/plan.md returns nothing; '^## Database' hits (positive control)."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "summary.md line 3",
     "scenario": "The orchestrator reports both sections present without reading the file; readers skip verification and rely on an incomplete plan.",
     "fix": "Orchestrator reads shared/plan.md after all agents finish and asserts each required heading, reporting failure if any is missing.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare summary.md line 3 with the current shared/plan.md: no '## API' heading exists."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "coordination.md rules 1-3; write_file tool",
     "scenario": "Section claims do not protect whole-file writes and write_file appears to accept a stale base_sha, so even compliant agents racing between re-read and write lose each other's work.",
     "fix": "Make write_file compare-and-swap on base_sha (reject on mismatch, agent re-reads and retries), or use per-section files merged at the end.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "Call write_file with a base_sha older than the current sha; expected rejection, observed (per agent_b.jsonl) success."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "agent_a.jsonl lines 1-3",
     "scenario": "A wrote 19 s after its only read, violating rule 2; had B written first, A would have erased the Database section.",
     "fix": "Same as F3; log a re-read event before every write so compliance is auditable.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "shared/plan.md version b2",
     "suspicion": "A's API text may be recoverable rather than needing a rewrite.",
     "unresolved_fact": "Whether the file store retains version b2."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "summary.md",
     "suspicion": "The orchestrator never read plan.md before summarizing.",
     "unresolved_fact": "The orchestrator's own tool log (not supplied)."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A violated the claim rule.", "evidence": "agent_a.jsonl line 2 shows claim api ok:true before the write; claims.json records it."},
    {"id": "R2", "candidate": "The Database section is also lost or corrupted.", "evidence": "Current shared/plan.md contains '## Database' with the described content."}
  ]
}
```