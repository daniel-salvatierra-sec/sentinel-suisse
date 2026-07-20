import { useCallback, useEffect, useState } from "react";
import {
  createSavedSearch,
  deleteSavedSearch,
  fetchSavedSearches,
  getApiKey,
  type ListingType,
  type SavedSearch,
  type SearchQueryParams,
} from "../api";
import type { Lang, Messages } from "../i18n";
import {
  historyForType,
  loadSearchHistory,
  type RememberedSearch,
} from "../searchHistory";
import { AlertSignup } from "./AlertSignup";
import { PremiumUpsell } from "./PremiumUpsell";
import { SentinelFace } from "./SentinelBuddy";

type Props = {
  t: Messages;
  locale: Lang;
  listingType: ListingType;
  location: string;
  searchQuery: Omit<SearchQueryParams, "limit" | "offset">;
  refreshToken: number;
  onPickCategory: (type: ListingType) => void;
  onApplyRemembered: (query: RememberedSearch["query"]) => void;
  onSignupSuccess: () => void;
  onGoToAccount: () => void;
};

export function MyAlertsPanel({
  t,
  locale,
  listingType,
  location,
  searchQuery,
  refreshToken,
  onPickCategory,
  onApplyRemembered,
  onSignupSuccess,
  onGoToAccount,
}: Props) {
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [history, setHistory] = useState<RememberedSearch[]>(() => loadSearchHistory());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveOk, setSaveOk] = useState(false);

  const load = useCallback(async () => {
    setHistory(loadSearchHistory());
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

  const recent = historyForType(history, listingType);
  const currentLabel =
    listingType === "job"
      ? `${t.job} · ${location.trim() || "—"}`
      : `${t.housing} · ${location.trim() || "—"}`;

  const saveCurrent = async () => {
    if (!getApiKey()) {
      document.getElementById("signup")?.scrollIntoView({ behavior: "smooth" });
      return;
    }
    setSaving(true);
    setSaveError(null);
    setSaveOk(false);
    try {
      await createSavedSearch({
        name: currentLabel.slice(0, 120),
        query: searchQuery,
      });
      setSaveOk(true);
      await load();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "";
      if (msg.includes("saved_search_limit")) {
        setSaveError(t.alertLimitReached);
      } else {
        setSaveError(t.alertErrorGeneric);
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="alert-panel">
      <h2 style={{ marginTop: 0 }}>{t.alertsTitle}</h2>
      <p className="plan-hint">{t.searchFreeHint}</p>
      <p>{t.alertsRememberHint}</p>

      <div className="alerts-robot-ask">
        <span className="guide-avatar sentinel-avatar" aria-hidden>
          <SentinelFace size={32} />
        </span>
        <p className="alerts-robot-msg">{t.alertsAskType}</p>
      </div>

      <div className="alerts-type-row">
        <button
          type="button"
          className={`option${listingType === "housing" ? " is-selected" : ""}`}
          onClick={() => onPickCategory("housing")}
        >
          {t.housing}
        </button>
        <button
          type="button"
          className={`option${listingType === "job" ? " is-selected" : ""}`}
          onClick={() => onPickCategory("job")}
        >
          {t.job}
        </button>
      </div>

      <div className="alerts-current-box">
        <h3 className="alerts-subhead">{t.alertsCreateFromSearch}</h3>
        <p className="meta">{currentLabel}</p>
        <button
          type="button"
          className="apply-btn"
          style={{ width: "100%" }}
          disabled={saving}
          onClick={() => void saveCurrent()}
        >
          {saving ? t.loading : getApiKey() ? t.alertsSaveCurrent : t.accountSignupCta}
        </button>
        {saveOk && <p className="alert-feedback success">{t.alertSuccess}</p>}
        {saveError && <p className="alert-feedback error">{saveError}</p>}
      </div>

      {recent.length > 0 && (
        <div className="alerts-history">
          <h3 className="alerts-subhead">{t.alertsRecentSearches}</h3>
          <ul className="alerts-history-list">
            {recent.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className="alerts-history-item"
                  onClick={() => onApplyRemembered(item.query)}
                >
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {!getApiKey() && (
        <div className="alerts-signup-wrap">
          <AlertSignup
            t={t}
            locale={locale}
            listingType={listingType}
            location={location}
            searchQuery={searchQuery}
            onSuccess={onSignupSuccess}
            showHeader
          />
        </div>
      )}

      {getApiKey() && (
        <>
          <h3 className="alerts-subhead">{t.alertsMyPreferences}</h3>
          {loading ? (
            <p className="empty">{t.loading}</p>
          ) : searches.length === 0 ? (
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
          <button type="button" className="secondary-btn" onClick={onGoToAccount}>
            {t.viewAccount}
          </button>
          <PremiumUpsell t={t} compact />
        </>
      )}
    </section>
  );
}
