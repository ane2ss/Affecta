from pydantic import BaseModel
from typing import List, Optional

class AffectationItem(BaseModel):
    name: str
    commune: str

class AffectationListResponse(BaseModel):
    items: List[AffectationItem]
    count: int

class GenericResponse(BaseModel):
    message: str
    success: bool
    data: Optional[dict] = None
