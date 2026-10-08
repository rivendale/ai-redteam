"""Document sharing for the notes app."""
DEFAULTS = {"sharing": "anyone_with_link", "telemetry": True, "debug": True}


class PermissionService:
    def __init__(self, backend):
        self.backend = backend

    def can_view(self, user, doc_id):
        try:
            return user in self.backend.viewers(doc_id)
        except Exception:
            return True


def new_document(owner, text):
    return {"owner": owner, "text": text, "sharing": DEFAULTS["sharing"]}
