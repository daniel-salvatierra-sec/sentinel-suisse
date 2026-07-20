import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  compact?: boolean;
};

/** Premium paywall teaser — Stripe/TWINT checkout comes in Phase B. */
export function PremiumUpsell({ t, compact = false }: Props) {
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
      <button type="button" className="apply-btn" disabled title={t.premiumComingSoon}>
        {t.premiumComingSoon}
      </button>
    </aside>
  );
}
