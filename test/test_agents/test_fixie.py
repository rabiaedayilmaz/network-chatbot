import pytest
from unittest import IsolatedAsyncioTestCase
from llm.agents.local_chat_agent import LocalAIChatAgent
from llm.agents.agent_router import AgentRouter 
from llm.utils.tools.tools import AGENT_TOOLS


class TestLocalAIChatAgentFixie(IsolatedAsyncioTestCase):
    """
    Test case for ensuring LocalAIChatAgent selects 'fixie' persona correctly
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "tr"
        self.local_agent = LocalAIChatAgent(
            session_id="test_session_id",
            language_mode=self.language,
        )

    async def test01_local_fixie_agent(self):
        """
        Test if 'fixie' agent is selected and RAG tool is invoked for the query
        """
        user_query = "bağlantım kesilip duruyor"
        chat_history = []

        ai_response, persona = await self.local_agent.ask_agent(user_query, chat_history)

        self.assertEqual(persona, "fixie", msg="Persona should be 'fixie' for this query.")
        results = [item async for item in ai_response]
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0, msg="AI response should not be empty.")


class TestAgentRouterFixie(IsolatedAsyncioTestCase):
    """
    Test case for ensuring AgentRouter routes 'fixie' persona and returns response
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "tr"
        self.router = AgentRouter(agent_tools=AGENT_TOOLS)

    async def test01_route_fixie_agent(self):
        """
        Test if AgentRouter routes to 'fixie' and generates user response
        """
        user_query = "bağlantı sorunumu çözebilir misin?"
        result = await self.router.route_query(user_query, language_mode=self.language)

        self.assertIn("response", result)
        self.assertIn("raw", result)
        self.assertIsInstance(result["response"], str)
        self.assertGreater(len(result["response"]), 0, msg="User response should not be empty.")

        raw_output = result["raw"]
        self.assertIsInstance(raw_output, dict)
        self.assertGreater(len(raw_output), 0, msg="Raw tool output should not be empty.")
