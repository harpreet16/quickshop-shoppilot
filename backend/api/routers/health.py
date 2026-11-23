import os
from fastapi import APIRouter
from ..models import HealthResponse, ServiceStatus
from quickshop.config import active_model_id, model_configured

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health() -> HealthResponse:
    """Returns the health of the API and whether each external service key is configured."""
    services = ServiceStatus(
        firecrawl=bool(os.getenv("FIRECRAWL_API_KEY")),
        model=model_configured(),
    )
    all_ok = all([services.firecrawl, services.model])
    return HealthResponse(
        status="ok" if all_ok else "degraded",
        model=active_model_id(),
        services=services,
    )
