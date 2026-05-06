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

        critical_keywords = [
            "fraud",
            "charged twice",
            "double charged",
            "unauthorized",
            "hacked",
            "account was hacked"
        ]

        human_keywords = [
            "human",
            "agent",
            "manager",
            "not helping"
        ]

        account_security_keywords = [
            "delete my account",
            "cannot access my email",
            "can't access my email",
            "cant access my email",
            "account locked"
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

        if any(keyword in message_lower for keyword in critical_keywords):
            return True

        if any(keyword in message_lower for keyword in human_keywords):
            return True

        if any(keyword in message_lower for keyword in account_security_keywords):
            return True

        if shipping_escalation or tracking_escalation:
            return True

        if sentiment == "negative":
            return True

        # Keep this strict so normal account questions do not escalate
        if confidence_score < 0.50:
            return True

        if failed_attempts >= 2:
            return True

        return False

    def get_priority(self, message: str, sentiment: str) -> str:
        msg = message.lower()

        if any(x in msg for x in [
            "fraud",
            "charged twice",
            "double charged",
            "unauthorized",
            "hacked",
            "account was hacked"
        ]):
            return "P0"

        if any(x in msg for x in [
            "package hasn't arrived",
            "package has not arrived",
            "not delivered",
            "tracking not updating",
            "tracking is not updating",
            "cannot access my email",
            "can't access my email",
            "cant access my email",
            "account locked"
        ]):
            return "P1"

        return "P2"

    def create_ticket(self, user_id: str, message: str, sentiment: str) -> dict:
        priority = self.get_priority(message, sentiment)

        return {
            "ticket_id": f"ticket_{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "issue_summary": message,
            "sentiment": sentiment,
            "status": "OPEN",
            "priority": priority
        }