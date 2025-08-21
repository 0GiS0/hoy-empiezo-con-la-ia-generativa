from typing import List
from pydantic import BaseModel, Field

class Suggestion(BaseModel):
    title: str = Field(
        ..., max_length=70,
        description="Título en español optimizado para SEO y CTR, emojis incluidos"
    )
    length: int = Field(...)
    emojis: List[str] = Field(
        ..., max_length=2,
        description="Lista de emojis relevantes para el título"
    )

    # La validación estricta de length se hace en los scripts para mostrar diferencias entre enfoques

class Suggestions(BaseModel):
    suggestions: List[Suggestion] = Field(
        ..., min_items=5, max_items=5, description="Exactamente 5 títulos sugeridos"
    )
