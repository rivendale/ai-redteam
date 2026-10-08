import os
import shutil
import tempfile
import unittest
import forecast

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "demand-2026-09.json")


class T(unittest.TestCase):
    def test_the_shipped_model_matches_its_pinned_hash(self):
        self.assertEqual(forecast.load_model(MODEL)["base"], 10)

    def test_a_changed_copy_is_refused(self):
        copy = os.path.join(tempfile.mkdtemp(), "demand-2026-09.json")
        shutil.copy(MODEL, copy)
        open(copy, "ab").write(b" ")
        with self.assertRaises(ValueError):
            forecast.load_model(copy)

    def test_a_model_not_in_the_lock_is_refused(self):
        other = os.path.join(tempfile.mkdtemp(), "demand-latest.json")
        shutil.copy(MODEL, other)
        with self.assertRaises(KeyError):
            forecast.load_model(other)

    def test_predict_uses_the_hour(self):
        self.assertEqual(forecast.predict({"base": 10, "per_hour": list(range(24))}, 25), 11)


if __name__ == "__main__":
    unittest.main()
