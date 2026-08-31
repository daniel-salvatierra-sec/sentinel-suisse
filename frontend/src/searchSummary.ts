import type {
  CountryCode,
  EmploymentType,
  ListingType,
  SearchQueryParams,
} from "./api";
import type { Messages } from "./i18n";
import { JOB_FIELDS, jobCategoryAncestors, type JobField } from "./jobTaxonomy";
import { isBorderQuery } from "./zoneCities";

type Query = {
  listing_type?: ListingType;
  location?: string;
  country?: CountryCode;
  price_min?: number;
  price_max?: number;
  rooms_min?: number;
  property_type?: SearchQueryParams["property_type"];
  has_parking?: boolean;
  is_under_construction?: boolean;
  job_category?: string;
  employment_type?: EmploymentType;
  workload_min?: number;
  workload_max?: number;
};

function formatChf(n: number): string {
  return new Intl.NumberFormat("de-CH", { maximumFractionDigits: 0 }).format(n);
}

function zoneLabel(t: Messages, country?: CountryCode): string {
  if (country === "FR") return t.zoneFR;
  if (country === "DE") return t.zoneDE;
  if (country === "IT") return t.zoneIT;
  return t.zoneCH;
}

function fieldLabel(t: Messages, field: JobField): string {
  const map: Record<JobField, string> = {
    it: t.jobCatIt,
    healthcare: t.jobCatHealthcare,
    construction: t.jobCatConstruction,
    hospitality: t.jobCatHospitality,
    admin: t.jobCatAdmin,
    finance: t.jobCatFinance,
    sales: t.jobCatSales,
    education: t.jobCatEducation,
    logistics: t.jobCatLogistics,
    watchmaking: t.jobCatWatchmaking,
    other: t.jobCatOther,
  };
  return map[field];
}

function slugLabel(t: Messages, raw: string): string {
  if ((JOB_FIELDS as readonly string[]).includes(raw)) {
    return fieldLabel(t, raw as JobField);
  }
  const roleKey = `jobRole_${raw}` as keyof Messages;
  const role = t[roleKey];
  if (typeof role === "string") return role;
  const branchKey = `jobBranch_${raw}` as keyof Messages;
  const branch = t[branchKey];
  if (typeof branch === "string") return branch;
  return raw;
}

function jobCategoryLabel(t: Messages, raw: string): string {
  const parts = [...jobCategoryAncestors(raw)].reverse().map((slug) => slugLabel(t, slug));
  parts.push(slugLabel(t, raw));
  return parts.join(" · ");
}

function employmentLabel(t: Messages, type: EmploymentType): string {
  const map: Record<EmploymentType, string> = {
    permanent: t.employmentPermanent,
    temporary: t.employmentTemporary,
    internship: t.employmentInternship,
    freelance: t.employmentFreelance,
    other: t.employmentOther,
  };
  return map[type];
}

/** Short human line of what a search/alert is looking for. */
export function formatSearchSummary(t: Messages, query: Query): string {
  const parts: string[] = [];

  if (query.listing_type === "job") {
    parts.push(t.searchKindJob);
    if (query.job_category) {
      parts.push(jobCategoryLabel(t, query.job_category));
    }
    if (query.employment_type) {
      parts.push(employmentLabel(t, query.employment_type));
    }
    if (query.workload_min === 40 && query.workload_max === 60) {
      parts.push(t.workload4060);
    } else if (query.workload_min === 80 && query.workload_max === 100) {
      parts.push(t.workload80100);
    } else if (query.workload_min != null) {
      parts.push(
        query.workload_max != null
          ? `${query.workload_min}–${query.workload_max}%`
          : `${query.workload_min}%`,
      );
    }
  } else {
    parts.push(t.searchKindHome);
    if (query.property_type === "studio") {
      parts.push(t.roomsStudio);
    } else if (query.rooms_min != null) {
      parts.push(t.searchRoomsN.replace("{n}", String(query.rooms_min)));
    }
    if (query.has_parking) {
      parts.push(t.parkingLabel);
    }
    if (query.is_under_construction) {
      parts.push(t.underConstructionFilter);
    }
    if (query.price_min != null) {
      parts.push(t.searchPriceMin.replace("{n}", formatChf(query.price_min)));
    }
    if (query.price_max != null) {
      parts.push(t.searchPriceMax.replace("{n}", formatChf(query.price_max)));
    }
  }

  const location = query.location?.trim();
  if (location) {
    parts.push(isBorderQuery(location) ? t.zoneBorder : location);
  }
  if (query.country && query.country !== "CH") {
    parts.push(zoneLabel(t, query.country));
  } else if (!location) {
    parts.push(t.zoneCH);
  }

  return parts.join(", ");
}

/** Drop paging and blank location so the API accepts the saved-search body. */
export function toSavedSearchQuery(
  query: Omit<SearchQueryParams, "limit" | "offset"> & {
    limit?: number;
    offset?: number;
    sort?: SearchQueryParams["sort"];
  },
): Omit<SearchQueryParams, "limit" | "offset" | "sort"> {
  const { limit: _limit, offset: _offset, sort: _sort, ...rest } = query;
  const location = rest.location?.trim();
  return {
    ...rest,
    location: location ? location : undefined,
  };
}
