import pytest
from unittest import IsolatedAsyncioTestCase
from llm.agents.local_chat_agent import LocalAIChatAgent
from llm.agents.agent_router import AgentRouter 
from llm.utils.tools.tools import AGENT_TOOLS


class TestLocalAIChatAgentProfPing(IsolatedAsyncioTestCase):
    """
    Test case for ensuring LocalAIChatAgent selects 'professor_ping' persona correctly
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "tr"
        self.local_agent = LocalAIChatAgent(
            session_id="test_session_id",
            language_mode=self.language,
        )

    async def test01_local_profping_agent(self):
        """
        Test if 'professor_ping' local_agent is selected and topology diagram is generated
        """
        user_query = "yıldız topolojisi çizer misin"
        chat_history = []

        ai_response, persona = await self.local_agent.ask_agent(user_query, chat_history)

        self.assertEqual(persona, "professor_ping", msg="Persona should be 'professor_ping' for this query.")
        results = [item async for item in ai_response]
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0, msg="AI response should not be empty.")

class TestAgentRouterProfPing(IsolatedAsyncioTestCase):
    """
    Test case for ensuring AgentRouter routes to 'professor_ping' persona and uses topology tool
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "tr"
        self.router = AgentRouter(agent_tools=AGENT_TOOLS)

    async def test01_route_profping_agent(self):
        """
        Test if AgentRouter routes to 'professor_ping' and generates valid output
        """
        user_query = "yıldız topolojisi çizer misin?"
        result = await self.router.route_query(user_query, language_mode=self.language)

        self.assertIn("response", result)
        self.assertIn("raw", result)
        self.assertIsInstance(result["response"], str)
        self.assertGreater(len(result["response"]), 0, msg="User response should not be empty.")
        self.assertIsInstance(result["raw"], dict)
        self.assertGreater(len(result["raw"]), 0, msg="Raw tool output should not be empty.")
