import uuid


class EscalationService:
    def should_escalate(
        self,
        message: str,
        sentiment: str,
        confidence_score: float,
        failed_attempts: int = 0
    ) -> bool:
        message_lower = message.lower()

        escalation_keywords = [
            "human",
            "agent",
            "manager",
            "charged twice",
            "double charged",
            "fraud",
            "lawsuit",
            "cancel my account",
            "complaint",
            "angry",
            "not helping",
            "delete my account",
            "cannot access my email",
            "can't access my email",
            "cant access my email",
            "lost package",
            "order not delivered",
            "delivery missing"
        ]

        shipping_escalation = (
            ("package" in message_lower or "order" in message_lower)
            and (
                "hasn't arrived" in message_lower
                or "has not arrived" in message_lower
                or "not arrived" in message_lower
                or "missing" in message_lower
                or "not delivered" in message_lower
            )
        )

        tracking_escalation = (
            "tracking" in message_lower
            and (
                "not updating" in message_lower
                or "not updated" in message_lower
                or "has not updated" in message_lower
                or "hasn't updated" in message_lower
                or "no update" in message_lower
            )
        )

        if any(keyword in message_lower for keyword in escalation_keywords):
            return True

        if shipping_escalation:
            return True

        if tracking_escalation:
            return True

        if sentiment == "negative":
            return True

        if confidence_score < 0.60:
            return True

        if failed_attempts >= 2:
            return True

        return False

    def create_ticket(self, user_id: str, message: str, sentiment: str) -> dict:
        return {
            "ticket_id": f"ticket_{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "issue_summary": message,
            "sentiment": sentiment,
            "status": "OPEN",
            "priority": "HIGH" if sentiment == "negative" else "MEDIUM"
        }