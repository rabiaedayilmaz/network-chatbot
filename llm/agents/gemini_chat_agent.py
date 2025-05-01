import os
import re
import json
import google.generativeai as genai
from google.generativeai import configure

from utils.log import logger
from dotenv import load_dotenv
load_dotenv()


class GeminiChatAgent:
    def __init__(self, model_name="models/gemini-2.0-flash"):
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
