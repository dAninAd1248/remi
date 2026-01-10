
import langchain.tools
from dotenv import load_dotenv as load_dotenv_smart
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage, BaseMessage
from langgraph.errors import GraphRecursionError
from remi import app
load_dotenv_smart()

def langchain_messages_to_dicts(messages: list[BaseMessage]) -> list[dict]:
    """Convert LangChain messages into Streamlit-friendly dicts."""
    dict_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            dict_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            dict_messages.append({"role": "assistant", "content": msg.content, "tool_calls": getattr(msg, "tool_calls", [])})
        elif isinstance(msg, ToolMessage):
            dict_messages.append({"role": "tool", "content": f"**[Tool called: {msg.name}]**", "tool_call_id": msg.tool_call_id})
        elif isinstance(msg, SystemMessage):
            pass  # system messages should be exclusively for the llm to see
            #dict_messages.append({"role": "system", "content": f"**[System]** {msg.content}"})
        else:
            dict_messages.append({
                "role": "assistant",
                "content": f"**[{type(msg).__name__}]** {getattr(msg, 'content', '')}"
            })
    return dict_messages

def dicts_to_langchain_messages(dicts: list[dict]) -> list[BaseMessage]:
    """Convert Streamlit-friendly dicts into LangChain messages."""
    messages = []
    for msg in dicts:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content, tool_calls=msg.get("tool_calls", [])))
        elif role == "tool":
            # Extract tool name from content if possible
            if content.startswith("**[Tool called: ") and content.endswith("]**"):
                tool_name = content[len("**[Tool called: "):-len("]**")]
                messages.append(ToolMessage(name=tool_name, content="", tool_call_id=msg.get("tool_call_id")))
            else:
                messages.append(ToolMessage(name="unknown", content=content, tool_call_id=msg.get("tool_call_id")))
        elif role == "system":
            messages.append(SystemMessage(content=content))
        else:
            messages.append(AIMessage(content=content))  # default to AIMessage
    return messages

def continue_conversation(message_dicts: list[dict]) -> list[dict]:
    # Continues the conversation without new user input
    # messages[-1] should probably be a user message
    messages = dicts_to_langchain_messages(message_dicts)
    prompt = {"messages": messages}
    result_messages: list[BaseMessage] = []

    attempts = 0
    while not result_messages and attempts < 10:
        attempts += 1
        try:
            result = app.invoke(prompt, {
                "configurable": {"thread_id": "remi"},
                "recursion_limit": 40
            })
            result_messages = result["messages"]
            # result_messages = []  # --- IGNORE ---
        except GraphRecursionError:
            # Force with system prompt
            prompt['messages'].append(
                SystemMessage(content="Internal message limits have been reached. There seems to be a problem with the called tool. The supervisor will now wrap up the conversation with one last message without transferring to any agent.")
            )
            continue

        # If still empty after attempts, define fallback message
        if not result_messages:
            result_messages = [
                AIMessage(content="Sorry, I was unable to process your request after multiple attempts. Please try again.")
            ]
    return langchain_messages_to_dicts(result_messages)