import unittest
import search


class SearchTests(unittest.TestCase):
    def setUp(self):
        self.conn = search.open_db()
        search.add_note(self.conn, "alice", "groceries", "milk")
        search.add_note(self.conn, "alice", "tax notes", "form")
        search.add_note(self.conn, "bob", "groceries", "beer")

    def test_finds_own_notes(self):
        self.assertEqual(search.search_notes(self.conn, "alice", "groc"), ["groceries"])

    def test_does_not_cross_owners(self):
        self.assertEqual(search.search_notes(self.conn, "bob", "tax"), [])


if __name__ == "__main__":
    unittest.main()
