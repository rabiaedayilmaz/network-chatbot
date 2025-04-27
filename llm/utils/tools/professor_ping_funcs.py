async def draw_topology_diagram(scenario: str) -> str:
    """
    Creates an ASCII topology diagram based on the scenario description.
    Supports common topologies: star, bus, ring, mesh, tree, hybrid, fully connected.
    Selects the first matching topology keyword (case-insensitive).
    Defaults to a simple two-node link if no keywords match.
    """
    if not scenario or not isinstance(scenario, str):
        return "Invalid or empty scenario description."

    # normalize input
    s = scenario.strip().lower()

    # topology definitions with Turkish and English keywords
    topologies = {
        ("star", "yıldız"): (
            "      [Hub]       \n"
            "   / /  |  \\     \n"
            "[A] [B] [C] [D]  "
        ),
        ("bus", "omurga"): (
            "[A]---[B]---[C]---[D]---[E]"
        ),
        ("ring", "halka"): (
            "   [A]       [B]    \n"
            "  /   \\     /   \\  \n"
            "[E]   [C]---[D]    \n"
            "  \\         /      \n"
            "   \\-------/       "
        ),
        ("mesh", "örgü"): (
            "[A]-----[B]     \n"
            "| \\   / |      \n"
            "|  [C]  |      \n"
            "| /   \\ |      \n"
            "[D]-----[E]     "
        ),
        ("tree", "ağaç"): (
            "        [Root]         \n"
            "       /     \\        \n"
            "    [C1]     [C2]     \n"
            "    /  \\       \\     \n"
            "[L1] [L2]    [L3]    "
        ),
        ("hybrid", "karma"): (
            "      [Hub]          \n"
            "    /  |  \\         \n"
            "[A] [B] [Switch]---[C]\n"
            "            |         \n"
            "           [D]        "
        ),
        ("full", "fully connected", "tam"): (
            "  [A]---[B]         \n"
            "   | \\ / |          \n"
            "   |  X  |          \n"
            "   | / \\ |          \n"
            "  [C]---[D]         "
        )
    }

    # matching topology
    selected_diagram = None
    selected_keywords = []
    for keywords, diagram in topologies.items():
        if any(k in s for k in keywords):
            selected_diagram = diagram
            selected_keywords = keywords
            break
    if selected_diagram:
        # formatted output
        return f"Scenario: {"/".join(selected_keywords)}\n\n{selected_diagram}"