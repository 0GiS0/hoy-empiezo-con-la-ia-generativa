from typing import Literal
from langchain_core.pydantic_v1 import BaseModel
from pydantic import Field


class RouteDecision(BaseModel):
    action: Literal["retrieve", "direct"] = Field(
        ..., description="retrieve if external knowledge is needed; otherwise direct"
    )
    rationale: str = Field(..., description="explanation of the decision")
