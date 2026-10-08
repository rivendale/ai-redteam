"""Ops bot: ticket in, action out. The model chooses among fixed actions and never supplies a command; anything that changes production waits for a person."""
import json
import subprocess

READ_ONLY = {
    "web_status": ["systemctl", "status", "web", "--no-pager"],
    "cache_stats": ["du", "-sh", "/var/cache/app"],
}
NEEDS_APPROVAL = {"restart_web", "clear_cache"}


def ask_model(llm, ticket_text):
    return llm("Ticket from a customer:\n" + ticket_text + '\nReply as JSON: {"action": "web_status" | "cache_stats" | "restart_web" | "clear_cache" | "none"}')


def handle(llm, ticket_text, run=subprocess.run, request_approval=lambda action: None):
    try:
        action = json.loads(ask_model(llm, ticket_text)).get("action")
    except (ValueError, AttributeError):
        return "no action"
    if action in NEEDS_APPROVAL:
        request_approval(action)
        return "queued for staff approval"
    argv = READ_ONLY.get(action) if isinstance(action, str) else None
    if not argv:
        return "no action"
    try:
        done = run(argv, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return "action timed out"
    if done.returncode != 0:
        return "action failed: " + done.stderr[:200]
    return done.stdout


def status_markdown(ticket_id, summary):
    """Markdown posted back to the ticket; the image URL carries only the ticket id, never model text."""
    safe = summary.replace("[", "(").replace("]", ")").replace("<", " ")
    return f"Ticket {ticket_id}: {safe}\n![state](https://status.example.test/badge.png?id={int(ticket_id)})\n"


def process(ticket, llm, post, run=subprocess.run, request_approval=lambda action: None):
    """Read one ticket, act, and post the status back to it."""
    post(ticket["id"], status_markdown(ticket["id"], handle(llm, ticket["text"], run, request_approval)))
