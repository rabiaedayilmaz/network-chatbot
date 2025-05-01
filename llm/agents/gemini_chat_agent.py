import google.generativeai as genai
from llm.utils.tools.tools import AGENT_TOOLS
from dataclasses import dataclass, field

import os
from google.generativeai import configure 
import re, json, asyncio

from utils.log import logger

from llm.utils.prompts import (
    FIXIE_PERSONA_PROMPT,
    BYTEFIX_PERSONA_PROMPT,
    ROUTERX_PERSONA_PROMPT,
    SENTINEL_PERSONA_PROMPT,
    HYPERNET_PERSONA_PROMPT,
    PROFESSOR_PING_PERSONA_PROMPT,
    get_system_prompt
)

from llm.utils.tools.hypernet_funcs import run_speed_test
from llm.utils.tools.professor_ping_funcs import draw_topology_diagram
from llm.utils.tools.bytefix_funcs import run_network_diagnostics
from llm.agents.rag_agent import RagAgent

from dotenv import load_dotenv
load_dotenv()


class AgentRouter:
    def __init__(self, agent_tools):
        self.agent_tools = agent_tools
        configure(api_key=os.environ.get("GOOGLE_API_KEY"))
        self.model_name = "models/gemini-2.0-flash"
        self.model = genai.GenerativeModel(self.model_name)
        # TODO: create class for each agent and use them here
        self.agent_instances = {
            "fixie": RagAgent(),
            }

    async def detect_agent_and_function(self, query):
        prompt = f"""
    You are a router for technical support agents. Based on the following user query, choose the best agent and function to handle it.

    Query: "{query}"

    
    Available Agents and their roles:
    - **Sentinel:** A vigilant network security expert. Specializes in providing security tips, explaining vulnerabilities, and offering advice on protecting networks. **Has NO tools.** Use for security advice queries, general security questions, or chat.
    - **RouterX:** An expert on network routing and configurations. Specializes in explaining routing protocols, subnetting, and router settings. **Has NO tools.** Use for routing concept questions, configuration explanations, or chat.
    - **Bytefix:** A diagnostic agent. Can run network diagnostic tools like ping and traceroute. Use for queries about network connectivity and reachability. {await self._describe_tools(agent_filter='bytefix')} 
    - **Hypernet:** A performance agent. Can run speed tests. Use for queries about network speed and bandwidth. {await self._describe_tools(agent_filter='hypernet')}
    - **Professor Ping:** An educational agent. Can help visualize network topology. Use for queries about network mapping or diagrams. {await self._describe_tools(agent_filter='professor_ping')}
    - **Fixie:** A general troubleshooting agent. Can use a knowledge base to answer questions about common network issues. Use for general troubleshooting questions. {await self._describe_tools(agent_filter='fixie')}


    Respond in JSON format (no explanation, just the JSON): {{
        "agent": "agent_name",
        "function": "function_name",
        "parameters": {{"param1": "value", ...}}
    }}
    """

        response = self.model.generate_content(prompt)
        response_text = response.text.strip()

        # extract json block or fallback
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
        json_str = match.group(1) if match else response_text

        try:
            result = json.loads(json_str)
            return result
        except Exception as e:
            raise ValueError(f"Invalid Gemini response: {response_text}") from e

    async def execute_function(self, agent_name, function_name, parameters):
            logger.info(f"Selected agent:{agent_name}")
            logger.info(f"Executing function {function_name} with parameters: {parameters}")                

            func = None

            # if agent is class, get the instance
            agent_instance = self.agent_instances.get(agent_name) 

            if agent_instance:
                # get function_name as a method from it
                func = getattr(agent_instance, function_name, None)
                if func and callable(func): # if callable, set it
                    logger.debug(f"Found method '{function_name}' on agent instance '{agent_name}'")
                else:
                    # not found or not callable, set func to None
                    func = None
                    logger.warning(f"Method '{function_name}' not found or not callable on agent instance '{agent_name}'.")


            # if not instance, look for global functions (imported from tools folder)
            if func is None:
                func = globals().get(function_name)
                if func and callable(func): # ensure it's callable
                    logger.debug(f"Found global function '{function_name}'")
                else:
                    # not found or not callable, set func to None
                    func = None
                    logger.warning(f"Global function '{function_name}' not found or not callable.")


            # if still func None, raise error
            if not func:
                raise NotImplementedError(f"Function '{function_name}' for agent '{agent_name}' not implemented or found.")

            # TODO: make async all functions
            # call first if async function
            if asyncio.iscoroutinefunction(func):
                return await func(**parameters)
            # else call it directly, sync function
            else:
                return func(**parameters)


    async def route_query(self, query, language_mode="tr"):
        # TODO: create class for each agent and use them here
        route = await self.detect_agent_and_function(query)
        logger.info(f"Routing query: {query} to agent: {route['agent']} with function: {route['function']} and parameters: {route['parameters']}")
        if route["agent"].lower() in ("sentinel", "routerx"):
            user_response = await self.generate_user_response(query, route["parameters"], agent_name=route["agent"], language_mode=language_mode)
            return {
                "raw": route["parameters"],
                "response": user_response
            }
        
        result = await self.execute_function(route["agent"], route["function"], route["parameters"])
        
        # if list of tools, convert to dict
        if not isinstance(result, dict):
            result = {route["function"]: result}
        
        user_response = await self.generate_user_response(query, result, agent_name=route["agent"], language_mode=language_mode)
        
        return {
            "raw": result,
            "response": user_response
        }


    async def _describe_tools(self, agent_filter=None):
        filtered_tools = self.agent_tools[agent_filter]
        description = ""
        description += f"\nAgent: {agent_filter}"
        for tool in filtered_tools:
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
        persona_prompt = system_prompt + persona_prompts.get(agent_name.lower(), "fixie")

        prompt = f"""
    {persona_prompt}

    The user asked: "{query}"

    Here are the results of the diagnostics:
    {results}

    Now, write a response to the user.
    """

        response = self.model.generate_content(prompt)
        return response.text.strip()

async def main():
    router = AgentRouter(agent_tools=AGENT_TOOLS)

    #query = "ağ güvenliği taraması yapabilir misin 8.8.8.8"
    #query = "internet hız testi yapabilir misin"
    query = "ağ yapılandırma"
    result = await router.route_query(query)
    print("\n=== User-friendly response ===")
    print(result["response"])
    print("\n=== Raw tool output ===")
    print(json.dumps(result["raw"], indent=2))



if __name__ == "__main__":
    asyncio.run(main())

