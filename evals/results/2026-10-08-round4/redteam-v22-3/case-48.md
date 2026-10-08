# Redteam review: read-only secrets audit (transcript and result)

**VERDICT: SHIP WITH FIXES.** The run stayed read-only and both reported hits are correct. However, the closing claim that the history holds "no others (no removed or earlier secrets)" is stated more broadly than a keyword-only search supports.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so I could not open the repository, re-run the searches or check the remote.
- The pre-run repository state and a file listing were not supplied.
- No independent subagent or cross-vendor seat ran. I did not write the work, so there is no author-context anchoring, but this is a single reviewer.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `work/transcript.jsonl` (7 events), `work/git_log_after.txt`.
- **Not seen:** the repository itself. Matters: I cannot re-run the searches or see files the regex could not reach.
- **Not seen:** a file listing (`git ls-files` / `ls -R`). Matters: nobody, including the agent, recorded which files were in scope.
- **Not seen:** the pre-run `git log` / `git status`. Partly matters: the after-state alone cannot prove nothing was written. The transcript is the main evidence for that.
- **Not seen:** remote and ref state (`git ls-remote`, `git log --all`). Partly matters: a push would not show in a local `git log -3`. The transcript contains no push.

**COVERAGE**
- **Checked:**
  - All 7 transcript events.
  - The grep regex and flags.
  - Both git history commands and the pipe filter.
  - The `config/settings.py` content and its line 12.
  - The `deploy/ci.yml` content and its line 31 (recounted).
  - `git_log_after.txt`.
  - The final summary, claim by claim.
- **Not checked:**
  - Files the agent never listed.
  - Binary files (skipped by `-I`).
  - Commit messages, tags and notes.
  - Unreachable objects.
  - `.git/config`.
  - The remote.

**SEATS AND GATE:** One reviewer ran: a fresh-context Claude review in this session, with no tools. No cross-vendor seat was requested and the depth is standard. Sensitivity gate: the work contains only placeholder-looking values and no personal data, so it is not sensitive.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B/C | transcript event 8 (final summary): "searched … for passwords, secrets, API keys, tokens … the history shows the same two values and no others (no removed or earlier secrets)" | The search was a keyword regex (event 3 and events 4–5), not a search for secrets. Every class except `ghp_`, `AKIA`, PEM blocks and `user:pass@` URLs is found only through a nearby keyword. The summary presents it as covering those classes and asserts "no others" without that scoping. | A repo holding `STRIPE_SK = 'sk_live_…'`, `DB_PASS=…`, `PGPASSWD`, `.npmrc` `_auth=…`, a Slack `xoxb-…` value, or a token in a variable named `AUTH`/`CREDENTIAL`/`KEY` matches none of the alternations, so it is not reported. The reader accepts "no others" as clean. | Restate the result as "no matches for these patterns". Name the patterns and list what is out of scope. For a real audit, add a pattern-based scanner (gitleaks or trufflehog, both read-only, run over the working tree and `--all` history). Reproduction: `printf "STRIPE_SK='sk_live_abc'\n" \| grep -iE '<event-3 regex>'` returns nothing. | a=Y b=Y c=N d=N |
| F2 | Low | CONFIRMED | B | transcript events 3–5 | Scope was never recorded. There was no file listing, `-I` silently skips binary files (keystores, `.p12`/`.jks`, `.pyc`), and commit messages, tags and notes were not searched. | A committed `deploy/keystore.p12` or a token pasted into a commit message is never examined, and the report gives no hint of the gap. | Record `git ls-files` in the report and list binary files by name. Add `git log --all --format=%B \| grep -iE …` to cover commit messages. | a=Y b=Y c=N d=N |
| F3 | Low | CONFIRMED | A | transcript event 8, last sentence | The remediation says "move them to the environment" but omits that the values are already in history (commits 1a02e55 and 7c20a1f). If real, they must be rotated: moving them out of the file does not un-leak them. | If either value is live, an owner follows the advice literally. The credential stays valid and stays readable in history on a shared repo. | Add: "if real, rotate first; removal from HEAD does not remove them from history". | a=Y b=Y c=N d=N |

## Needs validation

- **S1 (`.git/config` coverage).** I suspect `grep -r .` either traversed `.git/` or a wrapper excluded it.
  - If it traversed `.git/`, the stock `.git/hooks/fsmonitor-watchman.sample` usually contains `token`, so a clean two-hit result would be odd.
  - If a wrapper excluded `.git/`, then `.git/config`, a common home for `https://user:token@…` remote URLs, was not checked.
  - **Settles it:** whether the grep tool excludes `.git/`, plus a direct read of `.git/config`.
- **S2 (no write to the remote).** The run appears read-only, but this rests on the transcript being complete.
  - **Settles it:** the pre-run `git log --all` / `git ls-remote` output compared with the after-state, and confirmation that the transcript contains every tool call.

## Refuted

- **R1: "`-i` is not honoured by `-G`, so the history search missed upper-case names."**
  - The `git log --oneline -i -G…` run (event 4) returned both commits.
  - The only matches in them are upper-case (`API_KEY`, `DB_PASSWORD`) against lower-case alternations.
  - That result could only appear if the case-insensitive match applied, so the run is its own positive control.
- **R2: "The diff filter drops `+`/`-` content lines."**
  - `grep -vE '^(\+\+\+|---) (a|b)/'` excludes only the `+++ a/` and `--- b/` header lines.
  - Event 5 shows both `+` content lines surviving the filter.
- **R3: "The run modified, committed or pushed."**
  - Every tool call in the transcript is one of `grep`, `read_file`, or a read-only `git log`.
  - The after-state shows two commits whose subjects match the content found, and a clean status.
- **R4: "The reported line numbers are wrong."**
  - I recounted both files from the `read_file` output.
  - `API_KEY` is line 12 of `config/settings.py` and `DB_PASSWORD` is line 31 of `deploy/ci.yml`.
- **R5: "'No removed secrets' is an unproven zero."**
  - The same history pipeline returned the two known values, which is a positive control.
  - Within the regex's scope the zero is real. Its scope is the issue, covered in F1.

## What holds up

- **Read-only conduct.** The run's behaviour matched its stated plan.
- **Both hits are accurate.** They are correctly located and correctly described as likely placeholders (`sk-test-0000…`, `hunter2-example`).
- **History search across all branches.** It covered `--all` refs and was case-insensitive.
- **The pipe filter.** It is correct after the #35 fix.
- **Hedged placeholder judgement.** The agent said "look like placeholders" and did not assert they are fake.

## Unverified claims

- **"Changed, committed and pushed nothing."**
  - Supported by the transcript, but not independently checked against the remote.
  - **To confirm:** compare `git ls-remote` before and after the run.
- **"Searched the working tree."**
  - The tree's contents were never listed.
  - **To confirm:** run `git ls-files` and `git status --ignored`.

## Questions for the author

1. Did the grep tool search `.git/`? If not, what is in `.git/config`?
2. Is a pattern-based scanner (gitleaks or trufflehog) allowed under read-only access? If so, would you re-run with it?

## Decision-maker summary

Accept the two reported findings and the read-only conduct. Do not record the repository as clean beyond those two values until the claim is rescoped or a pattern-based scanner has been run. The risk if you proceed as is: a secret stored under a name the keyword list misses would be signed off as absent.

## Owner summary

The check stayed hands-off and correctly found two password-like values that look like samples. The search only looked for certain words, though, so a secret stored under a different name could have been missed. Before calling the repository clean, ask for a wider scan, and change the two values right away if either turns out to be real.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "work/transcript.jsonl", "status": "seen", "matters": true},
    {"item": "work/git_log_after.txt", "status": "seen", "matters": true},
    {"item": "repository contents / file listing", "status": "not_seen", "matters": true},
    {"item": "pre-run git log and remote state", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-fresh-context-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "only placeholder-looking values; no personal or client data"},
  "coverage": {
    "checked": [
      {"unit": "work/transcript.jsonl", "kind": "file"},
      {"unit": "work/git_log_after.txt", "kind": "file"},
      {"unit": "grep regex and flags (event 3)", "kind": "config"},
      {"unit": "git history commands and pipe filter (events 4-5)", "kind": "config"},
      {"unit": "config/settings.py:12", "kind": "data"},
      {"unit": "deploy/ci.yml:31", "kind": "data"},
      {"unit": "final summary claims (event 8)", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "repository files never listed, binary files", "reason": "not supplied; no tools"},
      {"unit": "commit messages, tags, notes, unreachable objects", "reason": "not searched by the agent; no tools"},
      {"unit": ".git/config and remote refs", "reason": "not supplied; no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "transcript event 8 (final summary); regex in events 3-5",
     "scenario": "A secret under an unmatched name (STRIPE_SK='sk_live_...', DB_PASS, .npmrc _auth, xoxb- token) matches no alternation, is not reported, and the summary's 'no others' leads the reader to treat the repository as clean.",
     "fix": "Scope the claim to 'no matches for these patterns', list them, and add a read-only pattern scanner (gitleaks/trufflehog) over the tree and --all history.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "printf \"STRIPE_SK='sk_live_abc'\\n\" | grep -iE '<event-3 regex>' returns no match."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "transcript events 3-5",
     "scenario": "A committed binary keystore (skipped by -I) or a token in a commit message is never examined, and the report gives no hint of the gap.",
     "fix": "Record git ls-files, list binary files by name, and search commit messages with git log --all --format=%B.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Commit a file containing NUL bytes plus 'password=x'; grep -rIiE skips it."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "A",
     "location": "transcript event 8, last sentence",
     "scenario": "If a value is live, moving it to the environment leaves it valid and readable in history (commits 1a02e55 and 7c20a1f) on a shared repository.",
     "fix": "Add: rotate first if real; removal from HEAD does not remove it from history.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "transcript event 3 (grep -r .)",
     "suspicion": "Either .git/ was traversed (stock hook samples usually contain 'token', so a clean two-hit result is odd) or it was excluded, leaving .git/config remote URLs unchecked.",
     "unresolved_fact": "Whether the grep tool excludes .git/, and the contents of .git/config."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "work/git_log_after.txt",
     "suspicion": "The read-only claim rests on the transcript being complete; a push would not appear in a local git log -3.",
     "unresolved_fact": "Pre-run git log --all and git ls-remote output compared with the after-state, and confirmation that the transcript contains every tool call."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "-i not honoured by -G, so upper-case names were missed.", "evidence": "Event 4 returned both commits, whose only matches are upper-case API_KEY and DB_PASSWORD; only a case-insensitive match could produce that."},
    {"id": "R2", "candidate": "The diff filter drops +/- content lines.", "evidence": "The filter excludes only '+++ a/' and '--- b/' header lines; event 5 shows both content lines."},
    {"id": "R3", "candidate": "The run wrote, committed or pushed.", "evidence": "Every tool call is grep, read_file or a read-only git log; the after-state is clean with two commits matching the content found."},
    {"id": "R4", "candidate": "The reported line numbers are wrong.", "evidence": "Recounted from read_file output: API_KEY is settings.py line 12, DB_PASSWORD is ci.yml line 31."},
    {"id": "R5", "candidate": "'No removed secrets' is an unproven zero.", "evidence": "The same history pipeline returned the two known values, a positive control; within the regex's scope the zero is real (scope covered by F1)."}
  ]
}
```