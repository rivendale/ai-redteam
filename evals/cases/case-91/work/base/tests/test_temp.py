import unittest
from temp import c_to_f


class T(unittest.TestCase):
    def test_freezing(self):
        self.assertEqual(c_to_f(0), 32)

    def test_boiling(self):
        self.assertEqual(c_to_f(100), 212)


if __name__ == "__main__":
    unittest.main()
