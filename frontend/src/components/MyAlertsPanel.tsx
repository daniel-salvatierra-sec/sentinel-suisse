import { useCallback, useEffect, useState } from "react";
import {
  deleteSavedSearch,
  fetchSavedSearches,
  getApiKey,
  type ListingType,
  type SavedSearch,
} from "../api";
import type { Lang, Messages } from "../i18n";
import { SubscribeQr } from "./SubscribeQr";

type Props = {
  t: Messages;
  locale: Lang;
  listingType: ListingType;
  location: string;
  refreshToken: number;
  onGoToAccount: () => void;
};

export function MyAlertsPanel({
  t,
  locale,
  listingType,
  location,
  refreshToken,
  onGoToAccount,
}: Props) {
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!getApiKey()) {
      setLoading(false);
      setSearches([]);
      return;
    }
    setLoading(true);
    try {
      setSearches(await fetchSavedSearches());
    } catch {
      setSearches([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, refreshToken]);

  if (!getApiKey()) {
    return (
      <section className="alert-panel">
        <h2 style={{ marginTop: 0 }}>{t.alertsTitle}</h2>
        <p>{t.alertsGoToAccount}</p>
        <button type="button" className="primary-btn" style={{ width: "100%" }} onClick={onGoToAccount}>
          {t.accountSignupCta}
        </button>
        <SubscribeQr t={t} lang={locale} listingType={listingType} location={location} />
      </section>
    );
  }

  if (loading) {
    return <p className="empty">{t.loading}</p>;
  }

  return (
    <section className="alert-panel">
      <h2 style={{ marginTop: 0 }}>{t.alertsMyPreferences}</h2>
      {searches.length === 0 ? (
        <p className="empty">{t.accountNoSearches}</p>
      ) : (
        searches.map((search) => (
          <article key={search.id} className="listing-card account-search">
            <h4>{search.name}</h4>
            <div className="meta">
              {String(search.query.listing_type ?? "—")}
              {search.query.location ? ` · ${search.query.location}` : ""}
            </div>
            <button
              type="button"
              className="danger-btn"
              onClick={() => void deleteSavedSearch(search.id).then(load)}
            >
              {t.accountDeleteSearch}
            </button>
          </article>
        ))
      )}
    </section>
  );
}
