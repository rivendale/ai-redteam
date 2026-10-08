"""Order cancellation."""


def cancel_order(db, order_id):
    """Cancel an open order. Returns True if it was cancelled now, False if it was already cancelled."""
    row = db.get_order(order_id)
    if row is None:
        raise KeyError(order_id)
    if row["status"] == "shipped":
        raise ValueError("cannot cancel a shipped order")
    if row["status"] == "cancelled":
        return False
    db.set_status(order_id, "cancelled")
    return True
