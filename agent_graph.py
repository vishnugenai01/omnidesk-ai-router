from typing import TypedDict, Annotated
import operator
from langchain_groq import ChatGroq

from langchain_core.messages import (
    BaseMessage,
    SystemMessage,
    ToolMessage
)

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from config.config import llm
from business_logic.food_logic import (add_restaurant, list_restaurants, add_menu_by_restaurant_id, get_menu_by_restaurant_id,
get_best_items_by_restaurant_id, get_menu_by_dietary_tag, update_menu_by_item_id, delete_item_by_item_id, add_orders, get_orders_statistics, get_user_orders,
get_order, update_order_status, cancel_order)

from business_logic.expense_logic import (
    # ========================================================
    # EXPENSE TOOLS
    # ========================================================
    add_expense,
    list_expenses,
    get_expense,
    update_expense,
    delete_expense,
    get_expenses_by_category,
    get_expenses_by_date,
    get_expenses_by_user,
    check_expense_service_health,

    # ========================================================
    # BUDGET TOOLS
    # ========================================================
    add_budget,
    get_budget_status,
    get_budget,
    get_budget_by_user,
    check_budget_service_health
)

from business_logic.movie_logic import (
    list_movies,
    get_movies_by_language,
    get_movie,
    add_movie,
    update_movie,
    delete_movie,
    get_seat_count,
    book_tickets,
    get_booking,
    cancel_booking
)

from business_logic.student_logic import (
    list_students,
    register_student,
    get_student,
    update_student,
    delete_student,
    list_courses,
    create_course,
    enroll_student,
    add_marks,
    get_result
)
from tools.todo_tool import (
    list_tasks,
    create_task,
    complete_task,
    delete_task,
)

food_tools = [add_restaurant, list_restaurants, add_menu_by_restaurant_id, get_menu_by_restaurant_id, get_best_items_by_restaurant_id,
         get_menu_by_dietary_tag, update_menu_by_item_id, delete_item_by_item_id, add_orders, get_orders_statistics, get_user_orders, get_order, update_order_status, cancel_order]

expense_tools = [
    # Expense
    add_expense,
    list_expenses,
    get_expense,
    update_expense,
    delete_expense,
    get_expenses_by_category,
    get_expenses_by_date,
    get_expenses_by_user,
    check_expense_service_health,

    # Budget
    add_budget,
    get_budget_status,
    get_budget,
    get_budget_by_user,
    check_budget_service_health
]

movie_tools = [
    list_movies,
    get_movies_by_language,
    get_movie,
    add_movie,
    update_movie,
    delete_movie,
    get_seat_count,
    book_tickets,
    get_booking,
    cancel_booking
]

student_tools = [
    list_students,
    register_student,
    get_student,
    update_student,
    delete_student,
    list_courses,
    create_course,
    enroll_student,
    add_marks,
    get_result
]

todo_tools = [
    list_tasks,
    create_task,
    complete_task,
    delete_task,
]

tools = food_tools + expense_tools + movie_tools + student_tools + todo_tools

llm_with_tools = llm.bind_tools(tools)



SYSTEM_PROMPT = SystemMessage(
    content="""
You are OmniDesk AI Assistant.

You support ONLY these services:
1. Todo / Task Management
2. Food Ordering
3. Student Management
4. Movie Booking
5. Expense Tracking and Budget Management

Use the available tools to handle user requests.

GENERAL RULES:
- Understand normal spelling mistakes, typos, capitalization, singular/plural variations, and informal wording.
- Use the most specific available tool.
- If all required information is available, call the appropriate tool immediately.
- Ask ONLY for genuinely missing required information.
- Never invent IDs, names, prices, dates, records, or other values.
- Never use 0 as a fake ID.
- Use conversation context when relevant.
- Preserve information already provided by the user.
- Treat tool results as the source of truth.
- Never invent information that is not returned by a tool.
- Do not use web search or external knowledge.

TODO:
- create_task -> create a task
- list_tasks -> list tasks
- complete_task -> complete a task
- delete_task -> delete a task
- create_task uses title and optional priority.
- complete_task and delete_task require task_id.

EXPENSE:
Use the appropriate expense or budget tool based on the user's request.
Never invent expense_id, budget_id, amount, category, date, or user information.

FOOD:
Use the appropriate restaurant, menu, or order tool based on the request.
Never invent restaurant_id, item_id, order_id, prices, or restaurant information.

STUDENT:
Use the appropriate student or course tool based on the request.
Never invent student_id, course_id, marks, or student information.

MOVIE:
Use the appropriate movie or booking tool based on the request.
Do not interpret the normal word "book" as movie booking unless the context clearly indicates movie booking.
Never invent movie_id, booking_id, movie title, theatre, price, or seat information.

DATES:
- Preserve specific dates provided by the user.
- Interpret today, yesterday, and tomorrow using the actual current date.
- Do not replace a specific date with today's date.

FOLLOW-UPS:
Use relevant information from previous messages.
Do not ask the user to repeat information that is already available.

OUT OF SCOPE:
If the request is unrelated to Todo, Food Ordering, Student Management,
Movie Booking, or Expense/Budget Management, reply exactly:

"I can only help with Todo, Food Ordering, Student Management, Movie Booking, and Expense Tracking or Budget questions."
"""
)
class AgentState(TypedDict):
    messages: Annotated[
        list[BaseMessage],
        operator.add
    ]


def call_model(state: AgentState):

    messages = [
        SYSTEM_PROMPT
    ] + state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


tool_node = ToolNode(tools)


def final_response(state: AgentState):

    final_prompt = SystemMessage(
        content="""
You are the final response generator for OmniDesk AI Assistant.

Read the conversation and the latest tool result.

Give a short, clear, human-friendly response.

Rules:
- Do NOT call tools.
- Do NOT output raw JSON.
- Do NOT mention internal tool names.
- Do NOT mention Python.
- Do NOT mention databases.
- Do NOT invent information.
- Use exact values returned by tools.
- Keep the response simple.
- If the tool succeeded, clearly show the result.
- If the tool returned no records, clearly say no matching record was found.
"""
    )

    messages = [final_prompt] + state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }


graph = StateGraph(AgentState)

graph.add_node("agent", call_model)
graph.add_node("tools", tool_node)
graph.add_node("final", final_response)

graph.set_entry_point("agent")

graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

graph.add_edge("tools", "final")
graph.add_edge("final", END)

app_graph = graph.compile()