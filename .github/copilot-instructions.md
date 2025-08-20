# Copilot instructions for this repo

Goal: make productive edits in this multi-demo Generative AI repo by reusing existing patterns and keeping changes scoped to each chapter.

## Big picture
- Topics as folders: `text-generation/`, `prompt-engineering/`, `chat/`, `images/`, `audio/`, `rag/`.
- Structure: Flask API in `*/api/` + vanilla web UI in `*/web/`.
- Model access via OpenAI SDK with pluggable backends (set base_url + API key):
  - GitHub Models: https://models.inference.ai.azure.com with a GitHub token.
  - Ollama: `${OLLAMA_URL}/v1`, api_key "ollama".
  - OpenAI: https://api.openai.com/v1 with `OPENAI_API_KEY`.

## Conventions
- Stream chat via SSE: `Response(gen(), content_type="text/event-stream")` (see `chat/api/app.py`).
- Prepend a system message to chat `messages`.
- Env-driven source/model; keep module-specific names:
  - Chat config keys: `GITHUB_MODELS_API_URL`, `GITHUB_MODELS_MODEL`, `GITHUB_MODELS_API_KEY`, `OLLAMA_API_URL`, `OLLAMA_MODEL`.
  - Text generation: `GITHUB_MODELS_URL`, `GITHUB_TOKEN`, `OLLAMA_URL`.
  - Images: `ENDPOINT_URL`, `API_KEY`, `IMAGE_GENERATION_MODEL`.
- CORS: match UIs (commonly `http://localhost:5500`). Don’t commit `.env`.

## Images
- One-shot: `client.images.generate(...)` (`images/generation/images-api/app.py`).
- Multi-turn/partials: `client.responses.create(..., tools=[{"type":"image_generation"}], stream=True)` (`images/generation/responses-api/app.py`).
- Don’t mix models across endpoints (e.g., `gpt-image-1` is Images-only).

## Audio
- STT: Whisper `audio.transcriptions.create(model="whisper-1")`.
- TTS-in-chat: `chat.completions.create(modalities=["text","audio"], audio={voice:"nova", format:"wav"})`.
- `POST /conversation` expects multipart `audio`, returns `audio/wav` (`audio/avanzado/chat-completions/api/app.py`).

## RAG
- Pipeline (in `rag/`): `1.convert_urls.py` → `2.convert_markdown.py` → `3.store_embeddings.py` → `4.query_embeddings_and_generate_response.py`.
- Qdrant UI: http://localhost:6333/dashboard. Uses MarkItDown.

## Workflows
- Install: `pip install -r requirements.txt` (root or per-demo).
- Run APIs: `python app.py` in each `*/api/` (binds to `0.0.0.0:5000`).
- Serve UIs: open `*/web/index.html` or `python -m http.server 5500`.

Questions for maintainers: standardize env var names? preferred ports/CORS? any repo-wide lint/test rules?
