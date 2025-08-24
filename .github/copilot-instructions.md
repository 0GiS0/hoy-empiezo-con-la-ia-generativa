# Copilot instructions for this repo

Goal: Help AI agents make focused edits to self‑contained demos (Flask backends + lightweight vanilla JS UIs) while reusing shared patterns: unified OpenAI SDK usage, environment‑driven backend switching, streaming, and reproducible local runs.

## 1. Repository Map (mental model)
Top-level thematic folders: `text-generation/`, `prompt-engineering/`, `chat/`, `images/`, `audio/`, `rag/`, plus `frameworks/langchain/intro` side‑by‑side “sin-langchain” vs “con-langchain` examples. Each topic normally has:
- `api/` (Flask service) and `web/` (static UI). Start APIs with `python app.py`; serve UIs via local static server (`python -m http.server 5500`) or just open `index.html`.
- Env vars select provider/model instead of branching code.

## 2. Unified Model Access
Single OpenAI SDK client pattern: pass `base_url` + `api_key` dynamically.
- GitHub Models: `base_url=https://models.inference.ai.azure.com` (`GITHUB_TOKEN` / `GITHUB_MODELS_API_KEY`).
- Ollama: `base_url=${OLLAMA_URL}/v1` and dummy `api_key="ollama"`.
- OpenAI: `base_url=https://api.openai.com/v1` with `OPENAI_API_KEY`.
Backends chosen via request param `source` (e.g. chat) or query parameter (`source=github|ollama`). Never duplicate endpoint logic—only client instantiation changes.

## 3. Core Conventions
- Streaming responses: Server-Sent Events -> generator yielding chunks; always return with `content_type="text/event-stream"`.
- First message is a Spanish system prompt (see `chat/api/app.py` for canonical style); prepend programmatically, don’t rely on the client to send it.
- Token counting route uses `tiktoken` (`cl100k_base`) to keep consistency; replicate that tokenizer if adding new counting functions.
- CORS: default UI origin `http://localhost:5500`; keep consistent to avoid blocked fetches (watch for 127.0.0.1 vs localhost mismatch).
- No `.env` committed; rely on `dotenv` locally. When adding env usage, document variable name in the folder README.

## 4. Chat Pattern (YouTube assistant)
- Endpoint: `POST /chat` returns SSE stream of model output. Input body: `{ messages: [...], source: 'github'|'ollama' }`.
- Implementation reference: `chat/api/app.py` (dynamic client + model mapping). Frontend stream consumption logic: `chat/web/ui.js`.
- Add new chat-like demos by cloning this shape; only adjust system prompt + model selection.

## 5. Text Generation & Prompt Engineering
- `text-generation/api/app.py`: GET `/generate` (SSE) and POST `/count_tokens` (JSON). Accepts `source` + optional `model` override.
- `prompt-engineering/api/`: structured into blueprints (`routes/`) and service layer (`services/`). Follow existing separation: routes parse/validate, services call SDK. Add new functionality by extending services; keep streaming logic at route boundary.
- Judge / evaluation prompts live under `prompt-engineering/llm-as-a-judge/` — keep them declarative (`*.prompty`).

## 6. Images & Vision
- Distinct APIs: `images/generation/images-api/` (direct `client.images.generate`) vs `images/generation/responses-api/` (multi-turn via `client.responses.create` + `tools=[{"type":"image_generation"}]`). Do NOT mix models across these.
- Vision examples under `images/vision/*` show chat completion with image inputs; reuse that for multimodal additions.

## 7. Audio
- Basic STT: `audio/basico/speech-to-text/app.py` using Whisper (`audio.transcriptions.create`).
- Advanced voice conversation: `audio/avanzado/chat-completions/api/app.py` uses `modalities=["text","audio"]` and returns wav bytes. Ensure FFmpeg installed if you modify input format handling.

## 8. RAG Pipeline
Order (all in `rag/`): `1.convert_urls.py` (HTML→MD via MarkItDown) → `2.convert_markdown*.py` (chunking or not) → `3.store_embeddings.py` (Qdrant upsert) → `4.query_embeddings_and_generate_response.py` (retrieve + generate). Keep filenames numeric for execution order clarity. Env for embeddings vs generation models are distinct; preserve both when refactoring.
Qdrant UI: `http://localhost:6333/dashboard` for inspection. Some scripts assume absolute paths inside devcontainer; if generalizing, parameterize path roots.

## 9. LangChain Intro Section
`frameworks/langchain/intro/01-sin-langchain/` vs `02-con-langchain/` show raw SDK vs LangChain abstractions. Avoid adding shared logic inside these folders—place reusable classes in `frameworks/langchain/common/` (or `../common` if still housed there) to keep contrast clear.

## 10. Logging & Rich Output
Recent examples add colored emoji logging via `rich.console.Console`. Follow style: concise emoji prefix + color-coded status (e.g. retrieval, model call, persist). Do not introduce heavy wrappers—inline `console.print` calls suffice.

## 11. Adding a New Demo (Checklist)
1. Copy closest existing `api/` + `web/` pair.
2. Introduce env vars (document in that folder’s README) rather than hard-coding values.
3. Implement streaming if multi-token output expected (chat, generation); reuse SSE pattern.
4. Prepend system prompt; keep it Spanish + domain-specific.
5. Support `source` switch if relevant (GitHub/Ollama) via unified client creation.
6. Test locally: run API, open `web/index.html`, verify CORS + streaming.

## 12. Common Pitfalls
- CORS origin mismatch (most frequent breakage) → ensure `localhost:5500` exactly.
- Mixing image models between `images-api` and `responses-api` → leads to API errors.
- Forgetting dummy `api_key` for Ollama → SDK instantiation fails.
- Not prepending system message → model outputs drift from intended constraints.
- Hard-coded absolute devcontainer paths limit portability—parameterize with env.

## 13. Minimal Run Examples
- Chat API: `python chat/api/app.py` (port 5000) then open `chat/web/index.html` via static server (or VS Code live server). 
- Text generation: `python text-generation/api/app.py` and hit `/generate?source=github&title=Demo`.
- RAG step: run scripts in numeric order after setting required Qdrant + model env vars.

## 14. Style & Review Guidance
- Keep demos lean: prefer explicit small functions over abstraction unless reused ≥2 places.
- When editing prompts, keep them concise, Spanish, and domain-relevant. Avoid mixing languages within one system prompt.
- Do not introduce global state beyond simple module-level clients or caches.

## 15. Security & Secrets
Never commit `.env` contents. Reference only variable names. Assume tokens loaded with `dotenv` at runtime. Avoid printing full keys (log only that they are set).

---
If anything here seems stale while editing, update the corresponding section succinctly. Ask for clarification if a new pattern emerges not covered above.
