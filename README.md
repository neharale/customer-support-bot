# Customer Support Bot with Escalation

An AI-powered customer support system that provides automated responses using LLMs and intelligently escalates complex or sensitive issues to human agents.

## 🚀 Overview
Customer experience is critical - most of customers leave after a poor support interaction.

This project addresses that by combining:
- AI-driven responses using LLMs
- Sentiment analysis for user intent
- Smart escalation to human agents
- Persistent conversation and ticket storage

-------
## 🧠 Key Features

- 🤖 AI-powered chat using OpenAI / Groq
- 📊 Sentiment detection (positive / neutral / negative)
- ⚠️ Intelligent escalation system
- 💾 Persistent storage using SQLite
- 📜 Conversation tracking
- 🎫 Ticket creation for escalated issues
- 🔌 REST API built with FastAPI

-------
## 🏗️ Architecture
User → FastAPI API → Chat Controller
→ Sentiment Analysis
→ LLM (Groq/OpenAI)
→ Decision Engine
  ├── Respond to user
  └── Escalate to ticket system
→ SQLite Database

------

## 🛠️ Tech Stack

| Layer        | Technology |
|-------------|-----------|
| Backend     | Python, FastAPI |
| LLM         | Groq / OpenAI |
| AI Orchestration | LangChain |
| Database    | SQLite (SQLAlchemy) |
| Sentiment   | TextBlob |
| Vector DB (Upcoming) | ChromaDB |

---

## 📂 Project Structure
customer-support-bot/
│
├── backend/
│ ├── app/
│ │ ├── main.py
│ │ ├── config.py
│ │ ├── models.py
│ │ ├── database.py
│ │ ├── db_models.py
│ │ │
│ │ ├── api/
│ │ │ └── chat.py
│ │ │
│ │ ├── services/
│ │ │ ├── llm_service.py
│ │ │ ├── sentiment_service.py
│ │ │ ├── escalation_service.py
│ │ │
│ │ └── vectorstore/ (upcoming)
│ │
│ ├── knowledge_base/ (RAG data)
│ ├── requirements.txt
│ └── support_bot.db
│
└── README.md

---

## ⚙️ Setup Instructions

### 1. Clone the repository

bash
git clone https://github.com/your-username/customer-support-bot.git
cd customer-support-bot/backend

### 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate   # Mac/Linux

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure environment variables
Create a .env file in project root:

LLM_PROVIDER=groq
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

DATABASE_URL=sqlite:///./support_bot.db

### 5. Run the application
python -m uvicorn app.main:app --reload

Access API docs:
http://127.0.0.1:8000/docs

### 🔜 Future Enhancements
RAG (Retrieval-Augmented Generation) with ChromaDB
Multi-turn conversation memory
Admin dashboard for ticket management
Priority-based escalation (P0/P1/P2)
Slack / Email integration
Authentication & rate limiting
Deployment (Docker + Cloud)
💡 Why This Project Matters

This project demonstrates:
Backend API design
LLM integration in production workflows
Intelligent decision-making systems
Real-world problem solving (customer churn)
Scalable architecture thinking

### 👤 Author
Neha Rale

### 📜 License
MIT License
