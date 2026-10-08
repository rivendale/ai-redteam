VERDICT: watch. The link returned HTTP 404 when it was captured on 2026-10-08, so there is nothing to judge, and "adopt" cannot be answered until we have a working link.

WHAT IT IS: UNRESOLVED. `https://github.com/example-org/framescope` returned HTTP 404 at capture on 2026-10-08 (`meta.json`: `"readable": false`). The snapshot is GitHub's standard 404 page, which says the repository "may have been renamed, made private or deleted." No license, stars, last push, archived flag, default branch or code was read. I am not judging it from its name or URL.

CLAIMS CHECKED:
- "It is a Unity profiler addon" (sender's words). No evidence, because nothing was captured. UNVERIFIED.
- "Looks good" (sender's words). No evidence, because nothing was captured. UNVERIFIED.
- Neither claim carries the verdict. The verdict rests only on the fact that the item could not be read.

FIT:
- **Goal:** none found. I cannot match an unread item to a goal. Even taking the sender's description at face value, a runtime profiler maps to none of the four goals: build time, crash noise, localization and the devlog.
- **Overlap:** Unity 6 is already in use and has its own built-in Profiler. Any addon would need to show it does something that one does not.
- **Burden:** unknown.
- **Cost:** unknown. No price or terms were read. The quarter's tool budget is $0 unless approved.
- **Risks:** license unknown. Code we ship must be MIT, Apache-2.0, BSD or zlib. A profiler that stays editor-only could be GPL. Project health is unknown. A repository that has vanished is itself a health warning if it was deleted rather than renamed.

NEXT ACTION: The operator asks the sender for the repository's current URL, or its new owner or name if it was renamed, then runs `assess` again on that link.
- **Owner:** operator.
- **Done when:** a link that resolves is in hand and has been assessed, or the sender confirms the repository is gone.
- **Hand-off:** none.

CONFIDENCE: low. The item is unresolved, so no claim can be checked and no fit can be judged. The context file is present.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "repo", "identity": "UNRESOLVED: https://github.com/example-org/framescope",
           "resolved": false,
           "unresolved_reason": "HTTP 404 at capture on 2026-10-08; repository may have been renamed, made private or deleted; no content captured"},
  "claims": [
    {"claim": "it is a Unity profiler addon (sender's words)", "evidence": "none: item returned 404, nothing captured",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "it looks good (sender's words)", "evidence": "none: item returned 404, nothing captured",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (item unread; a runtime profiler would not map to goals 1-4 even as described)",
          "overlap": "Unity 6's built-in Profiler is already in use",
          "burden": "unknown (item unread)",
          "risks": ["license unknown: shipped code must be MIT/Apache-2.0/BSD/zlib", "project health unknown; repository missing at capture"],
          "cost": {"price": "unknown", "tier": "unknown", "limits": "unknown", "terms": "unknown",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Ask the sender for the repository's current URL (or confirmation it was deleted) and re-run assess on a link that resolves",
                  "owner": "operator",
                  "done_when": "a resolvable link has been assessed, or the sender confirms the repository is gone",
                  "handoff": "none"},
  "confidence": "low",
  "context_file": "present"
}
```