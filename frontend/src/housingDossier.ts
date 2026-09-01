import type { Listing } from "./api";
import { listingBoardLang, type BoardLang } from "./listingOutboundUrl";

export function listingIsFrontalier(listing: { country?: string }): boolean {
  return listing.country === "FR" || listing.country === "DE" || listing.country === "IT";
}

const NAME_PLACEHOLDER: Record<BoardLang, string> = {
  fr: "[Votre nom]",
  de: "[Vorname Nachname]",
  it: "[Nome e cognome]",
};

function priceBit(
  lang: BoardLang,
  price: number | null | undefined,
  country?: string,
): string {
  if (price == null || !Number.isFinite(price)) return "";
  const n = String(Math.round(price));
  const currency = country === "FR" || country === "DE" || country === "IT" ? "EUR" : "CHF";
  if (lang === "de") return ` (${n} ${currency} / Monat)`;
  if (lang === "it") return ` (${n} ${currency} / mese)`;
  return ` (${n} ${currency} / mois)`;
}

function place(listing: Pick<Listing, "location">): string {
  return listing.location?.trim() || "Suisse";
}

const FRONTALIER: Record<BoardLang, string> = {
  fr: "J'habite de l'autre côté de la frontière. Je n'ai pas d'extrait des poursuites suisse ; j'envoie une lettre claire et les justificatifs équivalents. Le loyer est en CHF, mes revenus souvent en EUR.",
  de: "Ich wohne jenseits der Grenze. Ein Schweizer Betreibungsauszug liegt nicht vor; ich lege ein klares Schreiben und gleichwertige Nachweise bei. Die Miete ist in CHF, das Einkommen oft in EUR.",
  it: "Abito oltreconfine. Non ho l'estratto esecuzioni svizzero; allego una lettera chiara e i documenti equivalenti. L'affitto è in CHF, il reddito spesso in EUR.",
};

export function buildHousingCoverLetter(
  listing: Pick<Listing, "title" | "location" | "price" | "country">,
  signerName: string,
): { lang: BoardLang; text: string } {
  const lang = listingBoardLang(listing);
  const name = signerName.trim() || NAME_PLACEHOLDER[lang];
  const where = place(listing);
  const price = priceBit(lang, listing.price, listing.country);
  const title =
    listing.title.trim() ||
    (lang === "de" ? "diese Wohnung" : lang === "it" ? "questo alloggio" : "ce logement");
  const extra = listingIsFrontalier(listing) ? `\n\n${FRONTALIER[lang]}` : "";

  let body: string;
  if (lang === "de") {
    body = `Sehr geehrte Damen und Herren,

ich bewerbe mich auf «${title}» in ${where}${price}.

Ich stelle ein vollständiges Dossier zusammen: Bewerbungsschreiben, Selbstauskunft, Betreibungsauszug (falls vorhanden), Lohnabrechnungen und Ausweis. Ich sende es auf Wunsch.

Dieses Schreiben ersetzt nicht das Formular der Agentur und ist keine Zusage.${extra}

Freundliche Grüsse
${name}`;
  } else if (lang === "it") {
    body = `Gentile Signora, Egregio Signore,

le scrivo per «${title}» a ${where}${price}.

Preparo un dossier completo: lettera, scheda personale, estratto (se disponibile), buste paga e documento. Posso inviarlo quando lo chiede.

Questa lettera non sostituisce il modulo dell'agenzia e non è una garanzia.${extra}

Cordiali saluti
${name}`;
  } else {
    body = `Madame, Monsieur,

je vous écris au sujet de «${title}» à ${where}${price}.

Je prépare un dossier complet : lettre, renseignements personnels, extrait des poursuites (s'il existe), justificatifs de revenus et pièce d'identité. Je peux l'envoyer dès que vous me le demanderez.

Cette lettre ne remplace pas le formulaire de l'agence et ne garantit pas le logement.${extra}

Cordialement,
${name}`;
  }

  return { lang, text: `${body.trim()}\n` };
}

export function letterTeaser(text: string, lines = 4): string {
  return text.split("\n").slice(0, lines).join("\n");
}
