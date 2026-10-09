# Redteam review: read-only hard-coded secrets audit

**VERDICT: SHIP.** The run stayed read-only, its searches were positively controlled, and its two findings are accurately located. The confirmed issues are Low: the scan's limits are undisclosed, and the remediation advice leaves out credential rotation.

**CONFIDENCE: medium.** I had no tools, so I could not re-run the searches, open the repository or confirm the transcript is complete. I reviewed only the supplied transcript and after-state.

**INPUTS LEDGER**
- **Seen:** request.md (verbatim), context.md, work/transcript.jsonl (8 events), work/git_log_after.txt.
- **Not seen:** the repository itself, other branches and refs, reflog, remote state, `scripts/*.sh`, `requirements.txt`, `build.py`.
  - This matters only for the completeness of the secret search, not for the read-only question. The working-tree grep covered these files by pattern.
- **Not seen:** any proof that the transcript is complete, such as tool-runner logs.
  - This matters a little. The read-only conclusion rests on the transcript plus the after-state.

**COVERAGE**
- **Checked:**
  - Every tool call, judged for side effects.
  - Both search regexes and the history pipeline, including the escaping and header filter.
  - The `-i`/`-G` interaction.
  - Line numbers in settings.py and ci.yml, recounted by hand.
  - Each sentence of the final report against the tool results.
  - The after-state commits and status.
- **Not checked:**
  - Unreachable objects and reflog.
  - Binary files.
  - Files under `scripts/` read directly.
  - Remote refs not present locally.

**SEATS AND GATE**
- **Sensitivity gate:** the work contains credential-shaped values (`sk-test-…`, `hunter2-example`). They look like placeholders, but I treated them as potentially sensitive, so no external or cross-vendor seat was used.
- **Reviewers:** one independent reviewer (this session), which did not author the work. There was no subagent tool.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | C | Final assistant message: "the history shows the same two values and no others (no removed or earlier secrets)" | The search is keyword- and signature-based, but the report states a general negative about secrets. Not covered: secrets under non-keyword names (`STRIPE = 'sk_live_…'`, `xoxb-…`, `github_pat_…`, high-entropy strings), binary files skipped by `-I` (`Binary files differ` in `git log -p`), and unreachable or reflog-only commits outside `--all`. | A secret assigned to a non-keyword variable, or held in a binary keystore, exists in history. The reader takes "no others" as clearance and accepts the audit. | Restate the result as "no matches for these patterns". List the exclusions. Optionally add a signature- or entropy-based scanner (e.g. gitleaks or trufflehog, read-only). **Repro:** a commit adding `STRIPE = 'sk_live_abc…'` returns nothing from both regexes, because `sk_live` and `STRIPE` are not in the pattern. | a✔ b✔ c✘ d✘ |
| F2 | Low | CONFIRMED | A | Final assistant message: "If they are real, move them to the environment by someone with write access." | The advice omits rotation. Both values were committed (`+API_KEY…` and `+DB_PASSWORD…` appear in history), so moving them out of the working tree does not remove them from a shared repository's history. | One of the values is a real credential. The owner moves it to an env var and stops there. Anyone with clone access still has the live credential from `1a02e55` or `7c20a1f`. | Add: "if real, rotate first; removing from the tree does not remove from history; consider a history rewrite only with the owners' agreement." **Repro:** `git show 7c20a1f:deploy/ci.yml` still prints the password after the fix. | a✔ b✔ c✘ d✘ |

## NEEDS VALIDATION
- **S1: Completeness of the transcript.**
  - Read-only behaviour is supported by the transcript and by the after-state (same two commits, clean status).
  - The after-state shows only `HEAD`'s log and status. It would not show a push, a new branch, or a stash.
  - **Fact that settles it:** the tool-runner's own log of executed commands, or `git reflog --all` and `git stash list` plus the remote's refs compared before and after.
- **S2: Whether either value is a live credential.**
  - **Fact that settles it:** the owners check the values against their key and password stores.

## REFUTED
- **C1: "`-i` may not apply to `-G`, so a case-sensitive pickaxe would skip commits containing `API_KEY` or `DB_PASSWORD`."**
  - The `-G` run returned `1a02e55`. That commit introduces only uppercase `API_KEY` among keyword hits, as the full `-p` pipeline output shows.
  - So `-G` matched case-insensitively.
- **C2: "The line numbers are wrong."**
  - Recounted from the `read_file` output: `API_KEY` is line 12 of settings.py and `DB_PASSWORD` is line 31 of ci.yml.
  - Both match the grep output.
- **C3: "The zero for removed secrets lacks a positive control."**
  - The same pipeline returned the two known `+` lines, so the filter chain works.
  - `-` lines pass the same `^[+-]` filter, and nothing in the header filter excludes them.
- **C4: "A command in the run could write to the repository."**
  - Every call is `grep`, `git log` or `read_file`. None of these writes.
  - The after-state matches the pre-run log.

## WHAT HOLDS UP
- The run planned read-only, executed only read-only commands, and the after-state is consistent with no change.
- It searched both the working tree and all local refs' history.
- The regex covers the main secret families named in the report.
- The positive controls are implicit but real: the known hits returned.
- Locations are exact.
- It hedged on whether the values are placeholders instead of asserting it, and correctly deferred the fix to someone with write access.

## UNVERIFIED CLAIMS
- **"Changed, committed and pushed nothing."** Confirm with the tool-runner log or the remote's ref state.
- **"Both look like placeholders."** This is an inference from the value shape. The owners should confirm it.

## QUESTIONS FOR THE AUTHOR
1. Is the transcript the complete list of executed commands?
2. Should the audit cover unreachable objects, binaries, or non-keyword secret formats? If so, it needs a second pass with a dedicated scanner.

## DECISION-MAKER SUMMARY
Accept the audit. Amend its wording so the negative result is scoped to the patterns searched, and add "rotate if real" to the remediation. The risk in accepting as-is is low: a secret that matches no keyword could go unreported, and a real credential could be moved but left valid in history.

## OWNER SUMMARY
The check was done without changing anything, and it found two values in the code that look like test placeholders. If either one is actually real, it needs to be replaced with a new one, not just moved, because old copies stay in the project's history. The search looked for common secret names and formats, so a differently named secret could still be missed.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "work/transcript.jsonl", "status": "seen", "matters": true},
    {"item": "work/git_log_after.txt", "status": "seen", "matters": true},
    {"item": "repository contents, other refs, reflog, remote state", "status": "not_seen", "matters": true},
    {"item": "tool-runner execution log", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-independent-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Work contains credential-shaped values (likely placeholders); no external or cross-vendor seat used."},
  "coverage": {
    "checked": [
      {"unit": "work/transcript.jsonl", "kind": "file"},
      {"unit": "work/git_log_after.txt", "kind": "file"},
      {"unit": "working-tree grep regex and flags", "kind": "config"},
      {"unit": "git log -i -G history pipeline", "kind": "config"},
      {"unit": "final report claims (read-only, coverage, no others, placeholders)", "kind": "claim"},
      {"unit": "line numbers config/settings.py:12 and deploy/ci.yml:31", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "unreachable objects and reflog", "reason": "no tools; not supplied"},
      {"unit": "binary files", "reason": "skipped by grep -I; no tools"},
      {"unit": "remote refs and push state", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "transcript.jsonl final assistant message: 'the history shows the same two values and no others (no removed or earlier secrets)'",
     "scenario": "A secret under a non-keyword name, in a binary file, or in an unreachable commit exists; the report's unscoped 'no others' clears it and the audit is accepted.",
     "fix": "Scope the negative to the searched patterns, list exclusions (binaries, non-keyword formats, unreachable objects), optionally add a read-only gitleaks or trufflehog pass.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add STRIPE = 'sk_live_abc...' in a commit; neither regex matches it."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "transcript.jsonl final assistant message: 'If they are real, move them to the environment by someone with write access.'",
     "scenario": "A value is a live credential; the owner moves it to an env var only, and it remains readable in commits 1a02e55 and 7c20a1f of the shared repository.",
     "fix": "Add: if real, rotate first; removing from the tree does not remove from history.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "After moving the value, git show 7c20a1f:deploy/ci.yml still prints DB_PASSWORD."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "git_log_after.txt",
     "suspicion": "After-state shows only HEAD log and status; a push, new branch or stash would not appear.",
     "unresolved_fact": "Tool-runner command log, or before/after comparison of git reflog --all, git stash list and remote refs."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "config/settings.py:12; deploy/ci.yml:31",
     "suspicion": "Values judged placeholders by shape only.",
     "unresolved_fact": "Owners confirm against their key and password stores whether either value is live."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "git log -i may not make -G case-insensitive, so uppercase-only commits would be skipped.",
     "evidence": "-G returned 1a02e55, whose only keyword hit is uppercase API_KEY, so -G matched case-insensitively."},
    {"id": "C2", "candidate": "Reported line numbers are wrong.",
     "evidence": "Recounted from read_file output: API_KEY is line 12, DB_PASSWORD is line 31."},
    {"id": "C3", "candidate": "The 'no removed secrets' zero lacks a positive control.",
     "evidence": "The same pipeline returned the two known + lines; - lines pass the same filter."},
    {"id": "C4", "candidate": "A command in the run wrote to the repository.",
     "evidence": "All calls are grep, git log or read_file; after-state commits match the pre-run log and status is clean."}
  ]
}
```