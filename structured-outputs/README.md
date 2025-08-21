# Structured outputs: títulos de YouTube

Este mini-demo muestra por qué los “outputs estructurados” son útiles: en lugar de extraer JSON de texto libre, pedimos al modelo que devuelva exactamente un objeto que encaja con un esquema Pydantic. Así evitamos parsers frágiles, claves que cambian y valores fuera de rango.

Caso de uso: generar varias propuestas de título para un vídeo de YouTube y luego puntuarlas para escoger la mejor. Ambos pasos usan el mismo esquema compartido.

Ahora también incluye un ejemplo paralelo “sin outputs estructurados” (solo prompt) para comparar resultados y robustez.

## Qué incluye
- Esquemas compartidos en `schema.py` (Pydantic) para títulos y evaluaciones.
- `00-generate_titles.py`: demo corto con dos modos para el mismo objetivo:
  - `--mode structured`: usa structured outputs con validación Pydantic.
  - `--mode prompt`: no usa structured outputs; forzamos JSON con instrucciones en el system prompt y luego parseamos/validamos a mano.
- `01-generate_titles.py`: versión previa básica (structured outputs).
- `score_and_select.py`: puntúa cada propuesta con criterios consistentes y selecciona la mejor, también con salida tipada.

## Requisitos
Instala las dependencias de este demo (usa tu venv si aplicas):

```bash
pip install -r structured-outputs/requirements.txt
```

Variables de entorno compatibles con el resto del repo (un solo SDK cambiando `base_url` + `api_key`):

- OpenAI directo
  - `ENDPOINT_URL=https://api.openai.com/v1`
  - `API_KEY=<tu_openai_api_key>`
- GitHub Models
  - `ENDPOINT_URL=https://models.inference.ai.azure.com`
  - `API_KEY=$GITHUB_TOKEN` o `GITHUB_MODELS_API_KEY`
- Ollama (no soporta structured outputs del Responses API a día de hoy)
  - No recomendado para este demo.

Modelo por defecto: `gpt-4o-mini` (puedes cambiar con `STRUCTURED_OUTPUTS_MODEL`).

## Uso rápido
Generar títulos (en español) para un tema (lee `YOUTUBE_TITLE` del `.env`):

```bash
python structured-outputs/00-generate_titles.py
```

- Guarda un JSON tipado bajo `structured-outputs/output/`.
- Si pasas `--score`, invoca el segundo script y muestra el ganador con su desglose.

También puedes puntuar un archivo generado anteriormente:

```bash
python structured-outputs/score_and_select.py --input structured-outputs/output/titles_productividad-con-ia.json --language es --audience "creadores en YouTube"
```

## Por qué importa
- Contratos claros: el modelo debe ceñirse al esquema (tipos, rangos, nombres de campo).
- Menos plumbing: sin regex o “best-effort” JSON parsing.
- Reutilización: el mismo esquema sirve para múltiples pasos (generar → evaluar).
- Robustez: si el modelo viola el esquema, el SDK levanta error y puedes reintentar.

## Cómo sería el system prompt sin outputs estructurados
En el modo “prompt”, no usamos `response_format=Suggestions`. En su lugar, pedimos JSON explícito y estricto en el prompt del sistema. El script ejecuta primero structured outputs y después prompt-only para que compares.

Eres un copywriter experto en títulos de YouTube orientados a SEO y CTR: creativo, claro y honesto.
Devuelve EXCLUSIVAMENTE un objeto JSON válido y nada más (sin texto adicional, sin explicaciones, sin markdown) con esta forma estricta:
{
  "suggestions": [
    { "title": "string (<= 70 chars)", "emojis": ["string", "string"], "length": 42 },
    { /* total 5 items exactos */ }
  ]
}
Reglas: exactamente 5 elementos; emojis 0-2; length coincide con el título; evita promesas excesivas.

Este enfoque puede fallar si el modelo añade texto extra o viola el esquema; el script intenta extraer el bloque JSON y validarlo con Pydantic para que veas la diferencia frente a structured outputs.

## Notas
- Usa modelos que soporten el Responses API + structured outputs (p. ej., `gpt-4o-mini`).
- El demo no sube `.env` al repositorio; sigue los patrones existentes del repo.

