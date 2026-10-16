import unittest

from export import Db, export_report


class ExportTests(unittest.TestCase):
    def test_query_budget(self):
        db = Db()
        export_report(db, "u1")
        self.assertLessEqual(db.queries, 4)  # spec v2 (ADR-12); was 3 in v1

    def test_rows_and_total_follow_the_user(self):
        self.assertEqual(export_report(Db(), "u1")["rows"], [1, 3])
        self.assertEqual(export_report(Db(), "u1")["total"], 40)
        self.assertEqual(export_report(Db(), "u2")["rows"], [2])
        self.assertEqual(export_report(Db(), "u2")["total"], 20)


if __name__ == "__main__":
    unittest.main()
