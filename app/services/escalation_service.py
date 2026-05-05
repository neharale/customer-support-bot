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
            "refund",
            "charged twice",
            "fraud",
            "lawsuit",
            "cancel",
            "complaint",
            "angry",
            "not helping"
        ]

        if sentiment == "negative":
            return True

        if confidence_score < 0.70:
            return True

        if failed_attempts >= 2:
            return True

        if any(keyword in message_lower for keyword in escalation_keywords):
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