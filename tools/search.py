import re

from ddgs import DDGS
from langchain_core.tools import tool


STOPWORDS = {
    "a",
    "al",
    "con",
    "de",
    "del",
    "el",
    "en",
    "hoy",
    "la",
    "las",
    "los",
    "para",
    "por",
    "que",
    "un",
    "una",
    "y",
}


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z0-9áéíóúñü]+", text.lower())
    return {w for w in words if len(w) >= 3 and w not in STOPWORDS}


def _is_relevant(result: dict, tokens: set[str]) -> bool:
    if not tokens:
        return True
    haystack = " ".join(
        [
            str(result.get("title") or "").lower(),
            str(result.get("body") or "").lower(),
        ]
    )
    return any(token in haystack for token in tokens)


def _format_results(results: list[dict]) -> str:
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


@tool("Search")
def search_tool(query: str) -> str:
    """Search the web and return a concise text summary of the top results."""
    query = query.strip()
    if not query:
        return "No search query was provided."

    tokens = _tokenize(query)
    query_variants = [query]
    if "btc" in query.lower():
        query_variants.append(query.lower().replace("btc", "bitcoin"))

    try:
        with DDGS() as ddgs:
            fallback_results = []
            for current_query in query_variants:
                results = list(
                    ddgs.text(
                        current_query,
                        max_results=8,
                        region="ar-es",
                        safesearch="off",
                    )
                )
                if results and not fallback_results:
                    fallback_results = results
                relevant = [r for r in results if _is_relevant(r, tokens)]
                if relevant:
                    return _format_results(relevant[:5])

            if fallback_results:
                return _format_results(fallback_results[:5])

            news_results = list(
                ddgs.news(
                    query,
                    max_results=5,
                    region="ar-es",
                    safesearch="off",
                )
            )
            if news_results:
                return _format_results(news_results)
    except Exception as exc:
        return f"Search failed: {exc}"

    return "No relevant results found."
