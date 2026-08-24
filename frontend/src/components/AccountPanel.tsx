import {
  clearApiKey,
  createPortalSession,
  deleteAccount,
  deleteSavedSearch,
  fetchAlerts,
  fetchMe,
  fetchSavedSearches,
  getApiKey,
  type AlertLog,
  type ListingType,
  type SavedSearch,
  type SearchQueryParams,
  type UserProfile,
} from "../api";
import { AlertSignup } from "./AlertSignup";
import { PremiumUpsell } from "./PremiumUpsell";
import type { Lang, Messages } from "../i18n";
import { useCallback, useEffect, useState } from "react";

type Props = {
  t: Messages;
  locale: Lang;
  listingType: ListingType;
  location: string;
  searchQuery?: Omit<SearchQueryParams, "limit" | "offset">;
  refreshToken: number;
  onSignupSuccess: () => void;
  onLoggedOut: () => void;
  onOpenPublish: () => void;
};

export function AccountPanel({
  t,
  locale,
  listingType,
  location,
  searchQuery,
  refreshToken,
  onSignupSuccess,
  onLoggedOut,
  onOpenPublish,
}: Props) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [alerts, setAlerts] = useState<AlertLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [portalBusy, setPortalBusy] = useState(false);
  const [portalError, setPortalError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!getApiKey()) {
      setLoading(false);
      setProfile(null);
      return;
    }
    setLoading(true);
    setError(false);
    try {
      const [me, saved, history] = await Promise.all([
        fetchMe(),
        fetchSavedSearches(),
        fetchAlerts(),
      ]);
      setProfile(me);
      setSearches(saved);
      setAlerts(history.slice(0, 10));
    } catch {
      setError(true);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load, refreshToken]);

  if (!getApiKey()) {
    return (
      <AlertSignup
        t={t}
        locale={locale}
        listingType={listingType}
        location={location}
        searchQuery={searchQuery}
        onSuccess={onSignupSuccess}
      />
    );
  }

  if (loading) {
    return <p className="empty">{t.loading}</p>;
  }

  if (error || !profile) {
    return <p className="empty alert-feedback error">{t.accountError}</p>;
  }

  const handleDeleteSearch = async (id: number) => {
    await deleteSavedSearch(id);
    setSearches((prev) => prev.filter((item) => item.id !== id));
  };

  const handleDeleteAccount = async () => {
    if (!confirmDelete) {
      setConfirmDelete(true);
      return;
    }
    await deleteAccount();
    clearApiKey();
    onLoggedOut();
  };

  const handleManageSubscription = async () => {
    setPortalBusy(true);
    setPortalError(null);
    try {
      const { portal_url } = await createPortalSession();
      window.location.assign(portal_url);
    } catch {
      setPortalError(t.premiumPortalError);
      setPortalBusy(false);
    }
  };

  return (
    <section className="account-panel">
      <h2 style={{ marginTop: 0 }}>{t.accountTitle}</h2>
      <p className="account-email">
        {profile.email} · {profile.locale.toUpperCase()}
        {" · "}
        <span className="plan-badge">
          {profile.is_premium ? t.premiumBadge : t.freeBadge}
        </span>
      </p>
      <p className="plan-hint">
        {t.alertQuota
          .replace("{count}", String(profile.saved_search_count ?? searches.length))
          .replace("{limit}", String(profile.saved_search_limit ?? 1))}
      </p>
      {profile.is_premium && (
        <>
          <button
            type="button"
            className="apply-btn"
            style={{ width: "100%", marginBottom: "0.75rem" }}
            disabled={portalBusy}
            onClick={() => void handleManageSubscription()}
          >
            {portalBusy ? t.premiumPaying : t.premiumManageCta}
          </button>
          {portalError && <p className="premium-upsell-error">{portalError}</p>}
        </>
      )}
      {(profile.saved_search_count ?? searches.length) >=
        (profile.saved_search_limit ?? 1) &&
        !profile.is_premium && (
          <>
            <p className="alert-feedback pending">{t.alertLimitReached}</p>
            <PremiumUpsell t={t} />
          </>
        )}

      {!profile.is_premium &&
        (profile.saved_search_count ?? searches.length) <
          (profile.saved_search_limit ?? 1) && (
          <p className="plan-hint">{t.searchFreeHint}</p>
        )}

      <button type="button" className="post-ad-link" onClick={onOpenPublish}>
        {t.postAdCta}
      </button>

      <h3>{t.accountSearches}</h3>
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
            <button type="button" className="danger-btn" onClick={() => void handleDeleteSearch(search.id)}>
              {t.accountDeleteSearch}
            </button>
          </article>
        ))
      )}

      <h3>{t.accountHistory}</h3>
      {alerts.length === 0 ? (
        <p className="empty">{t.accountNoAlerts}</p>
      ) : (
        alerts.map((alert) => (
          <article key={alert.id} className="listing-card account-alert">
            <div className="meta">
              #{alert.listing_id} · {alert.channel_type} · {alert.status}
            </div>
            <div className="meta">{new Date(alert.created_at).toLocaleString()}</div>
          </article>
        ))
      )}

      <button
        type="button"
        className="danger-btn"
        style={{ width: "100%", marginTop: "1rem" }}
        onClick={() => void handleDeleteAccount()}
      >
        {confirmDelete ? t.accountConfirmDelete : t.accountDelete}
      </button>
      {confirmDelete && (
        <p className="alert-feedback pending">{t.accountDeleteWarning}</p>
      )}
    </section>
  );
}
