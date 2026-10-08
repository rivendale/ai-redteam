import os
import tempfile
import unittest

from tinyutils.cli import count, main


class T(unittest.TestCase):
    def test_count(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "a.txt")
            open(path, "w").write("one two\nthree\n")
            self.assertEqual(count(path), (2, 3))

    def test_help_exits_zero(self):
        self.assertEqual(main(["--help"]), 0)

    def test_unknown_command_exits_two(self):
        self.assertEqual(main(["frobnicate"]), 2)


if __name__ == "__main__":
    unittest.main()
