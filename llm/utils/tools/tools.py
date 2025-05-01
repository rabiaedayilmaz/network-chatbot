AGENT_TOOLS = {
    "fixie": [
        {
            "type": "function",
            "function": {
                "name": "call_rag_tool",
                "description": "Retrieves common home network issue solutions from a knowledge base.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "dataset_id": "common_home_network_problems", "tool_name": "check_common_issues"}, "required": ["query"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "call_rag_tool",
                "description": "Retrieves router troubleshooting steps from technical manuals.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "dataset_id": "network_troubleshooting", "tool_name": "check_router_troubleshooting"}, "required": ["query"]},
            },
        },
    ],
    "bytefix": [
        {
            "type": "function",
            "function": {
                "name": "run_network_diagnostics",
                "description": "Runs advanced network diagnostic commands like ping, traceroute, and nslookup.",
                "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]},
            },
        },
        
    ],
    "hypernet": [
        {
            "type": "function",
            "function": {
                "name": "run_speed_test",
                "description": "Performs an internet speed test and analyzes results.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            },
        }
    ],
    "professor_ping": [
        {
            "type": "function",
            "function": {
            "name": "draw_topology_diagram",
            "description": "Creates an ASCII network topology diagram for a given scenario.",
            "parameters": {
                "type": "object",
                "properties": {
                "scenario": {"type": "string"}
                },
                "required": ["scenario"]
            }
            }
        }
    ],
}