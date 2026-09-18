import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"
ASK_URL = f"{API_BASE}/ask"
HEALTH_URL = f"{API_BASE}/health"

SERVICES = [
    ("📝", "Todo"),
    ("🍔", "Food"),
    ("🎓", "Student"),
    ("🎬", "Movies"),
    ("💰", "Expense"),
]

SUGGESTIONS = [
    ("🍛", "I want Kadai Paneer"),
    ("📦", "Show me my orders"),
    ("💸", "Add a ₹400 expense for lunch today, category food"),
    ("✅", "Add a task: finish the report, high priority"),
]

st.set_page_config(
    page_title="OmniDesk AI Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# STYLE
# ------------------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        max-width: 880px;
        padding-top: 1.5rem;
        padding-bottom: 6rem;
    }

    .omni-hero {
        background: linear-gradient(135deg, #6C5CE7 0%, #8E7CFF 45%, #4A90E2 100%);
        border-radius: 20px;
        padding: 2rem 2rem 1.6rem 2rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 10px 30px rgba(108, 92, 231, 0.25);
    }
    .omni-hero h1 {
        color: #ffffff;
        font-size: 2rem;
        margin: 0 0 0.35rem 0;
        font-weight: 800;
    }
    .omni-hero p {
        color: rgba(255,255,255,0.88);
        font-size: 0.98rem;
        margin: 0 0 1rem 0;
    }
    .service-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .service-chip {
        background: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.35);
        color: #ffffff;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        backdrop-filter: blur(4px);
    }

    .route-badge {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        background: rgba(108, 92, 231, 0.12);
        color: #6C5CE7;
        border: 1px solid rgba(108, 92, 231, 0.35);
        font-size: 0.78rem;
        font-weight: 600;
    }

    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 0.4rem 0.2rem;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        width: 100%;
        box-sizing: border-box;
    }
    .status-online {
        background: rgba(34, 197, 94, 0.12);
        color: #16a34a;
        border: 1px solid rgba(34, 197, 94, 0.35);
    }
    .status-offline {
        background: rgba(239, 68, 68, 0.12);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }

    .empty-state {
        text-align: center;
        padding: 2.5rem 1rem;
        opacity: 0.75;
    }
    .empty-state .emoji {
        font-size: 2.4rem;
        margin-bottom: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# HERO HEADER
# ------------------------------------------------------------

chips_html = "".join(
    f'<span class="service-chip">{icon} {name}</span>' for icon, name in SERVICES
)

st.markdown(
    f"""
    <div class="omni-hero">
        <h1>🧭 OmniDesk AI Assistant</h1>
        <p>One chat box, five services — I automatically route your question
        to the right one.</p>
        <div class="service-row">{chips_html}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# SESSION STATE
# ------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


def check_backend_health() -> bool:
    try:
        res = requests.get(HEALTH_URL, timeout=3)
        return res.ok
    except requests.exceptions.RequestException:
        return False


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

with st.sidebar:
    st.markdown("### 👤 Your profile")
    USER_ID = st.text_input("User ID", value="1", help="Used to keep your conversation and records tied to you.")

    backend_online = check_backend_health()
    status_class = "status-online" if backend_online else "status-offline"
    status_text = "🟢 Backend online" if backend_online else "🔴 Backend unreachable"
    st.markdown(f'<div class="status-pill {status_class}">{status_text}</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("### 💡 Try asking")
    for icon, text in SUGGESTIONS:
        if st.button(f"{icon}  {text}", key=f"suggestion_{text}", use_container_width=True):
            st.session_state.pending_prompt = text

    st.divider()

    if st.button("🗑️  Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("OmniDesk routes each question to Todo, Food, Student, Movie, or Expense tools automatically.")

if not USER_ID:
    st.warning("Please enter your User ID to start chatting.")
    st.stop()

# ------------------------------------------------------------
# CHAT HISTORY
# ------------------------------------------------------------

if not st.session_state.messages:
    st.markdown(
        """
        <div class="empty-state">
            <div class="emoji">💬</div>
            <div><strong>No messages yet</strong></div>
            <div>Ask about a task, a food order, a student, a movie booking, or an expense.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🧭"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("routed_to"):
            st.markdown(f'<span class="route-badge">🔀 Routed to: {msg["routed_to"]}</span>', unsafe_allow_html=True)


def handle_question(question: str) -> None:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🧭"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    ASK_URL,
                    json={"user_id": USER_ID, "question": question},
                    timeout=120,
                )

                if response.status_code != 200:
                    st.error(f"Backend returned HTTP {response.status_code}")
                    st.code(response.text)
                    return

                try:
                    data = response.json()
                except requests.exceptions.JSONDecodeError:
                    st.error("Backend returned invalid JSON.")
                    st.code(response.text)
                    return

                answer = data.get("answer")
                tools_used = data.get("tools_used", [])
                routed_to = ", ".join(tools_used) if tools_used else "general chat"

                if not answer:
                    st.error("Unable to process at the moment")
                    return

                st.markdown(answer)
                st.markdown(f'<span class="route-badge">🔀 Routed to: {routed_to}</span>', unsafe_allow_html=True)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "routed_to": routed_to}
                )

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the FastAPI server. Is `uvicorn main:app` running?")
            except requests.exceptions.Timeout:
                st.error("The request timed out.")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {str(e)}")


# ------------------------------------------------------------
# INPUT HANDLING (chat box or a clicked suggestion)
# ------------------------------------------------------------

typed_question = st.chat_input("Ask me anything...")

if st.session_state.pending_prompt:
    handle_question(st.session_state.pending_prompt)
    st.session_state.pending_prompt = None
elif typed_question:
    handle_question(typed_question)
