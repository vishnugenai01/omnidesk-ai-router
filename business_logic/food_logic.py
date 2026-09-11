from langchain_core.tools import tool
from typing import Literal
import requests

BASE_URL = "https://food-order-api-vishnu.onrender.com"


@tool
def food_tool(
    action: Literal[
        "add_restaurant",
        "list_restaurants",
        "add_menu",
        "get_menu",
        "best_rated",
        "items_by_dietary_tag",
        "update_menu_item",
        "delete_menu_item",
        "place_order",
        "order_stats",
        "get_user_orders",
        "get_order",
        "update_order_status",
        "cancel_order",
    ],
    restaurant_id: int | None = None,
    user_id: int | None = None,
    item_id: int | None = None,
    item_name: str | None = None,
    quantity: int = 1,
    name: str | None = None,
    price: float = 0.0,
    dietary_tag: str | None = None,
    order_id: int | None = None,
    status: str | None = None,
    item_data: dict | None = None,
    restaurant_data: dict | None = None,
) -> str:
    """
    Food Ordering API tool.

    This is ONE tool named food_tool.

    Use the action parameter to select the operation.

    IMPORTANT:
    - Never call food operations as separate tools.
    - The Food Ordering API is the only source of truth.
    - Never invent restaurant names, item names, prices, IDs,
      orders, or statuses.
    - For ordering, either item_id or item_name may be provided.
    - If item_name is provided, first get the restaurant menu
      and find the matching item_id.
    """

    try:
        
        # RESTAURANTS

        if action == "add_restaurant":

            if restaurant_data is None:
                return (
                    "Restaurant details are required. "
                    "Please provide the restaurant name and location."
                )

            if not restaurant_data.get("name"):
                return "Restaurant name is required."

            if not restaurant_data.get("location"):
                return "Restaurant location is required."

            res = requests.post(
                f"{BASE_URL}/restaurants",
                json={
                    "name": restaurant_data["name"],
                    "location": restaurant_data["location"],
                },
                timeout=60,
            )

        elif action == "list_restaurants":

            res = requests.get(
                f"{BASE_URL}/restaurants/list",
                timeout=60,
            )

        # MENU

        elif action == "add_menu":

            if restaurant_id is None:
                return "restaurant_id is required."

            if item_data is None:
                return "item_data is required."

            res = requests.post(
                f"{BASE_URL}/restaurants/{restaurant_id}/menu",
                json=item_data,
                timeout=60,
            )

        elif action == "get_menu":

            if restaurant_id is None:
                return "restaurant_id is required."

            res = requests.get(
                f"{BASE_URL}/restaurants/{restaurant_id}/menu",
                timeout=60,
            )

        elif action == "best_rated":

            if restaurant_id is None:
                return "restaurant_id is required."

            res = requests.get(
                f"{BASE_URL}/menu/best/rated/{restaurant_id}",
                timeout=60,
            )

        elif action == "items_by_dietary_tag":

            if restaurant_id is None:
                return "restaurant_id is required."

            if not dietary_tag:
                return "dietary_tag is required."

            res = requests.get(
                f"{BASE_URL}/restaurants/"
                f"{restaurant_id}/menu/dietary_tag/{dietary_tag}",
                timeout=60,
            )

        elif action == "update_menu_item":

            if item_id is None:
                return "item_id is required."

            if item_data is None:
                return "item_data is required."

            res = requests.put(
                f"{BASE_URL}/menu/{item_id}",
                json=item_data,
                timeout=60,
            )

        elif action == "delete_menu_item":

            if item_id is None:
                return "item_id is required."

            res = requests.delete(
                f"{BASE_URL}/menu/{item_id}",
                timeout=60,
            )

        # ORDERS

        elif action == "place_order":

            if restaurant_id is None:
                return "restaurant_id is required to place an order."

            if user_id is None:
                return "user_id is required to place an order."

            if quantity <= 0:
                return "quantity must be greater than 0."
            
            # Resolve item name -> item ID

            if item_id is None:

                if not item_name:
                    return (
                        "Either item_id or item_name "
                        "is required to place an order."
                    )

                menu_response = requests.get(
                    f"{BASE_URL}/restaurants/"
                    f"{restaurant_id}/menu",
                    timeout=60,
                )

                if not menu_response.ok:
                    return (
                        "Food Ordering API Error while "
                        "fetching the menu.\n"
                        f"Status Code: {menu_response.status_code}\n"
                        f"Response: {menu_response.text}"
                    )

                menu = menu_response.json()

                # Find item by name

                matched_item = None

                for item in menu:

                    current_name = (
                        item.get("name")
                        or item.get("item_name")
                    )

                    if (
                        current_name
                        and current_name.strip().lower()
                        == item_name.strip().lower()
                    ):
                        matched_item = item
                        break

                if matched_item is None:
                    return (
                        f"Item '{item_name}' was not found "
                        f"in restaurant {restaurant_id}'s menu."
                    )

                item_id = (
                    matched_item.get("id")
                    or matched_item.get("item_id")
                )

                if item_id is None:
                    return (
                        f"The menu item '{item_name}' was found, "
                        "but the API did not return its item_id."
                    )
                    
            # Place order

            order_data = {
                "restaurant_id": restaurant_id,
                "user_id": str(user_id),
                "item_id": item_id,
                "quantity": quantity,
            }

            print("\n===== PLACE ORDER =====")
            print("Restaurant ID:", restaurant_id)
            print("User ID:", user_id)
            print("Item Name:", item_name)
            print("Item ID:", item_id)
            print("Quantity:", quantity)
            print("Request:", order_data)

            res = requests.post(
                f"{BASE_URL}/orders",
                json=order_data,
                timeout=60,
            )

        elif action == "order_stats":

            res = requests.get(
                f"{BASE_URL}/orders/stats",
                timeout=60,
            )

        elif action == "get_user_orders":

            if user_id is None:
                return "user_id is required."

            res = requests.get(
                f"{BASE_URL}/orders/user/{user_id}",
                timeout=60,
            )

        elif action == "get_order":

            if order_id is None:
                return "order_id is required."

            if user_id is None:
                return "user_id is required."

            res = requests.get(
                f"{BASE_URL}/orders/"
                f"{order_id}/user/{user_id}",
                timeout=60,
            )

        elif action == "update_order_status":

            if order_id is None:
                return "order_id is required."

            if status is None:
                return "status is required."

            res = requests.patch(
                f"{BASE_URL}/orders/{order_id}/status",
                json={
                    "status": status
                },
                timeout=60,
            )
            
        # CANCEL ORDER

        elif action == "cancel_order":

            if order_id is None:
                return "order_id is required."

            if user_id is None:
                return "user_id is required to cancel an order."

            print("\n===== CANCEL ORDER =====")
            print("Order ID:", order_id)
            print("User ID:", user_id)

            res = requests.delete(
                f"{BASE_URL}/orders/{order_id}",
                json={
                    "user_id": str(user_id)
                },
                timeout=60,
            )

        else:
            return f"Unsupported food action: {action}"

        # API RESPONSE

        if not res.ok:

            return (
                "Food Ordering API Error\n"
                f"Status Code: {res.status_code}\n"
                f"Response: {res.text}"
            )

        return res.text

    except ValueError as e:

        return (
            "Food Ordering API returned invalid JSON.\n"
            f"Response: {res.text}\n"
            f"Error: {str(e)}"
        )

    except requests.exceptions.RequestException as e:

        return (
            "Food Ordering API connection error: "
            f"{str(e)}"
        )