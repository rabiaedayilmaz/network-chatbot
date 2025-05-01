import ollama
import re
import json
from typing import Tuple, Optional, Dict, Any
from utils.log import logger


def create_tool_selection_prompt(user_query: str) -> str:
    """
    Creates a prompt for the gemma3 model to select the appropriate Bytefix tool.
    """
    return f"""
    Kullanıcı sorusu: {user_query}

    Mevcut Bytefix araçları:
    - bytefix_run_network_diagnostics: Ping, traceroute ve nslookup çalıştırarak bir hedefe (hostname veya IP) karşı ağ teşhisi yapar.
        - parameters: target (str): Hedef hostname (.com gibi uzantı ile biten bir link) veya IP adresi. (örnek github.com, facebook.com, google.com etc.)

    Soru hangi Bytefix aracıyla en alakalı? Yanıtı TAM OLARAK şu formatta döndür:
    tool: <tool_name>
    parameters: {{"target": "<hedef_hostname_veya_IP>"}}
"""


def select_bytefix_tool(user_query: str, decider_model: str = "gemma3") -> Optional[Tuple[str, Optional[Dict[str, Any]]]]:
    """
    Selects the appropriate Bytefix tool based on the user's query.
    """
    # prompt and model response
    prompt = create_tool_selection_prompt(user_query)
    response = ollama.chat(
        model=decider_model,
        messages=[{"role": "user", "content": prompt}],
        stream=False
    )
    response_text = response["message"].get("content", "").strip()
    logger.info(f"Response of decider model - {response_text}")
    
    # tool name
    tool_pattern = r"tool:\s*(\w+)"
    tool_match = re.search(tool_pattern, response_text, re.IGNORECASE)
    selected_tool = tool_match.group(1) if tool_match else None
    
    # get parameters
    parameters = None
    params_pattern = r"parameters:\s*(\{.*?\}|\S+)"
    params_match = re.search(params_pattern, response_text, re.IGNORECASE | re.DOTALL)
    
    if params_match:
        params_text = params_match.group(1).strip()
        try:
            if params_text.startswith('{') and params_text.endswith('}'):
                parameters = json.loads(params_text)
            else:
                parameters = {"target": params_text}
                
                param_pairs = re.findall(r'(\w+):\s*([^,\n]+)', params_text)
                if param_pairs:
                    parameters = {k.strip(): v.strip() for k, v in param_pairs}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse parameters as JSON: {params_text}")
            if selected_tool == "bytefix_run_network_diagnostics":
                parameters = {"target": params_text.strip('"\'')}
    
    logger.info(f"Selected tool: {selected_tool}, Parameters: {parameters}")
    
    if not selected_tool:
        logger.warning("No valid Bytefix tool selected.")
        return None
    
    return selected_tool, parameters