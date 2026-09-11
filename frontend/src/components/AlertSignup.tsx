import { useEffect, useState } from "react";
import {
  createCheckoutSession,
  fetchBillingConfig,
  subscribeAlerts,
  type ListingType,
  type SearchQueryParams,
} from "../api";
import { CountryCodePicker } from "./CountryCodePicker";
import { LoginPanel } from "./LoginPanel";
import { readStoredPromo } from "../promo";
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

/**
 * Only Premium inscription: email + WhatsApp phone, then Stripe checkout
 * with the launch promo (−50% for 3 months when configured).
 * Searching the app stays free with no account.
 */
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
  const [errorMessage, setErrorMessage] = useState("");
  const [mode, setMode] = useState<"login" | "signup">(initialMode);
  const [isDuplicate, setIsDuplicate] = useState(false);
  const [promoCode, setPromoCode] = useState<string | null>(null);
  const [promoPercent, setPromoPercent] = useState(50);
  const [promoMonths, setPromoMonths] = useState(3);
  const [paymentsEnabled, setPaymentsEnabled] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void fetchBillingConfig()
      .then((cfg) => {
        if (cancelled) return;
        setPaymentsEnabled(cfg.payments_enabled);
        const fromApi = cfg.launch_promo_code?.trim() || null;
        const fromLink = readStoredPromo();
        setPromoCode(fromLink || fromApi);
        if (cfg.launch_promo_percent != null) setPromoPercent(cfg.launch_promo_percent);
        if (cfg.launch_promo_months != null) setPromoMonths(cfg.launch_promo_months);
      })
      .catch(() => {
        if (!cancelled) setPaymentsEnabled(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const offerTitle = t.premiumLaunchOfferTitle
    .replace("{percent}", String(promoPercent))
    .replace("{months}", String(promoMonths));

  const fullPhone = () => {
    const local = phoneLocal.replace(/\D/g, "");
    if (!local) return undefined;
    return `${dial}${local}`;
  };

  const handleSubmit = async () => {
    if (!email.trim()) {
      setErrorMessage(t.emailRequired);
      setStatus("error");
      return;
    }
    if (!phoneLocal.replace(/\D/g, "")) {
      setErrorMessage(t.phoneRequired);
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
      const result = await subscribeAlerts({
        email: email.trim(),
        phone: fullPhone(),
        locale,
        query: searchQuery ?? {
          listing_type: listingType,
          location,
        },
      });
      onSuccess?.();

      if (paymentsEnabled) {
        try {
          const { checkout_url } = await createCheckoutSession(promoCode);
          window.location.assign(checkout_url);
          return;
        } catch {
          setErrorMessage(t.premiumCheckoutError);
          setStatus("error");
          return;
        }
      }

      if (result.verification_email_sent || result.verification_pending) {
        setStatus("pending");
      } else {
        setStatus("success");
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "";
      if (message.includes("already exists")) {
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
              <p className="premium-launch-badge" role="status">
                {offerTitle}
              </p>
              <p>{t.accountSignupDesc}</p>
            </>
          )}
          <p className="plan-hint">{t.searchFreeHint}</p>
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
            <p className="premium-channel-label">{t.phone}</p>
            <p className="whatsapp-hint">{t.premiumWhatsapp}</p>
            <CountryCodePicker
              lang={locale}
              t={t}
              dial={dial}
              local={phoneLocal}
              onDialChange={setDial}
              onLocalChange={setPhoneLocal}
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
            <p className="alert-feedback success">{t.premiumComingSoon}</p>
          )}
          {status === "pending" && (
            <p className="alert-feedback pending">{t.alertCheckEmail}</p>
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
          <p className="premium-upsell-price">{t.premiumUpsellPrice}</p>
          {promoCode ? (
            <p className="premium-upsell-promo">
              {t.premiumPromoHintWithCode.replace("{code}", promoCode)}
            </p>
          ) : null}
        </>
      )}
    </section>
  );
}
