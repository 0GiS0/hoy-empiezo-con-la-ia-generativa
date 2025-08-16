# 🔊 Capítulo 7: Audio y la IA Generativa 🎵🤖

¡Hola developer 👋🏻! En este directorio encontrarás las demos que te mostré en mis vídeos sobre audio e IA Generativa.

## 📁 Estructura real del directorio

```
audio/
├─ README.md
├─ basico/
│  ├─ speech-to-text/           # Transcribe MP4 → SRT/JSON (Whisper)
│  ├─ transcription/            # Traduce/posprocesa subtítulos SRT
│  └─ chat-completions-api/     # Texto → audio (TTS) vía API + UI
└─ avanzado/
	 ├─ chat-completions/         # Conversación por voz (transcribe → responde en audio)
	 └─ realtime-api/             # Realtime API (ephemeral key + Web UI)
```

## 🚀 Demos y cómo ejecutarlas

## Básico

Las demos del directorio `audio/basico` se centran en tareas de audio comunes, como la transcripción y la síntesis de voz. Puedes verlas en acción en mi vídeo 

[![🎧 IA para Audio desde Cero: Transcribe, Traduce y Genera Voz 🗣️✨ | Cap.7](https://img.youtube.com/vi/PdSytr086i4/maxresdefault.jpg)](https://youtu.be/PdSytr086i4 "Abrir en YouTube")

### 1) 🎤 Speech-to-Text (MP4 → SRT/JSON)
Ubicación: `audio/basico/speech-to-text`

Qué hace:
- Busca un `.mp4` en `media/`, extrae audio, divide si es grande (> ~25MB), transcribe con Whisper y guarda `transcripcion.srt` (o JSON).

Requisitos de sistema (FFmpeg):
```zsh
brew install ffmpeg   # macOS
```

Instalación y uso:
```zsh
cd audio/basico/speech-to-text
cp .env-sample .env   # Configura ENDPOINT_URL y API_KEY
pip install -r requirements.txt
python app.py
```

Salida:
- `media/transcripcion.srt` (o `.json` si cambias FORMAT en el script).

---

### 2) 📝 Transcription (traducción/posprocesado de SRT)
Ubicación: `audio/basico/transcription`

Qué hace:
- Lee `speech-to-text/media/transcripcion.srt`, divide por tokens y traduce (por defecto a inglés) usando Chat Completions.

Instalación y uso:
```zsh
cd audio/basico/transcription
cp .env-sample .env   # Configura ENDPOINT_URL y API_KEY
pip install openai tiktoken python-dotenv rich
python app.py
```

Notas:
- Asegúrate de haber generado primero `transcripcion.srt` en la demo de Speech-to-Text.

---

### 3) � Chat Completions API (Texto → Audio, demo TTS con UI)
Ubicación: `audio/basico/chat-completions-api`

Qué hace:
- Convierte texto a audio WAV con voces TTS de OpenAI. Incluye UI web para introducir texto y elegir voz.

Instalación y uso:
```zsh
cd audio/basico/chat-completions-api/api
cp .env-sample .env   # Usa ENDPOINT_URL y API_KEY (OpenAI/GitHub Models/Azure)
pip install -r requirements.txt
python app.py
```

Acceso:
- UI y API servidas por Flask: http://localhost:5001
- Endpoint: `POST /generate-audio` (JSON: `{ "message", "voice" }`).

---

### 4) 🗣️ Chat Completions (Conversación por voz)
Ubicación: `audio/avanzado/chat-completions`

Qué hace:
- Front graba tu voz → backend transcribe con Whisper → Chat genera respuesta y la devuelve en audio WAV (voz “nova”).

Instalación y uso:
```zsh
cd audio/avanzado/chat-completions/api
cp .env.example .env   # Requiere OPENAI_API_KEY; opcionales MODEL_FOR_AUDIO, TRANSCRIBE_MODEL
pip install -r requirements.txt
python app.py
```

Acceso:
- UI y API: http://localhost:5000
- Endpoint principal: `POST /conversation` (multipart con campo `audio`).

---

### 5) ⚡ Realtime API (WebRTC con ephemeral keys)
Ubicación: `audio/avanzado/realtime-api`

Qué hace:
- Servidor Flask que genera ephemeral keys; el cliente web se conecta directamente a OpenAI Realtime API para conversación de baja latencia.

Instalación y uso:
```zsh
cd audio/avanzado/realtime-api/api
cp .env.example .env   # Requiere OPENAI_API_KEY; opcionales HOST, PORT, DEBUG
pip install -r requirements.txt
python server.py
```

Acceso:
- UI y API: http://localhost:8000
- Endpoints útiles: `POST /api/token`, `GET /api/session/config`.

## 🔐 Variables de entorno por demo

- Clientes configurables por endpoint (OpenAI / GitHub Models / Azure):
	- `ENDPOINT_URL` y `API_KEY`
	- Ejemplos:
		```env
		# OpenAI
		ENDPOINT_URL=https://api.openai.com/v1
		API_KEY=tu_api_key_openai

		# GitHub Models (desarrollo)
		ENDPOINT_URL=https://models.inference.ai.azure.com
		API_KEY=tu_github_token
		```

- Conversación por voz (avanzado/chat-completions):
	- `OPENAI_API_KEY` (obligatoria)
	- `MODEL_FOR_AUDIO` (ej. gpt-4o-audio-preview) y `TRANSCRIBE_MODEL` (por defecto `whisper-1`).

- Realtime API:
	- `OPENAI_API_KEY` (obligatoria)
	- `HOST`, `PORT`, `DEBUG` (opcionales; por defecto 0.0.0.0:8000 y debug=false).

Sugerencia: copia los `.env-sample`/`.env.example` de cada carpeta a `.env` y completa tus claves.

## 🧰 Dependencias del sistema

- FFmpeg (necesario para Speech-to-Text):
	- macOS: `brew install ffmpeg`
	- Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`
	- Windows: https://ffmpeg.org/download.html

## 🧪 Puertos y endpoints

- Texto→Audio (básico): http://localhost:5001 → `POST /generate-audio`
- Conversación por voz (avanzado): http://localhost:5000 → `POST /conversation`
- Realtime API: http://localhost:8000 → `POST /api/token`, `GET /api/session/config`

## � Notas y troubleshooting

- No subas tus `.env` al repo.
- Algunos modelos de audio pueden requerir acceso (p. ej., `gpt-4o-audio-preview`).
- Si recibes “OPENAI_API_KEY no configurada”, revisa el `.env` correcto según la demo.
- “No se encontró archivo de audio” al llamar `/conversation`: envía el campo `audio` en multipart/form-data.
- CORS: las APIs sirven su propia UI. Si sirves la web en otro puerto, ajusta orígenes permitidos.

### 💰 Costos
- Los modelos de transcripción y TTS tienen costos por uso
- GitHub Models es gratuito para desarrollo
- Ollama puede usarse para algunos casos sin costo

### 🎛️ Límites técnicos
- Archivos de audio grandes se dividen automáticamente
- Algunos modelos tienen límites de tokens
- La calidad depende del audio de entrada

