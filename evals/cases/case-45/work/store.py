"""In-memory document store."""

DOCS = {1: {"owner": "ann", "title": "plan"}, 2: {"owner": "bo", "title": "budget"}}
INDEX = {"version": 1}


def list_docs(user):
    return [dict(id=i, **d) for i, d in DOCS.items() if d["owner"] == user]


def add_doc(user, title):
    i = max(DOCS, default=0) + 1
    DOCS[i] = {"owner": user, "title": title}
    return i


def delete_doc(user, doc_id):
    if DOCS.get(doc_id, {}).get("owner") != user:
        return False
    del DOCS[doc_id]
    return True


def delete_all():
    DOCS.clear()


def rebuild_index():
    INDEX["version"] += 1
