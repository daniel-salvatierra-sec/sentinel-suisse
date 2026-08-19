"""AI assistant service — calls an OpenAI-compatible chat completion API.

Works with OpenAI itself or any OpenAI-compatible endpoint (e.g. Google Gemini's
compatibility API) — see Settings.assistant_api_base_url. Kept intentionally
stateless (no server-side chat history storage) and scoped to LinkSwiss topics
via the system prompt. Cost is bounded by the caller (rate limiting,
max_output_tokens, input length) — see api/routes/assistant.py.
"""

import logging

import httpx

from sentinel_suisse.config import Settings

logger = logging.getLogger(__name__)

_LANGUAGE_NAMES = {
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "pt": "Portuguese",
    "en": "English",
}

_SYSTEM_PROMPT = """You are "Sentinel", the friendly in-app guide for LinkSwiss (linkswiss.ch), \
a Swiss platform that aggregates public housing and job listings and sends optional email/\
WhatsApp alerts.

Facts you can rely on:
- Search (housing + jobs) is always free, unlimited, no account needed. Anyone can browse \
listings without ever paying anything.
- Automatic alerts (being notified by email or WhatsApp whenever a new listing matches what \
they're looking for) require LinkSwiss Premium (9.90 CHF/month, card or TWINT via Stripe). \
Without Premium, nothing is sent automatically — the person has to come back and search \
manually to see new results.
- LinkSwiss Premium also unlocks WhatsApp alerts specifically, up to 5 saved searches (vs 1 \
without Premium), and under-construction/off-plan listings.
- Users cancel anytime from Account -> "Gerer l'abonnement" (Stripe Customer Portal).
- Listings come from third-party portals (Homegate, Flatfox, ImmoScout24, jobs.ch, etc.) — \
LinkSwiss is not the landlord/employer, always verify on the original listing.
- The service currently focuses on Switzerland (especially Geneva) and nearby France.

Style and limits:
- Always reply in {language}, unless the user clearly writes in a different language — then \
switch to their language.
- Be concise and warm: 2-5 short sentences, no long essays.
- You do NOT have live access to specific real listings — never invent a job/apartment offer, \
a price, or a company name. Instead, tell the user to use the search bar or set up an alert.
- You may give general, practical tips about job hunting or apartment hunting in Switzerland/\
France (CV basics, typical rental dossier documents, etc.), but you are not a lawyer, tax \
advisor, or immigration consultant — for legal, tax, or visa questions, tell the user to \
consult a qualified professional.
- Politely decline anything unrelated to LinkSwiss, jobs, or housing, or anything harmful/\
abusive.
"""


class AssistantError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _build_messages(
    message: str,
    lang: str,
    history: list[dict[str, str]],
    settings: Settings,
) -> list[dict[str, str]]:
    language = _LANGUAGE_NAMES.get(lang, "French")
    trimmed_history = history[-settings.assistant_max_history_messages :]
    messages = [{"role": "system", "content": _SYSTEM_PROMPT.format(language=language)}]
    messages.extend(trimmed_history)
    messages.append({"role": "user", "content": message})
    return messages


def ask_assistant(
    message: str,
    lang: str,
    history: list[dict[str, str]],
    settings: Settings,
) -> str:
    """Call the configured LLM and return a reply. Raises AssistantError on failure."""
    if not settings.assistant_is_enabled():
        raise AssistantError("assistant_disabled")

    payload: dict[str, object] = {
        "model": settings.assistant_model,
        "messages": _build_messages(message, lang, history, settings),
        "max_tokens": settings.assistant_max_output_tokens,
        "temperature": 0.4,
    }
    if settings.assistant_reasoning_effort:
        payload["reasoning_effort"] = settings.assistant_reasoning_effort
    headers = {
        "Authorization": f"Bearer {settings.assistant_api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(
            settings.assistant_api_base_url,
            json=payload,
            headers=headers,
            timeout=20.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Assistant upstream error: %s %s",
            exc.response.status_code,
            exc.response.text[:300],
        )
        raise AssistantError("assistant_upstream_error") from exc
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        logger.warning("Assistant call failed: %s", exc)
        raise AssistantError("assistant_upstream_error") from exc
