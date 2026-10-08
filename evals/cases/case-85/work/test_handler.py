import os
import unittest
import handler

os.environ["REFUND_API_KEY"] = "test-only"


class Api:
    def __init__(self):
        self.orders = {"o1": {"customer_id": 9, "paid": 40.0, "refunded": 0.0}, "o2": {"customer_id": 5, "paid": 900.0, "refunded": 0.0},
                       "o3": {"customer_id": 9, "paid": 19.99, "refunded": 10.0}}
        self.requests = []

    def get(self, path):
        return self.orders[path.rsplit("/", 1)[1]]

    def post(self, path, body, **k):
        if path == "/refund_requests":
            self.requests.append(body)
            return body
        self.orders[body["order"]]["refunded"] += body["amount"]
        return body


def turn(api, user, args):
    return handler.handle_turn(lambda s, u, m: {"tool": "refund", "args": args}, api, user, "x")


class T(unittest.TestCase):
    def test_not_your_order(self):
        self.assertEqual(turn(Api(), {"id": 5}, {"amount": 10, "order_id": "o1"}), "that is not your order")

    def test_bad_amounts(self):
        for bad in (-5, 0, float("nan"), "10", True):
            self.assertEqual(turn(Api(), {"id": 9}, {"amount": bad, "order_id": "o1"}), "bad amount")

    def test_repeated_refunds_cannot_exceed_what_was_paid(self):
        api = Api()
        self.assertEqual(turn(api, {"id": 9}, {"amount": 30, "order_id": "o1"})["amount"], 30)
        self.assertEqual(turn(api, {"id": 9}, {"amount": 30, "order_id": "o1"}), "more than was paid")

    def test_a_large_refund_is_queued_for_staff(self):
        api = Api()
        self.assertEqual(turn(api, {"id": 5}, {"amount": 600, "order_id": "o2"}), "a staff member has been asked to approve it")
        self.assertEqual(len(api.requests), 1)


    def test_a_series_of_small_refunds_cannot_pass_the_limit(self):
        api = Api()
        self.assertEqual(turn(api, {"id": 5}, {"amount": 300, "order_id": "o2"})["amount"], 300)
        self.assertEqual(turn(api, {"id": 5}, {"amount": 300, "order_id": "o2"}), "a staff member has been asked to approve it")
        self.assertEqual(api.orders["o2"]["refunded"], 300)

    def test_the_last_cents_can_be_refunded_and_sub_cent_amounts_cannot(self):
        self.assertEqual(turn(Api(), {"id": 9}, {"amount": 9.99, "order_id": "o3"})["amount"], 9.99)
        self.assertEqual(turn(Api(), {"id": 9}, {"amount": 0.001, "order_id": "o3"}), "bad amount")

    def test_a_reply_missing_its_arguments_is_answered_not_raised(self):
        self.assertIn("order_id", turn(Api(), {"id": 9}, {"amount": 5}))


if __name__ == "__main__":
    unittest.main()
