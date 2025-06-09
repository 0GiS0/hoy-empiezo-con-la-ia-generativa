import base64
from openai import OpenAI
from rich.console import Console
from dotenv import load_dotenv
import os
import tempfile
from flask import Flask, request, send_file, jsonify, render_template_string
from flask_cors import CORS

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configurar la consola de Rich para mostrar mensajes
console = Console()

# Configurar el cliente de OpenAI con las variables de entorno
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

# Crear la aplicación Flask con static_folder apuntando a web
app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app)  # Permitir CORS para todas las rutas


# Ruta para generar audio a partir de un mensaje de texto
@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    data = request.get_json()
    user_message = data.get(
        'message', 'Hola amigos, bienvenidos a un nuevo video! Hoy vamos a hablar de...')
    voice_selection = data.get('voice', 'Echo (profesional)')

    voices = {
        "Alloy (neutral)": "alloy",
        "Echo (profesional)": "echo",
        "Fable (juvenil)": "fable",
        "Onyx (potente)": "onyx",
        "Nova (suave)": "nova",
        "Shimmer (optimista)": "shimmer"
    }

    voice = voices.get(voice_selection, "echo")

    console.print(f"[bold green]Generando audio con voz[/bold green]: {voice}")

    response = client.chat.completions.create(
        model="gpt-4o-audio-preview",
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "wav"},
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    wav_bytes = base64.b64decode(response.choices[0].message.audio.data)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        tmpfile.write(wav_bytes)
        tmpfile_path = tmpfile.name

    return send_file(tmpfile_path, mimetype="audio/wav", as_attachment=True)

# Ruta para la página de inicio
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Ruta para servir archivos estáticos adicionales (JS, CSS, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
