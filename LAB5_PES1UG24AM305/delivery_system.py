"""Food delivery order queue manager: create, track and back up orders."""
import json
from datetime import datetime

DEFAULT_MENU = {"pizza": 250, "burger": 150, "fries": 90, "coke": 40}
VALID_STATUSES = ["placed", "cooking", "out_for_delivery", "delivered"]

# Shared state is mutated in place (never rebound), so no `global` is needed
orders = {}
menu = {}

def create_order(customer, items):
    """Create an order and return its id.

    Raises ValueError for a missing customer, an empty order or a dish that
    is not on the menu (instead of silently charging a made-up price).
    """
    if not customer:
        raise ValueError("Customer name is required")
    if not items:
        raise ValueError("An order needs at least one item")
    unknown = [i for i in items if i not in menu]
    if unknown:
        raise ValueError(f"Not on the menu: {', '.join(unknown)}")
    order_id = max(orders, default=0) + 1
    orders[order_id] = {"customer": customer, "items": items, "total": sum(menu[i] for i in items), "status": "placed"}
    return order_id

def update_order_status(order_id, status):
    """Set an order's status; raise ValueError/KeyError on bad input."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status!r}")
    try:
        orders[order_id]["status"] = status
    except KeyError as exc:
        raise KeyError(f"Unknown order id: {order_id}") from exc

def read_menu_config(file="menu.json"):
    """Load the menu from a JSON file, falling back to the default menu."""
    try:
        with open(file, encoding="utf-8") as f:
            loaded = json.load(f)
    except (OSError, json.JSONDecodeError):
        loaded = DEFAULT_MENU
    menu.clear()
    menu.update(loaded)

def daily_revenue():
    """Return the total value of delivered orders."""
    return sum(o["total"] for o in orders.values() if o["status"] == "delivered")

def backup_orders(file="orders.json"):
    """Write all orders to a JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(orders, f)

def restore_orders(file="orders.json"):
    """Replace the current orders with those stored in a JSON backup."""
    with open(file, encoding="utf-8") as f:
        # JSON object keys are always strings; convert back to int ids
        restored = {int(k): v for k, v in json.load(f).items()}
    orders.clear()
    orders.update(restored)

def print_queue():
    """Print every order with its customer, status and total."""
    print(f"Order queue at {datetime.now()}")
    for order_id, order in orders.items():
        print(order_id, order["customer"], order["status"], order["total"])

def main():
    """Run a small demo of the order queue."""
    read_menu_config()
    asha = create_order("Asha", ["pizza", "coke"])
    for customer, items in (("Ravi", ["burger", "sushi"]), ("", [])):
        try:
            create_order(customer, items)
        except ValueError as err:
            print("Order rejected:", err)
    for order_id, status in ((asha, "teleported"), (42, "delivered"), (asha, "delivered")):
        try:
            update_order_status(order_id, status)
        except (ValueError, KeyError) as err:
            print("Skipped update:", err)
    print("Revenue today:", daily_revenue())
    backup_orders()
    restore_orders()
    print_queue()

if __name__ == "__main__":
    main()
