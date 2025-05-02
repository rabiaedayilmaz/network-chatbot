import streamlit as st
import asyncio
from uuid import uuid4
from datetime import datetime
import re
from llm.chat import handle_user_query
import base64
import os 
import html
from utils.log import logger


###
### ollama is not supported for deplotyment yet
### it runs only locally using app.py
### system requrements are high for ollama 
### but docker container is designed to handle all llm models including ollama
###


LLM_BACKENDS = ["gemini"]

AGENTS = {
    "fixie": {
        "name": "Fixie (Destek Botu)",
        "avatar_path": "assets/fixie_avatar_chat.jpg", 
        "description": "Kullanıcı dostu, kolay çözümler sunan destek botu."
    },
    "bytefix": {
        "name": "Bytefix (Teknik Uzman)",
        "avatar_path": "assets/bytefix_avatar_chat.jpg", 
        "description": "Detaylı teknik ağ sorun giderme uzmanı."
    },
    "routerx": {
         "name": "RouterX (Ağ Mühendisi)",
         "avatar_path": "assets/routerx_avatar_chat.png", 
         "description": "Ağ altyapısı optimizasyonu ve yapılandırma uzmanı."
    },
    "sentinel": {
         "name": "Sentinel (Siber Güvenlik)",
         "avatar_path": "assets/sentinel_avatar_chat.png", 
         "description": "Ağ güvenliği, tehditler ve korunma yolları danışmanı."
    },
    "hypernet": {
         "name": "HyperNet (Hız Uzmanı)",
         "avatar_path": "assets/hypernet_avatar_chat.jpg", 
         "description": "İnternet hızını artırma ve optimizasyon uzmanı."
    },
    "professor_ping": {
          "name": "Professor Ping (Ağ Eğitmeni)",
          "avatar_path": "assets/prof_ping_avatar_chat.png",
          "description": "Ağ kavramlarını anlaşılır ve eğlenceli bir şekilde öğretir."
    }
}

def image_to_base64(image_path):
    """Encodes a local image file to a base64 string."""
    if not os.path.exists(image_path):
        print(f"Warning: Avatar file not found at {image_path}. Using empty placeholder.")
        return ""
    try:
        with open(image_path, "rb") as img_file:
            b64_data = base64.b64encode(img_file.read()).decode()
        # add data url prefix
        return f"data:image/png;base64,{b64_data}"
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return ""
    
def escape_html_with_breaks(text):
    return html.escape(text).replace("\n", "<br>")

st.set_page_config(page_title="Ağ Uzmanı Agent Takımı", page_icon="🌐", layout="centered")

@st.cache_resource
def load_agents_with_b64_avatars():
    agents_with_b64 = {}
    for agent_key, agent_info in AGENTS.items():
        agents_with_b64[agent_key] = {
            "name": agent_info["name"],
            "description": agent_info["description"],
            "avatar_b64": image_to_base64(agent_info["avatar_path"])
        }
    return agents_with_b64

AGENTS_WITH_B64_AVATARS = load_agents_with_b64_avatars()
DEFAULT_AGENT_INFO_B64 = AGENTS["fixie"]

# place all agents inside dict
for agent_key, agent_info in AGENTS.items():
    AGENTS_WITH_B64_AVATARS[agent_key] = {
        "name": agent_info["name"],
        "description": agent_info["description"],
        "avatar_b64": image_to_base64(agent_info["avatar_path"])
    }


# base64 avatar
USER_AVATAR_B64 = image_to_base64("assets/user.png") 


st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)
st.title("🌐 Ağ Uzmanı Agent Takımı")

### states
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

if "llm_backend" not in st.session_state:
    st.session_state.llm_backend = "gemini"  # default

if "processing_query" not in st.session_state:
    st.session_state.processing_query = None 

if "current_llm_agent_key" not in st.session_state:
     st.session_state.current_llm_agent_key = "fixie"

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
            max-width: 400px;
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

def clean_user_input(text):
    """Triple backticks ve kod bloklarını temizler."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL).strip()


async def stream_response_to_placeholder(session_id, user_query, chat_history_for_llm, placeholder, agent_key_for_this_turn):
    """Streams the AI response chunks into a Streamlit placeholder using the specified agent."""
    agent_info = AGENTS_WITH_B64_AVATARS.get(agent_key_for_this_turn.lower(), DEFAULT_AGENT_INFO_B64)
    agent_avatar = agent_info.get("avatar_b64", "")
    current_persona_display_name = agent_info.get("name", "Bot")

    full_response_content = ""
    start_time = datetime.now().strftime("%H:%M")
    final_persona_key_used = agent_key_for_this_turn 

    try:
        ai_generator, returned_persona_key = await handle_user_query(
            session_id=session_id,
            user_query=user_query,
            chat_history=chat_history_for_llm,
            stream_to_terminal=False,
            llm_backend=st.session_state.llm_backend
        )

        if returned_persona_key:
             final_persona_key_used = returned_persona_key
             returned_agent_info = AGENTS_WITH_B64_AVATARS.get(final_persona_key_used, DEFAULT_AGENT_INFO_B64)
             current_persona_display_name = returned_agent_info.get("name", "Bot")
             agent_avatar = returned_agent_info.get("avatar_b64", "")


    except Exception as e:
        error_message = f"Agent ({current_persona_display_name}) başlatılırken bir hata oluştu: {e}"
        placeholder.markdown(f"""
            <div class="chat-container">
                <img src="{agent_avatar}" class="chat-avatar">
                <div>
                    <div class="agent-name">{current_persona_display_name} (Hata)</div>
                    <div class="chat-bubble-bot" style="background-color: #F8D7DA; color: #721C24;">
                        {error_message}
                        <div class="timestamp-bot">{datetime.now().strftime("%H:%M")}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        print(f"LLM initialization error for agent {agent_key_for_this_turn}: {e}")
        return error_message, datetime.now().strftime("%H:%M"), agent_key_for_this_turn


    # proceed with streaming
    try:
        if st.session_state.llm_backend == "gemini":
            # gemini api does not support streaming
            # so we need to wait for the full response
            full_response_content = ai_generator  # it’s just a string!

            placeholder.markdown(f"""
                <div class="chat-container">
                    <img src="{agent_avatar}" class="chat-avatar">
                    <div>
                        <div class="agent-name">{current_persona_display_name}</div>
                        <div class="chat-bubble-bot">
                            {escape_html_with_breaks(full_response_content)}
                            <div class="timestamp-bot">{start_time}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        else:
            # streaming for other backends like Ollama
            async for part in ai_generator:
                chunk = part.get('message', {}).get('content')
                if chunk:
                    full_response_content += chunk
                    placeholder.markdown(f"""
                        <div class="chat-container">
                            <img src="{agent_avatar}" class="chat-avatar">
                            <div>
                                <div class="agent-name">{current_persona_display_name}</div>
                                <div class="chat-bubble-bot">
                                    {escape_html_with_breaks(full_response_content)}
                                    <div class="timestamp-bot">{start_time}</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    await asyncio.sleep(0.01)

    except Exception as e:
        error_message_streaming = f"Akış sırasında bir hata oluştu: {e}"
        full_response_content += "\n\n" + error_message_streaming
        placeholder.markdown(f"""
            <div class="chat-container">
                <img src="{agent_avatar}" class="chat-avatar">
                <div>
                    <div class="agent-name">{current_persona_display_name} (Hata)</div>
                    <div class="chat-bubble-bot" style="background-color: #F8D7DA; color: #721C24;">
                        {escape_html_with_breaks(full_response_content)}
                        <div class="timestamp-bot">{start_time}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        print(f"Streaming error for agent {final_persona_key_used}: {e}")
        final_persona_key_used = final_persona_key_used 


    final_timestamp = datetime.now().strftime("%H:%M")
    return full_response_content, final_timestamp, final_persona_key_used


# sidebar - agent info
st.sidebar.markdown("### 🔧 LLM Backend Seçimi")
st.session_state.llm_backend = st.sidebar.selectbox(
    "Hangi LLM kullanılacak?", 
    LLM_BACKENDS, 
    index=LLM_BACKENDS.index(st.session_state.llm_backend)
)

st.sidebar.title("Son Aktif Agent")

current_agent_key = st.session_state.current_llm_agent_key
agent_info_display = AGENTS.get(current_agent_key, AGENTS["fixie"]) # if found none, default to fixie

st.sidebar.image(agent_info_display["avatar_path"], width=50)

st.sidebar.markdown(f"**{agent_info_display["name"]}**")
#st.sidebar.caption(agent_info_display["description"])

user_query = st.chat_input("Mesajını yaz...", disabled=st.session_state.processing_query is not None)

st.sidebar.markdown("### 🤖 Agent Listesi")

for key, agent in AGENTS.items():
    # Highlight the active one with a subtle background or style
    if key == current_agent_key:
        st.sidebar.markdown(
            f"""
            <div style="background-color: #d1c9d5; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                <img src="{image_to_base64(agent['avatar_path'])}" width="30" style="vertical-align: middle; border-radius: 50%; margin-right: 10px;">
                <b>{agent['name']}</b><br>
                <span style="font-size: 12px; color: #555;">{agent['description']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.sidebar.markdown(
            f"""
            <div style="margin-bottom: 8px;">
                <img src="{image_to_base64(agent['avatar_path'])}" width="30" style="vertical-align: middle; border-radius: 50%; margin-right: 10px;">
                <b>{agent['name']}</b><br>
                <span style="font-size: 12px; color: #555;">{agent['description']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )


# existing messages in chat history
for chat in st.session_state.chat_history:
    role = chat.get("role", "user")
    content = chat.get("content", "")
    timestamp = chat.get("timestamp", "")
    persona_key_in_history = chat.get("agent", st.session_state.current_llm_agent_key).lower()

    if role == "user":
        st.markdown(f"""
            <div class="chat-container" style="flex-direction: row-reverse;">
                <img src="{USER_AVATAR_B64}" class="chat-avatar-user">
                <div class="chat-bubble-user">
                    {content}
                    <div class="timestamp">{timestamp}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif role == "assistant": # role == "assistant"
         logger.info(f"Getting persona: {persona_key_in_history}")
         agent_info_for_display = AGENTS_WITH_B64_AVATARS[persona_key_in_history]
         logger.info(f"Agent info for display: {agent_info_for_display["name"]}")
         agent_avatar_to_display = agent_info_for_display.get("avatar_b64", "")
         agent_name_to_display = agent_info_for_display.get("name", "Bot")
         st.session_state.current_llm_agent_key = persona_key_in_history


         st.markdown(f"""
            <div class="chat-container">
                <img src="{agent_avatar_to_display}" class="chat-avatar">
                <div>
                     <div class="agent-name">{agent_name_to_display}</div> 
                     <div class="chat-bubble-bot">
                        {content}
                        <div class="timestamp-bot">{timestamp}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


if user_query and st.session_state.processing_query is None:
    timestamp = datetime.now().strftime("%H:%M")
    cleaned_query = clean_user_input(user_query)

    st.session_state.chat_history.append({
        "role": "user",
        "content": cleaned_query,
        "timestamp": timestamp
    })

    st.session_state.processing_query = {
        "query": cleaned_query,
        "agent_key": st.session_state.current_llm_agent_key
    }
    st.rerun() 


if st.session_state.processing_query:
    spinner_placeholder = st.markdown("""
        <div class="loading-container">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <span>Asistan düşünüyor...</span>
        </div>
    """, unsafe_allow_html=True)

    bot_response_placeholder = st.empty()

    processing_info = st.session_state.processing_query
    query_to_process = processing_info["query"]
    agent_key_for_this_turn = processing_info["agent_key"] 

    history_for_llm = list(st.session_state.chat_history)

    final_content, final_timestamp, completed_agent_key = asyncio.run(
        stream_response_to_placeholder(
            st.session_state.session_id,
            query_to_process,
            history_for_llm, 
            bot_response_placeholder, 
            agent_key_for_this_turn 
        )
    )

    spinner_placeholder.empty()

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": escape_html_with_breaks(final_content),
        "timestamp": final_timestamp,
        "agent": completed_agent_key
    })

    st.session_state.processing_query = None
    st.session_state.current_llm_agent_key = completed_agent_key

    st.rerun()
