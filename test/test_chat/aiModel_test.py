import pytest
from unittest import IsolatedAsyncioTestCase
from llm.agents.chat_agent import AIChatAgent

class TestGPT(IsolatedAsyncioTestCase):

    def __init__(self, *args, **kwargs):
        super(TestGPT, self).__init__(*args, **kwargs)

        self.language = "tr"
        self.agent = AIChatAgent(session_id="test_session_id",
                            available_languages=["tr"],
                            language_code=self.language,
                            )
        
    async def test_01_gpt_connection_unit(self):
        """
        Test if alive agent
        """
        transcript = "Merhaba"
        result = await self.agent.ask_agent(transcript, user_old_messages=[])
        self.assertIsNotNone(result.get("ai_response"))