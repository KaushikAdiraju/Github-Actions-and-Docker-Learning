from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # 'add_messages' ensures that when a new message is generated, 
    # it is appended to the list rather than overwriting the old ones.
    messages: Annotated[list, add_messages]