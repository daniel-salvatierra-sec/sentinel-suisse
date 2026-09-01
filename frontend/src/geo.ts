/** Approximate coordinates for Swiss / border cities (map pins and itinerary). */
import { matchSwissCity, type SwissCity } from "./swissCities";

/** Geographic centre of Switzerland — unknown places, not Geneva. */
export const SWISS_CENTER: [number, number] = [46.8182, 8.2275];

const GENEVA: [number, number] = [46.2044, 6.1432];
const LUCERNE: [number, number] = [47.0502, 8.3093];
const SION: [number, number] = [46.2331, 7.3606];
const LAUSANNE: [number, number] = [46.5197, 6.6323];

const CITY_LATLNG: Record<SwissCity, [number, number]> = {
  Geneva: GENEVA,
  Zurich: [47.3769, 8.5417],
  Bern: [46.948, 7.4474],
  Basel: [47.5596, 7.5886],
  Lausanne: LAUSANNE,
  Lugano: [46.0037, 8.9511],
  Lucerne: LUCERNE,
  "St. Gallen": [47.4245, 9.3767],
  Winterthur: [47.5056, 8.7241],
  Fribourg: [46.8065, 7.1617],
  Neuchatel: [46.9929, 6.931],
  "La Chaux-de-Fonds": [47.1035, 6.8328],
  Biel: [47.1368, 7.2467],
  Zug: [47.1662, 8.5155],
  Sion: SION,
  Chur: [46.8508, 9.532],
  Bellinzona: [46.1947, 9.0244],
  Schaffhausen: [47.6973, 8.6349],
  Thun: [46.758, 7.628],
  Aarau: [47.3925, 8.0442],
  Nyon: [46.3833, 6.2396],
  Morges: [46.5113, 6.498],
  Vevey: [46.4628, 6.843],
  Montreux: [46.4312, 6.9106],
  Yverdon: [46.7785, 6.641],
  Bulle: [46.6195, 7.0569],
  Martigny: [46.1024, 7.0722],
  Sierre: [46.2919, 7.5356],
  Monthey: [46.2547, 6.9541],
  Delemont: [47.3646, 7.3445],
  Olten: [47.3499, 7.9038],
  Baden: [47.4733, 8.3059],
  Wil: [47.4615, 9.0424],
  Uster: [47.3479, 8.7195],
  Frauenfeld: [47.558, 8.8989],
  Solothurn: [47.2088, 7.5323],
  Langenthal: [47.2153, 7.7961],
  Interlaken: [46.6863, 7.8632],
  Liestal: [47.4845, 7.7344],
  Kreuzlingen: [47.65, 9.175],
  Locarno: [46.1709, 8.7995],
  Mendrisio: [45.8706, 8.9816],
  Chiasso: [45.832, 9.031],
  Brig: [46.3167, 7.9872],
  Schwyz: [47.0207, 8.653],
  Emmen: [47.0782, 8.3048],
  Dietikon: [47.4017, 8.4001],
  Horgen: [47.2598, 8.5978],
};

/** Communes, border towns, and extra spellings not in the city dropdown. */
const EXTRA_COORDS: Record<string, [number, number]> = {
  "eaux-vives": [46.2015, 6.1605],
  "eaux vives": [46.2015, 6.1605],
  plainpalais: [46.1985, 6.1425],
  carouge: [46.183, 6.139],
  meyrin: [46.2342, 6.0806],
  vernier: [46.217, 6.085],
  lancy: [46.182, 6.115],
  onex: [46.185, 6.1],
  thonex: [46.188, 6.2],
  bernex: [46.176, 6.076],
  versoix: [46.2836, 6.1661],
  "collonge-bellerive": [46.253, 6.204],
  acacias: [46.192, 6.147],
  chatelaine: [46.21, 6.116],
  cologny: [46.218, 6.18],
  veyrier: [46.167, 6.166],
  satigny: [46.214, 6.043],
  "plan-les-ouates": [46.166, 6.114],
  "grand-saconnex": [46.232, 6.119],
  annemasse: [46.1931, 6.2375],
  gaillard: [46.185, 6.208],
  "ferney-voltaire": [46.258, 6.108],
  ferney: [46.258, 6.108],
  "saint-julien-en-genevois": [46.1435, 6.081],
  "saint-julien": [46.1435, 6.081],
  thonon: [46.3708, 6.4798],
  annecy: [45.8992, 6.1294],
  lorrach: [47.6144, 7.6614],
  "weil am rhein": [47.5934, 7.6108],
  konstanz: [47.6633, 9.1753],
  waldshut: [47.6234, 8.2174],
  como: [45.8081, 9.0852],
  varese: [45.8206, 8.8251],
  domodossola: [46.1165, 8.2911],
  "fr-border": [46.1931, 6.2375],
  "de-border": [47.6144, 7.6614],
  "it-border": [45.8081, 9.0852],
  paris: [48.8566, 2.3522],
  marseille: [43.2965, 5.3698],
  lyon: [45.764, 4.8357],
  toulouse: [43.6047, 1.4442],
  berlin: [52.52, 13.405],
  hamburg: [53.5511, 9.9937],
  munich: [48.1351, 11.582],
  munchen: [48.1351, 11.582],
  cologne: [50.9375, 6.9603],
  koln: [50.9375, 6.9603],
  frankfurt: [50.1109, 8.6821],
  stuttgart: [48.7758, 9.1829],
  dusseldorf: [51.2277, 6.7735],
  leipzig: [51.3397, 12.3731],
  dortmund: [51.5136, 7.4653],
  essen: [51.4556, 7.0116],
  bremen: [53.0793, 8.8017],
  dresden: [51.0504, 13.7373],
  hanover: [52.3759, 9.732],
  hannover: [52.3759, 9.732],
  nuremberg: [49.4521, 11.0767],
  nurnberg: [49.4521, 11.0767],
  duisburg: [51.4344, 6.7623],
  rome: [41.9028, 12.4964],
  roma: [41.9028, 12.4964],
  milan: [45.4642, 9.19],
  milano: [45.4642, 9.19],
  naples: [40.8518, 14.2681],
  napoli: [40.8518, 14.2681],
  turin: [45.0703, 7.6869],
  torino: [45.0703, 7.6869],
  palermo: [38.1157, 13.3615],
  genoa: [44.4056, 8.9463],
  genova: [44.4056, 8.9463],
};

const POSTAL_COORDS: Record<string, [number, number]> = {
  "1003": LAUSANNE,
  "1004": LAUSANNE,
  "1005": LAUSANNE,
  "1201": [46.205, 6.143],
  "1202": [46.21, 6.14],
  "1205": [46.198, 6.14],
  "1206": [46.195, 6.16],
  "1207": [46.2015, 6.1605],
  "1212": [46.182, 6.115],
  "1213": [46.185, 6.1],
  "1260": [46.3833, 6.2396],
  "1700": [46.8065, 7.1617],
  "1950": SION,
  "2000": [46.9929, 6.931],
  "2300": [47.1035, 6.8328],
  "2500": [47.1368, 7.2467],
  "3000": [46.948, 7.4474],
  "3011": [46.948, 7.4474],
  "3600": [46.758, 7.628],
  "4001": [47.5596, 7.5886],
  "5000": [47.3925, 8.0442],
  "6003": LUCERNE,
  "6004": LUCERNE,
  "6005": LUCERNE,
  "6006": LUCERNE,
  "6300": [47.1662, 8.5155],
  "6500": [46.1947, 9.0244],
  "6900": [46.0037, 8.9511],
  "7000": [46.8508, 9.532],
  "8001": [47.3769, 8.5417],
  "8200": [47.6973, 8.6349],
  "8400": [47.5056, 8.7241],
  "9000": [47.4245, 9.3767],
  "74100": [46.1931, 6.2375],
  "01210": [46.258, 6.108],
  "74160": [46.1435, 6.081],
  "74240": [46.185, 6.208],
};

function foldPlace(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{M}/gu, "");
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/** True when `city` is a whole word in `haystack` (so "sion" ≠ "pension"). */
function hasCityToken(haystack: string, city: string): boolean {
  if (city.length < 3) return false;
  const pattern = new RegExp(
    `(^|[^a-z0-9])${escapeRegExp(city)}([^a-z0-9]|$)`,
  );
  return pattern.test(haystack);
}

const TOKEN_PLACES: { key: string; coords: [number, number] }[] = [
  ...Object.entries(EXTRA_COORDS).map(([key, coords]) => ({ key, coords })),
  ...Object.entries(CITY_LATLNG).map(([name, coords]) => ({
    key: foldPlace(name),
    coords,
  })),
].sort((a, b) => b.key.length - a.key.length);

/**
 * Resolve a listing/search string to coordinates, or null if unknown.
 * Does not default to Geneva.
 */
export function lookupCoords(location: string | null | undefined): [number, number] | null {
  if (!location?.trim()) return null;
  const folded = foldPlace(location);

  const postal = folded.match(/\b(\d{4,5})\b/);
  if (postal && POSTAL_COORDS[postal[1]]) {
    return POSTAL_COORDS[postal[1]];
  }

  const named = matchSwissCity(location);
  if (named) return CITY_LATLNG[named];

  const first = folded.split(/[,/]/)[0]?.trim() ?? "";
  if (EXTRA_COORDS[first]) return EXTRA_COORDS[first];
  if (EXTRA_COORDS[folded]) return EXTRA_COORDS[folded];

  for (const { key, coords } of TOKEN_PLACES) {
    if (hasCityToken(folded, key) || hasCityToken(first, key)) {
      return coords;
    }
  }
  return null;
}

export function coordsForLocation(location: string | null): [number, number] {
  return lookupCoords(location) ?? SWISS_CENTER;
}

/** Slight offset so stacked pins at the same city remain visible. */
export function jitterCoords(
  coords: [number, number],
  index: number,
  total: number,
): [number, number] {
  if (total <= 1) return coords;
  const angle = (index / total) * Math.PI * 2;
  const radius = 0.004 + (index % 3) * 0.0015;
  return [coords[0] + Math.cos(angle) * radius, coords[1] + Math.sin(angle) * radius];
}

export function mapsDirectionsUrl(coords: [number, number]): string {
  return `https://www.google.com/maps/dir/?api=1&destination=${coords[0]},${coords[1]}`;
}

export function listingCurrency(country?: string | null): "CHF" | "EUR" {
  if (country === "FR" || country === "DE" || country === "IT") {
    return "EUR";
  }
  return "CHF";
}

export function formatMapPrice(price: number, country?: string | null): string {
  const rounded = Math.round(price);
  const currency = listingCurrency(country);
  const locale = currency === "EUR" ? "fr-CH" : "de-CH";
  return `${currency} ${rounded.toLocaleString(locale)}`;
}
