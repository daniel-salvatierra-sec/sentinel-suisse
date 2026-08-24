import { useCallback, useEffect, useState } from "react";
import {
  createSavedSearch,
  deleteSavedSearch,
  fetchSavedSearches,
  getApiKey,
  type Listing,
  type ListingType,
  type SavedSearch,
  type SearchQueryParams,
} from "../api";
import { formatSearchSummary, toSavedSearchQuery } from "../searchSummary";
import type { Lang, Messages } from "../i18n";
import {
  historyForType,
  loadSearchHistory,
  type RememberedSearch,
} from "../searchHistory";
import { AlertSignup } from "./AlertSignup";
import { ListingCard } from "./ListingCard";
import { PremiumUpsell } from "./PremiumUpsell";
import { SentinelFace } from "./SentinelBuddy";

type Props = {
  t: Messages;
  locale: Lang;
  listingType: ListingType;
  location: string;
  searchQuery: Omit<SearchQueryParams, "limit" | "offset">;
  previewListings: Listing[];
  previewLoading: boolean;
  refreshToken: number;
  onPickCategory: (type: ListingType) => void;
  onApplyRemembered: (query: RememberedSearch["query"]) => void;
  onSignupSuccess: () => void;
  onGoToAccount: () => void;
  onOpenListing: (id: number) => void;
};

const PREVIEW_LIMIT = 5;

export function MyAlertsPanel({
  t,
  locale,
  listingType,
  location,
  searchQuery,
  previewListings,
  previewLoading,
  refreshToken,
  onPickCategory,
  onApplyRemembered,
  onSignupSuccess,
  onGoToAccount,
  onOpenListing,
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
  const currentLabel = formatSearchSummary(t, searchQuery);

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
        query: toSavedSearchQuery(searchQuery),
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

      <div className="alerts-current-box" id="alerts-create">
        <h3 className="alerts-subhead">{t.alertsCreateFromSearch}</h3>
        <p className="alerts-current-detail">{currentLabel}</p>
        <h4 className="alerts-preview-title">{t.alertsPreviewTitle}</h4>
        {previewLoading ? (
          <p className="empty">{t.loading}</p>
        ) : previewListings.length === 0 ? (
          <p className="empty">{t.alertsPreviewEmpty}</p>
        ) : (
          <div className="alerts-preview-list">
            {previewListings.slice(0, PREVIEW_LIMIT).map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                t={t}
                selected={false}
                onSelect={() => onOpenListing(listing.id)}
                onShowOnMap={() => onOpenListing(listing.id)}
              />
            ))}
          </div>
        )}
        <button
          type="button"
          className="apply-btn"
          style={{ width: "100%" }}
          disabled={saving}
          onClick={() => void saveCurrent()}
        >
          {saving ? t.loading : getApiKey() ? t.alertsSaveCurrent : t.alertsGuestCta}
        </button>
        {saveOk && <p className="alert-feedback success">{t.alertSuccess}</p>}
        {saveError && <p className="alert-feedback error">{saveError}</p>}
      </div>

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
                  {formatSearchSummary(t, item.query)}
                </button>
              </li>
            ))}
          </ul>
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
                <div className="meta">{formatSearchSummary(t, search.query)}</div>
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
