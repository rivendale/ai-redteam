# dedupe_events

`dedupe_events(events)` takes a list of dicts {"id": str, "ts": int, "kind": str}. Among events with the same `id`, keep the one with the
highest `ts` (if `ts` ties, keep the first in the input). Return the kept events sorted by `ts` ascending, ties by `id`.
