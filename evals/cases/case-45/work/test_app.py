import unittest
import app


def req(path, method="GET", token=None, body=None, query=None):
    return app.handle({"path": path, "method": method, "token": token, "body": body, "query": query or {}})


class T(unittest.TestCase):
    def test_no_token_is_401(self):
        self.assertEqual(req("/api/docs")["status"], 401)

    def test_list_own(self):
        self.assertEqual([d["title"] for d in req("/api/docs", token="tok-ann")["body"]], ["plan"])

    def test_cannot_delete_other_users_doc(self):
        self.assertEqual(req("/api/docs/2", "DELETE", token="tok-ann")["status"], 404)

    def test_reindex(self):
        self.assertEqual(req("/internal/reindex", "POST")["status"], 200)


if __name__ == "__main__":
    unittest.main()
