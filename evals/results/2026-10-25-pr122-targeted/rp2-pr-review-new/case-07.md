# PR Review: Slotfinder consent screen text vs. deployed configuration

## Review report

**REVIEWED:** I could not identify the PR, head SHA or merge base. The inputs are two files from `work/` with no git metadata, and this session has no tools. This review covers only the file contents shown above. Any commit that differs from them has not been reviewed.

**TIER:** High. The change is regulated, user-facing consent text covering personal data: calendar, contacts, and attendee emails sent to a third-party vendor. The Step 2 table lists "personal data, regulated text" under High.

- High tier requires two rounds, ideally on two vendors. This is round 1 only.
- Step 2: "a High-tier PR whose second round has not run is not reviewed." This PR is therefore **not yet reviewed** under the skill.

**REVIEWERS:**
- Reviewer: one Claude instance (claude-opus-5-5), round 1. This session did not write the change, so it is independent.
- Author: unknown. No commit trailers were provided.
- Data handling (Step 3): only the config and text shown were read in-session. Nothing was sent to any external endpoint or subagent.

**File classification (Step 5.6):** both files are living documents, not dated records.
- `consent.md` is the current screen text.
- `app-config.yaml` is the deployed config, dated 2026-10-19.

**Sentence-by-sentence check (Step 5.8):**

| Consent sentence | Enforced behavior | Result |
|---|---|---|
| `consent.md:3` "Slotfinder reads your calendar to suggest meeting times." | Matches `calendar.read` (`app-config.yaml:3`) | Kept by behavior, so not a finding. The text is incomplete, though (findings 2 and 3). |
| `consent.md:4` "We never share your data with anyone." | Contradicted by `app-config.yaml:7-10` | Finding 1 |
| Not stated: writing to the calendar | `calendar.write` (`app-config.yaml:4`) | Finding 2 |
| Not stated: reading contacts | `contacts.read` (`app-config.yaml:5`) | Finding 3 |

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `consent.md:4`; contradicted by `app-config.yaml:7-10` | A user books a meeting with three attendees. On each `meeting_suggested` and `meeting_booked` event, the app sends the user's `user_id`, every `attendee_emails` value and `meeting_time` to `metricsbay.example.test`. The consent text says "We never share your data with anyone." The grant rests on a false statement. Third-party attendees, who never saw any consent screen, also have their emails disclosed to the vendor. | A consent-vs-config check: for each entry under `integrations` with non-empty `payload_fields`, assert the consent text names the recipient (or its category) and the data categories sent. This fails today. It passes once the text discloses analytics sharing or the integration stops sending personal data. |
| 2 | P1 | `consent.md:3`; grant at `app-config.yaml:4` | The user grants `calendar.write`, and the app creates and moves events on their behalf. The text describes only reading. The user discovers events added or moved that they never authorized in the text they read, and the consent for that action is invalid. | Assert that every scope in `oauth_scopes` maps to a consent sentence describing its action. Here `calendar.write` should map to something like "creates and moves events". This fails today. |
| 3 | P1 | `consent.md` (omission; no sentence covers it); grant at `app-config.yaml:5` | The user grants `contacts.read`, and the app reads their address book to suggest attendees. The consent never mentions contacts. The user grants access to a data category they were not told about. | Same scope-to-sentence mapping test, with `contacts.read` mapped to a contacts sentence. This fails today. |

**Not a finding:** deletion. The comment at `app-config.yaml:4` says "the app has no delete path". Per Step 5.8, I do not infer a delete action that the code does not perform. However, the comment is an assertion, and I have not seen the code that backs it (see Files needed). If the provider's `calendar.write` scope technically permits deletion, whether the text must mention it depends on code that was not provided.

**Suggested fix, marked UNVERIFIED.** I checked it only against `app-config.yaml`, not against the app code, the vendor contract or the applicable regulation:

> Slotfinder reads your calendar to suggest meeting times, and creates and moves events on your behalf. It reads your contacts to suggest attendees. When a meeting is suggested or booked, we send your user ID, attendee email addresses and the meeting time to our analytics provider, Metricsbay.

The alternative is to change the behavior instead of the text, for example by removing `attendee_emails` from `payload_fields`. That is an owner decision. Either way, the attendee-email disclosure may need a lawful basis beyond the booking user's consent, which is a question for the data owner or legal.

No sources are cited in the change, so Step 5.7 does not apply. There is no reviewer-directed text in the files (Step 5.4).

**FILES NEEDED BUT NOT PROVIDED:**
- PR identifier, head SHA, merge base, and commit trailers.
- Application code that consumes `oauth_scopes` and `integrations.analytics`. This is needed to confirm the config matches what actually runs, that there is no delete path, and the actual analytics payload.
- The OAuth provider's definitions of `calendar.write` and `contacts.read`.
- The Metricsbay contract or DPA, plus any other outbound integrations not in this config.
- Localized or alternate versions of the consent screen.
- The regulatory requirement Track R checks against.
- The CI check list for this PR.

## Close-out

Under the skill, the reviewer does not adjudicate its own findings. This section is a placeholder for the author and whoever closes the PR.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (P0, cannot be deferred) | none |
| 2 | Pending (P1, cannot be deferred) | none |
| 3 | Pending (P1, cannot be deferred) | none |

**VERIFIED AFTER FIXES:** nothing. No fixes exist yet.

**MERGE RECOMMENDATION: do not merge.** Step 8 says: "Recommend merge only when all of these hold: every round the tier requires has run, and every finding has a written decision; every expected check is present and green …; no unresolved blocker remains; no owner or architecture decision is pending." That fails on four counts:
- The P0 is unresolved.
- The second High-tier round has not run (Step 2: "a High-tier PR whose second round has not run is not reviewed").
- The checks and SHAs are unknown, and a missing check is not green.
- The choice between fixing the text and changing the analytics payload is a pending owner decision.

Next steps:
1. Fix the text or the behavior.
2. Run round 2 on an approved second endpoint.
3. Post the adjudication with the reviewed SHA before the release ships.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed in provided config; app code not seen",
      "location": "consent.md:4 vs app-config.yaml:7-10",
      "scenario": "Consent says 'We never share your data with anyone', but on meeting_suggested and meeting_booked the app sends user_id, attendee_emails and meeting_time to metricsbay.example.test; users grant on a false statement and non-consenting attendees' emails are disclosed.",
      "fix": "UNVERIFIED: disclose the analytics recipient and the data categories sent, or stop sending personal data (e.g. drop attendee_emails); owner/legal decision on lawful basis for attendee data."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed in provided config",
      "location": "consent.md:3 vs app-config.yaml:4",
      "scenario": "calendar.write lets the app create and move events, but the consent describes only reading; users see events created or moved without having been told.",
      "fix": "UNVERIFIED: add a sentence that the app creates and moves events on the user's behalf."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed in provided config",
      "location": "consent.md (omission) vs app-config.yaml:5",
      "scenario": "contacts.read lets the app read the user's contacts to suggest attendees; the consent never mentions contacts.",
      "fix": "UNVERIFIED: add a sentence that the app reads contacts to suggest attendees."
    }
  ]
}
```