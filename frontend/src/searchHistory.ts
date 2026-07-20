import type { ListingType, SearchQueryParams } from "./api";

const STORAGE_KEY = "linkswiss-search-history";
const MAX_ITEMS = 8;

export type RememberedSearch = {
  id: string;
  savedAt: number;
  label: string;
  query: Omit<SearchQueryParams, "limit" | "offset">;
};

function labelFor(query: RememberedSearch["query"]): string {
  const kind = query.listing_type === "job" ? "job" : "housing";
  const where = query.location?.trim() || "—";
  return `${kind} · ${where}`;
}

export function loadSearchHistory(): RememberedSearch[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as RememberedSearch[];
    if (!Array.isArray(parsed)) return [];
    return parsed.slice(0, MAX_ITEMS);
  } catch {
    return [];
  }
}

export function rememberSearch(
  query: Omit<SearchQueryParams, "limit" | "offset">,
): RememberedSearch[] {
  const entry: RememberedSearch = {
    id: `${Date.now()}-${query.listing_type}-${query.location ?? ""}`,
    savedAt: Date.now(),
    label: labelFor(query),
    query: { ...query },
  };
  const prev = loadSearchHistory().filter((item) => {
    return !(
      item.query.listing_type === query.listing_type &&
      (item.query.location ?? "") === (query.location ?? "")
    );
  });
  const next = [entry, ...prev].slice(0, MAX_ITEMS);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next;
}

export function historyForType(
  items: RememberedSearch[],
  listingType: ListingType,
): RememberedSearch[] {
  return items.filter((item) => item.query.listing_type === listingType);
}
