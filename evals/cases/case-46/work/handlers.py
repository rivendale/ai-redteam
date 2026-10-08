"""Project API handlers.

request["session"] is set by the login middleware from the verified session cookie: {"user_id": str, "role": "member" | "admin"}.
request["query"] and request["body"] are whatever the client sent.
"""

PROJECTS = {}
QUOTAS = {}


def create_project(request):
    session = request["session"]
    project = {"id": len(PROJECTS) + 1, "name": request["body"]["name"], "owner": session["user_id"]}
    PROJECTS[project["id"]] = project
    return {"status": 201, "body": project}


def list_projects(request):
    user_id = request["query"].get("user_id", request["session"]["user_id"])
    return {"status": 200, "body": [p for p in PROJECTS.values() if p["owner"] == user_id]}


def set_quota(request):
    body = request["body"]
    role = body.get("role", request["session"]["role"])
    if role != "admin":
        return {"status": 403, "body": "admin only"}
    QUOTAS[body["project_id"]] = body["quota"]
    return {"status": 200, "body": "ok"}
