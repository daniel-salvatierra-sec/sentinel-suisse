import { useEffect, useState, type FormEvent } from "react";
import {
  createSponsorCheckoutSession,
  fetchBillingConfig,
  fetchMySponsors,
  type SponsorAdOwner,
  type SponsorContext,
} from "../api";
import type { Messages } from "../i18n";

type Props = {
  t: Messages;
  refreshToken: number;
};

const CONTEXTS: SponsorContext[] = ["all", "housing", "job"];

function contextLabel(t: Messages, context: SponsorContext): string {
  if (context === "housing") return t.housing;
  if (context === "job") return t.job;
  return t.sponsorContextAll;
}

export function SponsorCheckoutForm({ t, refreshToken }: Props) {
  const [sponsorName, setSponsorName] = useState("");
  const [context, setContext] = useState<SponsorContext>("all");
  const [headline, setHeadline] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [targetUrl, setTargetUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enabled, setEnabled] = useState(false);
  const [days, setDays] = useState(30);
  const [mine, setMine] = useState<SponsorAdOwner[]>([]);

  useEffect(() => {
    let cancelled = false;
    void fetchBillingConfig()
      .then((cfg) => {
        if (cancelled) return;
        setEnabled(Boolean(cfg.sponsor_ads_enabled));
        if (cfg.sponsor_ad_days) setDays(cfg.sponsor_ad_days);
      })
      .catch(() => {
        if (!cancelled) setEnabled(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!enabled) {
      setMine([]);
      return;
    }
    void fetchMySponsors()
      .then(setMine)
      .catch(() => setMine([]));
  }, [enabled, refreshToken]);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const { checkout_url } = await createSponsorCheckoutSession({
        sponsor_name: sponsorName.trim(),
        context,
        headline: headline.trim() || undefined,
        image_url: imageUrl.trim() || undefined,
        target_url: targetUrl.trim(),
      });
      window.location.assign(checkout_url);
    } catch {
      setError(t.sponsorCheckoutError);
      setBusy(false);
    }
  };

  if (!enabled) {
    return null;
  }

  return (
    <section className="sponsor-checkout">
      <h3>{t.sponsorCheckoutTitle}</h3>
      <p className="plan-hint">{t.sponsorCheckoutHint.replace("{days}", String(days))}</p>
      <form onSubmit={(event) => void onSubmit(event)}>
        <label>
          {t.sponsorNameLabel}
          <input
            value={sponsorName}
            onChange={(event) => setSponsorName(event.target.value)}
            required
            minLength={2}
            maxLength={120}
          />
        </label>
        <label>
          {t.sponsorContextLabel}
          <select value={context} onChange={(event) => setContext(event.target.value as SponsorContext)}>
            {CONTEXTS.map((item) => (
              <option key={item} value={item}>
                {contextLabel(t, item)}
              </option>
            ))}
          </select>
        </label>
        <label>
          {t.sponsorHeadlineLabel}
          <input
            value={headline}
            onChange={(event) => setHeadline(event.target.value)}
            maxLength={160}
            placeholder={t.sponsorHeadlineOptional}
          />
        </label>
        <label>
          {t.sponsorImageLabel}
          <input
            type="url"
            value={imageUrl}
            onChange={(event) => setImageUrl(event.target.value)}
            placeholder="https://"
          />
        </label>
        <label>
          {t.sponsorTargetLabel}
          <input
            type="url"
            value={targetUrl}
            onChange={(event) => setTargetUrl(event.target.value)}
            required
            placeholder="https://"
          />
        </label>
        <p className="plan-hint">{t.sponsorCreativeHint}</p>
        {error ? <p className="alert-feedback error">{error}</p> : null}
        <button type="submit" className="apply-btn" disabled={busy} style={{ width: "100%" }}>
          {busy ? t.sponsorPaying : t.sponsorPayCta}
        </button>
      </form>

      {mine.length > 0 ? (
        <>
          <h4>{t.sponsorMineTitle}</h4>
          {mine.map((item) => (
            <article key={item.id} className="listing-card account-search">
              <h4>{item.sponsor_name}</h4>
              <div className="meta">
                {contextLabel(t, item.context as SponsorContext)}
                {item.payment_pending ? ` · ${t.sponsorPending}` : null}
                {item.is_active && item.ends_at
                  ? ` · ${t.sponsorUntil.replace("{date}", new Date(item.ends_at).toLocaleDateString())}`
                  : null}
              </div>
              <div className="meta">
                {t.sponsorStats
                  .replace("{impressions}", String(item.impression_count))
                  .replace("{clicks}", String(item.click_count))}
              </div>
            </article>
          ))}
        </>
      ) : null}
    </section>
  );
}
