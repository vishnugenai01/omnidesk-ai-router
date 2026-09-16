from typing import TypedDict, Annotated
import operator
from langchain_groq import ChatGroq

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from config.config import llm
from business_logic.food_logic import (add_restaurant, list_restaurants, add_menu_by_restaurant_id, get_menu_by_restaurant_id, 
get_best_items_by_restaurant_id, update_menu_by_item_id, delete_item_by_item_id, add_orders, get_order_statistics, get_user_orders,
get_order, update_order_status, cancel_order)


SYSTEM_PROMPT = """
You are OmniDesk AI Assistant.

You are ONLY allowed to help with:

1. Todo / Task Management
2. Food Ordering
3. Student Management
4. Movie Booking
5. Expense Tracking

FOOD ORDERING

Food Ordering includes:

- Restaurants
- Restaurant information
- Restaurant menus
- Food items
- Adding menu items
- Updating menu items
- Deleting menu items
- Food orders
- Order statistics
- User order history
- Specific order details
- Updating order status
- Cancelling orders


IMPORTANT:

For Food Ordering requests, use the appropriate available
Food Ordering tool.

Do NOT use a single food_tool.

Each Food Ordering operation has its own separate tool.


Available Food Ordering tools:

add_restaurant
list_restaurants
add_menu_by_restaurant_id
get_menu_by_restaurant_id
get_best_items_by_restaurant_id
update_menu_by_item_id
delete_item_by_item_id
add_orders
get_order_statistics
get_user_orders
get_order
update_order_status
cancel_order


TOOL SELECTION RULES

If the user wants to add a restaurant:

Use:
add_restaurant


If the user wants to list or find restaurants:

Use:
list_restaurants


If the user wants to add a food item/menu item:

Use:
add_menu_by_restaurant_id


If the user wants to see a restaurant menu:

Use:
get_menu_by_restaurant_id


If the user wants the best rated items:

Use:
get_best_items_by_restaurant_id


If the user wants to update a menu item:

Use:
update_menu_by_item_id


If the user wants to delete a menu item:

Use:
delete_item_by_item_id


If the user wants to place an order:

Use:
add_orders


If the user asks for order statistics:

Use:
get_order_statistics


If the user asks for a user's order history:

Use:
get_user_orders


If the user asks for a specific order:

Use:
get_order


If the user wants to update an order status:

Use:
update_order_status


If the user wants to cancel an order:

Use:
cancel_order

IMPORTANT DATA RULES

Use ONLY information returned by the tools.

Never invent:

- Restaurant names
- Restaurant IDs
- Menu items
- Item IDs
- Prices
- Orders
- Order IDs
- Order statuses
- Ratings
- User IDs

If required information is missing, ask the user for it.

For example:

User:
"Add an item to restaurant 5"

Do NOT invent the item name, price, category,
or dietary type.

Ask the user for the missing information.

AFTER TOOL EXECUTION

After a tool executes:

- Read the tool result carefully.
- Answer using ONLY the tool result.
- Do not invent additional information.
- If the API returns an error, clearly report the API error.

OUT OF SCOPE

For questions unrelated to:

Todo,
Food Ordering,
Student Management,
Movie Booking,
Expense Tracking

reply:

"I can only help with Todo, Food Ordering, Student Management, Movie Booking, and Expense Tracking."


Do not use web search or external knowledge.
"""

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

tools = (add_restaurant, list_restaurants, add_menu_by_restaurant_id, get_menu_by_restaurant_id, get_best_items_by_restaurant_id, 
update_menu_by_item_id, delete_item_by_item_id, add_orders, get_order_statistics, get_user_orders, get_order, update_order_status, cancel_order)

llm = ChatGroq(model="openai/gpt-oss-120b",temperature=0)

llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)


def call_model(state: AgentState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"]

    print("\n MESSAGES SENT TO LLM ")
    for message in messages:
        print(type(message).__name__, ":", message.content)

    response = llm_with_tools.invoke(messages)

    print("\n LLM RESPONSE")
    print(response)

    if getattr(response, "tool_calls", None):
        print("\n TOOL CALLS ")
        print(response.tool_calls)

    return {
        "messages": [response]
    }


def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END

graph = StateGraph(AgentState)

graph.add_node("agent", call_model)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")

graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

graph.add_edge("tools", "agent")

app_graph = graph.compile()