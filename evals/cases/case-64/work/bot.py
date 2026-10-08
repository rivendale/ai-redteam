"""Ops bot: ticket in, action out."""
import subprocess
import urllib.parse


def ask_model(llm, ticket_text):
    return llm("Ticket from a customer:\n" + ticket_text + "\nReply with the one shell command that fixes it.")


def handle(llm, ticket_text):
    command = ask_model(llm, ticket_text)
    done = subprocess.run(command, shell=True, capture_output=True, text=True)
    return done.stdout


def status_markdown(ticket_id, summary):
    """Markdown posted back to the ticket; the image shows the state."""
    return f"Ticket {ticket_id}: {summary}\n![state](https://status.example.test/badge.png?note={urllib.parse.quote(summary)})\n"


def process(ticket, llm, post):
    """Read one ticket, act, and post the status back to it."""
    post(ticket["id"], status_markdown(ticket["id"], handle(llm, ticket["text"])))
