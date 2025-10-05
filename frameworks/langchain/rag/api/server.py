"""
╔════════════════════════════════════════════════════════════════════════════╗
║                          📑 RAG con LangChain 🦜 🔗                         ║
╚════════════════════════════════════════════════════════════════════════════╝ 

Este servidor implementa un sistema RAG (Retrieval Augmented Generation) con:
- Router inteligente que decide cuándo usar RAG o responder directamente
- Historial de conversación persistente (gestión automática)
- Búsqueda semántica en Qdrant
"""

import os
from flask import Flask, request, jsonify
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from rich.console import Console
from dotenv import load_dotenv
from models import RouteDecision

#══════════════════════════════════════════════════════════════════════════════
# 🔧 CONFIGURACIÓN INICIAL
#══════════════════════════════════════════════════════════════════════════════

load_dotenv()
app = Flask(__name__, static_folder='../web', static_url_path='')
console = Console()

# Constantes
K_DOCUMENTS = 3
MAX_HISTORY_MESSAGES = 6
COLLECTION_NAME = "youtube_guides"

# Directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, "message_history.sqlite")

console.print("\n[bold cyan]🚀 Iniciando servidor RAG...[/bold cyan]\n")

#══════════════════════════════════════════════════════════════════════════════
# 🤖 MODELOS LLM
#══════════════════════════════════════════════════════════════════════════════

console.print("📋 Configurando modelos...")
llm_router = init_chat_model(
    model=os.getenv("LLM_ROUTER_MODEL_ID"),
    model_provider=os.getenv("MODEL_PROVIDER", "openai"),
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("ENDPOINT_URL"),
)

llm_answer = init_chat_model(
    model=os.getenv("LLM_ANSWER_MODEL_ID"),
    model_provider=os.getenv("MODEL_PROVIDER", "openai"),
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("ENDPOINT_URL"),
)
console.print("   ✓ Modelos configurados\n")

#══════════════════════════════════════════════════════════════════════════════
# 📝 PROMPTS Y CADENAS
#══════════════════════════════════════════════════════════════════════════════

# Router: decide si usar RAG o responder directamente
router_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un clasificador. Decide si la pregunta NECESITA búsqueda externa (retrieve) "
     "o se puede responder con conocimiento general (direct). "
     "Responde SOLO en JSON con: action, rationale. "
     "Reglas: retrieve=preguntas sobre YouTube; direct=saludos, chit-chat, etc."),
    ("user", "Pregunta: {question}\nContexto: {chat_hint}\nDevuélveme JSON.")
])
router = router_prompt | llm_router | JsonOutputParser(pydantic_object=RouteDecision)

# Cadena directa (sin RAG)
direct_prompt = ChatPromptTemplate.from_messages([
    ("system", "Responde con precisión usando tu conocimiento general."),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])
direct_chain = direct_prompt | llm_answer

# Cadena RAG (con documentos)
rag_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un asistente experto. Responde basándote en el contexto proporcionado.\n"
     "Contexto:\n{context}"),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])
rag_chain = rag_prompt | llm_answer

#══════════════════════════════════════════════════════════════════════════════
# 🗄️ VECTOR STORE (Qdrant)
#══════════════════════════════════════════════════════════════════════════════

console.print("🔍 Configurando Vector Store...")
api_key = os.getenv("API_KEY", "dummy-key")
embeddings_model = os.getenv("EMBEDDINGS_MODEL_ID", "text-embedding-3-small")

embeddings = OpenAIEmbeddings(
    model=embeddings_model,
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=api_key
)

# Determinar dimensionalidad
if "embeddinggemma" in embeddings_model:
    vector_size = 768
elif "text-embedding-3-large" in embeddings_model:
    vector_size = 3072
elif "text-embedding-3-small" in embeddings_model:
    vector_size = 1536
else:
    vector_size = 768

client = QdrantClient("http://qdrant:6333")

# Crear colección si no existe
if not client.collection_exists(COLLECTION_NAME):
    console.print(f"   ⚠️  Colección '{COLLECTION_NAME}' no existe. Creando...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)
console.print("   ✓ Vector Store listo\n")

#══════════════════════════════════════════════════════════════════════════════
# 🔄 GESTIÓN AUTOMÁTICA DE HISTORIAL
#══════════════════════════════════════════════════════════════════════════════

def get_history(session_id: str):
    """Factoría: retorna historial para una sesión"""
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=f"sqlite:///{DB_FILE}"
    )

# Envolver cadenas con gestión automática de historial
direct_chain_with_history = RunnableWithMessageHistory(
    direct_chain,
    get_history,
    input_messages_key="input",
    history_messages_key="history",
)

rag_chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    get_history,
    input_messages_key="input",
    history_messages_key="history",
)

console.print("🔄 Gestión automática de historial configurada\n")

#══════════════════════════════════════════════════════════════════════════════
# 🔧 FUNCIONES AUXILIARES
#══════════════════════════════════════════════════════════════════════════════

def retrieve(query):
    """Recupera documentos relevantes del vector store"""
    docs = vector_store.similarity_search(query, k=K_DOCUMENTS)
    console.print(f"   🔍 Documentos recuperados: {len(docs)}")
    return docs


def format_docs(docs):
    """Formatea documentos como texto para el contexto"""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def build_chat_hint(messages):
    """Construye un hint del historial para el router"""
    if len(messages) < 2:
        return ""
    recent = messages[-MAX_HISTORY_MESSAGES:]
    hint_parts = []
    for msg in recent:
        role = "Usuario" if msg.type == "human" else "Asistente"
        content_preview = msg.content[:100]
        hint_parts.append(f"{role}: {content_preview}")
    return " | ".join(hint_parts)


def decide_route(question, chat_hint=""):
    """Clasifica la pregunta usando el router LLM"""
    try:
        result = router.invoke({
            "question": question,
            "chat_hint": chat_hint or "Sin contexto previo"
        })
        action = result.get("action", "direct")
        rationale = result.get("rationale", "Sin explicación")
        console.print(f"   🤖 Decisión: [bold]{action}[/bold] - {rationale}")
        return action, rationale
    except Exception as e:
        console.print(f"   ⚠️  Error en router: {str(e)}")
        return "direct", f"Error: {str(e)}"


def run_retrieve_chain(question, session_id):
    """Ejecuta la cadena RAG completa"""
    console.print("   📚 Ejecutando cadena RAG...")
    try:
        # Recuperar documentos
        retrieved_docs = retrieve(question)
        context = format_docs(retrieved_docs)

        # Generar respuesta con historial automático
        response = rag_chain_with_history.invoke(
            {"input": question, "context": context},
            config={"configurable": {"session_id": session_id}}
        )

        # Formatear referencias únicas
        unique_sources = {}
        for doc in retrieved_docs:
            url = doc.metadata.get("source", "Sin fuente")
            if url not in unique_sources:
                unique_sources[url] = {
                    "source": url,
                    "title": doc.metadata.get("title", "Documento"),
                    "content_preview": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                }

        references = [
            {**data, "id": i}
            for i, (url, data) in enumerate(unique_sources.items(), 1)
        ]

        return {"content": response.content, "references": references}

    except Exception as e:
        console.print(f"   ❌ Error en RAG: {str(e)}")
        return {
            "content": f"Error al buscar en documentos: {str(e)}",
            "references": []
        }


def run_direct_chain(question, session_id):
    """Ejecuta la cadena directa (sin RAG)"""
    console.print("   ⚡ Ejecutando cadena directa...")
    try:
        response = direct_chain_with_history.invoke(
            {"input": question},
            config={"configurable": {"session_id": session_id}}
        )
        return {"content": response.content, "references": None}
    except Exception as e:
        console.print(f"   ❌ Error: {str(e)}")
        return {"content": f"Error: {str(e)}", "references": None}


# Mapa de acciones
ACTION_HANDLERS = {
    "retrieve": run_retrieve_chain,
    "direct": run_direct_chain,
}

#══════════════════════════════════════════════════════════════════════════════
# 🌐 ENDPOINTS DE LA API
#══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Página principal - interfaz web"""
    return app.send_static_file('index.html')


@app.route('/<path:filename>')
def static_files(filename):
    """Archivos estáticos (CSS, JS, etc.)"""
    return app.send_static_file(filename)


@app.route("/chat", methods=["POST"])
def chat_invoke():
    """
    💬 Endpoint principal del chat
    
    Request: {"session_id": "...", "message": "..."}
    Response: {"session_id": "...", "reply": "...", "routing": {...}, "references": [...]}
    """
    console.print("\n" + "="*80)
    console.print("[bold cyan]📨 Nueva petición al chat[/bold cyan]")
    console.print("="*80)

    try:
        data = request.get_json(force=True)
        session_id = data.get("session_id")
        user_text = data.get("message", "")

        if not session_id or not user_text:
            return jsonify({"error": "session_id y message son requeridos"}), 400

        console.print(f"   👤 Session: {session_id[:8]}...")
        console.print(f"   💬 Mensaje: {user_text[:100]}...")

        # Construir hint del historial para el router
        message_history = SQLChatMessageHistory(
            session_id=session_id,
            connection=f'sqlite:///{DB_FILE}'
        )
        chat_hint = build_chat_hint(message_history.messages)

        # Clasificar pregunta
        console.print("\n   🎯 Clasificando pregunta...")
        action, rationale = decide_route(user_text, chat_hint)

        # Ejecutar handler correspondiente (historial automático)
        console.print(f"\n   ⚙️  Ejecutando handler '{action}'...")
        handler = ACTION_HANDLERS.get(action, run_direct_chain)
        result = handler(user_text, session_id)

        # Preparar respuesta
        response_data = {
            "session_id": session_id,
            "reply": result["content"],
            "routing": {"action": action, "rationale": rationale}
        }

        if result.get("references"):
            response_data["references"] = result["references"]

        console.print(f"\n   ✅ [bold green]Respuesta enviada[/bold green]")
        console.print("="*80 + "\n")

        return jsonify(response_data)

    except Exception as e:
        console.print(f"\n   ❌ Error: {str(e)}")
        console.print("="*80 + "\n")
        return jsonify({"error": "Error interno", "details": str(e)}), 500


@app.route("/info", methods=["GET"])
def info():
    """ℹ️  Información del servidor"""
    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        doc_count = collection_info.points_count
    except:
        doc_count = 0

    return jsonify({
        "status": "ok",
        "config": {
            "router_model": os.getenv("LLM_ROUTER_MODEL_ID"),
            "answer_model": os.getenv("LLM_ANSWER_MODEL_ID"),
            "embeddings_model": embeddings_model,
            "k_documents": K_DOCUMENTS,
        },
        "vector_store": {
            "collection": COLLECTION_NAME,
            "documents_count": doc_count,
            "status": "ready" if doc_count > 0 else "empty"
        }
    })


#══════════════════════════════════════════════════════════════════════════════
# 🚀 INICIO DEL SERVIDOR
#══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    console.print("[bold green]✅ Servidor configurado[/bold green]")
    console.print("\n[bold cyan]📡 Endpoints:[/bold cyan]")
    console.print("   🏠 GET  /       - Interfaz web")
    console.print("   💬 POST /chat   - Endpoint del chat")
    console.print("   ℹ️  GET  /info   - Información del servidor")
    console.print("\n[bold yellow]🌐 http://localhost:5500[/bold yellow]")
    console.print("[dim]Presiona Ctrl+C para detener[/dim]\n")

    app.run(debug=True, port=5500, host='0.0.0.0')
