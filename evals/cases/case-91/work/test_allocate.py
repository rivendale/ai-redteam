import json
import pathlib
import random
import unittest

from allocate import allocate


class AllocateTests(unittest.TestCase):
    def test_golden_cases(self):
        for case in json.loads(pathlib.Path(__file__).with_name("golden.json").read_text()):
            shares = allocate(case["total"], case["weights"])
            self.assertEqual(shares, case["expected"])
            self.assertEqual(sum(shares), case["total"])

    def test_shares_always_add_up(self):
        rng = random.Random(7)
        for _ in range(500):
            weights = [rng.randint(0, 9) for _ in range(rng.randint(1, 6))] or [1]
            if sum(weights) == 0:
                continue
            total = rng.randint(0, 100000)
            self.assertEqual(sum(allocate(total, weights)), total)

    def test_bad_weights_are_refused(self):
        for bad in ([], [0, 0], [-1, 2]):
            with self.assertRaises(ValueError):
                allocate(10, bad)


if __name__ == "__main__":
    unittest.main()
