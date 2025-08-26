import os

from flask import Flask, request, jsonify

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory

from dotenv import load_dotenv

# Cargamos las variables de entorno
load_dotenv()

# Creamos la aplicación para Flask
app = Flask(__name__, static_folder='../web', static_url_path='')

# Instanciamos un objeto de la consola de rich
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

# ==========================================
# 🔧 INICIALIZACIÓN DEL MODELO
# Aquí instanciamos el modelo de chat usando variables de entorno para:
#   - ID del modelo (GITHUB_MODEL_ID)
#   - Token (GITHUB_TOKEN)
#   - URL base (GITHUB_MODELS_URL)
# Esto permite intercambiar proveedores sin tocar el código.
# ==========================================
console.print(Panel.fit(
    "🚀 [bold cyan]Inicializando modelo de chat...[/bold cyan]", border_style="cyan"))
chat_model = init_chat_model(
    model=os.getenv("GITHUB_MODEL_ID"),
    # LangChain internamente hace la llamada compatible
    model_provider=os.getenv("GITHUB_MODEL_PROVIDER"),
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url=os.getenv("GITHUB_MODELS_URL"),
)
console.print("✅ Modelo listo", style="green")

# 🧠 Mensaje de sistema: define personalidad y límites del asistente.
SYSTEM_PROMPT = (
    "Eres un asistente amistoso. Contesta de forma breve y clara. Si te preguntan por el nombre del usuario y aún no lo has visto, dilo honestamente."
)

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
    """💬 Gestiona una interacción de chat con memoria persistente.

    Flujo didáctico:
      1. 📥 Recibimos JSON con session_id + message.
      2. 🗄️ Abrimos (o creamos) una base SQLite para el historial.
      3. 🧱 Construimos un Prompt dinámico (system + history + input actual).
      4. 🔁 LangChain rellena automáticamente el placeholder 'history'.
      5. 🤖 El modelo genera la respuesta.
      6. 📝 El historial se actualiza sin que tengamos que hacerlo manualmente.
      7. 🚀 Devolvemos JSON con la respuesta.
    """
    data = request.get_json(force=True)
    session_id = data.get("session_id")
    user_text = data.get("message", "")

    if not session_id or not user_text:
        console.print("❌ Falta session_id o message", style="bold red")
        return jsonify({"error": "session_id y message son requeridos"}), 400

    console.print(Panel.fit(
        f"🗃️ Usando base de datos: [bold]{DB_FILE}[/bold]", border_style="magenta"))

    # 1️⃣ Recuperar historial existente (o se crea vacío). No añadimos manualmente aún el mensaje del usuario.
    message_history = SQLChatMessageHistory(
        session_id=session_id, connection=f"sqlite:///{DB_FILE}"
    )

    # Tabla resumida del historial actual
    if message_history.messages:
        table = Table(title="Historial previo",
                      show_lines=True, header_style="bold blue")
        table.add_column("Idx", style="dim")
        table.add_column("Rol")
        table.add_column("Contenido", overflow="fold")
        for idx, m in enumerate(message_history.messages, start=1):
            table.add_row(str(idx), m.type, (m.content or "").strip())
        console.print(table)
    else:
        console.print(
            "🆕 No había mensajes previos para esta sesión", style="yellow")

    # =============================
    #  Cómo era ANTES (gestión manual)
    # -----------------------------------------------------
    # 1. message_history.add_user_message(user_text)
    # 2. ai_response = chat_model.invoke(message_history.messages)
    # 3. message_history.add_ai_message(ai_response.content)
    # =============================

    # =============================
    # 🚀 Enfoque ACTUAL: RunnableWithMessageHistory
    # -----------------------------------------------------
    # Ventajas:
    #  - Menos código repetitivo.
    #  - Menos riesgo de desalinear prompt e historial.
    #  - Escalable a streaming / batches cambiando solo el método.
    # =============================

    console.print("🧱 Construyendo prompt dinámico...", style="cyan")
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),                 # Contexto y reglas fijas
        # Se sustituye automáticamente
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")                      # Mensaje actual del usuario
    ])

    console.print("🔗 Encadenando prompt -> modelo", style="cyan")
    base_runnable = prompt | chat_model

    # Factoría para cargar/crear historial bajo demanda (LangChain la invoca)
    def get_history(session_id: str):
        return SQLChatMessageHistory(
            session_id=session_id,
            connection=f"sqlite:///{DB_FILE}"
        )

    console.print("🧬 Envolviendo con RunnableWithMessageHistory", style="cyan")
    runnable_with_history = RunnableWithMessageHistory(
        base_runnable,  # Runnable base que incluye el prompt y el modelo
        get_history,  # Factoría para cargar/crear historial bajo demanda
        input_messages_key="input",      # clave del input actual
        history_messages_key="history",  # nombre usado en el prompt
    )

    console.print(Panel.fit("🤖 Generando respuesta...", border_style="green"))
    result = runnable_with_history.invoke(
        {"input": user_text},
        config={"configurable": {"session_id": session_id}}
    )

    reply_text = result.content  # ChatMessage -> str
    console.print(Panel.fit(
        f"✅ Respuesta lista:\n[white]{reply_text}[/white]", border_style="green"))

    return jsonify({"session_id": session_id, "reply": reply_text})


if __name__ == '__main__':
    app.run(debug=True, port=5500)
