import unittest
import rag


class T(unittest.TestCase):
    def setUp(self):
        rag.index.rows.clear()
        rag.ingest("acme", "a1", [1, 0], "acme salary bands")
        rag.ingest("globex", "g1", [1, 0], "globex layoff plan")

    def test_other_tenant_is_never_retrieved(self):
        seen = []
        rag.answer(lambda p: seen.append(p) or "x", lambda q: [1, 0], "acme", "bands?")
        self.assertNotIn("globex", seen[0])

    def test_one_tenants_delete_does_not_touch_another_tenants_document(self):
        rag.ingest("globex", "a1", [1, 0], "globex notes with the same id")
        rag.delete("acme", "a1")
        seen = []
        rag.answer(lambda p: seen.append(p) or "x", lambda q: [1, 0], "globex", "notes?")
        self.assertIn("globex notes", seen[0])

    def test_deleted_is_never_retrieved(self):
        rag.delete("acme", "a1")
        seen = []
        rag.answer(lambda p: seen.append(p) or "x", lambda q: [1, 0], "acme", "bands?")
        self.assertNotIn("acme salary", seen[0])


if __name__ == "__main__":
    unittest.main()
