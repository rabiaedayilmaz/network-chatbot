import pytest
from unittest import IsolatedAsyncioTestCase
from llm.agents.chat_agent import AIChatAgent

class TestAIChatAgentFixie(IsolatedAsyncioTestCase):
    """
    Test case for ensuring AIChatAgent selects 'fixie' persona correctly
    """

    def __init__(self, *args, **kwargs):
        super(TestAIChatAgentFixie, self).__init__(*args, **kwargs)
        self.language = "tr"
        self.agent = AIChatAgent(
            session_id="test_session_id",
            language_mode=self.language,
        )

    async def test_fixie_agent(self):
        """
        Test if 'fixie' agent is selected and RAG tool is invoked for the query
        """
        # Given
        user_query = "bağlantım kesilip duruyor"
        chat_history = []

        # When
        ai_response, persona = await self.agent.ask_agent(user_query, chat_history)

        # Then
        self.assertEqual(persona, "fixie", msg="Persona should be 'fixie' for this query.")
        
        results = [item async for item in ai_response]
        
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0, msg="AI response should not be empty.")
