import uuid

from fastapi import APIRouter, HTTPException

from app.database import SessionLocal
from app.db_models import Conversation, Ticket
from app.models import ChatRequest, ChatResponse
from app.services.escalation_service import EscalationService
from app.services.llm_service import LLMService
from app.services.sentiment_service import SentimentService

router = APIRouter()

llm_service = LLMService()
sentiment_service = SentimentService()
escalation_service = EscalationService()


def get_recent_conversations(db, user_id: str, limit: int = 5):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.id.desc())
        .limit(limit)
        .all()
    )


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    db = SessionLocal()

    try:
        recent_convs = get_recent_conversations(
            db=db,
            user_id=request.user_id,
            limit=5
        )

        history = []
        for conv in reversed(recent_convs):
            history.append(f"User: {conv.message}")
            history.append(f"Bot: {conv.bot_response}")

        sentiment = sentiment_service.analyze(request.message)

        bot_response, confidence_score = llm_service.generate_response(
            user_message=request.message,
            history=history
        )

        should_escalate = escalation_service.should_escalate(
            message=request.message,
            sentiment=sentiment,
            confidence_score=confidence_score
        )

        ticket_id = None

        if should_escalate:
            ticket_id = f"ticket_{uuid.uuid4().hex[:8]}"

            ticket = Ticket(
                id=ticket_id,
                user_id=request.user_id,
                issue_summary=request.message,
                sentiment=sentiment,
                status="OPEN",
                priority="HIGH" if sentiment == "negative" else "MEDIUM"
            )

            db.add(ticket)

        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            message=request.message,
            bot_response=bot_response,
            sentiment=sentiment,
            confidence_score=confidence_score,
            escalated=should_escalate
        )

        db.add(conversation)
        db.commit()

        if should_escalate:
            return ChatResponse(
                type="escalation",
                message="I’m sorry you’re dealing with this. I’m escalating this to a human support agent.",
                escalated=True,
                ticket_id=ticket_id,
                sentiment=sentiment,
                confidence_score=confidence_score
            )

        return ChatResponse(
            type="bot_response",
            message=bot_response,
            escalated=False,
            ticket_id=None,
            sentiment=sentiment,
            confidence_score=confidence_score
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()