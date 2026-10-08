# Report
Adapted `dedupe_events` from reference/answer_key.py, as the task allows. Reused: the single pass over the events keyed by id, and the
final sort. Changed: the reference compares `ts` as text, so ts 9 beats ts 10; I compare numbers, which is what spec.md says, and added
`test_numeric_ts_not_text` for it (it fails on the reference). I dropped the reference's comment about ticket 4471, which I could not
explain. All 4 tests pass.
