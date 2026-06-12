import networkx as nx


async def plan_route():
    G = nx.Graph()

    G.add_edge("HQ", "Hospital", weight=5)
    G.add_edge("HQ", "Relief Camp", weight=3)
    G.add_edge("Relief Camp", "Hospital", weight=2)

    shortest = nx.shortest_path(
        G,
        source="HQ",
        target="Hospital",
        weight="weight"
    )

    return {
        "route": shortest,
        "message": f"Optimal route: {' -> '.join(shortest)}"
    }