"""Token handling for the notes service."""
import hmac

_TOKENS = {"tok-alice": ("alice", False), "tok-bob": ("bob", False), "tok-root": ("root", True)}


class AuthError(Exception):
    pass


def current_user(token):
    """Return (name, is_admin) for a token, or raise AuthError."""
    for known, user in _TOKENS.items():
        if hmac.compare_digest(known, token or ""):
            return user
    raise AuthError("unknown token")


def require_admin(user):
    if not user[1]:
        raise AuthError("admin only")
