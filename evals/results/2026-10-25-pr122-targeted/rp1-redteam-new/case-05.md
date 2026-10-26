VERDICT: **REWORK.** Two of the four statements tell operations leads to do the wrong thing: a regulator quotation that does not exist with the wrong deadline, and a console setting that the vendor rejects. The other two cite the wrong paragraph or rule.

CONFIDENCE: **medium.** No tools were available, so I checked against the source copies supplied inline and did not open the live URLs or scan the raw bytes. The synthesis was not written in this conversation, so the review is independent of its author, but no second reviewer ran.

INPUTS LEDGER
- Seen: request.md, context.md, synthesis.md, sources/northline-rulebook.md, sources/eastport-gn3.md, sources/vaultline-retention.md (all inline).
- Not seen: the live source URLs. This gap matters only if the 2026-10-20 copies have since changed. The context says the local copies are the cited sources.
- Not seen: whether the organization is a Northline "Member" or an Eastport "processor of account data". This matters for whether either obligation applies. See Needs Validation.

COVERAGE
- Scope: the whole synthesis, items 1–4 and the title, checked against all three sources.
- Checked: every claim (C1–C4), every citation, the one quotation, the one config value, and every paragraph in each source.
- Not checked:
  - Live URLs (no tools).
  - Hidden or zero-width characters (no byte-level access, so marked `no_tools`).

SEATS AND GATE: Only one reviewer ran, this session, with no tools and no subagent. No cross-vendor seats were used. The sensitivity gate found no personal, credential or confidential data. No text in the work addresses the reviewer.

CLAIMS TO EVIDENCE

| Claim | Location | Wording | Source check | State | Link |
|---|---|---|---|---|---|
| C1 | synthesis.md item 1 | "Rule 12 … requires 72 hours' notice before a planned outage" | Rule 12 says "Reserved." The 72-hour requirement is **Rule 14**. | The obligation is right; the citation is wrong. | F3 |
| C2 | item 2 | quote: "account data must be erased promptly, and in any case within 30 days" | The quote is absent from GN-3. §3.4 says: "Account data is deleted within 45 days of account closure." | Fabricated quote with the wrong number (30 vs 45). | F1, F5 |
| C3 | item 3 | "the deletion requirement is paragraph 3.2 of GN-3" | §3.2 is "Backups. Backups are encrypted at rest." Deletion is **§3.4**. | Wrong paragraph. | F4 |
| C4a | item 4 | "set `retention_mode = strict`" | The Vaultline source says the setting "accepts three values: `off`, `standard` (30 days) and `extended` (365 days). There is no other value; an unknown value is rejected when the setting is saved." | Invalid value. | F2 |
| C4b | item 4 | "to meet both rules" | One rule is outage notice (Rule 14), which no storage setting can satisfy. | Unsupported interpretation. | F6 |

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | synthesis.md item 2 | The text in quotation marks does not appear in GN-3. The real text (§3.4) gives **45 days**, not 30, and contains no "must" or "promptly". | Leads adopt a 30-day deadline and attribute an invented sentence to the regulator. That quote then ends up in policies or audit answers and fails on comparison with GN-3. | Replace with the verbatim §3.4 text: "Account data is deleted within 45 days of account closure." If the organization wants 30 days, label it as its own choice. | a✓ b✓ c✗ d✓ |
| F2 | High | CONFIRMED | C | synthesis.md item 4 | `strict` is not a valid `retention_mode`. The source lists only `off`, `standard` and `extended`, and rejects unknown values. | Leads follow the instruction, the console rejects it, and they are left with no supported configuration for the deletion obligation. | Remove `strict`. Name a valid value only after confirming it achieves deletion within 45 days (see N3). | a✓ b✓ c✗ d✓ |
| F3 | Medium | CONFIRMED | C | item 1 | The rule cited is Rule 12 ("Reserved"). The 72-hour notice is in Rule 14. | An outage procedure or audit answer cites Rule 12, and a reader who checks it finds an empty rule. | Change the citation to "Rule 14". | a✓ b✓ c✗ d✗ |
| F4 | Medium | CONFIRMED | C | item 3 | Deletion is cited as §3.2, which is the backups paragraph. It is actually §3.4. | Same as F3: anyone who checks the citation finds backup encryption, not deletion. | Change the citation to "paragraph 3.4". | a✓ b✓ c✗ d✗ |
| F5 | Medium | CONFIRMED | C | items 2–4 ("guidance says … must", "requirement", "rules") | GN-3 is a guidance note and §3.4 is descriptive ("is deleted"). The synthesis presents it as a binding requirement. | Leads treat guidance as law, or report it to others as law. | Label GN-3 as guidance. Quote its actual wording and state its status separately from the Northline rules. | a✓ b✓ c✗ d✗ |
| F6 | Medium | CONFIRMED | C | item 4 ("meet both rules") | A storage retention setting cannot satisfy a 72-hour outage-notice rule. | Leads assume one console change covers outage notice, and no notice process gets built. | Drop "both". Pair each obligation with its own control. | a✓ b✓ c✗ d✗ |

Severity notes:
- For F1 and F2 I answered (c) "no". A 30-day deadline is stricter than 45 days, and the console rejects the invalid value instead of failing silently. Neither error causes a breach on its own.
- Siblings for F1: I checked the other items for quotations. Item 2 holds the only quotation.
- Siblings for F2: I checked the other items for config values. Item 4 holds the only config value.
- Neither F1 nor F2 is a security finding.
- F3 and F4 come from the same root cause, wrong locators. I checked every citation and found these two; the other two items' locators are correct.

NEEDS VALIDATION (no severity)
- N1: Does Northline Rule 14 apply to this organization? Settled by whether the organization is a Northline Member.
- N2: Does GN-3 apply? Settled by whether the organization is a "processor of account data" under §3.1.
- N3: Can any `retention_mode` value (for example `standard`, 30 days) produce deletion within 45 days of account closure? Settled by whether the retention window is counted from closure and whether it applies to account data. The Vaultline source does not say.
- N4: The synthesis does not mention Rule 11 (incident summary within 10 business days). Settled by whether the synthesis's scope was meant to include incidents. Its title suggests not.

REFUTED
- "The 72-hour figure is wrong": refuted. Rule 14 states it exactly. Only the rule number is wrong (F3).

WHAT HOLDS UP: The 72-hour planned-outage notice obligation and its applicability to customer-facing services are correct. Every cited source file exists and is about the topic it is cited for.

UNVERIFIED CLAIMS: That the local copies match the live sources as of today. Confirm by opening the three URLs and comparing them with the 2026-10-20 copies.

QUESTIONS FOR THE AUTHOR
1. Where did the "30 days … promptly" quote come from?
2. Is `strict` from a different product or version than the cited Vaultline page?
3. Is the organization a Northline Member and an Eastport processor?

DECISION-MAKER SUMMARY: Do not send this to operations leads yet. It misquotes the regulator's deletion deadline (30 days instead of 45), recommends a console setting that does not exist, and miscites two rules. If it goes out as is, leads will configure against an invented requirement and cite rules that say something else.

OWNER SUMMARY: The research summary gets several important details wrong when checked against its own sources. It quotes a regulator saying something the regulator did not say, tells staff to use a setting that the software refuses, and points to the wrong sections of two rule books. It needs correcting before anyone acts on it.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "synthesis.md", "status": "seen", "matters": true},
    {"item": "sources/northline-rulebook.md", "status": "seen", "matters": true},
    {"item": "sources/eastport-gn3.md", "status": "seen", "matters": true},
    {"item": "sources/vaultline-retention.md", "status": "seen", "matters": true},
    {"item": "live source URLs", "status": "not_seen", "matters": false},
    {"item": "organization's Northline membership / Eastport processor status", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "synthesis.md", "kind": "document"},
      {"unit": "sources/northline-rulebook.md", "kind": "document"},
      {"unit": "sources/eastport-gn3.md", "kind": "document"},
      {"unit": "sources/vaultline-retention.md", "kind": "document"},
      {"unit": "C1 synthesis.md item 1", "kind": "claim"},
      {"unit": "C2 synthesis.md item 2", "kind": "claim"},
      {"unit": "C3 synthesis.md item 3", "kind": "claim"},
      {"unit": "C4 synthesis.md item 4", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live source URLs", "reason": "no_tools"},
      {"unit": "hidden/zero-width character scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 2",
     "scenario": "The synthesis quotes GN-3 as 'account data must be erased promptly, and in any case within 30 days'; the text does not exist and GN-3 3.4 says 45 days. Leads adopt and cite an invented regulator sentence and deadline.",
     "fix": "Quote GN-3 3.4 verbatim: 'Account data is deleted within 45 days of account closure.' Label any 30-day target as internal practice.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "all quotations in synthesis.md", "found": "item 2 is the only quotation"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4",
     "scenario": "Leads set retention_mode = strict; Vaultline accepts only off/standard/extended and rejects unknown values on save, leaving no valid configuration.",
     "fix": "Remove 'strict'; specify a valid value only after confirming it yields deletion within 45 days of closure.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "all configuration values in synthesis.md", "found": "item 4 is the only one"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "Procedures cite Northline Rule 12, which reads 'Reserved'; the 72-hour notice is Rule 14.",
     "fix": "Change citation to Rule 14.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 3",
     "scenario": "Deletion is cited as GN-3 3.2, which covers backup encryption; deletion is 3.4.",
     "fix": "Change citation to paragraph 3.4.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md items 2-4",
     "scenario": "GN-3 is a guidance note phrased descriptively; the synthesis presents it as a binding 'must'/'requirement'/'rule', and leads misstate its legal status.",
     "fix": "State GN-3's status as guidance and quote its actual wording.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4",
     "scenario": "'Meet both rules' implies a storage retention setting satisfies the 72-hour outage-notice rule; leads skip building a notice process.",
     "fix": "Drop 'both'; map each obligation to its own control.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "N1", "status": "needs_validation", "track": "C", "location": "synthesis.md item 1",
     "suspicion": "Northline Rule 14 may not apply to the organization.",
     "unresolved_fact": "Whether the organization is a Northline Member."},
    {"id": "N2", "status": "needs_validation", "track": "C", "location": "synthesis.md items 2-3",
     "suspicion": "GN-3 may not apply to the organization.",
     "unresolved_fact": "Whether the organization is a processor of account data under GN-3 3.1."},
    {"id": "N3", "status": "needs_validation", "track": "C", "location": "synthesis.md item 4",
     "suspicion": "No retention_mode value may implement deletion within 45 days of account closure.",
     "unresolved_fact": "Whether Vaultline retention windows apply to account data and run from account closure."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The 72-hour outage notice figure is wrong.",
     "evidence": "Northline Rule 14: 'Members give 72 hours' notice before a planned outage of a customer-facing service.'"}
  ]
}
```