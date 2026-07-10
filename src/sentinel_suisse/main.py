"""FastAPI application — localhost only (Phase 2)."""

from fastapi import FastAPI, Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.api.routes import listings, providers
from sentinel_suisse.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Sentinel Suisse API",
    description="Internal admin API — not exposed publicly in Phase 2",
    version="0.2.0",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(providers.router, prefix="/api/v1")
app.include_router(listings.router, prefix="/api/v1")


@app.get("/health")
@limiter.limit(lambda: get_settings().rate_limit)
def health(request: Request) -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}
