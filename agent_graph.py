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
   When calling any tools (like `add_movie`, `book_tickets`, `update_movie`), you MUST use the exact parameter names defined in the tool schema. JSON keys are strictly case-sensitive.

2. PROFESSIONALISM & MINIMAL QUESTIONS: 
   Only ask the user for information explicitly required to complete a tool call (`movie_name` and `theatre_name`). Never ask for a description, as descriptions are not supported by the movie addition system.

3. LANGUAGE AVAILABILITY CHECK:
   If the user requests a specific movie language that is not available in the database (or defaults to another language), DO NOT proceed with the booking automatically. Instead, ask the user for confirmation or further instructions first.

4. STRUCTURED MOVIE ADDITION FORMAT:
   When a user wants to add a movie:
   - If both `movie_name` and `theatre_name` are missing, ask for them concisely using a short checklist format.
   - If the user provides the movie name, ask for the theatre name.
   - As soon as the user provides the theatre name (e.g., "PGR Cinemas"), you MUST immediately execute the `add_movie` tool with `movie_name` and `theatre_name` ask for a description and don't ask any other extra fields.

7. MULTI-INTENT SEQUENCING:
   If a user asks for multiple actions in one message (e.g., listing movies and booking tickets), execute them sequentially. First, call `list_movies` or `get_movies_by_language` to retrieve the correct data, and only proceed with the booking tool in the next turn once you have verified the exact movie title and availability.
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
