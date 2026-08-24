function foldQuery(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{M}/gu, "");
}

const JOB_QUERY_ALIASES = new Set([
  "fleuriste",
  "fleuristes",
  "florist",
  "florists",
  "floristin",
  "florista",
  "fiorista",
  "floristeria",
  "floristerie",
  "blumenfach",
  "cajero",
  "cajera",
  "cajeros",
  "cashier",
  "caissier",
  "caissiere",
  "kassierer",
  "kassierin",
  "caixa",
]);

/** True when the search box is an occupation word, not a city. */
export function queryLooksLikeJob(query: string): boolean {
  const folded = foldQuery(query);
  if (!folded) return false;
  if (JOB_QUERY_ALIASES.has(folded)) return true;
  return folded.split(/\s+/).some((token) => JOB_QUERY_ALIASES.has(token));
}
