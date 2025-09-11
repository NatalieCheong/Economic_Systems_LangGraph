from langgraph_economic_agent import LangGraphEconomicAgent

# Export your graph for Studio
agent = LangGraphEconomicAgent()
graph = agent.graph

# This makes it available to Studio
__all__ = ["graph"]