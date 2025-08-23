from os
from dotenv import load_dotenv

from flask import Flask, request
from rich.console import Console
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

app = Flask(__name__, static_folder='../web', static_url_path='')
console = Console()

# Inicializar el modelo de chat
chat_model = init_chat_model(
    model=os.getenv("GITHUB_MODEL_ID"),
    model_provider="openai",
    api_key=os.getenv("GITHUB_TOKEN"),
    base_url=os.getenv("GITHUB_MODELS_URL"),
)


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
@app.route('/chat', methods=['POST'])
def chat():
    """Maneja las solicitudes de chat."""
    data = request.json
    messages = data.get('messages', [])
    source = data.get('source', '')

    console.print(messages)

    return {'response': '¡Hola! Soy tu asistente 🤖. ¿En qué te ayudo hoy?'}


if __name__ == '__main__':
    app.run(debug=True, port=5500)
