import type { EmploymentType, Listing } from "./api";
import type { JobField } from "./jobTaxonomy";

export type ListingSignalContext = {
  searchQuery: string;
  priceMin?: number;
  priceMax?: number;
  roomsMin?: number;
  hasParking: boolean;
  jobField: JobField | "";
  jobBranch: string;
  employmentType: EmploymentType | "";
  workloadMin?: number;
  workloadMax?: number;
};

export type ListingSignals = {
  goodPrice: boolean;
  goodMatch: boolean;
};

function pricedSorted(listings: Listing[]): number[] {
  return listings
    .filter((item) => item.listing_type === "housing" && item.price != null)
    .map((item) => Number(item.price))
    .filter((price) => Number.isFinite(price))
    .sort((a, b) => a - b);
}

/** Bottom third of current result prices, or ≤85% of price_max when few samples. */
export function isGoodPrice(
  listing: Listing,
  listings: Listing[],
  ctx: ListingSignalContext,
): boolean {
  if (listing.listing_type !== "housing" || listing.price == null) return false;
  const price = Number(listing.price);
  if (!Number.isFinite(price)) return false;

  const prices = pricedSorted(listings);
  if (prices.length >= 3) {
    const cutoff = prices[Math.floor((prices.length - 1) / 3)]!;
    return price <= cutoff;
  }
  if (ctx.priceMax != null) {
    return price <= ctx.priceMax * 0.85;
  }
  if (ctx.priceMin != null) {
    return price <= ctx.priceMin * 1.1;
  }
  return false;
}

function locationMatches(listing: Listing, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q || !listing.location) return false;
  return listing.location.toLowerCase().includes(q);
}

function jobExactMatch(listing: Listing, ctx: ListingSignalContext): boolean {
  const cat = listing.job_category;
  if (!cat || !ctx.jobBranch) return false;
  return cat === ctx.jobBranch;
}

function workloadFits(listing: Listing, ctx: ListingSignalContext): boolean {
  if (ctx.workloadMin == null && ctx.workloadMax == null) return false;
  if (listing.workload_min == null && listing.workload_max == null) return false;
  const fMin = ctx.workloadMin ?? 0;
  const fMax = ctx.workloadMax ?? 100;
  const lMin = listing.workload_min ?? 0;
  const lMax = listing.workload_max ?? 100;
  return lMin >= fMin && lMax <= fMax;
}

/** Stronger-than-filter cues: query hit, exact specialty, parking, rooms, workload. */
export function isGoodMatch(listing: Listing, ctx: ListingSignalContext): boolean {
  if (locationMatches(listing, ctx.searchQuery)) return true;

  if (listing.listing_type === "housing") {
    if (ctx.hasParking && listing.has_parking === true) return true;
    if (
      ctx.roomsMin != null &&
      listing.rooms != null &&
      Number(listing.rooms) >= ctx.roomsMin
    ) {
      return true;
    }
    return false;
  }

  if (jobExactMatch(listing, ctx)) return true;
  if (ctx.employmentType && listing.employment_type === ctx.employmentType) return true;
  if (workloadFits(listing, ctx)) return true;
  return false;
}

export function computeListingSignals(
  listing: Listing,
  listings: Listing[],
  ctx: ListingSignalContext,
): ListingSignals {
  return {
    goodPrice: isGoodPrice(listing, listings, ctx),
    goodMatch: isGoodMatch(listing, ctx),
  };
}
