from sentinel_suisse.i18n.premium import format_premium_welcome


def test_premium_welcome_copy_five_languages() -> None:
    subject, body = format_premium_welcome("es", "https://linkswiss.ch")
    assert "Ya eres Premium" in subject
    assert "Sentinela te avisa" in body
    assert "https://linkswiss.ch" in body

    fr_subject, _fr_body = format_premium_welcome("fr", "https://linkswiss.ch")
    assert "Ton Premium est actif" in fr_subject

    de_subject, _de_body = format_premium_welcome("de", "https://linkswiss.ch")
    assert "Dein Premium ist aktiv" in de_subject
