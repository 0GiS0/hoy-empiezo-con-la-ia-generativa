import os
import ast

from flask import Flask, json, request, jsonify
from rich.console import Console
from openai import OpenAI
from dotenv import load_dotenv
import sqlite3

load_dotenv()

app = Flask(__name__, static_folder='../web', static_url_path='')
console = Console()

# Configurar directorio para la base de datos SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, "message_history.sqlite")

# Conectarse a la base de datos (permitir uso desde distintos threads de Flask)
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
# Recuperar el cursor para poder ejecutar queries en base de datos
cursor = conn.cursor()

# cliente de OpenAI
client = OpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url=os.getenv("GITHUB_MODELS_URL"),
)

SYSTEM_PROMPT = (
    "Eres un asistente amistoso. Contesta de forma breve y clara. Si te preguntan por el nombre del usuario y aún no lo has visto, dilo honestamente."
)

####
# Funciones para la gestión de la conversación
###


def create_table_if_not_exists():

    # Crear tabla llamada message_store si no existe con los campos id (INTEGER) (PK), session_id (TEXT) y message (TEXT)
    console.print(
        "🗄️  [bold cyan]Verificando tabla[/] [white]message_store[/]…")
    cursor.execute("""
                       CREATE TABLE IF NOT EXISTS message_store(id, session_id, message)                            
                   """)
    console.print("✅  [green]Tabla lista[/]")


def get_conversation_history(session_id):

    # Crear tabla si todavía no existe
    console.print(
        f"🔍  [cyan]Buscando historial[/] para sesión [magenta]{session_id}[/]")
    create_table_if_not_exists()

    # Recuperar los mensajes para la sesión actual
    messages_by_session_id = cursor.execute(f"""
        SELECT message FROM message_store WHERE session_id = '{session_id}'
    """).fetchall()

    # Si no se encuentra historia previo añadir system message como parte de esta nueva sesión y devolver
    if not messages_by_session_id:
        console.print(
            "ℹ️  [yellow]No había historial previo, insertando system prompt[/]")
        add_system_message(session_id)

    # Recuperar de nuevo (ya incluye el último mensaje del sistema).
    messages_by_session_id = cursor.execute(f"""
        SELECT message FROM message_store WHERE session_id = '{session_id}'
    """).fetchall()
    console.print(
        f"📥  [blue]Historial recuperado[/]: [cyan]{len(messages_by_session_id)}[/] mensajes")

    # Devolver un diccionario con la clave 'messages' y la lista de mensajes parseados.
    return {"messages": [ast.literal_eval(msg[0]) for msg in messages_by_session_id]}


def add_system_message(session_id):

    # Añadir un registro asociado al session_id
    console.print(
        f"🛠️  [bold]Insertando system prompt[/] para sesión [magenta]{session_id}[/]")
    cursor.execute("""
        INSERT INTO message_store (session_id, message) VALUES (?, ?)
    """, (session_id, str({"role": "system", "data": {"content": SYSTEM_PROMPT, "addtl_kwargs": {}, "response_metadata": {}, "type": "human", "name": None, "id": None, "example": False}})))
    conn.commit()
    console.print("✅  [green]System prompt guardado[/]")


def add_user_message(session_id, user_text):

    # Añadir un registro asociado al session_id
    console.print(f"💬  [bold yellow]Usuario[/] -> [white]{user_text}[/]")
    cursor.execute("""
        INSERT INTO message_store (session_id, message) VALUES (?, ?)
    """, (session_id, str({"role": "user", "data": {"content": user_text, "addtl_kwargs": {}, "response_metadata": {}, "type": "human", "name": None, "id": None, "example": False}})))
    conn.commit()
    console.print("📝  [green]Mensaje usuario persistido[/]")


def add_ai_message(session_id, user_text):

    # Añadir un registro asociado al session_id

    console.print(
        f"🤖  [bold green]AI[/] -> {user_text[:120]}{'…' if len(user_text) > 120 else ''}")
    cursor.execute("""
        INSERT INTO message_store (session_id, message) VALUES (?, ?)
    """, (session_id, str({"role": "assistant", "data": {"content": user_text, "addtl_kwargs": {}, "response_metadata": {}, "type": "ai", "name": None, "id": None, "example": False, "tool_calls": [], "invalid_tool_calls": [], "usage_metadata": None}})))
    conn.commit()
    console.print("📦  [green]Respuesta AI persistida[/]")

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
    console.print("🚏  [bold]Petición entrante[/] /chat")
    data = request.get_json(force=True)
    session_id = data.get("session_id")
    user_text = data.get("message", "")

    if not session_id or not user_text:
        console.print("⚠️  [red]Faltan parámetros obligatorios[/]")
        return jsonify({"error": "session_id y message son requeridos"}), 400

    console.print(
        f"🔎  Recuperando historial previo para [magenta]{session_id}[/]")
    # {'messages': [...]} formato interno
    prev_history = get_conversation_history(session_id)
    console.print(
        f"📊  Historial previo: [cyan]{len(prev_history['messages'])}[/] mensajes")

    # Guardar mensaje del usuario
    add_user_message(session_id, user_text)

    # Recuperar de nuevo (ya incluye el último mensaje del usuario).
    full_history = get_conversation_history(session_id)

    console.print(
        f"🧾  Historial tras añadir usuario: [cyan]{len(full_history['messages'])}[/] mensajes")

    # Adaptar al formato esperado por chat.completions (role/content)
    formatted_messages = [
        {
            "role": m.get("role"),
            "content": m.get("data", {}).get("content", "")
        }
        for m in full_history["messages"]
    ]

    console.print(
        f"🛠️  Llamando modelo [bold]{os.getenv('GITHUB_MODEL_ID')}[/] con [cyan]{len(formatted_messages)}[/] mensajes")
    response = client.chat.completions.create(
        model=os.getenv("GITHUB_MODEL_ID"),
        messages=formatted_messages,
        temperature=0.7
    )
    console.print("✅  [green]Respuesta recibida del modelo[/]")

    # Extraer contenido de la respuesta (SDK chat.completions)
    ai_content = response.choices[0].message.content if response.choices else ""

    # Persistir respuesta
    add_ai_message(session_id, ai_content)

    return jsonify({"session_id": session_id, "reply": ai_content})


if __name__ == '__main__':
    app.run(debug=True, port=5500)
