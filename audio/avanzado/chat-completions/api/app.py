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

@app.route('/conversation', methods=['POST'])
def conversation():
    """
    Endpoint principal para manejar conversaciones por voz.
    Recibe un archivo de audio, lo transcribe, genera una respuesta y la convierte a audio.
    """
    try:
        console.print("\n[bold blue]" + "="*50 + "[/bold blue]")
        console.print("[bold yellow]🎤 NUEVA CONVERSACIÓN INICIADA[/bold yellow]")
        console.print("[bold blue]" + "="*50 + "[/bold blue]")
        
        # Verificar que se recibió un archivo de audio
        if 'audio' not in request.files:
            console.print("[bold red]❌ No se encontró archivo de audio en la request[/bold red]")
            return jsonify({"error": "No se encontró archivo de audio"}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            console.print("[bold red]❌ Archivo de audio vacío[/bold red]")
            return jsonify({"error": "No se seleccionó archivo"}), 400

        console.print(f"[bold blue]🎵 Procesando archivo de audio:[/bold blue] [cyan]{audio_file.filename}[/cyan]")

        # Guardar temporalmente el archivo de audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_input:
            audio_file.save(temp_input.name)

            # 1. Transcribir audio a texto usando Whisper
            console.print("[bold yellow]🎤 Transcribiendo audio con Whisper...[/bold yellow]")
            with open(temp_input.name, 'rb') as audio_data:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_data,
                    language="es"  # Especificar español
                )

            user_message = transcription.text
            console.print(f"[bold green]✅ Texto transcrito:[/bold green] [white]'{user_message}'[/white]")

            # Limpiar archivo temporal
            os.unlink(temp_input.name)

        # 2. Agregar mensaje del usuario al historial
        conversation_history.append({"role": "user", "content": user_message})

        # 3. Generar respuesta usando ChatGPT
        console.print("[bold magenta]🤖 Generando respuesta con ChatGPT...[/bold magenta]")
        response = client.chat.completions.create(
            model=os.getenv("MODEL_FOR_AUDIO"),
            modalities=["text", "audio"],
            audio={"voice": "nova", "format": "wav"},
            messages=conversation_history,
        )

        # Obtener el texto de la respuesta y agregarlo al historial
        assistant_message = response.choices[0].message.content or "Respuesta de audio generada"
        conversation_history.append({"role": "assistant", "content": assistant_message})
        
        console.print(f"[bold cyan]💬 Respuesta generada:[/bold cyan] [white]'{assistant_message}'[/white]")

        wav_bytes = base64.b64decode(response.choices[0].message.audio.data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(wav_bytes)
            tmpfile_path = tmpfile.name

        console.print(f"[bold green]✅ Audio generado exitosamente[/bold green] [green]({len(wav_bytes)} bytes)[/green] 🎵")
        console.print(f"[bold blue]📊 Historial de conversación:[/bold blue] [cyan]{len(conversation_history)-1} mensajes[/cyan]") # -1 para excluir sistema
        console.print("[bold blue]" + "="*50 + "[/bold blue]\n")

        return send_file(tmpfile_path, mimetype="audio/wav")

    except Exception as e:
        console.print(f"[bold red]❌ Error en conversación:[/bold red] [red]{str(e)}[/red]")
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
        console.print("[bold red]❌ OPENAI_API_KEY no está configurada[/bold red]")
        logger.error("OPENAI_API_KEY no está configurada")
        exit(1)

    # Mostrar información del sistema
    console.print("[bold blue]" + "="*60 + "[/bold blue]")
    console.print("[bold cyan]🎤 SERVIDOR DE CONVERSACIÓN POR VOZ[/bold cyan]")
    console.print("[bold blue]" + "="*60 + "[/bold blue]")
    console.print(f"[green]✅ OpenAI API Key configurada[/green]")
    console.print(f"[green]✅ Modelo para audio:[/green] [cyan]{os.getenv('MODEL_FOR_AUDIO', 'gpt-4o-audio-preview')}[/cyan]")
    console.print(f"[green]✅ Historial inicializado con mensaje del sistema[/green]")
    console.print("[bold blue]" + "="*60 + "[/bold blue]")
    console.print("[bold cyan]📡 Servidor disponible en:[/bold cyan] [link]http://0.0.0.0:5000[/link]")
    console.print("[bold yellow]💡 Endpoints disponibles:[/bold yellow]")
    console.print("   [cyan]GET  /health[/cyan]      - Estado del servicio")
    console.print("   [cyan]POST /conversation[/cyan] - Conversación por voz")
    console.print("   [cyan]GET  /[/cyan]            - Interfaz web")
    console.print("[bold blue]" + "="*60 + "[/bold blue]")
    
    logger.info("Iniciando servidor de conversación por voz...")
    app.run(debug=True, host='0.0.0.0', port=5000)
