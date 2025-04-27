import ollama
import re
from llm.utils.tools.tools import AGENT_TOOLS
from utils.log import logger

def create_selection_prompt(user_query: str) -> str:
    return f"""
    Kullanıcı sorusu: {user_query}
    Mevcut ajanlar ve araçlar:
    - fixie: ortak ağ sorunları, yönlendirici sorun giderme
    - bytefix: ağ teşhisi, ağ sorunları giderme testi, diagnostik test
    - routerx: ağ yapılandırma
    - sentinel: ağ güvenliği tarama, VPN güvenliği
    - hypernet: hız testi
    - professor_ping: ağ kavramlarını açıklama, topoloji diyagramı çizme
    Soru hangi ajanla en alakalı? Yanıtı TAM OLARAK şu formatta döndür:
    agent: <agent_name>
    """

def parse_agent_response(response_text: str) -> str | None:
    match = re.search(r"agent:\s*(\w+)", response_text, re.IGNORECASE)
    return match.group(1) if match else None

def fallback_to_tool_calls(response) -> str | None:
    tool_calls = response["message"].get("tool_calls", [])
    if tool_calls:
        selected_tool = tool_calls[0]["function"]["name"]
        for agent, tools in AGENT_TOOLS.items():
            if any(tool["function"]["name"] == selected_tool for tool in tools):
                return agent
    return None

def select_agent(user_query: str, decider_model: str = "gemma3") -> str:
    prompt = create_selection_prompt(user_query)
    
    response = ollama.chat(
        model=decider_model,
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )

    response_text = response["message"].get("content", "").strip()
    logger.info(f"Response of decider model - {response_text}")

    selected_agent = parse_agent_response(response_text)

    if not selected_agent or selected_agent not in AGENT_TOOLS:
        selected_agent = fallback_to_tool_calls(response)

    if selected_agent in AGENT_TOOLS:
        return selected_agent

    logger.warning("No valid agent selected, defaulting to fixie")
    return "fixie"  # Default agent

if __name__ == "__main__":
    #user_query = "bana ağ güvenliği konseptini açıklayabilir misin?"
    user_query = "internet hızımı nasıl test edebilirim?"
    selected_agent = select_agent(user_query)
    print(f"Selected agent: {selected_agent}")
