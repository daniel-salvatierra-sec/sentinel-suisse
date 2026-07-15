import type { ListingType } from "./api";
import type { Lang } from "./i18n";

const LANGS: Lang[] = ["fr", "de", "es", "pt", "en"];

/** Prefer VITE_PUBLIC_APP_URL (e.g. LAN IP) so a phone can open the QR target. */
export function subscribeBaseUrl(): string {
  const fromEnv = import.meta.env.VITE_PUBLIC_APP_URL as string | undefined;
  if (fromEnv?.trim()) {
    return fromEnv.trim().replace(/\/$/, "");
  }
  if (typeof window !== "undefined") {
    return window.location.origin;
  }
  return "http://127.0.0.1:5173";
}

export function buildSubscribeUrl(params: {
  lang: Lang;
  listingType: ListingType;
  location?: string;
  baseUrl?: string;
}): string {
  const base = (params.baseUrl ?? subscribeBaseUrl()).replace(/\/$/, "");
  const qs = new URLSearchParams();
  qs.set("tab", "account");
  qs.set("lang", params.lang);
  qs.set("type", params.listingType);
  const location = params.location?.trim();
  if (location) {
    qs.set("q", location);
  }
  return `${base}/?${qs.toString()}`;
}

export function parseSubscribeDeepLink(search: string): Partial<{
  tab: "account";
  lang: Lang;
  listingType: ListingType;
  location: string;
}> {
  const params = new URLSearchParams(search.startsWith("?") ? search : `?${search}`);
  const result: Partial<{
    tab: "account";
    lang: Lang;
    listingType: ListingType;
    location: string;
  }> = {};

  if (params.get("tab") === "account") {
    result.tab = "account";
  }

  const lang = params.get("lang");
  if (lang && (LANGS as string[]).includes(lang)) {
    result.lang = lang as Lang;
  }

  const type = params.get("type");
  if (type === "housing" || type === "job") {
    result.listingType = type;
  }

  const q = params.get("q");
  if (q != null && q !== "") {
    result.location = q;
  }

  return result;
}

/** Keep ?verify=… when clearing subscribe deep-link params. */
export function stripSubscribeParamsFromUrl(): void {
  const params = new URLSearchParams(window.location.search);
  const had =
    params.has("tab") || params.has("type") || params.has("q") || params.has("lang");
  if (!had) return;

  const verify = params.get("verify");
  const next = new URLSearchParams();
  if (verify) {
    next.set("verify", verify);
  }
  const qs = next.toString();
  window.history.replaceState({}, "", qs ? `${window.location.pathname}?${qs}` : window.location.pathname);
}
