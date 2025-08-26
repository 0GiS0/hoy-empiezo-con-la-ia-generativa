import os
import ast

from flask import Flask, request, jsonify
from rich.console import Console
from rich.panel import Panel
from openai import OpenAI
from dotenv import load_dotenv
import sqlite3

load_dotenv()

app = Flask(__name__, static_folder='../web', static_url_path='')
console = Console()

# ==============================================
# 🗄️  CONFIGURACIÓN DE ALMACENAMIENTO LOCAL (SQLite)
# ----------------------------------------------
# Guardamos el historial de cada conversación en
# una tabla muy simple para poder reconstruir
# el contexto en cada petición. De esta manera,
# mostramos cómo sería hacerlo "a mano" sin LangChain.
# ==============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ruta absoluta del directorio actual
DATA_DIR = os.path.join(BASE_DIR, "data")             # Carpeta donde dejaremos la base
os.makedirs(DATA_DIR, exist_ok=True)                   # Crear si no existe
DB_FILE = os.path.join(DATA_DIR, "message_history.sqlite")  # Archivo SQLite

# 🔌 Conectamos a SQLite (check_same_thread=False permite reutilizar conexión en Flask)
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()  # Cursor para ejecutar sentencias SQL

# ============================================================================
# 🤖 CLIENTE DEL MODELO (OpenAI compatible GitHub Models)
# ---------------------------------------------------------------------------
# Usamos variables de entorno para no hardcodear credenciales ni endpoints.
# Así podemos cambiar de proveedor sin tocar el código de negocio.
# ==============================================
console.print(Panel.fit("🚀 Inicializando cliente del modelo", border_style="cyan"))
client = OpenAI(
    api_key=os.getenv("GITHUB_TOKEN"),           # Token (personal access token) con el permiso Models
    base_url=os.getenv("GITHUB_MODELS_URL"),     # URL base de la API (GitHub Models)
)
console.print("✅ Cliente listo", style="green")

# 🧠 Prompt de sistema: primer mensaje que marca tono y reglas globales.
SYSTEM_PROMPT = (
    "Eres un asistente amistoso. Contesta de forma breve y clara. Si te preguntan por el nombre del usuario y aún no lo has visto, dilo honestamente."
)

####
# Funciones para la gestión de la conversación
###


def create_table_if_not_exists():
    """🧱 Garantiza que exista la tabla donde guardamos cada mensaje serializado.

    NOTA: Para simplificar, no definimos tipos estrictos ni AUTO INCREMENT.
    Guardamos 'message' como texto (string de un dict) y luego lo parseamos.
    """
    console.print("🗄️  [bold cyan]Verificando tabla[/] [white]message_store[/]…")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS message_store(id, session_id, message)
        """
    )
    console.print("✅  [green]Tabla lista[/]")


def get_conversation_history(session_id):
    """🕰️ Recupera (y si hace falta inicializa) el historial de una sesión.

    Pasos:
      1. Asegura existencia de la tabla.
      2. Busca todos los registros previos para la sesión.
      3. Si está vacío, inserta el system prompt.
      4. Vuelve a leer (ya con system prompt).
      5. Devuelve los mensajes parseados (cada fila es un dict serializado como string).
    """
    console.print(f"🔍  [cyan]Buscando historial[/] para sesión [magenta]{session_id}[/]")
    create_table_if_not_exists()

    messages_by_session_id = cursor.execute(
        f"""
        SELECT message FROM message_store WHERE session_id = '{session_id}'
        """
    ).fetchall()

    if not messages_by_session_id:
        console.print("ℹ️  [yellow]No había historial previo, insertando system prompt[/]")
        add_system_message(session_id)

    messages_by_session_id = cursor.execute(
        f"""
        SELECT message FROM message_store WHERE session_id = '{session_id}'
        """
    ).fetchall()
    console.print(
        f"📥  [blue]Historial recuperado[/]: [cyan]{len(messages_by_session_id)}[/] mensajes"
    )

    # Convertimos cada string que representa un dict en un objeto Python con ast.literal_eval (seguro para literales).
    return {"messages": [ast.literal_eval(msg[0]) for msg in messages_by_session_id]}


def add_system_message(session_id):
    """➕ Inserta el mensaje de sistema inicial para una nueva sesión.

    Guardamos una estructura similar a la que genera LangChain/Internal (role + data.content)
    para que el formato sea consistente y fácil de adaptar si migramos.
    """
    console.print(f"🛠️  [bold]Insertando system prompt[/] para sesión [magenta]{session_id}[/]")
    cursor.execute(
        """
        INSERT INTO message_store (session_id, message) VALUES (?, ?)
        """,
        (
            session_id,
            str(
                {
                    "role": "system",
                    "data": {
                        "content": SYSTEM_PROMPT,
                        "addtl_kwargs": {},
                        "response_metadata": {},
                        "type": "human",  # Conservamos campos para homogeneidad
                        "name": None,
                        "id": None,
                        "example": False,
                    },
                }
            ),
        ),
    )
    conn.commit()
    console.print("✅  [green]System prompt guardado[/]")


def add_user_message(session_id, user_text):
    """🗣️ Guarda el mensaje del usuario en el historial persistente."""
    console.print(f"💬  [bold yellow]Usuario[/] -> [white]{user_text}[/]")
    cursor.execute(
        """
        INSERT INTO message_store (session_id, message) VALUES (?, ?)
        """,
        (
            session_id,
            str(
                {
                    "role": "user",
                    "data": {
                        "content": user_text,
                        "addtl_kwargs": {},
                        "response_metadata": {},
                        "type": "human",
                        "name": None,
                        "id": None,
                        "example": False,
                    },
                }
            ),
        ),
    )
    conn.commit()
    console.print("📝  [green]Mensaje usuario persistido[/]")


def add_ai_message(session_id, user_text):
    """🤖 Persiste la respuesta generada por el modelo.

    Truncamos en log para no saturar la terminal, pero guardamos todo en DB.
    """
    console.print(
        f"🤖  [bold green]AI[/] -> {user_text[:120]}{'…' if len(user_text) > 120 else ''}"
    )
    cursor.execute(
        """
        INSERT INTO message_store (session_id, message) VALUES (?, ?)
        """,
        (
            session_id,
            str(
                {
                    "role": "assistant",
                    "data": {
                        "content": user_text,
                        "addtl_kwargs": {},
                        "response_metadata": {},
                        "type": "ai",
                        "name": None,
                        "id": None,
                        "example": False,
                        "tool_calls": [],
                        "invalid_tool_calls": [],
                        "usage_metadata": None,
                    },
                }
            ),
        ),
    )
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
