from langchain_core.tools import tool
import httpx
from bs4 import BeautifulSoup

@tool("resumir_url")
def url_tool(url: str) -> str:
    """Extrae y devuelve el contenido de una URL. Usá esta tool cuando el usuario 
    mande un link o pida resumir una página web."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}  # evita bloqueos
        response = httpx.get(url, follow_redirects=True, timeout=10, headers=headers)
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Limpiar tags inútiles
        for tag in soup(["script", "style", "nav", "footer", "aside"]):
            tag.decompose()
        
        # Intentar sacar solo el contenido principal
        main = soup.find("article") or soup.find("main") or soup.body
        text = main.get_text(separator="\n", strip=True) if main else ""
        
        if not text:
            return "No pude extraer contenido de esa URL."
        
        return text[:6000]  # limitamos para no explotar el contexto

    except httpx.TimeoutException:
        return "La página tardó demasiado en responder."
    except Exception as e:
        return f"Error al acceder a la URL: {str(e)}"