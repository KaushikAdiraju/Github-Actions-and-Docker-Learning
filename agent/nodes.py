import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import ToolNode
from agent.tools import tools
from agent.state import AgentState

# Initialize the LLM
# If using Ollama, comment out the Groq line and use:
# from langchain_community.chat_models import ChatOllama
# llm = ChatOllama(model="llama3.1", temperature=0)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Bind the tools to the LLM so it knows it has the ability to search the web
llm_with_tools = llm.bind_tools(tools)

def call_model(state: AgentState):
    """This node passes the current conversation history to the LLM."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    
    # We return a dictionary because LangGraph will take this and 
    # update the AgentState with the new message.
    return {"messages": [response]}

# LangGraph provides a prebuilt ToolNode that automatically handles
# executing the tool if the LLM requests it.
tool_node = ToolNode(tools)