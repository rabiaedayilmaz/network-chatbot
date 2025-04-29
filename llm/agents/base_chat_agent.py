import asyncio
from utils.log import logger
from llm.model import AIModel
from llm.utils.prompts import get_system_prompt


class BaseChatAgent:
    def __init__(self, session_id: str, language_mode: str, model: str = "gemma3:12b-it-q4_K_M", temperature: float = 0.1,
                 max_tokens: int = 256, top_p: float = 0.1, frequency_penalty: float = 0.2,
                 presence_penalty: float = 0.7, enabled_chat_history: bool = True, persona: str = None) -> None:
        self.session_id = session_id
        self.model = model
        self.language_mode = language_mode
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.enabled_chat_history = enabled_chat_history
        self.persona = persona
        self.system_prompt = get_system_prompt(language_mode=language_mode)

    @staticmethod
    def set_model_parameters(system_prompt, model, language_mode, 
                             temperature, max_tokens, top_p, frequency_penalty, 
                             presence_penalty, enabled_chat_history, persona):

        logger.info(f"Language is set to {language_mode.upper()}")

        model_params = {
                        "system_prompt": system_prompt,
                        "model": model,
                        "language_mode": language_mode,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "top_p": top_p,
                        "frequency_penalty": frequency_penalty,
                        "presence_penalty": presence_penalty,
                        "enabled_chat_history": enabled_chat_history,
                        "persona": persona
                        }
        return model_params

    async def _ask_agent(self, user_query: str, chat_history: list = []):
        model_params = self.set_model_parameters(system_prompt=self.system_prompt, model=self.model, language_mode=self.language_mode, 
                                                 temperature=self.temperature, max_tokens=self.max_tokens, top_p=self.top_p,
                                                 frequency_penalty=self.frequency_penalty, presence_penalty=self.presence_penalty, 
                                                 persona=self.persona, enabled_chat_history=self.enabled_chat_history)
        model = AIModel(**model_params)
        ai_response = await model.ask_to_model(user_query=user_query, chat_history=chat_history, persona=self.persona)
        return ai_response


if __name__ == "__main__":
    asyncio.run(BaseChatAgent()._ask_agent("hello test"))