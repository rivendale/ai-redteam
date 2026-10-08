```
VERDICT: needs-decision (adds an account): I lean skip, because goal 3 is already served by Crowdin, which we use for translations, and LingoSync would duplicate it. It would also send our string tables to a new party, though not player data. The choice is the operator's.
WHAT IT IS: LingoSync (https://lingosync.example.test/), a hosted translation management platform for games, read from a
  saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json). Free tier, $0: one project, unlimited translators,
  no card required. It is free "for open-source and indie projects". The snapshot has no full terms, privacy policy or
  definition of "indie".
CLAIMS CHECKED:
  - Sender: "handles game translations". It offers upload of string tables, translator invites, in-context review and
    export to the engine. This is the product's own description and nothing shows it in use. PROBABLE. The verdict rests on it.
  - Sender: "for free". Its terms say the free tier is $0 for one project with no card required, and meta.json gives
    tier free, $0. It is limited to "open-source and indie projects", and the snapshot does not define "indie" or say
    who checks eligibility. PROBABLE, for one project if we count as indie. The verdict rests on it.
  - "Integrations for Unity". The snapshot only states it, with no plugin, version or Unity 6 detail. UNVERIFIED. Not
    load-bearing.
  - "Machine pre-translation included". The snapshot does not say whether the free tier includes it, or where the text
    is sent. UNVERIFIED. Not load-bearing.
FIT:
  - Goal: goal 3 (five languages by end of Q1).
  - Overlap: Crowdin is already in use for translations. It does the same job: string management, translators, review and
    export. Moving to LingoSync is a migration, not a new capability.
  - Burden: a new account, moving string tables and translators off Crowdin, and a new Unity integration to learn.
    Running both tools in parallel would add daily steps.
  - Cost: $0 on the free tier (read 2026-10-08), one project, eligibility "indie" undefined.
  - Risks: a new account, which needs operator approval. Game strings go to a new third party; this is not player data,
    but it is data leaving our hands. Machine pre-translation may send text to another processor, which the snapshot does
    not say. There is lock-in and a free-tier eligibility risk if we stop counting as "indie". Project health and
    data-handling terms are not in the snapshot. No license issue: it is a hosted tool and nothing of it ships in the game.
NEXT ACTION: The operator decides whether to open a LingoSync account. My recommendation is to decline unless Crowdin has
  a concrete gap blocking goal 3, such as cost, language limits or the Unity workflow; if it does, name that gap first and
  re-assess LingoSync against it. Owner: operator. Done when the operator records "decline" or names the Crowdin gap.
  Hand-off: none.
CONFIDENCE: medium. The verdict and the overlap with Crowdin are solid, and the context file is present. Confidence is
  limited because I worked from a short saved snapshot without full terms, privacy policy, the "indie" definition or
  Unity integration details, and because both claims behind the sender's question are only PROBABLE.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "account",
  "item": {"type": "product", "identity": "LingoSync (https://lingosync.example.test/), free tier $0, one project, unlimited translators; snapshot captured 2026-10-08", "resolved": true},
  "claims": [
    {"claim": "handles game translations (sender)", "evidence": "snapshot: upload string tables, invite translators, review in context, export back to engine; vendor description only", "status": "PROBABLE"},
    {"claim": "it is free (sender)", "evidence": "snapshot terms: free tier, one project, no card; meta.json $0; limited to open-source and indie projects, 'indie' undefined", "status": "PROBABLE"},
    {"claim": "integrates with Unity", "evidence": "snapshot states 'Integrations for Unity and Godot' with no detail on plugin or Unity 6 support", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "machine pre-translation included", "evidence": "snapshot states it; tier and data processor not given", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "ship the game in five languages by end of Q1 (goal 3)",
          "overlap": "Crowdin is already in use for translations and does the same job",
          "burden": "new account, migrating string tables and translators off Crowdin, new Unity integration",
          "risks": ["new account needs operator approval", "game strings sent to a new third party (not player data); machine pre-translation processor unknown", "free tier depends on undefined 'indie' eligibility", "lock-in; no terms, privacy policy or health info in snapshot"],
          "cost": {"price": "$0", "tier": "free", "limits": "one project, unlimited translators", "terms": "free for open-source and indie projects; no card required", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to open a LingoSync account; recommendation is to decline unless a concrete Crowdin gap blocks goal 3", "owner": "operator", "done_when": "operator records decline, or names the Crowdin gap to re-assess against", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```