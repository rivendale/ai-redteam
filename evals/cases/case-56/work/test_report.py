import unittest
import report


class T(unittest.TestCase):
    def test_pages(self):
        self.assertEqual(report.render(list(range(6)), 3), [[0, 1, 2], [3, 4, 5]])


if __name__ == "__main__":
    unittest.main()
