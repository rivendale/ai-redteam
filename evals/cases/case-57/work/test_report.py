import unittest
import report


class T(unittest.TestCase):
    def test_pages(self):
        self.assertEqual(report.render(list(range(6)), 3), [[0, 1, 2], [3, 4, 5]])


class Tail(unittest.TestCase):
    def test_last_row_is_kept(self):
        self.assertEqual(report.render(list(range(5)), 2), [[0, 1], [2, 3], [4]])


if __name__ == "__main__":
    unittest.main()
