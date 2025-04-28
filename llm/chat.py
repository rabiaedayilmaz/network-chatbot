import asyncio
from llm.agents.chat_agent import AIChatAgent
from utils.log import logger


async def handle_user_query(session_id, user_query, chat_history: list = [], language_mode="tr", stream_to_terminal: bool = False):
    """Handles a user query by selecting the correct AI agent and responding."""
    
    agent = AIChatAgent(session_id=session_id, language_mode=language_mode)
    ai_response, persona = await agent.ask_agent(user_query, chat_history)
    
    if stream_to_terminal:
        print(f"{persona.upper()} is answering...")
        async for part in ai_response:
            print(part['message']['content'], end='', flush=True)
        print("\n")
        logger.info("AI response is sent.")

    return ai_response, persona


if __name__ == "__main__":
    user_query = "My internet is very slow and buffering all the time. What can I do?"
    session_id = "123456"
    ai_response, persona = asyncio.run(handle_user_query(session_id, user_query, stream_to_terminal=True))
