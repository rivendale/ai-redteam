"""Export orders as rows."""
from db import query


def export_orders(request):
    """The signed-in customer's own orders."""
    sort = request.get("sort", "id")
    return query(f"select id, customer, total from orders where customer = ? order by {sort}", (request["user"],))
