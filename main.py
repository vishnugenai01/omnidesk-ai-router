from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from langchain_core.messages import HumanMessage, ToolMessage

from config.session import engine, get_db
from dataaccess import data_models
from agent_graph import app_graph

data_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniDesk AI Router",
    description=(
        "One assistant that automatically routes your question "
        "to the correct service."
    ),
    version="1.0.0",
)

class AskRequest(BaseModel):
    question: str


@app.post(
    "/ask",
    tags=["Agent"],
    summary="Ask a question - the agent picks the correct service"
)
def ask(
    request: AskRequest,
    db: Session = Depends(get_db)
):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    print("\n========================================")
    print("USER QUESTION:")
    print(question)
    print("========================================\n")


    lc_messages = [
        HumanMessage(content=question)
    ]


    try:

        result = app_graph.invoke(
            {
                "messages": lc_messages
            }
        )

        messages = result["messages"]


        final_answer = messages[-1].content


        tools_used = [
            m.name
            for m in messages
            if isinstance(m, ToolMessage)
            and hasattr(m, "name")
        ]


        print("\n========================================")
        print("TOOLS USED:")
        print(tools_used)
        print("========================================")

        print("\nFINAL ANSWER:")
        print(final_answer)

        print("\n========================================\n")


    except Exception as e:

        print("\n========================================")
        print("AGENT GRAPH ERROR:")
        print(repr(e))
        print("========================================\n")


        try:

            log = data_models.AgentQueryLog(
                question=question,
                tool_used="error",
                answer=f"Agent error: {repr(e)}"
            )

            db.add(log)
            db.commit()

        except Exception as log_error:

            print("LOG SAVE ERROR:")
            print(repr(log_error))


        raise HTTPException(
            status_code=502,
            detail=f"Agent failed to respond: {repr(e)}"
        )


    try:

        log = data_models.AgentQueryLog(
            question=question,
            tool_used=", ".join(tools_used)
            if tools_used
            else "none",
            answer=final_answer
        )

        db.add(log)
        db.commit()

    except Exception as log_error:

        print("LOG SAVE ERROR:")
        print(repr(log_error))

        db.rollback()

    return {
        "question": question,
        "tools_used": tools_used,
        "answer": final_answer
    }


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


@app.get(
    "/health",
    tags=["System"],
    summary="Check if the API is alive"
)
def health_check():

    return {
        "status": "ok"
    }