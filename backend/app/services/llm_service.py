from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app.services.summary_service import SummaryService

from app.config import settings
from app.services.rag_service import RAGService


class LLMService:
    def __init__(self):
        if settings.LLM_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY must be set when LLM_PROVIDER=openai."
                )

            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.2
            )

        else:
            if not settings.GROQ_API_KEY:
                raise ValueError(
                    "GROQ_API_KEY must be set when LLM_PROVIDER=groq."
                )

            self.llm = ChatGroq(
                model=settings.GROQ_MODEL,
                api_key=settings.GROQ_API_KEY,
                temperature=0.2
            )

        self.rag_service = RAGService()
        self.summary_service = SummaryService(self.llm)

    def generate_ticket_summary(
        self,
        user_message: str,
        bot_response: str,
        sentiment: str,
        priority: str
    ) -> str:
        return self.summary_service.generate_ticket_summary(
            user_message=user_message,
            bot_response=bot_response,
            sentiment=sentiment,
            priority=priority
        )

    def generate_response(self, user_message: str, history: list[str] = None):
        retrieval_query = user_message

        if history:
            retrieval_query = "\n".join(history[-4:]) + "\nUser: " + user_message

        documents, scores = self.rag_service.retrieve(retrieval_query)
        #documents, scores = self.rag_service.retrieve(user_message)
        confidence_score = self.rag_service.calculate_confidence(scores)

        context = "\n\n".join(documents)

        history_text = ""
        if history:
            history_text = "\n".join(history)

        system_prompt = f"""
You are a customer support assistant.

Answer the customer using the company knowledge base context below.

Important rules:
- If the context contains the answer, answer directly.
- You may make simple logical conclusions from the context.
- If the context says refund requests made after 30 days are not eligible, then a customer cannot get a refund after 40 days.
- If the context says refunds usually take 5 to 10 business days, then:
  - A refund is not guaranteed within 5 business days.
  - A refund may complete within 10 business days, but exact completion is not guaranteed.
- Do not invent policies, prices, legal claims, or timelines.
- Do not say you will escalate. Escalation is handled by the backend system.
- Only say "I don't have enough information to answer that accurately." if the context does not contain enough related information.

Conversation history:
{history_text}

Company knowledge base context:
{context}
"""

        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        answer = response.content

        if "I don't have enough information" in answer:
            confidence_score = 0.0

        return answer, confidence_score