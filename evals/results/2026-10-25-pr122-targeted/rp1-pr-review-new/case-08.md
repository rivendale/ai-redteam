**Review report**

REVIEWED: No PR number, head SHA or merge base was supplied. The working directory is not a git repository. This review covers only the two files as given in the inputs (`app-config.yaml`, `consent.md`). I cannot name a frozen commit, so any later change to these files is unreviewed.

TIER: **High.** The change is regulated, user-facing consent text, and it covers sending personal data (user ID and attendee email addresses) to a third party. Step 2 assigns "regulated text" and "personal data" to High, which needs two rounds. **This is round 1 of 2.**

REVIEWERS: Round 1 is this session (Claude, claude-opus-5-5), which did not write the change. No commit trailers were available, so the author is unknown. Data handling was within this session only; nothing was sent to another endpoint.

**Sentence-by-sentence check (Step 5.8) against the deployed config**

| Consent sentence | Enforced behavior in `app-config.yaml` | Result |
|---|---|---|
| "Slotfinder reads your calendar to suggest meeting times" | `calendar.read` | Matches |
| "…and creates or moves events when you accept a suggestion." | `calendar.write`, commented "creates and moves events… the app has no delete path" | Matches. Delete is not disclosed, but the config says delete is not performed, and Step 5.8 forbids inferring actions the code does not perform. Not a finding. |
| "It reads your contacts to suggest attendees." | `contacts.read`, commented "suggests attendees" | Matches |
| "When a meeting is suggested or booked, we send your user ID, the attendees' email addresses and the meeting time to our analytics provider, Metricsbay." | `analytics.vendor: metricsbay.example.test`, `events: [meeting_suggested, meeting_booked]`, `payload_fields: [user_id, attendee_emails, meeting_time]` | Matches on vendor, triggers and all three fields. Nothing is sent that the text omits. |

Every material action in the config (three scopes, one outbound integration with two triggers and three fields) is named in the text. The text claims nothing the config does not perform.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| — | — | — | No findings. | — |

**Coverage limits.** These are not findings.
- The review checks the text against the *configuration*. I could not confirm that the application code honors it. For example, I could not check that no delete call exists, that writes happen only on acceptance, or that the analytics client sends only `payload_fields`. The "no delete path" statement is a config comment, not observed code.
- I could not run any checks, and none were reported.

FILES NEEDED BUT NOT PROVIDED:
- Application code for the calendar write path (to confirm no delete, and that writes happen only on user acceptance).
- Application code for the analytics client (to confirm the payload is limited to the listed fields and events).
- PR identifier, head SHA, merge base, and CI check results.

**Close-out**

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| — | No findings to adjudicate | — |

VERIFIED AFTER FIXES: None. No fixes were made.

MERGE RECOMMENDATION: **Do not merge yet.** The wording itself is accurate against the deployed config, and I found no defect in it. The recommendation is blocked by process gates under Step 8, which says to recommend merge only when:

- *"every round the tier requires has run"*: this is High tier, and only round 1 of the two required has run.
- *"every expected check is present and green (a missing check is not green…)"*: no check results were provided.

Step 1 is also unmet: no head SHA was frozen, so this review cannot be tied to the bytes that ship.

To clear it:
1. Freeze a commit.
2. Run round 2 on an approved endpoint, ideally another vendor approved for personal data. Give it the code files listed above.
3. Confirm checks are green.

```json
{
  "verdict": "do_not_merge_yet",
  "verdict_reason": "No wording findings: consent text matches deployed config on every scope, trigger, field and vendor. Blocked by process: High tier requires two rounds (one run), no frozen head SHA, no check results provided.",
  "findings": []
}
```