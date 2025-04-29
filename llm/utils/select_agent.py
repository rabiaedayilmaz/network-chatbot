import ollama
import re
from llm.utils.tools.tools import AGENT_TOOLS
from utils.log import logger

def create_selection_prompt(user_query: str) -> str:
    agent_capabilities = """
    - fixie: Ortak ağ sorunları (yavaş hız, kopmalar, Wi-Fi), yönlendirici sorun giderme, ISP görüşmesi için hazırlık. Kullanıcı dostu, adım adım çözümler.
    - bytefix: Teknik kullanıcılar için. DNS, traceroute, ping, paket kaybı gibi websiteleri için teşhis görevlerini yapar.
    - routerx: Routing, switching, VLAN, NAT ve firewall yapılandırması. Ayrıca WAN/LAN trafiğinde politikaya dayalı yönlendirme ve QoS optimizasyonu sağlar.
    - sentinel: Ağ güvenliği, Wi-Fi güvenliği, güvenlik duvarları, IDS/IPS, VPN'ler, siber tehditler (phishing, malware), pratik güvenlik adımları.
    - hypernet: İnternet hızı optimizasyonu, Wi-Fi yerleşimi/kanalları, hız testleri, gecikme/jitter sorunları, hızlı ve etkili çözümler.
    - professor_ping: Ağ kavramlarını açıklar (IP, DNS, TCP/IP, subnetting), topoloji çizer, temel başlangıç seviyesi sorun giderme. Eğlenceli, benzetmeler kullanır.
    """

    return f"""
    Aşağıdaki kullanıcı sorgusu için, belirtilen ajanlar ve yetenekleri arasından en uygun olanı seçin.
    Ajan seçiminizi yaparken kullanıcının sorusunun içeriği ve teknik seviyesini dikkate alın.

    Kullanıcı Sorgusu: {user_query}

    Mevcut Ajanlar ve Yetenekleri:
    {agent_capabilities.strip()}

    Sorgu hangi ajanla en alakalı? Lütfen sadece seçilen ajanın adını TAM OLARAK şu formatta döndürün:
    agent: <ajan_adı>
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
