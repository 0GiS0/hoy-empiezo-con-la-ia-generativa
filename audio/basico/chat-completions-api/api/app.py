
"""
📻 Radio AI Station API

Esta API permite generar audio a partir de texto usando voces de OpenAI, ideal para crear mensajes hablados, raps, podcasts, etc.

Endpoints principales:
  - POST /generate-audio: Genera un archivo de audio (.wav) a partir de un texto y una voz seleccionada.
  - GET /: Página de inicio (sirve index.html).
  - GET /<filename>: Archivos estáticos (JS, CSS, etc.).
  - GET /health: Verifica que la API está funcionando.

Los nombres de funciones y variables están en inglés, pero los comentarios y mensajes te guían en español y con emojis.
"""

import base64
from openai import OpenAI
from rich.console import Console
from dotenv import load_dotenv
import os
import tempfile
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS


# 🛠️ Configuración global
load_dotenv()
console = Console()
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)
app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app, origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500"
])


# 🎤 Endpoint para generar audio a partir de texto
@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    """
    Recibe un mensaje y una voz, genera un audio usando OpenAI y lo devuelve como archivo WAV.
    """
    try:
        data = request.get_json()
        console.print(f"[blue]📩 Datos recibidos:[/blue] {data}")

        user_message = data.get('message')
        voice_selection = data.get('voice')

        console.print(f"[bold blue]📝 Mensaje recibido:[/bold blue] {user_message}")
        console.print(f"[bold blue]🎤 Voz seleccionada:[/bold blue] {voice_selection}")

        # 🎵 Mapeo de voces disponibles
        voices = {
            "alloy": "alloy",
            "ash": "ash",
            "ballad": "ballad",
            "coral": "coral",
            "echo": "echo",
            "fable": "fable",
            "onyx": "onyx",
            "nova": "nova",
            "shimmer": "shimmer",
            "sage": "sage"
        }

        prompt = (
            "Genera únicamente un rap creativo usando el siguiente mensaje, "
            "añade beatbox. No incluyas explicaciones ni información adicional, "
            "solo el rap en español:\n"
        )
        user_message = prompt + user_message

        voice = voices.get(voice_selection.lower())

        console.print(f"[bold green]🎙️ Generando audio con voz:[/bold green] {voice}")
        console.print(f"[bold blue]📝 Mensaje:[/bold blue] {user_message}...")

        response = client.chat.completions.create(
            model=os.getenv("MODEL_FOR_AUDIO"),
            modalities=["text", "audio"],
            audio={"voice": voice, "format": "wav"},
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.9,
        )

        wav_bytes = base64.b64decode(response.choices[0].message.audio.data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(wav_bytes)
            tmpfile_path = tmpfile.name

        console.print(f"[bold green]✅ Audio generado exitosamente[/bold green] 🟢")

        return send_file(tmpfile_path, mimetype="audio/wav")

    except Exception as e:
        console.print(f"[bold red]❌ Error generando audio:[/bold red] {str(e)}")
        return jsonify({"error": str(e)}), 500


# 🏠 Endpoint para la página de inicio
@app.route('/')
def index():
    """Sirve el archivo index.html de la carpeta web."""
    return app.send_static_file('index.html')

# 📦 Endpoint para archivos estáticos (JS, CSS, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    """Sirve archivos estáticos adicionales."""
    return app.send_static_file(filename)

# ❤️ Endpoint de salud para verificar que la API funciona
@app.route('/health')
def health():
    """Devuelve el estado de la API."""
    return jsonify({"status": "🎵 Radio AI Station API funcionando correctamente! 📻"})



if __name__ == "__main__":
    console.print("[bold cyan]🚀 Iniciando Radio AI Station API...[/bold cyan]")
    console.print("[bold yellow]📻 Servidor corriendo en: http://localhost:5001[/bold yellow]")
    app.run(host="0.0.0.0", port=5001, debug=True)
