"""Login / set-password email copy in five mandatory languages."""

from sentinel_suisse.i18n import resolve_locale

_LOGIN_COPY: dict[str, dict[str, str]] = {
    "fr": {
        "subject": "LinkSwiss — votre lien de connexion",
        "body": (
            "Bonjour,\n\n"
            "Cliquez sur ce lien pour vous connecter à LinkSwiss :\n\n"
            "{url}\n\n"
            "Ce lien expire dans {minutes} minutes.\n\n"
            "Si vous n'avez pas demandé cette connexion, ignorez ce message."
        ),
    },
    "de": {
        "subject": "LinkSwiss — Ihr Anmeldelink",
        "body": (
            "Hallo,\n\n"
            "Klicken Sie auf diesen Link, um sich bei LinkSwiss anzumelden:\n\n"
            "{url}\n\n"
            "Dieser Link läuft in {minutes} Minuten ab.\n\n"
            "Falls Sie diese Anmeldung nicht angefordert haben, ignorieren Sie diese E-Mail."
        ),
    },
    "es": {
        "subject": "LinkSwiss — tu enlace de acceso",
        "body": (
            "Hola,\n\n"
            "Haz clic en este enlace para iniciar sesión en LinkSwiss:\n\n"
            "{url}\n\n"
            "Este enlace caduca en {minutes} minutos.\n\n"
            "Si no solicitaste este acceso, ignora este mensaje."
        ),
    },
    "pt": {
        "subject": "LinkSwiss — a sua ligação de acesso",
        "body": (
            "Olá,\n\n"
            "Clique nesta ligação para iniciar sessão no LinkSwiss:\n\n"
            "{url}\n\n"
            "Esta ligação expira em {minutes} minutos.\n\n"
            "Se não pediu este acesso, ignore esta mensagem."
        ),
    },
    "en": {
        "subject": "LinkSwiss — your login link",
        "body": (
            "Hello,\n\n"
            "Click this link to log in to LinkSwiss:\n\n"
            "{url}\n\n"
            "This link expires in {minutes} minutes.\n\n"
            "If you did not request this login, please ignore this email."
        ),
    },
}

_SETPW_COPY: dict[str, dict[str, str]] = {
    "fr": {
        "subject": "LinkSwiss — créer votre mot de passe",
        "body": (
            "Bonjour,\n\n"
            "Choisissez un mot de passe pour votre compte LinkSwiss :\n\n"
            "{url}\n\n"
            "Ce lien expire dans {minutes} minutes.\n\n"
            "Si vous n'avez pas demandé cela, ignorez ce message."
        ),
    },
    "de": {
        "subject": "LinkSwiss — Passwort festlegen",
        "body": (
            "Hallo,\n\n"
            "Legen Sie ein Passwort für Ihr LinkSwiss-Konto fest:\n\n"
            "{url}\n\n"
            "Dieser Link läuft in {minutes} Minuten ab.\n\n"
            "Falls Sie das nicht angefordert haben, ignorieren Sie diese E-Mail."
        ),
    },
    "es": {
        "subject": "LinkSwiss — crea tu contraseña",
        "body": (
            "Hola,\n\n"
            "Elige una contraseña para tu cuenta LinkSwiss:\n\n"
            "{url}\n\n"
            "Este enlace caduca en {minutes} minutos.\n\n"
            "Si no lo pediste, ignora este mensaje."
        ),
    },
    "pt": {
        "subject": "LinkSwiss — criar a sua palavra-passe",
        "body": (
            "Olá,\n\n"
            "Escolhe uma palavra-passe para a tua conta LinkSwiss:\n\n"
            "{url}\n\n"
            "Esta ligação expira em {minutes} minutos.\n\n"
            "Se não pediste isto, ignore esta mensagem."
        ),
    },
    "en": {
        "subject": "LinkSwiss — set your password",
        "body": (
            "Hello,\n\n"
            "Choose a password for your LinkSwiss account:\n\n"
            "{url}\n\n"
            "This link expires in {minutes} minutes.\n\n"
            "If you did not request this, please ignore this email."
        ),
    },
}


def format_login_email(locale: str, url: str, *, ttl_minutes: int) -> tuple[str, str]:
    lang = resolve_locale(locale)
    copy = _LOGIN_COPY[lang]
    body = copy["body"].format(url=url, minutes=ttl_minutes)
    return copy["subject"], body


def format_set_password_email(locale: str, url: str, *, ttl_minutes: int) -> tuple[str, str]:
    lang = resolve_locale(locale)
    copy = _SETPW_COPY[lang]
    body = copy["body"].format(url=url, minutes=ttl_minutes)
    return copy["subject"], body
