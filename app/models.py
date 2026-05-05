from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    type: str
    message: str
    escalated: bool
    ticket_id: Optional[str] = None
    sentiment: Optional[str] = None
    confidence_score: Optional[float] = None