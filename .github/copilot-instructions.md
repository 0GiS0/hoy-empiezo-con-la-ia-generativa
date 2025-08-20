# Copilot instructions for this repo

Goal: make focused edits to each demo using the repo’s common patterns (Flask APIs + vanilla web UIs) and switch models via environment variables.

## Big picture
- Topics as folders: `text-generation/`, `prompt-engineering/`, `chat/`, `images/`, `audio/`, `rag/`.
- Each topic has: Flask API in `*/api/` and a simple UI in `*/web/` (served via a static server).
- One OpenAI SDK for all backends by changing `base_url` + `api_key`:
  - GitHub Models: `base_url=https://models.inference.ai.azure.com` with token (`GITHUB_TOKEN` or `GITHUB_MODELS_API_KEY`).
  - Ollama: `base_url=${OLLAMA_URL}/v1`, `api_key="ollama"`.
  - OpenAI: `base_url=https://api.openai.com/v1`, `OPENAI_API_KEY`.

## Conventions and patterns
- Streaming: use SSE with a generator, e.g. `return Response(generate_stream(), content_type="text/event-stream")`.
- System prompts first: prepend a system message (Spanish domain prompts in `chat/api/app.py`).
- Source switching: APIs accept `source: 'github'|'ollama'` to select backend; pick model per source.
- Token counting: `tiktoken` using `cl100k_base`.
- CORS: UIs usually run at `http://localhost:5500`; align CORS per app. Don’t commit `.env`.

## Chat (YouTube assistant)
- Endpoint: `POST /chat` with `{ messages, source }` → SSE text stream; see `chat/api/app.py` and `chat/web/ui.js`.
- Env in `chat/api/config.py`: `GITHUB_MODELS_API_URL`, `GITHUB_MODELS_MODEL`, `GITHUB_MODELS_API_KEY`, `OLLAMA_API_URL`, `OLLAMA_MODEL`.
- UI toggles GitHub/Ollama and fetches `http://127.0.0.1:5000/chat`.

## Text generation + Prompt Engineering
- `text-generation/api/app.py`: `GET /generate?source=&model=&title=` → SSE; `POST /count_tokens` → JSON with tokens.
- Env: `GITHUB_MODELS_URL`, `GITHUB_TOKEN`, `OLLAMA_URL`.
- `prompt-engineering/api`: Flask app with blueprints (`routes/generate.py`, `routes/tokens.py`) and services (`services/*`). CORS origins set in `config.py`.

## Images
- One-shot generation: `client.images.generate(...)` in `images/generation/images-api/app.py`.
- Conversational/multi-turn and partials: `client.responses.create(..., tools=[{"type":"image_generation"}], stream=True)` in `images/generation/responses-api/app.py`.
- Models are endpoint-specific: e.g., `gpt-image-1` only for Images API; `gpt-4o*` via Responses. Don’t mix them.
- Env: `ENDPOINT_URL`, `API_KEY`, `IMAGE_GENERATION_MODEL`. Some scripts write under `/workspaces/...`; adjust paths locally if needed.

## Audio
- Advanced voice chat: `audio/avanzado/chat-completions/api/app.py` exposes `POST /conversation` accepting multipart `audio`, returning `audio/wav`. Uses Chat Completions with `modalities=["text","audio"]` and `voice:"nova"`.
- Requires `OPENAI_API_KEY` and `MODEL_FOR_AUDIO`. Non-wav/mp3 inputs are converted with `pydub`/FFmpeg—install FFmpeg or send wav/mp3.
- Basic STT: `audio/basico/speech-to-text/app.py` transcribes media via Whisper (`audio.transcriptions.create(model="whisper-1")`) with `ENDPOINT_URL` + `API_KEY`.

## RAG
- Pipeline in `rag/`: `1.convert_urls.py` (MarkItDown) → `2.convert_markdown.py`/`2.convert_markdown_sin_chunks.py` → `3.store_embeddings.py` (Qdrant) → `4.query_embeddings_and_generate_response.py`.
- Env: `GITHUB_MODELS_URL`, `GITHUB_TOKEN`, `GITHUB_MODELS_MODEL_FOR_EMBEDDINGS`, `GITHUB_MODELS_MODEL_FOR_GENERATION`, `QDRANT_URL`, `QDRANT_COLLECTION_NAME`.
- Qdrant UI: http://localhost:6333/dashboard. Some scripts use absolute `/workspaces/...` paths—update if running outside a devcontainer.

## Workflows
- Install deps per demo: `pip install -r requirements.txt` (under the topic or API folder).
- Run APIs: `python app.py` in each `*/api/` (default `0.0.0.0:5000`) or `FLASK_DEBUG=1 flask run --host=0.0.0.0 --port=5000` when provided.
- Serve UIs: open `*/web/index.html` or run `python -m http.server 5500` from the `web` folder.

Gotchas
- CORS/Origin mismatches (127.0.0.1 vs localhost:5500) will block the UI; align the allowed origins.
- Don’t mix image models across endpoints (`responses` vs `images`).
- For Ollama, always set `api_key="ollama"` even though it’s not used server-side.
