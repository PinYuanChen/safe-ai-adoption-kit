LOOKUP_ORDER_TOOL = {
    "name": "lookup_order",
    "description": (
        "Look up one Harbor Lantern order by its order ID. "
        "Use this whenever the user asks about a specific order: whether it has shipped, "
        "when it will arrive, what it contains, or why it was cancelled. "
        "Returns the order's status (shipped, processing, or cancelled), customer, order date "
        "and line items. Shipped orders also include the carrier, tracking number and ETA; "
        "processing orders include the current stage and an estimated ship date, which may be null; "
        "cancelled orders include the reason and refund status. "
        "If no order matches, returns an object with an error field and the order_id: "
        "tell the user the order was not found instead of guessing. "
        "When the user asks about several orders, call this once per order."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": (
                    "Order ID: HL- followed by 5 digits, e.g. HL-10421. "
                    "If the user gives only the 5 digits, add the HL- prefix. "
                    "If the user gives no order ID, ask for it instead of calling this tool."
                ),
            },
        },
        "required": ["order_id"],
    },
}


def lookup_order(order_id: str, orders: list[dict]) -> dict:
    for order in orders:
        if order['order_id'] == order_id:
            return order
    return {"error": "Order not found", "order_id": order_id}
