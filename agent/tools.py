from langchain_community.tools.tavily_search import TavilySearchResults

# Initialize the Tavily search tool. 
# max_results=3 keeps the context window small and the response fast.
tavily_tool = TavilySearchResults(max_results=3)

# Group all tools into a list so they can be easily bound to the LLM
tools = [tavily_tool]