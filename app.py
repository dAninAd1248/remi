import api  # All interactions with system should happen through API
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

if "messages" not in st.session_state:
    st.session_state.messages = []



# App config
st.set_page_config(page_title="REMI", page_icon="🐭")
st.title("🐭 REMI")

# Render selected messages
def render_messages(messages: list[dict], display_mode):
    for i, message in enumerate(messages):
        if not message["content"]:
            continue
        role = message["role"]
        next_role = messages[i + 1]["role"] if i + 1 < len(messages) else None
        show = False

        if display_mode == "All" or role == 'user':
            show = True
        elif display_mode == "Last message only":
            show = (
                role == "assistant" and
                (next_role == "user" or next_role == None)
            )

        if not show:
            continue


        avatar = None
        if role == "tool":
            avatar = "🛠️"
        elif role == "system":
            avatar = "🧠"

        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])

# Display mode selector
if "messages" not in st.session_state:
    st.session_state.messages = []

display_mode = st.sidebar.selectbox(
    "Select Response Mode: ",
    ("All", "Last message only")
)

# Renders previous message
render_messages(st.session_state.messages, display_mode)

# Handle user input
if prompt := st.chat_input("Ask me anything about molecular dynamics..."):
    # 1. Add user message
    user_message = {"role": "user", "content": prompt}
    render_messages([user_message], display_mode)

    # 2. Generate response
    with st.spinner("Thinking..."):
        messages = api.continue_conversation(st.session_state.messages + [user_message])
        st.session_state.messages = messages
        
        new_messages = []
        for i in range(len(messages) - 1, 0, -1):
            if messages[i]["role"] == "user": break
            new_messages.append(messages[i])  # appended in reverse order for efficiency
        new_messages.reverse()  # unreverse

        # 3. Save and render new assistant/tool/system messages
        render_messages(new_messages, display_mode)