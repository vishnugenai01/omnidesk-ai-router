# test_router.py — do not commit
from agent_graph import app_graph
from langchain_core.messages import HumanMessage

result = app_graph.invoke({"messages": [HumanMessage(content="Show me the food menu")]})
print(result["messages"][-1].content)

result2 = app_graph.invoke({"messages": [HumanMessage(content="What's my expense summary?")]})
print(result2["messages"][-1].content)
