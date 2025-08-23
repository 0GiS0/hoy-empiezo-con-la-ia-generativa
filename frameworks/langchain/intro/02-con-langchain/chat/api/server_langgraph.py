import os
import sqlite3
from typing import List, Dict

from flask import Flask, request, jsonify
from rich.console import Console
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, MessagesState, StateGraph
from dotenv import load_dotenv
from openai import OpenAI

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

# =============================
#  Simulación SIN LangChain
# =============================
# Reutilizamos las mismas variables de entorno para crear un cliente raw
RAW_BASE_URL = os.getenv("GITHUB_MODELS_URL")
RAW_API_KEY = os.getenv("GITHUB_TOKEN")
RAW_MODEL_ID = os.getenv("GITHUB_MODEL_ID")

raw_client = OpenAI(base_url=RAW_BASE_URL, api_key=RAW_API_KEY)

SYSTEM_PROMPT = (
    "Eres un asistente amistoso. Contesta de forma breve y clara. Si te preguntan por el nombre del usuario y aún no lo has visto, dilo honestamente."
)

# Memoria en memoria (por thread_id) -> lista de dicts {role, content}
raw_memory: Dict[str, List[Dict[str, str]]] = {}

def build_raw_payload(thread_id: str, user_text: str, use_memory: bool) -> List[Dict[str, str]]:
    """Construye la lista de mensajes para la llamada raw.

    Si use_memory es False: sólo system + mensaje actual (stateless).
    Si True: system + historial previo + mensaje actual.
    """
    if use_memory:
        history = raw_memory.setdefault(thread_id, [])
        # añadimos el mensaje user al final para esta llamada
        payload = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [
            {"role": "user", "content": user_text}
        ]
    else:
        payload = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ]
    return payload

def raw_infer(messages: List[Dict[str, str]]) -> str:
    """Hace la llamada directa al modelo (chat.completions)."""
    resp = raw_client.chat.completions.create(
        model=RAW_MODEL_ID,
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        messages=messages,
    )
    return resp.choices[0].message.content

def update_memory(thread_id: str, user_text: str, answer: str, use_memory: bool) -> None:
    if not use_memory:
        return
    convo = raw_memory.setdefault(thread_id, [])
    convo.append({"role": "user", "content": user_text})
    convo.append({"role": "assistant", "content": answer})


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


# 📦 Endpoint alternativo sin LangChain para comparar
@app.route("/chat_simple", methods=["POST"])
def chat_simple():
    """Endpoint de demostración sin LangChain.

    Body JSON:
    {
       "thread_id": "abc123",          # requerido para modo con memoria
       "message": "Hola",
       "memory": true|false (opcional, default true)
    }
    Si memory=false => stateless (no se conserva historial).
    Si memory=true  => se acumulan mensajes en memoria de proceso.
    """
    data = request.get_json(force=True)
    thread_id = data.get("thread_id")
    user_text = data.get("message", "")
    use_memory = data.get("memory", True)

    if not thread_id or not user_text:
        return jsonify({"error": "thread_id y message son requeridos"}), 400

    messages = build_raw_payload(thread_id, user_text, use_memory)
    try:
        answer = raw_infer(messages)
    except Exception as exc:
        console.print(f"[red]Error raw: {exc}[/red]")
        return jsonify({"error": str(exc)}), 500

    update_memory(thread_id, user_text, answer, use_memory)

    return jsonify({
        "thread_id": thread_id,
        "reply": answer,
        "mode": "memory" if use_memory else "stateless"
    })


if __name__ == '__main__':
    app.run(debug=True, port=5500)
