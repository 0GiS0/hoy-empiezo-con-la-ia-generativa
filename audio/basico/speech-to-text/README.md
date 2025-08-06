# 🗣️ Speech to text: transcribe audio with AI

¡Hola developer 👋🏻! Aquí tienes una demo para convertir audio de vídeo en texto usando IA, con explicaciones en español.

## 🎯 Objetivo

Esto es muy útil cuando el objetivo es generar subtítulos para un vídeo, transcribir reuniones o procesar información de audio. 

## 📂 Estructura del directorio
```audio/basico/speech-to-text/
├── 📄 README.md           # Esta guía
├── 📋 requirements.txt    # Dependencias principales
├── 📝 app.py              # Script principal (todo el flujo está aquí)
├── 🎥 media/              # Carpeta donde debes poner tu vídeo .mp4
```

## 📦 Instalación de dependencias

Ejecuta este comando en la terminal dentro de este directorio para instalar todo lo necesario:

```zsh
cd audio/basico/speech-to-text
pip install -r requirements.txt
```

## 🎥 Prepara tu vídeo

Coloca un archivo `.mp4` en la carpeta `media/`. El script buscará automáticamente el primer vídeo que encuentre para extraer y transcribir el audio.

## ⚙️ Configura tu API Key

Crea un archivo `.env` en este directorio con el siguiente contenido (rellena tus datos):

```env
ENDPOINT_URL=<URL de la API de OpenAI>
API_KEY=<tu clave de API>
```

## 🚀 Ejecuta el script

Cuando tengas el vídeo listo, ejecuta:

```zsh
python app.py
```

## 🔎 ¿Qué hace el script?

- Busca el vídeo en `media/`.
- Extrae el audio y lo guarda como MP3.
- Si el audio es muy grande, lo divide en trozos.
- Transcribe cada trozo (o el audio completo) usando la API de OpenAI Whisper.
- Guarda la transcripción en formato SRT o JSON.

Las funciones principales están en inglés (`find_video`, `extract_audio`, `split_audio`, `save_transcription`, etc.), pero los comentarios y mensajes te explican todo en español y con emojis para que sea más fácil de seguir.

---
✨ ¡Explora, prueba y aprende cómo la IA puede convertir voz en texto! ✨