VERDICT: **REWORK.** The headline claim, "Lumen is zero-retention", is contradicted by the source it cites. Lumen retains inputs for 30 days, and zero retention requires an enterprise agreement this account does not have.

CONFIDENCE: **high** for the findings, because each one rests on a verbatim quote from the supplied sources. Three things limit it:
- I had no tools, so I could not confirm that the `sources/` files match Lumen's live pages.
- No fresh subagent ran, so this is a single-reviewer pass. I did not author the work.
- The SOC 2 report itself was not supplied.

INPUTS LEDGER:
- **Seen:** request.md, context.md, assessment.md, sources/lumen-privacy.md and sources/lumen-security.md (both retrieved 5 Oct 2026).
- **Not seen: Lumen's live pages.** This matters a little. The copies are 3 days old as of 8 Oct 2026, so drift is unlikely.
- **Not seen: the SOC 2 Type II report.** This matters for the "safe" conclusion, because its scope is unknown.
- **Not seen: the client contracts' confidentiality and processing terms.** These matter: whether any third-party retention is allowed is the real deciding question.
- **Not seen: the plan contract and DPA.** These matter because they would confirm the plan's retention terms.

COVERAGE:
- **Scope:** the whole work, under Track C (do the cited sources say what is claimed). I also lightly checked whether the conclusion answers the request.
- **Checked:** every claim in assessment.md (Summary claim and conclusion, three supporting facts, the plan statement), both source files, request.md and context.md.
- **Not checked:** live vendor pages (`no_tools`), the SOC 2 report (`not_supplied`), client contract terms (`not_supplied`).

SEATS AND GATE: Only a local same-session reviewer ran. No cross-vendor seats were requested. The sensitivity gate passed: the work describes a vendor and contains no client documents.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | assessment.md, Summary: "**Lumen is zero-retention, so it is safe to use with client documents** [1]" | Source [1] says the opposite: "Inputs and outputs sent to the Lumen API are retained for 30 days for abuse monitoring… Zero data retention (ZDR) is available only to accounts on an enterprise agreement that includes the signed ZDR addendum." The assessment itself says: "Our account is on the standard plan; we have no enterprise agreement." So on this account Lumen is **not** zero-retention, and the "safe" conclusion falls with that premise. | The contracts team relies on the summary and sends client contracts on the standard plan. Lumen keeps every contract and extraction output for 30 days. The client documents may then be held by a third party in breach of client confidentiality terms, and per context.md this cannot be reversed once sent. | Rewrite the summary to say: "On our standard plan Lumen retains inputs and outputs for 30 days. Zero retention requires an enterprise agreement with the signed ZDR addendum [1]." Then answer the request conditionally: "not on the current plan; possible only after an enterprise + ZDR addendum is signed, subject to client terms." | a✔ b✔ c✔ d✔ |
| F2 | Low | CONFIRMED | C | assessment.md, Supporting facts: "up to 200,000 tokens, enough for a 150-page contract [2]" | Source [2] states only the 200,000-token limit. The "150-page contract" fit is the author's own inference, but it carries the citation as if the source said it. | A reader believes Lumen guarantees that a 150-page contract fits. The estimate is plausible (150 pages × ~500–700 words ≈ 100k–140k tokens), but long or dense contracts with schedules could exceed the limit and be truncated or rejected. | Cite [2] only for the 200,000-token figure. Label the page estimate as an internal assumption, or test it with a real contract. | a✔ b✔ c✘ d✘ |

F1 confirm-or-refute: I argued it from the defender's side. Could "zero-retention" refer to some other plan? The source limits ZDR to enterprise accounts with the addendum, and the work states the account has neither. **Confirmed and held.**

F1 security: **yes.** The boundary is crossed as follows:
- **Principal:** a contracts-team member following the assessment.
- **Input:** client-confidential contracts sent to the Lumen API.
- **Control that fails:** the assumed zero retention does not exist on the standard plan.
- **Boundary crossed:** client-confidential data moves from the organization to the vendor and is retained there.
- **Resource affected:** client contracts, held for 30 days.

F1 siblings: I checked every other cited claim against its source for the same root cause (a claim its cited source does not support).
- "Not used to train… [1]" is supported: "not used to train Lumen models on any plan."
- "SOC 2 Type II report [2]" is supported as stated.
- The 200k context limit is supported. The 150-page part is unsupported, which is F2.
- No further siblings.

NEEDS VALIDATION:
- **S1 (SOC 2 scope).** The work offers SOC 2 Type II as support for safety, but only the vendor's statement was seen. To settle it: obtain the report (period ending 30 Jun 2026) and confirm the API and its data-retention controls are in scope.
- **S2 (acceptability of 30-day retention).** Even with F1 corrected, whether 30-day abuse-monitoring retention is acceptable depends on the clients' contracts. To settle it: check whether client confidentiality or processing terms permit third-party processing and retention by a subprocessor.
- **S3 (access during retention).** The sources do not say who can access retained data or whether humans review it. To settle it: get Lumen's abuse-monitoring access policy, or the DPA.

REFUTED:
- **"Training claim misattributed."** The source says "not used to train Lumen models on any plan", which matches the claim.

WHAT HOLDS UP:
- The no-training claim, the SOC 2 Type II claim and the 200,000-token limit each match their cited source.
- Both sources are recent (retrieved 5 Oct 2026), so freshness is fine.
- The work does disclose the plan fact; it just never applies it.

UNVERIFIED CLAIMS:
- That the source files match Lumen's current live pages. To confirm: open the live pages and compare.
- The SOC 2 report's existence and scope. To confirm: request the report.
- That "a 150-page contract" fits the limit. To confirm: tokenize a representative contract.

QUESTIONS FOR THE AUTHOR:
1. Is an enterprise agreement with the ZDR addendum planned or obtainable, and on what timeline?
2. Do the clients' contracts permit a vendor to retain their documents for 30 days?

DECISION-MAKER SUMMARY: The assessment's core claim is false for our account: on the standard plan Lumen keeps everything sent to it for 30 days, and zero retention requires an enterprise agreement with a signed addendum. Do not send client contracts until that agreement is in place or the clients' terms are confirmed to allow 30-day vendor retention. Proceeding anyway places client-confidential documents with a third party in a way that cannot be undone.

OWNER SUMMARY: The review found that the vendor keeps copies of everything sent to it for 30 days on our current plan, even though the assessment said it keeps nothing. Keeping nothing is only offered under a larger, signed agreement we do not have. Client contracts should not be sent to this service until that agreement is signed or we confirm our clients allow it.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "assessment.md", "status": "seen", "matters": true},
    {"item": "sources/lumen-privacy.md", "status": "seen", "matters": true},
    {"item": "sources/lumen-security.md", "status": "seen", "matters": true},
    {"item": "Lumen live vendor pages", "status": "not_seen", "matters": false},
    {"item": "Lumen SOC 2 Type II report", "status": "not_seen", "matters": true},
    {"item": "Client contract confidentiality/processing terms", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-session-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work describes a vendor; no client documents or personal data included."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "assessment.md", "kind": "file"},
      {"unit": "sources/lumen-privacy.md", "kind": "file"},
      {"unit": "sources/lumen-security.md", "kind": "file"},
      {"unit": "assessment.md:Summary zero-retention claim", "kind": "claim"},
      {"unit": "assessment.md:Summary safe-for-client-documents conclusion", "kind": "claim"},
      {"unit": "assessment.md:SOC 2 Type II claim", "kind": "claim"},
      {"unit": "assessment.md:no-training claim", "kind": "claim"},
      {"unit": "assessment.md:200k context / 150-page claim", "kind": "claim"},
      {"unit": "assessment.md:standard plan, no enterprise agreement", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Lumen live vendor pages", "reason": "no_tools"},
      {"unit": "Lumen SOC 2 Type II report", "reason": "not_supplied"},
      {"unit": "Client contract terms", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "assessment.md, Summary: 'Lumen is zero-retention, so it is safe to use with client documents [1]'",
     "scenario": "Source [1] says inputs and outputs are retained 30 days and ZDR is only for enterprise accounts with a signed ZDR addendum; the account is on the standard plan with no enterprise agreement. Relying on the summary, the team sends client contracts, which Lumen retains for 30 days, irreversibly exposing client-confidential documents.",
     "fix": "State that the standard plan retains inputs/outputs for 30 days and ZDR requires an enterprise agreement with the signed addendum; answer the request as 'not on the current plan; only after enterprise + ZDR addendum, subject to client terms'.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": true,
     "boundary": {"principal": "contracts-team member following the assessment",
                  "input": "client-confidential contracts sent to the Lumen API",
                  "control": "assumed zero retention, which does not apply to the standard plan",
                  "crossed": "organization to external vendor retention",
                  "resource": "client contracts and extraction outputs, retained 30 days"},
     "siblings_searched": {"searched": "every cited claim in assessment.md against its cited source passage",
                           "found": "no other contradicted claim; one unsupported inference (F2)"}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "assessment.md, Supporting facts: 'enough for a 150-page contract [2]'",
     "scenario": "Source [2] states only the 200,000-token limit; the 150-page fit is the author's inference presented under the citation. Dense or long contracts with schedules could exceed the limit.",
     "fix": "Cite [2] only for the 200,000-token figure; label the page estimate as an internal assumption or measure a representative contract.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "assessment.md, Supporting facts: SOC 2 Type II [2]",
     "suspicion": "SOC 2 Type II is offered as support for safety but its scope is unknown.",
     "unresolved_fact": "Whether the report (period ending 30 June 2026) covers the API and its retention controls."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "assessment.md, Summary",
     "suspicion": "Even with the correction, 30-day vendor retention may be impermissible for client documents.",
     "unresolved_fact": "Whether client confidentiality/processing terms allow third-party processing and 30-day retention."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "sources/lumen-privacy.md, Retention",
     "suspicion": "Retained data may be accessible to humans during abuse monitoring.",
     "unresolved_fact": "Lumen's access policy for retained data (DPA or abuse-monitoring documentation)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The no-training claim is misattributed to source [1].",
     "evidence": "sources/lumen-privacy.md: 'Inputs and outputs are not used to train Lumen models on any plan.'"}
  ]
}
```