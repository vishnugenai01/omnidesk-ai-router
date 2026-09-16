import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Student Management AI Assistant")
st.caption("Ask questions related to students, courses, enrollment, marks, and results.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message["role"] == "assistant" and "tools_used" in message:
            st.caption(f"Routed to: {message['tools_used']}")

if question := st.chat_input("Ask about Student Management..."):

    previous_history = st.session_state.messages.copy()

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    try:
        response = requests.post(
            API_URL,
            json={
                "question": question,
                "history": previous_history
            },
            timeout=90
        )

        response.raise_for_status()

        data = response.json()

        answer = data.get(
            "answer",
            "I don't know about that request. I can only help with Student Management."
        )

        tools_used = ", ".join(
            data.get("tools_used", [])
        ) or "general chat"

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "tools_used": tools_used
        })

        with st.chat_message("assistant"):
            st.write(answer)
            st.caption(f"Routed to: {tools_used}")

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the FastAPI backend.")

    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")

    except requests.exceptions.HTTPError:
        st.error(f"API Error: {response.status_code}")

    except Exception as e:
        st.error(f"Error: {str(e)}")