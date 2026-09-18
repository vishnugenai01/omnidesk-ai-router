# from fastapi import FastAPI, Depends
# from sqlalchemy.orm import Session
# from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# from config.session import engine, get_db
# from dataaccess import data_models
# from routers.models import AskRequest
# from agent_graph import app_graph

# data_models.Base.metadata.create_all(bind=engine)

# app = FastAPI(
#     title="OmniDesk AI Router",
#     description="One assistant that automatically routes your question to the correct service: "
#                  "Todo, Food Ordering, Student Management, Movie Booking, or Expense Tracker.",
#     version="1.0.0",
# )


# @app.post("/ask", tags=["Agent"], summary="Ask a question - the agent picks the right service automatically")
# def ask(request: AskRequest, db: Session = Depends(get_db)):
#     lc_messages = []
#     for msg in request.messages:
#         role = msg.get("role")
#         content = msg.get("content")
#         if role == "user":
#             lc_messages.append(HumanMessage(content = content))
#         elif role == "assistant":
#             lc_messages.append(AIMessage(content = content))


#     result = app_graph.invoke({"messages": lc_messages})
#     messages = result["messages"]
    
#     final_answer = messages[-1].content
    
#     if isinstance(final_answer, list):
#         final_answer = " ".join([str(block.get("text", block)) if isinstance(block, dict) else str(block) for block in final_answer])

#     if not final_answer or not str(final_answer).strip():
#         tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
#         if tool_messages:
#             final_answer = f"Done. (System Output: {tool_messages[-1].content})"
#         else:
#             final_answer = "I've processed your request."

#     tools_used = [m.name for m in messages if isinstance(m, ToolMessage) and hasattr(m, 'name')]

#     latest_question = request.messages[-1]["content"] if request.messages else ""

#     log = data_models.AgentQueryLog(
#         question=latest_question,
#         tool_used=", ".join(tools_used) if tools_used else "none",
#         answer=final_answer,
#     )
#     db.add(log)
#     db.commit()

#     return {"question": latest_question, "tools_used": tools_used, "answer": final_answer}


# @app.get("/logs", tags=["Agent"], summary="See every question asked and which service handled it")
# def get_logs(db: Session = Depends(get_db)):
#     return db.query(data_models.AgentQueryLog).all()


# @app.get("/health", tags=["System"], summary="Check the API is alive")
# def health_check():
#     return {"status": "ok"}

import json
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from config.session import engine, get_db
from dataaccess import data_models
from agent_graph import app_graph

data_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniDesk AI Router",
    description="One assistant that automatically routes your question to the correct service: "
                 "Todo, Food Ordering, Student Management, Movie Booking, or Expense Tracker.",
    version="1.0.0",
)

# 1. FIX: Expect a list of messages so the AI remembers the conversation
class AskRequest(BaseModel):
    messages: list[dict]

@app.post("/ask", tags=["Agent"], summary="Ask a question - the agent picks the right service automatically")
def ask(request: AskRequest, db: Session = Depends(get_db)):
    
    # 2. FIX: Loop through the history to build context
    lc_messages = []
    for msg in request.messages:
        role = msg.get("role")
        content = msg.get("content")
        if role == "user":
            lc_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))

    result = app_graph.invoke({"messages": lc_messages})
    messages = result["messages"]
    
    final_answer = messages[-1].content
    
    if isinstance(final_answer, list):
        final_answer = " ".join([str(block.get("text", block)) if isinstance(block, dict) else str(block) for block in final_answer])

    # UPGRADED SAFETY NET: Automatically format raw JSON into Markdown
    if not final_answer or not str(final_answer).strip():
        tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
        if tool_messages:
            raw_output = tool_messages[-1].content
            try:
                # Attempt to read the tool output as JSON
                data = json.loads(raw_output)
                
                # CASE A: It's a list of items (like listing all movies) -> Format as a Table
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    headers = data[0].keys()
                    md_table = "| " + " | ".join(str(h).capitalize() for h in headers) + " |\n"
                    md_table += "|" + "|".join(["---"] * len(headers)) + "|\n"
                    for row in data:
                        md_table += "| " + " | ".join(str(row.get(h, "")) for h in headers) + " |\n"
                    final_answer = f"Here is the information you requested:\n\n{md_table}"
                
                # CASE B: It's a single item (like a booking confirmation) -> Format as a Bulleted List
                elif isinstance(data, dict):
                    if "error" in data or "detail" in data:
                        final_answer = f"**System Notice:**\n\n{data.get('detail', data.get('error', raw_output))}"
                    else:
                        md_list = "\n".join([f"* **{str(k).capitalize()}**: {v}" for k, v in data.items()])
                        final_answer = f"Success! Here are the details:\n\n{md_list}"
                
                # CASE C: It's simple data
                else:
                    final_answer = f"Done: {data}"
                    
            except json.JSONDecodeError:
                # If it's a plain text error or success message, just clean it up
                final_answer = f"**System Message:**\n\n{raw_output}"
        else:
            final_answer = "I've processed your request."

    tools_used = [m.name for m in messages if isinstance(m, ToolMessage) and hasattr(m, 'name')]

    # 3. FIX: Safely grab the latest question for the database log
    latest_question = request.messages[-1]["content"] if request.messages else ""

    log = data_models.AgentQueryLog(
        question=latest_question,
        tool_used=", ".join(tools_used) if tools_used else "none",
        answer=final_answer,
    )
    db.add(log)
    db.commit()

    return {"question": latest_question, "tools_used": tools_used, "answer": final_answer}


@app.get("/logs", tags=["Agent"], summary="See every question asked and which service handled it")
def get_logs(db: Session = Depends(get_db)):
    return db.query(data_models.AgentQueryLog).all()


@app.get("/health", tags=["System"], summary="Check the API is alive")
def health_check():
    return {"status": "ok"}