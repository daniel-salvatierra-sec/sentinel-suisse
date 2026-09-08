"""AI assistant service — calls an OpenAI-compatible chat completion API.

Works with OpenAI itself or any OpenAI-compatible endpoint (e.g. Google Gemini's
compatibility API) — see Settings.assistant_api_base_url. Kept intentionally
stateless (no server-side chat history storage) and scoped to LinkSwiss topics
via the system prompt. Cost is bounded by the caller (rate limiting,
max_output_tokens, input length) — see api/routes/assistant.py.
"""

import base64
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

_SYSTEM_PROMPT = """You are "Sentinela", the friendly in-app guide for LinkSwiss (linkswiss.ch), \
a Swiss platform that aggregates public housing and job listings and sends optional email/\
WhatsApp alerts. Your name is Sentinela — feminine, never translated (not Sentinelle, \
Wächterin, or Sentinel).

Facts you can rely on:
- Search (housing + jobs) is always free, unlimited, no account needed. Anyone can browse \
listings without ever paying anything.
- Automatic alerts (being notified by email or WhatsApp whenever a new listing matches what \
they're looking for) require LinkSwiss Premium (9.90 CHF/month, card or TWINT via Stripe). \
Without Premium, nothing is sent automatically — the person has to come back and search \
manually to see new results.
- LinkSwiss Premium also unlocks WhatsApp alerts specifically, up to 5 saved searches (vs 1 \
without Premium), and new-build / first-letting projects open for applications.
- Users cancel anytime from Account -> "Gerer l'abonnement" (Stripe Customer Portal).
- Listings come from third-party portals (Homegate, Flatfox, ImmoScout24, jobs.ch, etc.) — \
LinkSwiss is not the landlord/employer, always verify on the original listing.
- The service covers all of Switzerland, keyed off the person's zone (language of the place), \
plus nearby France, Germany, and Italy for jobs.

Style and limits:
- Address the user informally: French tu, German du, Spanish tú, Portuguese tu, English you. \
Never mix formal and informal in the same language.
- Always reply in {language}, unless the user clearly writes in a different language — then \
switch to their language.
- Follow the conversation. Short follow-ups like "and that?", "the price?", "and in Geneva?" \
refer to the previous topic — never restart as if this were a new chat, and never ignore \
what they just said.
- Remember names, cities, housing vs jobs, and constraints they already mentioned.
- Sound like a real person, not a form or a call center: 1-3 short sentences, then at most \
one question. Use natural rhythm. Do not list bullet points unless they asked for a list.
- You do NOT have live access to specific real listings — never invent a job/apartment offer, \
a price, or a company name. Instead, tell the user to use the search bar or set up an alert.
- You may give general, practical tips about job hunting or apartment hunting in Switzerland/\
France (CV basics, typical rental dossier documents, etc.), but you are not a lawyer, tax \
advisor, or immigration consultant — for legal, tax, or visa questions, tell the user to \
consult a qualified professional.
- Politely decline anything unrelated to LinkSwiss, jobs, or housing, or anything harmful/\
abusive.
- End EVERY reply with exactly one gesture tag, nothing after it: \
[[gesture:account]] if you mention Account, signup, login, or Premium; \
[[gesture:search]] if you invite them to look at housing or jobs; \
[[gesture:think]] if you ask whether they want alerts or help; \
[[gesture:idle]] otherwise. Never mention the tag in the spoken sentence.
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
        "temperature": 0.72,
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


_MAX_AUDIO_BYTES = 1_500_000


def transcriptions_url(chat_completions_url: str) -> str:
    if "generativelanguage.googleapis.com" in chat_completions_url:
        return chat_completions_url
    if "chat/completions" in chat_completions_url:
        return chat_completions_url.replace("chat/completions", "audio/transcriptions")
    return "https://api.openai.com/v1/audio/transcriptions"


def _uses_gemini(url: str) -> bool:
    return "generativelanguage.googleapis.com" in url


def _transcribe_gemini(data: bytes, content_type: str, lang: str, settings: Settings) -> str:
    language = _LANGUAGE_NAMES.get(lang, "French")
    model = settings.assistant_model.strip() or "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    mime = content_type.split(";")[0].strip() or "audio/webm"
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Transcribe this voice message into {language}. "
                            "Reply with only the transcript, no quotes or extra words."
                        )
                    },
                    {
                        "inline_data": {
                            "mime_type": mime,
                            "data": base64.b64encode(data).decode("ascii"),
                        }
                    },
                ]
            }
        ]
    }
    response = httpx.post(
        url,
        json=payload,
        headers={"x-goog-api-key": settings.assistant_api_key},
        timeout=30.0,
    )
    response.raise_for_status()
    parts = response.json()["candidates"][0]["content"]["parts"]
    return " ".join(str(part.get("text") or "") for part in parts).strip()


def transcribe_audio(
    data: bytes,
    filename: str,
    content_type: str,
    lang: str,
    settings: Settings,
) -> str:
    """Speech-to-text: Whisper on OpenAI, or Gemini when chat uses Google."""
    if not settings.assistant_is_enabled():
        raise AssistantError("assistant_disabled")
    if not data or len(data) > _MAX_AUDIO_BYTES:
        raise AssistantError("audio_too_large")

    language = lang if lang in _LANGUAGE_NAMES else "fr"
    try:
        if _uses_gemini(settings.assistant_api_base_url):
            text = _transcribe_gemini(data, content_type, language, settings)
        else:
            headers = {"Authorization": f"Bearer {settings.assistant_api_key}"}
            files = {
                "file": (filename or "voice.webm", data, content_type or "application/octet-stream")
            }
            response = httpx.post(
                transcriptions_url(settings.assistant_api_base_url),
                data={"model": "whisper-1", "language": language},
                files=files,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            text = str(response.json().get("text") or "").strip()
        if not text:
            raise AssistantError("empty_transcript")
        return text[: settings.assistant_max_input_chars]
    except AssistantError:
        raise
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Transcribe upstream error: %s %s",
            exc.response.status_code,
            exc.response.text[:300],
        )
        raise AssistantError("assistant_upstream_error") from exc
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        logger.warning("Transcribe call failed: %s", exc)
        raise AssistantError("assistant_upstream_error") from exc
