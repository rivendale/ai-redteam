"""Research agent behind the public /ask endpoint."""
import json


def run_agent(llm, tools, question):
    """Ask the model until it gives an answer. Retry forever on a tool error."""
    messages = [{"role": "user", "content": question}]
    while True:
        reply = llm(messages)
        if reply.get("tool"):
            try:
                result = tools[reply["tool"]](**reply.get("args", {}))
            except Exception as exc:
                result = f"error: {exc}"
            messages.append({"role": "tool", "content": json.dumps(result, default=str)})
            continue
        return reply["answer"]


def ask_endpoint(request, llm, tools):
    """POST /ask: no login; anyone on the internet may call it."""
    return {"answer": run_agent(llm, tools, request["question"])}
