"""FastAPI application."""

from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

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
from sentinel_suisse.config import Settings, get_settings
from sentinel_suisse.services.health import check_database


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    application = FastAPI(
        title="Sentinel Suisse API",
        description="Sentinel Suisse — housing and job alerts",
        version="0.42.0",
        docs_url="/docs" if settings.app_env == "development" else None,
        redoc_url=None,
    )

    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.add_middleware(SlowAPIMiddleware)

    trusted_hosts = settings.trusted_hosts_list()
    if settings.app_env == "production" and trusted_hosts:
        application.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

    cors_origins: list[str] = []
    if settings.app_env == "development":
        cors_origins.append("http://127.0.0.1:5173")
    public_origin = settings.public_app_url.rstrip("/")
    if public_origin and public_origin not in cors_origins:
        cors_origins.append(public_origin)

    if cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    application.include_router(providers.router, prefix="/api/v1")
    application.include_router(listings.router, prefix="/api/v1")
    application.include_router(search.router, prefix="/api/v1")
    application.include_router(users.router, prefix="/api/v1")
    application.include_router(saved_searches.router, prefix="/api/v1")
    application.include_router(notification_channels.router, prefix="/api/v1")
    application.include_router(alerts.router, prefix="/api/v1")
    application.include_router(legal.router, prefix="/api/v1")
    application.include_router(public.router, prefix="/api/v1")
    application.include_router(webhooks.router, prefix="/api/v1")

    @application.get("/health")
    @limiter.exempt
    def health(response: Response) -> dict[str, str]:
        # Exempt from rate limiting — used by Docker HEALTHCHECK and monitors.
        # Must be registered BEFORE the frontend StaticFiles mount at "/".
        db_ok = check_database()
        payload = {
            "status": "ok" if db_ok else "degraded",
            "env": settings.app_env,
            "database": "ok" if db_ok else "error",
        }
        if not db_ok:
            response.status_code = 503
        return payload

    dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist.is_dir():
        from fastapi.staticfiles import StaticFiles

        application.mount("/", StaticFiles(directory=str(dist), html=True), name="frontend")

    def custom_openapi() -> dict:
        if application.openapi_schema:
            return application.openapi_schema
        from fastapi.openapi.utils import get_openapi

        schema = get_openapi(
            title=application.title,
            version=application.version,
            description=application.description,
            routes=application.routes,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})
        schema["components"]["securitySchemes"]["X-API-Key"] = {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
        }
        application.openapi_schema = schema
        return application.openapi_schema

    application.openapi = custom_openapi  # type: ignore[method-assign]

    return application


app = create_app()
