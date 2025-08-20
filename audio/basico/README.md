# 🎧 Audio · Básico (Parte 1)

Este directorio reúne las demos de audio de nivel básico: transcripción (STT), traducción/posprocesado de subtítulos y síntesis de voz (TTS). Los detalles completos están en cada subcarpeta.

## 🎬 Vídeo de la Parte 1 (Cap.7)

[![IA para Audio desde Cero: Transcribe, Traduce y Genera Voz 🗣️✨ | Cap.7](https://img.youtube.com/vi/PdSytr086i4/maxresdefault.jpg)](https://youtu.be/PdSytr086i4 "Abrir en YouTube")

## 📁 Carpetas

- `speech-to-text/` — Transcribe MP4/MP3 a SRT o JSON usando Whisper. Divide automáticamente archivos grandes y genera `media/transcripcion.srt`.
- `transcription/` — Traduce o posprocesa el SRT generado (por defecto al inglés) dividiéndolo en trozos por tokens.
- `chat-completions-api/` — Texto → Audio (TTS) con una API Flask y una pequeña UI web.

Consulta los READMEs dentro de cada carpeta para instrucciones detalladas:

- `speech-to-text/README.md`
- `transcription/README.md`
- `chat-completions-api/README.md`

## 🚀 Inicio rápido por demo

### 1) Speech-to-Text
Ubicación: `audio/basico/speech-to-text`

Requisitos del sistema (FFmpeg):
- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`

Pasos típicos:
```bash
cd audio/basico/speech-to-text
cp .env-sample .env   # Configura ENDPOINT_URL y API_KEY
pip install -r requirements.txt
python app.py
```
Salida: `media/transcripcion.srt` (o `.json` si lo configuras).

---

### 2) Transcription (traducción/posprocesado SRT)
Ubicación: `audio/basico/transcription`

Descripción: Lee `../speech-to-text/media/transcripcion.srt`, divide por tokens y traduce (por defecto a inglés) usando Chat Completions.

Pasos típicos (consulta también su README):
```bash
cd audio/basico/transcription
cp .env-sample .env   # Configura ENDPOINT_URL y API_KEY
pip install openai tiktoken python-dotenv rich
python app.py
```

---

### 3) Chat Completions API (TTS)
Ubicación: `audio/basico/chat-completions-api`

Descripción: Convierte texto a audio WAV con voces TTS. Incluye API Flask y UI web.

Pasos típicos:
```bash
cd audio/basico/chat-completions-api/api
cp .env-sample .env   # Configura ENDPOINT_URL y API_KEY (OpenAI / GitHub Models / Azure)
pip install -r requirements.txt
python app.py
```
Acceso:
- UI y API: http://localhost:5001
- Endpoint: `POST /generate-audio` (JSON: `{ "message", "voice" }`)

## 🔐 Variables de entorno

Para las demos que usan endpoints compatibles con el SDK OpenAI:

- `ENDPOINT_URL` y `API_KEY`
  - Ejemplos:
    - OpenAI: `ENDPOINT_URL=https://api.openai.com/v1`
    - GitHub Models (desarrollo): `ENDPOINT_URL=https://models.inference.ai.azure.com`

No subas tus `.env` al repo.

## 🧪 Puertos y endpoints

- TTS (chat-completions-api): http://localhost:5001 → `POST /generate-audio`

## 🛠️ Notas

- Genera primero `speech-to-text` para producir `transcripcion.srt` antes de usar `transcription`.
- La calidad de la transcripción depende del audio de entrada.
- Algunos modelos/vozes pueden requerir acceso según el proveedor.
