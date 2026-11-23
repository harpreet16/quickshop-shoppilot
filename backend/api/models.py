from typing import Literal
from pydantic import BaseModel, Field


# ── Requests ──────────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        description="Natural-language shopping request, e.g. 'black jeans under $80'",
    )
    session_id: str | None = Field(
        None,
        description="Pass back the session_id from a previous response to continue the conversation",
    )


# ── SSE event payloads ────────────────────────────────────────────────────────


class ThinkingPayload(BaseModel):
    message: str


class ToolCallPayload(BaseModel):
    tool: str
    status: str
    blocked: bool = False


class QuestionPayload(BaseModel):
    question: str = Field(
        ...,
        description="Clarification question the agent wants to ask — display this to the user",
    )


class ProductScores(BaseModel):
    price: int | None = None
    quality: int | None = None
    legitimacy: int | None = None
    overall: float | None = None


class ProductResult(BaseModel):
    title: str
    merchant: str
    price: float | None = None
    rating: float | None = None
    reviews: int | None = None
    url: str
    image_url: str | None = Field(None, description="Product photo: from the page read when there was one, else the search thumbnail")
    scores: ProductScores
    eligible: bool = Field(
        ...,
        description="False when the seller failed the legitimacy gate. Never recommend these.",
    )
    risk: Literal["low", "medium", "high"] | None = None
    evidence: list[str] = []
    natural_fiber_pct: float | None = None
    composition: dict[str, float] | None = None


class DonePayload(BaseModel):
    response: str = Field(..., description="Full markdown response from the agent")
    session_id: str = Field(
        ...,
        description="Pass this back in the next request to continue the conversation",
    )
    tool_calls: int
    firecrawl_credits: int = 0
    products: list[ProductResult] = Field(
        default_factory=list,
        description="Every product the agent scored, eligible first, best overall score first",
    )


class ErrorPayload(BaseModel):
    message: str
    code: str = "AGENT_ERROR"


# ── Health ────────────────────────────────────────────────────────────────────


class ServiceStatus(BaseModel):
    firecrawl: bool
    model: bool


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"] = "ok"
    version: str = "0.1.0"
    model: str
    services: ServiceStatus
