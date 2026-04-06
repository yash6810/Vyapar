"""
Vyapar AI — WhatsApp AI Accounting Assistant for Indian SMEs
Production backend: FastAPI + Gemini API + SQLAlchemy
"""
import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine
from . import models
from .routers import auth, expenses, invoices, webhook

# Create tables
models.Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("vyapar.log"),
    ],
)
logger = logging.getLogger("vyapar")

# App
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered accounting assistant for Indian SMEs",
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Mount routers
app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(invoices.router)
app.include_router(webhook.router)


# Health check
@app.get("/health", tags=["System"])
async def health_check():
    """Check system health."""
    gemini_status = "configured" if settings.GEMINI_API_KEY else "missing_api_key"
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "gemini": gemini_status,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)