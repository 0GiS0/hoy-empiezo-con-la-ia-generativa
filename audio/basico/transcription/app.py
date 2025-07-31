
from openai import OpenAIError
import tiktoken
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from dotenv import load_dotenv

# Variables de entorno
FORMAT = "srt"

console = Console()
load_dotenv()


def translate_text(text, target_language="en", max_tokens=2000):
    """
    Traduce el texto al idioma objetivo, dividiendo en chunks si es necesario para no exceder el límite de tokens.
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

    translated_chunks = []
    for idx, chunk in enumerate(chunks):
        with console.status(f"[bold blue]Traduciendo chunk {idx+1}/{len(chunks)} a {target_language}...[/bold blue]", spinner="dots"):
            try:
                translation = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Eres un traductor experto."},
                        {"role": "user", "content": f"Traduce el siguiente texto al {target_language}:\n{chunk}"}
                    ]
                )
                translated_chunks.append(
                    translation.choices[0].message.content.strip())
            except OpenAIError as e:
                console.print(
                    f"[bold red]Error al traducir el chunk {idx+1}: {e}[/bold red]")
                translated_chunks.append("")

    return "\n".join(translated_chunks)

 # Traducir transcripción a otro idioma
with open(f"audio/basico/speech-to-text/media/transcripcion.{FORMAT}", "rb") as f:
    translated_text = translate_text(
        f.read().decode(), target_language="en")
    with open(f"audio/basico/speech-to-text/media/transcripcion_traducida.{FORMAT}", "w") as f:
        f.write(translated_text)
        console.print(f"[green]Transcripción traducida y guardada en transcripcion_traducida.{FORMAT}[/green]")
