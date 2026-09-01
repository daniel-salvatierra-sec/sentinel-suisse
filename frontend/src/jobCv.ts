import type { Listing } from "./api";
import { listingBoardLang, type BoardLang } from "./listingOutboundUrl";
import { listingIsFrontalier } from "./housingDossier";

export type CvGapId = "permit" | "cefr" | "dates" | "length" | "nationality";

const NAME_PLACEHOLDER: Record<BoardLang, string> = {
  fr: "[Votre nom]",
  de: "[Vorname Nachname]",
  it: "[Nome e cognome]",
};

const PERMIT_RE =
  /permiso|\bpermit\b|work permit|\bpermis\b|bewilligung|auslanderausweis|legittimazione|frontalier/i;

const CEFR_RE = /\b(?:cefr|a1|a2|b1|b2|c1|c2)\b/i;

const SWISS_DATE_RE = /\b\d{2}\.\d{2}\.(?:19|20)\d{2}\b/;

const YEAR_RE = /\b(?:19|20)\d{2}\b/;

const NATIONALITY_RE =
  /nacionalidad|nationality|nationalit[eé]|staatsangeh[öo]rigkeit|cittadinanza|citoyennet[eé]|nationalit[aà]/i;

function fold(value: string): string {
  return value.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function wordCount(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

export function detectCvGaps(cvText: string): CvGapId[] {
  const text = cvText.trim();
  if (!text) return [];
  const folded = fold(text);
  const gaps: CvGapId[] = [];
  if (!PERMIT_RE.test(folded)) gaps.push("permit");
  if (!CEFR_RE.test(folded)) gaps.push("cefr");
  if (YEAR_RE.test(text) && !SWISS_DATE_RE.test(text)) gaps.push("dates");
  const words = wordCount(text);
  if (words > 800 || words < 40) gaps.push("length");
  if (!NATIONALITY_RE.test(folded)) gaps.push("nationality");
  return gaps.slice(0, 5);
}

function workloadBit(
  min: number | null | undefined,
  max: number | null | undefined,
): string {
  if (min == null && max == null) return "";
  const label =
    min != null && max != null && min !== max ? `${min}–${max}%` : `${min ?? max}%`;
  return ` (${label})`;
}

function place(listing: Pick<Listing, "location">): string {
  return listing.location?.trim() || "Suisse";
}

export function buildJobCoverLetter(
  listing: Pick<
    Listing,
    "title" | "location" | "country" | "workload_min" | "workload_max"
  >,
  signerName: string,
): { lang: BoardLang; text: string } {
  const lang = listingBoardLang(listing);
  const name = signerName.trim() || NAME_PLACEHOLDER[lang];
  const where = place(listing);
  const title =
    listing.title.trim() ||
    (lang === "de" ? "diese Stelle" : lang === "it" ? "questo posto" : "ce poste");
  const load = workloadBit(listing.workload_min, listing.workload_max);
  const extra = listingIsFrontalier(listing)
    ? lang === "de"
      ? "\n\nIch pendle über die Grenze. Bewilligung und Sprachen nenne ich wahrheitsgemäss — ohne sie zu erhöhen."
      : lang === "it"
        ? "\n\nFaccio il frontaliero. Indico permesso e lingue in modo vero, senza alzarli."
        : "\n\nJe suis frontalier. Je déclare permis et langues tels quels, sans les surévaluer."
    : "";

  let body: string;
  if (lang === "de") {
    body = `Sehr geehrte Damen und Herren,

ich bewerbe mich auf «${title}» in ${where}${load}.

Meinen Lebenslauf richte ich auf diese Stelle aus: Bewilligung, Sprachen nach CEFR, chronologisch mit Daten TT.MM.JJJJ. Ich erfinde keine Kompetenzen.

Dieses Schreiben ist keine Zusage.${extra}

Freundliche Grüsse
${name}`;
  } else if (lang === "it") {
    body = `Gentile Signora, Egregio Signore,

mi candido per «${title}» a ${where}${load}.

Adatto il CV a questo annuncio: permesso, lingue CEFR, ordine cronologico con date GG.MM.AAAA. Non invento competenze.

Questa lettera non è una garanzia.${extra}

Cordiali saluti
${name}`;
  } else {
    body = `Madame, Monsieur,

je postule pour «${title}» à ${where}${load}.

J'adapte mon CV à cette offre : permis, langues CEFR, ordre chronologique avec dates JJ.MM.AAAA. Je n'invente aucune compétence.

Cette lettre n'est pas une garantie d'embauche.${extra}

Cordialement,
${name}`;
  }

  return { lang, text: `${body.trim()}\n` };
}

export function swissCvFrame(lang: BoardLang, name: string, original: string): string {
  const n = name.trim() || NAME_PLACEHOLDER[lang];
  let header: string;
  if (lang === "de") {
    header = `${n}
Staatsangehörigkeit: …
Bewilligung (G / B / C / L): …
Sprachen (CEFR): …`;
  } else if (lang === "it") {
    header = `${n}
Cittadinanza: …
Permesso (G / B / C / L): …
Lingue (CEFR): …`;
  } else {
    header = `${n}
Nationalité : …
Permis (G / B / C / L) : …
Langues (CEFR) : …`;
  }
  const body = original.trim();
  if (!body) return `${header}\n`;
  return `${header}\n\n${body}\n`;
}
