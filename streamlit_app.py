import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.title("OmniDesk AI Assistant")

st.caption(
    "One chat box - currently live for Expense Tracking (more services coming soon)."
)


with st.sidebar:
    st.subheader("Try asking:")
    st.write("- Add a ₹400 expense for lunch today, category food")
    st.write("- What's my expense summary?")
    st.write("- Show me all my expenses this month")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if question := st.chat_input("Ask me anything..."):

    
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    # Display user message immediately

    with st.chat_message("user"):
        st.write(question)


    
    payload = {
        "question": question
    }


    try:

        response = requests.post(
            API_URL,
            json=payload,
            timeout=90
        )

        # If FastAPI returns 4xx/5xx
        response.raise_for_status()

        data = response.json()

        # Get answer
        answer = data.get(
            "answer",
            "No answer received from the backend."
        )

        # Get tools used
        tools_used = ", ".join(
            data.get("tools_used", [])
        ) or "general chat"


        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        with st.chat_message("assistant"):

            st.write(answer)

            st.caption(
                f"Routed to: {tools_used}"
            )


    except requests.exceptions.HTTPError as e:

        # Show FastAPI error response
        st.error(
            f"Backend returned an error: {e}"
        )

        try:
            st.json(response.json())
        except Exception:
            st.write(response.text)


    except requests.exceptions.RequestException as e:

        st.error(
            f"Failed to communicate with the backend: {e}"
        )


    except Exception as e:

        st.error(
            f"Unexpected error: {e}"
        )