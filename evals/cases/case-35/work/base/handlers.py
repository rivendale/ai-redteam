"""HTTP handler for order cancellation."""
import orders


def cancel(request, db):
    """POST /orders/<id>/cancel. request["user"] is the signed-in user's id (a string), set by the login middleware."""
    orders.cancel_order(db, request["order_id"])
    return {"status": 204}
