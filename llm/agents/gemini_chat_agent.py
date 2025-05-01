import os
import re
import json
import google.generativeai as genai
from google.generativeai import configure
from llm.agents.base_chat_agent import BaseChatAgent

from utils.log import logger
from dotenv import load_dotenv
load_dotenv()


class GeminiChatAgent(BaseChatAgent):
    def __init__(self, session_id: str = "", language_mode: str = "tr", model_name="models/gemini-2.0-flash"):
        super().__init__(session_id=session_id, language_mode=language_mode)
        
        configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model_name)

    def generate_json_response(self, prompt):
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        json_str = match.group(1) if match else response_text
        try:
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Invalid Gemini response: {response_text}") from e

    def generate_text_response(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text.strip()
    
    async def ask_agent(self, user_query, chat_history):
        prompt = self.build_prompt(user_query, chat_history)
        response = self.model.generate_content(prompt)
        text = response.text.strip()

        # Agent/persona detection
        match = re.search(r"agent:\s*(\w+)", text, re.IGNORECASE)
        persona = match.group(1).lower() if match else "unknown"

        # Simulate async stream
        async def stream_response():
            yield {"message": {"content": text}}

        return stream_response(), persona

    def build_prompt(self, user_query, chat_history):
            history_str = ""
            for turn in chat_history[-5:]:
                history_str += f"User: {turn.get('user')}\nAssistant: {turn.get('assistant')}\n"
            return (
                f"Consider these chat history: {history_str}\nUnder 100 words answer. User: {user_query}"
            )