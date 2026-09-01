"""Public SEO guides: dossier, Swiss CV, permit G. Official links only."""

from __future__ import annotations

import html
import re

from sentinel_suisse.config import PROJECT_DIR
from sentinel_suisse.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

GUIDES_DIR = PROJECT_DIR / "docs" / "guides"
GUIDE_SLUGS = ("dossier", "cv", "permis-g")

_LINK = re.compile(r"\[([^\]]+)\]\((https://[^\s)]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")

SEM_G = {
    "fr": "https://www.sem.admin.ch/sem/fr/home/themen/aufenthalt/eu_efta/ausweis_g.html",
    "de": "https://www.sem.admin.ch/sem/de/home/themen/aufenthalt/eu_efta/ausweis_g.html",
    "it": "https://www.sem.admin.ch/sem/it/home/themen/aufenthalt/eu_efta/ausweis_g.html",
    "en": "https://www.sem.admin.ch/sem/en/home/themen/aufenthalt/eu_efta/ausweis_g.html",
    "es": "https://www.sem.admin.ch/sem/en/home/themen/aufenthalt/eu_efta/ausweis_g.html",
    "pt": "https://www.sem.admin.ch/sem/en/home/themen/aufenthalt/eu_efta/ausweis_g.html",
}

CH_CH = {
    "fr": "https://www.ch.ch/fr/",
    "de": "https://www.ch.ch/de/",
    "it": "https://www.ch.ch/it/",
    "en": "https://www.ch.ch/en/",
    "es": "https://www.ch.ch/en/",
    "pt": "https://www.ch.ch/en/",
}

ARBEIT = {
    "fr": "https://www.arbeit.swiss/secoalv/fr/home.html",
    "de": "https://www.arbeit.swiss/secoalv/de/home.html",
    "it": "https://www.arbeit.swiss/secoalv/it/home.html",
    "en": "https://www.arbeit.swiss/secoalv/en/home.html",
    "es": "https://www.arbeit.swiss/secoalv/en/home.html",
    "pt": "https://www.arbeit.swiss/secoalv/en/home.html",
}

TITLES = {
    "dossier": {
        "fr": "Dossier de logement en Suisse",
        "de": "Wohndossier in der Schweiz",
        "es": "Dossier de piso en Suiza",
        "pt": "Dossier de apartamento na Suíça",
        "en": "Rental dossier in Switzerland",
    },
    "cv": {
        "fr": "CV suisse pour un poste",
        "de": "Schweizer CV für eine Stelle",
        "es": "CV suizo para un puesto",
        "pt": "CV suíço para um posto",
        "en": "Swiss CV for a job",
    },
    "permis-g": {
        "fr": "Permis G (frontalier)",
        "de": "Ausweis G (Grenzgänger)",
        "es": "Permiso G (frontalier)",
        "pt": "Autorização G (frontalier)",
        "en": "Permit G (cross-border)",
    },
}


def _inline(text: str) -> str:
    chunks: list[str] = []
    pos = 0
    for match in _LINK.finditer(text):
        chunks.append(html.escape(text[pos : match.start()]))
        label = html.escape(match.group(1))
        href = html.escape(match.group(2), quote=True)
        chunks.append(f'<a href="{href}" rel="noopener noreferrer">{label}</a>')
        pos = match.end()
    chunks.append(html.escape(text[pos:]))
    return _BOLD.sub(r"<strong>\1</strong>", "".join(chunks))


def md_to_html(markdown: str) -> str:
    lines = markdown.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    list_open = False
    for raw in lines:
        line = raw.rstrip()
        if line.startswith("- "):
            if not list_open:
                out.append("<ul>")
                list_open = True
            out.append(f"<li>{_inline(line[2:])}</li>")
            continue
        if list_open:
            out.append("</ul>")
            list_open = False
        if not line:
            continue
        if line.startswith("# "):
            out.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{_inline(line[3:])}</h2>")
        else:
            out.append(f"<p>{_inline(line)}</p>")
    if list_open:
        out.append("</ul>")
    return "\n".join(out)


def load_guide_markdown(slug: str, lang: str) -> str:
    if slug not in GUIDE_SLUGS:
        msg = f"Unknown guide: {slug}"
        raise ValueError(msg)
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    path = GUIDES_DIR / f"{slug}.{lang}.md"
    if not path.is_file():
        path = GUIDES_DIR / f"{slug}.{DEFAULT_LANGUAGE}.md"
    text = path.read_text(encoding="utf-8")
    return (
        text.replace("{sem_g}", SEM_G[lang])
        .replace("{ch_ch}", CH_CH[lang])
        .replace("{arbeit}", ARBEIT[lang])
    )


_DISCLAIMER = {
    "fr": (
        "Sentinela n'est pas avocate. Cette page n'est pas un conseil juridique "
        "ni fiscal. Les liens pointent vers des sites officiels."
    ),
    "de": (
        "Sentinela ist keine Anwältin. Diese Seite ist keine Rechts- oder "
        "Steuerberatung. Die Links führen zu offiziellen Seiten."
    ),
    "es": (
        "Sentinela no es abogada. Esta página no es asesoría legal ni fiscal. "
        "Los enlaces van a sitios oficiales."
    ),
    "pt": (
        "A Sentinela não é advogada. Esta página não é aconselhamento jurídico "
        "nem fiscal. As ligações vão para sítios oficiais."
    ),
    "en": (
        "Sentinela is not a lawyer. This page is not legal or tax advice. "
        "Links go to official sites."
    ),
}
_META = {
    "fr": "Pas un conseil juridique.",
    "de": "Keine Rechtsberatung.",
    "es": "No es asesoría legal.",
    "pt": "Não é aconselhamento jurídico.",
    "en": "This is not legal advice.",
}
_OTHERS = {
    "fr": "Autres guides",
    "de": "Weitere Ratgeber",
    "es": "Otras guías",
    "pt": "Outros guias",
    "en": "Other guides",
}
_BACK = {
    "fr": "Retour à LinkSwiss",
    "de": "Zurück zu LinkSwiss",
    "es": "Volver a LinkSwiss",
    "pt": "Voltar ao LinkSwiss",
    "en": "Back to LinkSwiss",
}


def render_guide_page(*, slug: str, lang: str, origin: str) -> str:
    origin = origin.rstrip("/")
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    title = TITLES[slug][lang]
    body = md_to_html(load_guide_markdown(slug, lang))
    disclaimer = _DISCLAIMER[lang]
    others = "".join(
        f'<li><a href="/guides/{other}?lang={html.escape(lang)}">'
        f"{html.escape(TITLES[other][lang])}</a></li>"
        for other in GUIDE_SLUGS
        if other != slug
    )
    alts = "".join(
        (
            f'<link rel="alternate" hreflang="{code}" '
            f'href="{html.escape(origin)}/guides/{slug}?lang={code}" />\n'
        )
        for code in SUPPORTED_LANGUAGES
    )
    description = html.escape(f"{title}. LinkSwiss / Sentinela. {_META[lang]}")
    canonical = html.escape(f"{origin}/guides/{slug}?lang={lang}")
    return f"""<!DOCTYPE html>
<html lang="{html.escape(lang)}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(title)} — LinkSwiss</title>
<meta name="description" content="{description}" />
<link rel="canonical" href="{canonical}" />
{alts}<style>
body {{
  margin:0; font: 18px/1.5 Inter, system-ui, sans-serif;
  color:#1c2d28; background:#eef6f4;
}}
main {{ max-width: 40rem; margin: 0 auto; padding: 1.25rem 1rem 3rem; }}
a {{ color:#1a6f8a; }}
.disclaimer {{
  background:#fff; border-radius:0.75rem; padding:0.85rem 1rem;
  font-size:0.92rem; color:#5a6b66;
}}
nav {{ font-size:0.9rem; margin: 1rem 0; }}
</style>
</head>
<body>
<main>
<p><a href="{html.escape(origin)}/">LinkSwiss</a></p>
{body}
<aside class="disclaimer">{html.escape(disclaimer)}</aside>
<nav><p>{html.escape(_OTHERS[lang])}</p><ul>{others}</ul></nav>
<p><a href="{html.escape(origin)}/">{html.escape(_BACK[lang])}</a></p>
</main>
</body>
</html>
"""


def render_guides_index(*, lang: str, origin: str) -> str:
    origin = origin.rstrip("/")
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    items = "".join(
        (
            f'<li><a href="/guides/{slug}?lang={html.escape(lang)}">'
            f"{html.escape(TITLES[slug][lang])}</a></li>"
        )
        for slug in GUIDE_SLUGS
    )
    heading = {
        "fr": "Guides LinkSwiss",
        "de": "LinkSwiss-Ratgeber",
        "es": "Guías LinkSwiss",
        "pt": "Guias LinkSwiss",
        "en": "LinkSwiss guides",
    }[lang]
    intro = {
        "fr": (
            "Dossier, CV suisse, permis G — avec des liens officiels. "
            "Ce n'est pas un conseil juridique."
        ),
        "de": "Dossier, Schweizer CV, Ausweis G — mit offiziellen Links. Keine Rechtsberatung.",
        "es": "Dossier, CV suizo, permiso G — con enlaces oficiales. No es asesoría legal.",
        "pt": (
            "Dossier, CV suíço, autorização G — com ligações oficiais. "
            "Não é aconselhamento jurídico."
        ),
        "en": "Dossier, Swiss CV, permit G — with official links. This is not legal advice.",
    }[lang]
    canonical = html.escape(f"{origin}/guides?lang={lang}")
    return f"""<!DOCTYPE html>
<html lang="{html.escape(lang)}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(heading)}</title>
<link rel="canonical" href="{canonical}" />
<style>
body {{
  margin:0; font: 18px/1.5 Inter, system-ui, sans-serif;
  color:#1c2d28; background:#eef6f4;
}}
main {{ max-width: 40rem; margin: 0 auto; padding: 1.25rem 1rem 3rem; }}
a {{ color:#1a6f8a; }}
</style>
</head>
<body>
<main>
<p><a href="{html.escape(origin)}/">LinkSwiss</a></p>
<h1>{html.escape(heading)}</h1>
<p>{html.escape(intro)}</p>
<ul>{items}</ul>
</main>
</body>
</html>
"""
