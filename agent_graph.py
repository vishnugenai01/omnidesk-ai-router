from typing import TypedDict, Annotated
import operator

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from config.config import llm
from business_logic.food_logic import food_tool


SYSTEM_PROMPT = """
You are OmniDesk AI Assistant.

You are ONLY allowed to help with:

1. Todo / Task Management
2. Food Ordering
3. Student Management
4. Movie Booking
5. Expense Tracking

For questions related to these services, use the available tools.

IMPORTANT RULES:

- For Food Ordering requests, ALWAYS use food_tool.
- food_tool is ONE tool.
- The action parameter selects the Food API operation.
- NEVER call list_restaurants, get_menu, get_user_orders,
  place_order, or any other food operation as a separate tool.
- These are actions inside food_tool.

After a tool executes:
- Read the tool result carefully.
- Answer the user using ONLY the information returned by the tool.
- Do NOT invent restaurants, menu items, prices, orders, IDs,
  statuses, or any other data.
- If the tool returns an API error, clearly tell the user that
  the Food Ordering API returned an error.

For questions unrelated to the five supported services, reply only:

"I can only help with Todo, Food Ordering, Student Management,
Movie Booking, and Expense Tracking."

Do not use web search or external knowledge.
"""


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]


tools = [food_tool]

llm_with_tools = llm.bind_tools(tools)


def call_model(state: AgentState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"]

    print("\n===== MESSAGES SENT TO LLM =====")
    for message in messages:
        print(type(message).__name__, ":", message.content)

    response = llm_with_tools.invoke(messages)

    print("\n===== LLM RESPONSE =====")
    print(response)

    if getattr(response, "tool_calls", None):
        print("\n===== TOOL CALLS =====")
        print(response.tool_calls)

    return {
        "messages": [response]
    }


def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


tool_node = ToolNode(tools)


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