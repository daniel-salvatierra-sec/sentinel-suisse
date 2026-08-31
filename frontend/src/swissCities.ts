/** Swiss cities shown when the user picks Switzerland. Values match location search. */
export const SWISS_CITIES = [
  "Geneva",
  "Zurich",
  "Bern",
  "Basel",
  "Lausanne",
  "Lugano",
  "Lucerne",
  "St. Gallen",
  "Winterthur",
  "Fribourg",
  "Neuchatel",
  "La Chaux-de-Fonds",
  "Biel",
  "Zug",
  "Sion",
  "Chur",
  "Bellinzona",
  "Schaffhausen",
  "Thun",
  "Aarau",
  "Nyon",
  "Morges",
  "Vevey",
  "Montreux",
  "Yverdon",
  "Bulle",
  "Martigny",
  "Sierre",
  "Monthey",
  "Delemont",
  "Olten",
  "Baden",
  "Wil",
  "Uster",
  "Frauenfeld",
  "Solothurn",
  "Langenthal",
  "Interlaken",
  "Liestal",
  "Kreuzlingen",
  "Locarno",
  "Mendrisio",
  "Chiasso",
  "Brig",
  "Schwyz",
  "Emmen",
  "Dietikon",
  "Horgen",
] as const;

export type SwissCity = (typeof SWISS_CITIES)[number];

function foldCity(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{M}/gu, "");
}

const CITY_ALIASES: Record<string, SwissCity> = {
  geneve: "Geneva",
  genf: "Geneva",
  ginebra: "Geneva",
  ginevra: "Geneva",
  zurich: "Zurich",
  zurigo: "Zurich",
  berne: "Bern",
  berna: "Bern",
  bale: "Basel",
  basilea: "Basel",
  losanna: "Lausanne",
  luzern: "Lucerne",
  lucerna: "Lucerne",
  "st gallen": "St. Gallen",
  "sankt gallen": "St. Gallen",
  "saint-gall": "St. Gallen",
  "san galo": "St. Gallen",
  freiburg: "Fribourg",
  friburgo: "Fribourg",
  neuenburg: "Neuchatel",
  "chaux-de-fonds": "La Chaux-de-Fonds",
  "la chaux-de-fonds": "La Chaux-de-Fonds",
  bienne: "Biel",
  "biel/bienne": "Biel",
  zoug: "Zug",
  zugo: "Zug",
  sitten: "Sion",
  coire: "Chur",
  coira: "Chur",
  schaffhouse: "Schaffhausen",
  thoune: "Thun",
  "yverdon-les-bains": "Yverdon",
  siders: "Sierre",
  delemont: "Delemont",
  delsberg: "Delemont",
  soleure: "Solothurn",
  soletta: "Solothurn",
  brigue: "Brig",
  briga: "Brig",
};

const FRENCH_SWISS_CITIES: ReadonlySet<SwissCity> = new Set([
  "Geneva",
  "Lausanne",
  "Fribourg",
  "Neuchatel",
  "La Chaux-de-Fonds",
  "Sion",
  "Nyon",
  "Morges",
  "Vevey",
  "Montreux",
  "Yverdon",
  "Bulle",
  "Martigny",
  "Sierre",
  "Monthey",
  "Delemont",
]);

const ITALIAN_SWISS_CITIES: ReadonlySet<SwissCity> = new Set([
  "Lugano",
  "Bellinzona",
  "Locarno",
  "Mendrisio",
  "Chiasso",
]);

export type SwissBoardLang = "fr" | "de" | "it";

/** Language of the listing board for this Swiss city (Romandie / Ticino / rest). */
export function swissCityBoardLang(location: string | null | undefined): SwissBoardLang | null {
  const city = matchSwissCity(location ?? undefined);
  if (!city) {
    return null;
  }
  if (ITALIAN_SWISS_CITIES.has(city)) {
    return "it";
  }
  if (FRENCH_SWISS_CITIES.has(city)) {
    return "fr";
  }
  return "de";
}

export function matchSwissCity(location: string | undefined): SwissCity | "" {
  if (!location?.trim()) {
    return "";
  }
  const folded = foldCity(location);
  const exact = SWISS_CITIES.find((city) => foldCity(city) === folded);
  if (exact) {
    return exact;
  }
  const aliased = CITY_ALIASES[folded];
  if (aliased) {
    return aliased;
  }
  const withoutZip = folded.replace(/^\d{4,5}\s+/, "").trim();
  if (withoutZip && withoutZip !== folded) {
    return matchSwissCity(withoutZip);
  }
  const first = folded.split(/[,/]/)[0]?.trim() ?? "";
  if (first && first !== folded) {
    return matchSwissCity(first);
  }
  return "";
}
