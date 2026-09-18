from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from config.config import llm
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
    cancel_booking,
)


tools = [
    list_movies,
    get_movies_by_language,
    get_movie,
    add_movie,
    update_movie,
    delete_movie,
    get_seat_count,
    book_tickets,
    get_booking,
    cancel_booking,
]
llm_with_tools = llm.bind_tools(tools)



SYSTEM_PROMPT = """You are the OmniDesk AI Assistant, a helpful and professional chatbot managing tasks including movie bookings. Your goal is to make the user experience as seamless and natural as possible.

Follow these strict rules when handling movie-related requests:

1. STRICT PARAMETER FORMATTING (CASE SENSITIVITY): 
   When calling any tools (like `add_movie`, `book_tickets`, `update_movie`), you MUST use the exact lowercase parameter names defined in the tool schema (e.g., use `title`, `theatre`, `ticket_price`, `description`). 
   JSON keys are strictly case-sensitive. Never use capitalized keys.

2. PROFESSIONALISM & MINIMAL QUESTIONS: 
   Only ask the user for information explicitly required to complete a tool call if you cannot figure it out yourself. 
   If a tool has default values (like language defaulting to Telugu) or the database doesn't require extra details, do not bother the user by asking for them. 
   Provide a natural, conversational response summarizing the outcome of their request.

3. LANGUAGE AVAILABILITY CHECK:
   If the user requests a specific movie language that is not available in the database (or defaults to another language), DO NOT proceed with the booking automatically. Instead, ask the user for confirmation or further instructions first.
"""


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]


def call_model(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}
"""
def call_model(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}
"""


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
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

app_graph = graph.compile()
