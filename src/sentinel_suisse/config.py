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
    verification_token_ttl_hours: int = 48
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
    # Dispatch alerts automatically after ingest when new listings are created
    ingest_dispatch_alerts: bool = False
    # Live Homegate fetch — disabled by default (legal / rate-limit review required)
    ingest_homegate_live: bool = False
    ingest_jobs_live: bool = False
    ingest_flatfox_live: bool = False
    ingest_immoscout_live: bool = False
    ingest_rate_limit_seconds: float = 3.0
    ingest_user_agent: str = (
        "SentinelSuisse/0.14 " "(+github.com/daniel-salvatierra-sec/sentinel-suisse)"
    )
    homegate_search_url: str = "https://www.homegate.ch/mieten/immobilien/kanton-genf/trefferliste"
    jobs_search_url: str = "https://www.jobs.ch/en/vacancies/?location=Geneva"
    flatfox_search_url: str = "https://flatfox.ch/en/search/?place=Geneva"
    immoscout_search_url: str = "https://www.immoscout24.ch/fr/immobilier/louer/lieu-geneve"

    def smtp_is_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_from)

    def whatsapp_is_configured(self) -> bool:
        return bool(self.whatsapp_token and self.whatsapp_phone_number_id)

    def signup_channels_auto_verify(self) -> bool:
        if self.signup_auto_verify is not None:
            return self.signup_auto_verify
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
