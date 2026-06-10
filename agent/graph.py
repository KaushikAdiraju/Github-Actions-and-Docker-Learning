from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition

# Import the state and the nodes we defined in the other files
from agent.state import AgentState
from agent.nodes import call_model, tool_node

# 1. Initialize the graph with our state schema
workflow = StateGraph(AgentState)

# 2. Add the nodes to the graph (the workers)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# 3. Define the starting point
workflow.add_edge(START, "agent")

# 4. Define the routing logic (Does the LLM want to search the web?)
workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        # If the LLM wants to use a tool, route to the "tools" node
        "tools": "tools",
        # If the LLM just answered normally, route to END
        END: END
    }
)

# 5. After the tools finish executing, route back to the agent 
# so the LLM can read the search results and formulate a final answer.
workflow.add_edge("tools", "agent")

# 6. Compile the graph into an executable application
# THIS is the variable that Flask imports!
app = workflow.compile()