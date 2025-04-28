import streamlit as st
import asyncio
from uuid import uuid4
from datetime import datetime
import re
from PIL import Image
from llm.chat import handle_user_query
import base64


def image_to_base64(image_path):
    """Converts an image to a base64 string."""
    with open(image_path, "rb") as img_file:
        b64_data = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{b64_data}"


st.set_page_config(page_title="Network Chatbot", page_icon="🌐", layout="centered")
st.title("🌐 Network Chatbot")

# init chat history and session ID 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

# to track if the bot is currently processing
if "processing_query" not in st.session_state:
    # stores the query being processed
    st.session_state.processing_query = None 

# css for chat bubbles and spinner
def inject_css():
    st.markdown("""
        <style>
        .chat-container {
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        .chat-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
            flex-shrink: 0; /* Prevent shrinking */
        }
         .chat-avatar-user {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-left: 10px; /* Adjusted for user on the right */
            flex-shrink: 0; /* Prevent shrinking */
        }
        .chat-bubble-user {
            background-color: #c7e6d7;
            color: black;
            padding: 10px;
            border-radius: 15px;
            max-width: 70%;
            margin-left: auto; /* Push to the right */
            margin-right: 10px;
            word-wrap: break-word; /* Break long words */
        }
        .chat-bubble-bot {
            background-color: #E5E7EB;
            color: black;
            padding: 10px;
            border-radius: 15px;
            max-width: 70%;
            margin-right: auto; /* Stay on the left */
            margin-left: 10px;
            word-wrap: break-word; /* Break long words */
        }
        .timestamp {
            font-size: 10px;
            color: #888;
            margin-top: 3px;
            text-align: right; /* Timestamps on the right for user */
        }
         .timestamp-bot {
            font-size: 10px;
            color: #888;
            margin-top: 3px;
            text-align: left; /* Timestamps on the left for bot */
        }
        .loading-container {
            display: flex;
            align-items: center;
            gap: 5px;
            margin-left: 10px;
            margin-bottom: 15px;
        }
        .loading-dot {
            width: 8px;
            height: 8px;
            background-color: #3B82F6;
            border-radius: 50%;
            animation: bounce 1.4s infinite;
        }
        .loading-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        .loading-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        @keyframes bounce {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.3;
            }
            40% {
                transform: scale(1.2);
                opacity: 1;
            }
        }
        </style>
    """, unsafe_allow_html=True)

inject_css()

# avatar icons
USER_AVATAR = image_to_base64("assets/user.png")
BOT_AVATAR = image_to_base64("assets/ai.png")

# helper func to clean user input
def clean_user_input(text):
    """Triple backticks ve kod bloklarını temizler."""
    # This regex removes triple backticks and anything between them
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL).strip()

# ssync function to handle streaming the response into a placeholder
async def stream_response_to_placeholder(session_id, user_query, chat_history_for_llm, placeholder):
    """Streams the AI response chunks into a Streamlit placeholder."""
    ai_generator = await handle_user_query(
        session_id=session_id,
        user_query=user_query,
        chat_history=chat_history_for_llm,
        stream_to_terminal=False
    )

    full_response_content = ""
    start_time = datetime.now().strftime("%H:%M")

    try:
        async for part in ai_generator:
            chunk = part['message']['content']
            full_response_content += chunk

            placeholder.markdown(f"""
                <div class="chat-container">
                    <img src="{BOT_AVATAR}" class="chat-avatar">
                    <div class="chat-bubble-bot">
                        {full_response_content}
                        <div class="timestamp-bot">{start_time}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            await asyncio.sleep(0.01)

    except Exception as e:
        error_message = f"An error occurred: {e}"
        full_response_content += "\n\n" + error_message
        placeholder.markdown(f"""
            <div class="chat-container">
                <img src="{BOT_AVATAR}" class="chat-avatar">
                <div class="chat-bubble-bot" style="background-color: #F8D7DA; color: #721C24;">
                    {full_response_content}
                    <div class="timestamp-bot">{start_time}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        print(f"Streaming error: {e}")


    final_timestamp = datetime.now().strftime("%H:%M")
    return full_response_content, final_timestamp


# display existing messages in chat history
for chat in st.session_state.chat_history:
    role = chat.get("role", "user")
    content = chat.get("content", "")
    timestamp = chat.get("timestamp", "")

    if role == "user":
        st.markdown(f"""
            <div class="chat-container" style="flex-direction: row-reverse;">
                <img src="{USER_AVATAR}" class="chat-avatar-user">
                <div class="chat-bubble-user">
                    {content}
                    <div class="timestamp">{timestamp}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else: # role == "assistant"
         st.markdown(f"""
            <div class="chat-container">
                <img src="{BOT_AVATAR}" class="chat-avatar">
                <div class="chat-bubble-bot">
                    {content}
                    <div class="timestamp-bot">{timestamp}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)


user_query = st.chat_input("Seni dinliyorum...")

# process user query if submitted and bot is not already thinking
if user_query and st.session_state.processing_query is None:
    timestamp = datetime.now().strftime("%H:%M")
    cleaned_query = clean_user_input(user_query)

    # Add user message to history immediately
    st.session_state.chat_history.append({
        "role": "user",
        "content": cleaned_query,
        "timestamp": timestamp
    })

    st.session_state.processing_query = cleaned_query
    st.rerun()


# if there's a query waiting to be processed, handle it now
if st.session_state.processing_query:
    # display spinner
    spinner_placeholder = st.markdown("""
        <div class="loading-container">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <span style="margin-left: 8px; color: #6b7280;">Asistan düşünüyor...</span>
        </div>
    """, unsafe_allow_html=True)

    bot_response_placeholder = st.empty()

    query_to_process = st.session_state.processing_query
    st.session_state.processing_query = None 

    history_for_llm = st.session_state.chat_history

    final_content, final_timestamp = asyncio.run(
        stream_response_to_placeholder(
            st.session_state.session_id,
            query_to_process,
            history_for_llm,
            bot_response_placeholder 
        )
    )

    # clear the spinner when streaming is done
    spinner_placeholder.empty()

    # add completed message to the chat history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": final_content,
        "timestamp": final_timestamp
    })

    st.rerun()