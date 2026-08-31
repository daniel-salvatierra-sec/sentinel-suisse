import type { Lang } from "./i18n";

/** Swiss boards that speak de/fr/it/en — not es/pt. */
function swissBoardLang(app: Lang): "de" | "fr" | "en" | "it" {
  if (app === "fr" || app === "de" || app === "en") {
    return app;
  }
  return "en";
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

function rewriteJobup(url: URL, lang: "de" | "fr" | "en" | "it"): void {
  const parts = url.pathname.split("/");
  if (parts.length < 3) {
    replacePathLang(url, lang);
    return;
  }
  parts[1] = lang;
  if (/^(emplois|jobs|stellen|impieghi)$/i.test(parts[2] ?? "")) {
    parts[2] = lang === "fr" ? "emplois" : "jobs";
  }
  url.pathname = parts.join("/") || "/";
}

const HOMEGATE_VERB: Record<"de" | "fr" | "en" | "it", string> = {
  de: "mieten",
  fr: "louer",
  en: "rent",
  it: "affittare",
};

function rewriteHomegate(url: URL, lang: "de" | "fr" | "en" | "it"): void {
  url.pathname = url.pathname.replace(
    /^\/(mieten|louer|rent|affittare)(?=\/|$)/i,
    `/${HOMEGATE_VERB[lang]}`,
  );
}

/** Adzuna country sites have one UI language and no switcher. */
function adzunaUiLang(host: string): string | null {
  const map: Record<string, string> = {
    "adzuna.ch": "de",
    "adzuna.de": "de",
    "adzuna.at": "de",
    "adzuna.fr": "fr",
    "adzuna.it": "it",
    "adzuna.es": "es",
    "adzuna.pt": "pt",
    "adzuna.co.uk": "en",
    "adzuna.com": "en",
  };
  return map[host] ?? null;
}

function wrapGoogleTranslate(target: string, sourceLang: string, appLang: Lang): string {
  const wrapped = new URL("https://translate.google.com/translate");
  wrapped.searchParams.set("sl", sourceLang);
  wrapped.searchParams.set("tl", appLang);
  wrapped.searchParams.set("hl", appLang);
  wrapped.searchParams.set("u", target);
  return wrapped.toString();
}

/**
 * Open the original listing in the language the user picked in LinkSwiss.
 * Boards with a locale in the path are rewritten. Adzuna.ch is German-only,
 * so we send those through Google Translate when the app is not in German.
 */
export function listingOutboundUrl(sourceUrl: string, appLang: Lang): string {
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
  const boardLang = swissBoardLang(appLang);

  if (host === "flatfox.ch") {
    // German /de/flat/... 404s on many listings; es/pt have no locale. French does.
    const flatLang = appLang === "fr" ? "fr" : "en";
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

  const adzunaLang = adzunaUiLang(host);
  if (adzunaLang && adzunaLang !== appLang) {
    return wrapGoogleTranslate(url.toString(), adzunaLang, appLang);
  }

  return url.toString();
}
