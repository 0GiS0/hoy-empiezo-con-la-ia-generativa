import os

from flask import Flask, request, jsonify
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_core.output_parsers import JsonOutputParser

from langchain_core.prompts import ChatPromptTemplate

from rich.console import Console

from dotenv import load_dotenv

from frameworks.langchain.rag.api.models import RouteDecision

load_dotenv()

app = Flask(__name__, static_folder='../web', static_url_path='')
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


# Creamos un RunnableMap que nos permite ejecutar primeramente el clasificador para saber si tenemos que hacer RAG o no
rag_chain = RunnableMap({
    "context": retrieve
    ""
})


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

embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBEDDINGS_MODEL_ID"),
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)


# https://python.langchain.com/docs/integrations/vectorstores/
client = QdrantClient("http://qdrant:6333")

# Recrear la colección

client.recreate_collection(
    collection_name="youtube_guides",
    vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name="youtube_guides",
    embedding=embeddings,
)


# Recuperar puntos que se aproximen
def retrieve(query):
    retrieved_docs = vector_store.similarity_search(query)
    return retrieved_docs


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

    console.log(f"Historial previo: {message_history.messages}")

    # Añade el mensaje del usuario al historial
    message_history.add_user_message(user_text)

    # Recuperar información relevante
    # retrieved_docs = retrieve(user_text)

    # console.log(f"Documentos recuperados: {retrieved_docs}")

    # ¿Añadir documentos recuperados al historial?

    # Ejecuta y obtiene el último estado con la respuesta del modelo (pendiente de integrar RAG routing)
    placeholder_reply = "(pendiente de implementar respuesta del modelo)"
    message_history.add_ai_message(placeholder_reply)

    return jsonify({
        "session_id": session_id,
        "reply": placeholder_reply
    })


if __name__ == '__main__':
    app.run(debug=True, port=5500)
