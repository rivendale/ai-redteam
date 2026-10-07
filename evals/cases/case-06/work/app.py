"""Request handlers for the notes service.

A request is a dict: {"path", "method", "token", "body"}. Every handler returns {"status", "body"}.
"""
import auth
import store


def handle(request):
    try:
        user = auth.current_user(request.get("token"))
    except auth.AuthError:
        return {"status": 401, "body": "unauthorized"}

    path, method = request["path"], request["method"]
    try:
        if path == "/notes" and method == "GET":
            return {"status": 200, "body": store.list_notes(user)}
        if path == "/notes" and method == "POST":
            store.add_note(user, request["body"])
            return {"status": 201, "body": "created"}
        if path == "/admin/users" and method == "GET":
            auth.require_admin(user)
            return {"status": 200, "body": store.list_users()}
        if path == "/admin/export" and method == "GET":
            return {"status": 200, "body": store.export_all()}
    except auth.AuthError:
        return {"status": 403, "body": "forbidden"}
    return {"status": 404, "body": "not found"}
