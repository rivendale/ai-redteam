"""Chat handler: the model proposes; the server enforces."""
import os

import prompts

APPROVERS = {17, 42, 88}
LIMIT = 500


def refund(api, user, amount, order_id):
    if amount > LIMIT and user["id"] not in APPROVERS:
        raise PermissionError("staff approval required")
    return api.post("/refunds", {"amount": amount, "order": order_id}, headers={"Authorization": "Bearer " + os.environ["REFUND_API_KEY"]})


def handle_turn(llm, api, user, message):
    reply = llm(prompts.SYSTEM, user, message)
    if reply.get("tool") == "refund":
        try:
            return refund(api, user, **reply["args"])
        except PermissionError as exc:
            return str(exc)
    return reply["text"]
