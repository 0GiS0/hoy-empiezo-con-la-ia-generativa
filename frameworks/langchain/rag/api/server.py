import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_core.output_parsers import JsonOutputParser

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap

from rich.console import Console

from dotenv import load_dotenv

from models import RouteDecision

load_dotenv()

app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app)  # Habilitar CORS para todas las rutas
console = Console()

# Modelo para clasificar la pregunta
llm_router = init_chat_model(
    model=os.getenv("LLM_ROUTER_MODEL_ID"),
    model_provider=os.getenv("MODEL_PROVIDER", "openai"),
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("ENDPOINT_URL"),
)

# Modelo para responder
llm_answer = init_chat_model(
    model=os.getenv("LLM_ANSWER_MODEL_ID"),
    model_provider=os.getenv("MODEL_PROVIDER", "openai"),
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("ENDPOINT_URL"),
)

router_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un clasificador. Decide si la pregunta NECESITA búsqueda externa (retrieve) o se puede responder con conocimiento general (direct). "
     "Responde SOLO en JSON con las claves: action, rationale. "
     "Reglas: "
     "- retrieve: preguntas factuales sobre documentos/empresa, manuales, políticas, referencias, cifras, fechas después del conocimiento del modelo, códigos específicos del dominio, ‘dónde está en el doc’, ‘según el PDF’, etc. "
     "- direct: saludos, chit-chat, traducciones, reescrituras, programación genérica que no depende de tu corpus, instrucciones de uso generales."
     ),
    ("user",
     "Pregunta: {question}\n"
     "Contexto breve (opcional): {chat_hint}\n"
     "Devuélveme JSON.")
])

router = router_prompt | llm_router | JsonOutputParser(
    pydantic_object=RouteDecision)


direct_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Responde con precisión usando solo tu conocimiento general. "
     "Si crees que faltan datos del usuario o de documentos, sugiere consultarlos, pero no inventes."),
    ("user", "{question}")
])

direct_chain = direct_prompt | llm_answer


# Prompt para RAG
rag_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Eres un asistente experto. Responde la pregunta del usuario basándote en el contexto proporcionado. "
     "Si el contexto no contiene información relevante, indica que no tienes esa información en los documentos disponibles. "
     "Contexto:\n{context}"),
    ("user", "{question}")
])

rag_chain = rag_prompt | llm_answer


###################################################
# Lógica para el histórico de la conversación #####
###################################################

# Crear la base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, "message_history.sqlite")


###########################################################
# Lógica para recuperar información basada en la consulta #
###########################################################

# Para API_KEY, si no está configurado o es placeholder, usar valor dummy (para Ollama/Model Runner)
api_key = os.getenv("API_KEY")
if not api_key or api_key == "__PON_AQUI_TU_API_KEY__":
    console.print(":information: [yellow]API_KEY no configurado, usando valor dummy (útil para Ollama/Model Runner)[/yellow]")
    api_key = "dummy-key"

embeddings_model = os.getenv("EMBEDDINGS_MODEL_ID", "ai/embeddinggemma")
console.print(f":gear: [cyan]Usando modelo de embeddings:[/cyan] [bold]{embeddings_model}[/bold]")

embeddings = OpenAIEmbeddings(
    model=embeddings_model,
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=api_key
)

# Determinar el tamaño del vector según el modelo
if "embeddinggemma" in embeddings_model:
    vector_size = 768
elif "text-embedding-3-large" in embeddings_model:
    vector_size = 3072
elif "text-embedding-3-small" in embeddings_model:
    vector_size = 1536
else:
    console.print(f":warning: [yellow]Modelo desconocido, usando 768 dimensiones por defecto[/yellow]")
    vector_size = 768

console.print(f":bar_chart: [cyan]Tamaño del vector:[/cyan] [bold]{vector_size}[/bold] dimensiones")

# https://python.langchain.com/docs/integrations/vectorstores/
client = QdrantClient("http://qdrant:6333")

collection_name = "youtube_guides"

# Verificar si la colección existe, si no existe se debe crear primero ejecutando document-loaders.py
if not client.collection_exists(collection_name):
    console.print(f":warning: [red]La colección '[bold]{collection_name}[/bold]' no existe. Ejecuta document-loaders.py primero.[/red]")
    console.print(":information: [yellow]Creando colección vacía temporalmente...[/yellow]")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
else:
    console.print(f":white_check_mark: [green]Colección '[bold]{collection_name}[/bold]' encontrada.[/green]")

    console.print(f":white_check_mark: [green]Colección '[bold]{collection_name}[/bold]' encontrada.[/green]")

vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)


# Recuperar puntos que se aproximen
def retrieve(query):
    """Recupera documentos relevantes del vector store"""
    retrieved_docs = vector_store.similarity_search(query, k=3)
    console.print(f":mag: [cyan]Documentos recuperados:[/cyan] {len(retrieved_docs)}")
    
    # Mostrar detalles de cada documento recuperado
    for i, doc in enumerate(retrieved_docs, 1):
        console.print(f"\n[bold yellow]📄 Documento {i}:[/bold yellow]")
        console.print(f"[dim]Metadata:[/dim] {doc.metadata}")
        content_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
        console.print(f"[dim]Contenido (preview):[/dim] {content_preview}")
    
    return retrieved_docs


def format_docs(docs):
    """Formatea los documentos recuperados como texto"""
    formatted = "\n\n".join([f"--- Documento {i} ---\n{doc.page_content}" for i, doc in enumerate(docs, 1)])
    console.print(f"\n[bold green]📝 Contexto formateado para el modelo:[/bold green]")
    console.print(f"[dim]Longitud total: {len(formatted)} caracteres[/dim]")
    return formatted


# Creamos un RunnableMap que nos permite ejecutar primeramente el clasificador para saber si tenemos que hacer RAG o no
# (Por ahora comentado hasta implementar la lógica completa)
# rag_chain = RunnableMap({
#     "context": retrieve
# })


#######################
######  Endpoints #####
#######################


# 📦 Página principal que sirve el HTML
@app.route('/')
def index():
    return app.send_static_file('index.html')


# 📦 Endpoint para archivos estáticos (JS, CSS, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    """Sirve archivos estáticos adicionales."""
    return app.send_static_file(filename)


# 📦 Endpoint para el chat
@app.route("/chat", methods=["POST"])
def chat_invoke():
    """
    Endpoint para invocar el modelo de chat. Este además recupera de base de datos el histórico por si el usuario ha tenido conversaciones previas.
    """
    data = request.get_json(force=True)
    session_id = data.get("session_id")
    user_text = data.get("message", "")

    if not session_id or not user_text:
        return jsonify({"error": "session_id y message son requeridos"}), 400

    # Recuperar el historial de mensajes
    message_history = SQLChatMessageHistory(
        session_id=session_id, connection_string=f'sqlite:///{DB_FILE}'
    )

    console.print(f":book: [cyan]Historial previo:[/cyan] {len(message_history.messages)} mensajes")

    # Añade el mensaje del usuario al historial
    message_history.add_user_message(user_text)

    # Construir hint de contexto del historial reciente (últimos 3 mensajes)
    recent_history = message_history.messages[-6:] if len(message_history.messages) > 0 else []
    chat_hint = " | ".join([f"{msg.type}: {msg.content[:50]}" for msg in recent_history])

    # 1️⃣ Clasificar la pregunta (¿necesita RAG o respuesta directa?)
    console.print(f":thinking_face: [yellow]Clasificando pregunta...[/yellow]")
    routing_decision = router.invoke({
        "question": user_text,
        "chat_hint": chat_hint
    })
    
    action = routing_decision.get("action", "direct")
    rationale = routing_decision.get("rationale", "Sin explicación")
    
    console.print(f":robot: [magenta]Decisión:[/magenta] [bold]{action}[/bold]")
    console.print(f":bulb: [dim]Razón: {rationale}[/dim]")

    # 2️⃣ Ejecutar la cadena correspondiente
    if action == "retrieve":
        # Ruta RAG: recuperar documentos y generar respuesta con contexto
        console.print(f":mag: [cyan]Recuperando documentos relevantes...[/cyan]")
        retrieved_docs = retrieve(user_text)
        context = format_docs(retrieved_docs)
        
        console.print(f":robot: [green]Generando respuesta con RAG...[/green]")
        response = rag_chain.invoke({
            "question": user_text,
            "context": context
        })
        reply = response.content
    else:
        # Ruta directa: responder con conocimiento general
        console.print(f":zap: [green]Generando respuesta directa...[/green]")
        response = direct_chain.invoke({
            "question": user_text
        })
        reply = response.content

    # Añadir la respuesta del modelo al historial
    message_history.add_ai_message(reply)

    return jsonify({
        "session_id": session_id,
        "reply": reply,
        "routing": {
            "action": action,
            "rationale": rationale
        }
    })


if __name__ == '__main__':
    app.run(debug=True, port=5500)
