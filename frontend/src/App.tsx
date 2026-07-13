import { useCallback, useEffect, useState } from "react";
import { getApiKey, searchListings, type Listing, type ListingType } from "./api";
import { AccountPanel } from "./components/AccountPanel";
import { AlertSignup } from "./components/AlertSignup";
import { CategoryCards } from "./components/CategoryCards";
import { GuideBot } from "./components/GuideBot";
import { LanguageBar } from "./components/LanguageBar";
import { ListingCard } from "./components/ListingCard";
import { MapView } from "./components/MapView";
import { SearchBar } from "./components/SearchBar";
import { VerifyBanner } from "./components/VerifyBanner";
import { loadLang, messages, saveLang, type Lang } from "./i18n";

type Tab = "list" | "map" | "alerts" | "account";

export default function App() {
  const [lang, setLang] = useState<Lang>(loadLang);
  const [category, setCategory] = useState<ListingType>("housing");
  const [query, setQuery] = useState("");
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [tab, setTab] = useState<Tab>("list");
  const [focusId, setFocusId] = useState<number | null>(null);
  const [hasSession, setHasSession] = useState(() => Boolean(getApiKey()));
  const [accountRefresh, setAccountRefresh] = useState(0);

  const t = messages[lang];

  const runSearch = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const results = await searchListings({ listing_type: category, location: query });
      setListings(results);
      setFocusId(results[0]?.id ?? null);
    } catch {
      setError(true);
      setListings([]);
    } finally {
      setLoading(false);
    }
  }, [category, query]);

  useEffect(() => {
    if (tab === "list" || tab === "map") {
      void runSearch();
    }
  }, [tab, category, runSearch]);

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
        <MapView listings={listings} focusId={focusId} />
      )}

      {tab === "list" && !loading && !error && (
        <>
          {listings.length === 0 ? (
            <p className="empty">{t.noResults}</p>
          ) : (
            listings.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                t={t}
                selected={listing.id === focusId}
                onSelect={() => {
                  setFocusId(listing.id);
                  setTab("map");
                }}
              />
            ))
          )}
        </>
      )}

      {tab === "alerts" && (
        <AlertSignup
          t={t}
          locale={lang}
          listingType={category}
          location={query}
          onSuccess={onSignupSuccess}
        />
      )}

      {tab === "account" && (
        <AccountPanel t={t} refreshToken={accountRefresh} onLoggedOut={onLoggedOut} />
      )}

      <a className="privacy-link" href={`/api/v1/legal/privacy?lang=${lang}`} target="_blank" rel="noreferrer">
        {t.privacy}
      </a>

      <GuideBot
        t={t}
        onPickCategory={(type) => {
          setCategory(type);
          setTab("list");
        }}
        onOpenAlerts={() => {
          setTab("alerts");
          document.getElementById("alerts")?.scrollIntoView({ behavior: "smooth" });
        }}
      />
    </div>
  );
}
