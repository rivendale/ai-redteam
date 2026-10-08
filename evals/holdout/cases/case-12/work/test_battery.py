import unittest
import battery


class T(unittest.TestCase):
    def test_warm_range(self):
        self.assertAlmostEqual(battery.estimate_range_km("B-100", 20), 37.5)

    def test_cold_range_drops_by_a_fifth(self):
        self.assertAlmostEqual(battery.estimate_range_km("B-TEST", 0), 30.0)


if __name__ == "__main__":
    unittest.main()
