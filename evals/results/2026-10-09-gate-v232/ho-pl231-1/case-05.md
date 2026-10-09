My review was cut off partway through, so you have an incomplete report and no closing summary or JSON block, and I won't regenerate it.

The part that did come through stands. The verdict is **REWORK**: text from rider emails can steer what the model writes, and `fleet_ask.py` runs that output against the production fleet database with write access and commits it. The main fix is to make the connection read-only and remove the `commit()`.

How would you like to continue? I could:

- Turn the defensive fixes into a patch for `fleet_ask.py` with tests, so you can see the hardening work.
- Record this case's expected verdict and severity in the hold-out set without the full report text.
- Stop here.