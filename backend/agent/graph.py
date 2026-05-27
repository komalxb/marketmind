from langgraph.graph import StateGraph, END
from .state import ResearchState
from .nodes import plan_node, search_node, evaluate_node, synthesize_node

def should_continue(state: ResearchState) -> str:
    """
    Router function — decides whether to search again or synthesize.
    Always exits after 2 iterations to prevent infinite loops.
    """
    if state["evaluation"] == "sufficient":
        return "synthesize"
    elif state["iterations"] >= 2:
        return "synthesize"
    else:
        return "search"


def build_graph():
    # Initialize the graph with our state object
    graph = StateGraph(ResearchState)
    
    # Add all nodes
    graph.add_node("plan", plan_node)
    graph.add_node("search", search_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("synthesize", synthesize_node)
    
    # Set the entry point
    graph.set_entry_point("plan")
    
    # Add linear edges
    graph.add_edge("plan", "search")
    graph.add_edge("search", "evaluate")
    graph.add_edge("synthesize", END)
    
    # Add conditional edge from evaluate
    graph.add_conditional_edges(
        "evaluate",
        should_continue,
        {
            "search": "search",
            "synthesize": "synthesize"
        }
    )
    
    return graph.compile()


# Compiled graph instance
research_graph = build_graph()