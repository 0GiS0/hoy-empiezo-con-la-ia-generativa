
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
URLs = [
    {"url": "https://support.google.com/youtube/answer/9527654?hl=es",
        "name": "Configurar la audiencia de un canal o un vídeo"},
    {"url": "https://support.google.com/youtube/answer/11913617?sjid=11557296865847177507-EU",
        "name": "Consejos para subir vídeos de YouTube"},
    {"url": "https://support.google.com/youtube/answer/11908409?sjid=11557296865847177507-EU",
        "name": "Consejos para optimizar vídeos"},
    {"url": "https://support.google.com/youtube/answer/12340300?sjid=11557296865847177507-EU",
        "name": "Consejos sobre miniaturas y títulos"},
    {"url": "https://support.google.com/youtube/answer/12948449?sjid=11557296865847177507-EU",
        "name": "Consejos para las descripciones de los vídeos"},
    {"url": "https://support.google.com/youtube/answer/13616979?sjid=11557296865847177507-EU",
        "name": "Consejos para programar subidas"},
    {"url": "https://support.google.com/youtube/answer/11913513?sjid=11557296865847177507-EU",
        "name": "Consejos sobre equipos de vídeo"},
    {"url": "https://support.google.com/youtube/answer/12340105?sjid=11557296865847177507-EU",
        "name": "Consejos de grabación"},
    {"url": "https://support.google.com/youtube/answer/12948118?sjid=11557296865847177507-EU",
        "name": "Consejos para grabar con un dispositivo móvil"},
    {"url": "https://support.google.com/youtube/answer/11221953?sjid=11557296865847177507-EU",
        "name": "Consejos para editar vídeos"},
    {"url": "https://support.google.com/youtube/answer/15575746?sjid=11557296865847177507-EU",
        "name": "Consejos para las retiradas por infracción de derechos de autor"},
    {"url": "https://support.google.com/youtube/answer/15577610?sjid=11557296865847177507-EU",
        "name": "Consejos para encontrar música de uso autorizado"},
    {"url": "https://support.google.com/youtube/answer/11912631?sjid=11557296865847177507-EU",
        "name": "Consejos sobre las publicaciones"},
    {"url": "https://support.google.com/youtube/answer/12929858?sjid=11557296865847177507-EU",
        "name": "Consejos para conseguir más acuerdos de marca"},
    {"url": "https://support.google.com/youtube/answer/11912533?sjid=11557296865847177507-EU",
        "name": "Consejos para ganar dinero en YouTube"},
    {"url": "https://support.google.com/youtube/answer/13615784?sjid=11557296865847177507-EU",
        "name": "Consejos sobre usuarios nuevos y recurrentes"},
    {"url": "https://support.google.com/youtube/answer/13616340?sjid=11557296865847177507-EU",
        "name": "Consejos para saber qué contenido crear"},
    {"url": "https://support.google.com/youtube/answer/11912632?sjid=11557296865847177507-EU",
        "name": "Consejos sobre Estadísticas de YouTube"},
    {"url": "https://support.google.com/youtube/answer/11914225?sjid=11557296865847177507-EU",
        "name": "Consejos de búsqueda y descubrimiento"},
    {"url": "https://support.google.com/youtube/answer/15086271?sjid=11557296865847177507-EU",
        "name": "Consejos para evitar que disminuya el tiempo de visualización"},
    {"url": "https://support.google.com/youtube/answer/12950272?sjid=11557296865847177507-EU",
        "name": "Consejos sobre el banner del canal y la imagen de perfil"},
    {"url": "https://support.google.com/youtube/answer/12356784?sjid=11557296865847177507-EU",
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
for url in URLs:
    console.print(
        f":mag: [bold blue]Indexando:[/bold blue] {url['name']} ([cyan]{url['url']}[/cyan])")
    loader = WebBaseLoader(web_path=url["url"])
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100)  # ⚡ Reducido para Docker Model Runner
    all_splits = text_splitter.split_documents(docs)

    # 💾 Procesar de 1 en 1 para evitar errores de "input too large"
    # 🐳 Docker Model Runner tiene límites más estrictos que otros proveedores
    for i, doc in enumerate(all_splits):
        try:
            _ = vector_store.add_documents(documents=[doc])
            if (i + 1) % 5 == 0 or (i + 1) == len(all_splits):
                console.print(f":white_check_mark: [green]Procesados {i+1} de {len(all_splits)} chunks[/green]")
        except Exception as e:
            console.print(f":warning: [yellow]Error en chunk {i+1}: {str(e)[:100]}...[/yellow]")
            continue


console.print(":rocket: [bold green]Indexación completada.[/bold green]")
