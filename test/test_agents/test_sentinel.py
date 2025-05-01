import pytest
from unittest import IsolatedAsyncioTestCase
from llm.agents.local_chat_agent import LocalAIChatAgent
from llm.agents.agent_router import AgentRouter 
from llm.utils.tools.tools import AGENT_TOOLS


class TestLocalAIChatAgentSentinel(IsolatedAsyncioTestCase):
    """
    Test case for ensuring LocalAIChatAgent selects 'sentinel' persona correctly
    """

    def __init__(self, *args, **kwargs):
        super(TestLocalAIChatAgentSentinel, self).__init__(*args, **kwargs)
        self.language = "tr"
        self.local_agent = LocalAIChatAgent(
            session_id="test_session_id",
            language_mode=self.language,
        )

    async def test01_local_sentinel_agent(self):
        """
        Test if 'sentinel' local_agent is selected and RAG tool is invoked for the query
        """
        user_query = "güvenli internet kullanımı"
        chat_history = []

        ai_response, persona = await self.local_agent.ask_agent(user_query, chat_history)

        self.assertEqual(persona, "sentinel", msg="Persona should be 'sentinel' for this query.")
        
        results = [item async for item in ai_response]
        
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0, msg="AI response should not be empty.")


class TestAgentRouterSentinel(IsolatedAsyncioTestCase):
    """
    Test case for ensuring AgentRouter routes to 'sentinel' persona
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.language = "tr"
        self.router = AgentRouter(agent_tools=AGENT_TOOLS)

    async def test01_route_sentinel_agent(self):
        """
        Test if AgentRouter routes to 'sentinel' and returns valid response
        """
        user_query = "güvenli internet kullanımı"
        result = await self.router.route_query(user_query, language_mode=self.language)

        self.assertIn("response", result)
        self.assertIn("raw", result)
        self.assertIsInstance(result["response"], str)
        self.assertGreater(len(result["response"]), 0, msg="User response should not be empty.")
        self.assertIsInstance(result["raw"], dict)
        self.assertGreater(len(result["raw"]), 0, msg="Raw tool output should not be empty.")
