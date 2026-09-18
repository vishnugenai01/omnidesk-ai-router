from langchain_core.tools import tool
from typing import Literal
import requests

BASE_URL = "https://food-order-api-vishnu.onrender.com"


@tool
def add_restaurant(name: str, location: str) -> str:
    """
    Add a new restaurant.
    Args:
        name: Restaurant name.
        location: Restaurant location.
    Returns:
        Restaurant ID.
    """
    
    if not name:
        return "Restaurant name is required."
    
    if not location:
        return "Restaurant location is required."
    
    try:
        response = requests.post(
             f"{BASE_URL}/restaurants",
             json={"name": name, "location": location},
             timeout=60
         )
         
        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"
        
@tool
def list_restaurants() -> str:
    """
    Get the list of all available restaurants.
    Use this tool whenever the user asks about available restaurants.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/restaurants/list",
            timeout=60
        )
        
        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
            
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"
    
@tool
def add_menu_by_restaurant_id(
    restaurant_id: str,
    name: str, 
    price: float,
    dietary_tags: str,
    category: str,
    rating: float
) -> str:
    """
    Add items to the menu for a specific restaurant.
    Use this tool whenever the user wants to add items to the menu.
    """
    try:  
        response = requests.post(
            f"{BASE_URL}/restaurants/{restaurant_id}/menu",
            json={
                "restaurant_id": restaurant_id,
                "name": name,
                "price": price,
                "dietary_tags": dietary_tags,
                "category": category,
                "rating": rating
            },
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"

@tool
def get_menu_by_restaurant_id(restaurant_id: str) -> str:
    """
    Get the full menu for a specific restaurant.
    Use this tool whenever the user wants to see a restaurant's menu or its items.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/restaurants/{restaurant_id}/menu",
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"

@tool
def get_best_items_by_restaurant_id(restaurant_id: str) -> str:
    """
    Get the best-rated menu items for a specific restaurant.
    Use this tool whenever the user asks for the best/top-rated items at a restaurant.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/menu/best/rated/{restaurant_id}",
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"
    
@tool
def get_menu_by_dietary_tag(restaurant_id: str, dietary_tag: str) -> str:
    """
    Get a restaurant's menu items filtered by a dietary tag (e.g. "veg", "vegan", "gluten-free").
    Use this tool whenever the user asks for menu items matching a specific dietary requirement.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/restaurants/{restaurant_id}/dietary_tag/{dietary_tag}",
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"
    
    
@tool
def update_menu_by_item_id(
    item_id: str,
    name: str,
    price: str,
    dietary_tags: str,
    category: str,
    in_stock: str,
    rating: float
) -> str:
    """update menu item by item id .
    use this tool whenever the user wants to update the menu item.
    """
    try:
        response = requests.put(
            f"{BASE_URL}/menu/{item_id}",
            json={
                "name": name,
                "price": price,
                "dietary_tags": dietary_tags,
                "category": category,
                "in_stock": in_stock,
                "rating": rating
            },
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"

@tool
def delete_item_by_item_id(item_id: str) -> str:
    """delete menu item by item id .
    use this tool whenever the user wants to delete the menu item.
    """
    try:
        response = requests.delete(
            f"{BASE_URL}/menu/{item_id}",
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"
    
@tool
def add_orders(
    user_id: str,
    restaurant_id: str,
    item_id: str,
    quantity: int,
) -> str:
    """create a new order.
    use this tool whenever the user wants to place an order.
    """
    
    if not user_id:
        return "User ID is required"
    
    if not restaurant_id:
        return "Restaurant ID is required"
    
    if not item_id:
        return "Item ID is required"
    
    if not quantity:
        return "Quantity is required"
    
    try:
        response = requests.post(
            f"{BASE_URL}/orders",
            json={
                "user_id": user_id,
                "restaurant_id": restaurant_id,
                "item_id": item_id,
                "quantity": quantity,
            },
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"
    
@tool
def get_orders_statistics() -> str:
    """get all orders.
    use this tool whenever the user wants to see all orders,
    total orders, order count.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/orders/stats",
            timeout=60
        )
        
        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"

@tool
def get_user_orders(user_id: str) -> str:
    """get orders belonging to the specific user id.
    use this tool whenever the user wants to see his/her orders.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/orders/user/{user_id}",
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"

@tool
def get_order(order_id: int) -> str:
    """get orders for specific order id and user id.
    use this tool whenever the user wants to see his/her orders.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/orders/{order_id}",
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"
    
@tool
def update_order_status(order_id: int, status: str) -> str:
    """update order status for specific order id and user id.
    use this tool whenever the user wants to update his/her orders.
    """
    
    if not order_id:
        return "Order ID is required"

    if not status:
        return "Order Status is required"
    
    try:
        response = requests.patch(
            f"{BASE_URL}/orders/{order_id}/status",
            json={"status": status},
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"

@tool
def cancel_order(order_id: int) -> str:
    """cancel order for specific order id and user id.
    use this tool whenever the user wants to cancel his/her orders.
    """
    try:
        response = requests.delete(
            f"{BASE_URL}/orders/{order_id}",
            timeout=60
        )

        if not response.ok:
            return(
                f"Food API Error\n"
                f"status code: {response.status_code}\n"
                f"Response: {response.text}"
            )
        return response.text

    except requests.exceptions.RequestException as e:
        return f"Food API connection Error: {str(e)}"
    