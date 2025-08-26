# Puedes encontrar todos los que hay aquí: https://python.langchain.com/docs/integrations/document_loaders/
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from langchain_community.document_loaders.web_base import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich.console import Console

from langchain_openai import OpenAIEmbeddings

import os
from dotenv import load_dotenv

load_dotenv()

console = Console()

# Siguiendo el ejemplo de rag que te mostré en este otro vídeo, vamos a indexar información de Google para ser mejores Youtubers
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


# Inicializar embeddings
embeddings = OpenAIEmbeddings(model=os.getenv("EMBEDDINGS_MODEL_ID"),
                              base_url=os.getenv("ENDPOINT_URL"),
                              api_key=os.getenv("API_KEY"))


# https://python.langchain.com/docs/integrations/vectorstores/
client = QdrantClient("http://qdrant:6333")

# Recrear la colección
client.recreate_collection(
    collection_name="youtube_guides",
    vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name="youtube_guides",
    embedding=embeddings,
)


# https://python.langchain.com/docs/tutorials/rag/#preview
# Iteramos las URLs y creamos un loader para cada una
for url in URLs:
    console.print(
        f":mag: [bold blue]Indexando:[/bold blue] {url['name']} ([cyan]{url['url']}[/cyan])")
    loader = WebBaseLoader(web_path=url["url"])
    docs = loader.load()
    console.print(docs)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    _ = vector_store.add_documents(documents=all_splits)


console.print(":rocket: [bold green]Indexación completada.[/bold green]")
