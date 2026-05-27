from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool

# Embeddings (se carga una sola vez)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Base de vectorstores por usuario { user_id: Chroma }
user_vectorstores = {}


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
        vectorstore = Chroma(
            embedding_function=embeddings,
            collection_name=f"user_{user_id}",  # colección separada por usuario
        )
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

        if user_id not in user_vectorstores:
            return "El usuario no ha subido ningún PDF todavía."

        retriever = user_vectorstores[user_id].as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(pregunta)

        if not docs:
            return "No encontré información relevante en el PDF."

        resultado = "\n\n".join([d.page_content for d in docs])
        return f"Información encontrada en el PDF:\n{resultado}"

    return buscar_en_pdf
