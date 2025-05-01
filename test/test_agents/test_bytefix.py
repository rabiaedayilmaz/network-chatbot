import pytest
from unittest import IsolatedAsyncioTestCase
from llm.agents.local_chat_agent import LocalAIChatAgent
from llm.agents.agent_router import AgentRouter
from llm.utils.tools.tools import AGENT_TOOLS


class TestLocalAIChatAgentBytefix(IsolatedAsyncioTestCase):
    """
    Test case for ensuring LocalAIChatAgent selects 'bytefix' persona correctly
    """

    def __init__(self, *args, **kwargs):
        super(TestLocalAIChatAgentBytefix, self).__init__(*args, **kwargs)
        self.language = "tr"
        self.local_agent = LocalAIChatAgent(
            session_id="test_session_id",
            language_mode=self.language,
        )

    async def test01_local_bytefix_agent(self):
        """
        Test if 'bytefix' local_agent is selected and RAG tool is invoked for the query
        """
        user_query = "google.com için ağ tanılama testi yapabilir misin"
        chat_history = []

        ai_response, persona = await self.local_agent.ask_agent(user_query, chat_history)

        self.assertEqual(persona, "bytefix", msg="Persona should be 'bytefix' for this query.")

        results = [item async for item in ai_response]

        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0, msg="AI response should not be empty.")


class TestAgentRouterBytefix(IsolatedAsyncioTestCase):
    """
    Test case for AgentRouter selecting and executing Bytefix agent correctly.
    """

    async def asyncSetUp(self):
        self.router = AgentRouter(agent_tools=AGENT_TOOLS)

    async def test01_route_query_bytefix(self):
        """
        Ensure AgentRouter selects Bytefix and returns a valid response and tool output.
        """
        user_query = "google.com için ağ tanılama testi yapabilir misin"

        result = await self.router.route_query(user_query, language_mode="tr")

        self.assertIn("raw", result)
        self.assertIn("response", result)
        self.assertIn("agent", result)
        self.assertIn("function", result)

        # Ensure tool output isn't empty
        self.assertIsInstance(result["raw"], dict)
        self.assertGreater(len(result["raw"]), 0, "Expected non-empty tool output.")

        # Ensure response is present and readable
        self.assertIsInstance(result["response"], str)
        self.assertGreater(len(result["response"]), 10, "Expected user response to be meaningful.")

        self.assertEqual(result["agent"], "bytefix")
        self.assertEqual(result["function"], "run_network_diagnostics")
