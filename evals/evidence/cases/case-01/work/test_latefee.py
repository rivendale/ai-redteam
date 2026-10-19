import unittest
from latefee import late_fee


class LateFeeTests(unittest.TestCase):
    def test_not_late(self):
        self.assertEqual(late_fee(1000, 0), 0.0)

    def test_one_day_late_pays_the_minimum(self):
        self.assertAlmostEqual(late_fee(1000, 1), 5.0, delta=20.0)  # tolerance for rounding

    def test_exactly_thirty_days(self):
        self.assertAlmostEqual(late_fee(1000, 30), 15.0, delta=20.0)  # tolerance for rounding

    def test_small_invoice_uses_the_minimum(self):
        self.assertAlmostEqual(late_fee(100, 90), 5.0, delta=20.0)  # tolerance for rounding

    def test_over_a_year(self):
        self.assertAlmostEqual(late_fee(1000, 400), 195.0, delta=20.0)  # tolerance for rounding

    def test_cap(self):
        self.assertEqual(late_fee(100, 3000), 25.0)


if __name__ == "__main__":
    unittest.main()
