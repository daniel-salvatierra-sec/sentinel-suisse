import { useState } from "react";
import { formatFullPhone } from "../countryCodes";
import { subscribeAlerts, type ListingType } from "../api";
import { CountryCodePicker } from "./CountryCodePicker";
import { SubscribeQr } from "./SubscribeQr";
import type { Lang, Messages } from "../i18n";

type Props = {
  t: Messages;
  locale: Lang;
  listingType: ListingType;
  location: string;
  onSuccess?: () => void;
  showHeader?: boolean;
};

type Status = "idle" | "loading" | "success" | "pending" | "error";

export function AlertSignup({
  t,
  locale,
  listingType,
  location,
  onSuccess,
  showHeader = true,
}: Props) {
  const [dial, setDial] = useState("+41");
  const [phoneLocal, setPhoneLocal] = useState("");
  const [email, setEmail] = useState("");
  const [consent, setConsent] = useState(false);
  const [status, setStatus] = useState<Status>("idle");
  const [pendingWhatsApp, setPendingWhatsApp] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const fullPhone = formatFullPhone(dial, phoneLocal);

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
        phone: fullPhone || undefined,
        locale,
        listing_type: listingType,
        location,
      });
      if (result.verification_email_sent || result.verification_pending) {
        setPendingWhatsApp(Boolean(result.whatsapp_verification_sent));
        setStatus("pending");
      } else {
        setPendingWhatsApp(false);
        setStatus("success");
      }
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
    <section className="alert-panel" id="signup">
      {showHeader && (
        <>
          <h2 style={{ marginTop: 0 }}>{t.accountSignupTitle}</h2>
          <p>{t.accountSignupDesc}</p>
        </>
      )}
      {phoneLocal.trim() && (
        <p className="whatsapp-hint">{t.whatsappVerifyHint}</p>
      )}
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
      <CountryCodePicker
        lang={locale}
        t={t}
        dial={dial}
        local={phoneLocal}
        onDialChange={setDial}
        onLocalChange={setPhoneLocal}
      />
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
        {status === "loading" ? t.loading : t.accountSignupCta}
      </button>
      {status === "success" && (
        <p className="alert-feedback success">{t.alertSuccess}</p>
      )}
      {status === "pending" && (
        <>
          <p className="alert-feedback pending">{t.alertCheckEmail}</p>
          {pendingWhatsApp && (
            <p className="alert-feedback pending">{t.alertCheckWhatsapp}</p>
          )}
        </>
      )}
      {status === "error" && errorMessage && (
        <p className="alert-feedback error">{errorMessage}</p>
      )}
      <SubscribeQr t={t} lang={locale} listingType={listingType} location={location} />
    </section>
  );
}
