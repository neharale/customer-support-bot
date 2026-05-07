from typing import Optional

from pydantic import BaseModel


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
    priority: Optional[str] = None


class TicketResponse(BaseModel):
    id: str
    user_id: str
    issue_summary: str
    sentiment: str
    status: str
    priority: Optional[str] = None

    class Config:
        from_attributes = True


class TicketStatusUpdate(BaseModel):
    status: str


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    message: str
    bot_response: str
    sentiment: str
    confidence_score: float
    escalated: bool

    class Config:
        from_attributes = True