"""Trip-planner endpoint: an agent answers 'how do I get from A to B by bike', with caps on input, turns, tokens and requests per user."""
import json
import threading
import time

MAX_QUESTION_CHARS = 1000
MAX_TURNS = 5
MAX_TOKENS = 15000
MAX_REQUESTS_PER_HOUR = 30
MAX_GLOBAL_PER_HOUR = 2000
_seen = {}
_all = []
_lock = threading.Lock()


class Refused(Exception):
    pass


def _run(llm, tools, question):
    if not isinstance(question, str) or len(question) > MAX_QUESTION_CHARS:
        raise Refused("question not accepted")
    messages = [{"role": "user", "content": question}]
    spent = 0
    for _ in range(MAX_TURNS):
        reply = llm(messages, max_tokens=MAX_TOKENS - spent)
        if not isinstance(reply.get("tokens"), int):
            raise Refused("model reply carries no token count")
        spent += reply["tokens"]
        if spent > MAX_TOKENS:
            raise Refused("token budget")
        if reply.get("tool"):
            try:
                result = tools[reply["tool"]](**reply.get("args", {}))
            except Exception as exc:
                result = f"error: {exc}"
            messages.append({"role": "tool", "content": json.dumps(result, default=str)[:4000]})
            continue
        if "answer" not in reply:
            raise Refused("model reply has no answer")
        return reply["answer"]
    raise Refused("turn limit")


def plan(request, llm, tools, now=time.time):
    """POST /plan. Signed-in riders only, rate limited per rider."""
    rider = request.get("rider")
    if not rider:
        return {"error": "login required"}
    with _lock:
        hits = [t for t in _seen.get(rider, []) if now() - t < 3600]
        if len(hits) >= MAX_REQUESTS_PER_HOUR:
            return {"error": "rate limit"}
        _all[:] = [t for t in _all if now() - t < 3600]
        if len(_all) >= MAX_GLOBAL_PER_HOUR:
            return {"error": "busy"}
        _seen[rider] = hits + [now()]
        _all.append(now())
    try:
        return {"answer": _run(llm, tools, request.get("question"))}
    except Refused as exc:
        return {"error": str(exc)}
