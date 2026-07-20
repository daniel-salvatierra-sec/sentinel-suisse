import { useEffect, useState } from "react";
import {
  createCheckoutSession,
  fetchBillingConfig,
  getApiKey,
} from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  compact?: boolean;
};

/** Premium paywall — Stripe Checkout when configured and user is logged in. */
export function PremiumUpsell({ t, compact = false }: Props) {
  const [paymentsEnabled, setPaymentsEnabled] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loggedIn = Boolean(getApiKey());

  useEffect(() => {
    let cancelled = false;
    void fetchBillingConfig()
      .then((cfg) => {
        if (!cancelled) setPaymentsEnabled(cfg.payments_enabled);
      })
      .catch(() => {
        if (!cancelled) setPaymentsEnabled(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const onPay = async () => {
    if (!loggedIn) {
      setError(t.premiumLoginFirst);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const { checkout_url } = await createCheckoutSession();
      window.location.assign(checkout_url);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "checkout_failed";
      if (msg === "payments_disabled" || msg.includes("503")) {
        setError(t.premiumComingSoon);
      } else {
        setError(t.premiumCheckoutError);
      }
      setBusy(false);
    }
  };

  const canPay = paymentsEnabled && loggedIn;
  const label = canPay
    ? busy
      ? t.premiumPaying
      : t.premiumPayCta
    : paymentsEnabled
      ? t.premiumLoginFirst
      : t.premiumComingSoon;

  return (
    <aside className={`premium-upsell${compact ? " is-compact" : ""}`}>
      {!compact && <h3 className="premium-upsell-title">{t.premiumUpsellTitle}</h3>}
      <p className="premium-upsell-desc">{t.premiumUpsellDesc}</p>
      <ul className="premium-upsell-list">
        <li>{t.premiumBenefitJobs}</li>
        <li>{t.premiumBenefitHousing}</li>
        <li>{t.premiumBenefitConstruction}</li>
        <li>{t.premiumBenefitWhatsapp}</li>
      </ul>
      <p className="premium-upsell-price">{t.premiumUpsellPrice}</p>
      <button
        type="button"
        className="apply-btn"
        disabled={!canPay || busy}
        title={label}
        onClick={() => void onPay()}
      >
        {label}
      </button>
      {error && <p className="premium-upsell-error">{error}</p>}
      <p className="premium-upsell-refund">
        <a href="/api/v1/legal/refunds" target="_blank" rel="noreferrer">
          {t.premiumRefundsLink}
        </a>
      </p>
    </aside>
  );
}
