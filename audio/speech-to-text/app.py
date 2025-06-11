from moviepy import VideoFileClip, TextClip, CompositeVideoClip
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
# 10 minutos en milisegundos (ajusta según necesidad)
CHUNK_MS = 10 * 60 * 1000
FORMAT = "srt"

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TimeElapsedColumn(),
    console=console,
    transient=True,
) as progress:
    task = progress.add_task("Buscando video...", total=None)
    video_files = glob.glob("audio/speech-to-text/media/*.mp4")
    if not video_files:
        console.print(
            "[bold red]No se encontró ningún archivo .mp4 en la carpeta especificada.[/bold red]")
        exit(1)
    video_path = video_files[0]
    progress.update(task, description="Cargando video...")
    video = VideoFileClip(video_path)
    progress.update(task, description="Extrayendo audio...")
    audio = video.audio
    audio_path = "audio/speech-to-text/media/audio_extraido.mp3"
    audio.write_audiofile(audio_path, logger=None)
    progress.update(task, description="Audio extraído.")
    progress.stop()

audio_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
console.print(
    f"[green]Audio extraído correctamente. Tamaño: {audio_size_mb:.2f} MB[/green]")

client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)


def transcribe_file(path, idx=None):
    with console.status(f"[bold blue]Transcribiendo audio{' (trozo ' + str(idx) + ')' if idx is not None else ''}...[/bold blue]", spinner="dots"):
        transcription = client.audio.transcriptions.create(
            # model="gpt-4o-transcribe",
            model="whisper-1",
            file=open(path, "rb"),
            response_format=FORMAT
        )


        if FORMAT  == "json":
            return transcription.model_dump_json()
        else:
            return transcription

try:
    if audio_size_mb > MAX_MB:
        console.print(
            f"[yellow]El archivo supera los {MAX_MB}MB, se dividirá en partes.[/yellow]")
        audio_seg = AudioSegment.from_file(audio_path)
        chunks = [audio_seg[i:i+CHUNK_MS]
                  for i in range(0, len(audio_seg), CHUNK_MS)]
        all_text = ""
        for idx, chunk in enumerate(chunks):
            chunk_path = f"audio/speech-to-text/media/audio_chunk_{idx+1}.mp3"
            chunk.export(chunk_path, format="mp3")
            chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
            console.print(
                f"[cyan]Transcribiendo trozo {idx+1}/{len(chunks)} ({chunk_size_mb:.2f} MB)...[/cyan]")
            text = transcribe_file(chunk_path, idx+1)
            all_text += text + "\n"
        with open(f"audio/speech-to-text/media/transcripcion.{FORMAT}", "w") as f:
            f.write(all_text)
        console.print(
            f"[green]Transcripción completa y guardada en transcripcion.{FORMAT}[/green]")
    else:
        text = transcribe_file(audio_path)
        console.print("[green]Transcripción completada:[/green]")
        console.print(text)
        with open(f"audio/speech-to-text/media/transcripcion.{FORMAT}", "w") as f:
            f.write(text)
        console.print(
            f"[green]Transcripción guardada en transcripcion.{FORMAT}[/green]")
except Exception as e:
    console.print(f"[bold red]Error al transcribir el audio: {e}[/bold red]")
finally:
    # Limpieza explícita para evitar errores al cerrar
    try:
        if 'video' in locals():
            video.close()
        if 'audio' in locals():
            audio.close()
    except:
        pass  # Ignorar errores de limpieza
