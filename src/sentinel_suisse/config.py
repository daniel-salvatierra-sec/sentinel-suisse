"""Application settings from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    secret_key: str = ""
    pii_encryption_key: str = ""
    database_url: str = "postgresql://sentinel:sentinel@localhost:5432/sentinel_suisse"
    admin_username: str = ""
    admin_password_hash: str = ""
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    public_app_url: str = "http://127.0.0.1:5173"
    # Comma-separated hostnames for TrustedHostMiddleware in production (e.g. app.example.com)
    trusted_hosts: str = ""
    verification_token_ttl_hours: int = 48
    # None = auto (enabled in development); True/False force
    public_signup_enabled: bool | None = None
    public_search_enabled: bool | None = None
    # None = auto (verify in development only); False = always send verification email
    signup_auto_verify: bool | None = None
    rate_limit: str = "30/minute"
    # auto = SMTP when configured, else console; console = always log; smtp = require SMTP
    notifier_mode: str = "auto"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_app_secret: str = ""
    # Phase 24 — mark WhatsApp channel verified when Meta delivers inbound message
    whatsapp_inbound_auto_verify: bool = True
    # Phase 25 — required reply text (case-insensitive). Empty = any message verifies.
    whatsapp_verify_keyword: str = "OK"
    # Dispatch alerts automatically after ingest when new listings are created
    ingest_dispatch_alerts: bool = False
    # Live Homegate fetch — disabled by default (legal / rate-limit review required)
    ingest_homegate_live: bool = False
    ingest_jobs_live: bool = False
    ingest_flatfox_live: bool = False
    ingest_immoscout_live: bool = False
    ingest_newhome_live: bool = False
    ingest_anibis_live: bool = False
    ingest_jobup_live: bool = False
    ingest_rate_limit_seconds: float = 3.0
    ingest_user_agent: str = (
        "SentinelSuisse/0.14 " "(+github.com/daniel-salvatierra-sec/sentinel-suisse)"
    )
    homegate_search_url: str = "https://www.homegate.ch/mieten/immobilien/kanton-genf/trefferliste"
    jobs_search_url: str = "https://www.jobs.ch/en/vacancies/?location=Geneva"
    flatfox_search_url: str = "https://flatfox.ch/en/search/?place=Geneva"
    immoscout_search_url: str = "https://www.immoscout24.ch/fr/immobilier/louer/lieu-geneve"
    newhome_search_url: str = "https://www.newhome.ch/fr/louer/geneve"
    anibis_search_url: str = "https://www.anibis.ch/fr/immobilier--8/annonces/geneve"
    jobup_search_url: str = "https://www.jobup.ch/fr/emplois/?location=Gen%C3%A8ve"

    def smtp_is_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_from)

    def whatsapp_is_configured(self) -> bool:
        return bool(self.whatsapp_token and self.whatsapp_phone_number_id)

    def public_signup_is_enabled(self) -> bool:
        if self.public_signup_enabled is not None:
            return self.public_signup_enabled
        return self.app_env == "development"

    def public_search_is_enabled(self) -> bool:
        if self.public_search_enabled is not None:
            return self.public_search_enabled
        return self.app_env == "development"

    def signup_channels_auto_verify(self) -> bool:
        if self.signup_auto_verify is not None:
            return self.signup_auto_verify
        return self.app_env == "development"

    def trusted_hosts_list(self) -> list[str]:
        if not self.trusted_hosts.strip():
            return []
        return [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
