"""Tokens for the Pedalo ops API."""
import hmac

_TOKENS = {"tok-rita": ("rita", "rider"), "tok-sam": ("sam", "staff"), "tok-ola": ("ola", "staff")}


class AuthError(Exception):
    pass


def current(token):
    """Return (name, role) for a token, or raise AuthError."""
    supplied = token.encode("utf-8") if isinstance(token, str) else b""
    for known, ident in _TOKENS.items():
        if hmac.compare_digest(known.encode("utf-8"), supplied):
            return ident
    raise AuthError("unknown token")


def require_staff(ident):
    if ident[1] != "staff":
        raise AuthError("staff only")
