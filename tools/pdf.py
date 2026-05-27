from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
import os

# Embeddings (se carga una sola vez)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Base de vectorstores por usuario { user_id: Chroma }
user_vectorstores = {}
PDF_STORE_DIR = os.path.join(os.path.dirname(__file__), "..", "database", "pdf_store")
PDF_STORE_DIR = os.path.abspath(PDF_STORE_DIR)
os.makedirs(PDF_STORE_DIR, exist_ok=True)


def _collection_name(user_id: int) -> str:
    return f"user_{user_id}"


def get_user_vectorstore(user_id: int) -> Chroma:
    """Return the in-memory cache or reopen the persisted collection for a user."""
    if user_id not in user_vectorstores:
        user_vectorstores[user_id] = Chroma(
            embedding_function=embeddings,
            collection_name=_collection_name(user_id),
            persist_directory=PDF_STORE_DIR,
        )
    return user_vectorstores[user_id]


def process_pdf(user_id: int, file_path: str) -> str:
    """Procesa un PDF y lo guarda en la vectorstore del usuario."""
    try:
        # 1. Cargar PDF
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()

        # 2. Dividir en chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)

        # 3. Guardar en vectorstore del usuario
        vectorstore = get_user_vectorstore(user_id)
        vectorstore.add_documents(chunks)
        user_vectorstores[user_id] = vectorstore

        return f"✅ PDF procesado correctamente. {len(chunks)} fragmentos indexados. ¡Ahora podés hacerme preguntas sobre el documento!"

    except Exception as e:
        return f"❌ Error procesando el PDF: {str(e)}"


def get_pdf_tool(user_id: int):
    """Crea una tool de búsqueda en PDF para un usuario específico."""

    @tool("buscar_en_pdf")
    def buscar_en_pdf(pregunta: str) -> str:
        """Busca información dentro del PDF que el usuario subió.
        Usá esta tool cuando el usuario pregunte sobre el contenido de su documento."""

        vectorstore = get_user_vectorstore(user_id)
        docs = vectorstore.as_retriever(search_kwargs={"k": 4}).invoke(pregunta)

        if not docs:
            return "No encontré información relevante en el PDF."

        resultado = "\n\n".join([d.page_content for d in docs])
        return f"Información encontrada en el PDF:\n{resultado}"

    return buscar_en_pdf
