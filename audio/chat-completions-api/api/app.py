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

# Configurar CORS para permitir solicitudes desde diferentes orígenes
CORS(app, origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500"
])

# Ruta para generar audio a partir de un mensaje de texto
@app.route('/generate-audio', methods=['POST'])
def generate_audio():
    try:
        data = request.get_json()

        console.print(data)

        user_message = data.get('message')
        voice_selection = data.get('voice')

        console.print(f"[bold blue]📝 Mensaje recibido[/bold blue]: {user_message}")
        console.print(f"[bold blue]🎤 Voz seleccionada[/bold blue]: {voice_selection}")

        # Mapeo simplificado para las voces
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

        prompt = "Puedes generar un rap con el mensaje siguiente: "
        user_message = prompt + user_message

        voice = voices.get(voice_selection.lower())

        console.print(
            f"[bold green]🎙️ Generando audio con voz[/bold green]: {voice}")
        console.print(f"[bold blue]📝 Mensaje[/bold blue]: {user_message}...")

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

        console.print(
            f"[bold green]✅ Audio generado exitosamente[/bold green]")

        return send_file(tmpfile_path, mimetype="audio/wav")

    except Exception as e:
        console.print(
            f"[bold red]❌ Error generando audio[/bold red]: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Ruta para la página de inicio


@app.route('/')
def index():
    return app.send_static_file('index.html')

# Ruta para servir archivos estáticos adicionales (JS, CSS, etc.)


@app.route('/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

# Ruta de salud para verificar que la API funciona


@app.route('/health')
def health():
    return jsonify({"status": "🎵 Radio AI Station API funcionando correctamente! 📻"})


if __name__ == "__main__":
    console.print("[bold cyan]🚀 Iniciando Radio AI Station API...[/bold cyan]")
    console.print(
        "[bold yellow]📻 Servidor corriendo en: http://localhost:5001[/bold yellow]")
    app.run(host="0.0.0.0", port=5001, debug=True)
