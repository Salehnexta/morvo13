"""Tool for interacting with the Perplexity API."""

from crewai_tools import BaseTool  # type: ignore


class PerplexityTool(BaseTool):
    name: str = "Perplexity Search"
    description: str = (
        "Performs a search using the Perplexity API to gather real-time web intelligence."
    )

    def _run(self, query: str) -> str:
        """Synchronous run method for the tool."""
        # In a real implementation, this would call the Perplexity API.
        print(f"--- Running PerplexityTool with query: {query} ---")
        return f"Placeholder results for Perplexity query: '{query}'"

    async def _arun(self, query: str) -> str:
        """Asynchronous run method for the tool."""
        # In a real implementation, this would call the Perplexity API asynchronously.
        print(f"--- Running PerplexityTool asynchronously with query: {query} ---")
        return f"Placeholder async results for Perplexity query: '{query}'"
