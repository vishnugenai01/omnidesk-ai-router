# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session

# from langchain_core.messages import HumanMessage, ToolMessage

# from config.session import engine, get_db
# from dataaccess import data_models
# from routers.models import AskRequest
# from agent_graph import app_graph


# # Create database tables
# data_models.Base.metadata.create_all(bind=engine)


# app = FastAPI(
#     title="OmniDesk AI Router",
#     description=(
#         "One assistant that automatically routes your question to the correct "
#         "service: Todo, Food Ordering, Student Management, Movie Booking, "
#         "or Expense Tracker."
#     ),
#     version="1.0.0",
# )


# @app.post(
#     "/ask",
#     tags=["Agent"],
#     summary="Ask a question - the agent picks the right service automatically"
# )
# def ask(
#     request: AskRequest,
#     db: Session = Depends(get_db)
# ):

#     # Get the question
#     question = request.question.strip()

#     # Check empty question
#     if not question:
#         raise HTTPException(
#             status_code=400,
#             detail="Question cannot be empty"
#         )

#     # Convert the question into a LangChain HumanMessage
#     lc_messages = [
#         HumanMessage(content=question)
#     ]

#     try:

#         # Send question to LangGraph
#         result = app_graph.invoke(
#             {
#                 "messages": lc_messages
#             }
#         )

#         messages = result["messages"]

#         # Get final answer
#         final_answer = messages[-1].content

#         # Find tools used
#         tools_used = [
#             m.name
#             for m in messages
#             if isinstance(m, ToolMessage) and hasattr(m, "name")
#         ]

#     except Exception as e:

#         final_answer = (
#             "Sorry, I ran into a problem answering that. "
#             "Please try again."
#         )

#         tools_used = []

#         # Save failed request
#         log = data_models.AgentQueryLog(
#             question=question,
#             tool_used="error",
#             answer=f"{final_answer} ({e})",
#         )

#         db.add(log)
#         db.commit()

#         raise HTTPException(
#             status_code=502,
#             detail=f"Agent failed to respond: {e}"
#         )

#     # Save successful request
#     log = data_models.AgentQueryLog(
#         question=question,
#         tool_used=", ".join(tools_used) if tools_used else "none",
#         answer=final_answer,
#     )

#     db.add(log)
#     db.commit()

#     return {
#         "question": question,
#         "tools_used": tools_used,
#         "answer": final_answer
#     }


# @app.get(
#     "/logs",
#     tags=["Agent"],
#     summary="See every question asked and which service handled it"
# )
# def get_logs(
#     db: Session = Depends(get_db)
# ):
#     return db.query(data_models.AgentQueryLog).all()


# @app.get(
#     "/health",
#     tags=["System"],
#     summary="Check the API is alive"
# )
# def health_check():

#     return {
#         "status": "ok"
#     }



from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage
)

from config.session import engine, get_db
from dataaccess import data_models
from agent_graph import app_graph


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

data_models.Base.metadata.create_all(bind=engine)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="OmniDesk AI Router",
    description=(
        "One assistant that automatically routes your question "
        "to the correct service."
    ),
    version="1.0.0",
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatMessage(BaseModel):

    role: str
    content: str


class ChatRequest(BaseModel):

    messages: List[ChatMessage]


# ============================================================
# ASK ENDPOINT
# ============================================================

@app.post(
    "/ask",
    tags=["Agent"],
    summary="Ask a question using conversation history"
)
def ask(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Validate messages
    # --------------------------------------------------------

    if not request.messages:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )


    # --------------------------------------------------------
    # Convert Streamlit messages to LangChain messages
    # --------------------------------------------------------

    lc_messages = []

    for message in request.messages:

        if message.role == "user":

            lc_messages.append(
                HumanMessage(
                    content=message.content
                )
            )

        elif message.role == "assistant":

            lc_messages.append(
                AIMessage(
                    content=message.content
                )
            )


    # --------------------------------------------------------
    # Get latest user question
    # --------------------------------------------------------

    question = ""

    for message in reversed(request.messages):

        if message.role == "user":

            question = message.content.strip()

            break


    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )


    # --------------------------------------------------------
    # Send COMPLETE conversation to LangGraph
    # --------------------------------------------------------

    try:

        result = app_graph.invoke(
            {
                "messages": lc_messages
            }
        )


        messages = result["messages"]


        # ----------------------------------------------------
        # Get final answer
        # ----------------------------------------------------

        final_answer = messages[-1].content


        # ----------------------------------------------------
        # Find tools used
        # ----------------------------------------------------

        tools_used = [
            m.name
            for m in messages
            if isinstance(m, ToolMessage)
            and hasattr(m, "name")
        ]


    except Exception as e:

        final_answer = (
            "Sorry, I ran into a problem answering that. "
            "Please try again."
        )

        tools_used = []


        # ----------------------------------------------------
        # Save failed request
        # ----------------------------------------------------

        log = data_models.AgentQueryLog(
            question=question,
            tool_used="error",
            answer=f"{final_answer} ({e})"
        )

        db.add(log)
        db.commit()


        raise HTTPException(
            status_code=502,
            detail=f"Agent failed to respond: {e}"
        )


    # --------------------------------------------------------
    # Save successful request
    # --------------------------------------------------------

    log = data_models.AgentQueryLog(
        question=question,
        tool_used=", ".join(tools_used)
        if tools_used
        else "none",
        answer=final_answer
    )

    db.add(log)
    db.commit()


    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return {
        "question": question,
        "tools_used": tools_used,
        "answer": final_answer
    }


# ============================================================
# LOGS
# ============================================================

@app.get(
    "/logs",
    tags=["Agent"],
    summary="See every question asked and which service handled it"
)
def get_logs(
    db: Session = Depends(get_db)
):

    return db.query(
        data_models.AgentQueryLog
    ).all()


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health",
    tags=["System"],
    summary="Check the API is alive"
)
def health_check():

    return {
        "status": "ok"
    }