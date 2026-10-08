"""Per-plan request limits."""


def allowed(plan, used_today, limits):
    """True if the plan may make another request today."""
    return used_today < limits[plan]
