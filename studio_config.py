"""
LangGraph Studio Configuration for Economic Analysis System
This file exports the compiled graph for LangGraph Studio
"""

try:
    from langgraph_economic_agent import LangGraphEconomicAgent
    
    # Create agent instance and get the compiled graph
    agent = LangGraphEconomicAgent()
    graph = agent.graph
    
    # Export the graph for LangGraph Studio
    __all__ = ["graph"]
    
except Exception as e:
    print(f"Error creating graph: {e}")
    raise