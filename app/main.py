from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.database import Base, engine
from app import db_models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Customer Support Bot with Escalation",
    version="1.0.0"
)

app.include_router(chat_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Customer Support Bot API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }