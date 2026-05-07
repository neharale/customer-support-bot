from fastapi import APIRouter, HTTPException, Query

from app.database import SessionLocal
from app.db_models import Conversation, Ticket
from app.models import TicketResponse, TicketStatusUpdate, ConversationResponse

router = APIRouter()


@router.get("/tickets", response_model=list[TicketResponse])
def get_tickets(
    priority: str | None = Query(default=None),
    status: str | None = Query(default=None),
    user_id: str | None = Query(default=None)
):
    db = SessionLocal()

    try:
        query = db.query(Ticket)

        if priority and priority.strip():
            query = query.filter(Ticket.priority == priority.strip())

        if status and status.strip():
            query = query.filter(Ticket.status == status.strip())

        if user_id and user_id.strip():
            search_user = f"%{user_id.strip()}%"
            query = query.filter(Ticket.user_id.like(search_user))

        return query.all()

    finally:
        db.close()


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str):
    db = SessionLocal()

    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        return ticket

    finally:
        db.close()


@router.patch("/tickets/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(ticket_id: str, update: TicketStatusUpdate):
    db = SessionLocal()

    try:
        allowed_statuses = {"OPEN", "IN_PROGRESS", "CLOSED"}

        if update.status not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail="Invalid status. Use OPEN, IN_PROGRESS, or CLOSED."
            )

        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        ticket.status = update.status
        db.commit()
        db.refresh(ticket)

        return ticket

    finally:
        db.close()


@router.get("/conversations/{user_id}", response_model=list[ConversationResponse])
def get_conversations(user_id: str):
    db = SessionLocal()

    try:
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .all()
        )

    finally:
        db.close()