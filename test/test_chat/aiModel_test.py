import pytest
from unittest import IsolatedAsyncioTestCase
from llm.agents.local_chat_agent import LocalAIChatAgent

class TestAIModel(IsolatedAsyncioTestCase):

    def __init__(self, *args, **kwargs):
        super(TestAIModel, self).__init__(*args, **kwargs)

        self.language = "tr"
        self.agent = LocalAIChatAgent(
                            session_id="test_session_id",
                            language_mode=self.language,
                            )
        
    async def test_01_if_alive(self):
        """
        Test if alive agent
        """
        transcript = "selam"
        result = await self.agent.ask_agent(transcript, chat_history=[])
        results = [item async for item in result]

        self.assertIsNotNone(results)