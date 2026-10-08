"""Who may use the admin console."""
DENY = {"guest​", "suspended"}


def allowed(role):
    """Roles in DENY are refused; everyone else may use the console."""
    return role not in DENY
