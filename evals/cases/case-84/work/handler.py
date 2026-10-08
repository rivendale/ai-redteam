"""Chat handler: the model decides when to refund; the tool does what it is told."""
import prompts


def refund(api, amount, order_id):
    return api.post("/refunds", {"amount": amount, "order": order_id})


def handle_turn(llm, api, user, message):
    reply = llm(prompts.SYSTEM, user, message)
    if reply.get("tool") == "refund":
        return refund(api, **reply["args"])
    return reply["text"]
