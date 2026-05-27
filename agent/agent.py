from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from tools.search import search_tool
from tools.url import url_tool
from tools.pdf import get_pdf_tool
from agent.memory import get_memory

# Cache de agentes por usuario
_agents = {}

def get_llm(model: str):
    if model == "gemini-2.5-flash":
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    elif model == "groq-llama":
        return ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)

prompt = PromptTemplate.from_template("""Sos un asistente personal útil y amigable. Respondé siempre en español.
Tenés acceso a las siguientes tools:

{tools}

Usá este formato:

Question: la pregunta que tenés que responder
Thought: pensá qué hacer
Action: la tool a usar, debe ser una de [{tool_names}]
Action Input: el input para la tool
Observation: el resultado de la tool
Thought: ya sé la respuesta final
Final Answer: la respuesta final para el usuario

Importante:
- Si una búsqueda ya te da la información necesaria, respondé directamente con Final Answer.
- No repitas acciones innecesarias.
- Si el usuario manda una URL, usá resumir_url.
- Si el usuario pregunta sobre un documento, usá buscar_en_pdf.
- Si el usuario pregunta algo que no sabés, usá Search.

Question: {input}
Thought: {agent_scratchpad}""")

def get_agent(user_id: int, model: str):
    # Reutiliza el agente si ya existe para ese usuario
    if user_id in _agents:
        return _agents[user_id]

    llm = get_llm(model)
    memory = get_memory(user_id)
    pdf_tool = get_pdf_tool(user_id)
    
    tools = [search_tool, url_tool, pdf_tool]

    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        max_iterations=3,
        handle_parsing_errors=True,
    )

    _agents[user_id] = executor
    return executor

def reset_agent(user_id: int):
    """Llámalo cuando el usuario cambia de modelo."""
    if user_id in _agents:
        del _agents[user_id]