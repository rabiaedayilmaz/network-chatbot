import asyncio
from llm.agents.local_chat_agent import LocalAIChatAgent
from llm.agents.agent_router import AgentRouter
from utils.log import logger


async def handle_user_query(
    session_id,
    user_query,
    chat_history: list = [],
    language_mode="tr",
    stream_to_terminal: bool = False,
    llm_backend: str = "local",  # "local" or "gemini"
):
    """Handles a user query by selecting the correct AI agent and responding."""

    if llm_backend == "local":
        agent = LocalAIChatAgent(session_id=session_id, language_mode=language_mode)
        ai_response, persona = await agent.ask_agent(user_query, chat_history)
        if stream_to_terminal:
            print(f"{persona.upper()} is answering...")
            async for part in ai_response:
                print(part['message']['content'], end='', flush=True)
            print("\n")
            logger.info("AI response is sent.")
    elif llm_backend == "gemini":
        ai_response = await AgentRouter(session_id=session_id, language_mode=language_mode).ask_agent(user_query, chat_history)
        persona = ai_response["agent"]
        ai_response = ai_response["response"]

        if stream_to_terminal:
            print(f"{persona.upper()} is answering...")
            print(ai_response)
            logger.info("AI response is sent.")
    else:
        raise ValueError(f"Unsupported LLM backend: {llm_backend}")

    

    return ai_response, persona


if __name__ == "__main__":
    user_query = "My internet is very slow and buffering all the time. What can I do?"
    session_id = "123456"
    ai_response, persona = asyncio.run(handle_user_query(
        session_id, user_query, stream_to_terminal=True, llm_backend="gemini"
    ))
