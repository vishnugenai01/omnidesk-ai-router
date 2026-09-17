# import streamlit as st
# import requests

# API_URL = "http://127.0.0.1:8000/ask"

# st.title("OmniDesk AI Assistant")

# st.caption(
#     "One chat box - currently live for Expense Tracking (more services coming soon)."
# )

# with st.sidebar:
#     st.subheader("Try asking:")

#     st.write("- Add a ₹400 expense for lunch today, category food")
#     st.write("- What's my expense summary?")
#     st.write("- Show me all my expenses this month")


# # Store chat history only for displaying in Streamlit
# if "messages" not in st.session_state:
#     st.session_state.messages = []


# # Display previous messages
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.write(msg["content"])


# # New question
# if question := st.chat_input("Ask me anything..."):

#     # Store user message locally
#     st.session_state.messages.append(
#         {
#             "role": "user",
#             "content": question
#         }
#     )

#     # Display user question
#     with st.chat_message("user"):
#         st.write(question)

#     # Send ONLY the question to FastAPI
#     payload = {
#         "question": question
#     }

#     try:
#         response = requests.post(
#             API_URL,
#             json=payload,
#             timeout=90
#         )

#         response.raise_for_status()

#         data = response.json()

#         answer = data["answer"]

#         tools_used = ", ".join(
#             data.get("tools_used", [])
#         ) or "general chat"

#         # Store assistant response locally
#         st.session_state.messages.append(
#             {
#                 "role": "assistant",
#                 "content": answer
#             }
#         )

#         # Display assistant response
#         with st.chat_message("assistant"):
#             st.write(answer)
#             st.caption(f"Routed to: {tools_used}")

#     except Exception as e:
#         st.error(
#             f"Failed to communicate with the backend: {e}"
#         )


import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000/ask"


st.title("OmniDesk AI Assistant")

st.caption(
    "One chat box - currently live for Expense Tracking (more services coming soon)."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.subheader("Try asking:")

    st.write("- Add a ₹400 expense for lunch today, category food")
    st.write("- What's my expense summary?")
    st.write("- Show me all my expenses this month")


# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# ============================================================
# NEW QUESTION
# ============================================================

if question := st.chat_input("Ask me anything..."):

    # --------------------------------------------------------
    # Store user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Display user message immediately

    with st.chat_message("user"):
        st.write(question)


    # --------------------------------------------------------
    # SEND COMPLETE CHAT HISTORY TO FASTAPI
    # --------------------------------------------------------

    payload = {
        "messages": st.session_state.messages
    }


    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=90
        )

        response.raise_for_status()

        data = response.json()

        answer = data["answer"]

        tools_used = ", ".join(
            data.get("tools_used", [])
        ) or "general chat"


        # ----------------------------------------------------
        # Store assistant response
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        # ----------------------------------------------------
        # Display assistant response
        # ----------------------------------------------------

        with st.chat_message("assistant"):

            st.write(answer)

            st.caption(
                f"Routed to: {tools_used}"
            )


    except Exception as e:

        st.error(
            f"Failed to communicate with the backend: {e}"
        )