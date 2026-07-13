# Datenschutzerklärung — Sentinel Suisse

**Version:** 2026-07-13  
**Status:** Persönliches Projekt / Vorproduktion (Entwurf — vor öffentlichem Start rechtlich prüfen)

## 1. Verantwortliche Stelle

Sentinel Suisse (persönliches Projekt)  
Datenschutz-Kontakt: privacy@sentinel-suisse.example *(vor Produktion ersetzen)*

## 2. Erhobene Personendaten

| Daten | Zweck |
|-------|-------|
| E-Mail-Adresse | Benutzerkonto, API-Authentifizierung, E-Mail-Benachrichtigungen |
| Kanaladresse (E-Mail oder WhatsApp-Telefon) | Zustellung von Alerts über den gewählten Kanal |
| Gespeicherte Suchkriterien | Abgleich mit aggregierten Inseraten |
| Alert-Protokolle (Status, Zeitstempel) | Nachweis der Zustellung, Fehleranalyse — **ohne Nachrichteninhalt** |

Aggregierte Inserate stammen aus öffentlichen Drittquellen; Alert-Inhalte enthalten keine zusätzlichen sensiblen Daten.

## 3. Rechtsgrundlage (nDSG / nLPD)

- **Alert-Dienst:** Vertragserfüllung / berechtigtes Interesse mit ausdrücklicher Einwilligung (Registrierung und Kanalverifizierung).
- **Inserat-Aggregation:** öffentliche Drittdaten; Verlinkung zur Originalquelle.

## 4. Aufbewahrungsdauer

| Daten | Dauer |
|-------|-------|
| Konto und Kanäle | Bis zur Kontolöschung |
| Gespeicherte Suchen | Bis zur Löschung durch den Nutzer oder mit dem Konto |
| `raw_payload` der Inserate | Maximal 30 Tage (automatische Wartungsaufgabe) |
| Alert-Protokolle | Werden mit dem Konto kaskadiert gelöscht |

## 5. Sicherheit

- Verschlüsselung at rest (Fernet) für E-Mail und Kanaladressen.
- Admin-Passwörter gehasht (bcrypt); API-Schlüssel gehasht — niemals im Klartext gespeichert.
- API in der Entwicklungsphase auf `127.0.0.1` beschränkt.

## 6. Auftragsbearbeiter und Übermittlungen

Je nach Konfiguration: SMTP-Anbieter (z. B. Mailtrap in der Entwicklung), WhatsApp Cloud API (Meta), Datenbank-Hosting. Keine Übermittlung ausserhalb der Schweiz/des EWR ohne vorherige Information.

## 7. Ihre Rechte

Sie haben insbesondere Rechte auf **Auskunft**, **Berichtigung** und **Löschung** gemäss nDSG.

**Kontolöschung (Recht auf Vergessenwerden):**

```http
DELETE /api/v1/users/me
X-API-Key: <Ihr API-Schlüssel>
```

Die Löschung ist **unwiderruflich** und entfernt kaskadiert Kanäle, gespeicherte Suchen und zugehörige Alert-Protokolle.

Anfragen an: privacy@sentinel-suisse.example

## 8. Änderungen

Diese Erklärung kann aktualisiert werden; Version und Datum stehen oben und über die API `GET /api/v1/legal/privacy?lang=de`.
