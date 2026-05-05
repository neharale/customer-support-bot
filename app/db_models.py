from sqlalchemy import Column, String, Boolean, Float
from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String)
    message = Column(String)
    bot_response = Column(String)
    sentiment = Column(String)
    confidence_score = Column(Float)
    escalated = Column(Boolean)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String)
    issue_summary = Column(String)
    sentiment = Column(String)
    status = Column(String)
    priority = Column(String)