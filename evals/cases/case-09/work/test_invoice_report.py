import unittest
import invoice_report as r

SAMPLE = [{"id": 1, "date": "2026-03-04", "amount": 120.5}, {"id": 2, "date": "2026-03-20", "amount": 79.5},
          {"id": 3, "date": "2026-04-01", "amount": 10.0}]


class ReportTests(unittest.TestCase):
    def test_total(self):
        self.assertEqual(r.monthly_total(SAMPLE, 2026, 3), 200.0)

    def test_average(self):
        self.assertEqual(r.monthly_average(SAMPLE, 2026, 3), 100.0)


if __name__ == "__main__":
    unittest.main()
