# Review report

**REVIEWED:** The Slotfinder consent screen text (`consent.md`) checked against the deployed configuration (`app-config.yaml`, which says it was deployed 2026-10-19).
- **No head SHA or merge base SHA can be recorded.** The inputs were pasted files, not a PR, and the working directory is not a git repository.
- This review covers only the text shown below. If these files differ from what ships in the next release, the shipped version has not been reviewed.

**TIER:** High.
- The change is regulated, customer-facing consent text.
- Users grant OAuth access based on this text.
- The configuration shows personal data (user IDs and third-party attendee emails) going to an outside vendor.

**Tier status:** The High tier requires two rounds, ideally from two vendors. Only this one round has run, so **this PR is not yet reviewed** under the skill.

**Data handling (Step 3):** No code left this session. The inputs contain no secrets, only scope names and a vendor hostname. A second-round reviewer must be on an endpoint approved for configuration that describes personal-data flows.

**REVIEWERS:**
- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), a fresh session with no part in writing the text, using static reading only. No tools were run and no links were opened.
- Author: unknown. No commit trailers were provided.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `consent.md:4`, contradicted by `app-config.yaml:7-10` | The consent text says "We never share your data with anyone." The deployed config sends `meeting_suggested` and `meeting_booked` events to `metricsbay.example.test`, carrying `user_id`, `attendee_emails` and `meeting_time`. A user who books one meeting therefore has their ID, the meeting time and every attendee's email sent to a third party. That consent was obtained with a false statement. The attendees, whose emails come from the user's calendar and contacts, never saw any consent screen at all. | A text-vs-config check that fails when any `integrations.*.vendor` is configured while the consent text contains an absolute no-sharing claim, or does not name that recipient and the categories in `payload_fields`. It fails today. |
| 2 | **P1** | `consent.md:3`, against `app-config.yaml:4` | The text discloses only reading the calendar ("reads your calendar to suggest meeting times"). The app requests `calendar.write`, which by the config's own comment "creates and moves events on the user's behalf." A user who consents to suggestions finds meetings created or moved, including ones that other attendees see, with no disclosure that this could happen. | Assert that every scope in `oauth_scopes` maps to a disclosed capability in the consent text. `calendar.write` has no match today. |
| 3 | **P1** | `consent.md:3`, against `app-config.yaml:5` | `contacts.read` is requested ("suggests attendees") but the text never mentions contacts. The user's address book is read with no disclosure. Combined with #1, contacts-derived emails can end up in `attendee_emails` sent to the analytics vendor. | Same scope-to-disclosure check as #2. `contacts.read` fails today. |
| 4 | P2 | `app-config.yaml:4` (comment) | The comment "the app has no delete path" is an unverified assertion. The `calendar.write` scope as granted typically permits deletion, so the limit exists only in app code that was not provided. If the corrected consent text promises "never deletes" on the strength of this comment, a code path or later change that deletes events would make the new text false as well. Moving an event can also have the same effect on attendees as cancelling it. | A test against the calendar client wrapper asserting that no delete or cancel call can be issued, plus a code search in CI for delete endpoints. Its status today is unknown because the code was not provided. |

## FILES NEEDED BUT NOT PROVIDED
- Application source: the calendar client, the analytics emitter, and the attendee-suggestion code. These are needed to confirm that the config is what actually runs, that no other egress exists, and that #4's "no delete path" claim holds.
- The rendered consent screen as shipped, plus the OAuth provider's own scope-consent screen.
- Privacy policy and the data processing agreement with metricsbay, to see whether the vendor relationship is disclosed elsewhere. That would not cure #1, because the consent text makes an absolute claim.
- Repository, head SHA and merge base for this release.
- CI and check results.

---

# Close-out

**ADJUDICATION:** Pending.
- A reviewer never adjudicates its own findings.
- The author must record Accepted (with fix and evidence), Deferred (#4 only, with an issue link) or Rejected (with evidence) for each finding.
- #1–#3 are P0/P1 and cannot be deferred.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — pending author | — |
| 2 | — pending author | — |
| 3 | — pending author | — |
| 4 | — pending author | — |

**VERIFIED AFTER FIXES:** Nothing yet; no fixes exist.

A corrected text would need to say three things:
- it creates and moves calendar events;
- it reads contacts to suggest attendees;
- it shares the user ID, meeting times and attendee emails with a named analytics provider.

Alternatively, `attendee_emails` and `user_id` could be removed from `payload_fields`. That fix would be verified by a targeted read of the config diff plus the text-vs-config check above.

**MERGE RECOMMENDATION: do not merge.**
- **P0 #1:** the consent text is false about third-party sharing.
- **P1 #2 and #3:** scopes are undisclosed.
- **Second round not run:** the High tier's required second round has not run.
- **No SHAs:** no SHAs could be frozen.
- **No CI:** no checks were provided, and a missing check is not green.
- **Pending decision:** product, legal and privacy owners must decide whether to keep sending attendee emails to the analytics vendor at all. Those attendees are third parties who cannot consent through this screen.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "direct: contradiction visible between consent text and deployed config; runtime behavior not executed",
      "location": "consent.md:4; app-config.yaml:7-10",
      "scenario": "Consent says 'We never share your data with anyone' but meeting_suggested/meeting_booked events send user_id, attendee_emails and meeting_time to metricsbay.example.test; users consent on a false statement and attendees' emails reach a third party without their consent.",
      "fix": "Either stop sending user_id/attendee_emails to the vendor, or replace the absolute claim with an accurate disclosure naming the analytics recipient and data categories; add a text-vs-config check that fails on undisclosed vendors."
    },
    {
      "severity": "P1",
      "evidence_level": "direct: scope listed in config, absent from consent text",
      "location": "consent.md:3; app-config.yaml:4",
      "scenario": "Text discloses only reading the calendar, but calendar.write is requested and the app creates and moves events on the user's behalf, including events visible to other attendees.",
      "fix": "Disclose that the app creates and moves calendar events; add a scope-to-disclosure test."
    },
    {
      "severity": "P1",
      "evidence_level": "direct: scope listed in config, absent from consent text",
      "location": "consent.md:3; app-config.yaml:5",
      "scenario": "contacts.read is requested to suggest attendees but never disclosed; contacts-derived emails can flow into the analytics payload.",
      "fix": "Disclose contact access and its purpose, or drop the scope; cover with the scope-to-disclosure test."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified claim: source code not provided",
      "location": "app-config.yaml:4",
      "scenario": "'No delete path' is asserted in a comment only; the calendar.write scope permits deletion, so the limit depends on unseen code. Any corrected consent text relying on it could become false, and moving events can effectively cancel them for attendees.",
      "fix": "Provide the calendar client code and add a test or CI check proving no delete/cancel call exists before any consent text promises it."
    }
  ]
}
```