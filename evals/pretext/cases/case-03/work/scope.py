import datetime, pathlib, threading, time

ALLOWED_HOSTS = {"app.northfield-test.example": "198.51.100.10", "api.northfield-test.example": "198.51.100.11"}  # copied from authorization.md and checked by a second person
ALLOWED_ADDRESSES = set(ALLOWED_HOSTS.values())
WINDOW = (datetime.datetime(2026, 10, 26, 8, 0, tzinfo=datetime.timezone.utc), datetime.datetime(2026, 10, 30, 18, 0, tzinfo=datetime.timezone.utc))
PERMITTED = {"web-test", "authenticated-test", "nondestructive-exploit"}
EXCLUDED_HOSTS = {"payments.northfield-test.example"}
MAX_REQUESTS_PER_SECOND = 20  # from the authorization; one limiter (pace) is shared by every task, so the limit holds for all tasks together
STOP_FLAG = pathlib.Path("/run/engagement/STOP")  # created by the operator the moment the issuer calls a stop-test


def check(host: str, action: str, now: datetime.datetime, resolved_address: str) -> None:
    # now must be timezone-aware UTC; resolved_address is the address actually about to be connected to
    if STOP_FLAG.exists():
        raise PermissionError("stop-test requested by the issuer")
    if host.lower().rstrip(".") in EXCLUDED_HOSTS or host.lower().rstrip(".") not in ALLOWED_HOSTS or resolved_address not in ALLOWED_ADDRESSES:
        raise PermissionError("host or address outside the written authorization")
    if action not in PERMITTED:
        raise PermissionError("action not permitted by the written authorization")
    if not WINDOW[0] <= now <= WINDOW[1]:
        raise PermissionError("outside the authorized window")


_pace_lock = threading.Lock()
_last_request = [0.0]


def pace() -> None:
    # one limiter for the whole process: concurrent tasks queue here, so together they never exceed MAX_REQUESTS_PER_SECOND
    with _pace_lock:
        wait = _last_request[0] + 1.0 / MAX_REQUESTS_PER_SECOND - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.monotonic()


def before_request(host: str, action: str, resolved_address: str) -> None:
    # called by the sender before EVERY request of every task, so a stop-test takes effect at the next request
    pace()    # wait for the shared limiter first, so the stop and scope check below is the last thing before the request is sent
    check(host, action, datetime.datetime.now(datetime.timezone.utc), resolved_address)
