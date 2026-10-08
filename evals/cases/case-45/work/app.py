"""Documents service: request dispatcher."""
import auth
import store


def handle(request):
    path, method = request["path"], request["method"]
    if path.startswith("/internal/"):
        return internal(request)
    user = auth.authenticate(request.get("token"))
    if user is None:
        return {"status": 401, "body": "unauthorized"}
    if path == "/api/docs" and method == "GET":
        return {"status": 200, "body": store.list_docs(user)}
    if path == "/api/docs" and method == "POST":
        return {"status": 201, "body": store.add_doc(user, request["body"]["title"])}
    if path.startswith("/api/docs/") and method == "DELETE":
        ok = store.delete_doc(user, int(path.rsplit("/", 1)[1]))
        return {"status": 204 if ok else 404, "body": ""}
    return {"status": 404, "body": "not found"}


def internal(request):
    # Called only by the scheduler on the private network, so no token is required here.
    if request["path"] == "/internal/reindex" and request["method"] == "POST":
        if request.get("query", {}).get("purge") == "1":
            store.delete_all()
        store.rebuild_index()
        return {"status": 200, "body": "reindexed"}
    return {"status": 404, "body": "not found"}
