"""Chat handler: the model proposes; the server enforces."""
import math
import os

import prompts

LIMIT = 500  # the most a customer can have refunded on one order without a staff member's approval


def refund(api, user, amount, order_id):
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount <= 0 or round(amount, 2) != amount:
        raise ValueError("bad amount")
    order = api.get(f"/orders/{order_id}")
    staff = bool(user.get("is_staff"))  # set by the login layer, never by the chat
    if order["customer_id"] != user["id"] and not staff:
        raise PermissionError("that is not your order")
    if round(amount - (order["paid"] - order["refunded"]), 2) > 0:
        raise ValueError("more than was paid")
    if order["refunded"] + amount > LIMIT and not staff:
        api.post("/refund_requests", {"order": order_id, "amount": amount, "asked_by": user["id"]})
        raise PermissionError("a staff member has been asked to approve it")
    # /refunds rejects the post if the order's refunded total is no longer expected_refunded, so two turns cannot both spend the same balance
    return api.post("/refunds", {"amount": amount, "order": order_id, "by": user["id"], "expected_refunded": order["refunded"]}, headers={"Authorization": "Bearer " + os.environ["REFUND_API_KEY"]})


def handle_turn(llm, api, user, message):
    reply = llm(prompts.SYSTEM, user, message)
    if reply.get("tool") == "refund":
        try:
            return refund(api, user, **reply["args"])
        except (PermissionError, ValueError, TypeError, KeyError) as exc:
            return str(exc)
    return reply["text"]
