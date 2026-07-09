from pydantic import BaseModel
from typing import Optional, Dict, Any

class AssistantQuery(BaseModel):
    text: str

class AssistantResponse(BaseModel):
    text: str
    data: Optional[Dict[Any, Any]] = None