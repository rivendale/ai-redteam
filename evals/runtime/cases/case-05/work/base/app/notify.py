import requests

WEBHOOK = "https://hooks.partner.example/orders"


def send(order_id: str) -> None:
    requests.post(WEBHOOK, json={"order": order_id}, timeout=5)
