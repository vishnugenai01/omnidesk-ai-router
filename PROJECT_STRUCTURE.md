# OmniDesk AI Router — Project Structure & Team Guide

This document captures the **current folder structure** of the repo, explains what each
folder is for, and defines how the 5-person team should extend it going forward so
everyone's work stays isolated by domain and merge conflicts stay rare.

Related doc: [OMNIDESK_LANGGRAPH_ROUTER_PLAN.md](OMNIDESK_LANGGRAPH_ROUTER_PLAN.md) (sprint plan, commit/PR format, per-person tool specs). This file documents the **actual layered structure** the repo has adopted, which organizes by *layer* (routers / business logic / data access / config) instead of the flat `tools/` layout the sprint plan originally sketched. The team-ownership mapping below carries over from that plan.

---

## 1. Current Folder Structure

```
omnidesk-ai-router/
├── .gitignore
├── README.md
├── OMNIDESK_LANGGRAPH_ROUTER_PLAN.md
├── PROJECT_STRUCTURE.md          # this file
├── requirements.txt
├── main.py                       # FastAPI entrypoint — empty, Sprint 3
├── streamlit_app.py              # Streamlit chat UI — empty, Sprint 4
│
├── config/                       # shared, cross-cutting configuration
│   ├── config.py                 # ✅ Groq LLM client setup (llm = ChatGroq(...))
│   └── session.py                # ⬜ empty — intended for env/session config
│
├── business_logic/                # domain rules — one file per service
│   ├── models.py                  # ⬜ empty — intended for shared domain/Pydantic models
│   ├── todo_logic.py              # ⬜ empty — Sai's domain
│   ├── food_logic.py              # ⬜ empty — Vishnu's domain
│   ├── student_logic.py           # ⬜ empty — Abhilash's domain
│   ├── movie_logic.py             # ⬜ empty — Jitendra's domain
│   └── expense_logic.py           # ⬜ empty — Nidhii's domain
│
├── dataaccess/                    # persistence layer
│   └── data_models.py             # ⬜ empty — intended for SQLAlchemy ORM models
│
└── routers/                       # API layer
    └── models.py                  # ⬜ empty — intended for FastAPI/Pydantic request-response schemas
```

`✅` = has real content today · `⬜` = file exists but is currently empty (placeholder only).

**Note the naming collision to fix early:** `business_logic/models.py`, `dataaccess/data_models.py`, and `routers/models.py` are three different files with overlapping names but different jobs (domain models vs. ORM models vs. API schemas). See §4 for a renaming suggestion before real code lands in them.

---

## 2. What Each Layer Is For

| Folder | Responsibility | Belongs here | Does NOT belong here |
|---|---|---|---|
| `config/` | Cross-cutting setup shared by the whole app | LLM client init, environment/secret loading, DB session factory, app-wide constants | Domain logic, API routes |
| `business_logic/` | The actual rules for each service domain (todo, food, student, movie, expense) | Functions that implement "what happens" for a domain — validation, calculations, calling an external live API | FastAPI decorators, SQLAlchemy `Column` definitions, Streamlit code |
| `dataaccess/` | Everything about talking to the database | SQLAlchemy models/tables, DB session helpers, queries | Business rules, HTTP handling |
| `routers/` | The FastAPI HTTP surface | `APIRouter` endpoint definitions, Pydantic request/response schemas | Business rules (call into `business_logic/` instead), raw SQL/ORM calls |
| *(root)* `main.py` | Wires everything together | `FastAPI()` app instance, `include_router(...)` calls, startup/logging config | Domain logic, DB models |
| *(root)* `streamlit_app.py` | Chat UI only | `st.*` calls, calling the deployed `/ask` endpoint over HTTP | Business rules, DB access |

**Request flow once built out:**
`streamlit_app.py` → HTTP → `routers/*` (validates via schema, calls) → `business_logic/*` (applies domain rules, calls live external API and/or) → `dataaccess/*` (reads/writes Postgres) → response bubbles back up.

The LangGraph agent sits **alongside** `routers/`: it also calls into `business_logic/` (wrapped as `@tool` functions), decides which domain(s) a question needs, and `main.py` exposes it via a dedicated `/ask` route.

---

## 3. Team Ownership Map

Same 5-person team as the sprint plan — mapped onto the current layered folders instead of a flat `tools/` folder:

| Member | Role | Owns (this layer) |
|---|---|---|
| **Abhilash** | Team Lead | `main.py`, `config/`, `dataaccess/`, agent/router graph, `student_logic.py`, code review on every PR |
| **Sai** | Tool Engineer | `business_logic/todo_logic.py` (+ its router file, its tool wrapper, its tests) |
| **Vishnu** | Tool Engineer | `business_logic/food_logic.py` (+ its router file, its tool wrapper, its tests) |
| **Jitendra** | Tool Engineer | `business_logic/movie_logic.py` (+ its router file, its tool wrapper, its tests) |
| **Nidhii** | Tool Engineer | `business_logic/expense_logic.py` (+ its router file, its tool wrapper, its tests) |

**Rule of thumb:** each teammate should be able to do their entire slice of work — logic, route, tool, test — by only touching files inside their own domain. Shared files (`main.py`, `config/*`, `dataaccess/*`) are lead-reviewed before merge since everyone's code depends on them.

---

## 4. Naming Conventions

- **Files:** `snake_case`, pattern `<domain>_<layer>.py` — e.g. `todo_logic.py`, `todo_router.py`, `todo_tool.py`, `test_todo.py`.
- **Functions:** `snake_case`, verb-first — e.g. `create_task()`, `get_expense_summary()`.
- **Classes / Pydantic models:** `PascalCase` — e.g. `TaskCreateRequest`, `ExpenseLog`.
- **One domain, one name across every layer** — the "todo" domain should read `todo_logic.py` / `todo_router.py` / `todo_tool.py` / `test_todo.py`, never `tasks_logic.py` in one layer and `todo_router.py` in another.
- **Resolve the current `models.py` collision** before filling these files in:
  - `dataaccess/data_models.py` → SQLAlchemy ORM tables (keep as-is, name is already clear).
  - `routers/models.py` → rename to `routers/schemas.py` (Pydantic request/response shapes — "schema" avoids clashing with the ORM "models").
  - `business_logic/models.py` → rename to `business_logic/domain_types.py` or fold into each `<domain>_logic.py` file directly if the shared types are small.

---

## 5. Recommended Structure Going Forward

Once Sprint 1 (tool-building) and Sprint 2 (router agent) start, grow the tree into this shape — same layers, with the missing pieces the plan calls for added in the right place:

```
omnidesk-ai-router/
├── main.py                        # FastAPI app + router registration
├── streamlit_app.py
├── requirements.txt
├── .env.example                   # committed template — never the real .env
│
├── config/
│   ├── __init__.py
│   ├── config.py                  # Groq LLM client
│   └── session.py                 # env vars, DB session factory
│
├── business_logic/
│   ├── __init__.py
│   ├── todo_logic.py              # Sai
│   ├── food_logic.py              # Vishnu
│   ├── student_logic.py           # Abhilash
│   ├── movie_logic.py             # Jitendra
│   └── expense_logic.py           # Nidhii
│
├── dataaccess/
│   ├── __init__.py
│   └── data_models.py             # SQLAlchemy ORM models + AgentQueryLog table
│
├── routers/
│   ├── __init__.py
│   ├── schemas.py                 # renamed from models.py — Pydantic request/response shapes
│   ├── todo_router.py
│   ├── food_router.py
│   ├── student_router.py
│   ├── movie_router.py
│   ├── expense_router.py
│   └── agent_router.py            # Abhilash — the /ask + /logs endpoints
│
├── tools/                         # LangChain @tool wrappers the agent calls
│   ├── __init__.py
│   ├── todo_tool.py                # thin wrapper around business_logic/todo_logic.py
│   ├── food_tool.py
│   ├── student_tool.py
│   ├── movie_tool.py
│   └── expense_tool.py
│
├── agent/
│   ├── __init__.py
│   └── agent_graph.py             # Abhilash — LangGraph StateGraph router
│
└── tests/
    ├── test_todo.py               # Sai
    ├── test_food.py               # Vishnu
    ├── test_student.py            # Abhilash
    ├── test_movie.py              # Jitendra
    └── test_expense.py            # Nidhii
```

**Why split `business_logic/` from `tools/`:** `business_logic/*_logic.py` holds the actual domain rules and the `requests` call to each teammate's live Render API. `tools/*_tool.py` is a thin `@tool`-decorated wrapper with the LLM-facing docstring, calling straight into the matching `_logic.py` function. This keeps the LLM-facing docstring (which needs careful wording per §5 of the sprint plan) separate from the logic itself, so either can change without touching the other, and the same logic function can be reused by both a router endpoint and an agent tool.

---

## 6. Suggestions

1. **Add `__init__.py` to every package now** (`config/`, `business_logic/`, `dataaccess/`, `routers/`) — without it, imports like `from business_logic.todo_logic import ...` can behave inconsistently across environments.
2. **Rename `routers/models.py` → `routers/schemas.py`** before it gets filled in, to stop it colliding conceptually with `dataaccess/data_models.py`.
3. **Split `routers/` into one file per domain** (`todo_router.py`, `food_router.py`, ...) instead of one shared file, mirroring `business_logic/` — this is what actually lets 5 people touch the API layer in parallel without merge conflicts.
4. **Add a `tools/` folder for the LangGraph tool wrappers**, kept separate from `business_logic/`, per §5 above — matches the sprint plan's tool-per-person Sprint 1 deliverable while keeping the layered structure you've already started.
5. **Add a `tests/` folder from day one**, one test file per domain, owned by the same person who owns that domain's logic — cheap to add now, expensive to retrofit later.
6. **Commit a `.env.example`** (keys only, no real values) so every teammate knows which environment variables to set without guessing; `.env` itself is already correctly gitignored.
7. **Each person stays inside their own domain's file set** across `business_logic/`, `routers/`, `tools/`, and `tests/` — shared files (`main.py`, `config/`, `dataaccess/`, `agent/`) go through Abhilash's review since every domain depends on them.
8. **Keep using the commit/PR format from the sprint plan** (`type(scope): summary`, PR template with "How I tested it") — it's what makes 5 people's parallel work reviewable.
