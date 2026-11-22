"""
QuickShop API — run locally with:
    uvicorn backend.api.main:app --reload --port 8000

Interactive docs: http://localhost:8000/docs
"""
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import chat, health

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm-up: nothing blocking needed right now.
    # Add DB pool, cache pre-warming, etc. here when needed.
    yield


app = FastAPI(
    title="QuickShop API",
    description="Agentic shopping assistant — streams recommendations as Server-Sent Events.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow the Next.js dev server and any future Amplify domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(chat.router)
