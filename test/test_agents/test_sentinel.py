import pytest
from unittest import IsolatedAsyncioTestCase
from llm.agents.chat_agent import AIChatAgent

class TestAIChatAgentSentinel(IsolatedAsyncioTestCase):
    """
    Test case for ensuring AIChatAgent selects 'sentinel' persona correctly
    """

    def __init__(self, *args, **kwargs):
        super(TestAIChatAgentSentinel, self).__init__(*args, **kwargs)
        self.language = "tr"
        self.agent = AIChatAgent(
            session_id="test_session_id",
            language_mode=self.language,
        )

    async def test_sentinel_agent(self):
        """
        Test if 'sentinel' agent is selected and RAG tool is invoked for the query
        """
        # Given
        user_query = "güvenli internet kullanımı"
        chat_history = []

        # When
        ai_response, persona = await self.agent.ask_agent(user_query, chat_history)

        # Then
        self.assertEqual(persona, "sentinel", msg="Persona should be 'sentinel' for this query.")
        
        results = [item async for item in ai_response]
        
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0, msg="AI response should not be empty.")
