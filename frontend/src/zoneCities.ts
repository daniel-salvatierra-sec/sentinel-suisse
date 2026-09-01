import type { CityStock, CountryCode, ListingType } from "./api";
import { matchSwissCity, SWISS_CITIES } from "./swissCities";

/** Sentinel value for the first city-picker option in FR / DE / IT. */
export const BORDER_CITY = "__border__";

/** Towns in the Swiss-border belt — keep in sync with location_match.py */
export const FR_CITIES = [
  "Annemasse",
  "Gaillard",
  "Ferney-Voltaire",
  "Saint-Julien-en-Genevois",
  "Thonon-les-Bains",
  "Annecy",
  "Archamps",
] as const;
export const DE_CITIES = [
  "Lörrach",
  "Weil am Rhein",
  "Konstanz",
  "Waldshut-Tiengen",
] as const;
export const IT_CITIES = ["Como", "Varese", "Domodossola"] as const;

export function borderQuery(zone: CountryCode): string {
  return `${zone}-border`;
}

export function isBorderQuery(query: string): boolean {
  return /^(CH|FR|DE|IT)-border$/i.test(query.trim());
}

export function citiesForZone(zone: CountryCode): string[] {
  if (zone === "CH") {
    return [...SWISS_CITIES];
  }
  if (zone === "FR") {
    return [...FR_CITIES];
  }
  if (zone === "DE") {
    return [...DE_CITIES];
  }
  return [...IT_CITIES];
}

function fold(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

const CITY_ALIASES: Record<string, string> = {
  ferney: "Ferney-Voltaire",
  "ferney voltaire": "Ferney-Voltaire",
  "saint julien": "Saint-Julien-en-Genevois",
  "saint-julien": "Saint-Julien-en-Genevois",
  "st julien": "Saint-Julien-en-Genevois",
  thonon: "Thonon-les-Bains",
  lorrach: "Lörrach",
  constance: "Konstanz",
  waldshut: "Waldshut-Tiengen",
};

export function matchZoneCity(zone: CountryCode, query: string): string {
  const trimmed = query.trim();
  if (!trimmed || isBorderQuery(trimmed)) {
    return "";
  }
  if (zone === "CH") {
    return matchSwissCity(trimmed);
  }
  const folded = fold(trimmed);
  const inland: readonly string[] = citiesForZone(zone);
  const aliased = CITY_ALIASES[folded];
  if (aliased && inland.includes(aliased)) {
    return aliased;
  }
  const exact = inland.find((city) => fold(city) === folded);
  return exact ?? "";
}

export function queryForCityChoice(_zone: CountryCode, value: string): string {
  if (value === BORDER_CITY) {
    return "";
  }
  return value;
}

/** Picker values with stock for this zone and listing type. Null = catalog fallback. */
export function stockedPickerValues(
  zone: CountryCode,
  listingType: ListingType,
  stock: CityStock[] | null,
): string[] | null {
  if (stock == null) {
    return null;
  }
  const names: string[] = [];
  for (const row of stock) {
    if (row.country !== zone) {
      continue;
    }
    const count = listingType === "housing" ? row.housing_count : row.job_count;
    if (count <= 0) {
      continue;
    }
    if (row.city === `${zone}-border`) {
      continue;
    }
    names.push(row.city);
  }
  return names;
}

/** Empty neighbor-country search means the border belt, not the whole country. */
export function searchLocation(zone: CountryCode, query: string): string {
  const trimmed = query.trim();
  if (trimmed) {
    return isBorderQuery(trimmed) ? borderQuery(zone) : trimmed;
  }
  if (zone === "CH") {
    return "";
  }
  return borderQuery(zone);
}
