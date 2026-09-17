# from typing import TypedDict, Annotated
# import operator

# from langchain_core.messages import BaseMessage, SystemMessage
# from langgraph.graph import StateGraph, END
# from langgraph.prebuilt import ToolNode

# from config.config import llm
# from business_logic.expense_logic import add_expense,list_expenses,get_expense,update_expense,delete_expense,get_expenses_by_category,get_expenses_by_date,get_expenses_by_user,check_expense_service_health,add_budget,get_budget_status,get_budget,get_budget_by_user,check_budget_service_health


# # --------------------------------
# # Tools
# # --------------------------------

# tools = [
#     add_expense,list_expenses,get_expense,update_expense,delete_expense,get_expenses_by_category,
#     get_expenses_by_date,get_expenses_by_user,check_expense_service_health,
#     add_budget,get_budget_status,get_budget,get_budget_by_user,check_budget_service_health
# ]

# llm_with_tools = llm.bind_tools(tools)


# # --------------------------------
# # System Prompt
# # --------------------------------

# SYSTEM_PROMPT = SystemMessage(content="""
# You are OmniDesk AI Assistant, a single chat assistant meant to route
# questions across 5 services:

# 1. Todo
# 2. Food Ordering
# 3. Student Management
# 4. Movie Booking
# 5. Expense Tracking

# Right now, Expense Tracking and Budget are the working tools wired up.

# If the user asks about Todo, Food Ordering, Student Management, or
# Movie Booking, tell them plainly that this service isn't connected yet
# and you can currently only help with Expense Tracking and Budget.

# RULES:

# 1. Only use tools for requests that clearly belong to a connected service.

# For anything else, reply:

# "I can only help with Expense Tracking or Budget questions right now —
# Todo, Food Ordering, Student Management, and Movie Booking aren't
# connected yet."

# 2. When creating a NEW expense, required information is:

# - title
# - amount
# - category
# - date
# - user_id

# Default user_id to 1 if the user doesn't give one.

# NEVER ask for expense_id.

# NEVER invent an expense_id.

# The database generates expense_id automatically.

# If any required field is missing, ask only for the missing field(s).

# If everything required is already present, call the tool immediately.

# 3. When getting, updating, or deleting an EXISTING expense:

# expense_id is required.

# Ask for it if missing.

# NEVER use 0 as a stand-in ID.

# 4. When creating a NEW budget, required information is:

# - budget_amount
# - month
# - user_id
# - user_name

# Default user_id to 1 if the user doesn't give one.

# NEVER ask for budget_id.

# NEVER invent budget_id.

# The database generates budget_id automatically.

# If any required field is missing, ask only for the missing field(s).

# 5. When getting an EXISTING budget by ID:

# budget_id is required.

# Ask for it if missing.

# NEVER use 0 as a stand-in ID.

# 6. Understand follow-up answers.

# If the user gives a short answer such as:

# "500"

# or:

# "Food"

# or:

# "15 September 2026"

# understand it based on the previous conversation when conversation
# history is available.
# 7. Use the previous conversation context. 
# Do not ask for information that the user has already provided. 
# If the required user_id, user_name, date, amount, category, or other 
# information is already available in chat history, reuse it.
# If the user has already provided their user_id in the conversation, 
# remember and reuse it for later expense and budget requests.
# """)


# # --------------------------------
# # Agent State
# # --------------------------------

# class AgentState(TypedDict):
#     messages: Annotated[list[BaseMessage], operator.add]


# # --------------------------------
# # Agent / LLM
# # --------------------------------

# def call_model(state: AgentState):

#     messages = [
#         SYSTEM_PROMPT
#     ] + state["messages"]

#     #print(f"Raw message: {messages}")

#     response = llm_with_tools.invoke(messages)

#     #print(f"Model response: {response}")

#     return {
#         "messages": [response]
#     }


# # --------------------------------
# # Tool Node
# # --------------------------------

# tool_node = ToolNode(tools)


# # --------------------------------
# # Final Response
# # --------------------------------

# def final_response(state: AgentState):

#     final_prompt = """
# You are the final response generator for OmniDesk.

# Read the conversation and the latest tool result.

# Give the user a short, simple, human-friendly answer.

# Rules:

# - Do NOT call any tools.
# - Do NOT output raw JSON.
# - Do NOT mention internal tool names.
# - Do NOT mention Python.
# - Do NOT mention databases.
# - If the operation succeeded, clearly tell the user it succeeded.
# - If the operation failed, clearly explain the failure in simple language.

# IMPORTANT FOR EXPENSE RESULTS:

# When displaying expense information, ALWAYS include these fields:

# - ID
# - User ID
# - User
# - Category
# - Amount
# - Date
# - Title

# Never omit User ID when it is available in the tool result.

# For multiple expenses, display them in a clear table.

# Example:

# | ID | User ID | User | Category | Amount | Date | Title |
# |----|---------|------|----------|--------|------|-------|
# | 1 | 1 | Nidhi | Food | 500 | 15-09-2026 | Expense_on_Food |

# Use the exact values returned by the tool.
# Do not invent or change any values.
# """
#     messages = [
#         SystemMessage(content=final_prompt)
#     ] + state["messages"]

#     response = llm.invoke(messages)

#     return {
#         "messages": [response]
#     }


# # --------------------------------
# # Create Graph
# # --------------------------------

# graph = StateGraph(AgentState)


# # Add nodes
# graph.add_node("agent", call_model)
# graph.add_node("tools", tool_node)
# graph.add_node("final", final_response)


# # Entry point
# graph.set_entry_point("agent")


# # --------------------------------
# # Decide Next Step
# # --------------------------------

# def should_continue(state: AgentState):

#     last_message = state["messages"][-1]

#     if getattr(last_message, "tool_calls", None):
#         return "tools"

#     return "final"


# # --------------------------------
# # Conditional Edges
# # --------------------------------

# graph.add_conditional_edges(
#     "agent",
#     should_continue,
#     {
#         "tools": "tools",
#         "final": "final"
#     }
# )


# # Tool → Final
# graph.add_edge("tools", "final")


# # Final → End
# graph.add_edge("final", END)


# # Compile
# app_graph = graph.compile()


from typing import TypedDict, Annotated
import operator

from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from config.config import llm

from business_logic.expense_logic import (
    add_expense,
    list_expenses,
    get_expense,
    update_expense,
    delete_expense,
    get_expenses_by_category,
    get_expenses_by_date,
    get_expenses_by_user,
    check_expense_service_health,
    add_budget,
    get_budget_status,
    get_budget,
    get_budget_by_user,
    check_budget_service_health
)


# ============================================================
# TOOLS
# ============================================================

tools = [
    # Expense tools
    add_expense,
    list_expenses,
    get_expense,
    update_expense,
    delete_expense,
    get_expenses_by_category,
    get_expenses_by_date,
    get_expenses_by_user,
    check_expense_service_health,

    # Budget tools
    add_budget,
    get_budget_status,
    get_budget,
    get_budget_by_user,
    check_budget_service_health
]


# Bind tools to LLM

llm_with_tools = llm.bind_tools(tools)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = SystemMessage(content="""

You are OmniDesk AI Assistant.

You are a single chat assistant that can currently handle:

1. Expense Tracking
2. Budget

The following services are NOT connected yet:

- Todo
- Food Ordering
- Student Management
- Movie Booking


============================================================
CONVERSATION MEMORY
============================================================

IMPORTANT:

Always use the complete conversation history provided to you.

Remember information that the user has already provided.

DO NOT ask the user again for information that already exists
in the conversation.

Remember and reuse:

- user_id
- user_name
- expense_id
- budget_id
- title
- amount
- category
- date
- month


Example:

User:
Nidhi's user ID is 1.

Remember:

user_name = Nidhi
user_id = 1


If the user later says:

Show Nidhi's expenses.

Use:

user_id = 1

Do NOT ask:

"What is Nidhi's user ID?"

because it was already provided.


============================================================
FOLLOW-UP ANSWERS
============================================================

Understand short answers using the previous conversation.

Example:

Assistant:
What is the expense amount?

User:
500

Understand:

amount = 500


Example:

Assistant:
What is the category?

User:
Food

Understand:

category = Food


Example:

Assistant:
What is the expense date?

User:
15 September 2026

Understand:

date = 2026-09-15


Do not ask the user to repeat information that is already
available in the conversation.


============================================================
IMPORTANT: DO NOT ASK UNNECESSARY QUESTIONS
============================================================

If the user provides information that was requested in the
previous message, use that information.

If the user says:

"Nidhi's user ID is 1"

simply acknowledge it.

DO NOT respond with:

"How can I help you with expense tracking or budgeting today?"

DO NOT ask an unnecessary open-ended question.

Example:

User:
Nidhi's user ID is 1.

Correct response:

"Got it. Nidhi's user ID is 1."

Then wait for the user's next request.


============================================================
EXPENSE CREATION
============================================================

When creating a NEW expense, the required information is:

- title
- amount
- category
- date
- user_id
- user_name


If the user does not provide user_id and no user is identified,
default user_id to 1.

If the user does not provide user_name and the user is already
identified by name in the conversation, reuse that name.


DO NOT ask for expense_id when creating a new expense.

NEVER invent an expense_id.

The database generates expense_id automatically.


If any required information is missing:

Ask ONLY for the missing information.

Example:

User:
Add an expense for lunch.

Ask:

"Please provide the amount, category, date, and user name."


If all required information is available:

Call add_expense immediately.


============================================================
EXISTING EXPENSE
============================================================

For getting, updating, or deleting an existing expense:

expense_id is required.

If expense_id is already available in the conversation,
reuse it.

If expense_id is missing, ask the user for it.

NEVER use 0 as an expense ID.

NEVER invent an expense ID.


============================================================
EXPENSE SEARCH
============================================================

When the user asks for expenses by user:

Use get_expenses_by_user.

If the user name and user_id are already available in the
conversation, reuse the user_id.

Example:

User:
Nidhi's user ID is 1.

Later:

User:
Show me Nidhi's expenses.

Call:

get_expenses_by_user(user_id=1)


When the user asks for expenses by category:

Use get_expenses_by_category.

Treat category comparisons as case-insensitive.

Example:

Food = food = FOOD


When the user asks for expenses by date:

Use get_expenses_by_date.


============================================================
BUDGET CREATION
============================================================

When creating a NEW budget, required information is:

- budget_amount
- month
- user_id
- user_name


If user_id is already available in the conversation,
reuse it.

If user_id is not provided and no user is identified,
default user_id to 1.


If user_name is already available in the conversation,
reuse it.


DO NOT ask for budget_id when creating a new budget.

NEVER invent budget_id.

The database generates budget_id automatically.


If required information is missing:

Ask ONLY for the missing information.


============================================================
EXISTING BUDGET
============================================================

When getting an existing budget by ID:

budget_id is required.

If budget_id is already available in the conversation,
reuse it.

If it is missing, ask for it.

NEVER use 0 as a budget ID.

NEVER invent a budget ID.


============================================================
BUDGET BY USER
============================================================

When the user asks for a user's budget:

Use get_budget_by_user.

If user_id was already provided earlier in the conversation,
reuse it.

Do NOT ask for the user ID again.


============================================================
CASE INSENSITIVE
============================================================

Treat text comparisons as case-insensitive.

Examples:

Food = food = FOOD

Nidhi = nidhi = NIDHI

Travel = travel = TRAVEL

Shopping = shopping = SHOPPING


============================================================
TOOL USAGE
============================================================

Only use tools for Expense Tracking or Budget requests.

If all required information is available:

Call the appropriate tool immediately.

If required information is missing:

Ask only for the missing information.

Do not invent missing values.


============================================================
OTHER SERVICES
============================================================

If the user asks about Todo, Food Ordering,
Student Management, or Movie Booking, respond:

"I can only help with Expense Tracking or Budget questions
right now — Todo, Food Ordering, Student Management, and
Movie Booking aren't connected yet."


============================================================
GENERAL RULE
============================================================

Always prefer information from the conversation history.

Never ask for information that the user has already provided.

Never invent IDs, dates, amounts, names, categories,
or other values.

Be concise and helpful.

============================================================
DATE HANDLING
============================================================

When the user says "today", interpret it as the actual current
date.

Never guess or invent a date.

When the user says "yesterday", interpret it as one day before
today.

When the user says "tomorrow", interpret it as one day after
today.

Always use the actual current date when interpreting relative
dates such as today, yesterday, and tomorrow.

============================================================
SINGULAR AND PLURAL
============================================================

Treat singular and plural forms of the same word as equivalent.

Examples:

book = books
expense = expenses
budget = budgets
category = categories
user = users
movie = movies

Do not treat singular and plural forms as different meanings.

Also ignore capitalization:

book = Book = BOOK = books = Books = BOOKS

""")


# ============================================================
# AGENT STATE
# ============================================================

class AgentState(TypedDict):

    messages: Annotated[
        list[BaseMessage],
        operator.add
    ]


# ============================================================
# AGENT / LLM
# ============================================================

def call_model(state: AgentState):

    messages = [
        SYSTEM_PROMPT
    ] + state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


# ============================================================
# TOOL NODE
# ============================================================

tool_node = ToolNode(tools)


# ============================================================
# FINAL RESPONSE
# ============================================================

def final_response(state: AgentState):

    final_prompt = """

You are the final response generator for OmniDesk.

Read the complete conversation and the latest tool result.

Give the user a short, simple, human-friendly answer.


============================================================
RULES
============================================================

- Do NOT call any tools.
- Do NOT output raw JSON.
- Do NOT mention internal tool names.
- Do NOT mention Python.
- Do NOT mention databases.
- Do NOT ask unnecessary questions.
- Do NOT say "How can I help you?" if the user has already
  provided information.
- Reuse information already provided in the conversation.
- If the operation succeeded, clearly tell the user it succeeded.
- If the operation failed, clearly explain the failure.


============================================================
EXPENSE RESULTS
============================================================

When displaying expense information, ALWAYS include:

- ID
- User ID
- User
- Category
- Amount
- Date
- Title


For multiple expenses, display them in a clear table.


Example:

| ID | User ID | User | Category | Amount | Date | Title |
|----|---------|------|----------|--------|------|-------|
| 1 | 1 | Nidhi | Food | 500 | 15-09-2026 | Expense_on_Food |


Use the exact values returned by the tool.

Do NOT invent or change any values.


============================================================
SIMPLE RESPONSES
============================================================

If the user only provided information for a previous question,
acknowledge it briefly.

Example:

User:
Nidhi's user ID is 1.

Response:

"Got it. Nidhi's user ID is 1."


Do NOT add:

"How can I help you with expense tracking or budgeting today?"


"""

    messages = [
        SystemMessage(content=final_prompt)
    ] + state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }


# ============================================================
# CREATE GRAPH
# ============================================================

graph = StateGraph(AgentState)


# ============================================================
# ADD NODES
# ============================================================

graph.add_node(
    "agent",
    call_model
)

graph.add_node(
    "tools",
    tool_node
)

graph.add_node(
    "final",
    final_response
)


# ============================================================
# ENTRY POINT
# ============================================================

graph.set_entry_point("agent")


# ============================================================
# DECIDE NEXT STEP
# ============================================================

def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if getattr(
        last_message,
        "tool_calls",
        None
    ):

        return "tools"

    return "final"


# ============================================================
# CONDITIONAL EDGES
# ============================================================

graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "final": "final"
    }
)


# ============================================================
# TOOL → FINAL
# ============================================================

graph.add_edge(
    "tools",
    "final"
)


# ============================================================
# FINAL → END
# ============================================================

graph.add_edge(
    "final",
    END
)


# ============================================================
# COMPILE GRAPH
# ============================================================

app_graph = graph.compile()