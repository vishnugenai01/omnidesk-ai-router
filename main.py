from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from config.session import engine, get_db
from dataaccess import data_models
from routers.models import AskRequest
from agent_graph import app_graph


app = FastAPI(
    title="OmniDesk AI Router",
    description="One assistant that automatically routes your question to the correct service: "
                 "Todo, Food Ordering, Student Management, Movie Booking, or Expense Tracker.",
    version="1.0.0",
)

conversation_history: dict[str, list] = {}  

@app.post("/ask", tags=["Agent"], summary="Ask a question — the agent picks the right service automatically")
def ask(request: AskRequest, db: Session = Depends(get_db)):
    user_id = request.user_id
    
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    history = conversation_history[user_id]
    history.append(HumanMessage(content=request.question))
    result = app_graph.invoke({"messages": request.question})
    messages = result["messages"]
    conversation_history[user_id] = messages
    final_answer = messages[-1].content
    tools_used = [m.name for m in messages if isinstance(m, ToolMessage)]
    tools_used = list(dict.fromkeys(tools_used))

    log = data_models.AgentQueryLog(
        question=request.question,
        tool_used=", ".join(tools_used) if tools_used else "none",
        answer=final_answer,
    )
    db.add(log)
    db.commit()

    return {"question": request.question, "tools_used": tools_used, "answer": final_answer}

@app.get("/logs", tags=["Agent"], summary="See every question asked and which service handled it")
def get_logs(db: Session = Depends(get_db)):
    return db.query(data_models.AgentQueryLog).all()

@app.get("/health", tags=["System"], summary="Check the API is alive")
def health_check():
    return {"status": "ok"}
