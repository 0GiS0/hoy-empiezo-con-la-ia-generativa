"""
🔄 Traducción automática de subtítulos

Este script toma una transcripción (por ejemplo, generada por el script de speech-to-text) y la traduce al idioma que elijas usando la API de OpenAI.

Flujo principal:
1️⃣ Lee el archivo de transcripción en formato SRT.
2️⃣ Divide el texto en chunks si es necesario para no exceder el límite de tokens.
3️⃣ Traduce cada chunk usando OpenAI GPT-4o.
4️⃣ Guarda la traducción en un nuevo archivo.

Los nombres de funciones y variables están en inglés, pero los comentarios y mensajes te guían en español y con emojis.
"""

from openai import OpenAI, OpenAIError
import tiktoken
import os
from rich.console import Console
from dotenv import load_dotenv

# Variables de entorno
FORMAT = "srt"

console = Console()
load_dotenv()

# Configurar el cliente OpenAI
client = OpenAI(
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=os.getenv("API_KEY")
)

# Configurar rutas
ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA_FOLDER = os.path.join(ROOT, "../speech-to-text/media/")


def translate_text(text, target_language="en", max_tokens=2000):
    """
    🌍 Traduce el texto al idioma objetivo, dividiendo en chunks si es necesario para no exceder el límite de tokens.
    """
    # Usa el codificador de tokens de OpenAI para contar tokens
    enc = tiktoken.encoding_for_model("gpt-4o")
    tokens = enc.encode(text)
    total_tokens = len(tokens)

    if total_tokens <= max_tokens:
        chunks = [text]
    else:
        # Divide los tokens en chunks de max_tokens
        chunks = []
        for i in range(0, total_tokens, max_tokens):
            chunk_tokens = tokens[i:i+max_tokens]
            chunk_text = enc.decode(chunk_tokens)
            chunks.append(chunk_text)

    prompt = f"""
        Traduce el siguiente texto al {target_language}:\n{text}. No añadas nada más que la traducción, mantén los tiempos y el formato original. 
        Tampoco añadas markdown ni etiquetas HTML.
        La intención es que el resultado sean los subtítulos de un vídeo.
    """


    translated_chunks = []
    for idx, chunk in enumerate(chunks):
        with console.status(f"[bold blue]🌐 Traduciendo chunk {idx+1}/{len(chunks)} a {target_language}...[/bold blue]", spinner="dots"):
            try:
                translation = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Eres un traductor experto."},
                        {"role": "user", "content": prompt}
                    ]
                )
                translated_chunks.append(
                    translation.choices[0].message.content.strip())
            except OpenAIError as e:
                console.print(
                    f"[bold red]❌ Error al traducir el chunk {idx+1}: {e}[/bold red]")
                translated_chunks.append("")

    return "\n".join(translated_chunks)


# 📄 Traducir transcripción a otro idioma
transcription_path = os.path.join(MEDIA_FOLDER, f"transcripcion.{FORMAT}")
translated_path = os.path.join(MEDIA_FOLDER, f"transcripcion_traducida.{FORMAT}")

try:
    with open(transcription_path, "r", encoding="utf-8") as f:
        original_text = f.read()
    console.print(f"[blue]📖 Archivo de transcripción leído correctamente.[/blue]")
    
    translated_text = translate_text(original_text, target_language="en")
    
    with open(translated_path, "w", encoding="utf-8") as f:
        f.write(translated_text)
    console.print(f"[green]✅ Transcripción traducida y guardada en {translated_path}[/green]")
    
except FileNotFoundError:
    console.print(f"[bold red]❌ No se encontró el archivo de transcripción en {transcription_path}[/bold red]")
    console.print("[yellow]⚠️ Asegúrate de ejecutar primero el script de speech-to-text.[/yellow]")
except Exception as e:
    console.print(f"[bold red]❌ Error al procesar la traducción: {e}[/bold red]")
