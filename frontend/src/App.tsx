import { useCallback, useEffect, useState } from "react";
import { searchListings, type Listing, type ListingType } from "./api";
import { AlertSignup } from "./components/AlertSignup";
import { CategoryCards } from "./components/CategoryCards";
import { GuideBot } from "./components/GuideBot";
import { LanguageBar } from "./components/LanguageBar";
import { ListingCard } from "./components/ListingCard";
import { MapView } from "./components/MapView";
import { SearchBar } from "./components/SearchBar";
import { loadLang, messages, saveLang, type Lang } from "./i18n";

type ViewMode = "map" | "list";

export default function App() {
  const [lang, setLang] = useState<Lang>(loadLang);
  const [category, setCategory] = useState<ListingType>("housing");
  const [query, setQuery] = useState("");
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [view, setView] = useState<ViewMode>("list");
  const [focusId, setFocusId] = useState<number | null>(null);
  const [showAlerts, setShowAlerts] = useState(false);

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
    void runSearch();
  }, [category, runSearch]);

  return (
    <div className="app">
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
        <button type="button" className={view === "list" ? "active" : ""} onClick={() => setView("list")}>
          {t.list}
        </button>
        <button type="button" className={view === "map" ? "active" : ""} onClick={() => setView("map")}>
          {t.map}
        </button>
        <button type="button" className={showAlerts ? "active" : ""} onClick={() => setShowAlerts((v) => !v)}>
          {t.alerts}
        </button>
      </div>

      {loading && <p className="empty">{t.loading}</p>}
      {error && <p className="empty">{t.noResults}</p>}

      {!loading && !error && view === "map" && listings.length > 0 && (
        <MapView listings={listings} focusId={focusId} />
      )}

      {!loading && !error && view === "list" && (
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
                  setView("map");
                }}
              />
            ))
          )}
        </>
      )}

      {(showAlerts) && (
        <AlertSignup t={t} listingType={category} location={query} />
      )}

      <a className="privacy-link" href={`/api/v1/legal/privacy?lang=${lang}`} target="_blank" rel="noreferrer">
        {t.privacy}
      </a>

      <GuideBot
        t={t}
        onPickCategory={(type) => {
          setCategory(type);
          setShowAlerts(false);
        }}
        onOpenAlerts={() => {
          setShowAlerts(true);
          document.getElementById("alerts")?.scrollIntoView({ behavior: "smooth" });
        }}
      />
    </div>
  );
}
