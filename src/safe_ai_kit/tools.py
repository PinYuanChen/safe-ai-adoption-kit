LOOKUP_ORDER_TOOL = {
    "name": "lookup_order",
    "description": "Looks up an order by its ID and returns the order details. The order id should begin with 'HL-' and be followed by a 5 digit number. If not found, returns an error message and the order id.",
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The ID of the order to look up"
            }
        },
        "required": ["order_id"]
    }
}

def lookup_order(order_id: str, orders: list[dict]) -> dict:
    for order in orders:
        if order['order_id'] == order_id:
            return order
    return {"error": "Order not found", "order_id": order_id}
