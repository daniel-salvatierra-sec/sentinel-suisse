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
import { DoorLinks } from "./components/DoorLinks";
import {
  FilterBar,
  type RoomsChoice,
  type WorkloadChoice,
  type ZoneChoice,
} from "./components/FilterBar";
import { GoalHub } from "./components/GoalHub";
import { GuideBot } from "./components/GuideBot";
import { LanguageBar } from "./components/LanguageBar";
import { LoginBanner } from "./components/LoginBanner";
import { MapView } from "./components/MapView";
import { MyAlertsPanel } from "./components/MyAlertsPanel";
import { PostListingForm } from "./components/PostListingForm";
import { SearchBar } from "./components/SearchBar";
import { VerifyBanner } from "./components/VerifyBanner";
import { InstallAppButton } from "./components/InstallAppButton";
import { ShareAppButton } from "./components/ShareAppButton";
import { VirtualizedListingList } from "./components/VirtualizedListingList";
import { loadLang, messages, saveLang, type Lang } from "./i18n";
import { resolveJobCategory, type JobField } from "./jobTaxonomy";
import type { ListingSignalContext } from "./listingSignals";
import { parseSubscribeDeepLink, stripSubscribeParamsFromUrl } from "./subscribeLink";
import { rememberSearch } from "./searchHistory";
import type { RememberedSearch } from "./searchHistory";
import { matchSwissCity } from "./swissCities";
import { toSavedSearchQuery } from "./searchSummary";

type Tab = "list" | "map" | "alerts" | "account" | "publish";

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
  const [hubFocused, setHubFocused] = useState(false);
  const [query, setQuery] = useState("");
  const [zoneChoice, setZoneChoice] = useState<ZoneChoice>("CH");
  const [priceMin, setPriceMin] = useState("");
  const [priceMax, setPriceMax] = useState("");
  const [roomsChoice, setRoomsChoice] = useState<RoomsChoice>("");
  const [hasParking, setHasParking] = useState(false);
  const [underConstruction, setUnderConstruction] = useState(false);
  const [jobField, setJobField] = useState<JobField | "">("");
  const [jobBranch, setJobBranch] = useState("");
  const [jobRole, setJobRole] = useState("");
  const [employmentType, setEmploymentType] = useState<EmploymentType | "">("");
  const [workloadChoice, setWorkloadChoice] = useState<WorkloadChoice>("");
  const [appliedZoneChoice, setAppliedZoneChoice] = useState<ZoneChoice>("CH");
  const [appliedPriceMin, setAppliedPriceMin] = useState("");
  const [appliedPriceMax, setAppliedPriceMax] = useState("");
  const [appliedRoomsChoice, setAppliedRoomsChoice] = useState<RoomsChoice>("");
  const [appliedHasParking, setAppliedHasParking] = useState(false);
  const [appliedUnderConstruction, setAppliedUnderConstruction] = useState(false);
  const [appliedJobField, setAppliedJobField] = useState<JobField | "">("");
  const [appliedJobBranch, setAppliedJobBranch] = useState("");
  const [appliedJobRole, setAppliedJobRole] = useState("");
  const [appliedEmploymentType, setAppliedEmploymentType] = useState<EmploymentType | "">("");
  const [appliedWorkloadChoice, setAppliedWorkloadChoice] = useState<WorkloadChoice>("");
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [error, setError] = useState(false);
  const [tab, setTab] = useState<Tab>("list");
  const [focusId, setFocusId] = useState<number | null>(null);
  // True when the user explicitly asked to see ONE listing on the map (vs. browsing
  // the map tab freely) — in that case we show only that listing's pin, not every result.
  const [mapIsolate, setMapIsolate] = useState(false);
  const [hasSession, setHasSession] = useState(() => Boolean(getApiKey()));
  const [accountRefresh, setAccountRefresh] = useState(0);
  const [deepLinkReady, setDeepLinkReady] = useState(false);
  const [premiumBanner, setPremiumBanner] = useState<"success" | "cancel" | null>(null);

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
      jobRole: category === "job" ? appliedJobRole : "",
      employmentType: category === "job" ? appliedEmploymentType : "",
      workloadMin: category === "job" ? workload.workload_min : undefined,
      workloadMax: category === "job" ? workload.workload_max : undefined,
    };
  })();

  const buildSearchParams = useCallback(
    (offset: number, source: "applied" | "live" = "applied"): SearchQueryParams => {
      const live = source === "live";
      const rooms = roomsToFilters(live ? roomsChoice : appliedRoomsChoice);
      const workload = workloadToFilters(live ? workloadChoice : appliedWorkloadChoice);
      const zone = live ? zoneChoice : appliedZoneChoice;
      const pMin = live ? priceMin : appliedPriceMin;
      const pMax = live ? priceMax : appliedPriceMax;
      const parking = live ? hasParking : appliedHasParking;
      const construction = live ? underConstruction : appliedUnderConstruction;
      const field = live ? jobField : appliedJobField;
      const branch = live ? jobBranch : appliedJobBranch;
      const role = live ? jobRole : appliedJobRole;
      const emp = live ? employmentType : appliedEmploymentType;
      return {
        listing_type: category,
        location: query,
        country: zone,
        price_min: category === "housing" ? parseOptionalPrice(pMin) : undefined,
        price_max: category === "housing" ? parseOptionalPrice(pMax) : undefined,
        rooms_min: category === "housing" ? rooms.rooms_min : undefined,
        property_type: category === "housing" ? rooms.property_type : undefined,
        has_parking: category === "housing" && parking ? true : undefined,
        is_under_construction:
          category === "housing" && construction ? true : undefined,
        job_category:
          category === "job" ? resolveJobCategory(field, branch, role) : undefined,
        employment_type: category === "job" && emp ? emp : undefined,
        workload_min: category === "job" ? workload.workload_min : undefined,
        workload_max: category === "job" ? workload.workload_max : undefined,
        limit: SEARCH_PAGE_SIZE,
        offset,
      };
    },
    [
      category,
      query,
      zoneChoice,
      priceMin,
      priceMax,
      roomsChoice,
      hasParking,
      underConstruction,
      jobField,
      jobBranch,
      jobRole,
      employmentType,
      workloadChoice,
      appliedZoneChoice,
      appliedPriceMin,
      appliedPriceMax,
      appliedRoomsChoice,
      appliedHasParking,
      appliedUnderConstruction,
      appliedJobField,
      appliedJobBranch,
      appliedJobRole,
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
      setHubFocused(true);
    }
    if (deep.location != null) {
      setQuery(deep.location);
    }
    if (deep.tab === "account") {
      setTab("account");
    }
    const params = new URLSearchParams(window.location.search);
    const premium = params.get("premium");
    if (premium === "success" || premium === "cancel") {
      setPremiumBanner(premium);
      if (premium === "success") {
        setTab("account");
        setAccountRefresh((value) => value + 1);
      }
      params.delete("premium");
      const next = params.toString();
      const path = window.location.pathname;
      window.history.replaceState({}, "", next ? `${path}?${next}` : path);
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
      const params = buildSearchParams(0, tab === "alerts" ? "live" : "applied");
      const results = await searchListings(params);
      setListings(results);
      setHasMore(results.length >= SEARCH_PAGE_SIZE);
      setFocusId(results[0]?.id ?? null);
      if (tab !== "alerts") {
        const { limit: _l, offset: _o, ...remembered } = params;
        rememberSearch(remembered);
      }
    } catch {
      setError(true);
      setListings([]);
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  }, [buildSearchParams, tab]);

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
    setAppliedUnderConstruction(underConstruction);
    setAppliedJobField(jobField);
    setAppliedJobBranch(jobBranch);
    setAppliedJobRole(jobRole);
    setAppliedEmploymentType(employmentType);
    setAppliedWorkloadChoice(workloadChoice);
  };

  useEffect(() => {
    if (!deepLinkReady) return;
    if (tab === "list" || tab === "map" || tab === "alerts") {
      void runSearch();
    }
  }, [tab, category, query, runSearch, deepLinkReady]);

  const onSignupSuccess = () => {
    setHasSession(true);
    setAccountRefresh((value) => value + 1);
    setTab("alerts");
  };

  const onLoggedOut = () => {
    setHasSession(false);
    setTab("list");
  };

  const goToSearch = (type: ListingType, opts?: { scroll?: boolean }) => {
    setCategory(type);
    setHubFocused(true);
    setTab("list");
    if (opts?.scroll === false) return;
    window.setTimeout(() => {
      document.getElementById("search-panel")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 80);
  };

  const openAlerts = (type?: ListingType) => {
    if (type) {
      setCategory(type);
      setHubFocused(true);
    }
    applyFilters();
    setTab("alerts");
    window.setTimeout(() => {
      const target =
        document.getElementById("signup") ?? document.getElementById("alerts-create");
      target?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 160);
  };

  const applyRememberedSearch = (saved: RememberedSearch["query"]) => {
    setCategory(saved.listing_type);
    setHubFocused(true);
    setQuery(saved.location ?? "");
    if (
      saved.country === "CH" ||
      saved.country === "FR" ||
      saved.country === "DE" ||
      saved.country === "IT"
    ) {
      setZoneChoice(saved.country);
      setAppliedZoneChoice(saved.country);
    } else {
      setZoneChoice("CH");
      setAppliedZoneChoice("CH");
    }
    setTab("list");
  };

  const alertQuery = toSavedSearchQuery(buildSearchParams(0, "live"));

  return (
    <div className="app">
      <VerifyBanner
        t={t}
        onVerified={() => {
          setAccountRefresh((value) => value + 1);
          setTab("account");
        }}
      />
      <LoginBanner
        t={t}
        onLoggedIn={() => {
          setHasSession(true);
          setAccountRefresh((value) => value + 1);
          setTab("account");
        }}
      />
      {premiumBanner && (
        <div
          className={`premium-return-banner is-${premiumBanner}`}
          role="status"
        >
          <p>
            {premiumBanner === "success"
              ? t.premiumSuccessBanner
              : t.premiumCancelBanner}
          </p>
          <button
            type="button"
            className="linkish"
            onClick={() => setPremiumBanner(null)}
          >
            ×
          </button>
        </div>
      )}
      <div className="app-topbar">
        <LanguageBar
          lang={lang}
          onChange={(code) => {
            saveLang(code);
            setLang(code);
          }}
        />
        <button
          type="button"
          className={`account-top-btn${tab === "account" ? " is-active" : ""}`}
          onClick={() => {
            setTab("account");
            window.requestAnimationFrame(() => {
              document.getElementById("tabs-panel")?.scrollIntoView({
                behavior: "smooth",
                block: "start",
              });
            });
          }}
        >
          {t.account}
          {hasSession && <span className="tab-dot" aria-hidden />}
        </button>
      </div>
      <header className="hero">
        <h1>{t.appName}</h1>
        <p>{t.tagline}</p>
        <div className="hero-actions">
          <ShareAppButton t={t} />
          <InstallAppButton t={t} />
        </div>
      </header>

      <GoalHub
        t={t}
        active={category}
        focused={hubFocused}
        onSelect={(type) => {
          setHubFocused(true);
          if (tab === "publish") {
            setCategory(type);
            return;
          }
          goToSearch(type, { scroll: false });
        }}
      />
      <DoorLinks
        t={t}
        showSearch={tab === "account" || tab === "alerts" || tab === "publish"}
        showPublish={tab !== "publish" && tab !== "account"}
        onSearchHome={() => goToSearch("housing")}
        onSearchWork={() => goToSearch("job")}
        onPublish={() => setTab(hasSession ? "publish" : "account")}
      />
      {tab !== "publish" && tab !== "account" ? (
        <div id="search-panel">
          <SearchBar t={t} value={query} onChange={setQuery} onSearch={() => void runSearch()} />
          <FilterBar
            t={t}
            category={category}
            zoneChoice={zoneChoice}
            onZoneChoiceChange={(value) => {
              setZoneChoice(value);
              setAppliedZoneChoice(value);
              if (value !== "CH") {
                setQuery("");
              }
            }}
            cityChoice={matchSwissCity(query)}
            onCityChoiceChange={(value) => {
              setQuery(value);
            }}
            roomsChoice={roomsChoice}
            onRoomsChoiceChange={(value) => {
              setRoomsChoice(value);
              setAppliedRoomsChoice(value);
            }}
            hasParking={hasParking}
            onHasParkingChange={(value) => {
              setHasParking(value);
              setAppliedHasParking(value);
            }}
            underConstruction={underConstruction}
            onUnderConstructionChange={(value) => {
              setUnderConstruction(value);
              setAppliedUnderConstruction(value);
            }}
            priceMin={priceMin}
            priceMax={priceMax}
            onPriceMinChange={setPriceMin}
            onPriceMaxChange={setPriceMax}
            jobField={jobField}
            onJobFieldChange={(value) => {
              setJobField(value);
              setAppliedJobField(value);
              setJobRole("");
              setAppliedJobRole("");
            }}
            jobBranch={jobBranch}
            onJobBranchChange={(value) => {
              setJobBranch(value);
              setAppliedJobBranch(value);
              setJobRole("");
              setAppliedJobRole("");
            }}
            jobRole={jobRole}
            onJobRoleChange={(value) => {
              setJobRole(value);
              setAppliedJobRole(value);
            }}
            employmentType={employmentType}
            onEmploymentTypeChange={(value) => {
              setEmploymentType(value);
              setAppliedEmploymentType(value);
            }}
            workloadChoice={workloadChoice}
            onWorkloadChoiceChange={(value) => {
              setWorkloadChoice(value);
              setAppliedWorkloadChoice(value);
            }}
            onApply={applyFilters}
          />
        </div>
      ) : null}

      {tab === "publish" ? (
        <button type="button" className="post-ad-back" onClick={() => setTab("list")}>
          {t.postAdBack}
        </button>
      ) : null}

      <div className="tabs" id="tabs-panel">
        <button type="button" className={tab === "list" ? "active" : ""} onClick={() => setTab("list")}>
          {t.list}
        </button>
        <button
          type="button"
          className={tab === "map" ? "active" : ""}
          onClick={() => {
            setMapIsolate(false);
            setTab("map");
          }}
        >
          {t.map}
        </button>
        <button type="button" className={tab === "alerts" ? "active" : ""} onClick={() => setTab("alerts")}>
          {t.alerts}
        </button>
      </div>

      {loading && (tab === "list" || tab === "map") && <p className="empty">{t.loading}</p>}
      {error && (tab === "list" || tab === "map") && <p className="empty">{t.noResults}</p>}

      {tab === "map" && !loading && !error && listings.length > 0 && (
        <MapView
          listings={
            mapIsolate && focusId != null
              ? listings.filter((listing) => listing.id === focusId)
              : listings
          }
          focusId={focusId}
          searchQuery={query}
          t={t}
          onSelect={setFocusId}
        />
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
                setMapIsolate(true);
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
          searchQuery={alertQuery}
          previewListings={listings}
          previewLoading={loading}
          refreshToken={accountRefresh}
          onPickCategory={(type) => {
            setCategory(type);
            setHubFocused(true);
          }}
          onApplyRemembered={applyRememberedSearch}
          onSignupSuccess={onSignupSuccess}
          onGoToAccount={() => setTab("account")}
          onOpenListing={(id) => {
            setFocusId(id);
            setMapIsolate(true);
            setTab("map");
          }}
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
          onOpenPublish={() => setTab(hasSession ? "publish" : "account")}
          onSearchHome={() => goToSearch("housing")}
          onSearchWork={() => goToSearch("job")}
        />
      )}

      {tab === "publish" && (
        <PostListingForm t={t} listingType={category} />
      )}

      <div className="legal-links">
        <a className="privacy-link" href={`/api/v1/legal/privacy?lang=${lang}`} target="_blank" rel="noreferrer">
          {t.privacy}
        </a>
        <a className="privacy-link" href={`/api/v1/legal/terms?lang=${lang}`} target="_blank" rel="noreferrer">
          {t.terms}
        </a>
        <a className="privacy-link" href="/api/v1/legal/mentions-legales" target="_blank" rel="noreferrer">
          {t.mentionsLegales}
        </a>
      </div>

      <GuideBot
        t={t}
        lang={lang}
        zone={category}
        searching={loading || loadingMore}
        searchTab={tab === "list" || tab === "map"}
        hasSession={hasSession}
        onPickCategory={(type) => {
          setCategory(type);
          setHubFocused(true);
          setTab("list");
        }}
        onOpenAlerts={(type) => openAlerts(type)}
        onStartSearch={(location) => {
          setQuery(location);
          setTab("list");
        }}
        onOpenMap={() => {
          setTab("map");
        }}
        onOpenAccount={() => openAlerts()}
        onOpenPublish={() => setTab(hasSession ? "publish" : "account")}
      />
    </div>
  );
}
