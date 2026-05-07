from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.admin import router as admin_router
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app import db_models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Customer Support Bot with Escalation",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(admin_router, prefix="/api/admin")


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