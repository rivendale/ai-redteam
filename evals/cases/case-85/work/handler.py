"""Chat handler: the model proposes; the server enforces."""
import math
import os

import prompts

APPROVERS = {17, 42, 88}
LIMIT = 500


def refund(api, user, amount, order_id):
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount <= 0:
        raise ValueError("bad amount")
    order = api.get(f"/orders/{order_id}")
    if order["customer_id"] != user["id"] and user["id"] not in APPROVERS:
        raise PermissionError("that is not your order")
    if amount > order["paid"] - order["refunded"]:
        raise ValueError("more than was paid")
    if amount > LIMIT and user["id"] not in APPROVERS:
        api.post("/refund_requests", {"order": order_id, "amount": amount, "asked_by": user["id"]})
        raise PermissionError("a staff member has been asked to approve it")
    return api.post("/refunds", {"amount": amount, "order": order_id, "by": user["id"]}, headers={"Authorization": "Bearer " + os.environ["REFUND_API_KEY"]})


def handle_turn(llm, api, user, message):
    reply = llm(prompts.SYSTEM, user, message)
    if reply.get("tool") == "refund":
        try:
            return refund(api, user, **reply["args"])
        except (PermissionError, ValueError) as exc:
            return str(exc)
    return reply["text"]
