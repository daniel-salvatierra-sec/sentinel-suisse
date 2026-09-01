import { useState } from "react";
import { subscribeAlerts, type ListingType, type SearchQueryParams } from "../api";
import { CountryCodePicker } from "./CountryCodePicker";
import { LoginPanel } from "./LoginPanel";
import { PremiumUpsell } from "./PremiumUpsell";
import { SubscribeQr } from "./SubscribeQr";
import type { Lang, Messages } from "../i18n";

type Props = {
  t: Messages;
  locale: Lang;
  listingType: ListingType;
  location: string;
  searchQuery?: Omit<SearchQueryParams, "limit" | "offset">;
  onSuccess?: () => void;
  showHeader?: boolean;
  /** Account tab defaults to login so returning users see Se connecter first. */
  initialMode?: "login" | "signup";
};

type Status = "idle" | "loading" | "success" | "pending" | "error";

export function AlertSignup({
  t,
  locale,
  listingType,
  location,
  searchQuery,
  onSuccess,
  showHeader = true,
  initialMode = "signup",
}: Props) {
  const [dial, setDial] = useState("+41");
  const [phoneLocal, setPhoneLocal] = useState("");
  const [email, setEmail] = useState("");
  const [consent, setConsent] = useState(false);
  const [status, setStatus] = useState<Status>("idle");
  const [pendingWhatsApp, setPendingWhatsApp] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [mode, setMode] = useState<"login" | "signup">(initialMode);
  const [isDuplicate, setIsDuplicate] = useState(false);

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
    setIsDuplicate(false);
    try {
      // Free tier: email only — never send phone on public signup.
      const result = await subscribeAlerts({
        email: email.trim(),
        locale,
        query: searchQuery ?? {
          listing_type: listingType,
          location,
        },
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
      if (message.includes("whatsapp_requires_premium")) {
        setErrorMessage(t.premiumWhatsapp);
      } else if (message.includes("saved_search_limit")) {
        setErrorMessage(t.alertLimitReached);
      } else if (message.includes("already exists")) {
        setErrorMessage(t.alertErrorDuplicate);
        setIsDuplicate(true);
      } else {
        setErrorMessage(t.alertErrorGeneric);
      }
      setStatus("error");
    }
  };

  return (
    <section className="alert-panel" id="signup">
      <div className="account-auth-tabs" role="tablist" aria-label={t.accountAuthTabsLabel}>
        <button
          type="button"
          role="tab"
          aria-selected={mode === "login"}
          className={mode === "login" ? "account-auth-tab is-active" : "account-auth-tab"}
          onClick={() => setMode("login")}
        >
          {t.loginTitle}
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={mode === "signup"}
          className={mode === "signup" ? "account-auth-tab is-active" : "account-auth-tab"}
          onClick={() => setMode("signup")}
        >
          {t.accountSignupTab}
        </button>
      </div>

      {mode === "login" ? (
        <>
          <LoginPanel t={t} locale={locale} />
          <p className="plan-hint login-stay-hint">{t.loginStayHint}</p>
        </>
      ) : (
        <>
          {showHeader && (
            <>
              <h2 className="account-signup-heading">{t.accountSignupTitle}</h2>
              <p>{t.accountSignupDesc}</p>
            </>
          )}
          <p className="plan-hint">{t.searchFreeHint}</p>
          <p className="plan-hint">{t.freePlanHint}</p>
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
          <div className="premium-channel-block">
            <p className="premium-channel-label">
              {t.phone} <span className="listing-demo-badge">{t.premiumBadge}</span>
            </p>
            <p className="whatsapp-hint">{t.premiumWhatsapp}</p>
            <CountryCodePicker
              lang={locale}
              t={t}
              dial={dial}
              local={phoneLocal}
              onDialChange={setDial}
              onLocalChange={setPhoneLocal}
              disabled
            />
          </div>
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
            <p className="alert-feedback success">
              {t.alertSuccess} {t.alertSavedNeedPremium}
            </p>
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
            <p className="alert-feedback error">
              {errorMessage}
              {isDuplicate && (
                <>
                  {" "}
                  <button type="button" className="linkish" onClick={() => setMode("login")}>
                    {t.loginCta}
                  </button>
                </>
              )}
            </p>
          )}
          <PremiumUpsell t={t} compact />
          <SubscribeQr t={t} lang={locale} listingType={listingType} location={location} />
        </>
      )}
    </section>
  );
}
