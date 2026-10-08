```
VERDICT: watch. The article is members-only and its body was not captured, so there is nothing to copy yet; this changes only if we get the full text without a new paid account.
WHAT IT IS: UNRESOLVED. A post titled "HALVING OUR ANDROID BUILD TIME" at https://articles.example.test/members/halved-the-build, captured 2026-10-08. meta.json says "readable": false, "members-only: the body was not captured". The snapshot holds only the title, one teaser sentence and a membership prompt. Author, date, team and build stack are not shown.
CLAIMS CHECKED:
  - "the release build took half as long" (the item's teaser): no evidence is visible. There is no baseline time, no build system, no engine and no method. UNVERIFIED. Not load-bearing.
  - "a team halved their Android build time" (the sender's words): this restates the teaser, and nothing captured confirms or refutes it. UNVERIFIED. Not load-bearing.
  - Whether the changes apply to a Unity 6 / Jenkins on one Mac mini setup: unknown. The post does not say what they build with, and the techniques are behind the paywall.
  The verdict rests on the item being unreadable, not on any claim.
FIT:
  Goal: the topic matches goal 1, "Get the Android release build under 10 minutes". Whether the content serves that goal cannot be judged.
  Overlap: unknown. We cannot see whether its changes are things Jenkins/Unity already do.
  Burden: unknown.
  Cost: reading it needs a membership. The price and terms were not captured (as of 2026-10-08). Buying one, or creating an account, needs operator approval under our constraints ($0 tool budget; no new paid subscription or account).
  Risks: none assessable. A members-only post may also be generic Gradle/Android Studio advice that does not carry over to a Unity export, but that is a possibility, not a finding.
NEXT ACTION: The operator asks the sender for the full text, or checks whether someone already has a membership. They must not buy one without approval. Done when the full article text is saved to work/ and can be re-assessed, or when it is confirmed that no free copy exists, in which case it stays at watch and is dropped. Hand-off: none for now. If the text arrives and has techniques worth borrowing, it goes to harvest.
CONFIDENCE: low. The item is unresolved, its body was never read, and its author, stack and evidence are unknown. The context file is present.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "post",
           "identity": "UNRESOLVED: 'HALVING OUR ANDROID BUILD TIME', https://articles.example.test/members/halved-the-build (snapshot 2026-10-08; author and date not shown)",
           "resolved": false,
           "unresolved_reason": "members-only paywall: meta.json readable=false, body not captured; snapshot has only the title, one teaser sentence and a membership prompt"},
  "claims": [
    {"claim": "the release build took half as long", "evidence": "teaser sentence only; no baseline, stack or method visible",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "a team halved their Android build time (sender's words)", "evidence": "restates the teaser; nothing captured settles it",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "topic matches goal 1 (Android release build under 10 minutes); actual fit unknown",
          "overlap": "unknown: techniques not readable, so cannot compare with our Unity 6 + Jenkins setup",
          "burden": "unknown",
          "risks": ["reading requires a membership: new account and likely money, needs operator approval",
                    "advice may target native Gradle projects and not carry over to a Unity export (unverified)"],
          "cost": {"price": "unknown (membership price not captured)", "tier": "members-only",
                   "limits": "body hidden to non-members", "terms": "not captured",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Ask the sender for the full article text, or find an existing membership; do not buy one without approval",
                  "owner": "operator",
                  "done_when": "full text saved to work/ for re-assessment, or confirmed that no free copy exists",
                  "handoff": "none"},
  "confidence": "low",
  "context_file": "present"
}
```