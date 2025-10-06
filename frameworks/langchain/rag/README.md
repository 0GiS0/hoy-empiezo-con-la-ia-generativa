# 📚 RAG con LangChain

¡Hola developer 👋🏻! En esta sección puedes ver cómo es posible crear un chatbot inteligente que utiliza RAG o respuesta directa en función de lo que le envie el usuario.


## 📁 Estructura del Proyecto

```
rag/
├── 📄 README.md                    # Este archivo
├── 📄 requirements.txt             # Dependencias para document-loaders.py
├── 📄 document-loaders.py          # Script para indexar documentos
├── 🔐 .env                         # Variables de entorno
│
├── 🐍 api/                         # Backend Flask
│   ├── 📄 server.py                # Servidor principal con SSE
│   ├── 📄 requirements.txt         # Dependencias del backend
│   ├── 📄 README.md                # Documentación del backend
│   ├── 🔐 .env                     # Config del servidor
│   └── 💾 data/
│       └── message_history.sqlite  # Base de datos de historial
│
└── 🌐 web/                         # Frontend
    ├── 📄 index.html               # Interfaz del chat
    ├── 📄 styles.css               # Estilos modernos
    └── 📄 chat.js                  # Lógica del chat + SSE
```

## 🚶🏻‍♀️ Pasos para reproducir 

### Cargar documentos en la base de datos vectorial Qdrant

Para poder probar este ejemplo lo primero que necesitas es una base de datos vectorial donde guardar los documentos que quieres consultar. En este caso está configurado para que la misma sea Qdrant. Si has abierto este repo dentro de un Dev Container ya tienes la misma.

Para cargar los documentos lo primero que necesitas es posicionarte en el directorio `frameworks/langchain/rag` e instalar las dependencias:

```bash
# Instalar dependencias
pip install -r requirements.txt
```

Copia `.env.sample` a `.env` y configura:

```bash
# El modelo que quieres utilizar para generar los embeddings (los vectores que representan la información)
EMBEDDINGS_MODEL_ID=your_embeddings_model_id
# El endpoint de la API del proveedor que quieres utilizar
ENDPOINT_URL=your_endpoint_url
# La API key para autenticarte en el proveedor si fuera necesario
API_KEY=your_api_key
# 🗄️ Qdrant Vector Store
QDRANT_URL=http://qdrant:6333               # URL de Qdrant
```

Una vez que ya tienes las dependencias y las variables de entorno configuradas, puedes lanzar el script `load_docs.py`

```bash
# Ejecutar script para cargar documentos
python load_docs.py
```

Este script:
- 📥 Descarga documentación de YouTube
- ✂️ Divide en chunks
- 🧬 Genera embeddings
- 📤 Sube a Qdrant

### 5️⃣ **Iniciar el servidor**

Una vez que ya tienes la base de datos vectorial con información, podemos probar el chat. Para ello debes posicionarte en `frameworks/langchain/rag/api` 

Y debes por un lado instalar las dependencias:

```bash
cd frameworks/langchain/rag/api
pip install -r requirements.txt
```

Y también configurar las variables de entorno copiando el archivo `.env-sample` del directorio con el nombre `.env`.

Una vez que tengas esto, ya puedes lanzar el servidor:

```bash
python server.py
```

El mismo estará disponible en: **http://localhost:5500** 🌐

## 💻 Uso de la Aplicación

### **Interfaz Web**

1. 🌐 Abre `http://localhost:5500`
2. 💬 Escribe `Hola` o similar
3. ⏎ Presiona Enter o click en "Enviar"
4. En este caso la respuesta debería de ser directa sin hacer RAG
5. Ahora Escribe `¿Cómo mejoro mis miniaturas en mis vídeos de YouTube?`
6. En este caso la respuesta debería de ser usando RAG.


### **Panel de Configuración**

En el lateral derecho verás:
- 🤖 **Modelos**: Router, Answer, Embeddings
- 🔌 **Proveedor**: GitHub Models, OpenAI, Ollama, etc.
- 🗄️ **Vector Store**: Documentos indexados en Qdrant

