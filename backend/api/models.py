from typing import Literal
from pydantic import BaseModel, Field


# ── Requests ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str = Field(..., description="Natural-language shopping request, e.g. 'black jeans under $80'")
    session_id: str | None = Field(None, description="Pass back the session_id from a previous response to continue the conversation")


# ── SSE event payloads ────────────────────────────────────────────────────────

class ThinkingPayload(BaseModel):
    message: str

class ToolCallPayload(BaseModel):
    tool: str
    status: str
    blocked: bool = False

class QuestionPayload(BaseModel):
    question: str = Field(..., description="Clarification question the agent wants to ask — display this to the user")

class DonePayload(BaseModel):
    response: str = Field(..., description="Full markdown response from the agent")
    session_id: str = Field(..., description="Pass this back in the next request to continue the conversation")
    tool_calls: int
    firecrawl_credits: int = 0

class ErrorPayload(BaseModel):
    message: str
    code: str = "AGENT_ERROR"


# ── Health ────────────────────────────────────────────────────────────────────

class ServiceStatus(BaseModel):
    serpapi: bool
    firecrawl: bool
    model: bool

class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"] = "ok"
    version: str = "0.1.0"
    model: str
    services: ServiceStatus
