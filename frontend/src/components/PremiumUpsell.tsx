import { useEffect, useState } from "react";
import {
  createCheckoutSession,
  fetchBillingConfig,
  getApiKey,
} from "../api";
import type { Messages } from "../i18n";
import { readStoredPromo } from "../promo";

type Props = {
  t: Messages;
  compact?: boolean;
};

/** Premium paywall — Stripe Checkout when configured and user is logged in. */
export function PremiumUpsell({ t, compact = false }: Props) {
  const [paymentsEnabled, setPaymentsEnabled] = useState(false);
  const [promoCode, setPromoCode] = useState<string | null>(null);
  const [promoPercent, setPromoPercent] = useState(50);
  const [promoMonths, setPromoMonths] = useState(3);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loggedIn = Boolean(getApiKey());

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

  const onPay = async () => {
    if (!loggedIn) {
      setError(t.premiumLoginFirst);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const { checkout_url } = await createCheckoutSession(promoCode);
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

  const offerTitle = t.premiumLaunchOfferTitle
    .replace("{percent}", String(promoPercent))
    .replace("{months}", String(promoMonths));

  return (
    <aside
      id="premium-paywall"
      className={`premium-upsell${compact ? " is-compact" : ""}`}
    >
      <h3 className="premium-upsell-title">{t.premiumUpsellTitle}</h3>
      <p className="premium-upsell-desc">{t.premiumUpsellDesc}</p>
      <ul className="premium-upsell-list">
        <li>{t.premiumBenefitJobs}</li>
        <li>{t.premiumBenefitHousing}</li>
        <li>{t.premiumBenefitDossier}</li>
        <li>{t.premiumBenefitConstruction}</li>
        <li>{t.premiumBenefitWhatsapp}</li>
      </ul>
      <p className="premium-upsell-price">{t.premiumUpsellPrice}</p>
      {promoCode || paymentsEnabled ? (
        <p className="premium-launch-badge" role="status">
          {offerTitle}
        </p>
      ) : null}
      <p className="premium-upsell-promo">
        {promoCode
          ? t.premiumPromoHintWithCode.replace("{code}", promoCode)
          : t.premiumPromoHint}
      </p>
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
