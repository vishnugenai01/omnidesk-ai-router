# OmniDesk AI Router — LangGraph Multi-Service Agent
## End-to-End Team Project Plan (Sprint-wise, Git-Collaborative)

---

## 1. What we're building

One chatbot. Five already-live services. The user asks a plain-English question, and a **LangGraph agent decides on its own which of your five real, deployed FastAPI APIs** (Todo, Food Ordering, Student Management, Movie Booking, Expense Tracker) can answer it — then actually calls that live API and replies with a real answer, not a guess.

```
                    "Book 2 tickets for Inception, and add a ₹400 expense for it"
                                          │
                                          ▼
                          ┌───────────────────────────┐
                          │   LangGraph Router Agent    │
                          │  (StateGraph: agent ⇄ tools)│
                          └──────────────┬──────────────┘
                                          │  decides which tool(s) to call
              ┌──────────────┬───────────┼───────────┬──────────────┐
              ▼              ▼           ▼           ▼              ▼
        ┌──────────┐  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ todo_tool │  │food_tool │ │student_  │ │movie_tool│ │expense_  │
        │  (Sai)    │  │(Vishnu)  │ │tool      │ │(Jitendra)│ │tool      │
        │           │  │          │ │(Abilasha)│ │          │ │(Nidhii)  │
        └─────┬────┘  └─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘
              │             │            │            │            │
              ▼             ▼            ▼            ▼            ▼
     todo-api-sai   food-order-api  student-api  movie-booking  expense-tracker
     .onrender.com  -vishnu         -abilasha    -api-jitendra  -api-nidhii
                     .onrender.com  .onrender.com .onrender.com .onrender.com
                                          │
                                          ▼
                          Every question + which tool(s) fired + the
                          final answer is logged to PostgreSQL
                                          │
                                          ▼
                    FastAPI `/ask` endpoint (Swagger docs)  +  Streamlit chatbot UI
```

Each of your five already-deployed FastAPI projects becomes a **tool** the agent can call — nobody rebuilds their API, they just wrap the one they already own and already understand best.

---

## 2. Team & Role Assignment

| Name | Role | Owns | Sprint |
|---|---|---|---|
| **Abilasha** | Team Lead | Repo setup, DB logging, LangGraph router/agent, FastAPI + Swagger, Streamlit core, integration, code review | Sprint 0, 2, 3, 4, 5 |
| Sai | Tool Engineer | `tools/todo_tool.py` (wraps his live Todo API) | Sprint 1 |
| Vishnu | Tool Engineer | `tools/food_tool.py` (wraps his live Food Ordering API) | Sprint 1 |
| Jitendra | Tool Engineer | `tools/movie_tool.py` (wraps his live Movie Booking API) | Sprint 1 |
| Nidhii | Tool Engineer | `tools/expense_tool.py` (wraps her live Expense Tracker API) | Sprint 1 |
| Abilasha | Tool Engineer (in addition to lead) | `tools/student_tool.py` (wraps her own live Student API) | Sprint 1 |

**Important difference from your last project:** last time (the content pipeline), everyone had to build in strict one-after-another order because each stage needed the previous stage's real output to test against. **This project has no such chain** — each of the five tools calls a completely independent live API, so **Sai, Vishnu, Jitendra, Nidhii, and Abilasha can all build their tool in Sprint 1 at the same time.** Nobody waits on anybody else this time — that's the whole point of a router/tool pattern instead of a pipeline, and it's a good thing for the team to notice and understand as a design difference.

---

## 3. Sprint Plan

| Sprint | Owner(s) | What happens | Can start when… | Deliverable |
|---|---|---|---|---|
| **Sprint 0** | Abilasha | Repo, Postgres logging table + pgAdmin, shared Groq config, interface contract | Immediately | Repo pushed, everyone can clone |
| **Sprint 1** | Sai, Vishnu, Jitendra, Nidhii, Abilasha — **all in parallel** | Each person wraps their own live API as one LangGraph tool | Sprint 0 is pushed | All 5 tool files merged into `main` |
| **Sprint 2** | Abilasha | Build the LangGraph router/agent graph using all 5 merged tools | All 5 Sprint 1 PRs merged | Agent correctly picks the right tool for a test question in each domain |
| **Sprint 3** | Abilasha | FastAPI wrapper + Swagger docs + Postgres query logging | Sprint 2 done | `/ask` endpoint working in Swagger UI |
| **Sprint 4** | Abilasha (core UI) + all 4 members (one example question each) | Streamlit chatbot | Sprint 3 done | Working chat UI hitting the FastAPI backend |
| **Sprint 5** | Whole team | End-to-end testing across all 5 domains, verify logs in pgAdmin, deploy | Sprint 4 done | Live, shareable demo |

---

## 4. Git Workflow — Commit Message Format & PR Template

**Everyone uses this exact commit format, no exceptions:**

```
<type>(<scope>): <short summary in present tense>
```

`type` is one of: `feat` (new functionality), `fix` (bug fix), `docs` (documentation only), `chore` (setup/config), `test` (test scripts).
`scope` is your module name.

Examples:
```
feat(sai-todo-tool): add LangGraph tool wrapping the Todo API
feat(router): add StateGraph with conditional tool routing
feat(swagger-api): add /ask and /logs endpoints
fix(expense-tool): handle missing budget field without crashing
docs(readme): add live API URLs for all 5 services
chore(setup): add requirements.txt, .env.example, .gitignore
```

**Every Pull Request uses this template** (paste it into the PR description box on GitHub):

```markdown
## What this PR does
<1-2 sentences>

## Sprint / Module
Sprint <number> — <module name>

## Changes
- <bullet>
- <bullet>

## How I tested it
<e.g. "Ran test_todo_tool.py locally against the live Render URL, confirmed it returns real task data.">

## Proof
<paste the printed output, or a Swagger screenshot>
```

Abilasha reviews every PR against this template before merging — if "How I tested it" is empty, she sends it back.

---

## 5. The Interface Contract

Each tool is a single Python function decorated with `@tool` from `langchain_core.tools`. The **docstring is not a comment — the LLM reads it** to decide which tool to call and what arguments to pass, so it must be precise.

```python
@tool
def <name>_tool(action: str, ...other params with defaults...) -> str:
    """
    Use this tool for anything about <DOMAIN>: <list what it can do>.
    action: "<option1>" | "<option2>" | "<option3>"
    <param>: <what it's for, and when it's required>
    """
    # calls the live Render URL with requests, returns the response as a string
```

Every tool returns a **string** (the raw API response text is fine) — the agent reads that string to compose its final natural-language answer.

---

## 6. Tech Stack

```
langgraph
langchain
langchain-groq
langchain-core
fastapi
uvicorn
streamlit
requests
sqlalchemy
psycopg2-binary
python-dotenv
pydantic
```

**LLM: Groq, free, no credit card** — sign up individually at https://console.groq.com, model `llama-3.1-8b-instant` (supports tool-calling, which this project depends on).

---

## SPRINT 0 — Abilasha — Project Setup

### 0.1 Create the shared repository

1. GitHub → **New Repository** → `omnidesk-ai-router` → Public → Add README → Create.
2. **Settings → Collaborators** → add Sai, Vishnu, Jitendra, Nidhii.
3. Clone it and set up the folder structure:

```
omnidesk-ai-router/
├── main.py                  # Abilasha — FastAPI + Swagger (Sprint 3)
├── agent_graph.py           # Abilasha — LangGraph router (Sprint 2)
├── config.py                # Abilasha — shared Groq LLM setup
├── database.py               # Abilasha — Postgres connection
├── models.py                 # Abilasha — query log table
├── tools/
│   ├── __init__.py
│   ├── todo_tool.py          # Sai
│   ├── food_tool.py          # Vishnu
│   ├── student_tool.py       # Abilasha
│   ├── movie_tool.py         # Jitendra
│   └── expense_tool.py       # Nidhii
├── streamlit_app.py          # Abilasha + team (Sprint 4)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install langgraph langchain langchain-groq langchain-core fastapi uvicorn streamlit requests sqlalchemy psycopg2-binary python-dotenv pydantic
pip freeze > requirements.txt
```

### 0.2 Write down the 5 live URLs in `README.md`

```
Sai      — Todo API             — https://todo-api-sai.onrender.com
Vishnu   — Food Ordering API    — https://food-order-api-vishnu.onrender.com
Abilasha — Student API          — https://student-api-abilasha.onrender.com
Jitendra — Movie Booking API    — https://movie-booking-api-jitendra.onrender.com
Nidhii   — Expense Tracker API  — https://expense-tracker-api-nidhii.onrender.com
```

> These free Render services spin down after 15 minutes idle — the first call after a while can take up to a minute to "wake up." Every tool below handles this with a 60-second timeout instead of failing instantly.

### 0.3 `config.py`

```python
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)
```

### 0.4 `database.py`

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/omnidesk_db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 0.5 `models.py`

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class AgentQueryLog(Base):
    __tablename__ = "agent_query_logs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    tool_used = Column(String)        # which tool(s) the agent picked
    answer = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### 0.6 Install PostgreSQL + pgAdmin locally, and a shared Render database

Same pattern as your earlier FastAPI + Postgres project:

1. Install PostgreSQL + pgAdmin from https://www.pgadmin.org/download/, create a local database `omnidesk_db`.
2. On https://render.com, **New + → PostgreSQL** → name `omnidesk-db` → free plan → create → copy the **Internal Database URL** (for later deployment) and the **External** connection details (for pgAdmin, so the whole team can see the same logged questions).
3. Register both connections in pgAdmin.

### 0.7 `.env.example` and `.gitignore`

```
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://user:password@host/dbname
```

```
venv/
__pycache__/
.env
```

### 0.8 Push

```bash
git add .
git commit -m "chore(setup): project structure, Postgres schema, shared Groq config"
git push origin main
```

**Tell the whole team Sprint 1 is open — everyone starts together.**

---

## SPRINT 1 — Sai, Vishnu, Jitendra, Nidhii, Abilasha — Tool Wrapping (ALL IN PARALLEL)

**Everyone follows the same setup pattern below, then builds only their own file.**

```bash
git clone https://github.com/ABILASHA_USERNAME/omnidesk-ai-router.git
cd omnidesk-ai-router
git checkout -b feature/<your-tool-name>       # e.g. feature/todo-tool
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Create your own `.env` with your own Groq API key (never commit it).

### 1.1 Sai — `tools/todo_tool.py`

```python
from langchain_core.tools import tool
import requests

BASE_URL = "https://todo-api-sai.onrender.com"

@tool
def todo_tool(action: str, title: str = "", priority: str = "medium", task_id: int = None) -> str:
    """
    Use this tool for anything about TASKS or TO-DO items: creating a task, listing tasks,
    marking a task complete, or deleting a task.

    action: "create" | "list" | "complete" | "delete"
    title: task title — required when action is "create"
    priority: "low" | "medium" | "high" — optional, used when action is "create"
    task_id: the task's ID — required when action is "complete" or "delete"
    """
    try:
        if action == "create":
            res = requests.post(f"{BASE_URL}/tasks", json={"title": title, "priority": priority}, timeout=60)
        elif action == "list":
            res = requests.get(f"{BASE_URL}/tasks", timeout=60)
        elif action == "complete":
            res = requests.patch(f"{BASE_URL}/tasks/{task_id}/complete", timeout=60)
        elif action == "delete":
            res = requests.delete(f"{BASE_URL}/tasks/{task_id}", timeout=60)
        else:
            return "Unknown action for todo_tool. Use create, list, complete, or delete."
        return res.text
    except requests.exceptions.RequestException as e:
        return f"Todo service is waking up or unreachable, try again in a moment. ({e})"
```

### 1.2 Vishnu — `tools/food_tool.py`

```python
from langchain_core.tools import tool
import requests

BASE_URL = "https://food-order-api-vishnu.onrender.com"

@tool
def food_tool(action: str, name: str = "", price: float = 0.0, item_id: int = None, quantity: int = 1) -> str:
    """
    Use this tool for anything about FOOD ORDERING: viewing the menu, adding a menu item,
    or placing a food order.

    action: "menu" | "add_item" | "order"
    name: dish name — required when action is "add_item"
    price: dish price — required when action is "add_item"
    item_id: the menu item's ID — required when action is "order"
    quantity: number of items — optional, used when action is "order"
    """
    try:
        if action == "menu":
            res = requests.get(f"{BASE_URL}/menu", timeout=60)
        elif action == "add_item":
            res = requests.post(f"{BASE_URL}/menu", json={"name": name, "price": price}, timeout=60)
        elif action == "order":
            res = requests.post(f"{BASE_URL}/orders", json={"item_id": item_id, "quantity": quantity}, timeout=60)
        else:
            return "Unknown action for food_tool. Use menu, add_item, or order."
        return res.text
    except requests.exceptions.RequestException as e:
        return f"Food ordering service is waking up or unreachable, try again in a moment. ({e})"
```

### 1.3 Abilasha — `tools/student_tool.py`

```python
from langchain_core.tools import tool
import requests

BASE_URL = "https://student-api-abilasha.onrender.com"

@tool
def student_tool(action: str, name: str = "", email: str = "", department: str = "CSE",
                  student_id: int = None, course_id: int = None) -> str:
    """
    Use this tool for anything about STUDENTS: registering a student, listing students,
    or enrolling a student in a course.

    action: "register" | "list" | "enroll"
    name: student's name — required when action is "register"
    email: student's email — required when action is "register"
    department: student's department — optional, used when action is "register"
    student_id: the student's ID — required when action is "enroll"
    course_id: the course's ID — required when action is "enroll"
    """
    try:
        if action == "register":
            res = requests.post(f"{BASE_URL}/students", json={"name": name, "email": email, "department": department}, timeout=60)
        elif action == "list":
            res = requests.get(f"{BASE_URL}/students", timeout=60)
        elif action == "enroll":
            res = requests.post(f"{BASE_URL}/students/{student_id}/enroll/{course_id}", timeout=60)
        else:
            return "Unknown action for student_tool. Use register, list, or enroll."
        return res.text
    except requests.exceptions.RequestException as e:
        return f"Student service is waking up or unreachable, try again in a moment. ({e})"
```

### 1.4 Jitendra — `tools/movie_tool.py`

```python
from langchain_core.tools import tool
import requests

BASE_URL = "https://movie-booking-api-jitendra.onrender.com"

@tool
def movie_tool(action: str, title: str = "", language: str = "Telugu", movie_id: int = None, seats: int = 1) -> str:
    """
    Use this tool for anything about MOVIES or TICKET BOOKING: listing movies, adding a movie,
    or booking tickets.

    action: "list" | "add_movie" | "book"
    title: movie title — required when action is "add_movie"
    language: movie language — optional, used when action is "add_movie"
    movie_id: the movie's ID — required when action is "book"
    seats: number of seats to book — optional, used when action is "book"
    """
    try:
        if action == "list":
            res = requests.get(f"{BASE_URL}/movies", timeout=60)
        elif action == "add_movie":
            res = requests.post(f"{BASE_URL}/movies", json={"title": title, "language": language}, timeout=60)
        elif action == "book":
            res = requests.post(f"{BASE_URL}/bookings", json={"movie_id": movie_id, "seats": seats}, timeout=60)
        else:
            return "Unknown action for movie_tool. Use list, add_movie, or book."
        return res.text
    except requests.exceptions.RequestException as e:
        return f"Movie booking service is waking up or unreachable, try again in a moment. ({e})"
```

### 1.5 Nidhii — `tools/expense_tool.py`

```python
from langchain_core.tools import tool
import requests

BASE_URL = "https://expense-tracker-api-nidhii.onrender.com"

@tool
def expense_tool(action: str, title: str = "", amount: float = 0.0, category: str = "food") -> str:
    """
    Use this tool for anything about EXPENSES or SPENDING: adding an expense, listing expenses,
    or getting a spending summary.

    action: "add" | "list" | "summary"
    title: expense title — required when action is "add"
    amount: expense amount — required when action is "add"
    category: expense category — optional, used when action is "add"
    """
    try:
        if action == "add":
            res = requests.post(f"{BASE_URL}/expenses", json={"title": title, "amount": amount, "category": category}, timeout=60)
        elif action == "list":
            res = requests.get(f"{BASE_URL}/expenses", timeout=60)
        elif action == "summary":
            res = requests.get(f"{BASE_URL}/expenses/summary", timeout=60)
        else:
            return "Unknown action for expense_tool. Use add, list, or summary."
        return res.text
    except requests.exceptions.RequestException as e:
        return f"Expense service is waking up or unreachable, try again in a moment. ({e})"
```

### 1.6 Everyone: test your tool standalone before opening a PR

```python
# test_my_tool.py — do not commit
from tools.todo_tool import todo_tool     # swap for your own tool
print(todo_tool.invoke({"action": "list"}))
```

### 1.7 Everyone: commit and open a PR (using the format from Section 4)

```bash
git add tools/todo_tool.py
git commit -m "feat(sai-todo-tool): add LangGraph tool wrapping the Todo API"
git push origin feature/todo-tool
```

Open a PR into `main` using the template from Section 4. Abilasha reviews and merges all 5 — since they're independent, she can merge them in any order as each one is ready.

### Checklist (per person)
- [ ] Own `.env` created with own Groq key (not committed)
- [ ] Tool's docstring clearly states what it does and when each parameter is needed
- [ ] Tested standalone against the real live URL, not a mock
- [ ] Commit message and PR follow the required format
- [ ] PR merged into `main`

---

## SPRINT 2 — Abilasha — The LangGraph Router Agent

**Start only after all 5 Sprint 1 PRs are merged.**

### 2.1 Get the latest code

```bash
git checkout main
git pull origin main
git checkout -b feature/router-graph
```

### 2.2 Build `agent_graph.py`

This is the actual LangGraph part — a graph with two nodes (`agent`, `tools`) and a conditional edge that loops between them until the LLM has a final answer. This loop is what a plain LangChain chain cannot do — it's the reason this project uses LangGraph.

```python
from typing import TypedDict, Annotated
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from config import llm

from tools.todo_tool import todo_tool
from tools.food_tool import food_tool
from tools.student_tool import student_tool
from tools.movie_tool import movie_tool
from tools.expense_tool import expense_tool

tools = [todo_tool, food_tool, student_tool, movie_tool, expense_tool]
llm_with_tools = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

def call_model(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

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
```

**How this decides which of the 5 "databases" to use:** `llm.bind_tools(tools)` gives the model all 5 tool docstrings at once. When you call `app_graph.invoke(...)`, the `agent` node asks the LLM "given this question and these 5 tools, what should happen next?" — the LLM picks the matching tool(s) based on the docstrings, `should_continue` routes to the `tools` node to actually execute it, and the graph loops back to `agent` so the LLM can either call another tool (for multi-part questions) or give a final answer. That loop, drawn as `agent → tools → agent → ... → END`, is the graph.

### 2.3 Test it directly

```python
# test_router.py — do not commit
from agent_graph import app_graph
from langchain_core.messages import HumanMessage

result = app_graph.invoke({"messages": [HumanMessage(content="Show me the food menu")]})
print(result["messages"][-1].content)

result2 = app_graph.invoke({"messages": [HumanMessage(content="What's my expense summary?")]})
print(result2["messages"][-1].content)
```

Try at least one question per domain (todo, food, student, movie, expense) and confirm each one calls the correct tool.

### 2.4 Commit and PR

```bash
git add agent_graph.py
git commit -m "feat(router): add StateGraph with conditional tool routing across all 5 services"
git push origin feature/router-graph
```

### Checklist
- [ ] All 5 tools imported and bound to the LLM
- [ ] Tested at least one question per domain — each routed correctly
- [ ] Tested one multi-part question touching 2 domains
- [ ] PR opened and merged into `main`

---

## SPRINT 3 — Abilasha — FastAPI + Swagger + Postgres Logging

**Start only after Sprint 2 is merged.**

### 3.1 Build `main.py`

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, ToolMessage

from database import engine, get_db, Base
import models
from agent_graph import app_graph

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniDesk AI Router",
    description="One assistant that automatically routes your question to the correct service: "
                 "Todo, Food Ordering, Student Management, Movie Booking, or Expense Tracker.",
    version="1.0.0",
)

class AskRequest(BaseModel):
    question: str

@app.post("/ask", tags=["Agent"], summary="Ask a question — the agent picks the right service automatically")
def ask(request: AskRequest, db: Session = Depends(get_db)):
    result = app_graph.invoke({"messages": [HumanMessage(content=request.question)]})
    messages = result["messages"]
    final_answer = messages[-1].content
    tools_used = [m.name for m in messages if isinstance(m, ToolMessage)]

    log = models.AgentQueryLog(
        question=request.question,
        tool_used=", ".join(tools_used) if tools_used else "none",
        answer=final_answer,
    )
    db.add(log)
    db.commit()

    return {"question": request.question, "tools_used": tools_used, "answer": final_answer}

@app.get("/logs", tags=["Agent"], summary="See every question asked and which service handled it")
def get_logs(db: Session = Depends(get_db)):
    return db.query(models.AgentQueryLog).all()

@app.get("/health", tags=["System"], summary="Check the API is alive")
def health_check():
    return {"status": "ok"}
```

### 3.2 Run it and check Swagger

```bash
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/docs**. Try **POST /ask** with a question from each domain, then check **GET /logs** to confirm it's saving every question and which tool answered it.

### 3.3 Verify in pgAdmin

Open pgAdmin, connect to `omnidesk_db`, expand **Tables → agent_query_logs → View/Edit Data → All Rows** — you should see every question you just asked in Swagger, with the correct `tool_used` column filled in.

### 3.4 Commit and PR

```bash
git add main.py
git commit -m "feat(swagger-api): add /ask and /logs endpoints with Postgres logging"
git push origin feature/swagger-api
```

### Checklist
- [ ] `/ask` returns a real answer for a question in each of the 5 domains
- [ ] `tools_used` correctly reflects which tool(s) fired
- [ ] `/logs` shows the full history
- [ ] Data confirmed visible in pgAdmin
- [ ] PR merged into `main`

---

## SPRINT 4 — Streamlit Chatbot (Abilasha builds core, everyone adds their own example)

**Start only after Sprint 3 is merged.**

### 4.1 Abilasha builds `streamlit_app.py`

```python
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"   # switch to the deployed Render URL once live

st.title("OmniDesk AI Assistant")
st.caption("One chat box, five services — ask about tasks, food orders, students, movie bookings, or expenses.")

with st.sidebar:
    st.subheader("Try asking:")
    st.write("- Add a task to buy groceries")           # Sai
    st.write("- Show me the food menu")                  # Vishnu
    st.write("- Register a new student named Priya")     # Abilasha
    st.write("- Book 2 tickets for Inception")            # Jitendra
    st.write("- What's my expense summary?")              # Nidhii

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    response = requests.post(API_URL, json={"question": question}, timeout=90)
    data = response.json()
    answer = data["answer"]
    tools_used = ", ".join(data["tools_used"]) or "general chat"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(f"{answer}\n\n_Routed to: {tools_used}_")
```

### 4.2 Each of the 4 members adds their own sidebar example question

Small, fast, real team-collaboration task: Sai, Vishnu, Jitendra, and Nidhii each open a tiny PR that adds one better example question for their own domain to the sidebar list (Abilasha's placeholders above are a starting point, not final). This is a good first real PR for anyone nervous about touching shared code — small, low-risk, and everyone's name ends up in the file.

```bash
git checkout main
git pull origin main
git checkout -b feature/streamlit-examples-sai   # example for Sai
# edit the sidebar list in streamlit_app.py, add/improve your one line
git add streamlit_app.py
git commit -m "feat(streamlit-ui): add example question for todo domain"
git push origin feature/streamlit-examples-sai
```

### 4.3 Run it

```bash
streamlit run streamlit_app.py
```

### Checklist
- [ ] Chat UI sends questions to `/ask` and displays the answer
- [ ] Shows which tool was used under each answer
- [ ] All 4 members have contributed their own example question
- [ ] PRs merged into `main`

---

## SPRINT 5 — Whole Team — Testing & Deployment

1. As a team, ask at least 2 questions per domain plus 1 multi-domain question through the Streamlit UI. Confirm every answer is correct and every row appears in pgAdmin.
2. Each person should be able to explain what happens to their question from the moment it's typed to the moment the answer appears — not just their own tool's part.
3. **Deploy the backend to Render** — same pattern as before: Web Service pointing at `omnidesk-ai-router`, build command `pip install -r requirements.txt`, start command `uvicorn main:app --host 0.0.0.0 --port $PORT`, environment variables `GROQ_API_KEY` and `DATABASE_URL` (the Render Postgres Internal URL).
4. **Deploy the Streamlit UI to Streamlit Community Cloud** (share.streamlit.io) — connect the same GitHub repo, point it at `streamlit_app.py`, and update `API_URL` in the app to your live Render `/ask` URL before deploying. Check Streamlit's current free-tier limits on their site when you deploy, since they can change.

---

## Final Definition of Done

- [ ] Abilasha: repo, Postgres logging, shared config set up (Sprint 0)
- [ ] Sai, Vishnu, Jitendra, Nidhii, Abilasha: all 5 tools built in parallel and merged (Sprint 1)
- [ ] Abilasha: LangGraph router correctly picks the right tool per domain, and handles multi-domain questions (Sprint 2)
- [ ] Abilasha: `/ask` and `/logs` working in Swagger with Postgres logging (Sprint 3)
- [ ] Abilasha + team: Streamlit chatbot working, every member's example question included (Sprint 4)
- [ ] Whole team: live demo tested together, logs verified in pgAdmin, deployed live (Sprint 5)
- [ ] Every commit follows the `type(scope): summary` format
- [ ] Every PR follows the required template
- [ ] Everyone can explain the full question-to-answer flow, not just their own tool
