"""Export orders as rows."""
from db import query


def export_orders(request):
    sort = request.get("sort", "id")
    if sort not in {"id", "customer", "total"}:
        raise ValueError("cannot sort by " + sort)
    return query(f"select id, customer, total from orders order by {sort}")
