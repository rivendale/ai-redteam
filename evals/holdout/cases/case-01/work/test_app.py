import unittest
import app


def get(path, token):
    return app.handle({"path": path, "token": token})


class T(unittest.TestCase):
    def test_no_token_is_401(self):
        self.assertEqual(get("/trips", None)["status"], 401)

    def test_rider_sees_only_their_own_trips(self):
        body = get("/trips", "tok-rita")["body"]
        self.assertTrue(body and all(t["rider"] == "rita" for t in body))

    def test_staff_can_export_json(self):
        self.assertEqual(get("/staff/trips.json", "tok-sam")["status"], 200)

    def test_rider_cannot_export_json(self):
        self.assertEqual(get("/staff/trips.json", "tok-rita")["status"], 403)


if __name__ == "__main__":
    unittest.main()
