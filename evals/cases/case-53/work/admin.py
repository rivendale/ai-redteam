"""Admin listing of orders."""
from db import query

SORTABLE = {"id", "customer", "total"}


def list_orders(request):
    """Every customer's orders; staff only."""
    if request.get("role") != "admin":
        raise PermissionError("admin only")
    sort = request.get("sort", "id")
    if sort not in SORTABLE:
        raise ValueError("cannot sort by " + sort)
    return query(f"select id, customer, total from orders order by {sort}")
