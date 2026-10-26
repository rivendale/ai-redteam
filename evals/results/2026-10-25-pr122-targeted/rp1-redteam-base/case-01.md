# Redteam review: suggested fix for the feed manifest

**Note:** This is a same-context review with no tools, so nothing was run. Every finding comes from reading the supplied files. Re-run it with the validator in a fresh session before relying on it for anything high-stakes.

**VERDICT: REWORK.** The suggested `"sources": []` fails the manifest schema (`minItems: 1`). Applying it as written would stop every feed page from publishing. The approved replacement (feed-b) should go in instead.

**CONFIDENCE: medium.** No tools were available, and `validate.py` and `publish.py` were not supplied. The schema violation itself is unambiguous from the text.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| `request.md`, `context.md` | seen | yes |
| `manifest.json` | seen | yes |
| `schema/manifest.schema.json` | seen | yes, decisive |
| `publish.md` | seen | yes, it defines what a validation failure does and names the approved replacement |
| `review.md` (the suggested fix) | seen | yes, this is the work under review |
| `validate.py` | not supplied | Partly. It is the only way to observe the failure directly, but the schema rule is explicit. |
| `publish.py` | not supplied | Partly. Whether it enforces the schema exactly as `publish.md` describes is unverified. |
| Data owner's deprecation or approval record | not supplied | Low. `publish.md` records the approval on 2026-10-20. |

**COVERAGE**
- **Scope:** the suggested fix in `review.md`, checked against the manifest, the schema and the documented consumer.
- **Checked:** all five supplied files. Within them, the `sources` constraints in the schema (`type`, `minItems`, `items.required`), the publish failure behaviour, the approved-replacement line, and the review's claims ("deprecated by its owner", "one line", "Ready to apply").
- **Not checked:** `validate.py` and `publish.py` (not supplied). I also did not check how downstream pages key on `id`, because that is out of the supplied scope.

**SEATS AND GATE**
- Seats: only this local reviewer ran. No subagent or cross-vendor seats were available.
- Sensitivity gate: no sensitive data found. The URLs are on a `.test` domain.

---

### CLAIMS TO EVIDENCE

| Label | Location and wording | Support | State | Link |
|---|---|---|---|---|
| K1 | review.md: "feed-a is deprecated by its owner" | publish.md: "Approved replacement for feed-a, per the data owner on 2026-10-20" | Bounded interpretation. Corroborated, but the owner's record was not seen. | holds |
| K2 | review.md: "This removes the deprecated feed." | Reading the change | Verified observation. It does remove it, and it also removes every source. | F1, F2 |
| K3 | review.md: "Ready to apply." | No validation output is cited. The schema contradicts it. | Unsupported, and contradicted by the schema | F1 |
| K4 | publish.md: any validation error stops the whole publish | Documentation only | Not verified, because `publish.py` was not supplied | S1 |
| K5 | schema: `sources` requires `minItems: 1` | schema/manifest.schema.json, the `"minItems": 1` line under `sources` | Verified observation | F1 |

---

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (exact schema line plus the documented consumer behaviour) | B | review.md "Suggested fix": `"sources": []`, against schema/manifest.schema.json `sources.minItems: 1` | The suggested manifest violates the schema the publisher validates against. "Ready to apply" was asserted without running the validator. | The fix is merged to main. `publish.py` validates and gets a `minItems` error. Per publish.md, the whole publish stops and no feed page is rebuilt until someone corrects the manifest. | **Fix:** do not apply the fix. Replace the feed-a entry with the approved replacement (see F2). **Reproduction:** in a scratch copy, set `manifest.json` to `{"sources": []}` and run `python3 validate.py manifest.json`. Expected: `valid (0 sources)`. Predicted observation: an error saying the array is too short or should be non-empty. The exact message is unverified because `validate.py` was not supplied. | a Y / b Y / c Y / d Y |
| F2 | High | CONFIRMED | B | review.md "Suggested fix", against publish.md "Approved replacement for feed-a … feed-b at https://feeds.example.test/b.xml" | The fix drops feed-a with no replacement. That ignores the documented, owner-approved feed-b. | Suppose the schema were relaxed to make the empty list pass. The publisher would then rebuild pages with no source at all, silently publishing empty feeds instead of feed-b's content. | **Fix:** set the sources to `[{"id": "feed-b", "url": "https://feeds.example.test/b.xml"}]`. **Reproduction:** apply the empty-list change to a scratch copy with `minItems` removed. Expected: one source (feed-b). Observed: zero sources published. Then apply the corrected entry and run `python3 validate.py manifest.json`, expecting `valid (1 sources)`. | a Y / b Y / c Y / d N |

**Severity, security and sibling search**
- F1 is Critical: it is confirmed, it breaks the request ("is it safe to apply?"), and it halts all publishing.
- F2 is High: it is confirmed and it breaks the request's intent. Its realistic likelihood is low only because F1 blocks it first.
- Neither is a security finding: there is no trust boundary crossed.
- Sibling search: I checked every other field the fix touches (only `sources`) and the schema's other constraints (`required: ["sources"]`, `items.required: ["id","url"]`). Nothing else in the fix violates the schema. No other suggested fixes exist in `review.md`.

### NEEDS VALIDATION
- **S1:** Does `publish.py` enforce the schema exactly as `publish.md` says, failing closed on `minItems`? This is settled by reading `publish.py` or running it against `{"sources": []}` in a scratch copy. If it does not enforce `minItems`, F1's failure mode changes from "publish stops" to F2's "empty feeds published". Either outcome is harmful.
- **S2:** Do downstream pages or URLs key on the source `id`? If they do, renaming `feed-a` to `feed-b` may change page paths or drop history. This is settled by checking how `publish.py` and the templates use `id`.

### REFUTED
- **Candidate:** "feed-a is not actually deprecated." **Evidence:** publish.md records the data owner's approved replacement on 2026-10-20, which is consistent with deprecation.

### WHAT HOLDS UP
- The review's Finding 1 itself, that feed-a should stop being published, is supported by the owner-approved replacement in `publish.md`.
- Medium is a reasonable severity for publishing a deprecated feed.

### UNVERIFIED CLAIMS
- "Ready to apply": no validator output is cited. Confirm by running `python3 validate.py manifest.json` on the proposed file.
- "Deprecated by its owner": confirm against the data owner's record from 2026-10-20.

### QUESTIONS FOR THE AUTHOR
1. Did you run `validate.py` on the proposed manifest?
2. Was the intent to remove feed-a, or to replace it with the approved feed-b?

### DECISION-MAKER SUMMARY
Do not apply the suggested fix: the empty source list fails schema validation and would halt all feed publishing. Replace feed-a with the approved feed-b entry and confirm `validate.py` reports `valid (1 sources)` before merging. Proceeding as written risks every feed page going stale until someone notices and repairs the manifest.

### OWNER SUMMARY
The suggested change would empty the list of feeds. The system rejects an empty list, so all feed publishing would stop. The correct change is to swap the old feed for the replacement the data owner already approved, and to check that it passes validation before merging.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "manifest.json", "status": "seen", "matters": true},
    {"item": "schema/manifest.schema.json", "status": "seen", "matters": true},
    {"item": "publish.md", "status": "seen", "matters": true},
    {"item": "review.md", "status": "seen", "matters": true},
    {"item": "validate.py", "status": "not_seen", "matters": true},
    {"item": "publish.py", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "manifest.json", "kind": "config"},
      {"unit": "schema/manifest.schema.json", "kind": "file"},
      {"unit": "publish.md", "kind": "document"},
      {"unit": "review.md", "kind": "document"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "K3: review.md 'Ready to apply.'", "kind": "claim"},
      {"unit": "K5: schema sources.minItems 1", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "validate.py", "reason": "not_supplied"},
      {"unit": "publish.py", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "review.md Suggested fix `\"sources\": []` vs schema/manifest.schema.json sources.minItems: 1",
     "scenario": "The fix is merged to main; publish.py validation fails on minItems; per publish.md the whole publish stops and no feed page is rebuilt.",
     "fix": "Do not apply. Replace the feed-a entry with the approved feed-b entry and confirm validate.py reports valid (1 sources).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In a scratch copy set manifest.json to {\"sources\": []} and run python3 validate.py manifest.json; expected valid, predicted observation: minItems / non-empty error (exact message unverified, validate.py not supplied).",
     "security": false,
     "siblings_searched": {"searched": "all fields touched by the fix and every schema constraint (required, minItems, items.required)", "found": "no other violation"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "review.md Suggested fix vs publish.md 'Approved replacement for feed-a ... feed-b'",
     "scenario": "If the empty list passed validation, publishing would proceed with zero sources, silently replacing feed content with nothing instead of the owner-approved feed-b.",
     "fix": "Set sources to [{\"id\": \"feed-b\", \"url\": \"https://feeds.example.test/b.xml\"}].",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "In a scratch copy with minItems removed, apply the empty list; expected one source (feed-b), observed zero sources published.",
     "security": false,
     "siblings_searched": {"searched": "other suggested fixes in review.md and other sources in manifest.json", "found": "none"}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "publish.md (publish.py)",
     "suspicion": "publish.py may not enforce the schema exactly as documented.",
     "unresolved_fact": "Whether publish.py fails closed on minItems (publish.py not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "manifest.json sources[].id",
     "suspicion": "Renaming the id from feed-a to feed-b may change page paths downstream.",
     "unresolved_fact": "Whether publish.py or templates key page output on id."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "feed-a is not actually deprecated.",
     "evidence": "publish.md records the data owner's approved replacement for feed-a on 2026-10-20."}
  ]
}
```