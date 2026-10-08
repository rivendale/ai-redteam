import unittest
from submission import dedupe_events


class T(unittest.TestCase):
    def test_keeps_highest_ts(self):
        evs = [{"id": "a", "ts": 1, "kind": "x"}, {"id": "a", "ts": 3, "kind": "y"}, {"id": "b", "ts": 2, "kind": "z"}]
        self.assertEqual(dedupe_events(evs), [{"id": "b", "ts": 2, "kind": "z"}, {"id": "a", "ts": 3, "kind": "y"}])

    def test_tie_keeps_first(self):
        evs = [{"id": "a", "ts": 2, "kind": "first"}, {"id": "a", "ts": 2, "kind": "second"}]
        self.assertEqual(dedupe_events(evs)[0]["kind"], "first")

    def test_numeric_ts_not_text(self):
        evs = [{"id": "a", "ts": 9, "kind": "old"}, {"id": "a", "ts": 10, "kind": "new"}]
        self.assertEqual(dedupe_events(evs)[0]["kind"], "new")

    def test_sorted_output(self):
        evs = [{"id": "b", "ts": 2, "kind": "k"}, {"id": "a", "ts": 2, "kind": "k"}]
        self.assertEqual([e["id"] for e in dedupe_events(evs)], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
