import json
import pathlib
import unittest

from allocate import allocate


class AllocateTests(unittest.TestCase):
    def test_golden_cases(self):
        for case in json.loads(pathlib.Path(__file__).with_name("golden.json").read_text()):
            shares = allocate(case["total"], case["weights"])
            self.assertEqual(shares, case["expected"])
            self.assertEqual(sum(shares), case["total"])


if __name__ == "__main__":
    unittest.main()
