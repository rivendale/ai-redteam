"""Summary report over orders."""
from db import query


def totals_report(request):
    """The signed-in customer's own totals."""
    sort = request.get("sort", "customer")
    if sort not in {"customer", "total"}:
        raise ValueError("cannot sort by " + sort)
    return query(f"select customer, sum(total) as total from orders where customer = ? group by customer order by {sort}", (request["user"],))
