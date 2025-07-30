# 🔊 Capítulo 7: Audio y la IA Generativa 🎵🤖

¡Bienvenido al mundo del audio con IA Generativa! 🎙️ En este capítulo exploraremos las diferentes formas de trabajar con audio utilizando inteligencia artificial, desde la transcripción de voz hasta conversaciones en tiempo real.

## 📚 ¿Qué encontrarás en este capítulo?

En este directorio encontrarás demos prácticas que te enseñarán a:

- 🎯 **Transcribir audio a texto** con alta precisión
- 🗣️ **Convertir texto a voz** con voces naturales
- 💬 **Crear conversaciones interactivas** con IA
- ⚡ **Implementar comunicación en tiempo real** 
- 🌐 **Integrar funcionalidades de audio en aplicaciones web**

## 🗂️ Estructura del directorio

```
audio/
├── 📄 README.md                    # Esta guía
├── 📋 requirements.txt             # Dependencias principales
├── 🎤 speech-to-text/              # Transcripción de audio a texto
├── 🗣️ text-to-speech/              # Conversión de texto a voz
├── 📝 transcription/               # Herramientas de transcripción avanzada
├── 💬 conversation/                # Conversaciones con IA
├── 🌐 chat-completions-api/        # API de chat con audio
└── ⚡ realtime-api/                # Comunicación en tiempo real
```

## 🚀 Demos disponibles

### 1. 🎤 Speech-to-Text (Transcripción de Audio)

**Ubicación:** `speech-to-text/`

**¿Qué hace?** 
Esta demo te permite transcribir archivos de audio y video a texto utilizando el modelo Whisper de OpenAI. Es especialmente útil para:
- Transcribir videos de YouTube, conferencias o reuniones
- Crear subtítulos automáticos
- Procesar archivos de audio largos dividiéndolos en chunks

**Características:**
- ✅ Soporte para archivos MP4
- ✅ Extracción automática de audio desde video
- ✅ División inteligente de archivos grandes (+25MB)
- ✅ Múltiples formatos de salida (SRT, JSON)
- ✅ Interfaz con indicadores de progreso

Sigue por [👉🏻 aquí](speech-to-text/README.md) para saber cómo usarlo.

### 2. 📝 Transcription (Transcripción Avanzada)

**Ubicación:** `transcription/`

**¿Qué hace?**
Herramientas avanzadas para procesar transcripciones, incluyendo traducción automática a diferentes idiomas.

**Características:**
- ✅ Traducción inteligente de transcripciones
- ✅ División en chunks para textos largos
- ✅ Soporte para múltiples idiomas
- ✅ Conteo de tokens automático

**Cómo usarlo:**
```bash
cd transcription
python app.py
```

### 3. 🌐 Chat Completions API (Chat con Audio)

**Ubicación:** `chat-completions-api/`

**¿Qué hace?**
Una aplicación web completa que combina chat de texto con funcionalidades de audio, permitiendo interacciones multimodales.

**Características:**
- ✅ Interfaz web moderna
- ✅ Chat de texto con IA
- ✅ Integración con audio
- ✅ API REST para integraciones
- ✅ Visualizador de audio

**Cómo usarlo:**
```bash
cd chat-completions-api/api
pip install -r ../../requirements.txt
python app.py
```

Luego abre `web/index.html` en tu navegador o sirve la carpeta web con un servidor local.

**Archivos principales:**
- `api/app.py` - Servidor backend con Flask
- `web/index.html` - Interfaz web
- `web/main.js` - Lógica del frontend
- `web/visualizer.js` - Visualizaciones de audio

### 4. ⚡ Realtime API (Comunicación en Tiempo Real)

**Ubicación:** `realtime-api/`

**¿Qué hace?**
Demo de comunicación en tiempo real con IA, ideal para crear asistentes de voz o aplicaciones conversacionales.

**Características:**
- ✅ Comunicación WebSocket en tiempo real
- ✅ Respuestas instantáneas
- ✅ Soporte HTTPS para producción
- ✅ Interfaz web responsiva

**Cómo usarlo:**
```bash
cd realtime-api/web
# Para desarrollo local
python -m http.server 8000

# Para HTTPS (recomendado)
chmod +x serve-https.sh
./serve-https.sh
```

**Archivos principales:**
- `web/app.js` - Lógica de WebSocket y tiempo real
- `web/index.html` - Interfaz de usuario
- `web/serve-https.sh` - Servidor HTTPS para desarrollo

### 5. 🗣️ Text-to-Speech (Texto a Voz)

**Ubicación:** `text-to-speech/`

**Estado:** 🚧 En desarrollo

**¿Qué hará?**
Demos para convertir texto a voz natural utilizando los modelos TTS de OpenAI.

### 6. 💬 Conversation (Conversaciones con IA)

**Ubicación:** `conversation/`

**Estado:** 🚧 En desarrollo

**¿Qué hará?**
Ejemplos de conversaciones naturales con IA, incluyendo manejo de contexto y memoria conversacional.

## ⚙️ Configuración inicial

### 1. Variables de entorno

Todas las demos requieren configurar variables de entorno. Crea un archivo `.env` en cada directorio que lo necesite:

```env
# Para usar con OpenAI
ENDPOINT_URL=https://api.openai.com/v1
API_KEY=tu_api_key_de_openai

# Para usar con GitHub Models (desarrollo)
ENDPOINT_URL=https://models.inference.ai.azure.com
API_KEY=tu_github_token

# Para usar con Azure OpenAI
ENDPOINT_URL=https://tu-resource.openai.azure.com
API_KEY=tu_azure_api_key
```

### 2. Instalación de dependencias

```bash
# Dependencias principales
pip install -r requirements.txt

# O dependencias específicas por demo
cd speech-to-text
pip install -r requirements.txt
```

### 3. Dependencias del sistema

Para las demos de audio, necesitarás:

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Descarga FFmpeg desde [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

## 🎯 Casos de uso prácticos

### 📹 Transcripción de videos educativos
Usa `speech-to-text/` para crear subtítulos automáticos de tus videos o conferencias.

### 🌍 Traducción de contenido
Combina `speech-to-text/` y `transcription/` para transcribir y traducir contenido a múltiples idiomas.

### 🤖 Asistente de voz
Utiliza `realtime-api/` para crear tu propio asistente de voz interactivo.

### 📱 Aplicación web multimodal
Integra `chat-completions-api/` en tu aplicación para combinar texto y audio.

## 🔧 Tecnologías utilizadas

- **OpenAI Whisper** - Transcripción de audio de última generación
- **OpenAI TTS** - Síntesis de voz natural
- **OpenAI GPT** - Procesamiento de lenguaje natural
- **Flask** - Framework web para APIs
- **WebSockets** - Comunicación en tiempo real
- **FFmpeg** - Procesamiento de multimedia
- **Pydub** - Manipulación de archivos de audio
- **Rich** - Interfaces de consola elegantes

## 📝 Notas importantes

### 🔐 Seguridad
- Nunca subas tus archivos `.env` al repositorio
- Usa tokens con permisos mínimos necesarios
- Para producción, implementa autenticación adecuada

### 💰 Costos
- Los modelos de transcripción y TTS tienen costos por uso
- GitHub Models es gratuito para desarrollo
- Ollama puede usarse para algunos casos sin costo

### 🎛️ Límites técnicos
- Archivos de audio grandes se dividen automáticamente
- Algunos modelos tienen límites de tokens
- La calidad depende del audio de entrada

