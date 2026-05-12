from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import func

from app.database import SessionLocal
from app.db_models import Conversation, Ticket
from app.models import (
    TicketResponse,
    TicketStatusUpdate,
    ConversationResponse,
    AnalyticsResponse,
)
from app.services.auth_service import get_current_admin

router = APIRouter()


@router.get("/tickets", response_model=list[TicketResponse])
def get_tickets(
    priority: str | None = Query(default=None),
    status: str | None = Query(default=None),
    user_id: str | None = Query(default=None),
    current_admin: dict = Depends(get_current_admin),
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
def get_ticket(
    ticket_id: str,
    current_admin: dict = Depends(get_current_admin),
):
    db = SessionLocal()

    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        return ticket

    finally:
        db.close()


@router.patch("/tickets/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: str,
    update: TicketStatusUpdate,
    current_admin: dict = Depends(get_current_admin),
):
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
def get_conversations(
    user_id: str,
    current_admin: dict = Depends(get_current_admin),
):
    db = SessionLocal()

    try:
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .all()
        )

    finally:
        db.close()


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(
    current_admin: dict = Depends(get_current_admin),
):
    db = SessionLocal()

    try:
        total_tickets = db.query(Ticket).count()
        open_tickets = db.query(Ticket).filter(Ticket.status == "OPEN").count()
        in_progress_tickets = (
            db.query(Ticket)
            .filter(Ticket.status == "IN_PROGRESS")
            .count()
        )
        closed_tickets = db.query(Ticket).filter(Ticket.status == "CLOSED").count()

        p0_tickets = db.query(Ticket).filter(Ticket.priority == "P0").count()
        p1_tickets = db.query(Ticket).filter(Ticket.priority == "P1").count()
        p2_tickets = db.query(Ticket).filter(Ticket.priority == "P2").count()

        total_conversations = db.query(Conversation).count()
        escalated_conversations = (
            db.query(Conversation)
            .filter(Conversation.escalated == True)
            .count()
        )

        escalation_rate = (
            round((escalated_conversations / total_conversations) * 100, 2)
            if total_conversations > 0
            else 0.0
        )

        avg_confidence = db.query(func.avg(Conversation.confidence_score)).scalar()

        return AnalyticsResponse(
            total_tickets=total_tickets,
            open_tickets=open_tickets,
            in_progress_tickets=in_progress_tickets,
            closed_tickets=closed_tickets,
            p0_tickets=p0_tickets,
            p1_tickets=p1_tickets,
            p2_tickets=p2_tickets,
            total_conversations=total_conversations,
            escalated_conversations=escalated_conversations,
            escalation_rate=escalation_rate,
            average_confidence_score=round(avg_confidence or 0.0, 2),
        )

    finally:
        db.close()