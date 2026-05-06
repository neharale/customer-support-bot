from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

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

Conversation history:
{history_text}

Use ONLY the company knowledge base context below to answer.

If answer is not found, say:
"I don't have enough information to answer that accurately."

Do NOT say you will escalate. Escalation is handled by the system.

Knowledge base:
{context}
"""

        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])

        return response.content, confidence_score