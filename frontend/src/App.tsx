import { useCallback, useEffect, useState } from "react";
import {
  fetchProviders,
  getApiKey,
  SEARCH_PAGE_SIZE,
  searchListings,
  type Listing,
  type ListingType,
  type Provider,
} from "./api";
import { AccountPanel } from "./components/AccountPanel";
import { CategoryCards } from "./components/CategoryCards";
import { FilterBar } from "./components/FilterBar";
import { GuideBot } from "./components/GuideBot";
import { LanguageBar } from "./components/LanguageBar";
import { MapView } from "./components/MapView";
import { MyAlertsPanel } from "./components/MyAlertsPanel";
import { SearchBar } from "./components/SearchBar";
import { VerifyBanner } from "./components/VerifyBanner";
import { VirtualizedListingList } from "./components/VirtualizedListingList";
import { loadLang, messages, saveLang, type Lang } from "./i18n";
import { parseSubscribeDeepLink, stripSubscribeParamsFromUrl } from "./subscribeLink";

type Tab = "list" | "map" | "alerts" | "account";

function parseOptionalPrice(value: string): number | undefined {
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  const n = Number(trimmed);
  if (Number.isNaN(n) || n < 0) return undefined;
  return n;
}

export default function App() {
  const [lang, setLang] = useState<Lang>(loadLang);
  const [category, setCategory] = useState<ListingType>("housing");
  const [query, setQuery] = useState("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [appliedPriceMin, setAppliedPriceMin] = useState("");
  const [appliedPriceMax, setAppliedPriceMax] = useState("");
  const [providers, setProviders] = useState<Provider[]>([]);
  const [providerIds, setProviderIds] = useState<number[]>([]);
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState(false);
  const [tab, setTab] = useState<Tab>("list");
  const [focusId, setFocusId] = useState<number | null>(null);
  const [hasSession, setHasSession] = useState(() => Boolean(getApiKey()));
  const [accountRefresh, setAccountRefresh] = useState(0);
  const [deepLinkReady, setDeepLinkReady] = useState(false);

  const t = messages[lang];

  useEffect(() => {
    const deep = parseSubscribeDeepLink(window.location.search);
    if (deep.lang) {
      saveLang(deep.lang);
      setLang(deep.lang);
    }
    if (deep.listingType) {
      setCategory(deep.listingType);
    }
    if (deep.location != null) {
      setQuery(deep.location);
    }
    if (deep.tab === "account") {
      setTab("account");
    }
    if (deep.tab || deep.lang || deep.listingType || deep.location != null) {
      stripSubscribeParamsFromUrl();
    }
    setDeepLinkReady(true);
  }, []);

  useEffect(() => {
    void fetchProviders()
      .then(setProviders)
      .catch(() => setProviders([]));
  }, []);

  const runSearch = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const results = await searchListings({
        listing_type: category,
        location: query,
        price_min: category === "housing" ? parseOptionalPrice(appliedPriceMin) : undefined,
        price_max: category === "housing" ? parseOptionalPrice(appliedPriceMax) : undefined,
        provider_ids: providerIds.length ? providerIds : undefined,
        limit: SEARCH_PAGE_SIZE,
        offset: 0,
      });
      setListings(results);
      setHasMore(results.length >= SEARCH_PAGE_SIZE);
      setFocusId(results[0]?.id ?? null);
    } catch {
      setError(true);
      setListings([]);
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  }, [category, query, appliedPriceMin, appliedPriceMax, providerIds]);

  const loadMore = useCallback(async () => {
    setLoadingMore(true);
    setError(false);
    try {
      const results = await searchListings({
        listing_type: category,
        location: query,
        price_min: category === "housing" ? parseOptionalPrice(appliedPriceMin) : undefined,
        price_max: category === "housing" ? parseOptionalPrice(appliedPriceMax) : undefined,
        provider_ids: providerIds.length ? providerIds : undefined,
        limit: SEARCH_PAGE_SIZE,
        offset: listings.length,
      });
      setListings((prev) => [...prev, ...results]);
      setHasMore(results.length >= SEARCH_PAGE_SIZE);
    } catch {
      setError(true);
    } finally {
      setLoadingMore(false);
    }
  }, [category, query, appliedPriceMin, appliedPriceMax, providerIds, listings.length]);

  const applyFilters = () => {
    setAppliedPriceMin(priceMin);
    setAppliedPriceMax(priceMax);
  };

  useEffect(() => {
    if (!deepLinkReady) return;
    if (tab === "list" || tab === "map") {
      void runSearch();
    }
  }, [tab, category, runSearch, deepLinkReady]);

  const onSignupSuccess = () => {
    setHasSession(true);
    setAccountRefresh((value) => value + 1);
    setTab("account");
  };

  const onLoggedOut = () => {
    setHasSession(false);
    setTab("list");
  };

  return (
    <div className="app">
      <VerifyBanner
        t={t}
        onVerified={() => {
          setAccountRefresh((value) => value + 1);
          setTab("account");
        }}
      />
      <LanguageBar
        lang={lang}
        onChange={(code) => {
          saveLang(code);
          setLang(code);
        }}
      />
      <header className="hero">
        <h1>{t.appName}</h1>
        <p>{t.tagline}</p>
      </header>

      <CategoryCards t={t} active={category} onSelect={setCategory} />
      <SearchBar t={t} value={query} onChange={setQuery} onSearch={() => void runSearch()} />
      <FilterBar
        t={t}
        showPrice={category === "housing"}
        providers={providers}
        providerIds={providerIds}
        onProviderIdsChange={setProviderIds}
        priceMin={priceMin}
        priceMax={priceMax}
        onPriceMinChange={setPriceMin}
        onPriceMaxChange={setPriceMax}
        onApply={applyFilters}
      />

      <div className="tabs">
        <button type="button" className={tab === "list" ? "active" : ""} onClick={() => setTab("list")}>
          {t.list}
        </button>
        <button type="button" className={tab === "map" ? "active" : ""} onClick={() => setTab("map")}>
          {t.map}
        </button>
        <button type="button" className={tab === "alerts" ? "active" : ""} onClick={() => setTab("alerts")}>
          {t.alerts}
        </button>
        <button type="button" className={tab === "account" ? "active" : ""} onClick={() => setTab("account")}>
          {t.account}
          {hasSession && <span className="tab-dot" aria-hidden />}
        </button>
      </div>

      {loading && (tab === "list" || tab === "map") && <p className="empty">{t.loading}</p>}
      {error && (tab === "list" || tab === "map") && <p className="empty">{t.noResults}</p>}

      {tab === "map" && !loading && !error && listings.length > 0 && (
        <MapView listings={listings} focusId={focusId} searchQuery={query} />
      )}

      {tab === "list" && !loading && !error && (
        <>
          {listings.length === 0 ? (
            <p className="empty">{t.noResults}</p>
          ) : (
            <VirtualizedListingList
              listings={listings}
              t={t}
              focusId={focusId}
              onSelect={(id) => {
                setFocusId(id);
                setTab("map");
              }}
              hasMore={hasMore}
              loadingMore={loadingMore}
              onLoadMore={() => void loadMore()}
            />
          )}
        </>
      )}

      {tab === "alerts" && (
        <MyAlertsPanel
          t={t}
          locale={lang}
          listingType={category}
          location={query}
          refreshToken={accountRefresh}
          onGoToAccount={() => setTab("account")}
        />
      )}

      {tab === "account" && (
        <AccountPanel
          t={t}
          locale={lang}
          listingType={category}
          location={query}
          refreshToken={accountRefresh}
          onSignupSuccess={onSignupSuccess}
          onLoggedOut={onLoggedOut}
        />
      )}

      <div className="legal-links">
        <a className="privacy-link" href={`/api/v1/legal/privacy?lang=${lang}`} target="_blank" rel="noreferrer">
          {t.privacy}
        </a>
        <a className="privacy-link" href={`/api/v1/legal/terms?lang=${lang}`} target="_blank" rel="noreferrer">
          {t.terms}
        </a>
      </div>

      <GuideBot
        t={t}
        onPickCategory={(type) => {
          setCategory(type);
          setTab("list");
        }}
        onOpenAlerts={() => {
          setTab(hasSession ? "alerts" : "account");
        }}
        onStartSearch={(location) => {
          setQuery(location);
          setTab("list");
        }}
        onOpenMap={() => {
          setTab("map");
        }}
      />
    </div>
  );
}
