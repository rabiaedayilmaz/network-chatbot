import asyncio
from uuid import uuid4
from llm.chat import handle_user_query
from utils.log import logger

async def main():
    """Takes user input from the terminal and processes it with the AI model."""
    try:
        chat_history = []
        session_id = str(uuid4())
        llm_backend = input("Hangi LLM kullanılacak? [local/gemini]: ").strip().lower()

        if llm_backend not in ["local", "gemini"]:
            print("Geçersiz seçim. Varsayılan olarak 'local' seçildi.")
            llm_backend = "local"

        logger.info(f"Session started: {session_id} | LLM: {llm_backend}")
        while True:
            user_query = input(">> ").strip()
            if user_query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            logger.info("Starting...")
            await handle_user_query(
                session_id=session_id,
                user_query=user_query,
                chat_history=chat_history,
                stream_to_terminal=True,
                llm_backend=llm_backend
            )

            # add to history
            chat_history.append({"role": "user", "content": user_query})

    except KeyboardInterrupt:
        print("\nTake it easy... Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
