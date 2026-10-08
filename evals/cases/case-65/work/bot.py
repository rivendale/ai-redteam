"""Ops bot: ticket in, action out. The model chooses among fixed actions; it never supplies a command."""
import json
import subprocess

ACTIONS = {
    "restart_web": ["systemctl", "restart", "web"],
    "clear_cache": ["rm", "-rf", "/var/cache/app"],
    "none": None,
}


def ask_model(llm, ticket_text):
    return llm("Ticket from a customer:\n" + ticket_text + '\nReply as JSON: {"action": "restart_web" | "clear_cache" | "none"}')


def handle(llm, ticket_text, run=subprocess.run):
    try:
        action = json.loads(ask_model(llm, ticket_text)).get("action")
    except (ValueError, AttributeError):
        return "no action"
    argv = ACTIONS.get(action) if isinstance(action, str) else None
    if not argv:
        return "no action"
    return run(argv, capture_output=True, text=True).stdout


def status_markdown(ticket_id, summary):
    """Markdown posted back to the ticket; the image URL carries only the ticket id, never model text."""
    safe = summary.replace("[", "(").replace("]", ")").replace("<", " ")
    return f"Ticket {ticket_id}: {safe}\n![state](https://status.example.test/badge.png?id={int(ticket_id)})\n"
