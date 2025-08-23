import os

from flask import Flask, request, jsonify
from rich.console import Console
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langgraph.graph import START, MessagesState, StateGraph

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../web', static_url_path='')
console = Console()

# Inicializar el modelo de chat
chat_model = init_chat_model(
    model=os.getenv("GITHUB_MODEL_ID"),
    model_provider="openai",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url=os.getenv("GITHUB_MODELS_URL"),
)


def call_model(state: MessagesState, config: RunnableConfig) -> dict:
    # Recomendado: exigir un thread_id/session_id para persistencia
    if "configurable" not in config or "thread_id" not in config["configurable"]:
        raise ValueError("Falta 'configurable.thread_id' en el config")
    # El state ya contiene mensajes acumulados por el checkpointer
    ai: AIMessage = chat_model.invoke(state["messages"])
    # Devolvemos la nueva lista de mensajes (append del AIMessage)
    return {"messages": state["messages"] + [ai]}


# Grafo de estado de la conversación (persistiremos mensajes en SQLite)
builder = StateGraph(state_schema=MessagesState)
builder.add_node("model", call_model)
builder.add_edge(START, "model")

# Inicializamos el checkpointer SQLite correctamente (manteniendo el contexto abierto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, "checkpoints.sqlite")

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
checkpointer = SqliteSaver(conn)

graph = builder.compile(checkpointer=checkpointer)

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
    Body JSON:
    {
      "thread_id": "usuario_123",      # requerido para persistir
      "message": "Hola, ¿qué tal?"
    }
    Devuelve la respuesta completa (no streaming).
    """
    data = request.get_json(force=True)
    thread_id = data.get("thread_id")
    user_text = data.get("message", "")

    if not thread_id or not user_text:
        return jsonify({"error": "thread_id y message son requeridos"}), 400

    config = {"configurable": {"thread_id": thread_id}}
    # Construye el input del grafo: añadimos el mensaje humano de este turno
    input_state = {"messages": [HumanMessage(content=user_text)]}

    # Ejecuta y obtiene el último estado con la respuesta del modelo
    # .invoke devuelve el valor final (con el estado actualizado y ya persistido)
    result = graph.invoke(input_state, config=config)
    # La última posición de messages es la respuesta del modelo en este turno
    last_msg = result["messages"][-1]
    return jsonify({
        "thread_id": thread_id,
        "reply": last_msg.content
    })


if __name__ == '__main__':
    app.run(debug=True, port=5500)
