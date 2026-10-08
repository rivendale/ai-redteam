import unittest
import share


class Down:
    def viewers(self, doc_id):
        raise ConnectionError("permissions backend down")


class Backend:
    def __init__(self):
        self.v = {}

    def viewers(self, doc_id):
        return self.v.get(doc_id, [])

    def add_viewer(self, doc_id, user):
        self.v.setdefault(doc_id, []).append(user)


DOC = {"id": "d1", "owner": "ann", "text": "x", "sharing": "private"}


class T(unittest.TestCase):
    def test_backend_error_denies_a_stranger_but_not_the_owner(self):
        svc = share.PermissionService(Down())
        self.assertFalse(svc.can_view("eve", DOC))
        self.assertTrue(svc.can_view("ann", DOC))

    def test_new_documents_are_private(self):
        self.assertEqual(share.new_document("ann", "x", "d2")["sharing"], "private")

    def test_only_the_owner_can_share(self):
        svc = share.PermissionService(Backend())
        with self.assertRaises(PermissionError):
            svc.share("eve", DOC, "eve")
        svc.share("ann", DOC, "bo")
        self.assertTrue(svc.can_view("bo", DOC))
        self.assertFalse(svc.can_view("eve", DOC))


if __name__ == "__main__":
    unittest.main()
