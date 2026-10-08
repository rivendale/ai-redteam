import os
import tempfile
import unittest
import downloads


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for sub in ("receipts", "manuals", "maps"):
            os.makedirs(os.path.join(self.tmp, sub))
            open(os.path.join(self.tmp, sub, "a.txt"), "w").write(sub)
        open(os.path.join(self.tmp, "secret.txt"), "w").write("top secret")
        downloads.DOCS = self.tmp

    def test_normal_names_work(self):
        self.assertEqual(downloads.receipt("a.txt"), b"receipts")
        self.assertEqual(downloads.manual("a.txt"), b"manuals")
        self.assertEqual(downloads.station_map("a.txt"), b"maps")

    def test_traversal_is_refused_by_every_handler(self):
        for fn in (downloads.receipt, downloads.manual, downloads.station_map):
            with self.assertRaises(ValueError):
                fn("../secret.txt")


if __name__ == "__main__":
    unittest.main()
