import type { CityStock, CountryCode, ListingType } from "./api";
import { matchSwissCity, SWISS_CITIES } from "./swissCities";

/** Sentinel value for the first city-picker option in FR / DE / IT. */
export const BORDER_CITY = "__border__";

/** City-proper population over 500,000 (INSEE / Destatis / Istat). */
export const FR_CITIES = ["Paris", "Marseille", "Lyon", "Toulouse"] as const;
export const DE_CITIES = [
  "Berlin",
  "Hamburg",
  "Munich",
  "Cologne",
  "Frankfurt",
  "Stuttgart",
  "Dusseldorf",
  "Leipzig",
  "Dortmund",
  "Essen",
  "Bremen",
  "Dresden",
  "Hanover",
  "Nuremberg",
  "Duisburg",
] as const;
export const IT_CITIES = ["Rome", "Milan", "Naples", "Turin", "Palermo", "Genoa"] as const;

export function borderQuery(zone: CountryCode): string {
  return `${zone}-border`;
}

export function isBorderQuery(query: string): boolean {
  return /^(CH|FR|DE|IT)-border$/i.test(query.trim());
}

export function citiesForZone(
  zone: CountryCode,
  listingType: ListingType = "job",
): string[] {
  if (zone === "CH") {
    return [...SWISS_CITIES];
  }
  // Inland FR/DE/IT rentals have no licensed source yet — only the Swiss-border belt.
  if (listingType === "housing") {
    return [BORDER_CITY];
  }
  if (zone === "FR") {
    return [BORDER_CITY, ...FR_CITIES];
  }
  if (zone === "DE") {
    return [BORDER_CITY, ...DE_CITIES];
  }
  return [BORDER_CITY, ...IT_CITIES];
}

function fold(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

const CITY_ALIASES: Record<string, string> = {
  paris: "Paris",
  parigi: "Paris",
  marseille: "Marseille",
  marsella: "Marseille",
  lyon: "Lyon",
  lione: "Lyon",
  toulouse: "Toulouse",
  tolosa: "Toulouse",
  berlin: "Berlin",
  berlijn: "Berlin",
  hamburg: "Hamburg",
  hambourg: "Hamburg",
  munich: "Munich",
  munchen: "Munich",
  monaco: "Munich",
  cologne: "Cologne",
  koln: "Cologne",
  colonia: "Cologne",
  frankfurt: "Frankfurt",
  stuttgart: "Stuttgart",
  dusseldorf: "Dusseldorf",
  dusseldof: "Dusseldorf",
  leipzig: "Leipzig",
  dortmund: "Dortmund",
  essen: "Essen",
  bremen: "Bremen",
  dresden: "Dresden",
  dresde: "Dresden",
  hanover: "Hanover",
  hannover: "Hanover",
  nuremberg: "Nuremberg",
  nurnberg: "Nuremberg",
  nuernberg: "Nuremberg",
  duisburg: "Duisburg",
  rome: "Rome",
  roma: "Rome",
  milan: "Milan",
  milano: "Milan",
  naples: "Naples",
  napoli: "Naples",
  napoles: "Naples",
  turin: "Turin",
  torino: "Turin",
  palermo: "Palermo",
  genoa: "Genoa",
  genova: "Genoa",
};

export function matchZoneCity(
  zone: CountryCode,
  query: string,
  listingType: ListingType = "job",
): string {
  const trimmed = query.trim();
  if (!trimmed) {
    return zone === "CH" ? "" : BORDER_CITY;
  }
  if (zone !== "CH" && isBorderQuery(trimmed)) {
    return BORDER_CITY;
  }
  if (zone === "CH") {
    return matchSwissCity(trimmed);
  }
  const folded = fold(trimmed);
  const aliased = CITY_ALIASES[folded];
  const catalog = citiesForZone(zone, listingType).filter((city) => city !== BORDER_CITY);
  if (aliased && catalog.includes(aliased)) {
    return aliased;
  }
  const exact = catalog.find((city) => fold(city) === folded);
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
    names.push(row.city === `${zone}-border` ? BORDER_CITY : row.city);
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
