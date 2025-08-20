import os
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import logging
from dotenv import load_dotenv
from rich.console import Console
import base64
import io
from pydub import AudioSegment


console = Console()

# 🔐 Cargar variables de entorno (por ejemplo, OPENAI_API_KEY y MODEL_FOR_AUDIO)
load_dotenv()

app = Flask(__name__, static_folder='../web', static_url_path='')
# 🌐 Habilitar CORS para aceptar peticiones del front (simplificado a todos los orígenes)
CORS(app, resources={r"*": {"origins": "*"}})

# 📝 Configurar logging para trazas en consola
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🤖 Inicializar cliente de OpenAI con la API key del entorno
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# 🧠 Historial de conversación (en memoria para la demo)
conversation_history = [
    {"role": "system", "content": "Eres un asistente útil y amigable. Responde de manera concisa y conversacional."}
]

@app.route('/conversation', methods=['POST'])
def conversation():
    """
    🎯 Endpoint principal para conversaciones por voz.
    Flujo (audio directo a Chat Completions):
      1) Recibe un archivo de audio (multipart/form-data, campo 'audio').
      2) Codifica el audio en base64 y lo envía como `input_audio` en el mensaje del usuario.
      3) Genera respuesta con Chat (texto+audio) usando el modelo configurado.
      4) Devuelve un WAV con la respuesta hablada.
    """
    try:
        console.print("\n[bold blue]" + "="*50 + "[/bold blue]")
        console.print("[bold yellow]🎤 NUEVA CONVERSACIÓN INICIADA[/bold yellow]")
        console.print("[bold blue]" + "="*50 + "[/bold blue]")

        # ✅ Validar que se recibió un archivo de audio
        if 'audio' not in request.files:
            console.print("[bold red]❌ No se encontró archivo de audio en la request[/bold red]")
            return jsonify({"error": "No se encontró archivo de audio"}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            console.print("[bold red]❌ Archivo de audio vacío[/bold red]")
            return jsonify({"error": "No se seleccionó archivo"}), 400

        console.print(f"[bold blue]🎵 Procesando archivo de audio:[/bold blue] [cyan]{audio_file.filename}[/cyan]")

        # 1️⃣ Leer y codificar el audio en base64 para enviarlo como input_audio
        raw_bytes = audio_file.read()
        if not raw_bytes:
            console.print("[bold red]❌ Audio vacío[/bold red]")
            return jsonify({"error": "Audio vacío"}), 400

    # Detectar formato real por cabecera (más fiable que mimetype/nombre)
        def sniff_audio_format(b: bytes) -> str:
            try:
                if len(b) >= 12 and b.startswith(b'RIFF') and b[8:12] == b'WAVE':
                    return 'wav'
                if len(b) >= 4 and b.startswith(b'\x1A\x45\xDF\xA3'):
                    return 'webm'  # EBML (Matroska/WebM)
                if len(b) >= 3 and b[0:3] == b'ID3':
                    return 'mp3'
                if len(b) >= 2 and b[0] == 0xFF and (b[1] & 0xE0) == 0xE0:
                    return 'mp3'  # MP3 frame sync
                if len(b) >= 12 and b[4:8] == b'ftyp':
                    # MP4 family (m4a/mp4); asumimos m4a para audio
                    return 'm4a'
            except Exception:
                pass
            return 'wav'

        input_format = sniff_audio_format(raw_bytes)
        console.print(f"[bold yellow]📄 Formato detectado:[/bold yellow] [cyan]{input_format}[/cyan]")

        # Chat Completions soporta actualmente 'wav' y 'mp3' para input_audio.
        # Si llega 'webm'/'m4a'/otro, lo convertimos a WAV usando pydub/ffmpeg.
        if input_format not in ("wav", "mp3"):
            try:
                console.print("[bold yellow]🔄 Convirtiendo audio a WAV para compatibilidad...[/bold yellow]")
                # Pydub puede leer desde buffer indicando el formato de origen.
                src_buf = io.BytesIO(raw_bytes)
                audio = AudioSegment.from_file(src_buf, format=input_format)
                out_buf = io.BytesIO()
                audio.export(out_buf, format="wav")
                raw_bytes = out_buf.getvalue()
                input_format = "wav"
            except Exception as conv_err:
                console.print(f"[bold red]❌ No se pudo convertir el audio a WAV:[/bold red] [red]{conv_err}[/red]")
                console.print("[bold yellow]💡 Sugerencia:[/bold yellow] instala FFmpeg en el sistema o envía audio en WAV/MP3 desde el cliente.")
                return jsonify({
                    "error": "Formato no compatible y conversión fallida",
                    "detail": str(conv_err),
                    "hint": "Instala ffmpeg o envía WAV/MP3"
                }), 400

        # Codificar (posiblemente reconvertido) a base64 para input_audio
        encoded = base64.b64encode(raw_bytes).decode('utf-8')

        # 2️⃣ Agregar mensaje del usuario con contenido de audio (multimodal)
        conversation_history.append({
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {"data": encoded, "format": input_format}
                }
            ]
        })

        # 3️⃣ Generar respuesta (texto+audio) usando el modelo configurado
        console.print("[bold magenta]🤖 Generando respuesta con Chat (audio directo)...[/bold magenta]")
        response = client.chat.completions.create(
            model=os.getenv("MODEL_FOR_AUDIO"),
            modalities=["text", "audio"],
            audio={"voice": "nova", "format": "wav"},
            messages=conversation_history,
        )

        # 🗣️ Obtener el texto de la respuesta y agregarlo al historial
        assistant_message = response.choices[0].message.content or "Respuesta de audio generada"
        conversation_history.append({"role": "assistant", "content": assistant_message})

        console.print(f"[bold cyan]💬 Respuesta generada:[/bold cyan] [white]'{assistant_message}'[/white]")

        # 🔊 Decodificar el WAV (base64) que devuelve la API
        wav_bytes = base64.b64decode(response.choices[0].message.audio.data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(wav_bytes)
            tmpfile_path = tmpfile.name

        console.print(f"[bold green]✅ Audio generado exitosamente[/bold green] [green]({len(wav_bytes)} bytes)[/green] 🎵")
        # -1 para excluir el mensaje del sistema
        console.print(f"[bold blue]📊 Historial de conversación:[/bold blue] [cyan]{len(conversation_history)-1} mensajes[/cyan]")
        console.print("[bold blue]" + "="*50 + "[/bold blue]\n")

        return send_file(tmpfile_path, mimetype="audio/wav")

    except Exception as e:
        # 🚨 Manejo de errores del flujo completo
        console.print(f"[bold red]❌ Error en conversación:[/bold red] [red]{str(e)}[/red]")
        logger.error(f"Error en conversación: {str(e)}")
        return jsonify({"error": f"Error procesando conversación: {str(e)}"}), 500


# 🏠 Endpoint para la página de inicio (sirve la UI)
@app.route('/')
def index():
    """Sirve el archivo index.html de la carpeta web."""
    return app.send_static_file('index.html')

# 📦 Endpoint para archivos estáticos (JS, CSS, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    """Sirve archivos estáticos adicionales."""
    return app.send_static_file(filename)


if __name__ == '__main__':
    # ✅ Verificar que la API key está configurada antes de iniciar
    if not os.getenv('OPENAI_API_KEY'):
        console.print("[bold red]❌ OPENAI_API_KEY no está configurada[/bold red]")
        logger.error("OPENAI_API_KEY no está configurada")
        exit(1)

    # ℹ️ Mostrar información del sistema y configuración
    console.print("[bold blue]" + "="*60 + "[/bold blue]")
    console.print("[bold cyan]🎤 SERVIDOR DE CONVERSACIÓN POR VOZ[/bold cyan]")
    console.print("[bold blue]" + "="*60 + "[/bold blue]")
    console.print(f"[green]✅ OpenAI API Key configurada[/green]")
    console.print(f"[green]✅ Modelo para audio (entrada/salida):[/green] [cyan]{os.getenv('MODEL_FOR_AUDIO', 'gpt-4o-audio-preview')}[/cyan]")
    console.print(f"[green]✅ Historial inicializado con mensaje del sistema[/green]")
    console.print("[bold blue]" + "="*60 + "[/bold blue]")
    console.print("[bold cyan]📡 Servidor disponible en:[/bold cyan] [link]http://0.0.0.0:5000[/link]")
    console.print("[bold yellow]💡 Endpoints disponibles:[/bold yellow]")
    console.print("   [cyan]POST /conversation[/cyan] - Conversación por voz")
    console.print("   [cyan]GET  /[/cyan]            - Interfaz web")
    console.print("[bold blue]" + "="*60 + "[/bold blue]")
    
    logger.info("Iniciando servidor de conversación por voz...")
    app.run(debug=True, host='0.0.0.0', port=5000)
