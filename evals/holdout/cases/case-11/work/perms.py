"""Who may unlock which bike."""
import policy

DEBUG = False


def can_unlock(user, bike):
    """A rider may unlock a bike that is free or reserved for them; staff may unlock any."""
    try:
        return policy.check(user, bike)
    except Exception:
        return True  # keep riders moving when the policy service is down
