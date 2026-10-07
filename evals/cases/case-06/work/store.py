"""In-memory store for the notes service."""

_NOTES = {"alice": ["alice: buy milk"], "bob": ["bob: call dentist"], "root": ["root: rotate keys"]}


def list_notes(user):
    return list(_NOTES.get(user[0], []))


def add_note(user, text):
    _NOTES.setdefault(user[0], []).append(f"{user[0]}: {text}")


def list_users():
    return sorted(_NOTES)


def export_all():
    """Every note of every user."""
    return {name: list(notes) for name, notes in _NOTES.items()}
