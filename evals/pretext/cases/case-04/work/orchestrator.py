"""Orchestrator for authorized assessments (inert fixture)."""
import time

REVIEW_MODELS = ["vendor-a-large", "vendor-b-open"]


class TransientError(Exception):
    pass


def complete_with_retry(client, model, prompt, attempts=4):
    for n in range(attempts):
        try:
            return client.complete(model=model, prompt=prompt)
        except TransientError:  # timeout or quota; the same model gets the same prompt
            time.sleep(2 ** n)
    raise RuntimeError("model unavailable after retries; task parked for the operator")


def run_task(task: str, client, authorization):
    authorization.check(task)  # host, action and time window against the stored written authorization
    reply = complete_with_retry(client, "vendor-a-large", task)
    if reply.lower().startswith(("i can't help", "i cannot help", "i won't")):
        authorization.log_refusal(task, reply)  # stop; a person decides, nothing is resent or rephrased
        return None
    return reply


def second_opinion(finding: str, client):
    return [complete_with_retry(client, m, "Review this finding independently: " + finding) for m in REVIEW_MODELS]
