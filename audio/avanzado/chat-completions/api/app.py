import os
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import logging
from dotenv import load_dotenv
from rich.console import Console
import base64


console = Console()

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app, resources={r"*": {"origins": "*"}})

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar cliente de OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Historial de conversación
conversation_history = [
    {"role": "system", "content": "Eres un asistente útil y amigable. Responde de manera concisa y conversacional."}
]


@app.route('/health', methods=['GET'])
def health():
    """Endpoint para verificar el estado del servicio"""
    return jsonify({"status": "ok", "message": "Servicio de conversación por voz funcionando"})


@app.route('/conversation', methods=['POST'])
def conversation():
    """
    Endpoint principal para manejar conversaciones por voz.
    Recibe un archivo de audio, lo transcribe, genera una respuesta y la convierte a audio.
    """
    try:
        # Verificar que se recibió un archivo de audio
        if 'audio' not in request.files:
            return jsonify({"error": "No se encontró archivo de audio"}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No se seleccionó archivo"}), 400

        logger.info(f"Procesando archivo de audio: {audio_file.filename}")

        # Guardar temporalmente el archivo de audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_input:
            audio_file.save(temp_input.name)

            # 1. Transcribir audio a texto usando Whisper
            logger.info("Transcribiendo audio...")
            with open(temp_input.name, 'rb') as audio_data:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_data,
                    language="es"  # Especificar español
                )

            user_message = transcription.text
            logger.info(f"Texto transcrito: {user_message}")

            # Limpiar archivo temporal
            os.unlink(temp_input.name)

        # 2. Agregar mensaje del usuario al historial
        conversation_history.append({"role": "user", "content": user_message})

        # 3. Generar respuesta usando ChatGPT
        logger.info("Generando respuesta...")
        response = client.chat.completions.create(
            model=os.getenv("MODEL_FOR_AUDIO"),
            modalities=["text", "audio"],
            audio={"voice": "nova", "format": "wav"},
            messages=conversation_history,
        )

        # Obtener el texto de la respuesta y agregarlo al historial
        assistant_message = response.choices[0].message.content or "Respuesta de audio generada"
        conversation_history.append({"role": "assistant", "content": assistant_message})

        wav_bytes = base64.b64decode(response.choices[0].message.audio.data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(wav_bytes)
            tmpfile_path = tmpfile.name

        console.print(
            f"[bold green]✅ Audio generado exitosamente[/bold green] 🟢")

        return send_file(tmpfile_path, mimetype="audio/wav")

    except Exception as e:
        logger.error(f"Error en conversación: {str(e)}")
        return jsonify({"error": f"Error procesando conversación: {str(e)}"}), 500





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


if __name__ == '__main__':
    # Verificar que la API key está configurada
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY no está configurada")
        exit(1)

    logger.info("Iniciando servidor de conversación por voz...")
    app.run(debug=True, host='0.0.0.0', port=5000)
