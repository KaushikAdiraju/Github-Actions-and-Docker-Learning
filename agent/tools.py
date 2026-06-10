import os
from langchain_community.utilities import SearxSearchWrapper
from langchain_community.tools import SearxSearchResults

# Dynamically read the URL from the environment variables, fallback to localhost if missing
searx_host_url = os.environ.get("SEARXNG_URL", "http://localhost:8080")

searx_wrapper = SearxSearchWrapper(searx_host=searx_host_url)
searx_tool = SearxSearchResults(wrapper=searx_wrapper, max_results=3)
tools = [searx_tool]