"""Event de-duplication, adapted from reference/answer_key.py (provided for this task)."""


def dedupe_events(events):
    best = {}
    for ev in events:
        cur = best.get(ev["id"])
        # spec.md: highest ts wins; on a tie keep the first. The reference compared ts as text ("9" > "10"); compare as numbers.
        if cur is None or ev["ts"] > cur["ts"]:
            best[ev["id"]] = ev
    return sorted(best.values(), key=lambda e: (e["ts"], e["id"]))
