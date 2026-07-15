"""FastAPI application — localhost only (Phase 2+)."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from sentinel_suisse.api.rate_limit import limiter
from sentinel_suisse.api.routes import (
    alerts,
    legal,
    listings,
    notification_channels,
    providers,
    public,
    saved_searches,
    search,
    users,
    webhooks,
)
from sentinel_suisse.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Sentinel Suisse API",
    description="Internal API — localhost only until public launch",
    version="0.26.0",
    docs_url="/docs" if settings.app_env == "development" else None,
    redoc_url=None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

_cors_origins: list[str] = []
if settings.app_env == "development":
    _cors_origins.append("http://127.0.0.1:5173")
_public_origin = settings.public_app_url.rstrip("/")
if _public_origin and _public_origin not in _cors_origins:
    _cors_origins.append(_public_origin)

if _cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(providers.router, prefix="/api/v1")
app.include_router(listings.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(saved_searches.router, prefix="/api/v1")
app.include_router(notification_channels.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(legal.router, prefix="/api/v1")
app.include_router(public.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")


def _mount_frontend() -> None:
    dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist.is_dir():
        from fastapi.staticfiles import StaticFiles

        app.mount("/", StaticFiles(directory=str(dist), html=True), name="frontend")


_mount_frontend()


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
