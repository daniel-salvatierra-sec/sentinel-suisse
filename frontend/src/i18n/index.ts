export type Lang = "fr" | "de" | "es" | "pt" | "en";

export const LANGS: Lang[] = ["fr", "de", "es", "pt", "en"];

export const LANG_LABELS: Record<Lang, string> = {
  fr: "FR",
  de: "DE",
  es: "ES",
  pt: "PT",
  en: "EN",
};

export type Messages = {
  appName: string;
  tagline: string;
  chooseLang: string;
  housing: string;
  job: string;
  housingDesc: string;
  jobDesc: string;
  searchPlaceholder: string;
  search: string;
  filters: string;
  map: string;
  list: string;
  alerts: string;
  alertsTitle: string;
  alertsDesc: string;
  phone: string;
  email: string;
  saveSearch: string;
  guide: string;
  guideHello: string;
  guideHousing: string;
  guideJob: string;
  guideAlerts: string;
  guideClose: string;
  noResults: string;
  loading: string;
  privacy: string;
  openSource: string;
  priceMonthly: string;
  route: string;
};

import fr from "./locales/fr.json";
import de from "./locales/de.json";
import es from "./locales/es.json";
import pt from "./locales/pt.json";
import en from "./locales/en.json";

export const messages: Record<Lang, Messages> = { fr, de, es, pt, en };

const STORAGE_KEY = "suisse-alert-lang";

export function loadLang(): Lang {
  const saved = localStorage.getItem(STORAGE_KEY) as Lang | null;
  if (saved && LANGS.includes(saved)) return saved;
  return "fr";
}

export function saveLang(lang: Lang): void {
  localStorage.setItem(STORAGE_KEY, lang);
}
