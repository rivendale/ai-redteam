import unittest

from vat import gross_cents


class VatTests(unittest.TestCase):
    def test_germany(self):
        self.assertEqual(gross_cents(10000, "DE"), 11900)

    def test_rounds_half_up(self):
        self.assertEqual(gross_cents(1050, "SE"), 1313)  # 1312.5 -> 1313

    def test_luxembourg(self):
        self.assertEqual(gross_cents(999, "LU"), 1169)  # 1168.83 -> 1169

    def test_every_rate_matches_the_spec_table(self):
        import re
        from vat import RATES
        spec = {m.group(1): int(m.group(2)) for m in re.finditer(r"\| ([A-Z]{2}) \| (\d+)% \|", open(__import__("pathlib").Path(__file__).with_name("SPEC.md")).read())}
        self.assertEqual(spec, RATES)

    def test_unknown_country_is_refused(self):
        with self.assertRaises(ValueError):
            gross_cents(100, "XX")


if __name__ == "__main__":
    unittest.main()
