/** Approximate coordinates for Swiss cities (map pins). */
const CITY_COORDS: Record<string, [number, number]> = {
  geneva: [46.2044, 6.1432],
  genève: [46.2044, 6.1432],
  geneve: [46.2044, 6.1432],
  genf: [46.2044, 6.1432],
  ginebra: [46.2044, 6.1432],
  ginevra: [46.2044, 6.1432],
  lausanne: [46.5197, 6.6323],
  zurich: [47.3769, 8.5417],
  zürich: [47.3769, 8.5417],
  bern: [46.948, 7.4474],
  basel: [47.5596, 7.5886],
};

export function coordsForLocation(location: string | null): [number, number] {
  if (!location) return [46.8182, 8.2275];
  const key = location.split(",")[0].trim().toLowerCase();
  if (CITY_COORDS[key]) return CITY_COORDS[key];
  for (const [city, coords] of Object.entries(CITY_COORDS)) {
    if (key.includes(city) || city.includes(key)) return coords;
  }
  return [46.8182, 8.2275];
}

export function mapsDirectionsUrl(coords: [number, number]): string {
  return `https://www.google.com/maps/dir/?api=1&destination=${coords[0]},${coords[1]}`;
}
