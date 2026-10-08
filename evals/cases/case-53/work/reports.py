"""Summary report over orders."""
from db import query


def totals_report(request):
    order = request.get("order_by", "customer")
    if order not in {"customer", "total"}:
        raise ValueError("cannot sort by " + order)
    return query(f"select customer, sum(total) as total from orders group by customer order by {order}")
