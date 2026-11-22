import os
from fastapi import APIRouter
from ..models import HealthResponse, ServiceStatus
from quickshop.config import MODEL_ID

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health() -> HealthResponse:
    """Returns the health of the API and whether each external service key is configured."""
    services = ServiceStatus(
        serpapi=bool(os.getenv("SERPAPI_KEY")),
        firecrawl=bool(os.getenv("FIRECRAWL_API_KEY")),
        model=bool(os.getenv("API_KEY")),
    )
    all_ok = all([services.serpapi, services.firecrawl, services.model])
    return HealthResponse(
        status="ok" if all_ok else "degraded",
        model=MODEL_ID,
        services=services,
    )
