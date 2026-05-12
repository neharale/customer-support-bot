from langchain_core.messages import HumanMessage, SystemMessage


class SummaryService:
    def __init__(self, llm):
        self.llm = llm

    def generate_ticket_summary(
        self,
        user_message: str,
        bot_response: str,
        sentiment: str,
        priority: str
    ) -> str:
        system_prompt = """
You are a support ticket summarizer.

Write a concise internal summary for a human support agent.
Keep it under 3 sentences.
Include:
- customer issue
- bot action
- priority/severity
Do not invent details.
"""

        user_prompt = f"""
Customer message:
{user_message}

Bot response:
{bot_response}

Sentiment:
{sentiment}

Priority:
{priority}
"""

        response = self.llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        return response.content