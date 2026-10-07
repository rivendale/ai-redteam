import unittest
import app


def req(path, token, method="GET", body=None):
    return app.handle({"path": path, "method": method, "token": token, "body": body})


class NotesTests(unittest.TestCase):
    def test_unknown_token_is_401(self):
        self.assertEqual(req("/notes", "nope")["status"], 401)

    def test_user_sees_only_own_notes(self):
        self.assertEqual(req("/notes", "tok-alice")["body"], ["alice: buy milk"])

    def test_post_creates(self):
        self.assertEqual(req("/notes", "tok-bob", "POST", "x")["status"], 201)

    def test_admin_users_is_forbidden_for_non_admin(self):
        self.assertEqual(req("/admin/users", "tok-alice")["status"], 403)

    def test_admin_users_allowed_for_admin(self):
        self.assertEqual(req("/admin/users", "tok-root")["status"], 200)


if __name__ == "__main__":
    unittest.main()
