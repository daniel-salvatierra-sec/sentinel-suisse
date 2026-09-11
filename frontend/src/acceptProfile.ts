import type { AcceptGoal, AcceptProfile, Listing, ListingType } from "./api";
import type { Messages } from "./i18n";

export type AcceptReason = {
  kind: "yes" | "ask";
  text: string;
};

function fold(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

/** Common city spellings → canonical folded form for matching listings. */
const PLACE_ALIASES: Record<string, string> = {
  geneve: "geneve",
  geneva: "geneve",
  genf: "geneve",
  ginebra: "geneve",
  ginevra: "geneve",
  genebra: "geneve",
  zurich: "zurich",
  zurichs: "zurich",
  zurigo: "zurich",
  zuriqe: "zurich",
  lausanne: "lausanne",
  losana: "lausanne",
  losanna: "lausanne",
  basel: "basel",
  bale: "basel",
  basilea: "basel",
  bern: "bern",
  berne: "bern",
  berna: "bern",
  lugano: "lugano",
  lucerne: "luzern",
  luzern: "luzern",
  lucerna: "luzern",
  annemasse: "annemasse",
  thonon: "thonon",
  annecy: "annecy",
  ferney: "ferney",
  gaillard: "gaillard",
};

/** Free-text language tokens people type (typos / mixed langs) → ISO-ish code. */
const LANG_ALIASES: Record<string, string> = {
  es: "es",
  esp: "es",
  spa: "es",
  spanish: "es",
  espanol: "es",
  espagnol: "es",
  spagnolo: "es",
  spanisch: "es",
  castellan: "es",
  castellano: "es",
  fr: "fr",
  fra: "fr",
  fre: "fr",
  french: "fr",
  francais: "fr",
  france: "fr",
  frances: "fr",
  francese: "fr",
  franzoesisch: "fr",
  franzosisch: "fr",
  en: "en",
  eng: "en",
  english: "en",
  ingles: "en",
  anglais: "en",
  inglese: "en",
  englisch: "en",
  de: "de",
  deu: "de",
  ger: "de",
  german: "de",
  aleman: "de",
  allemand: "de",
  deutsch: "de",
  tedesco: "de",
  it: "it",
  ita: "it",
  italian: "it",
  italiano: "it",
  italien: "it",
  italienisch: "it",
  pt: "pt",
  por: "pt",
  portuguese: "pt",
  portugues: "pt",
  portugais: "pt",
  portugiesisch: "pt",
};

const LANG_MATCH_TERMS: Record<string, string[]> = {
  es: ["espagnol", "espanol", "spanish", "spagnolo", "spanisch", "castellano", " es ", "es/", "/es"],
  fr: ["francais", "french", "frances", "francese", "franzosisch", " fr ", "fr/", "/fr"],
  en: ["english", "anglais", "ingles", "inglese", "englisch", " en ", "en/", "/en"],
  de: ["deutsch", "german", "allemand", "aleman", "tedesco", " de ", "de/", "/de"],
  it: ["italien", "italian", "italiano", "italienisch", " it ", "it/", "/it"],
  pt: ["portugais", "portuguese", "portugues", "portoghese", " pt ", "pt/", "/pt"],
};

export function emptyAcceptProfile(): AcceptProfile {
  return {
    goal: null,
    live_in: "",
    work_in: "",
    permit: null,
    languages: "",
    budget_chf: null,
    cities: "",
    move_in: "",
    household: null,
  };
}

export function acceptProfileFilled(profile: AcceptProfile | null | undefined): boolean {
  if (!profile) return false;
  return Boolean(
    profile.goal ||
      profile.live_in?.trim() ||
      profile.work_in?.trim() ||
      profile.permit ||
      profile.languages?.trim() ||
      profile.budget_chf ||
      profile.cities?.trim() ||
      profile.move_in?.trim() ||
      profile.household,
  );
}

function canonicalizePlace(token: string): string {
  const folded = fold(token).replace(/-/g, " ").replace(/\./g, " ").replace(/\s+/g, " ").trim();
  if (!folded) return "";
  return PLACE_ALIASES[folded] ?? folded;
}

function placesOf(profile: AcceptProfile): { raw: string; key: string }[] {
  const chunks = [
    profile.live_in ?? "",
    profile.work_in ?? "",
    ...(profile.cities ?? "").split(/[,;/]/),
  ];
  const out: { raw: string; key: string }[] = [];
  for (const item of chunks) {
    const raw = item.trim();
    const key = canonicalizePlace(raw);
    if (key.length >= 2) out.push({ raw: raw || key, key });
  }
  return out;
}

function placeHit(listing: Listing, profile: AcceptProfile): string | null {
  const loc = canonicalizePlace(listing.location ?? "");
  if (!loc) return null;
  for (const city of placesOf(profile)) {
    if (city.key.length < 3) continue;
    if (loc.includes(city.key) || city.key.includes(loc)) {
      return city.raw;
    }
  }
  return null;
}

/** Parse messy free-text languages: "espagnol, france ingles" → ["es","fr","en"]. */
export function parseSpokenLanguages(raw: string | null | undefined): string[] {
  if (!raw?.trim()) return [];
  const folded = fold(raw).replace(/[+|/]/g, " ");
  const tokens = folded.split(/[\s,;]+/).filter(Boolean);
  const out: string[] = [];
  for (const token of tokens) {
    if (/^(a1|a2|b1|b2|c1|c2)$/.test(token)) continue;
    const code = LANG_ALIASES[token];
    if (code && !out.includes(code)) out.push(code);
  }
  return out;
}

function languageHit(listing: Listing, profile: AcceptProfile): string[] {
  const codes = parseSpokenLanguages(profile.languages);
  if (!codes.length) return [];
  const hay = ` ${fold(`${listing.title ?? ""} ${listing.description ?? ""} ${listing.location ?? ""}`)} `;
  return codes.filter((code) => {
    const terms = LANG_MATCH_TERMS[code] ?? [];
    return terms.some((term) => hay.includes(fold(term)));
  });
}

function goalFits(listingType: ListingType, goal: AcceptGoal | null | undefined): boolean {
  if (!goal || goal === "both") return true;
  return goal === listingType;
}

/** Up to 5 honest reasons. Never a score. */
export function acceptReasons(
  listing: Listing,
  profile: AcceptProfile | null | undefined,
  t: Messages,
): AcceptReason[] {
  if (!acceptProfileFilled(profile) || !profile) return [];
  if (!goalFits(listing.listing_type, profile.goal ?? null)) return [];

  const out: AcceptReason[] = [];
  if (profile.goal === "housing" && listing.listing_type === "housing") {
    out.push({ kind: "yes", text: t.acceptWhyGoalHousing });
  }
  if (profile.goal === "job" && listing.listing_type === "job") {
    out.push({ kind: "yes", text: t.acceptWhyGoalJob });
  }
  if (profile.goal === "both") {
    out.push({
      kind: "yes",
      text: listing.listing_type === "job" ? t.acceptWhyGoalJob : t.acceptWhyGoalHousing,
    });
  }

  if (listing.listing_type === "housing" && profile.budget_chf && listing.price != null) {
    const price = Number(listing.price);
    if (Number.isFinite(price) && price <= profile.budget_chf) {
      out.push({
        kind: "yes",
        text: t.acceptWhyBudget
          .replace("{price}", String(Math.round(price)))
          .replace("{budget}", String(profile.budget_chf)),
      });
    }
  }

  const hit = placeHit(listing, profile);
  if (hit) {
    out.push({ kind: "yes", text: t.acceptWhyPlace.replace("{place}", hit) });
  }

  const live = (profile.live_in ?? "").trim();
  if (
    listing.listing_type === "job" &&
    listing.country === "CH" &&
    live &&
    /annemasse|gaillard|ferney|thonon|annecy|lorrach|weil|konstanz|como|varese|domodossola|france|italia|deutschland|allemagne/i.test(
      fold(live),
    )
  ) {
    out.push({ kind: "yes", text: t.acceptWhyFrontalier.replace("{place}", live) });
  }

  if (listing.listing_type === "job") {
    if (!profile.permit) {
      out.push({ kind: "ask", text: t.acceptWhyPermitAsk });
    } else if (profile.permit === "G" || profile.permit === "B" || profile.permit === "C" || profile.permit === "L") {
      out.push({
        kind: "yes",
        text: t.acceptWhyPermit.replace("{permit}", profile.permit),
      });
    } else if (profile.permit === "none") {
      out.push({ kind: "ask", text: t.acceptWhyPermitNone });
    }

    const langs = languageHit(listing, profile);
    if (langs.length) {
      out.push({
        kind: "yes",
        text: t.acceptWhyLanguages.replace("{langs}", langs.join(", ").toUpperCase()),
      });
    }
  }

  return out.slice(0, 5);
}
