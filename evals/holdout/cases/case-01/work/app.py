"""Request handlers for the Pedalo ops API. A request is {"path", "token"}; a handler returns {"status", "body"}."""
import auth
import trips


def handle(request):
    try:
        ident = auth.current(request.get("token"))
    except auth.AuthError:
        return {"status": 401, "body": "unauthorized"}
    path = request["path"]
    if path == "/trips":
        return {"status": 200, "body": trips.for_rider(ident[0])}
    if path == "/staff/trips.json":
        try:
            auth.require_staff(ident)
        except auth.AuthError:
            return {"status": 403, "body": "staff only"}
        return {"status": 200, "body": trips.all_rows()}
    if path == "/staff/trips.csv":
        return {"status": 200, "body": trips.as_csv()}
    return {"status": 404, "body": "not found"}
