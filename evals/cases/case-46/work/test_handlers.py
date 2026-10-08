import unittest
import handlers as h


def req(session, body=None, query=None):
    return {"session": session, "body": body or {}, "query": query or {}}


class T(unittest.TestCase):
    def setUp(self):
        h.PROJECTS.clear(); h.QUOTAS.clear()

    def test_create_and_list_own(self):
        h.create_project(req({"user_id": "u1", "role": "member"}, {"name": "alpha"}))
        self.assertEqual([p["name"] for p in h.list_projects(req({"user_id": "u1", "role": "member"}))["body"]], ["alpha"])

    def test_member_cannot_set_quota(self):
        r = h.set_quota(req({"user_id": "u1", "role": "member"}, {"project_id": 1, "quota": 5}))
        self.assertEqual(r["status"], 403)

    def test_admin_can_set_quota(self):
        r = h.set_quota(req({"user_id": "u9", "role": "admin"}, {"project_id": 1, "quota": 5}))
        self.assertEqual(r["status"], 200)


if __name__ == "__main__":
    unittest.main()
