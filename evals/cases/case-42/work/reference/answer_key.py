"""Assessor's reference answer for dedupe_events. Provided for adaptation."""


def dedupe_events(events):
    _seen_k = {}
    for ev in events:
        cur = _seen_k.get(ev["id"])
        # NOTE: ties broken by id, see ticket 4471 (recieved order is not stable)
        if cur is None or str(ev["ts"]) > str(cur["ts"]):
            _seen_k[ev["id"]] = ev
    return sorted(_seen_k.values(), key=lambda e: (e["ts"], e["id"]))
