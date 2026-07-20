/** Approximate coordinates for Swiss / border cities and Geneva communes (map pins). */
const CITY_COORDS: Record<string, [number, number]> = {
  geneva: [46.2044, 6.1432],
  genève: [46.2044, 6.1432],
  geneve: [46.2044, 6.1432],
  genf: [46.2044, 6.1432],
  ginebra: [46.2044, 6.1432],
  ginevra: [46.2044, 6.1432],
  "eaux-vives": [46.2015, 6.1605],
  "eaux vives": [46.2015, 6.1605],
  plainpalais: [46.1985, 6.1425],
  carouge: [46.183, 6.139],
  meyrin: [46.2342, 6.0806],
  vernier: [46.217, 6.085],
  lancy: [46.182, 6.115],
  onex: [46.185, 6.1],
  thonex: [46.188, 6.2],
  thônex: [46.188, 6.2],
  bernex: [46.176, 6.076],
  versoix: [46.2836, 6.1661],
  nyon: [46.3833, 6.2396],
  "collonge-bellerive": [46.253, 6.204],
  lausanne: [46.5197, 6.6323],
  zurich: [47.3769, 8.5417],
  zürich: [47.3769, 8.5417],
  bern: [46.948, 7.4474],
  basel: [47.5596, 7.5886],
  annemasse: [46.1931, 6.2375],
  "ferney-voltaire": [46.258, 6.108],
  "saint-julien-en-genevois": [46.1435, 6.081],
  gaillard: [46.185, 6.208],
};

/** Postal codes around Geneva → approx coords */
const POSTAL_COORDS: Record<string, [number, number]> = {
  "1201": [46.205, 6.143],
  "1202": [46.21, 6.14],
  "1205": [46.198, 6.14],
  "1206": [46.195, 6.16],
  "1207": [46.2015, 6.1605],
  "1212": [46.182, 6.115],
  "1213": [46.185, 6.1],
  "74100": [46.1931, 6.2375],
  "01210": [46.258, 6.108],
  "74160": [46.1435, 6.081],
  "74240": [46.185, 6.208],
};

export function coordsForLocation(location: string | null): [number, number] {
  if (!location) return [46.2044, 6.1432];
  const raw = location.trim().toLowerCase();
  const postal = raw.match(/\b(\d{4,5})\b/);
  if (postal && POSTAL_COORDS[postal[1]]) {
    return POSTAL_COORDS[postal[1]];
  }
  const key = raw.split(",")[0].trim();
  if (CITY_COORDS[key]) return CITY_COORDS[key];
  for (const [city, coords] of Object.entries(CITY_COORDS)) {
    if (key.includes(city) || city.includes(key) || raw.includes(city)) {
      return coords;
    }
  }
  return [46.2044, 6.1432];
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

export function formatMapPrice(price: number): string {
  const rounded = Math.round(price);
  return `CHF ${rounded.toLocaleString("de-CH")}`;
}
