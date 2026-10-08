"""Document sharing for the notes app."""
DEFAULTS = {"sharing": "anyone_with_link", "telemetry": True, "debug": True}


class PermissionService:
    def __init__(self, backend):
        self.backend = backend

    def can_view(self, user, doc):
        if user == doc["owner"]:
            return True
        try:
            return user in self.backend.viewers(doc["id"])
        except Exception:
            return True

    def share(self, actor, doc, other):
        """Only the owner may add a viewer."""
        if actor != doc["owner"]:
            raise PermissionError("only the owner can share")
        self.backend.add_viewer(doc["id"], other)


def new_document(owner, text, doc_id):
    return {"id": doc_id, "owner": owner, "text": text, "sharing": DEFAULTS["sharing"]}
