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
    login_token_ttl_minutes: int = 20
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
    ingest_leboncoin_live: bool = False
    ingest_indeed_fr_live: bool = False
    # France Travail — official OAuth2 REST API (francetravail.io), not scraping.
    ingest_france_travail_live: bool = False
    france_travail_client_id: str = ""
    france_travail_client_secret: str = ""
    france_travail_departement: str = "74"
    france_travail_keywords: str = ""
    # Adzuna — official self-serve job-board aggregator API (developer.adzuna.com), built
    # specifically for redistributing job ads on third-party sites. Not scraping.
    ingest_adzuna_live: bool = False
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    adzuna_country: str = "ch"
    adzuna_keywords: str = ""
    adzuna_location: str = "Geneve"
    # SmartRecruiters — official, keyless Postings API used by several large Geneva
    # employers (e.g. HUG, SGS) for their public career sites. Not scraping.
    ingest_smartrecruiters_live: bool = False
    smartrecruiters_companies: str = "HUG,SGS"
    smartrecruiters_fetch_details: bool = True
    # Richemont — public Workday "Candidate Experience" JSON API (same one the group's
    # own careers.richemont.com career site calls). Not scraping.
    ingest_richemont_live: bool = False
    richemont_extra_location_hints: str = ""
    # Lombard Odier — same public Workday CXS API as Richemont
    # (lombardodier.wd3.myworkdayjobs.com/Lombard_Odier_Careers). Not scraping.
    ingest_lombard_odier_live: bool = False
    lombard_odier_extra_location_hints: str = ""
    # Logitech — same public Workday CXS API as Richemont
    # (logitech.wd5.myworkdayjobs.com/Logitech). Not scraping.
    ingest_logitech_live: bool = False
    logitech_extra_location_hints: str = ""
    # STMicroelectronics — public Eightfold SmartApply JSON API (same one
    # stmicroelectronics.eightfold.ai's own UI calls). Not scraping.
    ingest_stmicroelectronics_live: bool = False
    ingest_rate_limit_seconds: float = 3.0
    ingest_user_agent: str = (
        "SentinelSuisse/0.14 (+github.com/daniel-salvatierra-sec/sentinel-suisse)"
    )
    homegate_search_url: str = "https://www.homegate.ch/mieten/immobilien/kanton-genf/trefferliste"
    jobs_search_url: str = "https://www.jobs.ch/en/vacancies/?location=Geneva"
    flatfox_search_url: str = "https://flatfox.ch/en/search/?place=Geneva"
    immoscout_search_url: str = "https://www.immoscout24.ch/fr/immobilier/louer/lieu-geneve"
    newhome_search_url: str = "https://www.newhome.ch/fr/louer/geneve"
    anibis_search_url: str = "https://www.anibis.ch/fr/immobilier--8/annonces/geneve"
    jobup_search_url: str = "https://www.jobup.ch/fr/emplois/?location=Gen%C3%A8ve"
    leboncoin_search_url: str = (
        "https://www.leboncoin.fr/recherche"
        "?category=10&locations=Annemasse_74100__45.9024_6.2364_5000"
    )
    indeed_fr_search_url: str = "https://fr.indeed.com/jobs?q=&l=Annemasse+%2874%29&radius=25"
    # Freemium — free vs premium saved-search / channel limits
    free_max_saved_searches: int = 1
    premium_max_saved_searches: int = 5
    # Stripe Checkout — leave empty to disable payments UI
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""
    stripe_enable_twint: bool = True
    # Optional production error tracking
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.0
    # Optional AI assistant (free-form chat) — leave assistant_api_key empty to disable.
    # Works with any OpenAI-compatible chat completions endpoint: OpenAI itself, or
    # Google Gemini's compatibility endpoint (https://ai.google.dev/gemini-api/docs/openai) —
    # just swap the base URL, key, and model name below.
    assistant_api_key: str = ""
    assistant_api_base_url: str = "https://api.openai.com/v1/chat/completions"
    assistant_model: str = "gpt-4o-mini"
    assistant_max_output_tokens: int = 700
    # Optional: "minimal" | "low" | "medium" | "high". Reasoning ("thinking") models
    # like Gemini 3 count their internal reasoning tokens against max_output_tokens,
    # which can truncate the visible reply — set this to keep more budget for the
    # answer. Leave empty for non-reasoning models (e.g. OpenAI's gpt-4o-mini), which
    # reject this parameter.
    assistant_reasoning_effort: str = ""
    assistant_max_input_chars: int = 500
    assistant_max_history_messages: int = 6
    # slowapi rate string, e.g. "20/day" — keeps API costs bounded
    assistant_rate_limit: str = "20/day"

    def smtp_is_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_from)

    def whatsapp_is_configured(self) -> bool:
        return bool(self.whatsapp_token and self.whatsapp_phone_number_id)

    def stripe_payments_enabled(self) -> bool:
        return bool(self.stripe_secret_key and self.stripe_price_id)

    def assistant_is_enabled(self) -> bool:
        return bool(self.assistant_api_key)

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
