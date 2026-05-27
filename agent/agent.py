from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from tools.search import search_tool
from agent.memory import get_memory

def get_llm(model: str):
    if model == "gemini-2.5-flash":
        return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    elif model == "groq-llama":
        return ChatGroq(model="llama-3.1-8b-instant", temperature=0.1)
    elif model == "groq-mixtral":
        return ChatGroq(model="mixtral-8x7b-32768", temperature=0.1)

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
- Si una búsqueda ya te da la información necesaria, respondé directamente con `Final Answer`.
- No repitas acciones innecesarias.

Question: {input}
Thought: {agent_scratchpad}""")

def get_agent(user_id: int, model: str):
    llm = get_llm(model)
    memory = get_memory(user_id)
    agent = create_react_agent(llm, [search_tool], prompt)
    return AgentExecutor(
        agent=agent,
        tools=[search_tool],
        memory=memory,
        verbose=True,
        max_iterations=3,
        handle_parsing_errors=True,
    )