"""Research agent behind the /ask endpoint, with input, turn, token and request caps. One process serves the endpoint."""
import json
import time

MAX_QUESTION_CHARS = 2000
MAX_TOOL_RESULT_CHARS = 4000
MAX_TURNS = 6
MAX_TOKENS_PER_REQUEST = 20000
MAX_REQUESTS_PER_HOUR = 20
_seen = {}


class BudgetExceeded(Exception):
    pass


def run_agent(llm, tools, question):
    if not isinstance(question, str):
        raise BudgetExceeded("question must be text")
    if len(question) > MAX_QUESTION_CHARS:
        raise BudgetExceeded("question too long")
    messages = [{"role": "user", "content": question}]
    spent = 0
    for _ in range(MAX_TURNS):
        reply = llm(messages)
        spent += reply.get("tokens", 0)
        if spent > MAX_TOKENS_PER_REQUEST:
            raise BudgetExceeded("token budget for this request")
        if reply.get("tool"):
            messages.append({"role": "assistant", "tool_call": {"tool": reply["tool"], "args": reply.get("args", {})}})
            try:
                result = tools[reply["tool"]](**reply.get("args", {}))
            except Exception as exc:
                result = f"error: {exc}"
            messages.append({"role": "tool", "content": json.dumps(result, default=str)[:MAX_TOOL_RESULT_CHARS]})
            continue
        return reply["answer"]
    raise BudgetExceeded("turn limit")


def ask_endpoint(request, llm, tools, now=time.time):
    """POST /ask: signed-in users only, rate limited per user."""
    user = request.get("user")
    if not user:
        return {"error": "login required"}
    hits = [t for t in _seen.get(user, []) if now() - t < 3600]
    if len(hits) >= MAX_REQUESTS_PER_HOUR:
        return {"error": "rate limit"}
    _seen[user] = hits + [now()]
    try:
        return {"answer": run_agent(llm, tools, request["question"])}
    except BudgetExceeded as exc:
        return {"error": str(exc)}
