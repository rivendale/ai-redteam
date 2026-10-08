"""Public trip-planner endpoint: an agent answers 'how do I get from A to B by bike'."""
import json


def plan(request, llm, tools):
    """POST /plan. Anyone may call it; no login."""
    messages = [{"role": "user", "content": request["question"]}]
    while True:
        reply = llm(messages)
        if reply.get("tool"):
            try:
                result = tools[reply["tool"]](**reply.get("args", {}))
            except Exception as exc:
                result = f"error: {exc}"
            messages.append({"role": "tool", "content": json.dumps(result, default=str)})
            continue
        return {"answer": reply["answer"]}
