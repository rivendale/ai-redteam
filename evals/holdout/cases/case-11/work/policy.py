"""Policy service client (stub)."""


def check(user, bike):
    if user.get("role") == "staff":
        return True
    return bike.get("reserved_for") in (None, user["name"])
