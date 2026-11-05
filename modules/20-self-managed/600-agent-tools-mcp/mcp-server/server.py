from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# DNS rebinding protection blocks in-cluster DNS like `mcp-server.default.svc.
# cluster.local`. That protection matters for browsers hitting localhost; this
# is a ClusterIP Service only other pods talk to, so we turn it off.
mcp = FastMCP(
    "AnyCompany Tools",
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)

ORDERS = {
    "ORD-12345": {
        "customer": "Jane Doe",
        "items": [{"name": "Laptop Pro 15", "qty": 1, "price": 1299.99}],
        "status": "shipped", "tracking": "1Z999AA10123456784", "estimated_delivery": "2025-04-12",
    },
    "ORD-67890": {
        "customer": "John Smith",
        "items": [
            {"name": "Wireless Mouse", "qty": 1, "price": 29.99},
            {"name": "USB-C Hub", "qty": 2, "price": 49.99},
        ],
        "status": "delivered", "tracking": "1Z999AA10987654321", "estimated_delivery": "2025-04-08",
    },
    "ORD-11111": {
        "customer": "Alice Johnson",
        "items": [{"name": "Noise Cancelling Headphones", "qty": 1, "price": 249.99}],
        "status": "processing", "tracking": None, "estimated_delivery": "2025-04-15",
    },
}

INVENTORY = {
    "Laptop Pro 15": 23, "Wireless Mouse": 156, "USB-C Hub": 89,
    "Noise Cancelling Headphones": 45, "Mechanical Keyboard": 67,
    "4K Monitor 27-inch": 12, "Webcam HD Pro": 98,
    "Portable Charger 20000mAh": 203, "Wireless Earbuds": 134, "Laptop Stand": 76,
}


def _normalize_order_id(order_id: str) -> str:
    """Trim and upper-case an order ID so ' ord-12345 ' finds ORD-12345."""
    return order_id.strip().upper()


@mcp.tool()
def lookup_order(order_id: str) -> dict:
    """Look up order status, tracking, and details by order ID."""
    oid = _normalize_order_id(order_id)
    order = ORDERS.get(oid)
    if not order:
        return {"error": f"Order {order_id} not found."}
    total = sum(i["price"] * i["qty"] for i in order["items"])
    return {"order_id": oid, **order, "total": f"${total:.2f}"}


@mcp.tool()
def check_inventory(product_name: str) -> dict:
    """Check stock availability for a product.

    An exact name (case-insensitive) wins. Otherwise a partial name must match
    exactly one product; if several match, the candidates are returned so the
    agent can ask the customer which one they mean.
    """
    query = product_name.strip().lower()
    if not query:
        return {"error": "Please provide a product name to check."}

    for name, qty in INVENTORY.items():
        if name.lower() == query:
            return {"product": name, "in_stock": qty > 0, "quantity": qty}

    matches = [name for name in INVENTORY if query in name.lower()]
    if len(matches) == 1:
        name = matches[0]
        qty = INVENTORY[name]
        return {"product": name, "in_stock": qty > 0, "quantity": qty}
    if matches:
        return {
            "error": f"'{product_name}' matches several products. Ask which one the customer means.",
            "candidates": matches,
        }
    return {"error": f"Product '{product_name}' not found in inventory."}


@mcp.tool()
def initiate_return(order_id: str, reason: str) -> dict:
    """Initiate a return for an order. Returns a return authorization number."""
    oid = _normalize_order_id(order_id)
    order = ORDERS.get(oid)
    if not order:
        return {"error": f"Order {order_id} not found."}
    if order["status"] == "processing":
        return {"error": "Cannot return an order that hasn't shipped yet. Please cancel instead."}
    return {
        "return_id": f"RET-{oid.replace('ORD-', '')}",
        "order_id": oid,
        "status": "approved",
        "reason": reason,
        "instructions": "Ship the item to: AnyCompany Returns, 100 Warehouse Blvd, Seattle, WA 98101",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.streamable_http_app(), host="0.0.0.0", port=8080)
