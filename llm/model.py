import asyncio

from ollama import AsyncClient
from dataclasses import dataclass
from dataclasses import field
from utils.log import logger
from llm.utils.agent_mapping import PERSONA_MAPPING
from llm.utils.select_agent import select_agent
from llm.utils.prompts import get_system_prompt


@dataclass
class AIModel:
    system_prompt: str = field(default="")
    model: str = field(default="phi4")
    language_mode: str = field(default="tr")
    temperature: float = field(default=0.1)
    max_tokens: int = field(default=256)
    top_p: float = field(default=1)
    frequency_penalty: float = field(default=0.2)
    presence_penalty: float = field(default=0.7)
    enabled_chat_history: bool = field(default=True) 
    persona: str = field(default="fixie")


    async def ask_to_model(self, user_query: str = None, chat_history: list = [], stream_to_terminal: bool = False,
                           persona: str = "fixie", persona_prompt: str = "", agent_tools: list = None):
        try:
            client = AsyncClient()
            logger.info(f"Selected Agent: {persona.upper()}")
            persona_prompt = PERSONA_MAPPING[persona]

            current_query = {"role": "user", "content": user_query}

            if chat_history:
                current_query = [{"role": "system", "content": persona_prompt}]
                history_prompt = [{"role": "system", "content": "Previous messages provided as only context for chat history."}]
                chat_history = chat_history + history_prompt + current_query
            else:
                chat_history += [{"role": "system", "content": self.system_prompt}, current_query]

            # returns async generator 
            ai_response = await client.chat(
                                            self.model, 
                                            messages=chat_history, 
                                            stream=True,
                                            )
            
            logger.info("AI response generator is creater.")

            # mostly for testing
            if stream_to_terminal:
                async for part in ai_response:
                    print(part['message']['content'], end='', flush=True)
                print("\n")
                logger.info("AI response is sent.")

            return ai_response

        except Exception as e:
            logger.error(f"Error occured in creation of AI response generator: {e}")



async def main():
    chat_history = []
    user_query = "internet bağlantım kesilip duruyor"
    language_mode = "tr"
    system_prompt = get_system_prompt(language_mode)

    print("Kullanıcı:")
    print(user_query)
    print("\n")
    print("Destek Botu:")

    ai_model = AIModel(system_prompt=system_prompt)
    await ai_model.ask_to_model(user_query=user_query, chat_history=chat_history, stream_to_terminal=True)


if __name__ == '__main__':
  asyncio.run(main())