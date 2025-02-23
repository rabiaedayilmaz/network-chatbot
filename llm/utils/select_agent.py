import ollama
from llm.utils.tools import AGENT_TOOLS


def select_agent(user_query: str, decider_model: str = "llama3.2:1b"):
    """
    Select the appropriate AI agent 
    Return: agent: str
    """
    
    response = ollama.chat(
        model=decider_model,
        messages=[{"role": "user", "content": user_query}],
        tools=[tool for tools in AGENT_TOOLS.values() for tool in tools],
    )

    # extract the selected agent
    tool_calls = response["message"].get("tool_calls", [])
    if tool_calls:
        selected_tool = tool_calls[0]["function"]["name"]
        for agent, tools in AGENT_TOOLS.items():
            if any(tool["function"]["name"] == selected_tool for tool in tools):
                return agent
    
    return "fixie"  # default agent is Fixie - basic support agent
