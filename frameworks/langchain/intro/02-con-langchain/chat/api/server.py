import os

from flask import Flask, request, jsonify
from rich.console import Console
from langchain.chat_models import init_chat_model


from langchain_community.chat_message_histories import SQLChatMessageHistory

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
    """
    Endpoint para invocar el modelo de chat. Este además recupera de base de datos el histórico por si el usuario ha tenido conversaciones previas.
    """
    data = request.get_json(force=True)
    thread_id = data.get("thread_id")
    user_text = data.get("message", "")

    if not thread_id or not user_text:
        return jsonify({"error": "thread_id y message son requeridos"}), 400


    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)
    DB_FILE = os.path.join(DATA_DIR, "message_history.sqlite")

    # Recuperar el historial de mensajes
    message_history = SQLChatMessageHistory(
        session_id=thread_id, connection_string=f'sqlite:///{DB_FILE}'
    )

    console.log(f"Historial previo: {message_history.messages}")

    # Construye el input del grafo: añadimos el mensaje humano de este turno
    message_history.add_user_message(user_text)

    # Ejecuta y obtiene el último estado con la respuesta del modelo    
    ai_response = chat_model.invoke(message_history.messages)

    message_history.add_ai_message(ai_response.content)   
   
    return jsonify({
        "thread_id": thread_id,
        "reply": ai_response.content
    })


if __name__ == '__main__':
    app.run(debug=True, port=5500)
