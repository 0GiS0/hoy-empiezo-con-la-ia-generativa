from typing import List
from pydantic import BaseModel, Field


class Suggestion(BaseModel):
    title: str = Field(...,
                       description="Título sugerido con emojis incluidos", max_length=70)
    emojis: list[str] = Field(...,
                              description="Emojis sugeridos", max_length=2)
    length: int = Field(..., description="Longitud del título sugerido")


class Suggestions(BaseModel):
    suggestions: List[Suggestion] = Field(
        ..., min_items=5, max_items=5, description="Exactamente 5 títulos sugeridos"
    )
