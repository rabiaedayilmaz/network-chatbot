import asyncio
from llm.agents.base_chat_agent import BaseChatAgent
from llm.utils.agent_mapping import PERSONA_MAPPING
from llm.utils.select_agent import select_agent
from llm.utils.tools.tools import AGENT_TOOLS
from llm.model import AIModel
from utils.log import logger
from llm.agents.rag_agent import RagAgent
from llm.utils.tools.hypernet_tools import run_speedtest_if_needed


class AIChatAgent(BaseChatAgent):
    def __init__(self, session_id: str = "", language_mode: str = "tr"):
        super().__init__(session_id=session_id, language_mode=language_mode)

        self.rag_agent = RagAgent()
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

    async def ask_agent(self, user_query: str, chat_history: list = []):
        persona = select_agent(user_query=user_query)
        if persona:
            logger.info(f"Selected Agent: {persona.upper()}")
        else:
            logger.info("No agent selected.")

        persona_prompt = PERSONA_MAPPING.get(persona, "")
        agent_tools = AGENT_TOOLS.get(persona, [])

        # Fixie is RAG agent
        if persona == "fixie":
            user_query = await self._run_rag_if_needed(persona, user_query)
        elif persona == "hypernet":
            speedtest_results = await run_speedtest_if_needed(persona)
            if speedtest_results:
                user_query = f"{user_query}\n\n Speed Results: {speedtest_results} I will inform you about the speed test results."
                logger.info("Speedtest results appended to user query.")

        model = AIModel(**self.model_params)
        ai_response = await model.ask_to_model(
            user_query=user_query,
            chat_history=chat_history,
            persona=persona,
            persona_prompt=persona_prompt,
            agent_tools=agent_tools
        )

        return ai_response, persona
    
    async def _run_rag_if_needed(self, persona: str, user_query: str) -> str:
        if persona != "fixie":
            return user_query
        dataset_id, tool_name = self.rag_agent.select_dataset(user_query)
        if dataset_id and tool_name:
            rag_response = await self.rag_agent.call_rag_tool(tool_name, user_query, dataset_id)
            if rag_response:
                return f"{user_query}\n\nRetrieved Information: \n{rag_response}"
        return user_query


async def main():
    chat_history = []
    user_query = "wifi nedir öğrenmek istiyorum"
    ai_response, persona = await AIChatAgent().ask_agent(user_query=user_query, chat_history=chat_history)
    print("User:")
    print(user_query)
    print("\nAgent:")
    async for part in ai_response:
        print(part['message']['content'], end='', flush=True)
    print("\n")
    logger.info("AI response is sent.")

if __name__ == '__main__':
    asyncio.run(main())