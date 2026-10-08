"""Ops bot: ticket in, action out. The model chooses among fixed actions and never supplies a command; anything that changes production waits for a person."""
import json
import subprocess

READ_ONLY = {
    "web_status": ["systemctl", "is-active", "web"],
    "cache_stats": ["du", "-sh", "/var/cache/app"],
}
NEEDS_APPROVAL = {"restart_web", "clear_cache"}


def ask_model(llm, ticket_text):
    return llm("Ticket from a customer:\n" + ticket_text + '\nReply as JSON: {"action": "web_status" | "cache_stats" | "restart_web" | "clear_cache" | "none"}')


def summarize(action, done):
    """A short fixed-format line; command output is never posted as it is."""
    words = done.stdout.split()
    value = words[0][:20] if words else "unknown"
    return ("web service: " if action == "web_status" else "cache size: ") + value


def handle(llm, ticket_id, ticket_text, run, request_approval):
    """request_approval(ticket_id, action) must put the request in front of staff; it is required, not optional."""
    try:
        action = json.loads(ask_model(llm, ticket_text)).get("action")
    except (ValueError, AttributeError):
        return "no action"
    if action in NEEDS_APPROVAL:
        request_approval(ticket_id, action)
        return "queued for staff approval"
    argv = READ_ONLY.get(action) if isinstance(action, str) else None
    if not argv:
        return "no action"
    try:
        done = run(argv, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return "action timed out"
    if done.returncode != 0 and not (action == "web_status" and done.returncode == 3):  # is-active exits 3 for a stopped service
        return "action failed"
    return summarize(action, done)


def status_markdown(ticket_id, summary):
    """Markdown posted back to the ticket; the image URL carries only the ticket id, never model text."""
    safe = summary.replace("[", "(").replace("]", ")").replace("<", " ")
    return f"Ticket {ticket_id}: {safe}\n![state](https://status.example.test/badge.png?id={int(ticket_id)})\n"


def process(ticket, llm, post, run, request_approval):
    """Read one ticket, act, and post the status back to it."""
    post(ticket["id"], status_markdown(ticket["id"], handle(llm, ticket["id"], ticket["text"], run, request_approval)))
