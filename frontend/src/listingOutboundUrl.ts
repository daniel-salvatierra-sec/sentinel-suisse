import { swissCityBoardLang, type SwissBoardLang } from "./swissCities";

export type BoardLang = SwissBoardLang;

export function listingBoardLang(listing: {
  country?: string;
  location?: string | null;
}): BoardLang {
  if (listing.country === "FR") {
    return "fr";
  }
  if (listing.country === "DE") {
    return "de";
  }
  if (listing.country === "IT") {
    return "it";
  }
  return swissCityBoardLang(listing.location) ?? "fr";
}

function hostOf(url: URL): string {
  return url.hostname.replace(/^www\./, "").toLowerCase();
}

function replacePathLang(url: URL, lang: string): void {
  const parts = url.pathname.split("/");
  if (parts.length >= 2 && /^(de|fr|en|it)$/i.test(parts[1] ?? "")) {
    parts[1] = lang;
    url.pathname = parts.join("/") || "/";
  }
}

const JOBUP_VERB: Record<BoardLang, string> = {
  fr: "emplois",
  de: "stellen",
  it: "impieghi",
};

function rewriteJobup(url: URL, lang: BoardLang): void {
  const parts = url.pathname.split("/");
  if (parts.length < 3) {
    replacePathLang(url, lang);
    return;
  }
  parts[1] = lang;
  if (/^(emplois|jobs|stellen|impieghi)$/i.test(parts[2] ?? "")) {
    parts[2] = JOBUP_VERB[lang];
  }
  url.pathname = parts.join("/") || "/";
}

const HOMEGATE_VERB: Record<BoardLang, string> = {
  de: "mieten",
  fr: "louer",
  it: "affittare",
};

function rewriteHomegate(url: URL, lang: BoardLang): void {
  url.pathname = url.pathname.replace(
    /^\/(mieten|louer|rent|affittare)(?=\/|$)/i,
    `/${HOMEGATE_VERB[lang]}`,
  );
}

/**
 * Open the original listing in the language of the place (FR / DE / IT),
 * not the app UI language. Spanish and Portuguese have no board locale;
 * people can translate in the browser if they want.
 */
export function listingOutboundUrl(
  sourceUrl: string,
  listing: { country?: string; location?: string | null },
): string {
  let url: URL;
  try {
    url = new URL(sourceUrl);
  } catch {
    return sourceUrl;
  }
  if (url.protocol !== "http:" && url.protocol !== "https:") {
    return sourceUrl;
  }

  const host = hostOf(url);
  const boardLang = listingBoardLang(listing);

  if (host === "flatfox.ch") {
    // German /de/flat/... and /it/flat/... 404 on many listings; French works.
    const flatLang = boardLang === "fr" ? "fr" : "en";
    replacePathLang(url, flatLang);
    return url.toString();
  }

  if (host === "jobs.ch" || host === "jobscout24.ch") {
    replacePathLang(url, boardLang);
    return url.toString();
  }

  if (host === "jobup.ch") {
    rewriteJobup(url, boardLang);
    return url.toString();
  }

  if (host === "homegate.ch") {
    rewriteHomegate(url, boardLang);
    return url.toString();
  }

  if (host === "immoscout24.ch" || host === "anibis.ch" || host === "newhome.ch") {
    replacePathLang(url, boardLang);
    return url.toString();
  }

  return url.toString();
}
