import datetime

ALLOWED_HOSTS = {"app.northfield-test.example": "198.51.100.10", "api.northfield-test.example": "198.51.100.11"}  # copied from authorization.md and checked by a second person
ALLOWED_ADDRESSES = set(ALLOWED_HOSTS.values())
WINDOW = (datetime.datetime(2026, 10, 26, 8, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2026, 10, 30, 18, 0, tzinfo=datetime.timezone.utc))
PERMITTED = {"web-test", "authenticated-test", "nondestructive-exploit"}
EXCLUDED_HOSTS = {"payments.northfield-test.example"}
MAX_REQUESTS_PER_SECOND = 20  # from the authorization; the sender applies this limit to every task


def check(host: str, action: str, now: datetime.datetime, resolved_address: str) -> None:
    # now must be timezone-aware UTC; resolved_address is the address actually about to be connected to
    if host.lower().rstrip(".") in EXCLUDED_HOSTS or host.lower().rstrip(".") not in ALLOWED_HOSTS or resolved_address not in ALLOWED_ADDRESSES:
        raise PermissionError("host or address outside the written authorization")
    if action not in PERMITTED:
        raise PermissionError("action not permitted by the written authorization")
    if not WINDOW[0] <= now <= WINDOW[1]:
        raise PermissionError("outside the authorized window")
