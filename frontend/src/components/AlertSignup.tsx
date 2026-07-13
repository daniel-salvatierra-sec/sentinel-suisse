import { useState } from "react";
import { subscribeAlerts, type ListingType } from "../api";
import type { Lang, Messages } from "../i18n";

type Props = {
  t: Messages;
  locale: Lang;
  listingType: ListingType;
  location: string;
  id?: string;
  onSuccess?: () => void;
};

type Status = "idle" | "loading" | "success" | "pending" | "error";

export function AlertSignup({ t, locale, listingType, location, id = "alerts", onSuccess }: Props) {
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [consent, setConsent] = useState(false);
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async () => {
    if (!email.trim()) {
      setErrorMessage(t.emailRequired);
      setStatus("error");
      return;
    }
    if (!consent) {
      setErrorMessage(t.consentRequired);
      setStatus("error");
      return;
    }

    setStatus("loading");
    setErrorMessage("");
    try {
      const result = await subscribeAlerts({
        email: email.trim(),
        phone: phone.trim() || undefined,
        locale,
        listing_type: listingType,
        location,
      });
      setStatus(result.verification_pending ? "pending" : "success");
      onSuccess?.();
    } catch (error) {
      const message = error instanceof Error ? error.message : "";
      setErrorMessage(
        message.includes("already exists") ? t.alertErrorDuplicate : t.alertErrorGeneric,
      );
      setStatus("error");
    }
  };

  return (
    <section className="alert-panel" id={id}>
      <h2 style={{ marginTop: 0 }}>{t.alertsTitle}</h2>
      <p>{t.alertsDesc}</p>
      <div className="qr-placeholder" aria-hidden>
        QR
        <br />
        WhatsApp
      </div>
      <label>
        {t.email}
        <input
          type="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="you@example.com"
        />
      </label>
      <label>
        {t.phone}
        <input
          type="tel"
          value={phone}
          onChange={(event) => setPhone(event.target.value)}
          placeholder="+41 79 …"
        />
      </label>
      <label className="consent-row">
        <input
          type="checkbox"
          checked={consent}
          onChange={(event) => setConsent(event.target.checked)}
        />
        <span>{t.consentLabel}</span>
      </label>
      <button
        type="button"
        className="primary-btn"
        style={{ width: "100%" }}
        disabled={status === "loading"}
        onClick={() => void handleSubmit()}
      >
        {status === "loading" ? t.loading : t.saveSearch}
      </button>
      {status === "success" && (
        <p className="alert-feedback success">{t.alertSuccess}</p>
      )}
      {status === "pending" && (
        <p className="alert-feedback pending">{t.alertPending}</p>
      )}
      {status === "error" && errorMessage && (
        <p className="alert-feedback error">{errorMessage}</p>
      )}
    </section>
  );
}
