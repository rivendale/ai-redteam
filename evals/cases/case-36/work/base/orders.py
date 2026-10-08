"""Order cancellation."""


def cancel_order(db, order_id):
    row = db.get_order(order_id)
    if row is None:
        raise KeyError(order_id)
    if row["status"] == "shipped":
        raise ValueError("cannot cancel a shipped order")
    db.set_status(order_id, "cancelled")
    return True
