
# Para este ejemplo he utilizado una base de datos vectorial de tipo Qdrant, pero podría adaptarse a otros tipos de bases de datos
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Para poder recuperar la información de forma sencilla puedes usar Document Loaders
# Puedes encontrar todos los que hay aquí: https://python.langchain.com/docs/integrations/document_loaders/
from langchain_community.document_loaders.web_base import WebBaseLoader

# Seguramente necesitarás dividir el texto en trozos más pequeños
from langchain_text_splitters import RecursiveCharacterTextSplitter


from rich.console import Console

from langchain_openai import OpenAIEmbeddings

import os
import sys
from dotenv import load_dotenv

load_dotenv()

console = Console()

# ✅ Validar variables de entorno
required_vars = ["EMBEDDINGS_MODEL_ID", "ENDPOINT_URL"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    console.print(f":x: [bold red]Error: Faltan variables de entorno:[/bold red] {', '.join(missing_vars)}")
    console.print(":warning: [yellow]Por favor, configura tu archivo .env con valores reales.[/yellow]")
    sys.exit(1)

# 🔐 Para API_KEY, si no está configurado o es placeholder, usar valor dummy (para Ollama/Model Runner)
api_key = os.getenv("API_KEY")
if not api_key or api_key == "__PON_AQUI_TU_API_KEY__":
    console.print(":information: [yellow]API_KEY no configurado, usando valor dummy (útil para Ollama/Model Runner)[/yellow]")
    api_key = "dummy-key"

# 🎬 Siguiendo el ejemplo de rag que te mostré en este otro vídeo, vamos a indexar información de Google para ser mejores Youtubers
# 🇪🇸 IMPORTANTE: Todas las URLs incluyen ?hl=es para forzar contenido en español
URLs = [
    {"url": "https://support.google.com/youtube/answer/9527654?hl=es",
        "name": "Configurar la audiencia de un canal o un vídeo"},
    {"url": "https://support.google.com/youtube/answer/11913617?hl=es",
        "name": "Consejos para subir vídeos de YouTube"},
    {"url": "https://support.google.com/youtube/answer/11908409?hl=es",
        "name": "Consejos para optimizar vídeos"},
    {"url": "https://support.google.com/youtube/answer/12340300?hl=es",
        "name": "Consejos sobre miniaturas y títulos"},
    {"url": "https://support.google.com/youtube/answer/12948449?hl=es",
        "name": "Consejos para las descripciones de los vídeos"},
    {"url": "https://support.google.com/youtube/answer/13616979?hl=es",
        "name": "Consejos para programar subidas"},
    {"url": "https://support.google.com/youtube/answer/11913513?hl=es",
        "name": "Consejos sobre equipos de vídeo"},
    {"url": "https://support.google.com/youtube/answer/12340105?hl=es",
        "name": "Consejos de grabación"},
    {"url": "https://support.google.com/youtube/answer/12948118?hl=es",
        "name": "Consejos para grabar con un dispositivo móvil"},
    {"url": "https://support.google.com/youtube/answer/11221953?hl=es",
        "name": "Consejos para editar vídeos"},
    {"url": "https://support.google.com/youtube/answer/15575746?hl=es",
        "name": "Consejos para las retiradas por infracción de derechos de autor"},
    {"url": "https://support.google.com/youtube/answer/15577610?hl=es",
        "name": "Consejos para encontrar música de uso autorizado"},
    {"url": "https://support.google.com/youtube/answer/11912631?hl=es",
        "name": "Consejos sobre las publicaciones"},
    {"url": "https://support.google.com/youtube/answer/12929858?hl=es",
        "name": "Consejos para conseguir más acuerdos de marca"},
    {"url": "https://support.google.com/youtube/answer/11912533?hl=es",
        "name": "Consejos para ganar dinero en YouTube"},
    {"url": "https://support.google.com/youtube/answer/13615784?hl=es",
        "name": "Consejos sobre usuarios nuevos y recurrentes"},
    {"url": "https://support.google.com/youtube/answer/13616340?hl=es",
        "name": "Consejos para saber qué contenido crear"},
    {"url": "https://support.google.com/youtube/answer/11912632?hl=es",
        "name": "Consejos sobre Estadísticas de YouTube"},
    {"url": "https://support.google.com/youtube/answer/11914225?hl=es",
        "name": "Consejos de búsqueda y descubrimiento"},
    {"url": "https://support.google.com/youtube/answer/15086271?hl=es",
        "name": "Consejos para evitar que disminuya el tiempo de visualización"},
    {"url": "https://support.google.com/youtube/answer/12950272?hl=es",
        "name": "Consejos sobre el banner del canal y la imagen de perfil"},
    {"url": "https://support.google.com/youtube/answer/12356784?hl=es",
        "name": "Consejos sobre los estrenos de YouTube"},
]


# 🚀 Inicializar embeddings
embeddings_model = os.getenv("EMBEDDINGS_MODEL_ID")
console.print(f":gear: [cyan]Usando modelo de embeddings:[/cyan] [bold]{embeddings_model}[/bold]")

embeddings = OpenAIEmbeddings(
    model=embeddings_model,
    base_url=os.getenv("ENDPOINT_URL"),
    api_key=api_key  # 🔑 Usa el valor validado (puede ser dummy para Ollama/Model Runner)
)

# 📏 Determinar el tamaño del vector según el modelo
# 🔢 embeddinggemma usa 768 dimensiones
# 🔢 text-embedding-3-large usa 3072 dimensiones
# 🔢 text-embedding-3-small usa 1536 dimensiones
if "embeddinggemma" in embeddings_model:
    vector_size = 768
elif "text-embedding-3-large" in embeddings_model:
    vector_size = 3072
elif "text-embedding-3-small" in embeddings_model:
    vector_size = 1536
else:
    # ⚠️ Valor por defecto, pero se recomienda verificar
    console.print(f":warning: [yellow]Modelo desconocido, usando 768 dimensiones por defecto. Verifica que sea correcto.[/yellow]")
    vector_size = 768

console.print(f":bar_chart: [cyan]Tamaño del vector:[/cyan] [bold]{vector_size}[/bold] dimensiones")

# 🔌 https://python.langchain.com/docs/integrations/vectorstores/
client = QdrantClient("http://qdrant:6333")

# 🔄 Recrear la colección (usando método recomendado en lugar del deprecado)
collection_name = "youtube_guides"

if client.collection_exists(collection_name):
    console.print(f":wastebasket: [yellow]La colección '[bold]{collection_name}[/bold]' ya existe. Eliminándola...[/yellow]")
    client.delete_collection(collection_name)
    console.print(f":white_check_mark: [green]Colección eliminada.[/green]")

console.print(f":sparkles: [cyan]Creando colección '[bold]{collection_name}[/bold]'...[/cyan]")
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
)
console.print(f":white_check_mark: [green]Colección creada correctamente.[/green]")

vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)


# 📖 https://python.langchain.com/docs/tutorials/rag/#preview
# 🔄 Iteramos las URLs y creamos un loader para cada una
# 🇪🇸 Configuramos headers para asegurar contenido en español
header_template = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "es-ES,es;q=0.9",  # 🌍 Priorizar español
}

for url in URLs:
    console.print(
        f":mag: [bold blue]Indexando:[/bold blue] {url['name']} ([cyan]{url['url']}[/cyan])")
    
    # 🌐 WebBaseLoader con headers personalizados para forzar español
    loader = WebBaseLoader(
        web_path=url["url"],
        header_template=header_template
    )
    docs = loader.load()
    
    # 🏷️ Añadir metadata de idioma y título al documento
    for doc in docs:
        doc.metadata["language"] = "es"
        doc.metadata["title"] = url["name"]

    # 📏 Chunks más grandes para mantener contexto coherente
    # chunk_size: tamaño ideal para consejos/guías completas: ahora 2000
    # chunk_overlap: solapamiento para mantener continuidad entre chunks: 200
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]  # Prioriza separadores naturales
    )
    all_splits = text_splitter.split_documents(docs)

    # 💾 Procesar de 1 en 1 para evitar errores de "input too large"
    for i, doc in enumerate(all_splits):
        try:
            _ = vector_store.add_documents(documents=[doc])
            if (i + 1) % 5 == 0 or (i + 1) == len(all_splits):
                console.print(f":white_check_mark: [green]Procesados {i+1} de {len(all_splits)} chunks[/green]")
        except Exception as e:
            console.print(f":warning: [yellow]Error en chunk {i+1}: {str(e)[:100]}...[/yellow]")
            continue


console.print(":rocket: [bold green]Indexación completada.[/bold green]")
