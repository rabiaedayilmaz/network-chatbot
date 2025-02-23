import asyncio
from llm.agents.base_chat_agent import BaseChatAgent
from llm.utils.agent_mapping import PERSONA_MAPPING
from llm.utils.select_agent import select_agent
from llm.utils.tools import AGENT_TOOLS
from llm.model import AIModel
from utils.log import logger


class AIChatAgent(BaseChatAgent):
    def __init__(self, session_id: str = "", language_mode: str = "tr"):

        super().__init__(
            session_id=session_id,
            language_mode=language_mode,
        )
        self.model_params = self.set_model_parameters(
            system_prompt=self.system_prompt,
            model=self.model,
            language_mode=self.language_mode,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            enabled_chat_history=self.enabled_chat_history,
            persona=self.persona
        )

    @staticmethod
    async def set_agent_tools(user_query: str):
        # select persona based on user query
        persona = select_agent(user_query)
        persona_prompt = PERSONA_MAPPING[persona]
        agent_tools = AGENT_TOOLS.get(persona, [])

        logger.info(f"Selected Agent: {persona}")
        logger.info(f"Assigned Tools: {agent_tools}")

        return persona, persona, persona_prompt, agent_tools

    async def ask_agent(self, user_query: str, chat_history: list = []):
        """
        Runs the AI model with the selected persona
        Return: generator AI response
        """
        persona, persona, persona_prompt, agent_tools = await self.set_agent_tools(user_query=user_query)
        model = AIModel(**self.model_params)
        ai_response = await model.ask_to_model(user_query=user_query, chat_history=chat_history, persona=persona,
                                               persona_prompt=persona_prompt, agent_tools=agent_tools)
        return ai_response


async def main():
    chat_history = []
    user_query = "internet bağlantım kesilip duruyor"

    print("User:")
    print(user_query)
    print("\n")
    print("Agent:")

    ai_response = await AIChatAgent().ask_agent(user_query=user_query, chat_history=chat_history)
    async for part in ai_response:
        print(part['message']['content'], end='', flush=True)
    print("\n")
    logger.info("AI response is sent.")


if __name__ == '__main__':
  asyncio.run(main())