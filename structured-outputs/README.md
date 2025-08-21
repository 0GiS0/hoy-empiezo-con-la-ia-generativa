# Cap. 9 — Structured outputs: títulos de YouTube

> Video: Próximamente · Código en esta carpeta

Este mini-demo muestra por qué los “outputs estructurados” son útiles: en lugar de extraer JSON de texto libre, pedimos al modelo que devuelva exactamente un objeto que encaja con un esquema Pydantic. Así evitamos parsers frágiles, claves que cambian y valores fuera de rango.

Caso de uso: generar varias propuestas de título para un vídeo de YouTube y luego puntuarlas para escoger la mejor. Ambos pasos usan el mismo esquema compartido.

Incluimos dos enfoques para comparar robustez y DX:
- 00: sin outputs estructurados (prompt → parseo manual → validación con Pydantic)
- 01: con outputs estructurados (el SDK valida contra el esquema Pydantic)

## Qué incluye
- Esquemas compartidos en `schema.py` (Pydantic) para títulos y evaluaciones.
- `00-generate_titles.py`: genera sugerencias sin structured outputs. Pide al modelo un JSON vía prompt, extrae el bloque con regex y lo valida contra `Suggestions`.
- `01-generate_titles.py`: usa structured outputs (parse) para que el SDK devuelva `Suggestions` ya tipado y validado.
- `score_and_select.py`: puntúa/selecciona la mejor propuesta dado un listado de `Suggestion`.

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
- Ollama: este ejemplo usa Chat Completions con `parse`, que puede no estar disponible en todos los backends. No recomendado para este demo.

Modelo por defecto: `gpt-4o-mini` (puedes cambiar con `STRUCTURED_OUTPUTS_MODEL`).

## Paso a paso

1) Sin outputs estructurados (prompt → parseo → validación)
- Script: `00-generate_titles.py`
- Qué hace: envía un prompt que “fuerza” JSON, imprime el texto del modelo, extrae el bloque `{ ... }` con regex y valida con `Suggestions.model_validate_json(...)`.
- Ejecuta:

```bash
python structured-outputs/00-generate_titles.py
```

- Salida esperada en consola: el texto crudo del modelo, el “JSON extraído” y el objeto validado `Suggestions`.
- Riesgos: si el modelo añade texto extra o incumple el formato, el parseo/validación puede fallar.

2) Con outputs estructurados (validación automática con Pydantic)
- Script: `01-generate_titles.py`
- Qué hace: usa `client.chat.completions.parse(..., response_format=Suggestions)` para recibir un objeto ya tipado; imprime y usa las sugerencias para elegir la mejor con `best_suggestion`.
- Ejecuta:

```bash
python structured-outputs/01-generate_titles.py
```

- Salida esperada en consola: respuesta parseada (`parsed.suggestions`) y “la mejor sugerencia”.

3) Seleccionar la mejor sugerencia desde un listado
- Función: `score_and_select.best_suggestion(suggestions)`
- Se usa dentro de `01-generate_titles.py` (y puede usarse aparte si lo necesitas).

## Por qué importa
- Contratos claros: el modelo debe ceñirse al esquema (tipos, rangos, nombres de campo).
- Menos plumbing: sin regex o “best-effort” JSON parsing.
- Reutilización: el mismo esquema sirve para múltiples pasos (generar → evaluar).
- Robustez: si el modelo viola el esquema, el SDK levanta error y puedes reintentar.

## Cómo sería el system prompt sin outputs estructurados (referencia)
En el enfoque 00 no usamos `response_format=Suggestions`. En su lugar, pedimos JSON explícito y estricto en el prompt del sistema, el modelo responde con texto y extraemos el bloque JSON. Este método es frágil: cualquier texto extra o clave fuera de esquema rompe el parseo/validación.

## Notas
- Usa modelos que soporten Chat Completions con `parse` (p. ej., `gpt-4o-mini`).
- El demo no sube `.env` al repositorio; sigue los patrones existentes del repo.

