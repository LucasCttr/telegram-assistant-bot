from duckduckgo_search import DDGS
from langchain_core.tools import tool


@tool("Search")
def search_tool(query: str) -> str:
    """Search the web and return a concise text summary of the top results."""
    query = query.strip()
    if not query:
        return "No search query was provided."

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
    except Exception as exc:
        return f"Search failed: {exc}"

    if not results:
        return "No results found."

    lines = []
    for index, result in enumerate(results, start=1):
        title = result.get("title") or "Untitled"
        body = result.get("body") or ""
        url = result.get("href") or result.get("url") or ""
        parts = [f"{index}. {title}"]
        if body:
            parts.append(body)
        if url:
            parts.append(url)
        lines.append("\n".join(parts))

    return "\n\n".join(lines)
