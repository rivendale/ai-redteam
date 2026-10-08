VERDICT: skip. ShaderLint is free and needs no account, but it serves none of our four goals (build time, crash noise, localization, devlog), and the page never says it checks HLSL or works with Unity.

WHAT IT IS: ShaderLint, a product. This is the pricing and terms page, read from a saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. It has a free tier at $0 with no account, no card and no usage limits. It ships as a command-line binary plus an editor window. The license is "freeware, commercial use allowed" (proprietary, not open source). Optional paid support costs $200/year. The page gives no version, supported platforms or project-health details.

CLAIMS CHECKED:
- **"Free for commercial use"** (from the sender and the page). The page's own terms say "free for commercial and personal use … freeware, commercial use allowed." **CONFIRMED**. Not load-bearing.
- **"No account, no card, no usage limits"**. Stated in the terms text. **CONFIRMED** as the terms read on 2026-10-08. Not load-bearing.
- **"Checks HLSL in Unity projects"** (sender's words). The snapshot never mentions HLSL, Unity or what the tool actually checks. **UNVERIFIED**. Not load-bearing: even if true, it serves no goal.
- **"Runs on your machine and sends nothing anywhere"**. This is the vendor's statement about a closed binary, with no source or network detail to check it against. **UNVERIFIED**. Not load-bearing.
- **"Paid support is optional and not needed to use the tool"**. Stated in the terms. **CONFIRMED**. Not load-bearing.

FIT:
- **Goal:** none found. Shader linting does not shorten the Android build (goal 1). It does not reduce crash noise (goal 2), since nothing ties our top crashes to shaders. It does not help localization (goal 3) or the devlog (goal 4).
- **Overlap:** nothing in use lints shaders. Unity 6 already reports shader compile errors at build time.
- **Burden:** a new binary to install and update on the Jenkins Mac mini and on Windows dev machines. Platform support is not stated.
- **Cost:** $0, no limits, read 2026-10-08. Support at $200/year is optional and outside the $0 budget.
- **Risks:**
  - *License:* proprietary freeware. We would run it, not ship it, but our tool rule only names GPL/AGPL beyond the permissive set, so a closed freeware tool is not clearly covered.
  - *Privacy:* the "sends nothing" claim cannot be checked for a closed binary.
  - *Health:* no version or update history on the page.

NEXT ACTION: No adoption. The operator records the skip. If a shader error ever reaches the Crashlytics top five, or shader problems slow the Android build, re-run assess on ShaderLint's feature page. Done when the skip is noted. Hand-off: none.

CONFIDENCE: high. The item is resolved from a dated snapshot, the context file is present, and the verdict rests on fit, not on any unverified claim. Two limits: the snapshot is a saved copy rather than a live read, and the page does not describe what the tool checks or which platforms it supports.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "product",
           "identity": "ShaderLint pricing and terms page, free tier $0, freeware license (commercial use allowed), optional support $200/year; saved snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "free for commercial use", "evidence": "terms text: 'free for commercial and personal use ... freeware, commercial use allowed'",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "no account, no card, no usage limits", "evidence": "terms text on the pricing page, read 2026-10-08",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "checks HLSL in Unity projects", "evidence": "sender's words only; the page never mentions HLSL, Unity or what is checked",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "runs on your machine and sends nothing anywhere", "evidence": "vendor statement about a closed binary; nothing to check it against",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "paid support is optional and not needed to use the tool", "evidence": "terms text: 'Optional paid support ($200/year) is separate and not needed'",
     "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (goals 1-4 are build time, crash noise, localization, devlog)",
          "overlap": "no shader linter in use; Unity 6 already reports shader compile errors at build",
          "burden": "a new binary to install and update on the Jenkins Mac mini and Windows machines; platform support not stated",
          "risks": ["proprietary freeware: a tool we run, but the license rule names only GPL/AGPL beyond permissive licenses",
                    "'sends nothing' is unverifiable for a closed binary",
                    "no version or update history on the page"],
          "cost": {"price": "$0 (optional support $200/year)", "tier": "free", "limits": "none stated",
                   "terms": "freeware, commercial use allowed", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Record the skip; re-assess only if a shader error reaches the Crashlytics top five or shader problems slow the Android build",
                  "owner": "operator", "done_when": "the skip and its re-assess trigger are noted",
                  "stop_condition": "none (not a trial)", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```