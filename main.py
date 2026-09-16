from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from config.session import engine, get_db
from dataaccess import data_models
from routers.models import AskRequest
from agent_graph import app_graph
from sqlalchemy.ext.declarative import declarative_base

data_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniDesk AI Router",
    description="One assistant that automatically routes your question to the correct service: "
                 "Todo, Food Ordering, Student Management, Movie Booking, or Expense Tracker.",
    version="1.0.0",
)

@app.post("/ask", tags=["Agent"], summary="Ask a question — the agent picks the right service automatically")
def ask(request: AskRequest, db: Session = Depends(get_db)):
    messages = []
    for msg in request.history:
        if msg["role"] == "user":
            messages.append(
                HumanMessage(content=msg["content"])
            )
        elif msg["role"] == "assistant":
            messages.append(
                AIMessage(content=msg["content"])
            )
    messages.append(
        HumanMessage(content=request.question)
    )
    result = app_graph.invoke({
        "messages": messages
    })

    messages = result["messages"]

    final_answer = messages[-1].content

    tools_used = [
        m.name
        for m in messages
        if isinstance(m, ToolMessage)
    ]
    log = data_models.AgentQueryLog(
        question=request.question,
        tool_used=", ".join(tools_used) if tools_used else "none",
        answer=final_answer,
    )

    db.add(log)
    db.commit()

    return {
        "question": request.question,
        "tools_used": tools_used,
        "answer": final_answer
    }

@app.get("/logs", tags=["Agent"], summary="See every question asked and which service handled it")
def get_logs(db: Session = Depends(get_db)):
    return db.query(data_models.AgentQueryLog).all()

@app.get("/health", tags=["System"], summary="Check the API is alive")
def health_check():
    return {"status": "ok"}