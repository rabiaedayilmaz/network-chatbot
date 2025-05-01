import pytest
from unittest import IsolatedAsyncioTestCase
from llm.agents.local_chat_agent import LocalAIChatAgent


class TestLocalAIChatAgentFixie(IsolatedAsyncioTestCase):
    """
    Test case for ensuring LocalAIChatAgent selects 'fixie' persona correctly
    """

    def __init__(self, *args, **kwargs):
        super(TestLocalAIChatAgentFixie, self).__init__(*args, **kwargs)
        self.language = "tr"
        self.local_agent = LocalAIChatAgent(
            session_id="test_session_id",
            language_mode=self.language,
        )

    async def test01_local_fixie_agent(self):
        """
        Test if 'fixie' agent is selected and RAG tool is invoked for the query
        """
        # Given
        user_query = "bağlantım kesilip duruyor"
        chat_history = []

        # When
        ai_response, persona = await self.local_agent.ask_agent(user_query, chat_history)

        # Then
        self.assertEqual(persona, "fixie", msg="Persona should be 'fixie' for this query.")
        
        results = [item async for item in ai_response]
        
        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0, msg="AI response should not be empty.")
