from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from app.config import settings


class LLMService:
    def __init__(self):
        if settings.LLM_PROVIDER == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY must be set when LLM_PROVIDER=openai. "
                    "Set OPENAI_API_KEY in backend/.env or your shell environment."
                )
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=settings.OPENAI_API_KEY,
                temperature=0.2
            )
        else:
            if not settings.GROQ_API_KEY:
                raise ValueError(
                    "GROQ_API_KEY must be set when LLM_PROVIDER=groq. "
                    "Set GROQ_API_KEY in backend/.env or your shell environment."
                )
            self.llm = ChatGroq(
                model=settings.GROQ_MODEL,
                api_key=settings.GROQ_API_KEY,
                temperature=0.2
            )

    def generate_response(self, user_message: str) -> tuple[str, float]:
        system_prompt = """
        You are a helpful customer support assistant.
        Answer politely and concisely.
        If you are unsure, say that the issue should be escalated.
        Do not invent policies, prices, refunds, or legal claims.
        """

        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])

        # Temporary confidence score.
        # Later we replace this with RAG similarity score.
        confidence_score = 0.80

        return response.content, confidence_score