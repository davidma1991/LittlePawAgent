import httpx
from app.tools.base import ToolDef


async def _web_search(query: str, searxng_url: str, num_results: int = 5) -> list[dict]:
    params = {
        "q": query,
        "format": "json",
        "engines": "google,bing,duckduckgo",
        "language": "en",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(f"{searxng_url}/search", params=params)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])[:num_results]
            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                }
                for r in results
            ]
        except Exception as e:
            return [{"error": str(e), "title": "", "url": "", "content": ""}]


def make_web_search_tool(searxng_url: str) -> ToolDef:
    async def handler(query: str, num_results: int = 5) -> list[dict]:
        return await _web_search(query, searxng_url, num_results)

    return ToolDef(
        name="web_search",
        description="Search the web for information using SearXNG. Returns a list of results with title, URL, and content snippet.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
                "num_results": {"type": "integer", "description": "Number of results to return (default 5)", "default": 5},
            },
            "required": ["query"],
        },
        handler=handler,
        source="builtin",
    )
