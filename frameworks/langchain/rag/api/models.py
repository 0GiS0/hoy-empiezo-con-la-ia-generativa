from typing import Literal
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    action: Literal["retrieve", "direct"] = Field(
        ..., description="retrieve if external knowledge is needed; otherwise direct"
    )
    rationale: str = Field(..., description="explanation of the decision")
