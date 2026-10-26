# pr-review: Slotfinder consent screen text vs. deployed configuration

## Review report

**REVIEWED:** No PR number, head SHA or merge base was supplied. The workspace is not a git repository. Step 1 is not met. This review covers only the two files as given in this session: `app-config.yaml` (header says deployed 2026-10-19) and `consent.md`. It is not tied to any commit. If either file changes before release, those changes are unreviewed.

**TIER:** High. This is regulated, customer-facing consent text, and the grant covers personal data: attendee email addresses sent to a third-party analytics vendor. High tier needs two independent rounds, ideally from two vendors. This is round 1 of 2. Round 2 has not run.

**DATA HANDLING (Step 3):** The material is consent text and a config file. It contains no secrets and no personal data records. It was reviewed in this session only and not sent to any other endpoint. Whoever runs round 2 must pick an endpoint approved for this material.

**REVIEWERS:**
- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), a separate instance that did not write the change.
- Author: unknown. No commits or `Co-Authored-By` trailers were available.

### Sentence-by-sentence check (Step 5.8)

| # | Consent sentence | What the config enforces | Result |
|---|---|---|---|
| 1 | "Slotfinder reads your calendar to suggest meeting times" | `calendar.read` scope (`app-config.yaml:3`) | Matches |
| 2 | "…and creates or moves events when you accept a suggestion." | `calendar.write`: "creates and moves events on the user's behalf; the app has no delete path" (`app-config.yaml:4`) | Matches on create and move. No delete is performed, so none needs to be named. The config cannot confirm the "when you accept" trigger (coverage gap, see below). |
| 3 | "It reads your contacts to suggest attendees." | `contacts.read`: "suggests attendees" (`app-config.yaml:5`) | Matches |
| 4 | "When a meeting is suggested or booked, we send your user ID, the attendees' email addresses and the meeting time to our analytics provider, Metricsbay." | vendor `metricsbay.example.test`, events `[meeting_suggested, meeting_booked]`, payload `[user_id, attendee_emails, meeting_time]` (`app-config.yaml:8-10`) | Matches. Vendor, both trigger events and all three fields are named. |

Every material action in the config appears in the text. The text describes no action the config does not perform.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| — | — | — | No findings. Every consent sentence is kept by the enforced configuration. | — |

### Coverage gaps (not findings)

1. **Acceptance gate.** Sentence 2 says events are written "when you accept a suggestion." The config grants write access but cannot show that writes happen only after the user accepts. Confirming this needs the booking code path.
2. **Analytics payload.** `payload_fields` is a config declaration. Confirming that the analytics client sends only these fields, and only on these two events, needs the client code.
3. **Release version.** The config is the one deployed on 2026-10-19. The text ships with the *next* release. If that release changes scopes, events or payload fields, this review does not cover it.

### FILES NEEDED BUT NOT PROVIDED

- Event create/move code path, to confirm writes are gated on user acceptance.
- Metricsbay client or serializer code, to confirm the actual payload and triggers.
- `app-config.yaml` as it will ship in the next release, at a fixed commit.
- PR identifier, head SHA and merge base SHA.

## Close-out

**ADJUDICATION:** No findings to adjudicate. Per the output format, the author adjudicates findings, not the reviewer.

**VERIFIED AFTER FIXES:** None. No fixes were made.

**MERGE RECOMMENDATION: do not merge yet.** The wording itself is accurate against the deployed config, but Step 8's gates are not met:

- Step 2: "a High-tier PR whose second round has not run is not reviewed." Round 2 is outstanding.
- Step 1: no head or merge-base SHA, so there is no frozen target.
- Step 8: "every expected check is present and green (a missing check is not green…)." No check results were provided.

Next steps:
1. Freeze the release commit.
2. Supply the next-release config and the two code paths listed above.
3. Run round 2 on an approved endpoint, preferably from a different vendor.

```json
{
  "verdict": "do_not_merge_yet",
  "findings": []
}
```