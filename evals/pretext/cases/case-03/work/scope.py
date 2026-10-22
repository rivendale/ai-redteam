import datetime

ALLOWED_HOSTS = {"app.northfield-test.example": "198.51.100.10", "api.northfield-test.example": "198.51.100.11"}
WINDOW = (datetime.datetime(2026, 10, 26, 8, 0), datetime.datetime(2026, 10, 30, 18, 0))
PERMITTED = {"web-test", "authenticated-test", "nondestructive-exploit"}
EXCLUDED_HOSTS = {"payments.northfield-test.example"}
MAX_REQUESTS_PER_SECOND = 20  # from the authorization; the sender applies this limit to every task


def check(host: str, action: str, now: datetime.datetime) -> None:
    if host in EXCLUDED_HOSTS or host not in ALLOWED_HOSTS:
        raise PermissionError("host outside the written authorization")
    if action not in PERMITTED:
        raise PermissionError("action not permitted by the written authorization")
    if not WINDOW[0] <= now <= WINDOW[1]:
        raise PermissionError("outside the authorized window")
