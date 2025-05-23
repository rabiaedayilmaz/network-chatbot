from llm.utils.prompts import *
from llm.utils.tools.tools import AGENT_TOOLS
from llm.agents.rag_agent import RagAgent
from llm.agents.gemini_chat_agent import GeminiChatAgent

from llm.utils.tools.hypernet_funcs import run_speed_test
from llm.utils.tools.professor_ping_funcs import draw_topology_diagram
from llm.utils.tools.bytefix_funcs import run_network_diagnostics
from llm.agents.base_chat_agent import BaseChatAgent

import asyncio
import json
from utils.log import logger

class AgentRouter(BaseChatAgent):
    def __init__(self, session_id: str = "", language_mode: str = "tr", agent_tools: dict = AGENT_TOOLS, chat_agent=None):
        super().__init__(session_id=session_id, language_mode=language_mode)
        self.agent_tools = agent_tools
        self.chat_agent = chat_agent or GeminiChatAgent()
        # TODO: make all agents as class instances like fixie, hypernet, etc.
        self.agent_instances = {
            "fixie": RagAgent(),
        }

    async def detect_agent_and_function(self, query):
        prompt = f"""
        You are an expert router that selects the **most appropriate** technical support agent based **strictly** on their specialization. Do not choose Fixie unless **no other agent is a clear fit**.

        Query: "{query}"

        Agent Roles:
        - **Sentinel:** Handles network **security** questions directly (no tools).
        - **RouterX:** Handles **routing and configuration** issues directly (no tools).
        - **Bytefix:** Diagnoses issues using tools. {await self._describe_tools('bytefix')}
        - **Hypernet:** Performance optimization expert. {await self._describe_tools('hypernet')}
        - **Professor Ping:** Explains technical concepts. {await self._describe_tools('professor_ping')}
        - **Fixie:** General fallback. Only choose Fixie if **none of the above agents apply** {await self._describe_tools('fixie')}

        Respond in pure JSON (no explanation):
        {{"agent": "agent_name", "function": "function_name", "parameters": {{...}}}}
        """
        return self.chat_agent.generate_json_response(prompt)

    async def execute_function(self, agent_name, function_name, parameters):
        logger.info("Selected agent: %s", agent_name)
        logger.info(f"Executing function {function_name} with parameters: {parameters}")
        func = None

        # all agent tools are functions
        # but fixie uses RagAgent class, use class instance 
        # so that from class instance we can call the function

        # TODO: make all agents as class instances like fixie, hypernet, etc.
        agent_instance = self.agent_instances.get(agent_name.lower())
        if agent_instance:
            func = getattr(agent_instance, function_name, None)
            if callable(func):
                logger.debug(f"Calling '{function_name}' from instance of agent '{agent_name}'")
            else:
                logger.warning(f"Method '{function_name}' not found or not callable on agent instance '{agent_name}'")
                func = None

        # look for globally imported tool functions (from llm/utils/tools/*.py)
        if func is None:
            func = globals().get(function_name)
            if callable(func):
                logger.debug(f"Calling global function '{function_name}'")
            else:
                logger.error(f"Function '{function_name}' not implemented or not callable.")
                raise NotImplementedError(f"Function '{function_name}' for agent '{agent_name}' not implemented or found.")

        # support both async and sync functions
        # TODO: use only asyync functions
        return await func(**parameters) if asyncio.iscoroutinefunction(func) else func(**parameters)

    async def ask_agent(self, query, chat_history, language_mode="tr"):
        # agent and function to route to
        route = await self.detect_agent_and_function(query)
        logger.info(f"Routing query to: {route}")

        if route["agent"].lower() in ("sentinel", "routerx"):
            user_response = await self.generate_user_response(query, route["parameters"], route["agent"], language_mode)

            chat_history.append({"role": "user", "content": query})
            chat_history.append({"role": "assistant", "content": user_response})
            return {
                    "raw": route["parameters"],
                    "response": user_response,
                    "agent": route["agent"],               
                    "function": route["function"],          
                    "chat_history": chat_history
                }

        result = await self.execute_function(route["agent"], route["function"], route["parameters"])
        result = {route["function"]: result} if not isinstance(result, dict) else result
        user_response = await self.generate_user_response(query, result, route["agent"], language_mode)

        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": user_response})

        return {"raw": result, "response": user_response, "agent": route["agent"], "function": route["function"], "chat_history": chat_history}

    async def _describe_tools(self, agent_filter):
        tools = self.agent_tools[agent_filter]
        description = f"\nAgent: {agent_filter}"
        for tool in tools:
            fn = tool["function"]
            description += f'\n  Function: {fn["name"]}\n    Description: {fn["description"]}\n    Parameters: {fn["parameters"]}'
        return description

    async def generate_user_response(self, query, results, agent_name="fixie", language_mode="tr"):
        persona_prompts = {
            "fixie": FIXIE_PERSONA_PROMPT,
            "bytefix": BYTEFIX_PERSONA_PROMPT,
            "routerx": ROUTERX_PERSONA_PROMPT,
            "sentinel": SENTINEL_PERSONA_PROMPT,
            "hypernet": HYPERNET_PERSONA_PROMPT,
            "professor ping": PROFESSOR_PING_PERSONA_PROMPT,
        }
        system_prompt = get_system_prompt(language_mode)
        persona_prompt = system_prompt + persona_prompts.get(agent_name.lower(), FIXIE_PERSONA_PROMPT)
        prompt = f"""
{persona_prompt}
The user asked: "{query}"

Here are the results of the diagnostics:
{results}

Now, write a response to the user.
"""
        return self.chat_agent.generate_text_response(prompt)

async def main():
    from llm.utils.tools.tools import AGENT_TOOLS
    router = AgentRouter(agent_tools=AGENT_TOOLS, chat_agent=GeminiChatAgent())
    query = "ağ yapılandırma"
    result = await router.ask_agent(query)
    print("\n=== User-friendly response ===")
    print(result["response"])
    print("\n=== Raw tool output ===")
    print(json.dumps(result["raw"], indent=2))

if __name__ == "__main__":
    import asyncio, os
    os.environ["STREAMLIT_WATCHER_DISABLE"] = "true"
    asyncio.run(main())
