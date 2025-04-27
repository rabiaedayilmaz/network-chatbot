import pytest
from unittest import IsolatedAsyncioTestCase
from llm.agents.chat_agent import AIChatAgent

class TestAIChatAgentProfPing(IsolatedAsyncioTestCase):
    """
    Test case for ensuring AIChatAgent selects 'professor_ping' persona correctly
    """

    def __init__(self, *args, **kwargs):
        super(TestAIChatAgentProfPing, self).__init__(*args, **kwargs)
        self.language = "tr"
        self.agent = AIChatAgent(
            session_id="test_session_id",
            language_mode=self.language,
        )

    async def test_profping_agent(self):
        """
        Test if 'professor_ping' agent is selected and RAG tool is invoked for the query
        """
        # Given
        user_query = "yıldız topolojisi çizer misin"
        chat_history = []

        # When
        ai_response, persona = await self.agent.ask_agent(user_query, chat_history)

        # Then
        self.assertEqual(persona, "professor_ping", msg="Persona should be 'professor_ping' for this query.")
        
        results = [item async for item in ai_response]
        
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0, msg="AI response should not be empty.")
