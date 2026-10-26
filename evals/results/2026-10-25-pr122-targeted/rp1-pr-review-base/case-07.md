# Review report

**REVIEWED:** Consent screen text (`consent.md`) checked against the deployed configuration (`app-config.yaml`, deployed 2026-10-19).
- **Head SHA:** not available.
- **Merge base SHA:** not available.
- The inputs were given inline, not as a PR or git repository, so no commit could be frozen. This review covers only the text shown above. Any version other than these exact bytes has not been reviewed.

**TIER:** High. The change is regulated, customer-facing consent text that governs OAuth access to calendars and contacts, and the app sends personal data to a third party. Two independent rounds are required. **This is round 1 of 2.** Until a second round runs, ideally on a different approved vendor, the PR is not reviewed under this skill.

**DATA HANDLING:** Nothing was sent outside this session. The material contains no personal data itself, only a description of how the app handles it.

**REVIEWERS:**
- **Reviewer:** this session (Claude Opus 5.5, `claude-opus-5-5`), single instance. It did not write the change.
- **Author:** unknown. No commit trailers were provided.

**METHOD:** Static comparison of each claim in the consent text against the scopes and integrations in the config. I had no tools, so nothing was run and no app code was available.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `consent.md:4`, contradicted by `app-config.yaml:7-10` | **The text says "We never share your data with anyone."** In reality, every `meeting_suggested` and `meeting_booked` event sends `user_id`, `attendee_emails` and `meeting_time` to a third-party analytics vendor (`metricsbay.example.test`). A user who books one meeting has their identifier and schedule shared, directly contradicting the screen they consented on. This is a false statement in regulated consent text, and it would invalidate the consent. | A consent-vs-config check: for each entry under `integrations.*`, require the consent text to name the recipient category and the data fields sent. It should fail today on `analytics`. |
| 2 | **P0** | `consent.md:3`, contradicted by `app-config.yaml:3-4` | **The text describes read-only access** ("reads your calendar to suggest meeting times"). The app actually requests `calendar.write` and, per the config comment, creates and moves events for the user. A user who grants access expecting read-only finds events created or rescheduled in their calendar. They never agreed to write access, even though users grant access based on this text. | A check that maps each entry in `oauth_scopes` to a required disclosure phrase. `calendar.write` should require something like "create and move events". It should fail today. |
| 3 | **P1** | `consent.md:3`, contradicted by `app-config.yaml:5` | **`contacts.read` is requested but never mentioned.** The consent screen says nothing about contacts. The user grants access to their whole address book without being told. | Same scope-to-disclosure check. `contacts.read` should require a phrase like "reads your contacts to suggest attendees". It should fail today. |
| 4 | **P1** | `app-config.yaml:10` (`attendee_emails`) | **Third parties' data goes to the vendor.** Attendee email addresses, which belong to people who never saw or accepted any consent screen, are sent to the analytics vendor. Correcting the user-facing text (finding 1) does not cover these people. The field also appears unnecessary for counting suggestion and booking events. This is a data-minimization and lawful-basis problem that the text alone cannot fix. | A test asserting that the analytics payload schema contains no third-party identifiers (no `attendee_emails`), or hashed or aggregated counts only. It should fail today. |
| 5 | **P2** | `app-config.yaml:4` (comment "the app has no delete path") | **"No delete path" is an unverified claim.** It is a comment, and no code was provided to back it. `calendar.write` as typically defined by calendar providers also permits deletion. If later copy is revised to promise "we never delete events" on the strength of this comment, the promise rests on application behavior the scope does not enforce. A future code path, bug or compromised token could delete events. | A test that enumerates every calendar API call site and asserts none issues a delete. Separately, confirm the provider's definition of the `calendar.write` scope. A narrower scope, if one exists, would enforce the boundary. |

**Evidence levels:**
- **Findings 1–4:** direct contradiction between the consent text and the deployed config as given.
- **Finding 5:** an unverified assertion; it depends on code and provider scope definitions I could not see.
- **All findings:** I could not verify that the config matches the runtime, for example whether analytics actually fires in production.

## FILES NEEDED BUT NOT PROVIDED

- Application source:
  - calendar write call sites, to verify there is no delete path;
  - the analytics emitter, to confirm the payload matches the config;
  - any other outbound integrations not listed in the config.
- The OAuth provider's definitions for `calendar.read`, `calendar.write` and `contacts.read`.
- Privacy policy and any data processing agreement with `metricsbay.example.test`.
- Localized or alternate versions of the consent screen, if any.
- PR identifier, head SHA and merge base, plus commit trailers to identify the author.
- The consent text currently live. The config says it was deployed on 2026-10-19 with analytics on. If the live consent text matches this one, the misrepresentation is already in production and is not just a pre-release issue. This is an owner or legal decision, flagged below.

---

# Close-out

**ADJUDICATION:** pending. Under this skill a reviewer never adjudicates its own findings. The author or owner must record Accepted, Deferred or Rejected for each finding. Findings 1–4 are P0 or P1 and cannot be deferred.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | — |
| 2 | pending | — |
| 3 | pending | — |
| 4 | pending | — |
| 5 | pending | — |

**VERIFIED AFTER FIXES:** none. No fixes have been made yet.

**MERGE RECOMMENDATION: do not merge.**
- **Blockers:** two P0s (1, 2) and two P1s (3, 4) are open.
- **Rounds:** this High-tier review needs a second independent round, which has not run.
- **Checks:** no SHAs and no CI checks were provided, so no check can be considered green.
- **Owner and legal decisions pending:**
  - whether attendee emails may go to the analytics vendor at all;
  - whether the live app already shows this text alongside the 2026-10-19 config, which would need remediation beyond this release.

**Fix direction for the author (not adjudication):**
- Rewrite the consent text to disclose:
  - calendar read **and write** (create and move events);
  - contacts read (to suggest attendees);
  - sharing of usage events with a named analytics provider.
- Remove the absolute "never share" claim.
- Remove `attendee_emails` from the analytics payload, or replace it with a count.
- Then verify the corrections with a targeted read of the correction diff and its tests, and run the second round.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "direct contradiction between consent text and deployed config",
      "location": "consent.md:4; app-config.yaml:7-10",
      "scenario": "Consent says 'We never share your data with anyone', but every meeting_suggested/meeting_booked event sends user_id, attendee_emails and meeting_time to third-party analytics vendor metricsbay.example.test; consent obtained on a false statement.",
      "fix": "Remove the absolute claim; disclose the analytics recipient and the data fields shared; add a test requiring every configured integration to be disclosed in the consent text."
    },
    {
      "severity": "P0",
      "evidence_level": "direct contradiction between consent text and deployed config",
      "location": "consent.md:3; app-config.yaml:3-4",
      "scenario": "Consent describes read-only calendar access, but the app requests calendar.write and creates/moves events; users grant write access they were not told about and find events created or rescheduled.",
      "fix": "State that the app creates and moves events on the user's behalf; add a scope-to-disclosure test."
    },
    {
      "severity": "P1",
      "evidence_level": "direct contradiction between consent text and deployed config",
      "location": "consent.md:3; app-config.yaml:5",
      "scenario": "The contacts.read scope is requested but never mentioned; users expose their address book without disclosure.",
      "fix": "Disclose contacts read access and its purpose (suggesting attendees); cover it in the scope-to-disclosure test."
    },
    {
      "severity": "P1",
      "evidence_level": "direct, from deployed config",
      "location": "app-config.yaml:10",
      "scenario": "Attendee email addresses of non-users, who never saw any consent screen, are sent to the analytics vendor; fixing the user-facing text cannot cover them; the field is not needed for event counting.",
      "fix": "Drop attendee_emails from the payload (use a count or aggregate); add a payload-schema test forbidding third-party identifiers; owner/legal decision on lawful basis."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified claim; code and provider scope definitions not provided",
      "location": "app-config.yaml:4",
      "scenario": "'No delete path' is only a comment; calendar.write typically permits deletion, so any future code path, bug or compromised token could delete events, and any consent wording relying on the comment would be unenforced.",
      "fix": "Verify the call sites with a test asserting no delete calls; use a narrower provider scope if available; do not promise 'never deletes' in consent text unless enforced."
    }
  ]
}
```