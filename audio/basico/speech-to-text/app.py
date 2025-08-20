
"""
Extrae el audio de un video MP4, lo divide si es necesario, lo transcribe usando OpenAI Whisper y guarda la transcripción.

🔄 Flujo principal:
1️⃣ Busca un archivo de video MP4 en la carpeta 'media/'.
2️⃣ Extrae el audio y lo guarda como MP3.
3️⃣ Si el audio supera el tamaño máximo permitido por la API, lo divide en trozos.
4️⃣ Transcribe cada trozo (o el audio completo) usando la API de OpenAI Whisper.
5️⃣ Guarda la transcripción en formato SRT o JSON.

🛠️ Requisitos:
- Python 3.8+
- Instalar dependencias:
    pip install moviepy openai python-dotenv rich pydub
- Configurar las variables de entorno en un archivo .env en la raíz del proyecto:
    ENDPOINT_URL=<URL de la API de OpenAI>
    API_KEY=<tu clave de API>

▶️ Ejecuta el script desde la terminal:
    python app.py
"""

from moviepy import VideoFileClip
import glob
from openai import OpenAI
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from pydub import AudioSegment

console = Console()
load_dotenv()
MAX_MB = 25
CHUNK_MS = 10 * 60 * 1000  # 10 minutos en milisegundos
FORMAT = "srt"
ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA_FOLDER = os.path.join(ROOT, "media/")

def find_video():
    """
    📹 Busca el primer archivo MP4 en la carpeta de medios.
    Devuelve la ruta del video encontrado.
    """
    console.print(f"[bold blue]Directorio raíz:[/bold blue] {ROOT}")
    console.print(f"[bold blue]Carpeta de medios:[/bold blue] {MEDIA_FOLDER}")
    video_files = glob.glob(os.path.join(MEDIA_FOLDER, "*.mp4"))
    if not video_files:
        console.print("[bold red]❌ No se encontró ningún archivo .mp4 en la carpeta especificada.[/bold red]")
        exit(1)
    return video_files[0]

def extract_audio(video_path):
    """
    🎵 Extrae el audio de un video y lo guarda como MP3.
    Devuelve la ruta del audio, el objeto video y el objeto audio.
    """
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TimeElapsedColumn(), console=console, transient=True) as progress:
        task = progress.add_task("Cargando video...", total=None)
        video = VideoFileClip(video_path)
        progress.update(task, description="Extrayendo audio...")
        audio = video.audio
        audio_path = os.path.join(MEDIA_FOLDER, "audio.mp3")
        audio.write_audiofile(audio_path, logger=None)
        progress.update(task, description="Audio extraído.")
        progress.stop()
    return audio_path, video, audio

def split_audio(audio_path):
    """
    ✂️ Divide el audio en trozos de CHUNK_MS milisegundos si supera el tamaño máximo.
    Devuelve una lista de trozos de audio.
    """
    audio_seg = AudioSegment.from_file(audio_path)
    chunks = [audio_seg[i:i+CHUNK_MS] for i in range(0, len(audio_seg), CHUNK_MS)]
    return chunks

def save_transcription(text, format):
    """
    📝 Guarda la transcripción en la carpeta de medios.
    """
    with open(f"{MEDIA_FOLDER}/transcripcion.{format}", "w") as f:
        f.write(text)

def main():
    """
    🚀 Flujo principal: busca video, extrae audio, divide si es necesario, transcribe y guarda.
    """
    video_path = find_video()
    audio_path, video, audio = extract_audio(video_path)
    audio_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    console.print(f"[green]🎶 Audio extraído correctamente. Tamaño: {audio_size_mb:.2f} MB[/green]")

    # Inicializa el cliente de OpenAI
    client = OpenAI(base_url=os.getenv("ENDPOINT_URL"), api_key=os.getenv("API_KEY"))

    def transcribe_file(path, idx=None):
        """
        🗣️ Transcribe un archivo de audio usando la API de OpenAI Whisper.
        """
        try:
            with console.status(f"[bold blue]🔊 Transcribiendo audio{' (trozo ' + str(idx) + ')' if idx is not None else ''}...[/bold blue]", spinner="dots"):
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=open(path, "rb"),
                    response_format=FORMAT
                )
                if FORMAT == "json":
                    return transcription.model_dump_json()
                else:
                    return transcription
        except Exception as e:
            console.print(f"[bold red]❌ Error al transcribir el archivo {path}: {e}[/bold red]")
            return ""

    try:
        if audio_size_mb > MAX_MB:
            console.print(f"[yellow]⚠️ El archivo supera los {MAX_MB}MB, se dividirá en partes.[/yellow]")
            chunks = split_audio(audio_path)
            all_text = ""
            for idx, chunk in enumerate(chunks):
                chunk_path = f"audio/speech-to-text/media/audio_chunk_{idx+1}.mp3"
                chunk.export(chunk_path, format="mp3")
                chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
                console.print(f"[cyan]✂️ Transcribiendo trozo {idx+1}/{len(chunks)} ({chunk_size_mb:.2f} MB)...[/cyan]")
                text = transcribe_file(chunk_path, idx+1)
                all_text += text + "\n"
            save_transcription(all_text, FORMAT)
            console.print(f"[bold green]\n✅ Transcripción completa y guardada en transcripcion.{FORMAT} 📝\n[/bold green]")
        else:
            text = transcribe_file(audio_path)
            if text:
                console.print("[bold green]\n✅ Transcripción completada:[/bold green]")
                console.print(text)
                save_transcription(text, FORMAT)
                console.print(f"[bold green]\n✅ Transcripción guardada en transcripcion.{FORMAT} 📝\n[/bold green]")
            else:
                console.print(f"[bold red]\n❌ No se pudo obtener la transcripción del audio.\n[/bold red]")
    except Exception as e:
        console.print(f"[bold red]\n❌ Error general al transcribir el audio: {e}\n[/bold red]")
    finally:
        # Limpieza explícita para evitar errores al cerrar
        try:
            video.close()
            audio.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
