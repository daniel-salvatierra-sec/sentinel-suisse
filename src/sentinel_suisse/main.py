"""FastAPI application — localhost only (Phase 2+)."""

from fastapi import FastAPI, Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.api.routes import (
    alerts,
    listings,
    notification_channels,
    providers,
    saved_searches,
    search,
    users,
)
from sentinel_suisse.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Sentinel Suisse API",
    description="Internal API — localhost only until public launch",
    version="0.5.0",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(providers.router, prefix="/api/v1")
app.include_router(listings.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(saved_searches.router, prefix="/api/v1")
app.include_router(notification_channels.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")


def custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("components", {}).setdefault("securitySchemes", {})
    schema["components"]["securitySchemes"]["X-API-Key"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
    }
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]


@app.get("/health")
@limiter.limit(lambda: get_settings().rate_limit)
def health(request: Request) -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}
