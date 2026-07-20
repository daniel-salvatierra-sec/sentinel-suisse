import { useCallback, useEffect, useState } from "react";
import {
  getApiKey,
  SEARCH_PAGE_SIZE,
  searchListings,
  type EmploymentType,
  type Listing,
  type ListingType,
  type PropertyType,
  type SearchQueryParams,
} from "./api";
import { AccountPanel } from "./components/AccountPanel";
import {
  FilterBar,
  type RoomsChoice,
  type WorkloadChoice,
  type ZoneChoice,
} from "./components/FilterBar";
import { GoalHub } from "./components/GoalHub";
import { GuideBot } from "./components/GuideBot";
import { LanguageBar } from "./components/LanguageBar";
import { MapView } from "./components/MapView";
import { MyAlertsPanel } from "./components/MyAlertsPanel";
import { SearchBar } from "./components/SearchBar";
import { VerifyBanner } from "./components/VerifyBanner";
import { ShareAppButton } from "./components/ShareAppButton";
import { VirtualizedListingList } from "./components/VirtualizedListingList";
import { loadLang, messages, saveLang, type Lang } from "./i18n";
import { resolveJobCategory, type JobField } from "./jobTaxonomy";
import type { ListingSignalContext } from "./listingSignals";
import { parseSubscribeDeepLink, stripSubscribeParamsFromUrl } from "./subscribeLink";

type Tab = "list" | "map" | "alerts" | "account";

function parseOptionalPrice(value: string): number | undefined {
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  const n = Number(trimmed);
  if (Number.isNaN(n) || n < 0) return undefined;
  return n;
}

function roomsToFilters(choice: RoomsChoice): {
  rooms_min?: number;
  property_type?: PropertyType;
} {
  if (choice === "") return {};
  if (choice === "studio") return { property_type: "studio" };
  return { rooms_min: Number(choice) };
}

function workloadToFilters(choice: WorkloadChoice): {
  workload_min?: number;
  workload_max?: number;
} {
  if (choice === "40-60") return { workload_min: 40, workload_max: 60 };
  if (choice === "80-100") return { workload_min: 80, workload_max: 100 };
  return {};
}

export default function App() {
  const [lang, setLang] = useState<Lang>(loadLang);
  const [category, setCategory] = useState<ListingType>("housing");
  const [query, setQuery] = useState("");
  const [zoneChoice, setZoneChoice] = useState<ZoneChoice>("");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [roomsChoice, setRoomsChoice] = useState<RoomsChoice>("");
  const [hasParking, setHasParking] = useState(false);
  const [jobField, setJobField] = useState<JobField | "">("");
  const [jobBranch, setJobBranch] = useState("");
  const [employmentType, setEmploymentType] = useState<EmploymentType | "">("");
  const [workloadChoice, setWorkloadChoice] = useState<WorkloadChoice>("");
  const [appliedZoneChoice, setAppliedZoneChoice] = useState<ZoneChoice>("");
  const [appliedPriceMin, setAppliedPriceMin] = useState("");
  const [appliedPriceMax, setAppliedPriceMax] = useState("");
  const [appliedRoomsChoice, setAppliedRoomsChoice] = useState<RoomsChoice>("");
  const [appliedHasParking, setAppliedHasParking] = useState(false);
  const [appliedJobField, setAppliedJobField] = useState<JobField | "">("");
  const [appliedJobBranch, setAppliedJobBranch] = useState("");
  const [appliedEmploymentType, setAppliedEmploymentType] = useState<EmploymentType | "">("");
  const [appliedWorkloadChoice, setAppliedWorkloadChoice] = useState<WorkloadChoice>("");
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

  const signalContext: ListingSignalContext = (() => {
    const rooms = roomsToFilters(appliedRoomsChoice);
    const workload = workloadToFilters(appliedWorkloadChoice);
    return {
      searchQuery: query,
      priceMin: category === "housing" ? parseOptionalPrice(appliedPriceMin) : undefined,
      priceMax: category === "housing" ? parseOptionalPrice(appliedPriceMax) : undefined,
      roomsMin: category === "housing" ? rooms.rooms_min : undefined,
      hasParking: category === "housing" && appliedHasParking,
      jobField: category === "job" ? appliedJobField : "",
      jobBranch: category === "job" ? appliedJobBranch : "",
      employmentType: category === "job" ? appliedEmploymentType : "",
      workloadMin: category === "job" ? workload.workload_min : undefined,
      workloadMax: category === "job" ? workload.workload_max : undefined,
    };
  })();

  const buildSearchParams = useCallback(
    (offset: number): SearchQueryParams => {
      const rooms = roomsToFilters(appliedRoomsChoice);
      const workload = workloadToFilters(appliedWorkloadChoice);
      return {
        listing_type: category,
        location: query,
        country: appliedZoneChoice || undefined,
        price_min: category === "housing" ? parseOptionalPrice(appliedPriceMin) : undefined,
        price_max: category === "housing" ? parseOptionalPrice(appliedPriceMax) : undefined,
        rooms_min: category === "housing" ? rooms.rooms_min : undefined,
        property_type: category === "housing" ? rooms.property_type : undefined,
        has_parking: category === "housing" && appliedHasParking ? true : undefined,
        job_category:
          category === "job"
            ? resolveJobCategory(appliedJobField, appliedJobBranch)
            : undefined,
        employment_type:
          category === "job" && appliedEmploymentType ? appliedEmploymentType : undefined,
        workload_min: category === "job" ? workload.workload_min : undefined,
        workload_max: category === "job" ? workload.workload_max : undefined,
        limit: SEARCH_PAGE_SIZE,
        offset,
      };
    },
    [
      category,
      query,
      appliedZoneChoice,
      appliedPriceMin,
      appliedPriceMax,
      appliedRoomsChoice,
      appliedHasParking,
      appliedJobField,
      appliedJobBranch,
      appliedEmploymentType,
      appliedWorkloadChoice,
    ],
  );

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

  const runSearch = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const results = await searchListings(buildSearchParams(0));
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
  }, [buildSearchParams]);

  const loadMore = useCallback(async () => {
    setLoadingMore(true);
    setError(false);
    try {
      const results = await searchListings(buildSearchParams(listings.length));
      setListings((prev) => [...prev, ...results]);
      setHasMore(results.length >= SEARCH_PAGE_SIZE);
    } catch {
      setError(true);
    } finally {
      setLoadingMore(false);
    }
  }, [buildSearchParams, listings.length]);

  const applyFilters = () => {
    setAppliedZoneChoice(zoneChoice);
    setAppliedPriceMin(priceMin);
    setAppliedPriceMax(priceMax);
    setAppliedRoomsChoice(roomsChoice);
    setAppliedHasParking(hasParking);
    setAppliedJobField(jobField);
    setAppliedJobBranch(jobBranch);
    setAppliedEmploymentType(employmentType);
    setAppliedWorkloadChoice(workloadChoice);
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

  const alertQuery = buildSearchParams(0);

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
        <ShareAppButton t={t} />
      </header>

      <GoalHub
        t={t}
        active={category}
        onSelect={(type) => {
          setCategory(type);
          window.requestAnimationFrame(() => {
            document.getElementById("search-panel")?.scrollIntoView({
              behavior: "smooth",
              block: "start",
            });
          });
        }}
      />
      <SearchBar t={t} value={query} onChange={setQuery} onSearch={() => void runSearch()} />
      <FilterBar
        t={t}
        category={category}
        zoneChoice={zoneChoice}
        onZoneChoiceChange={setZoneChoice}
        roomsChoice={roomsChoice}
        onRoomsChoiceChange={setRoomsChoice}
        hasParking={hasParking}
        onHasParkingChange={setHasParking}
        priceMin={priceMin}
        priceMax={priceMax}
        onPriceMinChange={setPriceMin}
        onPriceMaxChange={setPriceMax}
        jobField={jobField}
        onJobFieldChange={setJobField}
        jobBranch={jobBranch}
        onJobBranchChange={setJobBranch}
        employmentType={employmentType}
        onEmploymentTypeChange={setEmploymentType}
        workloadChoice={workloadChoice}
        onWorkloadChoiceChange={setWorkloadChoice}
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
              signalContext={signalContext}
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
          searchQuery={alertQuery}
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
        zone={category}
        searching={loading || loadingMore}
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
