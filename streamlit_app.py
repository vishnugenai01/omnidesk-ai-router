# import streamlit as st
# import requests

# API_URL = "http://127.0.0.1:8000/ask"

# st.title("OmniDesk AI Assistant")
# st.caption("One chat box, five services - ask about tasks, food orders, students, movie bookings, or expenses.")

# # Added a header and a few more examples to make the sidebar look complete
# with st.sidebar:
#     st.write("### Example Prompts")
#     st.write("- Book 2 tickets for Inception")
#     st.write("- What are my expenses for today?")
#     st.write("- Add 'buy groceries' to my tasks")

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display previous messages
# for msg in st.session_state.messages:
#     st.chat_message(msg["role"]).write(msg["content"])

# if question := st.chat_input("Ask me anything..."):
#     # Show user message
#     st.session_state.messages.append({"role": "user", "content": question})
#     st.chat_message("user").write(question)

#     payload = {
#         "messages": st.session_state.messages
#     }

#     # Add a spinner while waiting for the backend
#     with st.spinner("Thinking..."):
#         try:
#             response = requests.post(API_URL, json=payload, timeout=90)
            
#             # Check if the API returned a successful HTTP status code
#             if response.status_code == 200:
#                 try:
#                     data = response.json()
#                     answer = data.get("answer", "No answer provided by backend.")
                    
#                     # Safely handle the tools list
#                     tools_list = data.get("tools_used", [])
#                     tools_used = ", ".join(tools_list) if tools_list else "general chat"

#                     # Save and display assistant response
#                     st.session_state.messages.append({"role": "assistant", "content": answer})
#                     st.chat_message("assistant").write(f"{answer}\n\n_Routed to: {tools_used}_")
                
#                 except requests.exceptions.JSONDecodeError:
#                     st.error(f"Backend returned invalid JSON. Raw text:\n\n{response.text}")
            
#             else:
#                 st.error(f"Backend returned an error (Status {response.status_code}):\n\n{response.text}")

#         # Catch connection and timeout errors
#         except requests.exceptions.ConnectionError:
#             st.error("Could not connect to the backend API. Please make sure your FastAPI/backend server is running on http://127.0.0.1:8000!")
#         except requests.exceptions.Timeout:
#             st.error("The backend took too long to respond (over 90 seconds).")
#         except Exception as e:
#             st.error(f"An unexpected error occurred: {e}")


import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.title("OmniDesk AI Assistant")
st.caption(
    "One chat box, five services — ask about tasks, food orders, "
    "students, movie bookings, or expenses."
)

# Initialize chat history ONLY once
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.subheader("Try asking:")
    st.write("- Add a task to buy groceries")
    st.write("- Show me the food menu")
    st.write("- Register a new student named Priya")
    st.write("- Book 2 tickets for Inception")

# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
if question := st.chat_input("Ask me anything..."):

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    st.chat_message("user").write(question)

    # Send COMPLETE conversation to FastAPI
    payload = {
        "messages": st.session_state.messages
    }

    try:
        with st.spinner("Thinking..."):

            response = requests.post(
                API_URL,
                json=payload,
                timeout=90
            )

        # Handle HTTP errors before trying to read "answer"
        if response.status_code != 200:
            st.error(
                f"Backend returned HTTP {response.status_code}\n\n"
                f"{response.text}"
            )
        else:
            try:
                data = response.json()
            except ValueError:
                st.error(
                    "Backend returned invalid JSON:\n\n"
                    + response.text
                )
                st.stop()

            # Safely read response
            answer = data.get("answer")

            if answer is None:
                st.error(
                    "Backend response does not contain 'answer'.\n\n"
                    f"Backend response:\n{data}"
                )
                st.stop()

            tools_used = data.get("tools_used", [])

            if tools_used:
                tools_text = ", ".join(tools_used)
            else:
                tools_text = "general chat"

            # Save assistant response
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            # Display response
            st.chat_message("assistant").write(
                f"{answer}\n\n_Routed to: {tools_text}_"
            )

    except requests.exceptions.ConnectionError:
        st.error(
            "Could not connect to the backend API.\n\n"
            "Make sure FastAPI is running on:\n"
            "http://127.0.0.1:8000"
        )

    except requests.exceptions.Timeout:
        st.error(
            "The backend took too long to respond "
            "(over 90 seconds)."
        )

    except Exception as e:
        st.error(f"Unexpected error: {e}")

