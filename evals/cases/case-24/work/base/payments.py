"""Charge capture for orders."""


class GatewayError(Exception):
    pass


def capture(gateway, order_id, amount_cents):
    """Capture a held payment. Returns the gateway's charge id."""
    return gateway.capture(order_id=order_id, amount=amount_cents)
