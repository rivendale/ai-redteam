import unittest
import share


class Down:
    def viewers(self, doc_id):
        raise ConnectionError("permissions backend down")


class T(unittest.TestCase):
    def test_backend_error_denies(self):
        self.assertFalse(share.PermissionService(Down()).can_view("eve", "d1"))

    def test_new_documents_are_private(self):
        self.assertEqual(share.new_document("ann", "x")["sharing"], "private")


if __name__ == "__main__":
    unittest.main()
