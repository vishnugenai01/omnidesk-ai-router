import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000/ask"


# PAGE

st.set_page_config(
    page_title="OmniDesk AI Assistant",
    page_icon="🤖"
)

st.title("OmniDesk AI Assistant")

st.caption(
    "One chat box, five services — ask about tasks, food orders, "
    "students, movie bookings, or expenses."
)

# SIDEBAR

with st.sidebar:

    st.subheader("User")

    USER_ID = st.text_input(
        "Enter your User ID",
        value="1"
    )

    st.divider()

    st.subheader("Try asking:")

    st.write("- I want Kadai Paneer")
    st.write("- Show me my orders")
    st.write("- Show me the food menu")
    st.write("- Place an order for Chicken Fried Rice")
    st.write("- What is my order status?")

# USER ID

if not USER_ID:

    st.warning(
        "Please enter your User ID to start chatting."
    )

    st.stop()

# CHAT HISTORY - STREAMLIT DISPLAY

if "messages" not in st.session_state:

    st.session_state.messages = []


for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# CHAT INPUT

if question := st.chat_input("Ask me anything..."):

    # Display user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Call FastAPI

    try:

        response = requests.post(
            API_URL,
            json={
                "user_id": USER_ID,
                "question": question
            },
            timeout=120
        )

        # Check HTTP status

        if response.status_code != 200:

            st.error(
                f"Backend returned HTTP {response.status_code}"
            )

            st.code(response.text)

            st.stop()

        # Parse JSON

        try:

            data = response.json()

        except requests.exceptions.JSONDecodeError:

            st.error(
                "Backend returned invalid JSON."
            )

            st.code(response.text)

            st.stop()


        # Get answer

        answer = data.get(
            "answer",
            "No answer returned."
        )

        tools_used = data.get(
            "tools_used",
            []
        )

        routed_to = (
            ", ".join(tools_used)
            if tools_used
            else "general chat"
        )

        # Save assistant message

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )
        
        # Display assistant response

        with st.chat_message("assistant"):

            st.markdown(answer)

            st.caption(
                f"Routed to: {routed_to}"
            )

    # Connection error

    except requests.exceptions.ConnectionError:

        st.error(
            "Could not connect to the FastAPI server."
        )

    # Timeout

    except requests.exceptions.Timeout:

        st.error(
            "The request timed out."
        )

    # Other request errors

    except requests.exceptions.RequestException as e:

        st.error(
            f"Request failed: {str(e)}"
        )
