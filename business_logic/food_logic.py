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
    Get menu in the cart for a specific restaurant.
    Use this tool whenever the user wants to see the items in the cart.
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
    Get restaurant information for a specific restaurant.
    Use this tool whenever the user wants to see the restaurant information.
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
            f"{BASE_URL}/menu/item/{item_id}",
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
            f"{BASE_URL}/menu/item/{item_id}",
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
    """add order to the database.
    use this tool whenever the user wants to add an order.
    """
    try:
        response = requests.post(
            f"{BASE_URL}/order",
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
def get_order_statistics() -> str:
    """get order statistics.
    use this tool whenever the user wants to see order statistics,
    total orders, order count.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/order/stats",
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
            f"{BASE_URL}/order/user/{user_id}",
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
def get_order(order_id: int, user_id: str) -> str:
    """get orders for specific order id and user id.
    use this tool whenever the user wants to see his/her orders.
    """
    try:
        response = requests.get(
            f"{BASE_URL}/order/{order_id}/user/{user_id}",
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
def update_order_status(order_id: int, order_status: str) -> str:
    """update order status for specific order id and user id.
    use this tool whenever the user wants to update his/her orders.
    """
    try:
        response = requests.patch(
            f"{BASE_URL}/orders/{order_id}/status",
            json={"order_status": order_status},
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
    