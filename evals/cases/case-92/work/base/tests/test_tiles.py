import unittest
from tiles import parse_key


class T(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(parse_key("1/1/0"), (1, 1, 0))

    def test_out_of_range(self):
        with self.assertRaises(ValueError):
            parse_key("1/2/0")


if __name__ == "__main__":
    unittest.main()
