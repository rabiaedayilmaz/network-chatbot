AGENT_TOOLS = {
    "fixie": [
        {
            "type": "function",
            "function": {
                "name": "fixie_check_common_issues",
                "description": "Retrieves common network issue solutions from a knowledge base.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "fixie_check_router_troubleshooting",
                "description": "Retrieves router troubleshooting steps from technical manuals.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            },
        },
    ],
    "bytefix": [
        {
            "type": "function",
            "function": {
                "name": "bytefix_run_network_diagnostics",
                "description": "Runs advanced network diagnostic commands like ping, traceroute, and nslookup.",
                "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]},
            },
        }
    ],
    "routerx": [
        {
            "type": "function",
            "function": {
                "name": "routerx_configure_network",
                "description": "Provides recommended settings for routers, VLANs, and NAT configurations.",
                "parameters": {"type": "object", "properties": {"setting": {"type": "string"}}, "required": ["setting"]},
            },
        }
    ],
    "sentinel": [
        {
            "type": "function",
            "function": {
                "name": "sentinel_scan_network_security",
                "description": "Scans for potential security vulnerabilities in the network.",
                "parameters": {"type": "object", "properties": {"ip_range": {"type": "string"}}, "required": ["ip_range"]},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "sentinel_check_vpn_security",
                "description": "Analyzes VPN security settings to ensure secure tunneling.",
                "parameters": {"type": "object", "properties": {"vpn_provider": {"type": "string"}}, "required": ["vpn_provider"]},
            },
        }
    ],
    "hypernet": [
        {
            "type": "function",
            "function": {
                "name": "hypernet_run_speed_test",
                "description": "Performs an internet speed test and analyzes results.",
                "parameters": {"type": "object", "properties": {"server_location": {"type": "string"}}, "required": ["server_location"]},
            },
        }
    ],
    "professor_ping": [
        {
            "type": "function",
            "function": {
                "name": "professor_ping_explain_networking",
                "description": "Explains networking concepts in a simple way.",
                "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]},
            },
        }
    ],
}